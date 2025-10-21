import re
import logging

logger = logging.getLogger(__name__)

# Store user filter preferences temporarily (in-memory)
user_filters = {}


def detect_file_languages(filename):
    """Detect ALL languages present in filename (multi-language support)"""
    filename_lower = filename.lower()
    
    languages = []
    
    # Check for each language (short form + full form)
    if any(x in filename_lower for x in ['tam', 'tamil']):
        languages.append('Tamil')
    
    if any(x in filename_lower for x in ['tel', 'telugu']):
        languages.append('Telugu')
    
    if any(x in filename_lower for x in ['hin', 'hindi']):
        languages.append('Hindi')
    
    if any(x in filename_lower for x in ['mal', 'malayalam']):
        languages.append('Malayalam')
    
    if any(x in filename_lower for x in ['kan', 'kannada']):
        languages.append('Kannada')
    
    if any(x in filename_lower for x in ['eng', 'english']):
        languages.append('English')
    
    return languages


def detect_file_info(filename):
    """Detect languages, quality, and season from filename"""
    filename_lower = filename.lower()
    
    logger.info(f"Detecting info for: {filename}")
    
    # Detect ALL languages in the file
    languages = detect_file_languages(filename)
    
    # Detect Quality
    quality = None
    if '2160p' in filename_lower or '4k' in filename_lower:
        quality = '2160p'
    elif '1080p' in filename_lower:
        quality = '1080p'
    elif '720p' in filename_lower:
        quality = '720p'
    elif '480p' in filename_lower:
        quality = '480p'
    elif '360p' in filename_lower:
        quality = '360p'
    
    # Detect Season
    season = None
    season_match = re.search(r'[Ss]0*(\d+)', filename)
    if season_match:
        season_num = season_match.group(1)
        season = f"S{season_num}"
    
    logger.info(f"Detected -> Languages: {languages}, Quality: {quality}, Season: {season}")
    
    return languages, quality, season


def filter_files_by_preference(files, user_id):
    """Filter files based on user's language, quality, and season preferences"""
    if user_id not in user_filters:
        logger.info(f"No filters set for user {user_id}")
        return files
    
    prefs = user_filters[user_id]
    logger.info(f"User {user_id} filters: {prefs}")
    
    filtered = []
    
    for file in files:
        filename = file.get('file_name', '')
        languages, quality, season = detect_file_info(filename)
        
        match = True
        
        # Check language filter - File matches if selected language is IN the file's languages
        if 'language' in prefs and prefs['language'] != 'All':
            if prefs['language'] not in languages:
                match = False
                logger.info(f"File {filename[:40]}... rejected: Language mismatch (wants {prefs['language']}, has {languages})")
        
        # Check quality filter
        if 'quality' in prefs and prefs['quality'] != 'All':
            if quality != prefs['quality']:
                match = False
                logger.info(f"File {filename[:40]}... rejected: Quality mismatch ({quality} != {prefs['quality']})")
        
        # Check season filter
        if 'season' in prefs and prefs['season'] != 'All':
            if season != prefs['season']:
                match = False
                logger.info(f"File {filename[:40]}... rejected: Season mismatch ({season} != {prefs['season']})")
        
        if match:
            filtered.append(file)
            logger.info(f"File {filename[:40]}... ACCEPTED")
    
    logger.info(f"Filtered: {len(filtered)}/{len(files)} files match")
    
    return filtered


def get_filter_info(user_id):
    """Get current filter settings as text"""
    filter_info = ""
    if user_id in user_filters:
        prefs = user_filters[user_id]
        if 'language' in prefs and prefs['language'] != 'All':
            filter_info += f"\n🗣️ Language: {prefs['language']}"
        if 'quality' in prefs and prefs['quality'] != 'All':
            filter_info += f"\n📹 Quality: {prefs['quality']}"
        if 'season' in prefs and prefs['season'] != 'All':
            filter_info += f"\n📺 Season: {prefs['season']}"
    return filter_info


def set_user_filter(user_id, filter_type, value):
    """Set user filter preference"""
    if user_id not in user_filters:
        user_filters[user_id] = {}
    user_filters[user_id][filter_type] = value
    logger.info(f"Set filter for user {user_id}: {filter_type}={value}")


def reset_user_filters(user_id):
    """Reset all filters for a user"""
    if user_id in user_filters:
        del user_filters[user_id]
        logger.info(f"Reset all filters for user {user_id}")
    
