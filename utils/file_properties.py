import math
import time
from pyrogram.types import InlineKeyboardButton

def get_size(bytes):
    """Convert bytes to human readable format"""
    if not bytes:
        return "0B"
    
    size_name = ("B", "KB", "MB", "GB", "TB", "PB")
    i = int(math.floor(math.log(bytes, 1024)))
    p = math.pow(1024, i)
    s = round(bytes / p, 2)
    return f"{s} {size_name[i]}"


def get_file_id(message):
    """Get file ID from message"""
    if message.document:
        return message.document.file_id
    elif message.video:
        return message.video.file_id
    elif message.audio:
        return message.audio.file_id
    elif message.photo:
        return message.photo.file_id
    return None


def get_file_name(message):
    """Get file name from message"""
    if message.document:
        return message.document.file_name
    elif message.video:
        return getattr(message.video, 'file_name', 'video.mp4')
    elif message.audio:
        return getattr(message.audio, 'file_name', 'audio.mp3')
    return "Unknown"


def get_file_size(message):
    """Get file size from message"""
    if message.document:
        return message.document.file_size
    elif message.video:
        return message.video.file_size
    elif message.audio:
        return message.audio.file_size
    return 0


def time_formatter(seconds):
    """Format seconds to readable time"""
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    
    tmp = (
        (f"{days}d, " if days else "") +
        (f"{hours}h, " if hours else "") +
        (f"{minutes}m, " if minutes else "") +
        (f"{seconds}s" if seconds else "")
    )
    
    return tmp or "0s"
