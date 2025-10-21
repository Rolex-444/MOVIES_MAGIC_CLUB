from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.users import UserDB
from config import Config

user_db = UserDB()

@Client.on_callback_query(filters.regex("^help$"))
async def help_callback(client, query):
    buttons = [
        [InlineKeyboardButton("🔍 How to Search", callback_data="search_help")],
        [InlineKeyboardButton("🔐 Verification", callback_data="verify_help")],
        [InlineKeyboardButton("👑 Premium", callback_data="premium")],
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("🏠 Home", callback_data="start")]
    ]
    await query.message.edit(
        Config.HELP_TXT,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="html",
        disable_web_page_preview=True
    )

@Client.on_callback_query(filters.regex("^about$"))
async def about_callback(client, query):
    buttons = [
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("🏠 Home", callback_data="start")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    await query.message.edit(
        Config.ABOUT_TXT.format(client.username),
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="html",
        disable_web_page_preview=True
    )

@Client.on_callback_query(filters.regex("^start$"))
async def start_callback(client, query):
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
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="html",
        disable_web_page_preview=True
            )
    
