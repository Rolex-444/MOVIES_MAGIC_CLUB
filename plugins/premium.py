from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import Database
from info import PREMIUM_POINT, REFER_POINT
import time

user_db = Database()

# Payment details
PAYMENT_UPI_ID = "sivaramanc49@okaxis"
PAYMENT_CHANNEL_LINK = "https://t.me/+heQIYvXULRxjOGM1"

@Client.on_message(filters.command("premium") & filters.private)
async def premium_command(client, message):
    user_id = message.from_user.id
    
    # Check if already premium
    is_premium = await user_db.is_premium_user(user_id)
    
    if is_premium:
        expire_time = await user_db.get_premium_expire(user_id)
        remaining_days = (expire_time - int(time.time())) // 86400
        
        text = f"""
👑 **PREMIUM USER**

✅ You are already a premium member!

⏰ Valid for: **{remaining_days} days**

💎 **Premium Benefits:**
• Unlimited Downloads
• No Ads
• Instant Access
• Priority Support

Need Help?
Contact: @Siva9789
Channel: @movies_magic_club3
"""
        buttons = [
            [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.MARKDOWN)
        return
    
    # Show premium options
    points = await user_db.get_points(user_id)
    
    text = f"""
💎 **GET PREMIUM ACCESS**

Current Points: **{points}/{PREMIUM_POINT}**

**Choose your plan:**

🟢 **1 Hour - ₹1**
Perfect for quick access

🟡 **1 Day - ₹10**  
24 hours unlimited access

🔵 **1 Month - ₹99**
30 days unlimited access

💜 **FREE via Referrals**
Get {PREMIUM_POINT} points = 1 month free!

**Premium Benefits:**
• ✅ Unlimited Downloads
• ✅ No Verification
• ✅ No Ads
• ✅ Priority Support
"""
    
    buttons = [
        [InlineKeyboardButton("💵 1 Hour - ₹1", callback_data="buy_1hour")],
        [InlineKeyboardButton("💰 1 Day - ₹10", callback_data="buy_1day")],
        [InlineKeyboardButton("💎 1 Month - ₹99", callback_data="buy_1month")],
        [InlineKeyboardButton("🎁 Get Free via Referral", callback_data="referral_info")],
        [InlineKeyboardButton("🔞 18+ Rare Videos", url="https://t.me/REAL_TERABOX_PRO_bot")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    
    await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.MARKDOWN)


@Client.on_callback_query(filters.regex("^premium$"))
async def premium_callback(client, query):
    await premium_command(client, query.message)


@Client.on_callback_query(filters.regex("^buy_"))
async def buy_premium(client, query):
    user_id = query.from_user.id
    plan = query.data.split("_")[1]
    
    # Set price and duration
    if plan == "1hour":
        price = 1
        duration_text = "1 Hour"
    elif plan == "1day":
        price = 10
        duration_text = "1 Day"
    elif plan == "1month":
        price = 99
        duration_text = "1 Month"
    
    caption = f"""
💳 **Payment for Premium - {duration_text}**

💰 Please pay **₹{price}** via UPI to the below ID.

**UPI ID:** `{PAYMENT_UPI_ID}`

After payment, send the payment screenshot to our **Payment Verification Channel** using the button below.

Your premium will be activated after admin verification.

Thank you for supporting! 💎
"""
    
    buttons = [
        [InlineKeyboardButton("📤 Send Payment Proof", url=PAYMENT_CHANNEL_LINK)],
        [InlineKeyboardButton("❌ Cancel", callback_data="premium")]
    ]
    
    await query.message.edit(
        caption,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.MARKDOWN
    )


@Client.on_message(filters.command("referral") & filters.private)
async def referral_command(client, message):
    user_id = message.from_user.id
    points = await user_db.get_points(user_id)
    referrals = await user_db.get_referral_count(user_id)
    
    referral_link = f"https://t.me/{(await client.get_me()).username}?start=ref{user_id}"
    
    text = f"""
🎁 **REFERRAL PROGRAM**

Your Points: **{points}/{PREMIUM_POINT}**
Total Referrals: **{referrals}**

Your Referral Link:
`{referral_link}`

**How it works:**

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
    
    await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.MARKDOWN)


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
        "🎉 **Congratulations!**\n\nYour premium has been activated for 30 days!\n\nEnjoy unlimited access! 💎",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.MARKDOWN
)
    
