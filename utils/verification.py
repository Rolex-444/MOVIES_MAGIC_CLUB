"""
UNIVERSAL Shortlink Verification System
Works with ANY shortlink service - arolinks, gplinks, shrinkme, etc.
"""

import string
import random
import requests
import logging

logger = logging.getLogger(__name__)

def generate_verify_token(length=16):
    """Generate random verification token"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def create_universal_shortlink(original_url):
    """
    UNIVERSAL shortlink creator
    Tries ALL common API formats until one works
    """
    # Import here to avoid circular imports
    from info import SHORTLINK_URL, SHORTLINK_API
    
    logger.info(f"🔗 Creating shortlink for: {original_url}")
    logger.info(f"🌐 Using service: {SHORTLINK_URL}")
    logger.info(f"🔑 API key: {SHORTLINK_API[:10] if SHORTLINK_API else 'NOT SET'}...")
    
    # Check if shortlink is configured
    if not SHORTLINK_URL or not SHORTLINK_API:
        logger.warning("⚠️ SHORTLINK_URL or SHORTLINK_API not configured! Returning original URL.")
        return original_url
    
    # Prepare API endpoint
    api_endpoint = SHORTLINK_URL
    if not api_endpoint.startswith('http'):
        api_endpoint = f"https://{api_endpoint}"
    
    # Try 8 different API formats
    api_formats = [
        # Format 1: arolinks.com, gplinks.in style
        {
            "url": f"{api_endpoint}/api",
            "params": {"api": SHORTLINK_API, "url": original_url}
        },
        # Format 2: shrinkme.io style
        {
            "url": f"{api_endpoint}/api",
            "params": {"key": SHORTLINK_API, "url": original_url}
        },
        # Format 3: droplink.co style
        {
            "url": f"{api_endpoint}/api",
            "params": {"api_token": SHORTLINK_API, "url": original_url}
        },
        # Format 4: POST request format
        {
            "url": f"{api_endpoint}/api",
            "data": {"api": SHORTLINK_API, "url": original_url},
            "method": "POST"
        },
        # Format 5: ouo.io style
        {
            "url": f"{api_endpoint}/api/{SHORTLINK_API}",
            "params": {"url": original_url}
        },
        # Format 6: adf.ly style
        {
            "url": f"{api_endpoint}/api.php",
            "params": {"key": SHORTLINK_API, "url": original_url}
        },
        # Format 7: Alternative path
        {
            "url": f"{api_endpoint}/shorten",
            "params": {"api": SHORTLINK_API, "url": original_url}
        },
        # Format 8: JSON POST
        {
            "url": f"{api_endpoint}/api",
            "json": {"api_key": SHORTLINK_API, "link": original_url},
            "method": "POST"
        }
    ]
    
    # Try each format
    for i, format_config in enumerate(api_formats, 1):
        try:
            logger.info(f"🔄 Trying API format {i}/8...")
            
            method = format_config.get("method", "GET")
            
            if method == "POST":
                if "data" in format_config:
                    response = requests.post(
                        format_config["url"],
                        data=format_config["data"],
                        timeout=10
                    )
                elif "json" in format_config:
                    response = requests.post(
                        format_config["url"],
                        json=format_config["json"],
                        timeout=10
                    )
            else:
                response = requests.get(
                    format_config["url"],
                    params=format_config.get("params", {}),
                    timeout=10
                )
            
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                data = response.json()
                
                # Look for shortened URL in common keys
                shortened_url = (
                    data.get('shortenedUrl') or
                    data.get('short_url') or
                    data.get('shortlink') or
                    data.get('link') or
                    data.get('url') or
                    data.get('result') or
                    data.get('data', {}).get('url')
                )
                
                if shortened_url and shortened_url.startswith('http'):
                    logger.info(f"✅ Shortlink created successfully with format {i}!")
                    logger.info(f"💰 Monetized URL: {shortened_url}")
                    return shortened_url
                    
            except ValueError:
                # Response might be plain text URL
                if response.text.startswith('http'):
                    logger.info(f"✅ Shortlink created successfully with format {i}!")
                    logger.info(f"💰 Monetized URL: {response.text}")
                    return response.text.strip()
        
        except Exception as e:
            logger.warning(f"⚠️ Format {i} failed: {str(e)}")
            continue
    
    # If all formats fail, return original URL
    logger.error("❌ All API formats failed! Returning original URL.")
    logger.error("💡 Please check your SHORTLINK_URL and SHORTLINK_API in info.py!")
    return original_url


def generate_monetized_verification_link(bot_username, token):
    """
    Generate verification link with shortlink monetization
    """
    # Create Telegram deep link
    telegram_link = f"https://t.me/{bot_username}?start=verify_{token}"
    
    # Wrap in monetized shortlink
    monetized_link = create_universal_shortlink(telegram_link)
    
    logger.info(f"🎯 Monetized verification link generated!")
    logger.info(f"📱 Original: {telegram_link}")
    logger.info(f"💰 Monetized: {monetized_link}")
    
    return monetized_link


def test_shortlink_api():
    """Test function to check if shortlink API is working"""
    test_url = "https://google.com"
    result = create_universal_shortlink(test_url)
    
    if result == test_url:
        return "❌ Shortlink API not working! Check config."
    else:
        return f"✅ Shortlink API working! Test link: {result}"
    
