import aiohttp
import asyncio
from info import SHORTLINK_URL, SHORTLINK_API

async def get_shortlink(url, api_url=None, api_key=None):
    """
    Universal shortlink generator supporting multiple providers:
    - GPLinks, GPLinks.in, GPLinks.co
    - Droplink, Droplink.co
    - Arolinks
    - Clk.wiki, Clk.sh, Clk.asia
    - Earnlink, Earnl.xyz
    - Shortxlinks
    - Teralink
    - Ouo.io
    - And more...
    """
    
    if not api_url or not api_key:
        api_url = SHORTLINK_URL
        api_key = SHORTLINK_API
    
    if not api_url or not api_key:
        return url
    
    try:
        # Remove trailing slash from api_url
        api_url = api_url.rstrip('/')
        
        # GPLinks Family (gplinks.in, gplinks.co, etc.)
        if any(domain in api_url.lower() for domain in ['gplinks', 'gplink']):
            endpoint = f"{api_url}/api"
            params = {'api': api_key, 'url': url}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params, timeout=10) as response:
                    data = await response.json()
                    if data.get("status") == "success":
                        return data.get('shortenedUrl', url)
        
        # Droplink Family (droplink.co, etc.)
        elif 'droplink' in api_url.lower():
            endpoint = f"{api_url}/api"
            params = {'api': api_key, 'url': url}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params, timeout=10) as response:
                    data = await response.json()
                    if data.get("status") == "success":
                        return data.get('shortenedUrl', url)
        
        # Clk Family (clk.wiki, clk.sh, clk.asia)
        elif any(domain in api_url.lower() for domain in ['clk.wiki', 'clk.sh', 'clk.asia', 'clk']):
            endpoint = f"{api_url}/api"
            params = {'api': api_key, 'url': url}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params, timeout=10) as response:
                    data = await response.json()
                    if data.get("status") == "success":
                        return data.get('shortenedUrl', url)
        
        # Arolinks
        elif 'aro' in api_url.lower():
            endpoint = f"{api_url}/api"
            params = {'api': api_key, 'url': url}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params, timeout=10) as response:
                    data = await response.json()
                    if data.get("status") == "success":
                        return data.get('shortenedUrl', url)
        
        # Earnlink Family (earnl.xyz, etc.)
        elif any(domain in api_url.lower() for domain in ['earnl', 'earn']):
            endpoint = f"{api_url}/api"
            params = {'api': api_key, 'url': url}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params, timeout=10) as response:
                    data = await response.json()
                    if data.get("status") == "success":
                        return data.get('shortenedUrl', url)
        
        # Shortxlinks
        elif 'shortx' in api_url.lower():
            endpoint = f"{api_url}/api"
            params = {'api': api_key, 'url': url}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params, timeout=10) as response:
                    data = await response.json()
                    if data.get("status") == "success":
                        return data.get('shortenedUrl', url)
        
        # Teralink
        elif 'tera' in api_url.lower():
            endpoint = f"{api_url}/api"
            params = {'api': api_key, 'url': url}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params, timeout=10) as response:
                    data = await response.json()
                    if data.get("status") == "success":
                        return data.get('shortenedUrl', url)
        
        # Ouo.io
        elif 'ouo' in api_url.lower():
            endpoint = f"{api_url}/api/{api_key}"
            params = {'s': url}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params, timeout=10) as response:
                    text = await response.text()
                    return text if text.startswith('http') else url
        
        # Generic API format (works with most shortlink services)
        else:
            endpoint = f"{api_url}/api"
            params = {'api': api_key, 'url': url}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params, timeout=10) as response:
                    try:
                        data = await response.json()
                        # Try different response formats
                        if data.get("status") == "success":
                            return data.get('shortenedUrl', url)
                        elif 'short' in data:
                            return data['short']
                        elif 'shortened' in data:
                            return data['shortened']
                    except:
                        text = await response.text()
                        if text.startswith('http'):
                            return text
        
        return url
        
    except asyncio.TimeoutError:
        print(f"Shortlink timeout for {url}")
        return url
    except Exception as e:
        print(f"Shortlink error: {e}")
        return url


async def check_shortlink_api(api_url, api_key):
    """Check if shortlink API is working"""
    test_url = "https://telegram.org"
    try:
        result = await get_shortlink(test_url, api_url, api_key)
        return result != test_url
    except:
        return False
