from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.verify import VerifyDB
from utils.shortlink_api import get_shortlink
from info import VERIFY_EXPIRE, IS_VERIFY, SHORTLINK_URL, SHORTLINK_API, VERIFY_TUTORIAL
from config import Config
import time

verify_db = VerifyDB()

@Client.on_message(filters.command("verify"))
async def verify_command(client, message):
    """Handle verify command"""
    user_id = message.from_user.id
    
    if not IS_VERIFY:
        await message.reply("Verification is currently disabled.")
        return
    
    # Check if already verified
    if await verify_db.is_verified(user_id):
        status = await verify_db.get_verify_status(user_id)
        expire_time = status['expire_at'] - int(time.time())
        hours = expire_time // 3600
        minutes = (expire_time % 3600) // 60
        
        buttons = [
            [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        
        await message.reply(
            f"✅ You are already verified!\n\n"
            f"⏰ Time remaining: {hours}h {minutes}m",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return
    
    # Generate verification link
    verify_url = f"https://t.me/{client.username}?start=verify_{user_id}"
    short_url = await get_shortlink(verify_url, SHORTLINK_URL, SHORTLINK_API)
    
    buttons = [
        [InlineKeyboardButton("🔐 Verify Now", url=short_url)],
        [InlineKeyboardButton("📚 How to Verify?", url=VERIFY_TUTORIAL)],
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")]
    ]
    
    await message.reply(
        Config.VERIFY_TXT,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def check_verification(user_id: int) -> bool:
    """Check if user needs verification"""
    if not IS_VERIFY:
        return True
    return await verify_db.is_verified(user_id)
