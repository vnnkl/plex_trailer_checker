# Enhanced Usage Example with KinoCheck API Integration (Season-Based)

Based on your example file path:
```
/APPBOX_DATA/apps/yourappboxserverURL/Downloads/complete/Serien/Ironheart (2025) {imdb-tt13623126}/Season 01/Ironheart - S01E01 - Take Me Home WEBDL-2160p.mkv
```

## How the Enhanced Season-Based Script Works

### 1. Plex Detection & Season Grouping
The script connects to your Plex server and discovers all episodes:
- **Show**: Ironheart (2025)
- **Season**: 01 (6 episodes)
- **IMDB ID**: `tt13623126` (extracted from folder name or Plex metadata)
- **Season Directory**: `/APPBOX_DATA/apps/ubuntu.verbergwest.appboxes.co/Downloads/complete/Serien/Ironheart (2025) {imdb-tt13623126}/Season 01/`

### 2. KinoCheck API Query (Once Per Show)
The script queries the KinoCheck API for available trailers:
```http
GET https://api.kinocheck.de/shows?imdb_id=tt13623126&language=de&categories=Trailer
```

**API Response Example:**
```json
{
  "id": "abc123",
  "tmdb_id": 114695,
  "imdb_id": "tt13623126",
  "language": "de",
  "title": "Ironheart",
  "videos": [
    {
      "id": "xyz789",
      "youtube_video_id": "dQw4w9WgXcQ",
      "title": "IRONHEART Season 1 Trailer German Deutsch (2025)",
      "language": "de",
      "categories": ["Trailer"],
      "published": "2024-12-15T10:00:00+01:00"
    }
  ]
}
```

### 3. Season Trailer Check & Download
The script checks if Season 01 already has a trailer, and if not, downloads one:

#### Console Output:
```
  Checking show: Ironheart (2025)
    Season 01: No existing trailer found
    Downloading: IRONHEART Season 1 Trailer German Deutsch (2025)
    ✓ Successfully downloaded to: /APPBOX_DATA/.../Season 01/Trailers/Season_01_IRONHEART_Season_1_Trailer_German_Deutsch.mp4
```

### 4. File Organization
The downloaded trailer is placed at the season level:

#### Subdirectory Method (Default):
```
/APPBOX_DATA/apps/.../Season 01/
├── Ironheart - S01E01 - Take Me Home WEBDL-2160p.mkv
├── Ironheart - S01E02 - Born to Run WEBDL-2160p.mkv
├── Ironheart - S01E03 - Armor Yourself WEBDL-2160p.mkv
├── ... (other episodes)
└── Trailers/
    └── Season_01_IRONHEART_Season_1_Trailer_German_Deutsch.mp4
```

#### Inline Method (Alternative):
```
/APPBOX_DATA/apps/.../Season 01/
├── Ironheart - S01E01 - Take Me Home WEBDL-2160p.mkv
├── Ironheart - S01E02 - Born to Run WEBDL-2160p.mkv
├── ... (other episodes)
└── Ironheart_Season_01_IRONHEART_Season_1_Trailer_German_Deutsch-trailer.mp4
```

## Sample Enhanced Season-Based Report

```
================================================================================
PLEX TRAILER CHECKER REPORT (SEASON-BASED)
================================================================================
Generated: 2025-01-29 17:15:32

SUMMARY:
  Shows analyzed: 3
  Seasons analyzed: 15
  Seasons with trailers: 12
  Seasons without trailers: 3
  Trailers downloaded: 8
  Download failures: 1
  API requests made: 4
  Season trailer coverage: 80.0%

DOWNLOADED TRAILERS:
--------------------------------------------------
✓ Ironheart Season 01 - IRONHEART Season 1 Trailer German Deutsch (2025)
✓ The Office Season 02 - THE OFFICE Season 2 Official Trailer
✓ The Office Season 03 - THE OFFICE Season 3 Sneak Peek
✓ Breaking Bad Season 01 - BREAKING BAD Season 1 Trailer Deutsch
✓ Breaking Bad Season 02 - BREAKING BAD Season 2 Official Trailer
✓ Breaking Bad Season 03 - BREAKING BAD Season 3 Promo German
✓ Breaking Bad Season 04 - BREAKING BAD Season 4 Trailer
✓ Breaking Bad Season 05 - BREAKING BAD Final Season Trailer

DOWNLOAD FAILURES:
--------------------------------------------------
✗ Stranger Things Season 04 - No trailers found in KinoCheck database

REMAINING MISSING SEASON TRAILERS:
--------------------------------------------------
Show: Stranger Things
  Season 04 (9 episodes)
  Season directory:
    /path/to/Stranger Things/Season 04
  Expected trailer locations:
    /path/to/Stranger Things/Season 04/Season_04_*-trailer.[ext]
    /path/to/Stranger Things/Season 04/Trailers/Season_04_*.[ext]

API USAGE:
--------------------------------------------------
  Requests made: 4 / 1000 daily limit
  Shows queried: 3
  Seasons processed: 15
  Success rate: 93.3%
```

## Configuration for Your Setup

