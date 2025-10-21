from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config

@Client.on_callback_query(filters.regex("^help$"))
async def help_callback(client, query):
    buttons = [
        [InlineKeyboardButton("🏠 Home", callback_data="start")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    await query.message.edit(
        Config.HELP_TXT,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex("^about$"))
async def about_callback(client, query):
    me = await client.get_me()
    buttons = [
        [InlineKeyboardButton("🏠 Home", callback_data="start")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    await query.message.edit(
        Config.ABOUT_TXT.format(me.username),
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex("^start$"))
async def start_callback(client, query):
    first_name = query.from_user.first_name
    buttons = [
        [InlineKeyboardButton("🆘 Help", callback_data="help"),
         InlineKeyboardButton("ℹ️ About", callback_data="about")],
        [InlineKeyboardButton("🔐 Verify", callback_data="verify_user"),
         InlineKeyboardButton("👑 Premium", callback_data="premium")],
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
    ]
    await query.message.edit(
        Config.START_TXT.format(first_name),
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex("^close$"))
async def close_callback(client, query):
    await query.message.delete()
    
