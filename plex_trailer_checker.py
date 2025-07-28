#!/usr/bin/env python3
import os
import sys
import logging
import time
import re
import json
from pathlib import Path
from collections import defaultdict
from urllib.parse import urljoin
import subprocess
from difflib import SequenceMatcher

import requests
from tqdm import tqdm
from plexapi.server import PlexServer

from config import cfg

############################################################
# INIT
############################################################

# Setup logger
log_filename = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'trailer_checker.log')
logging.basicConfig(
    filename=log_filename,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logging.getLogger('urllib3.connectionpool').disabled = True
log = logging.getLogger("Plex_Trailer_Checker")

# Setup PlexServer object
try:
    plex = PlexServer(cfg['PLEX_SERVER'], cfg['PLEX_TOKEN'])
    log.info(f"Successfully connected to Plex server: {cfg['PLEX_SERVER']}")
except Exception as e:
    log.exception("Exception connecting to server %r with token %r", cfg['PLEX_SERVER'], cfg['PLEX_TOKEN'])
    print(f"Exception connecting to {cfg['PLEX_SERVER']} with token: {cfg['PLEX_TOKEN']}")
    print(f"Error: {e}")
    exit(1)

# Global request counter for API rate limiting
api_request_count = 0

############################################################
# KINOCHECK API FUNCTIONS
############################################################

def make_kinocheck_request(endpoint, params=None):
    """Make a request to the KinoCheck API with rate limiting"""
    global api_request_count
    
    if not cfg['KINOCHECK_API']['enabled']:
        log.debug("KinoCheck API is disabled in config")
        print("    KinoCheck API is disabled")
        return None
    
    if api_request_count >= cfg['KINOCHECK_API']['max_requests_per_day']:
        log.warning("API request limit reached for today")
        print("    API request limit reached")
        return None
    
    url = urljoin(cfg['KINOCHECK_API']['base_url'], endpoint)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Add API key if available
    if cfg['KINOCHECK_API']['api_key']:
        headers['X-Api-Key'] = cfg['KINOCHECK_API']['api_key']
        headers['X-Api-Host'] = 'api.kinocheck.de'
    
    # Add language parameter
    if params is None:
        params = {}
    params['language'] = cfg['KINOCHECK_API']['language']
    
    log.debug(f"Making API request to: {url} with params: {params}")
    print(f"    API Request: {url} with params: {params}")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        api_request_count += 1
        
        log.debug(f"API Response: Status {response.status_code}")
        print(f"    API Response: Status {response.status_code}")
        
        if response.status_code == 200:
            log.debug(f"KinoCheck API request successful: {url}")
            result = response.json()
            log.debug(f"API Response data: {result}")
            print(f"    Response data keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            return result
        else:
            log.error(f"KinoCheck API request failed: {response.status_code} - {response.text}")
            print(f"    API Error: {response.status_code} - {response.text[:100]}")
            return None
    
    except Exception as e:
        log.error(f"Error making KinoCheck API request: {e}")
        print(f"    API Exception: {e}")
        return None


def find_show_trailers(show):
    """Find trailers for a TV show using KinoCheck API"""
    trailers = []
    
    # Debug: Show the GUIDs for debugging
    print(f"    Show primary GUID: {getattr(show, 'guid', 'No GUID')}")
    
    # Get all external GUIDs
    external_guids = []
    if hasattr(show, 'guids'):
        external_guids = [str(guid) for guid in show.guids]
        print(f"    External GUIDs: {external_guids}")
    
    # Try with TMDB ID first
    if cfg['MATCHING']['use_tmdb_ids']:
        tmdb_id = None
        for guid_str in external_guids:
            tmdb_id = extract_tmdb_id(guid_str)
            if tmdb_id:
                break
        
        if tmdb_id:
            log.debug(f"Searching for trailers using TMDB ID: {tmdb_id}")
            print(f"    Found TMDB ID: {tmdb_id}")
            data = make_kinocheck_request('/shows', {'tmdb_id': tmdb_id, 'categories': 'Trailer'})
            if data and 'videos' in data:
                trailers.extend(data['videos'])
                log.debug(f"Found {len(data['videos'])} trailers via TMDB ID")
                print(f"    API returned {len(data['videos'])} trailers")
        else:
            log.debug("No TMDB ID found in GUIDs")
            print("    No TMDB ID found")
    
    # Try with IMDB ID if no trailers found yet
    if not trailers and cfg['MATCHING']['use_imdb_ids']:
        imdb_id = None
        for guid_str in external_guids:
            imdb_id = extract_imdb_id(guid_str)
            if imdb_id:
                break
        
        if imdb_id:
            log.debug(f"Searching for trailers using IMDB ID: {imdb_id}")
            print(f"    Found IMDB ID: {imdb_id}")
            data = make_kinocheck_request('/shows', {'imdb_id': imdb_id, 'categories': 'Trailer'})
            if data and 'videos' in data:
                trailers.extend(data['videos'])
                log.debug(f"Found {len(data['videos'])} trailers via IMDB ID")
                print(f"    API returned {len(data['videos'])} trailers")
        else:
            log.debug("No IMDB ID found in GUIDs")
            print("    No IMDB ID found")
    
    # Summary
    if trailers:
        print(f"    ✅ Found {len(trailers)} trailers for {show.title}")
    else:
        print(f"    ❌ No trailers found for {show.title}")
    
    return trailers


def extract_tmdb_id(guid_string):
    """Extract TMDB ID from Plex GUID string"""
    if not guid_string:
        log.debug("No GUID string provided for TMDB extraction")
        return None
    
    log.debug(f"Extracting TMDB ID from: {guid_string}")
    
    # Look for TMDB pattern in various formats
    patterns = [
        r'tmdb://(\d+)',           # tmdb://12345
        r'tmdb/(\d+)',             # tmdb/12345  
        r'agents\.tmdb://(\d+)',   # com.plexapp.agents.tmdb://12345
        r'Guid:tmdb://(\d+)',      # Guid:tmdb://12345
    ]
    
    for pattern in patterns:
        tmdb_match = re.search(pattern, guid_string)
        if tmdb_match:
            tmdb_id = int(tmdb_match.group(1))
            log.debug(f"Extracted TMDB ID: {tmdb_id}")
            return tmdb_id
    
    log.debug("No TMDB ID pattern found in GUID")
    return None


def extract_imdb_id(guid_string):
    """Extract IMDB ID from Plex GUID string"""
    if not guid_string:
        log.debug("No GUID string provided for IMDB extraction")
        return None
    
    log.debug(f"Extracting IMDB ID from: {guid_string}")
    
    # Look for IMDB pattern in various formats
    patterns = [
        r'imdb://(tt\d+)',         # imdb://tt1234567
        r'imdb//(tt\d+)',          # imdb//tt1234567 (double slash)
        r'agents\.imdb://(tt\d+)', # com.plexapp.agents.imdb://tt1234567
        r'Guid:imdb://(tt\d+)',    # Guid:imdb://tt1234567
    ]
    
    for pattern in patterns:
        imdb_match = re.search(pattern, guid_string)
        if imdb_match:
            imdb_id = imdb_match.group(1)
            log.debug(f"Extracted IMDB ID: {imdb_id}")
            return imdb_id
    
    log.debug("No IMDB ID pattern found in GUID")
    return None


############################################################
# TRAILER DOWNLOAD FUNCTIONS
############################################################

def download_trailer(youtube_video_id, target_path, title="Trailer"):
    """Download a trailer using yt-dlp with trimming options"""
    
    if not youtube_video_id:
        print(f"    ❌ No YouTube video ID provided for: {title}")
        return False
    
    youtube_url = f"https://www.youtube.com/watch?v={youtube_video_id}"
    
    # Show expected file location upfront
    expected_file = target_path.replace('%(ext)s', cfg['TRAILER_FORMAT'])
    print(f"    🎬 Downloading: {title}")
    print(f"    🔗 YouTube: https://www.youtube.com/watch?v={youtube_video_id}")
    print(f"    📁 Saving to: {expected_file}")
    
    # yt-dlp command with quality and format settings
    cmd = [
        'yt-dlp',
        '--format', cfg['TRAILER_QUALITY'],  # e.g., 'best[height<=1080]'
        '--merge-output-format', cfg['TRAILER_FORMAT'],  # e.g., 'mp4'
        '--output', target_path,
        '--no-playlist',
        youtube_url
    ]
    
    # Add trimming if configured
    if cfg.get('TRIM_START_SECONDS', 0) > 0:
        trim_seconds = cfg['TRIM_START_SECONDS']
        cmd.extend(['--download-sections', f'*{trim_seconds}-inf'])
        trim_message = f"trimming first {trim_seconds}s"
        print(f"    ✂️ Will trim first {trim_seconds} seconds")
    else:
        trim_message = "no trimming"
    
    log.debug(f"Downloading trailer: {title}")
    log.debug(f"Quality setting: {cfg['TRAILER_QUALITY']}")
    log.debug(f"Command: {' '.join(cmd)}")
    print(f"    ⬇️ Starting download ({cfg['TRAILER_QUALITY']})...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            # Find the actual downloaded file and show details
            import glob
            
            pattern = target_path.replace('%(ext)s', '*')
            matching_files = glob.glob(pattern)
            
            if matching_files:
                actual_file = matching_files[0]
                file_size = os.path.getsize(actual_file)
                file_size_mb = file_size / (1024 * 1024)
                
                log.info(f"Successfully downloaded trailer: {title}")
                print(f"    ✅ Download completed successfully!")
                print(f"    📄 File: {os.path.basename(actual_file)}")
                print(f"    📁 Full path: {actual_file}")
                print(f"    📏 Size: {file_size_mb:.1f} MB")
                
                # Try to get video resolution info
                try:
                    # Parse yt-dlp output for quality info
                    output_text = result.stderr + result.stdout
                    if output_text:
                        import re
                        # Look for various resolution patterns in yt-dlp output
                        patterns = [
                            r'(\d{3,4}x\d{3,4})',  # e.g., 1920x1080
                            r'(\d{3,4}p)',         # e.g., 1080p
                            r'height=(\d+)',       # height=1080
                        ]
                        
                        for pattern in patterns:
                            resolution_match = re.search(pattern, output_text)
                            if resolution_match:
                                print(f"    🎬 Resolution: {resolution_match.group(1)}")
                                break
                        else:
                            # If we can't parse from output, check the actual file with ffprobe
                            try:
                                probe_cmd = ['ffprobe', '-v', 'quiet', '-select_streams', 'v:0', 
                                           '-show_entries', 'stream=width,height', '-of', 'csv=p=0', actual_file]
                                probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=10)
                                if probe_result.returncode == 0:
                                    dimensions = probe_result.stdout.strip().split(',')
                                    if len(dimensions) >= 2:
                                        width, height = dimensions[0], dimensions[1]
                                        print(f"    🎬 Resolution: {width}x{height}")
                            except:
                                print(f"    🎬 Resolution: Could not determine")
                except:
                    pass  # Don't fail if we can't get quality info
                
                return True
            else:
                print(f"    ⚠️ Download may have completed but file not found")
                print(f"    🔍 Expected pattern: {pattern}")
                return False
        else:
            error_output = result.stderr.strip()
            log.error(f"yt-dlp failed: {error_output}")
            
            # Provide specific error messages
            print(f"    ❌ Download failed!")
            
            if "Video unavailable" in error_output:
                print(f"    🚫 Video is unavailable (removed or private)")
            elif "Sign in to confirm your age" in error_output:
                print(f"    🔞 Video requires age verification")
            elif "Join this channel to get access" in error_output:
                print(f"    🔒 Video requires channel membership")
            elif "Private video" in error_output:
                print(f"    🔒 Video is set to private")
            else:
                print(f"    ❓ Error: {error_output}")
            
            print(f"    🔗 Check manually: {youtube_url}")
            return False
    
    except subprocess.TimeoutExpired:
        log.error(f"Download timeout for trailer: {title}")
        print(f"    ⏰ Download timed out after 5 minutes")
        print(f"    💡 Video may be very large or connection is slow")
        return False
    except Exception as e:
        log.error(f"Error downloading trailer: {e}")
        print(f"    ❌ Unexpected error: {e}")
        print(f"    🔗 Check manually: {youtube_url}")
        return False


def get_season_trailer_target_path(season_info, trailer_title, season_directory):
    """Generate the target path for a downloaded season trailer"""
    
    # Clean up the trailer title for filename
    safe_title = re.sub(r'[<>:"/\\|?*]', '', trailer_title)
    safe_title = safe_title.replace(' ', '_')
    
    if cfg['DOWNLOAD_METHOD'] == 'inline':
        # Place alongside season episodes with -trailer suffix
        filename = f"{season_info['show']}_Season_{season_info['season']:02d}_{safe_title}-trailer.%(ext)s"
        return os.path.join(season_directory, filename)
    else:
        # Place in Trailers subdirectory
        trailers_dir = os.path.join(season_directory, cfg['TRAILER_NAMING_PATTERNS']['subdirectory_name'])
        os.makedirs(trailers_dir, exist_ok=True)
        filename = f"Season_{season_info['season']:02d}_{safe_title}.%(ext)s"
        return os.path.join(trailers_dir, filename)


############################################################
# HELPER FUNCTIONS
############################################################

def get_section_type(plex_section_name):
    """Get the type of Plex library section"""
    try:
        plex_section_type = plex.library.section(plex_section_name).type
        log.debug(f"Section {plex_section_name} is of type: {plex_section_type}")
        return plex_section_type
    except Exception:
        log.exception("Exception occurred while trying to lookup the section type for Library: %s", plex_section_name)
        exit(1)


def get_season_directory_from_episodes(episodes):
    """Get the common season directory from episodes"""
    if not episodes:
        return None
    
    # Get the directory path from the first episode
    try:
        first_episode = episodes[0]
        for media in first_episode.media:
            for part in media.parts:
                if hasattr(part, 'file') and part.file:
                    return os.path.dirname(part.file)
    except Exception as e:
        log.error(f"Error getting season directory: {e}")
    
    return None


def check_for_season_trailers_in_directory(directory_path, season_number):
    """Check for season trailers in a given directory using both naming patterns"""
    trailers_found = []
    
    if not os.path.exists(directory_path):
        log.debug(f"Directory does not exist: {directory_path}")
        return trailers_found
    
    try:
        # Check for inline trailers (files ending with -trailer.ext)
        for file in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path):
                file_stem = Path(file).stem.lower()
                file_ext = Path(file).suffix.lower()
                
                # Check if it's a video file and ends with trailer pattern
                # Also check if it contains season reference
                if (file_ext in [ext.lower() for ext in cfg['SUPPORTED_VIDEO_EXTENSIONS']] and 
                    file_stem.endswith(cfg['TRAILER_NAMING_PATTERNS']['inline_suffix']) and
                    ('season' in file_stem or f's{season_number:02d}' in file_stem or f'season_{season_number:02d}' in file_stem)):
                    trailers_found.append(file_path)
                    log.debug(f"Found inline season trailer: {file_path}")
        
        # Check for trailers in subdirectory
        trailers_dir = os.path.join(directory_path, cfg['TRAILER_NAMING_PATTERNS']['subdirectory_name'])
        if os.path.exists(trailers_dir) and os.path.isdir(trailers_dir):
            for file in os.listdir(trailers_dir):
                file_path = os.path.join(trailers_dir, file)
                if os.path.isfile(file_path):
                    file_ext = Path(file).suffix.lower()
                    if file_ext in [ext.lower() for ext in cfg['SUPPORTED_VIDEO_EXTENSIONS']]:
                        trailers_found.append(file_path)
                        log.debug(f"Found subdirectory season trailer: {file_path}")
    
    except Exception as e:
        log.error(f"Error checking for season trailers in {directory_path}: {e}")
    
    return trailers_found


############################################################
# MAIN ANALYSIS FUNCTIONS
############################################################

def analyze_tv_series():
    """Analyze TV series libraries for missing season trailers"""
    results = {
        'shows_analyzed': 0,
        'seasons_analyzed': 0,
        'seasons_with_trailers': 0,
        'seasons_without_trailers': 0,
        'missing_trailers': [],
        'trailers_downloaded': 0,
        'download_failures': 0
    }
    
    for library_name in cfg['PLEX_LIBRARIES']:
        try:
            section = plex.library.section(library_name)
            section_type = get_section_type(library_name)
            
            if section_type != 'show':
                log.info(f"Skipping library {library_name} - not a TV show library (type: {section_type})")
                continue
            
            log.info(f"Analyzing TV library: {library_name}")
            print(f"\nAnalyzing TV library: {library_name}")
            
            # Get all shows in the library
            shows = section.all()
            results['shows_analyzed'] += len(shows)
            
            for show in shows:
                print(f"  Checking show: {show.title}")
                log.info(f"Checking show: {show.title}")
                
                # Find available trailers for this show
                available_trailers = find_show_trailers(show) if cfg['DOWNLOAD_TRAILERS'] else []
                
                # Group episodes by season
                seasons = defaultdict(list)
                for episode in show.episodes():
                    seasons[episode.parentIndex].append(episode)
                
                for season_number, episodes in seasons.items():
                    if not episodes:
                        continue
                    
                    results['seasons_analyzed'] += 1
                    season_title = f"{show.title} - Season {season_number:02d}"
                    
                    # Get the season directory (from first episode)
                    season_directory = get_season_directory_from_episodes(episodes)
                    
                    if not season_directory:
                        log.warning(f"No directory found for season: {season_title}")
                        continue
                    
                    # Check if season already has trailers
                    existing_trailers = check_for_season_trailers_in_directory(season_directory, season_number)
                    
                    if existing_trailers:
                        results['seasons_with_trailers'] += 1
                        log.debug(f"Season has {len(existing_trailers)} trailer(s): {season_title}")
                    else:
                        results['seasons_without_trailers'] += 1
                        season_info = {
                            'show': show.title,
                            'season': season_number,
                            'season_title': season_title,
                            'episode_count': len(episodes),
                            'season_directory': season_directory
                        }
                        
                        # Try to download trailer if enabled
                        if cfg['DOWNLOAD_TRAILERS'] and available_trailers:
                            downloaded = attempt_season_trailer_download(season_info, available_trailers)
                            if downloaded:
                                results['trailers_downloaded'] += 1
                                results['seasons_with_trailers'] += 1
                                results['seasons_without_trailers'] -= 1
                                log.info(f"Successfully downloaded trailer for: {season_title}")
                            else:
                                results['download_failures'] += 1
                                results['missing_trailers'].append(season_info)
                                log.info(f"Failed to download trailer for: {season_title}")
                        else:
                            results['missing_trailers'].append(season_info)
                            log.info(f"Missing trailer for: {season_title}")
        
        except Exception as e:
            log.exception(f"Error analyzing library {library_name}")
            print(f"Error analyzing library {library_name}: {e}")
    
    return results


def attempt_season_trailer_download(season_info, available_trailers):
    """Attempt to download a suitable trailer for a season"""
    if not available_trailers:
        return False
    
    # Find the best trailer (prefer recent, shorter trailers)
    best_trailer = None
    for trailer in available_trailers:
        if 'youtube_video_id' not in trailer:
            continue
        
        # Prefer trailers with "Trailer" in categories
        if 'Trailer' in trailer.get('categories', []):
            best_trailer = trailer
            break
    
    if not best_trailer:
        best_trailer = available_trailers[0]  # Use first available
    
    # Download the trailer to the season directory
    season_directory = season_info['season_directory']
    target_path = get_season_trailer_target_path(season_info, best_trailer.get('title', 'Trailer'), season_directory)
    
    # Check if file already exists
    existing_files = []
    try:
        target_dir = os.path.dirname(target_path)
        if os.path.exists(target_dir):
            for f in os.listdir(target_dir):
                if f.startswith(os.path.basename(target_path).replace('.%(ext)s', '')):
                    existing_files.append(f)
    except:
        pass
    
    if existing_files and not cfg['OVERWRITE_EXISTING']:
        log.info(f"Season trailer already exists, skipping: {existing_files[0]}")
        return True
    
    success = download_trailer(
        best_trailer['youtube_video_id'], 
        target_path, 
        best_trailer.get('title', 'Trailer')
    )
    
    return success


def generate_report(results):
    """Generate a detailed report of missing season trailers"""
    report_lines = []
    
    # Header
    report_lines.append("=" * 80)
    report_lines.append("PLEX TRAILER CHECKER REPORT (SEASON-BASED)")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    # Summary
    report_lines.append("SUMMARY:")
    report_lines.append(f"  Shows analyzed: {results['shows_analyzed']}")
    report_lines.append(f"  Seasons analyzed: {results['seasons_analyzed']}")
    report_lines.append(f"  Seasons with trailers: {results['seasons_with_trailers']}")
    report_lines.append(f"  Seasons without trailers: {results['seasons_without_trailers']}")
    
    if cfg['DOWNLOAD_TRAILERS']:
        report_lines.append(f"  Trailers downloaded: {results['trailers_downloaded']}")
        report_lines.append(f"  Download failures: {results['download_failures']}")
        report_lines.append(f"  API requests made: {api_request_count}")
    
    if results['seasons_analyzed'] > 0:
        coverage_percentage = (results['seasons_with_trailers'] / results['seasons_analyzed']) * 100
        report_lines.append(f"  Season trailer coverage: {coverage_percentage:.1f}%")
    
    report_lines.append("")
    
    # Detailed missing trailers
    if results['missing_trailers']:
        report_lines.append("REMAINING MISSING SEASON TRAILERS:")
        report_lines.append("-" * 50)
        
        if cfg['REPORT_FORMAT'] == 'detailed':
            for item in results['missing_trailers']:
                report_lines.append(f"Show: {item['show']}")
                report_lines.append(f"  Season {item['season']:02d} ({item['episode_count']} episodes)")
                report_lines.append(f"  Season directory:")
                report_lines.append(f"    {item['season_directory']}")
                report_lines.append(f"  Expected trailer locations:")
                report_lines.append(f"    {item['season_directory']}/Season_{item['season']:02d}_*{cfg['TRAILER_NAMING_PATTERNS']['inline_suffix']}.[ext]")
                report_lines.append(f"    {item['season_directory']}/{cfg['TRAILER_NAMING_PATTERNS']['subdirectory_name']}/Season_{item['season']:02d}_*.[ext]")
                report_lines.append("")
        else:
            # Summary format
            show_counts = defaultdict(int)
            for item in results['missing_trailers']:
                show_counts[item['show']] += 1
            
            for show, count in sorted(show_counts.items()):
                report_lines.append(f"  {show}: {count} season(s) missing trailers")
    else:
        report_lines.append("CONGRATULATIONS! All seasons have trailers.")
    
    report_lines.append("")
    report_lines.append("=" * 80)
    
    # Write to file
    try:
        with open(cfg['OUTPUT_FILE'], 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        print(f"\nReport saved to: {cfg['OUTPUT_FILE']}")
    except Exception as e:
        log.error(f"Error writing report file: {e}")
        print(f"Error writing report file: {e}")
    
    # Also print to console
    print("\n" + "\n".join(report_lines))
    
    return report_lines


############################################################
# MAIN
############################################################

if __name__ == "__main__":
    print("""
 ____  _              _____           _ _            ____ _               _             
|  _ \| | _____  __  |_   _| __ __ _ (_) | ___ _ __ / ___| |__   ___  ___| | _____ _ __ 
| |_) | |/ _ \ \/ /    | || '__/ _` || | |/ _ \ '__| |   | '_ \ / _ \/ __| |/ / _ \ '__|
|  __/| |  __/>  <     | || | | (_| || | |  __/ |  | |___| | | |  __/ (__|   <  __/ |   
|_|   |_|\___/_/\_\    |_||_|  \__,_||_|_|\___|_|   \____|_| |_|\___|\___|_|\_\___|_|   

#############################################################################
# Enhanced with KinoCheck API Integration - SEASON-BASED TRAILERS          #
# Purpose:  Download one trailer per season for Plex TV series             #
#############################################################################
""")
    
    print("Initializing...")
    log.info("Starting Plex Trailer Checker with KinoCheck API (Season-based)")
    
    if not cfg['CHECK_SERIES']:
        print("TV Series checking is disabled in configuration.")
        log.info("TV Series checking is disabled")
        exit(0)
    
    # Check if yt-dlp is available for downloading
    if cfg['DOWNLOAD_TRAILERS']:
        try:
            subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
            print("✓ yt-dlp found - trailer downloading enabled")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("✗ yt-dlp not found - disabling trailer downloads")
            print("  Install with: pip install yt-dlp")
            cfg['DOWNLOAD_TRAILERS'] = False
    
    # Analyze TV series for missing season trailers
    print("Scanning Plex libraries for missing season trailers...")
    if cfg['DOWNLOAD_TRAILERS']:
        print("Will download one trailer per season using KinoCheck API...")
    
    results = analyze_tv_series()
    
    # Generate and display report
    generate_report(results)
    
    print("\nSeason trailer check complete!")
    if cfg['DOWNLOAD_TRAILERS']:
        print(f"Downloaded {results['trailers_downloaded']} season trailers")
        print(f"Failed downloads: {results['download_failures']}")
    
    log.info("Season trailer check completed") 