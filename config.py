#!/usr/bin/env python3

import json
import os
import sys

from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from getpass import getpass

config_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'config.json')
base_config = {
    'PLEX_SERVER': 'https://plex.your-server.com',
    'PLEX_TOKEN': '',
    'PLEX_LIBRARIES': ['TV Shows'],  # Start with TV shows, can add Movies later
    'CHECK_SERIES': True,
    'CHECK_MOVIES': False,  # For future implementation
    'TRAILER_NAMING_PATTERNS': {
        'inline_suffix': '-trailer',  # e.g., Episode_Name-trailer.mp4
        'subdirectory_name': 'Trailers'  # e.g., Season 01/Trailers/trailer.mp4
    },
    'SUPPORTED_VIDEO_EXTENSIONS': ['.mp4', '.mkv', '.avi', '.mov', '.m4v', '.wmv'],
    'REPORT_FORMAT': 'detailed',  # 'detailed' or 'summary'
    'OUTPUT_FILE': 'missing_trailers_report.txt',
    
    # KinoCheck API Configuration
    'KINOCHECK_API': {
        'enabled': True,
        'base_url': 'https://api.kinocheck.de',
        'api_key': '',  # Optional: for higher rate limits
        'language': 'de',  # 'de' or 'en'
        'fallback_language': 'en',  # Try this language if primary fails
        'max_requests_per_day': 1000
    },
    
    # Trailer Download Configuration
    'DOWNLOAD_TRAILERS': True,
    'DOWNLOAD_METHOD': 'subdirectory',  # 'inline' or 'subdirectory'
    'TRAILER_QUALITY': 'bestvideo[height<=2160]+bestaudio/bestvideo[height<=1080]+bestaudio/best',  # Best video+audio combo
    'TRAILER_FORMAT': 'mp4',
    'MAX_TRAILER_DURATION': 600,  # Maximum trailer length in seconds (10 minutes)
    'TRIM_START_SECONDS': 3,  # Skip first N seconds of each trailer (removes intro branding)
    'OVERWRITE_EXISTING': False,
    

    
    # VPN Configuration (Private Internet Access)
    'VPN': {
        'enabled': False,  # Set to True to use VPN for downloads
        'provider': 'pia',  # Currently only 'pia' supported
        'pia_username': '',  # Your PIA username (p1234567)
        'pia_password': '',  # Your PIA password
        'protocol': 'wireguard',  # 'wireguard' or 'openvpn'
        'auto_region': True,  # Auto-select best region
        'preferred_region': '',  # Specific region (e.g., 'us_california', 'de_berlin')
        'connect_timeout': 60,  # Seconds to wait for connection
        'disconnect_after_downloads': True,  # Disconnect VPN when done
        'setup_path': './pia-manual'  # Where to install PIA scripts
    },
    
    # Remote Server Transfer (if not running on Plex server)
    'REMOTE_TRANSFER': {
        'enabled': False,  # Set to True to enable automatic transfer after download
        'method': 'rsync',  # 'rsync' or 'scp'
        'server': 'user@plex-server.com',
        'remote_path': '/path/to/plex/media/',
        'ssh_key': '',  # Optional: path to SSH private key
        'delete_local_after_transfer': True  # Delete local files after successful transfer
    },
    
    # Show/Episode Matching
    'MATCHING': {
        'use_tmdb_ids': True,
        'use_imdb_ids': True,
        'fallback_to_title_search': True,
        'min_match_confidence': 0.8
    }
}
cfg = None


def get_plex_libraries(plex_server, plex_token):
    """Connect to Plex and get all available libraries"""
    try:
        plex = PlexServer(plex_server, plex_token)
        libraries = []
        
        for section in plex.library.sections():
            libraries.append({
                'name': section.title,
                'type': section.type,
                'key': section.key
            })
        
        return libraries
    except Exception as e:
        print(f"Error connecting to Plex server: {e}")
        return []


