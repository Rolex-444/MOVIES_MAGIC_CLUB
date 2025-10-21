from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.verify import VerifyDB
from utils.shortlink_api import get_shortlink
from info import VERIFY_EXPIRE, IS_VERIFY, SHORTLINK_URL, SHORTLINK_API, VERIFY_TUTORIAL
from config import Config
import time

verify_db = VerifyDB()

@Client.on_message(filters.command("verify"))
async def verify_command(client, message):
    user_id = message.from_user.id

    if not IS_VERIFY:
        await message.reply("Verification is currently disabled.", parse_mode="html")
        return

    if await verify_db.is_verified(user_id):
        status = await verify_db.get_verify_status(user_id)
        expire_time = status['expire_at'] - int(time.time())
        hours = expire_time // 3600
        minutes = (expire_time % 3600) // 60

        buttons = [
            [InlineKeyboardButton("🔞 <b><i>18+ Rare Videos</i></b>", url="https://t.me/REAL_TERABOX_PRO_bot")],
            [InlineKeyboardButton("❌ <b><i>Close</i></b>", callback_data="close")]
        ]

        await message.reply(
            f"✅ <b><i>You are already verified!</i></b>\n\n⏰ Time remaining: {hours}h {minutes}m\n\nJoin: <a href='https://t.me/movies_magic_club3'>@movies_magic_club3</a>",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="html",
            disable_web_page_preview=True
        )
        return

    verify_url = f"https://t.me/{client.username}?start=verify_{user_id}"
    short_url = await get_shortlink(verify_url, SHORTLINK_URL, SHORTLINK_API)

    buttons = [
        [InlineKeyboardButton("🔐 <b><i>Verify Now</i></b>", url=short_url)],
        [InlineKeyboardButton("📚 <b><i>How to Verify?</i></b>", url=VERIFY_TUTORIAL)],
        [InlineKeyboardButton("🔞 <b><i>18+ Rare Videos</i></b>", url="https://t.me/REAL_TERABOX_PRO_bot")]
    ]

    await message.reply(
        Config.VERIFY_TXT,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="html",
        disable_web_page_preview=True
    )

async def check_verification(user_id: int) -> bool:
    if not IS_VERIFY:
        return True
    return await verify_db.is_verified(user_id)
