from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import Database
from database.verify import VerifyDB
from database.users import UserDB
from utils.filters_func import search_files
from utils.shortlink_api import get_shortlink
from utils.file_properties import get_size
from info import *
from config import Config
import random
import asyncio

db = Database()
verify_db = VerifyDB()
user_db = UserDB()

@Client.on_message(filters.text & filters.group)
async def auto_filter(client, message):
    if message.text.startswith('/'):
        return
    search = message.text
    files, offset, total = await search_files(search)
    if not files:
        if SPELL_CHECK:
            await spell_check(client, message, search)
        return
    btn = []
    for file in files:
        file_id = str(file.get('_id'))
        file_name = file.get('file_name', 'Unknown')
        if IS_VERIFY:
            verify_url = f"https://t.me/{client.username}?start=file_{file_id}"
            short_url = await get_shortlink(verify_url)
            btn.append([InlineKeyboardButton(f"📁 {file_name}", url=short_url)])
        else:
            btn.append([InlineKeyboardButton(f"📁 {file_name}", callback_data=f"file#{file_id}")])
    if offset != "":
        btn.append(
            [InlineKeyboardButton("📄 Pages", callback_data="pages"),
             InlineKeyboardButton(f"1/{round(int(total)/10)}", callback_data="pages"),
             InlineKeyboardButton("Next ⏩", callback_data=f"next_{offset}")]
        )
    btn.append([InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")])
    btn.append([InlineKeyboardButton("❌ Close", callback_data="close")])

    if IMDB:
        imdb_info = await get_imdb_info(search)
        caption = format_caption(imdb_info, total)
    else:
        caption = f"<b>Found {total} results for:</b> <code>{search}</code>\n\n"

    try:
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=caption,
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode="html",
            disable_web_page_preview=True
        )
    except Exception:
        await message.reply(
            caption,
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode="html"
        )

@Client.on_callback_query(filters.regex(r"^file#"))
async def send_file(client, query):
    user_id = query.from_user.id
    file_id = query.data.split("#")[1]
    if IS_VERIFY and user_id not in ADMINS:
        is_verified = await verify_db.is_verified(user_id)
        if not is_verified:
            verify_url = f"https://t.me/{client.username}?start=verify_{user_id}"
            short_url = await get_shortlink(verify_url)
            buttons = [
                [InlineKeyboardButton("🔐 Verify Now", url=short_url)],
                [InlineKeyboardButton("📚 How to Verify?", url=VERIFY_TUTORIAL)],
                [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")]
            ]
            await query.answer("⚠️ You need to verify first!", show_alert=True)
            await query.message.reply(
                Config.VERIFY_TXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="html",
                disable_web_page_preview=True
            )
            return
    file_data = await db.get_file(file_id)
    if not file_data:
        await query.answer("File not found!", show_alert=True)
        return
    caption = CUSTOM_FILE_CAPTION if CUSTOM_FILE_CAPTION else Config.FILE_CAPTION
    caption = caption.format(
        file_name=file_data.get('file_name', 'Unknown'),
        file_size=get_size(file_data.get('file_size', 0)),
        caption=file_data.get('caption', '')
    )
    file_buttons = [
        [InlineKeyboardButton("🎬 Stream", callback_data=f"stream#{file_id}"),
         InlineKeyboardButton("⚡ Fast Download", callback_data=f"fast#{file_id}")],
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
    ]
    try:
        msg = await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_data.get('file_id'),
            caption=caption,
            reply_markup=InlineKeyboardMarkup(file_buttons),
            parse_mode="html",
            protect_content=PROTECT_CONTENT
        )
        await query.answer("File sent to PM!", show_alert=False)
        if AUTO_DELETE:
            await asyncio.sleep(AUTO_DELETE_TIME)
            try:
                await msg.delete()
            except:
                pass
    except Exception as e:
        await query.answer(f"Error: {e}", show_alert=True)

async def send_file_by_id(client, message, file_id):
    user_id = message.from_user.id
    file_data = await db.get_file(file_id)
    if not file_data:
        await message.reply("File not found!", parse_mode="html")
        return
    caption = CUSTOM_FILE_CAPTION if CUSTOM_FILE_CAPTION else Config.FILE_CAPTION
    caption = caption.format(
        file_name=file_data.get('file_name', 'Unknown'),
        file_size=get_size(file_data.get('file_size', 0)),
        caption=file_data.get('caption', '')
    )
    file_buttons = [
        [InlineKeyboardButton("🎬 Stream", callback_data=f"stream#{file_id}"),
         InlineKeyboardButton("⚡ Fast Download", callback_data=f"fast#{file_id}")],
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
    ]
    try:
        msg = await client.send_cached_media(
            chat_id=user_id,
            file_id=file_data.get('file_id'),
            caption=caption,
            reply_markup=InlineKeyboardMarkup(file_buttons),
            parse_mode="html",
            protect_content=PROTECT_CONTENT
        )
        if AUTO_DELETE:
            await asyncio.sleep(AUTO_DELETE_TIME)
            try:
                await msg.delete()
            except:
                pass
    except Exception as e:
        await message.reply(f"Error: {e}", parse_mode="html")
    
