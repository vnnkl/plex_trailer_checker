# Plex Trailer Checker with KinoCheck API Integration

An advanced Python script that scans your Plex libraries to identify missing TV series trailers and **automatically downloads them** using the [KinoCheck API](https://api.kinocheck.de/). Based on the architecture of [plex_dupefinder](https://github.com/l3uddz/plex_dupefinder), this tool helps you maintain a complete collection of **season trailers** for your Plex media.

## 🚀 New Features

- 🎬 **Automatic Season Trailer Downloads**: Fetches and downloads one trailer per season using the KinoCheck API
- 🌐 **Multi-language Support**: German and English trailers via KinoCheck
- 🎯 **Smart Matching**: Uses TMDB/IMDB IDs from Plex for accurate trailer finding
- 📊 **Enhanced Reporting**: Shows download progress and API usage statistics
- ⚡ **Rate Limiting**: Respects API limits (1000 requests/day free tier)
- 🎪 **Season-Based**: Downloads one trailer per season (not per episode) for efficiency
- 🎥 **High Quality Downloads**: Supports 4K/2160p and 1080p with intelligent fallbacks
- ✂️ **Smart Trimming**: Automatically removes intro branding/logos from trailers
- 📍 **Detailed Logging**: Shows exact file paths, sizes, and resolution of downloaded trailers
- 🌐 **VPN Integration**: Built-in Private Internet Access (PIA) support for bypassing geo-blocking

## Features

- 🔍 **Automatic Detection**: Scans TV series libraries for missing season trailers
- 📁 **Multiple Naming Patterns**: Supports both inline (`-trailer` suffix) and subdirectory (`Trailers/`) naming conventions
- 📊 **Detailed Reporting**: Generates comprehensive reports with missing trailer locations
- 🔧 **Easy Configuration**: Simple JSON-based configuration similar to plex_dupefinder
- 📝 **Extensive Logging**: Detailed logging for troubleshooting
- 🎯 **Extensible**: Designed to easily add movie support in the future

## Supported Trailer Naming Conventions

According to [Plex's official documentation](https://support.plex.tv/articles/local-files-for-trailers-and-extras/), trailers can be organized in two ways:

### Inline Method
Place trailers alongside season episodes with `-trailer` suffix:
```
/TV Shows/Show Name (Year)/Season 01/
  ├── Episode 01 - Episode Title.mkv
  ├── Episode 02 - Episode Title.mkv
  └── Show_Name_Season_01_Trailer-trailer.mp4
```

### Subdirectory Method (Recommended)
Place trailers in a dedicated `Trailers` subfolder:
```
/TV Shows/Show Name (Year)/Season 01/
  ├── Episode 01 - Episode Title.mkv
  ├── Episode 02 - Episode Title.mkv
  └── Trailers/
      └── Season_01_Official_Trailer.mp4
```

## Requirements

- Python 3.6+
- Plex Media Server with API access
- Plex Pass (recommended for full trailer feature support)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for downloading trailers
- Internet connection for KinoCheck API access

## Installation

1. **Clone or download the script files:**
   ```bash
   # Create a directory for the trailer checker
   mkdir plex_trailer_checker
   cd plex_trailer_checker
   
   # Copy the script files from the plex_trailer_checker folder
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install yt-dlp** (required for downloading):
   ```bash
   pip install yt-dlp
   # or
   pip install --upgrade yt-dlp
   ```

4. **Make the script executable (optional):**
   ```bash
   chmod +x plex_trailer_checker.py
   ```

## Configuration

1. **Run the script for the first time** to generate a configuration file:
   ```bash
   python3 plex_trailer_checker.py
   ```

2. **Follow the prompts** to configure your Plex server:
   ```
   Plex Server URL: http://your-plex-server:32400
   Plex Username: your_username
   Plex Password: [hidden]
   Check TV Series for trailers? [y/n]: y
   Check Movies for trailers? [y/n]: n
   Automatically download missing trailers? [y/n]: y
   Download method - (i)nline or (s)ubdirectory? [i/s]: s
   Preferred trailer language - (d)eutsch or (e)nglish? [d/e]: d
   KinoCheck API key (optional, press Enter to skip): 
   ```

3. **Edit the configuration file** (`config.json`) if needed:
   ```json
   {
       "CHECK_MOVIES": false,
       "CHECK_SERIES": true,
       "DOWNLOAD_TRAILERS": true,
       "DOWNLOAD_METHOD": "subdirectory",
       "KINOCHECK_API": {
           "api_key": "",
           "base_url": "https://api.kinocheck.de",
           "enabled": true,
           "language": "de",
           "max_requests_per_day": 1000
       },
       "MATCHING": {
           "fallback_to_title_search": true,
           "min_match_confidence": 0.8,
           "use_imdb_ids": true,
           "use_tmdb_ids": true
       },
       "OUTPUT_FILE": "missing_trailers_report.txt",
       "OVERWRITE_EXISTING": false,
       "PLEX_LIBRARIES": ["TV Shows"],
       "PLEX_SERVER": "http://your-plex-server:32400",
       "PLEX_TOKEN": "your_plex_token_here",
       "REPORT_FORMAT": "detailed",
       "TRAILER_FORMAT": "mp4",
       "TRAILER_QUALITY": "best[height<=1080]"
   }
   ```

## Usage

Simply run the script:
```bash
python3 plex_trailer_checker.py
```

The script will:
1. Connect to your Plex server
2. Scan all configured TV libraries
3. Group episodes by season
4. Extract TMDB/IMDB IDs from Plex metadata
5. Query KinoCheck API for available trailers
6. Download one trailer per season to the correct locations
7. Generate a detailed report of results

## How Season-Based Trailers Work

Instead of downloading a trailer for each episode (which would be excessive), the script:

1. **Groups episodes by season** for each show
2. **Checks if the season already has a trailer** in the season directory
3. **Downloads one trailer per season** if missing
4. **Places the trailer** in the season folder using Plex-compatible naming

This approach is:
- ✅ **More realistic** - TV series typically have season trailers, not episode trailers
- ✅ **More efficient** - Fewer API calls and downloads
- ✅ **Better organized** - One trailer per season folder
- ✅ **Plex compatible** - Follows Plex trailer conventions

## Configuration Options

### Core Settings

- **`PLEX_SERVER`**: Your Plex server URL (e.g., `http://localhost:32400`)
- **`PLEX_TOKEN`**: Plex authentication token (auto-generated during setup)
- **`PLEX_LIBRARIES`**: List of Plex library names to scan (e.g., `["TV Shows", "Anime"]`)

### Feature Toggles

- **`CHECK_SERIES`**: Enable/disable TV series scanning (`true`/`false`)
- **`CHECK_MOVIES`**: Enable/disable movie scanning (`true`/`false`) - *Future feature*
- **`DOWNLOAD_TRAILERS`**: Enable/disable automatic trailer downloading

### KinoCheck API Settings

- **`KINOCHECK_API.enabled`**: Enable/disable API usage
- **`KINOCHECK_API.language`**: Preferred language (`"de"` or `"en"`)
- **`KINOCHECK_API.api_key`**: Optional API key for higher rate limits
- **`KINOCHECK_API.max_requests_per_day`**: Daily request limit

### Download Settings

- **`DOWNLOAD_METHOD`**: Where to place trailers (`"inline"` or `"subdirectory"`)
- **`TRAILER_QUALITY`**: Video quality selection:
  - `"best[height<=2160]/best[height<=1080]/best"` - Prefer 4K, fallback to 1080p
  - `"best[height<=1080]"` - Maximum 1080p
  - `"best"` - Best available quality (any resolution)
- **`TRAILER_FORMAT`**: Target video format (`"mp4"`, `"mkv"`, etc.)
- **`TRIM_START_SECONDS`**: Skip first N seconds (removes intro branding/logos)
- **`OVERWRITE_EXISTING`**: Whether to overwrite existing trailer files

### VPN Settings (Geo-blocking Bypass)

- **`VPN.enabled`**: Enable/disable VPN usage for downloads
- **`VPN.provider`**: VPN provider (`"pia"` - Private Internet Access)
- **`VPN.pia_username`**: Your PIA username (e.g., `p1234567`)
- **`VPN.pia_password`**: Your PIA password
- **`VPN.protocol`**: VPN protocol (`"wireguard"` or `"openvpn"`)
- **`VPN.auto_region`**: Auto-select best region (`true`/`false`)
- **`VPN.preferred_region`**: Specific region (e.g., `"us_california"`, `"de_berlin"`)
- **`VPN.disconnect_after_downloads`**: Disconnect VPN when finished

### Matching Options

- **`MATCHING.use_tmdb_ids`**: Use TMDB IDs for trailer lookup
- **`MATCHING.use_imdb_ids`**: Use IMDB IDs for trailer lookup
- **`MATCHING.fallback_to_title_search`**: Enable title-based fallback

## Example Output

### Console Output
```
Plex Trailer Checker
#############################################################################

Initializing...
✓ yt-dlp found - trailer downloading enabled

Analyzing TV library: TV Shows
Will download one trailer per season using KinoCheck API...

  Checking show: Ironheart (2025)
    Downloading: IRONHEART Trailer German Deutsch (2025)
  Checking show: The Office
  Checking show: Stranger Things

Report saved to: missing_trailers_report.txt

SUMMARY:
  Shows analyzed: 3
  Seasons analyzed: 28
  Seasons with trailers: 15
  Seasons without trailers: 13
  Trailers downloaded: 10
  Download failures: 3
  API requests made: 5
  Season trailer coverage: 53.6%

Downloaded 10 season trailers
Failed downloads: 3

Season trailer check complete!
```

### Enhanced Report
```
================================================================================
PLEX TRAILER CHECKER REPORT (SEASON-BASED)
================================================================================
Generated: 2025-01-29 16:30:45

SUMMARY:
  Shows analyzed: 2
  Seasons analyzed: 12
  Seasons with trailers: 8
  Seasons without trailers: 4
  Trailers downloaded: 6
  Download failures: 2
  API requests made: 3
  Season trailer coverage: 66.7%

REMAINING MISSING SEASON TRAILERS:
--------------------------------------------------
Show: Ironheart (2025)
  Season 01 (6 episodes)
  Season directory:
    /APPBOX_DATA/apps/.../Ironheart (2025) {imdb-tt13623126}/Season 01
  Expected trailer locations:
    /APPBOX_DATA/.../Season 01/Season_01_*-trailer.[ext]
    /APPBOX_DATA/.../Season 01/Trailers/Season_01_*.[ext]
```

## File Structure

For above example:
```
/APPBOX_DATA/apps/yourappboxserverURL/Downloads/complete/Serien/Ironheart (2025) {imdb-tt13623126}/Season 01/Ironheart - S01E01 - Take Me Home WEBDL-2160p.mkv
```

### 1. Season Grouping
The script groups all episodes in the season:
- Season 01: Episodes 01-06 (or however many exist)

### 2. Metadata Extraction
Extracts the IMDB ID `tt13623126` from your folder name or Plex metadata.

### 3. API Query
Queries KinoCheck API: `GET /shows?imdb_id=tt13623126&language=de&categories=Trailer`

### 4. Season Trailer Download
If trailers are found, downloads one per season to:
```
/APPBOX_DATA/.../Season 01/Trailers/Season_01_IRONHEART_Trailer_Deutsch.mp4
```

## API Rate Limits

The KinoCheck API provides:
- **Free Tier**: 1,000 requests per day
- **With API Key**: Higher limits available (register at [KinoCheck](https://api.kinocheck.de/))

The script automatically tracks and respects these limits. With season-based downloads, you'll use far fewer API calls!

## Troubleshooting

### Common Issues

**"yt-dlp not found"**
```bash
pip install yt-dlp
# or update
pip install --upgrade yt-dlp
```

**"API request limit reached"**
- Wait until the next day for limit reset
- Register for a KinoCheck API key for higher limits

**"No trailers found"**
- Check if the show has TMDB/IMDB metadata in Plex
- Verify the show exists in the KinoCheck database
- Try switching between German (`de`) and English (`en`) language settings

**Download failures**
- Switch language settings in config.json (try both 'de' and 'en')
- Try VPN bypass: Enable VPN in config and get a PIA account
- Verify YouTube videos are accessible in your region
- Check internet connection and available disk space

**VPN connection issues**
- Test VPN setup: `python3 test_pia_vpn.py`
- Ensure sudo access is available: `sudo -n true`
- Verify PIA credentials are correct
- Try different protocol (WireGuard ↔ OpenVPN)
- Check PIA account is active and has remaining time

### Connection Issues
- Ensure your Plex server URL is correct and accessible
- Verify your Plex token is valid
- Check that your Plex server allows API access

### Permission Errors
- Ensure the script has write access to your media directories
- On Linux/macOS, you may need to run with appropriate permissions

## File Structure

Your script directory should look like this:
```
plex_trailer_checker/
├── plex_trailer_checker.py     # Main script
├── config.py                   # Configuration module
├── requirements.txt            # Python dependencies
├── README.md                   # This README
├── config.json                 # Generated configuration (after first run)
├── trailer_checker.log         # Generated log file
└── missing_trailers_report.txt # Generated report
```

## Advanced Usage

### Custom Download Quality
Modify `TRAILER_QUALITY` in config.json:
```json
"TRAILER_QUALITY": "best[height<=720]"  // 720p max
"TRAILER_QUALITY": "worst[height>=480]" // 480p min
"TRAILER_QUALITY": "best[filesize<100M]" // Under 100MB
```

### API Key Registration
For higher rate limits, register at [KinoCheck API](https://api.kinocheck.de/) and add your key:
```json
"KINOCHECK_API": {
    "api_key": "your_api_key_here"
}
```

## Benefits of Season-Based Approach

| Episode-Based (Old) | Season-Based (New) |
|---------------------|---------------------|
| 100+ API calls for large shows | 1 API call per show |
| 100+ trailer downloads | 1 trailer per season |
| Cluttered episode folders | Clean season organization |
| Unrealistic (episodes rarely have individual trailers) | Realistic (seasons typically have trailers) |
| High bandwidth usage | Efficient bandwidth usage |

## Contributing

This script is based on the excellent structure of [plex_dupefinder](https://github.com/l3uddz/plex_dupefinder) and enhanced with [KinoCheck API](https://api.kinocheck.de/) integration.

Feel free to submit issues or pull requests to improve the script!

## License

This project follows the same GPL v3 license as the original plex_dupefinder project.

## Credits

- **Original Architecture**: [l3uddz/plex_dupefinder](https://github.com/l3uddz/plex_dupefinder)
- **Trailer Data**: [KinoCheck API](https://api.kinocheck.de/)
- **Download Engine**: [yt-dlp](https://github.com/yt-dlp/yt-dlp) 