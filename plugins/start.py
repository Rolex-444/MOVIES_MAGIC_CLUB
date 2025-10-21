from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.users import UserDB
from database.verify import VerifyDB
from config import Config
from info import START_IMG, VERIFY_EXPIRE, ADMINS
import time

user_db = UserDB()
verify_db = VerifyDB()

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    await user_db.add_user(user_id, first_name)

    if len(message.command) > 1:
        data = message.command[1]

        if data.startswith("verify_"):
            verify_id = int(data.split("_")[1])
            if verify_id == user_id:
                await verify_db.add_user(user_id, VERIFY_EXPIRE)
                buttons = [
                    [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
                    [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
                ]
                await message.reply(
                    Config.VERIFIED_TXT,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    parse_mode="html",
                    disable_web_page_preview=True
                )
                return

        elif data.startswith("ref_"):
            referred_by = int(data.split("_")[1])
            if referred_by != user_id:
                from plugins.shortlink import handle_referral
                await handle_referral(client, user_id, referred_by)

        elif data.startswith("batch_"):
            batch_id = data.split("_", 1)[1]
            from plugins.batch import handle_batch
            await handle_batch(client, message, batch_id)
            return

        elif data.startswith("file_"):
            if not await verify_db.is_verified(user_id) and user_id not in ADMINS:
                await send_verification_message(client, message)
                return

            file_id = data.split("_")[1]
            from plugins.filters import send_file_by_id
            await send_file_by_id(client, message, file_id)
            return

    buttons = [
        [InlineKeyboardButton("🆘 Help", callback_data="help"),
         InlineKeyboardButton("ℹ️ About", callback_data="about")],
        [InlineKeyboardButton("🔐 Verify", callback_data="verify_user"),
         InlineKeyboardButton("👑 Premium", callback_data="premium")],
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
    ]

    await message.reply_photo(
        photo=START_IMG,
        caption=Config.START_TXT.format(first_name),
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="html",
        disable_web_page_preview=True
    )


async def send_verification_message(client, message):
    from utils.shortlink_api import get_shortlink
    from info import SHORTLINK_URL, SHORTLINK_API, VERIFY_TUTORIAL

    user_id = message.from_user.id
    verify_url = f"https://t.me/{client.username}?start=verify_{user_id}"
    short_url = await get_shortlink(verify_url, SHORTLINK_URL, SHORTLINK_API)

    buttons = [
        [InlineKeyboardButton("🔐 Verify Now", url=short_url)],
        [InlineKeyboardButton("📚 How to Verify?", url=VERIFY_TUTORIAL)],
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")]
    ]

    await message.reply(
        Config.VERIFY_TXT,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="html",
        disable_web_page_preview=True
                )
