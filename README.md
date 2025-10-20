# 🎬 Movie Filter Bot

Advanced Telegram Movie Filter Bot with Verification System

## ✨ Features

- 🔍 **Auto Filter Movies** - Search movies with IMDB info
- 🔐 **Universal Shortlink Verification** - Supports GPLinks, Droplink, Arolinks, Clk.wiki, Earnlink, and more
- 👑 **Premium System** - Point-based premium with referral rewards
- 📝 **Rename Files** - Rename files easily
- 🎬 **Stream Files** - Stream movies online (optional)
- 🔗 **Batch File Sharing** - Share multiple files at once
- 📊 **IMDB Integration** - Automatic movie information
- 👥 **Referral System** - Earn points by referring friends
- 📤 **Broadcast Messages** - Send messages to all users
- 📈 **Statistics** - Track bot usage
- 🔞 **18+ Content Promotion** - Built-in promotion button

## 🚀 Deploy to Koyeb (Recommended)

### Prerequisites
1. GitHub account
2. Koyeb account (free tier available)
3. MongoDB Atlas database (free tier)
4. Telegram Bot Token from @BotFather
5. API ID & Hash from https://my.telegram.org

### Deployment Steps

1. **Fork/Clone this repository**
2. **Create MongoDB Database**
- Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- Create free cluster
- Get connection string

3. **Get Telegram Credentials**
- Visit https://my.telegram.org
- Get API_ID and API_HASH
- Create bot with @BotFather
- Get BOT_TOKEN

4. **Deploy on Koyeb**
- Go to [Koyeb Dashboard](https://app.koyeb.com)
- Click "Create Service"
- Select "GitHub"
- Choose your repository
- Select "Dockerfile" as builder
- Set port to **8080**
- Add environment variables (see below)
- Click "Deploy"

## 🔧 Environment Variables

**Required:**
API_ID=12345678
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
DATABASE_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=MovieFilterBot
ADMINS=123456789 987654321
LOG_CHANNEL=-1001234567890

**Optional:**
CHANNELS=-1001234567890 -1009876543210
FORCE_SUB_CHANNEL=-1001234567890
FORCE_SUB_CHANNEL2=-1009876543210
SHORTLINK_URL=https://gplinks.in
SHORTLINK_API=your_api_key
VERIFY_EXPIRE=86400
IS_VERIFY=True
PREMIUM_POINT=1500
REFER_POINT=50
AUTO_DELETE=True
AUTO_DELETE_TIME=600
IMDB=True
SPELL_CHECK=True
PROTECT_CONTENT=False


## 📝 Commands

### User Commands
- `/start` - Start the bot
- `/help` - Get help about bot features
- `/verify` - Verify yourself for 24 hours
- `/premium` - Check premium status and plans
- `/refer` - Get your referral link

### Admin Commands
- `/stats` - Get bot statistics
- `/broadcast` - Broadcast message to all users
- `/index <channel_id>` - Index files from channel
- `/total` - Show total indexed files
- `/delete` - Delete all files from database
- `/deletegroup <group_id>` - Remove group from database
- `/ban <user_id>` - Ban user from bot
- `/give_premium <user_id> <days>` - Give premium to user

## 📚 How to Use

### For Users
1. Start the bot with `/start`
2. Complete verification (valid for 24 hours)
3. Join your groups where bot is added
4. Search for movie name in group
5. Click on file button to get the movie

### For Admins
1. Add bot to your file storage channel(s)
2. Make bot admin with post rights
3. Use `/index <channel_id>` to index files
4. Add bot to your movie groups
5. Use `/connect` in groups to activate bot
6. Users can now search movies

## 🔗 Shortlink Services Supported

- GPLinks (gplinks.in, gplinks.co)
- Droplink (droplink.co)
- Arolinks
- Clk.wiki / Clk.sh / Clk.asia
- Earnlink (earnl.xyz)
- Shortxlinks
- Teralink
- Ouo.io
- And many more...

## 💎 Premium Features

- No verification required
- Instant file access
- Fast download button
- Priority support
- Ad-free experience

**How to Get Premium:**
1. Use `/refer` to get your referral link
2. Share with friends
3. Earn 50 points per referral
4. Redeem 1500 points for 1 month premium

## 🛠️ Tech Stack

- **Language:** Python 3.11
- **Framework:** Pyrogram 2.0
- **Database:** MongoDB
- **Deployment:** Docker (Koyeb)
- **Libraries:** aiohttp, motor, imdbpy

## 📞 Support

- **Channel:** [@movies_magic_club3](https://t.me/movies_magic_club3)
- **Developer:** [@Siva9789](https://t.me/Siva9789)

## 📜 Credits

- **Developer:** [@Siva9789](https://t.me/Siva9789)
- **Channel:** [@movies_magic_club3](https://t.me/movies_magic_club3)
- **Library:** Pyrogram

## ⚖️ License

This project is for educational purposes only.

## 🤝 Contributing

Feel free to contribute to this project by submitting pull requests.

---

Made with ❤️ by [@Siva9789](https://t.me/Siva9789)
