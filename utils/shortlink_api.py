"""
Universal Shortlink Verification System
Works with ANY shortlink service - arolinks, gplinks, shrinkme, etc.
Generates shortlinks that earn you money when users click them
"""

import string
import random
import requests
import logging
from info import SHORTLINK_API, SHORTLINK_URL

logger = logging.getLogger(__name__)


def generate_verify_token(length=16):
    """Generate random verification token"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def get_shortlink(original_url, api_url=None, api_key=None):
    """
    Universal shortlink creator
    Tries ALL common API formats until one works
    Returns monetized shortlink URL
    """
    if not api_url:
        api_url = SHORTLINK_URL
    if not api_key:
        api_key = SHORTLINK_API
    
    logger.info(f"🔗 Creating shortlink for: {original_url}")
    logger.info(f"🌐 Using service: {api_url}")
    
    # Prepare API endpoint
    api_endpoint = api_url
    if not api_endpoint.startswith('http'):
        api_endpoint = f"https://{api_endpoint}"
    
    # Remove /api from end if present
    api_endpoint = api_endpoint.rstrip('/api').rstrip('/')
    
    # Try different API formats
    api_formats = [
        f"{api_endpoint}/api",
        f"{api_endpoint}/api.php",
        f"{api_endpoint}/api/shorten",
        api_endpoint
    ]
    
    # Parameter combinations to try
    param_combinations = [
        {"api": api_key, "url": original_url},
        {"key": api_key, "url": original_url},
        {"token": api_key, "url": original_url},
        {"apikey": api_key, "link": original_url},
        {"api_key": api_key, "long_url": original_url},
    ]
    
    # Try GET and POST for each combination
    for endpoint in api_formats:
        for params in param_combinations:
            # Try GET request
            try:
                logger.info(f"🔄 Trying GET: {endpoint} with params: {list(params.keys())}")
                response = requests.get(endpoint, params=params, timeout=10)
                
                if response.status_code == 200:
                    result = try_extract_shortlink(response)
                    if result:
                        logger.info(f"✅ Shortlink created: {result}")
                        return result
            except Exception as e:
                logger.debug(f"GET failed: {e}")
            
            # Try POST request
            try:
                logger.info(f"🔄 Trying POST: {endpoint} with params: {list(params.keys())}")
                response = requests.post(endpoint, data=params, timeout=10)
                
                if response.status_code == 200:
                    result = try_extract_shortlink(response)
                    if result:
                        logger.info(f"✅ Shortlink created: {result}")
                        return result
            except Exception as e:
                logger.debug(f"POST failed: {e}")
    
    # All attempts failed, return original URL
    logger.warning(f"⚠️ All shortlink attempts failed, returning original URL")
    return original_url


def try_extract_shortlink(response):
    """Try to extract shortlink from various response formats"""
    try:
        # Try JSON response
        data = response.json()
        
        # Common JSON field names for shortlinks
        possible_fields = [
            'short_url', 'shorturl', 'short', 'shortlink',
            'url', 'link', 'shortenedUrl', 'result_url',
            'data', 'shorten', 'shortURL'
        ]
        
        for field in possible_fields:
            if field in data:
                url = data[field]
                if isinstance(url, str) and url.startswith('http'):
                    return url
                elif isinstance(url, dict):
                    # Sometimes the URL is nested
                    for subfield in possible_fields:
                        if subfield in url and isinstance(url[subfield], str):
                            return url[subfield]
        
        # Check if entire response is a URL
        if isinstance(data, str) and data.startswith('http'):
            return data
            
    except:
        # Not JSON, try plain text
        text = response.text.strip()
        if text.startswith('http'):
            return text
    
    return None


def generate_monetized_verification_link(bot_username, user_id):
    """
    Generate a monetized verification link
    Creates a Telegram verification URL and wraps it in a shortlink
    """
    # Create the verification URL
    verify_url = f"https://t.me/{bot_username}?start=verify_{user_id}"
    
    # Create shortlink
    short_url = get_shortlink(verify_url)
    
    return short_url


def extract_token_from_start(start_param):
    """
    Extract verification token from /start command parameter
    Supports: verify_<token> and video_<token>
    """
    if not start_param:
        return None, None
    
    if start_param.startswith("verify_"):
        token = start_param.replace("verify_", "")
        return "verify", token
    elif start_param.startswith("video_"):
        token = start_param.replace("video_", "")
        return "video", token
    
    return None, None


def test_shortlink_api():
    """Test if shortlink API is working"""
    test_url = "https://telegram.org"
    result = get_shortlink(test_url)
    
    if result != test_url:
        logger.info("✅ Shortlink API is working!")
        return True
    else:
        logger.error("❌ Shortlink API test failed!")
        return False
                
