from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import Database
from database.verify import VerifyDB
from bson import ObjectId
from info import ADMINS, VERIFY_TUTORIAL, CUSTOM_FILE_CAPTION, FREE_FILE_LIMIT, AUTO_DELETE, AUTO_DELETE_TIME, REFER_POINT
from utils.verification import generate_verify_token, create_universal_shortlink
from config import Config
from utils.file_properties import get_size
import logging
import re
import asyncio

logger = logging.getLogger(__name__)

db = Database()
verify_db = VerifyDB()

# Get bot username (set on startup)
bot_username = None

# Your channel info
YOUR_CHANNEL = "@movies_magic_club3"
YOUR_CHANNEL_LINK = "https://t.me/movies_magic_club3"
RARE_VIDEOS_LINK = "https://t.me/REAL_TERABOX_PRO_bot"


def clean_caption(caption):
    """Remove other channel links and mentions from caption"""
    if not caption:
        return caption
    
    caption = re.sub(r'@\w+', '', caption)
    caption = re.sub(r'(https?://)?(t\.me|telegram\.me)/\S+', '', caption)
    
    spam_words = [
        'join', 'subscribe', 'channel', 'group', 'follow',
        'movie', 'download', 'here', 'now', 'free', 'latest',
        '👉', '⚡', '🎬', '📢', '▶️', '🔥', '✅'
    ]
    
    for word in spam_words:
        caption = re.sub(rf'\b{word}\b', '', caption, flags=re.IGNORECASE)
    
    caption = re.sub(r'\s+', ' ', caption)
    caption = caption.strip(' .-_|•~')
    
    return caption


async def process_referral(new_user_id, referrer_id):
    """Process referral when new user joins via referral link"""
    try:
        if new_user_id == referrer_id:
            return False
        
        user_data = await db.get_user(new_user_id)
        if user_data and user_data.get('referred_by'):
            return False
        
        await db.add_points(referrer_id, REFER_POINT)
        await db.update_user(new_user_id, {'referred_by': referrer_id})
        
        referrer_data = await db.get_user(referrer_id)
        current_refs = referrer_data.get('total_referrals', 0) if referrer_data else 0
        await db.update_user(referrer_id, {'total_referrals': current_refs + 1})
        
        logger.info(f"✅ Referral: {referrer_id} → {new_user_id} (+{REFER_POINT} points)")
        return True
        
    except Exception as e:
        logger.error(f"Error processing referral: {e}")
        return False


