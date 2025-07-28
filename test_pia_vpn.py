#!/usr/bin/env python3
"""
Test script for Private Internet Access (PIA) VPN integration
"""

import os
import sys
import json
import subprocess
import requests
import time

def load_config():
    """Load the trailer checker config"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        print("❌ config.json not found. Run the main script first.")
        return None

def get_current_location():
    """Get current IP and location"""
    try:
        response = requests.get('https://ipinfo.io/json', timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"Error getting location: {e}")
        return None

def test_git_availability():
    """Test if git is available for downloading PIA scripts"""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Git available: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Git not found")
            return False
    except FileNotFoundError:
        print(f"❌ Git not installed")
        return False

def test_sudo_access():
    """Test if sudo access is available (required for VPN)"""
    try:
        result = subprocess.run(['sudo', '-n', 'true'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Sudo access available (passwordless)")
            return True
        else:
            print(f"⚠️ Sudo access may require password")
            # Test if sudo works with password prompt
            print(f"   Testing sudo with password prompt...")
            result = subprocess.run(['sudo', 'true'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Sudo access confirmed")
                return True
            else:
                print(f"❌ Sudo access denied")
                return False
    except Exception as e:
        print(f"❌ Error testing sudo: {e}")
        return False

def download_pia_scripts(setup_path):
    """Download PIA scripts"""
    if os.path.exists(setup_path):
        print(f"✅ PIA scripts already exist at: {setup_path}")
        return True
    
    print(f"📥 Downloading PIA scripts to: {setup_path}")
    
    try:
        result = subprocess.run([
            'git', 'clone', 
            'https://github.com/pia-foss/manual-connections.git',
            setup_path
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            # Make scripts executable
            for script in ['run_setup.sh', 'get_token.sh', 'get_region.sh']:
                script_path = os.path.join(setup_path, script)
                if os.path.exists(script_path):
                    os.chmod(script_path, 0o755)
            
            print(f"✅ PIA scripts downloaded successfully")
            return True
        else:
            print(f"❌ Failed to download PIA scripts: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"❌ Error downloading PIA scripts: {e}")
        return False

def test_pia_credentials(setup_path, username, password):
    """Test PIA credentials by getting a token"""
    print(f"🔑 Testing PIA credentials...")
    
    try:
        original_dir = os.getcwd()
        os.chdir(setup_path)
        
        env = os.environ.copy()
        env.update({
            'PIA_USER': username,
            'PIA_PASS': password
        })
        
        result = subprocess.run(
            ['./get_token.sh'],
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        os.chdir(original_dir)
        
        if result.returncode == 0 and 'token' in result.stdout.lower():
            print(f"✅ PIA credentials valid - token obtained")
            return True
        else:
            print(f"❌ PIA credentials failed: {result.stderr}")
            return False
    
    except Exception as e:
        os.chdir(original_dir)
        print(f"❌ Error testing credentials: {e}")
        return False

def test_vpn_connection(setup_path, username, password, protocol='wireguard'):
    """Test actual VPN connection"""
    print(f"🔐 Testing VPN connection ({protocol})...")
    
    # Get initial location
    print(f"   📍 Getting initial location...")
    initial_location = get_current_location()
    if initial_location:
        print(f"   🌍 Before VPN: {initial_location.get('city', 'Unknown')}, {initial_location.get('country', 'Unknown')} ({initial_location.get('ip', 'Unknown IP')})")
    
    try:
        original_dir = os.getcwd()
        os.chdir(setup_path)
        
        env = os.environ.copy()
        env.update({
            'PIA_USER': username,
            'PIA_PASS': password,
            'VPN_PROTOCOL': protocol,
            'AUTOCONNECT': 'true',
            'DISABLE_IPV6': 'yes',
            'PIA_PF': 'false',
            'PIA_DNS': 'true',
            'PIA_CONNECT': 'true'
        })
        
        print(f"   🚀 Attempting VPN connection...")
        result = subprocess.run(
            ['sudo', './run_setup.sh'],
            env=env,
            capture_output=True,
            text=True,
            timeout=90,
            input='\n'
        )
        
        os.chdir(original_dir)
        
        if result.returncode == 0:
            print(f"   ✅ VPN connection script completed")
            
            # Wait a moment for connection to stabilize
            time.sleep(5)
            
            # Check new location
            print(f"   📍 Checking new location...")
            new_location = get_current_location()
            if new_location:
                new_ip = new_location.get('ip', 'Unknown')
                new_country = new_location.get('country', 'Unknown')
                new_city = new_location.get('city', 'Unknown')
                
                print(f"   🌍 After VPN: {new_city}, {new_country} ({new_ip})")
                
                # Check if IP changed
                if initial_location and new_ip != initial_location.get('ip'):
                    print(f"   ✅ VPN connection successful - IP changed!")
                    return True
                else:
                    print(f"   ❌ VPN connection may have failed - IP unchanged")
                    return False
            else:
                print(f"   ❌ Could not verify new location")
                return False
        else:
            print(f"   ❌ VPN connection failed: {result.stderr.split(chr(10))[0]}")
            return False
    
    except subprocess.TimeoutExpired:
        os.chdir(original_dir)
        print(f"   ⏰ VPN connection timed out")
        return False
    except Exception as e:
        os.chdir(original_dir)
        print(f"   ❌ VPN connection error: {e}")
        return False

def cleanup_vpn():
    """Clean up VPN connection"""
    print(f"🧹 Cleaning up VPN connection...")
    
    try:
        # Try to disconnect WireGuard
        subprocess.run(['sudo', 'wg-quick', 'down', 'pia'], 
                      capture_output=True, timeout=10)
        
        # Kill any OpenVPN processes
        subprocess.run(['sudo', 'pkill', '-f', 'openvpn'], 
                      capture_output=True, timeout=10)
        
        print(f"✅ VPN cleanup completed")
    except Exception as e:
        print(f"⚠️ VPN cleanup error: {e}")

def main():
    print("🧪 PIA VPN Integration Test")
    print("=" * 50)
    
    # Load configuration
    print("\n1. Loading configuration...")
    config = load_config()
    if not config:
        return
    
    vpn_config = config.get('VPN', {})
    if not vpn_config.get('enabled', False):
        print("❌ VPN is not enabled in config.json")
        print("   Run the main script and enable VPN during setup")
        return
    
    username = vpn_config.get('pia_username', '')
    password = vpn_config.get('pia_password', '')
    protocol = vpn_config.get('protocol', 'wireguard')
    setup_path = vpn_config.get('setup_path', './pia-manual')
    
    if not username or not password:
        print("❌ PIA credentials not configured")
        return
    
    print(f"✅ VPN configuration loaded")
    print(f"   Username: {username}")
    print(f"   Protocol: {protocol}")
    print(f"   Setup path: {setup_path}")
    
    # Test prerequisites
    print("\n2. Testing prerequisites...")
    
    git_ok = test_git_availability()
    sudo_ok = test_sudo_access()
    
    if not git_ok:
        print("💡 Install git: apt install git (Ubuntu) or brew install git (macOS)")
        return
    
    if not sudo_ok:
        print("💡 Ensure sudo access is available for VPN operations")
        return
    
    # Download PIA scripts
    print("\n3. Setting up PIA scripts...")
    scripts_ok = download_pia_scripts(setup_path)
    
    if not scripts_ok:
        return
    
    # Test credentials
    print("\n4. Testing PIA credentials...")
    creds_ok = test_pia_credentials(setup_path, username, password)
    
    if not creds_ok:
        print("💡 Check your PIA username and password in config.json")
        return
    
    # Test VPN connection
    print("\n5. Testing VPN connection...")
    vpn_ok = test_vpn_connection(setup_path, username, password, protocol)
    
    # Cleanup
    print("\n6. Cleanup...")
    cleanup_vpn()
    
    # Final result
    print("\n" + "=" * 50)
    if vpn_ok:
        print("🎉 PIA VPN test successful!")
        print("✅ Your trailer checker should now work with VPN bypass")
        print("\n💡 Next steps:")
        print("   • Run ./run.sh to start downloading trailers")
        print("   • VPN will connect automatically before downloads")
        print("   • Check logs if any downloads still fail")
    else:
        print("❌ PIA VPN test failed")
        print("\n💡 Troubleshooting:")
        print("   • Check your PIA account is active")
        print("   • Verify username/password are correct")
        print("   • Ensure sudo access works")
        print("   • Try different protocol (wireguard ↔ openvpn)")
        print("   • Check network connectivity")

if __name__ == "__main__":
    main() 