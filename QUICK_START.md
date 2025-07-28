# 🚀 Quick Start Guide (Season-Based Trailers)

## One-Command Setup

```bash
# Clone and enter directory
git clone [your-repo] && cd plex_trailer_checker

# Run automated setup
./setup.sh

# Run the trailer checker
./run.sh
```

That's it! The setup script handles everything automatically.

## What the Setup Does

1. ✅ **Checks Python 3** installation
2. ✅ **Creates virtual environment** (`venv/`)  
3. ✅ **Installs all dependencies** from `requirements.txt`
4. ✅ **Verifies yt-dlp** installation
5. ✅ **Ready to run!**

## First Run Configuration

When you run `./run.sh` for the first time, you'll be guided through setup:

```
Plex Server URL: http://your-server:32400
Plex Username: your_username  
Plex Password: [hidden]

Available Plex Libraries:
----------------------------------------
 1. Serien                    (Type: show)
 2. Filme                     (Type: movie)
 3. Musik                     (Type: artist)

Select TV Show libraries: 1
✓ Added TV library: Serien

Automatically download missing trailers? [y/n]: y
Download method - (i)nline or (s)ubdirectory? [s]

Trailer quality preference:
  1. 4K/2160p preferred (falls back to 1080p if unavailable)
  2. 1080p maximum
  3. Best available (any resolution)
Choose quality [1/2/3]: 1

Skip first few seconds of trailers (removes intro branding)? [y/n]: y
How many seconds to skip at start? [3]: 3
Preferred trailer language - (d)eutsch or (e)nglish? [d]
KinoCheck API key (optional): [Enter to skip]

🌐 VPN Configuration (for geo-blocking bypass):
If trailers are blocked in your region, you can use a VPN.
Use Private Internet Access (PIA) VPN for downloads? [y/n]: y
PIA Username (e.g., p1234567): your_username
PIA Password: [hidden]
```

## Alternative Installation Methods

### Manual Installation (if setup.sh doesn't work):
```bash
python3 -m venv venv
source venv/bin/activate  
pip install -r requirements.txt
python3 plex_trailer_checker.py
```

### For macOS (Homebrew Python):
The setup script handles externally managed environments automatically.

## What It Does

✅ **Scans** your Plex TV libraries  
✅ **Groups** episodes by season  
✅ **Finds** seasons missing trailers  
✅ **Downloads** one high-quality trailer per season using KinoCheck API  
✅ **Places** them in correct Plex-compatible locations  
✅ **Reports** progress and results  

## Season-Based Organization

Downloaded trailers are placed at the season level:

```
/Your/TV/Show/Season 01/
├── Episode 01.mkv
├── Episode 02.mkv
├── ... (all episodes)
└── Trailers/
    └── Season_01_Official_Trailer.mp4
```

## Features

🎬 **Season-Based Downloads** via KinoCheck API  
🌐 **German & English** trailer support  
🎯 **Smart Matching** using TMDB/IMDB IDs  
📊 **Progress Tracking** and detailed reports  
⚡ **Rate Limited** (respects API limits)  
🎪 **Efficient** - One trailer per season, not per episode
🎥 **High Quality** - 4K/2160p preferred, 1080p fallback
✂️ **Auto-Trimming** - Removes intro branding/logos

## Ongoing Usage

After initial setup, simply run:
```bash
./run.sh
```

The script will:
- Activate the virtual environment automatically
- Check for new seasons missing trailers  
- Download any newly available trailers
- Update your Plex library

## VPN Troubleshooting

If downloads fail due to geo-blocking, test your VPN setup:
```bash
python3 test_pia_vpn.py
```

This will verify:
- PIA credentials are working
- VPN connection establishes correctly  
- IP address changes (indicating bypass success)

## Need Help?

- Check `README.md` for full documentation
- Check `example_usage.md` for detailed examples
- Check `trailer_checker.log` for troubleshooting
- Test VPN: `python3 test_pia_vpn.py`
- If videos are unavailable, try switching language in config.json

## File Structure After Setup

```
plex_trailer_checker/
├── setup.sh              ← One-time setup
├── run.sh                ← Run anytime  
├── venv/                 ← Virtual environment (auto-created)
├── config.json           ← Your settings (auto-created)
├── plex_trailer_checker.py
├── requirements.txt
└── ... (other files)
``` 