@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    """Handle /start command and deep links"""
    global bot_username
    if not bot_username:
        me = await client.get_me()
        bot_username = me.username
    
    user_id = message.from_user.id
    
    logger.info(f"⭐ /start from user {user_id}")
    
    await db.add_user(user_id)
    
    # Check if it's a deep link
    if len(message.command) > 1:
        data = message.command[1]
        
        # Handle referral link
        if data.startswith("ref"):
            referrer_id = int(data.replace("ref", ""))
            success = await process_referral(user_id, referrer_id)
            
            if success:
                await message.reply(
                    f"🎉 **Welcome Bonus!**\n\n"
                    f"You've been referred by a friend!\n"
                    f"You both earned bonus points! 🎁\n\n"
                    f"Use /premium to check your benefits!\n\n"
                    f"Join: {YOUR_CHANNEL}",
                    quote=True
                )
                
                try:
                    referrer_data = await db.get_user(referrer_id)
                    points = referrer_data.get('points', 0) if referrer_data else 0
                    await client.send_message(
                        referrer_id,
                        f"🎁 **New Referral!**\n\n"
                        f"User {message.from_user.first_name} joined using your link!\n"
                        f"You earned **+{REFER_POINT} points**\n\n"
                        f"Total Points: **{points}**\n"
                        f"Use /premium to redeem!"
                    )
                except:
                    pass
            else:
                # ✅ 18+ button in welcome message
                buttons = [
                    [InlineKeyboardButton("👑 Get Premium", callback_data="premium"),
                     InlineKeyboardButton("🎁 Referral", callback_data="referral_info")],
                    [InlineKeyboardButton("🔞 18+ RARE VIDEOS💦", url=RARE_VIDEOS_LINK)],
                    [InlineKeyboardButton("🎬 Join Channel", url=YOUR_CHANNEL_LINK)]
                ]
                
                await message.reply(
                    f"👋 Welcome!\n\n"
                    f"🎬 Search for movies in the group\n"
                    f"📁 Or send me a movie name here\n\n"
                    f"Join: {YOUR_CHANNEL}",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            return
        
        # Handle verification token
        elif data.startswith("verify_"):
            token = data
            
            logger.info(f"🔍 Verification attempt by user {user_id}")
            
            token_valid = await verify_db.verify_token(user_id, token)
            
            if token_valid:
                await verify_db.update_verification(user_id)
                
                # ✅ 18+ button after successful verification
                buttons = [
                    [InlineKeyboardButton("🔞 18+ RARE VIDEOS💦", url=RARE_VIDEOS_LINK)],
                    [InlineKeyboardButton("🎬 Join Channel", url=YOUR_CHANNEL_LINK)]
                ]
                
                await message.reply(
                    "✅ **Verification Successful!**\n\n"
                    "You can now access unlimited files for 6 hours!\n"
                    "Search for movies in the group or send me a movie name.",
                    reply_markup=InlineKeyboardMarkup(buttons),
                    quote=True
                )
                logger.info(f"✅ User {user_id} successfully verified!")
            else:
                await message.reply(
                    "❌ **Verification Failed!**\n\n"
                    "Token is invalid or expired. Please try again.",
                    quote=True
                )
                logger.warning(f"❌ User {user_id} verification failed")
            return
        
        # File deep link
        elif data.startswith("file_"):
            file_id = data.split("_", 1)[1]
            await send_file_by_deeplink(client, message, file_id)
            return
    
    # ✅ 18+ button in regular /start message
    buttons = [
        [InlineKeyboardButton("👑 Get Premium", callback_data="premium"),
         InlineKeyboardButton("🎁 Referral", callback_data="referral_info")],
        [InlineKeyboardButton("🔞 18+ RARE VIDEOS💦", url=RARE_VIDEOS_LINK)],
        [InlineKeyboardButton("🎬 Join Channel", url=YOUR_CHANNEL_LINK)]
    ]
    
    await message.reply(
        f"👋 Welcome {message.from_user.first_name}!\n\n"
        f"🎬 Search for movies in the group\n"
        f"📁 Or send me a movie name here\n\n"
        f"💎 Want unlimited access? Check /premium!\n\n"
        f"Join: {YOUR_CHANNEL}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def send_file_by_deeplink(client, message, file_id):
    """Send file when accessed via deep link - WITH VERIFICATION AND AUTO-DELETE"""
    user_id = message.from_user.id
    
    logger.info(f"📥 File request from user {user_id} for file {file_id}")
    
    is_premium = await db.is_premium_user(user_id)
    
    if is_premium:
        logger.info(f"👑 Premium user {user_id} - bypassing verification")
    elif user_id not in ADMINS:
        is_verified = await verify_db.is_verified(user_id)
        
        if not is_verified:
            user_data = await verify_db.get_user(user_id)
            files_sent = user_data.get('files_sent', 0) if user_data else 0
            
            if files_sent >= FREE_FILE_LIMIT:
                logger.info(f"🚫 Access DENIED - showing verification link")
                
                token = generate_verify_token()
                await verify_db.set_verify_token(user_id, f"verify_{token}", 600)
                
                me = await client.get_me()
                telegram_link = f"https://t.me/{me.username}?start=verify_{token}"
                short_url = create_universal_shortlink(telegram_link)
                
                # ✅ 18+ button in verification message
                buttons = [
                    [InlineKeyboardButton("🔐 Verify Now", url=short_url)],
                    [InlineKeyboardButton("📚 How to Verify?", url=VERIFY_TUTORIAL)],
                    [InlineKeyboardButton("👑 Get Premium - No Verification!", callback_data="premium")],
                    [InlineKeyboardButton("🔞 18+ RARE VIDEOS💦", url=RARE_VIDEOS_LINK)]
                ]
                
                verify_msg = f"""
🔐 **Verification Required**

Hello {message.from_user.mention}!

You've used your **{files_sent}/{FREE_FILE_LIMIT} free files**.

**Option 1:** Verify now (Free, valid 6 hours)
**Option 2:** Get Premium (No verification needed!)

⏰ **Verification valid for:** 6 hours
💎 **Premium:** Unlimited access forever!

Click a button below:
"""
                
                await message.reply(
                    verify_msg,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    parse_mode=enums.ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
                return
        
        if not is_verified:
            await verify_db.increment_files_sent(user_id)
    
    # Get file data
    try:
        if len(file_id) == 24:
            mongo_id = ObjectId(file_id)
        else:
            mongo_id = file_id
        file_data = await db.get_file(mongo_id)
    except Exception as e:
        logger.error(f"❌ Error getting file: {e}")
        file_data = None
    
    if not file_data:
        await message.reply("❌ File not found!")
        return
    
    # Clean caption
    original_caption = file_data.get('caption', '')
    file_name = file_data.get('file_name', 'Unknown File')
    file_size = get_size(file_data.get('file_size', 0))
    
    display_name = original_caption if original_caption else file_name
    cleaned_caption = clean_caption(display_name)
    
    logger.info(f"📝 Original: {display_name[:80]}")
    logger.info(f"🧹 Cleaned: {cleaned_caption[:80]}")
    
    # Build caption
    if is_premium:
        caption = f"{cleaned_caption}\n\n👑 **Premium User**\n🎬 Join: {YOUR_CHANNEL}"
    else:
        caption = f"{cleaned_caption}\n\n🎬 Join: {YOUR_CHANNEL}"
    
    # ✅ 18+ button when sending file
    file_buttons = [
        [InlineKeyboardButton("🔞 18+ RARE VIDEOS💦", url=RARE_VIDEOS_LINK)],
        [InlineKeyboardButton("🎬 Join Our Channel", url=YOUR_CHANNEL_LINK)]
    ]
    
    if not is_premium:
        file_buttons.insert(1, [InlineKeyboardButton("👑 Get Premium", callback_data="premium")])
    
    # Send file
    try:
        telegram_file_id = file_data.get('file_id')
        file_type = file_data.get('file_type', 'document')
        
        if file_type == 'video':
            sent_message = await message.reply_video(
                telegram_file_id, 
                caption=caption, 
                reply_markup=InlineKeyboardMarkup(file_buttons)
            )
        elif file_type == 'audio':
            sent_message = await message.reply_audio(
                telegram_file_id, 
                caption=caption, 
                reply_markup=InlineKeyboardMarkup(file_buttons)
            )
        else:
            sent_message = await message.reply_document(
                telegram_file_id, 
                caption=caption, 
                reply_markup=InlineKeyboardMarkup(file_buttons)
            )
        
        logger.info(f"✅ File sent successfully to user {user_id}")
        
        # Auto-delete for non-premium users
        if AUTO_DELETE and not is_premium:
            asyncio.create_task(delete_message_after_delay(sent_message, AUTO_DELETE_TIME))
            
            minutes = AUTO_DELETE_TIME // 60
            await message.reply(
                f"⏰ This file will be deleted in **{minutes} minutes**!\n"
                f"Save it quickly!\n\n"
                f"💡 Get Premium for permanent access - no auto-delete!",
                quote=True
            )
        
    except Exception as e:
        logger.error(f"❌ Error sending file: {e}")
        await message.reply("❌ Error sending file!")


async def delete_message_after_delay(message, delay_seconds):
    """Delete message after specified delay"""
    try:
        await asyncio.sleep(delay_seconds)
        await message.delete()
        logger.info(f"🗑️ Auto-deleted message {message.id}")
    except Exception as e:
        logger.error(f"Error deleting message: {e}")


@Client.on_message(filters.text & filters.group, group=1)
async def group_search_handler(client, message):
    """Handle movie search in GROUPS"""
    search = message.text.strip()
    
    if len(search) < 3 or search.startswith("/"):
        return
    
    logger.info(f"🔍 GROUP SEARCH from {message.chat.id}: '{search}'")
    
    try:
        files, total = await db.search_files(search)
        
        if not files or total == 0:
            logger.info(f"❌ No files found for: {search}")
            return
        
        logger.info(f"✅ Found {total} files")
        
        global bot_username
        if not bot_username:
            me = await client.get_me()
            bot_username = me.username
        
        file_text = f"📁 Found {total} files for `{search}`\n\n"
        
        for file in files[:10]:
            try:
                file_id = str(file.get('_id', ''))
                original_caption = file.get('caption', '')
                file_name = file.get('file_name', 'Unknown')
                display_name = original_caption if original_caption else file_name
                cleaned_name = clean_caption(display_name)
                file_size = get_size(file.get('file_size', 0))
                
                deep_link = f"https://t.me/{bot_username}?start=file_{file_id}"
                clickable_text = f'<a href="{deep_link}">📁 {file_size} ▷ {cleaned_name}</a>'
                file_text += f"{clickable_text}\n\n"
            except Exception as e:
                logger.error(f"Error formatting file: {e}")
                continue
        
        file_text += f"🎬 Join: {YOUR_CHANNEL}"
        
        # ✅ 18+ button in group search results
        buttons = [
            [InlineKeyboardButton("🎭 LANGUAGE", callback_data=f"lang#{search}"),
             InlineKeyboardButton("🎬 Quality", callback_data=f"qual#{search}")],
            [InlineKeyboardButton("📺 Season", callback_data=f"season#{search}"),
             InlineKeyboardButton("📋 Episode", callback_data=f"episode#{search}")],
            [InlineKeyboardButton("🔞 18+ RARE VIDEOS💦", url=RARE_VIDEOS_LINK)],
            [InlineKeyboardButton("👑 Get Premium", callback_data="premium"),
             InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        
        await message.reply(
            file_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
        
        logger.info(f"✅ Search results sent to group {message.chat.id}")
        
    except Exception as e:
        logger.error(f"❌ Error in group_search: {e}", exc_info=True)


@Client.on_message(filters.text & filters.private & ~filters.command(["start", "help", "premium", "referral"]))
async def private_search(client, message):
    """Handle movie search in PRIVATE chat"""
    search = message.text.strip()
    
    logger.info(f"🔍 PRIVATE SEARCH: '{search}'")
    
    try:
        files, total = await db.search_files(search)
        
        if not files:
            await message.reply(f"❌ No files found for: {search}")
            return
        
        global bot_username
        if not bot_username:
            me = await client.get_me()
            bot_username = me.username
        
        file_text = f"📁 Found {total} files for `{search}`\n\n"
        
        for file in files[:10]:
            try:
                file_id = str(file.get('_id', ''))
                original_caption = file.get('caption', '')
                file_name = file.get('file_name', 'Unknown')
                display_name = original_caption if original_caption else file_name
                cleaned_name = clean_caption(display_name)
                file_size = get_size(file.get('file_size', 0))
                
                deep_link = f"https://t.me/{bot_username}?start=file_{file_id}"
                clickable_text = f'<a href="{deep_link}">📁 {file_size} ▷ {cleaned_name}</a>'
                file_text += f"{clickable_text}\n\n"
            except Exception as e:
                logger.error(f"Error: {e}")
        
        file_text += f"🎬 Join: {YOUR_CHANNEL}"
        
        # ✅ 18+ button in private search results
        buttons = [
            [InlineKeyboardButton("🎭 LANGUAGE", callback_data=f"lang#{search}"),
             InlineKeyboardButton("🎬 Quality", callback_data=f"qual#{search}")],
            [InlineKeyboardButton("📺 Season", callback_data=f"season#{search}"),
             InlineKeyboardButton("📋 Episode", callback_data=f"episode#{search}")],
            [InlineKeyboardButton("🔞 18+ RARE VIDEOS💦", url=RARE_VIDEOS_LINK)],
            [InlineKeyboardButton("👑 Get Premium", callback_data="premium"),
             InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        
        await message.reply(
            file_text, 
            reply_markup=InlineKeyboardMarkup(buttons), 
            parse_mode=enums.ParseMode.HTML, 
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"❌ Error in private_search: {e}", exc_info=True)


@Client.on_callback_query(filters.regex("^close$"))
async def close_callback(client, query):
    """Handle close button"""
    await query.message.delete()
    await query.answer()


logger.info("✅ FILTERS PLUGIN LOADED WITH AUTO-DELETE & PREMIUM & 18+ BUTTON")
                           
