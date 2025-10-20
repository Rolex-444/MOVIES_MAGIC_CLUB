from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.users import UserDB
from config import Config
import time

user_db = UserDB()

@Client.on_callback_query(filters.regex("^help$"))
async def help_callback(client, query):
    """Help callback"""
    buttons = [
        [InlineKeyboardButton("🔍 How to Search", callback_data="search_help")],
        [InlineKeyboardButton("🔐 Verification", callback_data="verify_help")],
        [InlineKeyboardButton("👑 Premium", callback_data="premium")],
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("🏠 Home", callback_data="start")]
    ]
    
    await query.message.edit(
        Config.HELP_TXT,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex("^about$"))
async def about_callback(client, query):
    """About callback"""
    buttons = [
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("🏠 Home", callback_data="start")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    
    await query.message.edit(
        Config.ABOUT_TXT.format(client.username),
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex("^start$"))
async def start_callback(client, query):
    """Start button callback"""
    buttons = [
        [InlineKeyboardButton("🆘 Help", callback_data="help"),
         InlineKeyboardButton("ℹ️ About", callback_data="about")],
        [InlineKeyboardButton("🔐 Verify", callback_data="verify_user"),
         InlineKeyboardButton("👑 Premium", callback_data="premium")],
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
    ]
    
    await query.message.edit(
        Config.START_TXT.format(query.from_user.first_name),
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex("^close$"))
async def close_callback(client, query):
    """Close message"""
    try:
        await query.message.delete()
    except:
        pass


@Client.on_callback_query(filters.regex("^verify_user$"))
async def verify_callback(client, query):
    """Verification button callback"""
    from plugins.verify import verify_command
    
    class MockMessage:
        def __init__(self, user, chat):
            self.from_user = user
            self.chat = chat
        
        async def reply(self, *args, **kwargs):
            return await query.message.reply(*args, **kwargs)
    
    mock_msg = MockMessage(query.from_user, query.message.chat)
    await verify_command(client, mock_msg)


@Client.on_message(filters.command("id"))
async def id_command(client, message):
    """Get user/chat ID"""
    
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        text = f"**User ID:** `{user.id}`\n**Name:** {user.first_name}"
    else:
        text = f"**Your ID:** `{message.from_user.id}`\n**Chat ID:** `{message.chat.id}`"
    
    await message.reply(text)


@Client.on_message(filters.command("info"))
async def info_command(client, message):
    """Get user info"""
    
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    
    text = f"""
**User Information**

**ID:** `{user.id}`
**Name:** {user.first_name}
**Username:** @{user.username if user.username else 'None'}
**DC ID:** {user.dc_id if user.dc_id else 'Unknown'}
**Is Bot:** {"Yes" if user.is_bot else "No"}
"""
    
    await message.reply(text)
