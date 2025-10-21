from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.users import UserDB
from info import ADMINS, PREMIUM_POINT, REFER_POINT
import time

user_db = UserDB()

@Client.on_message(filters.command("premium") & filters.private)
async def premium_info(client, message):
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
👑 <b><i>Premium Status</i></b>

✅ You are a Premium User!

⏰ <b>Time Remaining:</b> {days} days {hours} hours

<b><i>Premium Benefits:</i></b>
• No verification required  
• Instant file access  
• Fast download button  
• Priority support  
• Ad-free experience  
• Faster download links

Join: <a href='https://t.me/movies_magic_club3'>@movies_magic_club3</a>
"""
        buttons = [
            [InlineKeyboardButton("🔞 <b><i>18+ Rare Videos</i></b>", url="https://t.me/REAL_TERABOX_PRO_bot")],
            [InlineKeyboardButton("❌ <b><i>Close</i></b>", callback_data="close")]
        ]
    else:
        text = f"""
👑 <b><i>Premium Plans</i></b>

💎 <b>Your Points:</b> {points}  
🎯 <b>Required Points:</b> {PREMIUM_POINT}

<b><i>Premium Benefits:</i></b>
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

Contact <a href='https://t.me/Siva9789'>@Siva9789</a> for lifetime plans

Join: <a href='https://t.me/movies_magic_club3'>@movies_magic_club3</a>
"""
        buttons = []
        if points >= PREMIUM_POINT:
            buttons.append([InlineKeyboardButton("🎁 <b><i>Redeem Premium</i></b>", callback_data="redeem_premium")])
        buttons.append([InlineKeyboardButton("👥 <b><i>Refer & Earn</i></b>", callback_data="referral_info")])
        buttons.append([InlineKeyboardButton("🔞 <b><i>18+ Rare Videos</i></b>", url="https://t.me/REAL_TERABOX_PRO_bot")])
        buttons.append([InlineKeyboardButton("❌ <b><i>Close</i></b>", callback_data="close")])

    await message.reply(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="html",
        disable_web_page_preview=True
    )


@Client.on_callback_query(filters.regex("^premium$"))
async def premium_callback(client, query):
    await premium_info(client, query.message)


@Client.on_callback_query(filters.regex("^redeem_premium$"))
async def redeem_premium(client, query):
    user_id = query.from_user.id
    points = await user_db.get_points(user_id)

    if points < PREMIUM_POINT:
        await query.answer(f"You need {PREMIUM_POINT - points} more points!", show_alert=True)
        return

    await user_db.deduct_points(user_id, PREMIUM_POINT)
    expire_time = int(time.time()) + (30 * 86400)
    await user_db.make_premium(user_id, expire_time)

    buttons = [
        [InlineKeyboardButton("🔞 <b><i>18+ Rare Videos</i></b>", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("❌ <b><i>Close</i></b>", callback_data="close")]
    ]

    await query.message.edit(
        "🎉 <b><i>Congratulations!</i></b>\n\n"
        "You are now a Premium Member for 30 days!\n\n"
        "Enjoy all premium benefits! 👑\n\n"
        "Join: <a href='https://t.me/movies_magic_club3'>@movies_magic_club3</a>",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="html",
        disable_web_page_preview=True
    )


@Client.on_message(filters.command("give_premium") & filters.user(ADMINS))
async def give_premium_command(client, message):
    if len(message.command) < 3:
        await message.reply("Usage: /give_premium <user_id> <days>", parse_mode="html", disable_web_page_preview=True)
        return

    try:
        user_id = int(message.command[1])
        days = int(message.command[2])
        expire_time = int(time.time()) + (days * 86400)
        await user_db.make_premium(user_id, expire_time)
        await message.reply(f"✅ <b><i>Premium given to user {user_id} for {days} days!</i></b>",parse_mode="html")

        try:
            await client.send_message(user_id,
                                     f"🎉 <b><i>Congratulations!</i></b>\n\nYou have been given Premium access for {days} days!\n\nEnjoy all premium benefits! 👑\n\nJoin: @movies_magic_club3",
                                     parse_mode="html")
        except:
            pass

    except Exception as e:
        await message.reply(f"❌ <b><i>Error:</i></b> {e}", parse_mode="html")
                          
