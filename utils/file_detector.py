import re

# Store user filter preferences temporarily (in-memory)
user_filters = {}


def detect_file_info(filename):
    """Detect language, quality, and season from filename"""
    filename_lower = filename.lower()
    
    # Detect Language
    language = None
    if any(x in filename_lower for x in ['tam', 'tamil']):
        language = 'Tamil'
    elif any(x in filename_lower for x in ['tel', 'telugu']):
        language = 'Telugu'
    elif any(x in filename_lower for x in ['hin', 'hindi']):
        language = 'Hindi'
    elif any(x in filename_lower for x in ['mal', 'malayalam']):
        language = 'Malayalam'
    elif any(x in filename_lower for x in ['kan', 'kannada']):
        language = 'Kannada'
    elif any(x in filename_lower for x in ['eng', 'english']):
        language = 'English'
    
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
    season_match = re.search(r'[Ss](\d+)', filename)
    if season_match:
        season = f"S{season_match.group(1)}"
    
    return language, quality, season


def filter_files_by_preference(files, user_id):
    """Filter files based on user's language, quality, and season preferences"""
    if user_id not in user_filters:
        return files
    
    prefs = user_filters[user_id]
    filtered = []
    
    for file in files:
        filename = file.get('file_name', '')
        lang, qual, seas = detect_file_info(filename)
        
        match = True
        
        # Check language filter
        if 'language' in prefs and prefs['language'] != 'All':
            if lang != prefs['language']:
                match = False
        
        # Check quality filter
        if 'quality' in prefs and prefs['quality'] != 'All':
            if qual != prefs['quality']:
                match = False
        
        # Check season filter
        if 'season' in prefs and prefs['season'] != 'All':
            if seas != prefs['season']:
                match = False
        
        if match:
            filtered.append(file)
    
    return filtered if filtered else files


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


def reset_user_filters(user_id):
    """Reset all filters for a user"""
    if user_id in user_filters:
        del user_filters[user_id]
