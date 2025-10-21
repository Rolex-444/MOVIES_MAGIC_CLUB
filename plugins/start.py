from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.verify import VerifyDB
from info import START_IMG, ADMINS
from config import Config
import logging

logger = logging.getLogger(__name__)
verify_db = VerifyDB()

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    try:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        
        logger.info(f"Start command from {user_id}")
        
        # Add user to database
        await verify_db.add_user(user_id, first_name)
        
        # Check for deep link parameters
        if len(message.command) > 1:
            data = message.command[1]
            
            # Handle verification callback
            if data.startswith("verify_"):
                token = data.replace("verify_", "")
                verified_user = await verify_db.verify_token(token)
                
                if verified_user:
                    buttons = [
                        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
                        [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
                    ]
                    await message.reply(
                        Config.VERIFIED_TXT,
                        reply_markup=InlineKeyboardMarkup(buttons),
                        parse_mode=enums.ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                    return
                else:
                    await message.reply(
                        "❌ <b>Verification token expired or invalid!</b>\n\nPlease use /verify to get a new verification link.",
                        parse_mode=enums.ParseMode.HTML
                    )
                    return
            
            # Handle referral
            elif data.startswith("ref_"):
                referrer_id = int(data.replace("ref_", ""))
                if referrer_id != user_id:
                    # Add points to referrer
                    from info import REFER_POINT
                    await verify_db.add_points(referrer_id, REFER_POINT)
                    await verify_db.increment_referrals(referrer_id)
                    
                    try:
                        await client.send_message(
                            referrer_id,
                            f"🎉 <b>New Referral!</b>\n\nYou earned {REFER_POINT} points!\n\nUser: {first_name} ({user_id})",
                            parse_mode=enums.ParseMode.HTML
                        )
                    except:
                        pass
        
        # Default start message
        buttons = [
            [InlineKeyboardButton("🆘 Help", callback_data="help"),
             InlineKeyboardButton("ℹ️ About", callback_data="about")],
            [InlineKeyboardButton("🔐 Verify", callback_data="verify_user"),
             InlineKeyboardButton("👑 Premium", callback_data="premium")],
            [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
            [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
        ]
        
        try:
            await message.reply_photo(
                photo=START_IMG,
                caption=Config.START_TXT.format(first_name),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending photo: {e}")
            # Fallback without image
            await message.reply(
                Config.START_TXT.format(first_name),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )
    
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.reply("❌ An error occurred. Please try again later.")


# Callback handlers
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

@Client.on_callback_query(filters.regex("^close$"))
async def close_callback(client, query):
    await query.message.delete()
        