def select_libraries(libraries):
    """Let user select which libraries to use for TV shows and movies"""
    if not libraries:
        print("No libraries found. Using default configuration.")
        return ['TV Shows']
    
    print("\nAvailable Plex Libraries:")
    print("-" * 40)
    for i, lib in enumerate(libraries):
        print(f"{i+1:2}. {lib['name']:<25} (Type: {lib['type']})")
    
    selected_libraries = []
    
    # Select TV Show libraries
    print(f"\nSelect TV Show libraries (for series trailer checking):")
    print("Enter numbers separated by commas (e.g., 1,3) or press Enter to skip:")
    tv_input = input("TV Show libraries: ").strip()
    
    if tv_input:
        try:
            tv_indices = [int(x.strip()) - 1 for x in tv_input.split(',')]
            for idx in tv_indices:
                if 0 <= idx < len(libraries):
                    lib = libraries[idx]
                    selected_libraries.append(lib['name'])
                    print(f"✓ Added TV library: {lib['name']}")
        except ValueError:
            print("Invalid input. Please enter numbers separated by commas.")
    
    # Select Movie libraries (for future use)
    print(f"\nSelect Movie libraries (for future movie trailer checking):")
    print("Enter numbers separated by commas (e.g., 2,4) or press Enter to skip:")
    movie_input = input("Movie libraries: ").strip()
    
    movie_libraries = []
    if movie_input:
        try:
            movie_indices = [int(x.strip()) - 1 for x in movie_input.split(',')]
            for idx in movie_indices:
                if 0 <= idx < len(libraries):
                    lib = libraries[idx]
                    movie_libraries.append(lib['name'])
                    print(f"✓ Added Movie library: {lib['name']}")
        except ValueError:
            print("Invalid input. Please enter numbers separated by commas.")
    
    if not selected_libraries and not movie_libraries:
        print("No libraries selected. Using first available library as default.")
        selected_libraries = [libraries[0]['name']]
    
    return selected_libraries, movie_libraries


def prefilled_default_config(configs):
    try:
        plex_server = input("Plex Server URL: ")
        plex_username = input("Plex Username: ")
        plex_password = getpass("Plex Password: ")
        
        if plex_server and plex_username and plex_password:
            account = MyPlexAccount(plex_username, plex_password)
            configs['PLEX_SERVER'] = plex_server
            configs['PLEX_TOKEN'] = account.authenticationToken
            print(f"Successfully obtained token: {configs['PLEX_TOKEN'][:10]}...")
            
            # Fetch and select libraries
            print("\nFetching available Plex libraries...")
            libraries = get_plex_libraries(plex_server, configs['PLEX_TOKEN'])
            
            if libraries:
                tv_libraries, movie_libraries = select_libraries(libraries)
                configs['PLEX_LIBRARIES'] = tv_libraries
                
                # Update check settings based on selections
                configs['CHECK_SERIES'] = len(tv_libraries) > 0
                configs['CHECK_MOVIES'] = len(movie_libraries) > 0
                
                print(f"\nConfiguration updated:")
                print(f"✓ TV Libraries: {tv_libraries}")
                print(f"✓ Movie Libraries: {movie_libraries}")
                print(f"✓ Check TV Series: {configs['CHECK_SERIES']}")
                print(f"✓ Check Movies: {configs['CHECK_MOVIES']}")
            else:
                # Fallback to manual entry
                check_series = input("Check TV Series for trailers? [y/n]: ").lower()
                configs['CHECK_SERIES'] = check_series == 'y'
                
                check_movies = input("Check Movies for trailers? [y/n]: ").lower()
                configs['CHECK_MOVIES'] = check_movies == 'y'
        
        download_trailers = input("Automatically download missing trailers? [y/n]: ").lower()
        configs['DOWNLOAD_TRAILERS'] = download_trailers == 'y'
        
        if configs['DOWNLOAD_TRAILERS']:
            method = input("Download method - (i)nline or (s)ubdirectory? [i/s]: ").lower()
            configs['DOWNLOAD_METHOD'] = 'inline' if method == 'i' else 'subdirectory'
            
            # Ask about quality preference
            print("\nTrailer quality preference:")
            print("  1. 4K/2160p preferred (falls back to 1080p if unavailable)")
            print("  2. 1080p maximum") 
            print("  3. Best available (any resolution)")
            quality_choice = input("Choose quality [1/2/3]: ").strip()
            
            if quality_choice == '1':
                configs['TRAILER_QUALITY'] = 'bestvideo[height<=2160]+bestaudio/bestvideo[height<=1080]+bestaudio/best'
            elif quality_choice == '2':
                configs['TRAILER_QUALITY'] = 'bestvideo[height<=1080]+bestaudio/best'
            elif quality_choice == '3':
                configs['TRAILER_QUALITY'] = 'best'
            else:
                # Default to 4K preferred
                configs['TRAILER_QUALITY'] = 'bestvideo[height<=2160]+bestaudio/bestvideo[height<=1080]+bestaudio/best'
            
            # Ask about trimming
            trim_input = input("Skip first few seconds of trailers (removes intro branding)? [y/n]: ").lower()
            if trim_input == 'y':
                trim_seconds = input("How many seconds to skip at start? [3]: ").strip()
                try:
                    configs['TRIM_START_SECONDS'] = int(trim_seconds) if trim_seconds else 3
                except ValueError:
                    configs['TRIM_START_SECONDS'] = 3
            else:
                configs['TRIM_START_SECONDS'] = 0
            
            language = input("Preferred trailer language - (d)eutsch or (e)nglish? [d/e]: ").lower()
            primary_lang = 'de' if language == 'd' else 'en'
            fallback_lang = 'en' if primary_lang == 'de' else 'de'
            
            configs['KINOCHECK_API']['language'] = primary_lang
            configs['KINOCHECK_API']['fallback_language'] = fallback_lang
        
        api_key = input("KinoCheck API key (optional, press Enter to skip): ").strip()
        if api_key:
            configs['KINOCHECK_API']['api_key'] = api_key
        
        # Ask about VPN for geo-blocking bypass
        print(f"\n🌐 VPN Configuration (for geo-blocking bypass):")
        print(f"If trailers are blocked in your region, you can use a VPN.")
        vpn_enabled = input("Use Private Internet Access (PIA) VPN for downloads? [y/n]: ").lower()
        configs['VPN']['enabled'] = vpn_enabled == 'y'
        
        if configs['VPN']['enabled']:
            print(f"\nYou'll need a PIA account. Get one at: https://www.privateinternetaccess.com/")
            pia_username = input("PIA Username (e.g., p1234567): ").strip()
            pia_password = input("PIA Password: ").strip()
            
            configs['VPN']['pia_username'] = pia_username
            configs['VPN']['pia_password'] = pia_password
            
            print(f"\nVPN Protocol:")
            print(f"  1. WireGuard (recommended - faster, modern)")
            print(f"  2. OpenVPN (traditional, widely supported)")
            protocol_choice = input("Choose protocol [1/2]: ").strip()
            configs['VPN']['protocol'] = 'wireguard' if protocol_choice != '2' else 'openvpn'
            
            auto_region = input("Auto-select best region? [y/n]: ").lower()
            configs['VPN']['auto_region'] = auto_region == 'y'
            
            if not configs['VPN']['auto_region']:
                print(f"Common regions: us_california, us_newyork, de_berlin, uk_london, nl_amsterdam")
                region = input("Preferred region (leave blank for auto): ").strip()
                configs['VPN']['preferred_region'] = region
        
    except Exception as e:
        print(f"Error during configuration: {e}")
        print("Please edit the configuration file manually")
    
    return configs


