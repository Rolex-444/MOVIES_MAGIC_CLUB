from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.users import UserDB
from info import ADMINS, PREMIUM_POINT, REFER_POINT
import time

user_db = UserDB()

@Client.on_message(filters.command("premium") & filters.private)
async def premium_info(client, message):
    """Show premium information"""
    
    user_id = message.from_user.id
    is_premium = await user_db.is_premium(user_id)
    points = await user_db.get_points(user_id)
    
    if is_premium:
        user = await user_db.get_user(user_id)
        expire_time = user.get('premium_expire', 0)
        remaining = expire_time - int(time.time())
        days = remaining // 86400
        hours = (remaining % 86400) // 3600
        
        text = f"""
👑 <b>Premium Status</b>

✅ You are a Premium User!

⏰ <b>Time Remaining:</b> {days} days {hours} hours

<b>Premium Benefits:</b>
• No verification required
• Instant file access
• Fast download button
• Priority support
• Ad-free experience
• Faster download links

Join: @movies_magic_club3
"""
        buttons = [
            [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
    else:
        text = f"""
👑 <b>Premium Plans</b>

💎 <b>Your Points:</b> {points}
🎯 <b>Required Points:</b> {PREMIUM_POINT}

<b>Premium Benefits:</b>
• No verification required
• Instant file access
• Fast download button
• Priority support
• Ad-free experience
• Faster download links

<b>How to Get Premium:</b>
1. Refer friends using /refer
2. Earn {REFER_POINT} points per referral
3. Redeem {PREMIUM_POINT} points for 1 month premium

<b>Plans:</b>
• 1 Month - {PREMIUM_POINT} points
• Contact @Siva9789 for direct purchase

Join: @movies_magic_club3
"""
        buttons = []
        if points >= PREMIUM_POINT:
            buttons.append([InlineKeyboardButton("🎁 Redeem Premium", callback_data="redeem_premium")])
        buttons.append([InlineKeyboardButton("👥 Refer & Earn", callback_data="referral_info")])
        buttons.append([InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")])
        buttons.append([InlineKeyboardButton("❌ Close", callback_data="close")])
    
    await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^premium$"))
async def premium_callback(client, query):
    """Premium button callback"""
    user_id = query.from_user.id
    is_premium = await user_db.is_premium(user_id)
    points = await user_db.get_points(user_id)
    
    if is_premium:
        user = await user_db.get_user(user_id)
        expire_time = user.get('premium_expire', 0)
        remaining = expire_time - int(time.time())
        days = remaining // 86400
        hours = (remaining % 86400) // 3600
        
        text = f"""
👑 <b>Premium Status</b>

✅ You are a Premium User!

⏰ <b>Time Remaining:</b> {days} days {hours} hours

<b>Premium Benefits:</b>
• No verification required
• Instant file access
• Fast download button
• Priority support
• Ad-free experience

Join: @movies_magic_club3
"""
        buttons = [
            [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
            [InlineKeyboardButton("🏠 Home", callback_data="start")]
        ]
    else:
        text = f"""
👑 <b>Premium Plans</b>

💎 <b>Your Points:</b> {points}
🎯 <b>Required:</b> {PREMIUM_POINT} points

<b>How to Get Premium:</b>
1. Use /refer to get your link
2. Earn {REFER_POINT} points per referral
3. Redeem {PREMIUM_POINT} points

Join: @movies_magic_club3
"""
        buttons = []
        if points >= PREMIUM_POINT:
            buttons.append([InlineKeyboardButton("🎁 Redeem Premium", callback_data="redeem_premium")])
        buttons.append([InlineKeyboardButton("👥 Refer & Earn", callback_data="referral_info")])
        buttons.append([InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")])
        buttons.append([InlineKeyboardButton("🏠 Home", callback_data="start")])
    
    await query.message.edit(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^redeem_premium$"))
async def redeem_premium(client, query):
    """Redeem premium with points"""
    
    user_id = query.from_user.id
    points = await user_db.get_points(user_id)
    
    if points < PREMIUM_POINT:
        await query.answer(f"You need {PREMIUM_POINT - points} more points!", show_alert=True)
        return
    
    # Deduct points and make premium
    await user_db.deduct_points(user_id, PREMIUM_POINT)
    expire_time = int(time.time()) + (30 * 86400)  # 30 days
    await user_db.make_premium(user_id, expire_time)
    
    buttons = [
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    
    await query.message.edit(
        "🎉 <b>Congratulations!</b>\n\n"
        "You are now a Premium Member for 30 days!\n\n"
        "Enjoy all premium benefits! 👑\n\n"
        "Join: @movies_magic_club3",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_message(filters.command("give_premium") & filters.user(ADMINS))
async def give_premium_command(client, message):
    """Give premium to user (Admin only)"""
    
    if len(message.command) < 3:
        await message.reply("Usage: /give_premium <user_id> <days>")
        return
    
    try:
        user_id = int(message.command[1])
        days = int(message.command[2])
        
        expire_time = int(time.time()) + (days * 86400)
        await user_db.make_premium(user_id, expire_time)
        
        await message.reply(f"✅ Premium given to user {user_id} for {days} days!")
        
        try:
            await client.send_message(
                user_id,
                f"🎉 <b>Congratulations!</b>\n\n"
                f"You have been given Premium access for {days} days!\n\n"
                f"Enjoy all premium benefits! 👑\n\n"
                f"Join: @movies_magic_club3"
            )
        except:
            pass
            
    except Exception as e:
        await message.reply(f"Error: {e}")
