from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.users import UserDB
from info import ADMINS, PREMIUM_POINT, REFER_POINT
import time

user_db = UserDB()

# 1. Premium Info Command (no changes to your original logic)
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
• Unlimited file access
• Fast download button
• Priority support
• Ad-free experience
• No daily limits

<b>How to Get Premium:</b>
1. Refer friends using /refer
2. Earn {REFER_POINT} points per referral
3. Redeem {PREMIUM_POINT} points for 1 month premium

Pay manually using UPI for instant premium.  
Contact @Siva9789.

Join: @movies_magic_club3
"""
        buttons = []
        if points >= PREMIUM_POINT:
            buttons.append([InlineKeyboardButton("🎁 Redeem Premium", callback_data="redeem_premium")])
        buttons.append([InlineKeyboardButton("👥 Refer & Earn", callback_data="referral_info")])
        buttons.append([InlineKeyboardButton("💸 Buy Premium (UPI)", callback_data="buy_menu")])
        buttons.append([InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")])
        buttons.append([InlineKeyboardButton("❌ Close", callback_data="close")])

    await message.reply(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
    )


@Client.on_callback_query(filters.regex("^premium$"))
async def premium_callback(client, query):
    await premium_info(client, query.message)


# 2. Referral Feature (unchanged)
@Client.on_message(filters.command("refer") & filters.private)
async def referral_command(client, message):
    user_id = message.from_user.id
    points = await user_db.get_points(user_id)
    
    # Get bot username
    me = await client.get_me()
    referral_link = f"https://t.me/{me.username}?start=ref_{user_id}"
    
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

Join: @movies_magic_club3
"""
    buttons = [
        [InlineKeyboardButton("📤 Share Link", url=f"https://t.me/share/url?url={referral_link}&text=Join this amazing movie bot!")],
        [InlineKeyboardButton("👑 Check Premium", callback_data="premium")],
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")]
    ]
    await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)


@Client.on_callback_query(filters.regex("^referral_info$"))
async def referral_callback(client, query):
    await referral_command(client, query.message)


@Client.on_callback_query(filters.regex("^redeem_premium$"))
async def redeem_premium(client, query):
    user_id = query.from_user.id
    points = await user_db.get_points(user_id)
    if points < PREMIUM_POINT:
        await query.answer(f"You need {PREMIUM_POINT - points} more points!", show_alert=True)
        return
    await user_db.deduct_points(user_id, PREMIUM_POINT)
    expire_time = int(time.time()) + (30 * 86400)  # 30 days
    await user_db.make_premium(user_id, expire_time)
    buttons = [
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    await query.message.edit(
        "🎉 <b>Congratulations!</b>\n\nYou are now a Premium Member for 30 days!\n\nEnjoy all premium benefits! 👑\n\nJoin: @movies_magic_club3",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
    )


# 3. Admin command to manually grant premium
@Client.on_message(filters.command("give_premium") & filters.user(ADMINS))
async def give_premium_command(client, message):
    if len(message.command) < 3:
        await message.reply("Usage: /give_premium <user_id> <hours>", parse_mode=enums.ParseMode.HTML)
        return
    try:
        user_id = int(message.command[1])
        hours = float(message.command[2])
        expire_time = int(time.time()) + int(hours * 3600)
        await user_db.make_premium(user_id, expire_time)
        await message.reply(f"✅ Premium given to user {user_id} for {hours} hour(s)!", parse_mode=enums.ParseMode.HTML)
        try:
            await client.send_message(
                user_id,
                f"🎉 <b>Congratulations!</b>\n\nYour premium access is activated for {hours} hour(s).\n\nJoin: @movies_magic_club3",
                parse_mode=enums.ParseMode.HTML
            )
        except:
            pass
    except Exception as e:
        await message.reply(f"❌ Error: {e}", parse_mode=enums.ParseMode.HTML)


# 4. NEW: Payment Menu + Payment Plan Buttons
@Client.on_callback_query(filters.regex("^buy_menu$"))
async def buy_menu(client, query):
    buttons = [
        [InlineKeyboardButton("🕐 1 Hour - ₹1", callback_data="buy_1h")],
        [InlineKeyboardButton("⏳ 6 Hours - ₹5", callback_data="buy_6h")],
        [InlineKeyboardButton("⏰ 12 Hours - ₹10", callback_data="buy_12h")],
        [InlineKeyboardButton("📅 24 Hours - ₹15", callback_data="buy_24h")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    await query.message.edit(
        "<b>Select a premium plan to purchase:</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
    )


@Client.on_callback_query(filters.regex(r"buy_\d+h"))
async def send_payment_info(client, query):
    user_id = query.from_user.id
    plan_code = query.data.split("_")[1]  # '1h', '6h', etc.
    duration_map = {'1h': ('1 Hour', 1), '6h': ('6 Hours', 5), '12h': ('12 Hours', 10), '24h': ('24 Hours', 15)}
    if plan_code not in duration_map:
        await query.answer("Invalid plan.", show_alert=True)
        return
    duration_text, price = duration_map[plan_code]
    upi_id = "sivaramanc49@okaxis"
    payment_channel_id = "-1003037490791"
    qr_file = "IMG_20251021_083257.jpg"  # Make sure this path is correct in your repo

    caption = f"""
<b>Payment for Premium - {duration_text}</b>

🪙 Please pay <b>₹{price}</b> via UPI to the below ID or scan the attached QR code.

<b>UPI ID:</b> <code>{upi_id}</code>

After payment, send the payment screenshot to our <b>Payment Verification Channel</b> (<code>{payment_channel_id}</code>).

Your premium will be activated after admin verification.

Thank you for supporting! 💎
"""
    buttons = [
        [InlineKeyboardButton("❌ Cancel", callback_data="close")]
    ]
    await query.message.edit(
        caption,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        with open(qr_file, "rb") as qr_img:
            await client.send_photo(
                chat_id=user_id,
                photo=qr_img,
                caption=f"Scan this QR code to pay ₹{price}\n\n<b>UPI ID:</b> <code>{upi_id}</code>",
                parse_mode=enums.ParseMode.HTML
            )
    except Exception as e:
        await client.send_message(
            user_id,
            f"Could not send QR image. Please pay to UPI ID: <code>{upi_id}</code>",
            parse_mode=enums.ParseMode.HTML
                          )
    
