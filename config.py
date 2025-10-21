import os
import logging
from logging.handlers import RotatingFileHandler

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            "log.txt",
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)


class Config:
    """Configuration class with all bot messages and settings"""
    
    # Start message
    START_TXT = """
👋 <b>Hello {}</b>

<b>I'm a Movie Filter Bot</b>

I can provide you with movies, series, and files!

<b>Features:</b>
• Auto Filter Movies
• IMDB Info
• Free & Premium Access
• Daily Free Limits
• Refer & Earn Points
• Premium Plans

<b>Join our channel for updates:</b>
@movies_magic_club3
"""

    # Help message
    HELP_TXT = """
<b>How to Use the Bot</b>

<b>For Users:</b>
• Search movie names in connected groups
• Get file links instantly
• Free users: 5 files per day
• Verify for unlimited access (24hrs)

<b>Commands:</b>
/start - Start the bot
/help - Get help
/verify - Verify your account
/premium - Check premium status
/refer - Get referral link

<b>Features:</b>
• Auto Filter Movies
• IMDB Information
• Fast Downloads
• Auto Delete Messages
• Premium Benefits

<b>Need Help?</b>
Contact: @Siva9789
Channel: @movies_magic_club3
"""

    # About message
    ABOUT_TXT = """
<b>Bot Information</b>

<b>Bot:</b> @{}
<b>Channel:</b> @movies_magic_club3
<b>Developer:</b> @Siva9789

<b>Framework:</b> Pyrogram
<b>Language:</b> Python 3
<b>Database:</b> MongoDB
<b>Server:</b> Koyeb

<b>Features:</b>
• Advanced Auto Filter
• IMDB Integration
• Verification System
• Premium Plans
• Referral Rewards
• Daily Free Limits

<b>Support:</b>
For support and updates, join @movies_magic_club3
"""

    # Verification message
    VERIFY_TXT = """
<b>Verification Required</b>

You need to verify to access files.

<b>How to verify:</b>
1. Click the "🔐 Verify Now" button below
2. Complete the verification (click through the pages)
3. Return to the bot
4. Access unlimited files for 24 hours!

<b>Why verify?</b>
• Prevents bot abuse
• Ensures you're a real user
• Keeps the bot running for everyone

<b>Free Users:</b> 5 files per day without verification

<b>Verification valid for 24 hours</b>

Join: @movies_magic_club3
"""

    # Verified message
    VERIFIED_TXT = """
🎉 <b>Verification Successful!</b>

You are now verified and can access unlimited files for the next 24 hours!

<b>Benefits:</b>
• Unlimited file access
• No daily limits
• Fast downloads
• Priority support

<b>Enjoy your movies!</b> 🍿

Join: @movies_magic_club3
"""

    # File caption
    FILE_CAPTION = """
<b>File Name:</b> <code>{file_name}</code>

<b>Size:</b> {file_size}

{caption}

<b>Join:</b> @movies_magic_club3
<b>Owner:</b> @Siva9789
"""

    # Connection success
    CONNECTION_TXT = """
✅ <b>Group Connected Successfully!</b>

<b>Group:</b> {}
<b>ID:</b> <code>{}</code>

Now you can search for movies in this group!

<b>How to use:</b>
Just type the movie name in the group and I'll send you the files!

<b>Join our channel:</b>
@movies_magic_club3
"""

    # Stats message
    STATS_TXT = """
📊 <b>Bot Statistics</b>

<b>Total Users:</b> {}
<b>Total Groups:</b> {}
<b>Total Files:</b> {}

<b>Verified Users:</b> {}
<b>Premium Users:</b> {}

<b>Database:</b> {}
<b>Bot Uptime:</b> {}

<b>Developer:</b> @Siva9789
<b>Channel:</b> @movies_magic_club3
"""

    # Broadcast message
    BROADCAST_TXT = """
📢 <b>Broadcast Status</b>

<b>Total Users:</b> {}
<b>Success:</b> {}
<b>Failed:</b> {}
<b>Deleted:</b> {}

<b>Time Taken:</b> {}

<b>Broadcast Completed!</b>
"""

    # Premium messages
    PREMIUM_TXT = """
👑 <b>Premium Plans</b>

<b>Your Points:</b> {}
<b>Required Points:</b> {}

<b>Premium Benefits:</b>
• No verification required
• Unlimited file access
• Fast download links
• Priority support
• Ad-free experience
• No daily limits

<b>How to Get Premium:</b>
1. Refer friends using /refer
2. Earn {} points per referral
3. Redeem {} points for 1 month premium

<b>Or buy premium with UPI:</b>
• 1 Hour - ₹1
• 6 Hours - ₹5
• 12 Hours - ₹10
• 24 Hours - ₹15

Contact @Siva9789 for lifetime plans

Join: @movies_magic_club3
"""

    # Referral message
    REFER_TXT = """
👥 <b>Referral Program</b>

<b>Your Points:</b> {}
<b>Total Referrals:</b> {}
<b>Per Referral:</b> {} points

<b>Your Referral Link:</b>
<code>{}</code>

<b>How it works:</b>
1. Share your referral link
2. When someone joins using your link, you get {} points
3. Collect {} points to get 1 month premium!

<b>Premium Benefits:</b>
• Unlimited file access
• No verification needed
• Fast downloads
• Priority support

Join: @movies_magic_club3
"""

    # Payment instructions
    PAYMENT_TXT = """
<b>Payment for Premium - {}</b>

🪙 Please pay <b>₹{}</b> via UPI to the below ID or scan the QR code.

<b>UPI ID:</b> <code>sivaramanc49@okaxis</code>

<b>After payment:</b>
Send the payment screenshot to our Payment Verification Channel (ID: <code>-1003037490791</code>).

Your premium will be activated after admin verification.

Thank you for supporting! 💎

Join: @movies_magic_club3
"""

    # Admin help
    ADMIN_TXT = """
<b>Admin Commands</b>

<b>User Management:</b>
/stats - Get bot statistics
/broadcast - Broadcast message to all users
/ban <user_id> - Ban a user
/unban <user_id> - Unban a user

<b>Premium Management:</b>
/give_premium <user_id> <hours> - Give premium to user
/remove_premium <user_id> - Remove premium from user

<b>Database Management:</b>
/delete - Delete all files from database
/deletegroup <group_id> - Remove group from database

<b>File Management:</b>
/index <channel_id> - Index files from channel
/total - Get total indexed files

<b>Verification:</b>
/verify_user <user_id> - Manually verify a user

<b>Developer:</b> @Siva9789
"""
    
