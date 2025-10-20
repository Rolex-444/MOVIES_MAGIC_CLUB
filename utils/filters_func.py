from database.database import Database
import re

db = Database()

async def search_files(query, offset=0, max_results=10):
    """Search files in database"""
    
    # Clean query
    query = query.strip()
    
    # Search in database
    files, total = await db.search_files(query, offset, max_results)
    
    next_offset = str(offset + max_results) if total > (offset + max_results) else ""
    
    return files, next_offset, total


async def get_bad_files(query):
    """Get files with quality/language filters"""
    
    # Extract quality and language from query
    quality_pattern = r'\b(480p|720p|1080p|2160p|4k)\b'
    lang_pattern = r'\b(hindi|tamil|telugu|english|malayalam|kannada|dubbed)\b'
    
    quality = re.search(quality_pattern, query, re.IGNORECASE)
    language = re.search(lang_pattern, query, re.IGNORECASE)
    
    # Build search query without quality/language
    clean_query = re.sub(quality_pattern, '', query, flags=re.IGNORECASE)
    clean_query = re.sub(lang_pattern, '', clean_query, flags=re.IGNORECASE)
    clean_query = clean_query.strip()
    
    return clean_query, quality, language
