#!/bin/bash

# Automated PIA VPN Setup Script
# Pre-answers all questions using config values

set -e

echo "🔐 Automated PIA VPN Setup"
echo "Using pre-configured settings..."

# Source environment variables from parent process
USERNAME="${PIA_USER}"
PASSWORD="${PIA_PASS}"
PROTOCOL="${VPN_PROTOCOL}"
REGION="${PREFERRED_REGION}"

if [ -z "$USERNAME" ] || [ -z "$PASSWORD" ]; then
    echo "❌ Missing PIA credentials in environment"
    exit 1
fi

echo "✓ Username: ${USERNAME}"
echo "✓ Protocol: ${PROTOCOL}"
echo "✓ Region: ${REGION}"

# Ensure PIA directory exists
if [ ! -d "./pia-manual" ]; then
    echo "📥 Downloading PIA scripts first..."
    git clone https://github.com/pia-foss/manual-connections.git pia-manual
    chmod +x pia-manual/*.sh
fi

# Change to PIA directory
cd ./pia-manual || exit 1

# Create a configuration cache file to avoid repeated setup
CACHE_FILE="/tmp/pia_config_cache.txt"

# Check if we have a cached working configuration
if [ -f "$CACHE_FILE" ]; then
    echo "🔄 Using cached PIA configuration..."
    source "$CACHE_FILE"
else
    echo "🔍 Setting up PIA configuration for first time..."
    
    # Determine server number based on region
    case "${REGION}" in
        "de_berlin"|"de-berlin"|"berlin")
            SERVER_NUM="16"
            ;;
        "de_germany-so"|"de-germany"|"germany")
            SERVER_NUM="5"
            ;;
        "de-frankfurt"|"frankfurt")
            SERVER_NUM="9"
            ;;
        *)
            # Default to German Streaming Optimized
            SERVER_NUM="5"
            ;;
    esac
    
    # Cache the configuration
    echo "SERVER_NUM=${SERVER_NUM}" > "$CACHE_FILE"
fi

# Determine protocol letter
if [[ "${PROTOCOL}" == "wireguard" ]]; then
    PROTOCOL_LETTER="w"
else
    PROTOCOL_LETTER="o"
fi

echo "🚀 Running automated PIA setup..."
echo "📍 Server: ${SERVER_NUM} (${REGION})"
echo "🔗 Protocol: ${PROTOCOL}"

# Run setup with all answers pre-filled
{
    echo "${USERNAME}"
    echo ""
    echo "${PASSWORD}"
    echo ""
    echo "n"  # No dedicated IP
    echo ""
    echo "n"  # No port forwarding  
    echo ""
    echo "n"  # Don't disable IPv6
    echo ""
    echo "y"  # Manual server selection
    echo ""
    echo "0.2"  # 200ms latency for more servers
    echo ""
    echo "${SERVER_NUM}"  # Pre-selected German server
    echo ""
    echo "${PROTOCOL_LETTER}"  # Protocol choice
    echo ""
} | timeout 60 ./run_setup.sh

echo "✅ PIA setup completed automatically!"
echo "💾 Configuration cached for next time" 