def build_config():
    print(f"Dumping default config to: {config_path}")
    
    updated_cfg = prefilled_default_config(base_config.copy())
    
    with open(config_path, 'w') as fp:
        json.dump(updated_cfg, fp, indent=4, sort_keys=True)
    
    print("Please edit the default configuration before running again!")
    exit(0)


def dump_config():
    with open(config_path, 'w') as fp:
        json.dump(cfg, fp, indent=4, sort_keys=True)


def load_config():
    with open(config_path, 'r') as fp:
        return json.load(fp)


def upgrade_settings(defaults, currents):
    upgraded = False

    def inner_upgrade(default, current, key=None):
        nonlocal upgraded
        res = current.copy() if isinstance(current, dict) else current
        
        if isinstance(default, dict):
            for k, v in default.items():
                if k not in res:
                    res[k] = v
                    upgraded = True
                    if key:
                        print(f"Added new config option: {key}.{k} = {v}")
                    else:
                        print(f"Added new config option: {k} = {v}")
                else:
                    res[k] = inner_upgrade(default[k], res[k], key=k if not key else f"{key}.{k}")
        return res

    upgraded_settings = inner_upgrade(defaults, currents)
    return upgraded_settings, upgraded


# Load config
if os.path.exists(config_path):
    cfg = load_config()
    upgraded_cfg, upgraded = upgrade_settings(base_config, cfg)
    if upgraded:
        cfg = upgraded_cfg
        dump_config()
        print("Configuration has been upgraded with new options")
else:
    build_config() 