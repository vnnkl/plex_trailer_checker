# 🚀 Deployment Guide - Running on Plex Server

This guide explains how to deploy the Plex Trailer Checker directly on your Plex server for optimal performance.

## Prerequisites

- **SSH access** to your Plex server
- **Python 3.8+** installed on the server
- **Git** installed on the server
- **Write access** to your Plex media directories

## Quick Deployment

### 1. Connect to Your Plex Server
```bash
ssh username@your-plex-server.com
```

### 2. Clone and Setup (One Command)
```bash
git clone https://github.com/yourusername/plex-trailer-checker.git
cd plex-trailer-checker/plex_trailer_checker
./setup.sh
```

### 3. Run Initial Configuration
```bash
./run.sh
```

Follow the interactive setup to configure your libraries and preferences.

## Installation Locations

### Recommended: User Home Directory
```bash
# Install in user's home directory
cd ~
git clone [repo-url]
cd plex-trailer-checker/plex_trailer_checker
./setup.sh
```

### Alternative: System Directory
```bash
# Install system-wide (requires sudo)
cd /opt
sudo git clone [repo-url]
cd plex-trailer-checker/plex_trailer_checker
sudo ./setup.sh
```

## Common Server Configurations

### Ubuntu/Debian Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3 and Git (if not installed)
sudo apt install python3 python3-venv python3-pip git -y

# Clone and setup
git clone [repo-url]
cd plex-trailer-checker/plex_trailer_checker
./setup.sh
./run.sh
```

### CentOS/RHEL/Rocky Linux
```bash
# Update system
sudo yum update -y

# Install Python 3 and Git
sudo yum install python3 python3-pip git -y

# Clone and setup
git clone [repo-url]
cd plex-trailer-checker/plex_trailer_checker
./setup.sh
./run.sh
```

### Docker Container (if Plex runs in Docker)
```bash
# Enter Plex container
docker exec -it plex /bin/bash

# Install git and python (if not available)
apt update && apt install git python3 python3-venv -y

# Clone and setup
cd /config  # or appropriate directory
git clone [repo-url]
cd plex-trailer-checker/plex_trailer_checker
./setup.sh
./run.sh
```

## Automation Setup

### Cron Job (Run Daily)
```bash
# Edit crontab
crontab -e

# Add line to run daily at 3 AM
0 3 * * * cd /path/to/plex-trailer-checker/plex_trailer_checker && ./run.sh >/dev/null 2>&1
```

### Systemd Service (Advanced)
Create `/etc/systemd/system/plex-trailer-checker.service`:
```ini
[Unit]
Description=Plex Trailer Checker
After=network.target

[Service]
Type=oneshot
User=plex
WorkingDirectory=/path/to/plex-trailer-checker/plex_trailer_checker
ExecStart=/bin/bash -c "./run.sh"
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and test:
```bash
sudo systemctl daemon-reload
sudo systemctl enable plex-trailer-checker.timer
sudo systemctl start plex-trailer-checker.service
sudo systemctl status plex-trailer-checker.service
```

## Troubleshooting

### Permission Issues
```bash
# Ensure script has correct permissions
chmod +x setup.sh run.sh

# Fix media directory permissions (if needed)
sudo chown -R plex:plex /path/to/plex/media
sudo chmod -R 755 /path/to/plex/media
```

### Python Issues
```bash
# Check Python version
python3 --version

# Install pip if missing
sudo apt install python3-pip  # Ubuntu/Debian
sudo yum install python3-pip  # CentOS/RHEL
```

### Network/API Issues
```bash
# Test internet connectivity
curl -I https://api.kinocheck.de

# Test yt-dlp
source venv/bin/activate
yt-dlp --version
```

### Log Files
```bash
# Check logs for errors
tail -f trailer_checker.log
tail -f missing_trailers_report.txt
```

## Security Considerations

### File Permissions
```bash
# Secure config file
chmod 600 config.json

# Ensure only plex user can access
chown plex:plex config.json
```

### Firewall (if needed)
```bash
# Allow outbound HTTPS for API calls
sudo ufw allow out 443
```

## Updates

### Update the Script
```bash
cd /path/to/plex-trailer-checker
git pull
cd plex_trailer_checker
./setup.sh  # Reinstall dependencies if needed
```

### Update Dependencies
```bash
cd plex_trailer_checker
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

## Directory Structure on Server

```
/home/plex/plex-trailer-checker/
├── plex_trailer_checker/
│   ├── setup.sh              ← Setup script
│   ├── run.sh                ← Run script
│   ├── venv/                 ← Virtual environment
│   ├── config.json           ← Your configuration
│   ├── trailer_checker.log   ← Execution logs
│   ├── missing_trailers_report.txt ← Results
│   └── ... (script files)
└── README.md
```

## Performance Tips

1. **Run during off-peak hours** (early morning)
2. **Monitor disk space** for downloaded trailers
3. **Check logs regularly** for any issues
4. **Update regularly** to get new features

## Support

If you encounter issues:

1. Check `trailer_checker.log` for detailed error messages
2. Verify Plex server connectivity: `curl -I http://localhost:32400`
3. Test manual run: `source venv/bin/activate && python3 plex_trailer_checker.py`
4. Check file permissions in media directories 