Your `config.json` for German season trailers:
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
    "PLEX_LIBRARIES": [
        "Serien",
        "TV Shows"
    ],
    "PLEX_SERVER": "http://your-server:32400",
    "PLEX_TOKEN": "your_token_here",
    "REPORT_FORMAT": "detailed",
    "TRAILER_FORMAT": "mp4",
    "TRAILER_NAMING_PATTERNS": {
        "inline_suffix": "-trailer",
        "subdirectory_name": "Trailers"
    },
    "TRAILER_QUALITY": "best[height<=1080]"
}
```

## Step-by-Step Workflow

### 1. Initial Setup
```bash
cd plex_trailer_checker
python3 plex_trailer_checker.py
# Follow configuration prompts
```

### 2. Run the Enhanced Season-Based Script
```bash
python3 plex_trailer_checker.py
```

**Console Output:**
```
Plex Trailer Checker
#############################################################################

Initializing...
✓ yt-dlp found - trailer downloading enabled

Analyzing TV library: Serien
Will download one trailer per season using KinoCheck API...

  Checking show: Ironheart (2025)
    Found IMDB ID: tt13623126
    Querying KinoCheck API for trailers...
    Found 3 available trailers
    
    Season 01: No existing trailer found
    Downloading: IRONHEART Season 1 Trailer German Deutsch (2025)
    ✓ Downloaded to: /APPBOX_DATA/.../Season 01/Trailers/

  Checking show: The Office
    Season 01: Existing trailer found, skipping
    Season 02: No existing trailer found
    Downloading: THE OFFICE Season 2 Official Trailer
    ✓ Downloaded to: /path/to/The Office/Season 02/Trailers/

Report saved to: missing_trailers_report.txt

Downloaded 2 season trailers
Failed downloads: 0

Season trailer check complete!
```

### 3. Verify Results
Check your season folders:
```bash
ls "/APPBOX_DATA/apps/.../Season 01/Trailers/"
```

Expected files:
```
Season_01_IRONHEART_Season_1_Trailer_German_Deutsch.mp4
```

## Benefits of Season-Based Approach

### Efficiency Comparison

| Approach | API Calls | Downloads | Organization |
|----------|-----------|-----------|--------------|
| **Episode-Based** | 1 call per episode (100+) | 1 trailer per episode (100+) | Cluttered episode folders |
| **Season-Based** | 1 call per show (1) | 1 trailer per season (1-10) | Clean season organization |

### Real-World Example

For a show like **The Office** (9 seasons, 201 episodes):

**Episode-Based (Old Way):**
- 201 API calls
- 201 potential trailer downloads
- 201 trailer files scattered across episode folders

**Season-Based (New Way):**
- 1 API call
- 9 season trailer downloads max
- 9 trailer files organized by season

### File Organization Benefits

**Before (Episode-Based):**
```
Season 01/
├── Episode 01.mkv
├── Episode 01-trailer.mp4  ← Cluttered
├── Episode 02.mkv
├── Episode 02-trailer.mp4  ← Cluttered
└── ... (98 more files)
```

**After (Season-Based):**
```
Season 01/
├── Episode 01.mkv
├── Episode 02.mkv
├── ... (all episodes)
└── Trailers/
    └── Season_01_Official_Trailer.mp4  ← Clean organization
```

## Advanced Features

### Multi-Season Shows
For shows with multiple seasons:
```json
"TRAILER_QUALITY": "best[height<=1080]"
```

The script processes each season independently:
- Season 01: Gets its own trailer
- Season 02: Gets its own trailer  
- Season 03: Gets its own trailer
- etc.

### Smart Overwrite Protection
Avoids redownloading existing season trailers:
```json
"OVERWRITE_EXISTING": false
```

### Season Trailer Detection
The script intelligently detects existing season trailers by looking for:
- Files with "season" in the name
- Files with season numbers (S01, Season_01, etc.)
- Files in the Trailers subdirectory

## Troubleshooting Your Setup

### Common Issues with Season-Based Approach

**Issue**: No trailers found for any season
```
Solution: 
1. Check if the show exists in KinoCheck database
2. Try both language settings: "de" and "en"
3. Verify IMDB ID is correctly detected
```

**Issue**: Script downloads the same trailer for all seasons
```
Solution: This is expected behavior - TV shows typically have
series trailers rather than season-specific trailers. The script
downloads the best available trailer for each season.
```

**Issue**: Existing trailers not detected
```bash
# Check naming in your season folder
ls -la "/APPBOX_DATA/apps/.../Season 01/"
# Ensure trailers contain "season" or season numbers in filename
```

## Performance Expectations

For a typical German TV series library with season-based approach:

### API Efficiency
- **1 API call per show** (not per season or episode)
- **Massive reduction** in API usage vs episode-based
- **Respects rate limits** automatically

### Download Efficiency  
- **1 trailer per season** maximum
- **Realistic expectations** - matches how trailers actually exist
- **Faster completion** - fewer files to download

### Storage Efficiency
- **Clean organization** - one trailer per season folder
- **Logical placement** - trailers at season level where they belong
- **Plex compatibility** - follows Plex trailer conventions

For a library with 50 shows averaging 3 seasons each:
- **50 API calls** total (1 per show)
- **150 trailer downloads** maximum (1 per season)
- **Clean organization** with logical file placement

Much more efficient than the old episode-based approach! 🎬✨ 