# 🌐 VPN Setup Guide - Private Internet Access Integration

This guide explains how to set up and use the built-in VPN functionality to bypass geo-blocking when downloading trailers.

## Why Use VPN?

If you're experiencing "Video unavailable" errors when downloading trailers, it's likely due to geo-blocking. YouTube videos can be restricted in certain countries due to copyright licensing agreements. The VPN integration automatically connects to a different country before downloading trailers, bypassing these restrictions.

## Prerequisites

### 1. Private Internet Access Account
You'll need an active PIA subscription:
- **Get PIA**: [https://www.privateinternetaccess.com/](https://www.privateinternetaccess.com/)
- **Free Trial**: Most plans include a free trial period
- **Cost**: ~$3-10/month depending on subscription length

### 2. System Requirements
- **Linux/macOS**: Supported (requires sudo access)
- **Windows**: Not currently supported (use WSL2)
- **Git**: Required for downloading PIA scripts
- **Sudo Access**: Required for VPN operations

## Quick Setup

### 1. Enable VPN During Configuration
When running the trailer checker for the first time:

```bash
./run.sh
```

Answer **yes** when prompted:
```
🌐 VPN Configuration (for geo-blocking bypass):
If trailers are blocked in your region, you can use a VPN.
Use Private Internet Access (PIA) VPN for downloads? [y/n]: y

You'll need a PIA account. Get one at: https://www.privateinternetaccess.com/
PIA Username (e.g., p1234567): p1234567
PIA Password: your_password_here

VPN Protocol:
  1. WireGuard (recommended - faster, modern)
  2. OpenVPN (traditional, widely supported)
Choose protocol [1/2]: 1

Auto-select best region? [y/n]: y
```

### 2. Test VPN Setup
Before running the main script, test your VPN configuration:

```bash
python3 test_pia_vpn.py
```

This will verify:
- ✅ PIA credentials work
- ✅ VPN connection establishes  
- ✅ IP address changes (bypass confirmed)

## Manual Configuration

You can also configure VPN settings manually in `config.json`:

```json
{
    "VPN": {
        "enabled": true,
        "provider": "pia",
        "pia_username": "p1234567",
        "pia_password": "your_password",
        "protocol": "wireguard",
        "auto_region": true,
        "preferred_region": "",
        "connect_timeout": 60,
        "disconnect_after_downloads": true,
        "setup_path": "./pia-manual"
    }
}
```

### Configuration Options

| Setting | Description | Options |
|---------|-------------|---------|
| `enabled` | Enable/disable VPN | `true`/`false` |
| `provider` | VPN provider | `"pia"` (only option currently) |
| `pia_username` | Your PIA username | e.g., `"p1234567"` |
| `pia_password` | Your PIA password | Your account password |
| `protocol` | VPN protocol | `"wireguard"` (recommended) or `"openvpn"` |
| `auto_region` | Auto-select best region | `true` (recommended) or `false` |
| `preferred_region` | Specific region | e.g., `"us_california"`, `"de_berlin"` |
| `connect_timeout` | Connection timeout (seconds) | `60` (default) |
| `disconnect_after_downloads` | Auto-disconnect when done | `true` (recommended) |

## How It Works

### Automatic Workflow

1. **🔍 Analysis Phase**: Script scans Plex libraries normally (no VPN needed)
2. **🔐 VPN Connection**: If downloads are needed, connects to PIA VPN
3. **📍 Location Check**: Verifies new IP address and location
4. **📥 Downloads**: Downloads trailers through VPN connection
5. **🔓 Cleanup**: Disconnects VPN when finished

### Console Output Example

```
🔐 Setting up VPN connection for downloads...
    📥 Downloading PIA connection scripts...
    ✅ PIA scripts downloaded to: ./pia-manual
    🔐 Connecting to PIA VPN...
    🌍 Protocol: WIREGUARD
    🎯 Auto-selecting best region...
    ✅ VPN connected successfully!
    🌍 Connected via: Amsterdam, NL

  Checking show: Ironheart (2025)
    🎬 Downloading: IRONHEART Season 1 Trailer German Deutsch (2025)
    🔗 YouTube: https://www.youtube.com/watch?v=dQw4w9WgXcQ
    📁 Saving to: /path/to/Season 01/Trailers/Season_01_IRONHEART_Trailer.mp4
    ⬇️ Starting download...
    ✅ Download completed successfully!

🔓 Cleaning up VPN connection...
    ✅ VPN disconnected

Season trailer check complete!
Downloaded 5 season trailers
VPN used: ✅ Private Internet Access
```

## Regional Options

### Auto-Region (Recommended)
When `auto_region: true`, PIA automatically selects the server with lowest latency. This is usually the best option as it provides the fastest speeds while still bypassing geo-blocking.

### Manual Region Selection
If you prefer a specific country, set `auto_region: false` and specify a region:

| Region Code | Location | Good For |
|-------------|----------|----------|
| `us_california` | California, USA | US content |
| `us_newyork` | New York, USA | US content |
| `de_berlin` | Berlin, Germany | EU content |
| `uk_london` | London, UK | UK content |
| `nl_amsterdam` | Amsterdam, Netherlands | EU content |
| `ca_toronto` | Toronto, Canada | North American content |

## Troubleshooting

### Common Issues

**❌ "VPN connection failed"**
```bash
# Test your setup
python3 test_pia_vpn.py

# Check credentials
echo "Username: $PIA_USER"
echo "Password length: ${#PIA_PASS}"

# Verify sudo access
sudo -n true && echo "Sudo OK" || echo "Sudo needs password"
```

**❌ "Git not found"**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install git

# macOS
brew install git
# or install Xcode Command Line Tools
xcode-select --install
```

**❌ "Sudo access required"**
VPN operations need sudo access. Either:
1. Run with `sudo` (not recommended)
2. Set up passwordless sudo for your user
3. Use the script interactively (will prompt for password)

**❌ "Downloads still fail after VPN"**
- Verify IP changed: Check output for "Connected via: [City], [Country]"
- Try different protocol: Switch between WireGuard and OpenVPN
- Try different region: Disable auto-region and pick specific country
- Check PIA account: Ensure subscription is active

### Advanced Debugging

**Check current IP and location:**
```bash
curl -s https://ipinfo.io/json | jq
```

**Manual VPN test:**
```bash
cd ./pia-manual
sudo VPN_PROTOCOL=wireguard AUTOCONNECT=true PIA_USER=p1234567 PIA_PASS=password ./run_setup.sh
curl -s https://ipinfo.io/json | jq
sudo wg-quick down pia  # Disconnect
```

**Check active VPN connections:**
```bash
# WireGuard
sudo wg show

# OpenVPN
ps aux | grep openvpn
```

## Security Considerations

### Credentials Storage
Your PIA credentials are stored in `config.json`. Secure this file:

```bash
# Restrict access to config file
chmod 600 config.json

# Ensure only you can read it
ls -la config.json
```

### VPN Logs
The script creates logs in `trailer_checker.log`. This file contains:
- ✅ VPN connection status (no credentials)
- ✅ Download attempts and results
- ❌ Does not log your PIA password

### Auto-Disconnect
The script automatically disconnects the VPN when finished to:
- Restore your normal internet connection
- Prevent unnecessary VPN usage
- Avoid interfering with other applications

## Performance Impact

### Speed Considerations
- **WireGuard**: Faster, more modern protocol (recommended)
- **OpenVPN**: Slower but more widely supported
- **Region**: Closer regions = faster speeds
- **Auto-Region**: Usually picks fastest available server

### Usage Efficiency
- VPN only connects when downloads are needed
- Disconnects immediately after downloads complete
- Multiple downloads use the same VPN session (efficient)

## Alternatives

If PIA VPN doesn't work for you:

### Other VPN Options
1. **Manual VPN**: Connect to any VPN before running the script
2. **Different Provider**: The script could be adapted for other providers
3. **Proxy**: Some users prefer HTTP/SOCKS proxies

### No-VPN Solutions
1. **Language Switching**: Try both German and English in config
2. **Manual Download**: Use the generated YouTube links manually
3. **Different Timing**: Some restrictions are temporary

## Support

### Getting Help
- **Test Script**: `python3 test_pia_vpn.py`
- **Logs**: Check `trailer_checker.log` for detailed errors
- **PIA Support**: [https://www.privateinternetaccess.com/helpdesk](https://www.privateinternetaccess.com/helpdesk)

### Reporting Issues
When reporting VPN-related issues, include:
1. Output from `python3 test_pia_vpn.py`
2. Your operating system and version
3. Whether sudo access works: `sudo -n true`
4. Git availability: `git --version`

**Remember**: Never share your PIA credentials when reporting issues!

---

**🎬 With VPN bypass enabled, you should be able to download trailers from any region! Enjoy your complete Plex library with season trailers! ✨** 