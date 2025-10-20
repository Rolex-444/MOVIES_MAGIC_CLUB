from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.users import UserDB
from info import REFER_POINT, PREMIUM_POINT

user_db = UserDB()

@Client.on_message(filters.command("refer") & filters.private)
async def referral_command(client, message):
    """Show referral information"""
    
    user_id = message.from_user.id
    points = await user_db.get_points(user_id)
    
    referral_link = f"https://t.me/{client.username}?start=ref_{user_id}"
    
    text = f"""
👥 <b>Referral Program</b>

🎁 <b>Your Points:</b> {points}
💰 <b>Per Referral:</b> {REFER_POINT} points

<b>Your Referral Link:</b>
<code>{referral_link}</code>

<b>How it works:</b>
1. Share your referral link
2. When someone joins using your link, you get {REFER_POINT} points
3. Collect {PREMIUM_POINT} points to get 1 month premium!

Share your link and start earning! 🚀

Join: @movies_magic_club3
"""
    
    buttons = [
        [InlineKeyboardButton("📤 Share Link", url=f"https://t.me/share/url?url={referral_link}&text=Join this amazing movie bot!")],
        [InlineKeyboardButton("👑 Check Premium", callback_data="premium")],
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")]
    ]
    
    await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^referral_info$"))
async def referral_callback(client, query):
    """Referral button callback"""
    user_id = query.from_user.id
    points = await user_db.get_points(user_id)
    
    referral_link = f"https://t.me/{client.username}?start=ref_{user_id}"
    
    text = f"""
👥 <b>Referral Program</b>

🎁 <b>Your Points:</b> {points}
💰 <b>Per Referral:</b> {REFER_POINT} points

<b>Your Referral Link:</b>
<code>{referral_link}</code>

Share and earn! 🚀
"""
    
    buttons = [
        [InlineKeyboardButton("📤 Share Link", url=f"https://t.me/share/url?url={referral_link}")],
        [InlineKeyboardButton("🏠 Home", callback_data="start")]
    ]
    
    await query.message.edit(text, reply_markup=InlineKeyboardMarkup(buttons))


async def handle_referral(client, user_id, referred_by):
    """Add referral points"""
    
    # Check if user already exists
    user = await user_db.get_user(user_id)
    if user and user.get('referred_by'):
        return  # Already referred
    
    # Add points to referrer
    await user_db.add_points(referred_by, REFER_POINT)
    
    # Update user's referral info
    await user_db.update_referral(user_id, referred_by)
    
    # Notify referrer
    try:
        await client.send_message(
            referred_by,
            f"🎉 <b>New Referral!</b>\n\n"
            f"You got {REFER_POINT} points from a new referral!\n\n"
            f"Total Points: {await user_db.get_points(referred_by)}"
        )
    except:
        pass
