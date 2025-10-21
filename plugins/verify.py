from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.verify import VerifyDB
from utils.shortlink_api import get_shortlink, generate_verify_token
from info import VERIFY_EXPIRE, SHORTLINK_URL, SHORTLINK_API, VERIFY_TUTORIAL, ADMINS
from config import Config
import time

verify_db = VerifyDB()

# 1. Regular user verification command
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


# 2. Verify button callback
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


# 3. NEW: User resets their own verification
@Client.on_message(filters.command("resetverify") & filters.private)
async def reset_verify_command(client, message):
    """Reset user's own verification status"""
    user_id = message.from_user.id
    
    try:
        # Reset verification status
        await verify_db.reset_verification(user_id)
        
        buttons = [
            [InlineKeyboardButton("🔐 Verify Now", callback_data="verify_user")],
            [InlineKeyboardButton("👑 Premium", callback_data="premium")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        
        await message.reply(
            "✅ <b>Verification Reset Successfully!</b>\n\n"
            "Your verification status has been cleared.\n\n"
            "Use /verify to get verified again.\n\n"
            "Join: @movies_magic_club3",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply(
            f"❌ <b>Error:</b> {str(e)}",
            parse_mode=enums.ParseMode.HTML
        )


# 4. NEW: Admin manually verifies any user (instant verification)
@Client.on_message(filters.command("verify_user") & filters.user(ADMINS))
async def admin_verify_user(client, message):
    """Admin command to manually verify any user"""
    if len(message.command) < 2:
        await message.reply(
            "<b>Usage:</b> /verify_user <user_id> [hours]\n\n"
            "<b>Example:</b>\n"
            "/verify_user 123456789 24\n"
            "/verify_user 123456789 (default: 24 hours)\n\n"
            "Instantly verifies a user without shortlink.",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    try:
        target_user_id = int(message.command[1])
        
        # Get hours (default 24)
        hours = 24
        if len(message.command) > 2:
            hours = float(message.command[2])
        
        # Calculate expiry time
        expire_seconds = int(hours * 3600)
        
        # Add verification
        await verify_db.add_verification(target_user_id, expire_seconds)
        
        await message.reply(
            f"✅ <b>User Verified Successfully!</b>\n\n"
            f"User ID: <code>{target_user_id}</code>\n"
            f"Duration: {hours} hours\n\n"
            f"User can now access files without shortlink verification.",
            parse_mode=enums.ParseMode.HTML
        )
        
        # Notify the user
        try:
            await client.send_message(
                target_user_id,
                f"🎉 <b>Congratulations!</b>\n\n"
                f"You have been verified by admin!\n\n"
                f"⏰ Valid for: {hours} hours\n\n"
                f"You can now access unlimited files!\n\n"
                f"Join: @movies_magic_club3",
                parse_mode=enums.ParseMode.HTML
            )
        except:
            await message.reply("Note: Could not notify user (may have blocked bot)")
            
    except ValueError:
        await message.reply(
            "❌ Invalid format! Please provide valid numeric values.\n\n"
            "<b>Example:</b> /verify_user 123456789 24",
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        await message.reply(
            f"❌ <b>Error:</b> {str(e)}",
            parse_mode=enums.ParseMode.HTML
        )


# 5. Admin resets any user's verification
@Client.on_message(filters.command("resetverify_user") & filters.user(ADMINS))
async def admin_reset_verify(client, message):
    """Admin command to reset any user's verification"""
    if len(message.command) < 2:
        await message.reply(
            "<b>Usage:</b> /resetverify_user <user_id>\n\n"
            "<b>Example:</b> /resetverify_user 123456789\n\n"
            "Removes verification from a user.",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    try:
        target_user_id = int(message.command[1])
        
        # Reset verification status
        await verify_db.reset_verification(target_user_id)
        
        await message.reply(
            f"✅ <b>Verification Reset!</b>\n\n"
            f"User ID: <code>{target_user_id}</code>\n\n"
            f"Verification status has been cleared.",
            parse_mode=enums.ParseMode.HTML
        )
        
        # Notify the user
        try:
            await client.send_message(
                target_user_id,
                "⚠️ <b>Verification Reset</b>\n\n"
                "Your verification has been reset by admin.\n\n"
                "Use /verify to get verified again.\n\n"
                "Join: @movies_magic_club3",
                parse_mode=enums.ParseMode.HTML
            )
        except:
            await message.reply("Note: Could not notify user (may have blocked bot)")
            
    except ValueError:
        await message.reply(
            "❌ Invalid user ID! Please provide a valid numeric user ID.",
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        await message.reply(
            f"❌ <b>Error:</b> {str(e)}",
            parse_mode=enums.ParseMode.HTML
        )


# 6. Check verification status (for users and admins)
@Client.on_message(filters.command("mystatus") & filters.private)
async def check_status(client, message):
    """Check your verification and premium status"""
    user_id = message.from_user.id
    
    is_verified = await verify_db.is_verified(user_id)
    is_premium = await verify_db.is_premium(user_id)
    points = await verify_db.get_points(user_id)
    
    user_data = await verify_db.get_user(user_id)
    file_attempts = user_data.get('file_attempts', 0) if user_data else 0
    
    status_text = "📊 <b>Your Status</b>\n\n"
    
    # Verification status
    if is_verified:
        verify_status = await verify_db.get_verify_status(user_id)
        expire_time = verify_status['expire_at'] - int(time.time())
        hours = expire_time // 3600
        minutes = (expire_time % 3600) // 60
        status_text += f"✅ <b>Verified:</b> Yes\n⏰ <b>Time left:</b> {hours}h {minutes}m\n\n"
    else:
        status_text += "❌ <b>Verified:</b> No\n\n"
    
    # Premium status
    if is_premium:
        premium_expire = user_data.get('premium_expire', 0)
        remaining = premium_expire - int(time.time())
        days = remaining // 86400
        hours = (remaining % 86400) // 3600
        status_text += f"👑 <b>Premium:</b> Yes\n⏰ <b>Time left:</b> {days}d {hours}h\n\n"
    else:
        status_text += "👑 <b>Premium:</b> No\n\n"
    
    # Points and file attempts
    status_text += f"💎 <b>Points:</b> {points}\n"
    status_text += f"📁 <b>Files today:</b> {file_attempts}/5\n\n"
    status_text += "Join: @movies_magic_club3"
    
    buttons = [
        [InlineKeyboardButton("🔐 Verify", callback_data="verify_user"),
         InlineKeyboardButton("👑 Premium", callback_data="premium")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    
    await message.reply(
        status_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
        )
    
