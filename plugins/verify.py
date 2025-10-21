from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.verify import VerifyDB
from utils.shortlink_api import get_shortlink, generate_verify_token
from info import VERIFY_EXPIRE, SHORTLINK_URL, SHORTLINK_API, VERIFY_TUTORIAL
from config import Config

verify_db = VerifyDB()

@Client.on_message(filters.command("verify") & filters.private)
async def verify_command(client, message):
    user_id = message.from_user.id
    
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
            f"✅ <b>You are already verified!</b>\n\n⏰ Time remaining: {hours}h {minutes}m\n\nJoin: @movies_magic_club3",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
        return
    
    # Generate verification token
    token = generate_verify_token()
    await verify_db.set_verify_token(user_id, token, 600)  # Token valid for 10 minutes
    
    # Get bot username
    me = await client.get_me()
    
    # Create verification URL
    verify_url = f"https://t.me/{me.username}?start=verify_{token}"
    short_url = get_shortlink(verify_url, SHORTLINK_URL, SHORTLINK_API)
    
    buttons = [
        [InlineKeyboardButton("🔐 Verify Now", url=short_url)],
        [InlineKeyboardButton("📚 How to Verify?", url=VERIFY_TUTORIAL)],
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")]
    ]
    
    await message.reply(
        Config.VERIFY_TXT,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
    )


@Client.on_callback_query(filters.regex("^verify_user$"))
async def verify_callback(client, query):
    user_id = query.from_user.id
    
    # Check if already verified
    if await verify_db.is_verified(user_id):
        await query.answer("✅ You are already verified!", show_alert=True)
        return
    
    # Generate verification token
    token = generate_verify_token()
    await verify_db.set_verify_token(user_id, token, 600)
    
    # Get bot username
    me = await client.get_me()
    
    # Create verification URL
    verify_url = f"https://t.me/{me.username}?start=verify_{token}"
    short_url = get_shortlink(verify_url, SHORTLINK_URL, SHORTLINK_API)
    
    buttons = [
        [InlineKeyboardButton("🔐 Verify Now", url=short_url)],
        [InlineKeyboardButton("📚 How to Verify?", url=VERIFY_TUTORIAL)],
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")]
    ]
    
    await query.message.reply(
        Config.VERIFY_TXT,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
    )
    
