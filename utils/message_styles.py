# utils/message_styles.py

def success_message(text: str) -> str:
    """Formatted success message with gold & premium style"""
    return f"✅ <b><i>Success!</i></b>\n\n{text}"

def error_message(text: str) -> str:
    """Formatted error message with warning style"""
    return f"❌ <b><i>Error:</i></b>\n\n{text}"

def warning_message(text: str) -> str:
    """Formatted warning message with attention style"""
    return f"⚠️ <b><i>Warning!</i></b>\n\n{text}"

# Stylish button text templates for premium UX
BUTTON_TEXTS = {
    "default": "🎬 <b><i>Watch Movie</i></b>",
    "verify": "🔐 <b><i>Verify Now</i></b>",
    "premium": "🏆 <b><i>Get Premium</i></b>",
    "referral": "🚀 <b><i>Refer & Earn</i></b>",
    "delete": "🗑️ <b><i>Delete File</i></b>",
    "close": "❌ <b><i>Close</i></b>",
    "stream": "🎥 <b><i>Stream Online</i></b>",
    "fast_download": "⚡ <b><i>Fast Download</i></b>",
    "adult": "🔞 <b><i>18+ Rare Videos</i></b>"
}

def get_button_text(key: str) -> str:
    """Get formatted button text by key"""
    return BUTTON_TEXTS.get(key, BUTTON_TEXTS["default"])
