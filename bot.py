import logging
import logging.config
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from database.database import Database
from info import *
import asyncio
from aiohttp import web

# Enable logging
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

# Health check server for Koyeb
async def health_check(request):
    return web.Response(text="Bot is running!")

async def start_health_server():
    """Start health check server on port 8080 for Koyeb"""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    logging.info("Health check server started on port 8080")

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="MovieFilterBot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.username = usr_bot_me.username
        self.namebot = usr_bot_me.first_name
        self.id = usr_bot_me.id
        await Database().create_index()
        
        # Start health check server for Koyeb
        await start_health_server()
        
        logging.info(f"{self.namebot} Started ⚡")
        logging.info(f"Pyrogram version: {__version__}")
        logging.info(f"Layer: {layer}")
        
        if LOG_CHANNEL:
            try:
                await self.send_message(
                    chat_id=LOG_CHANNEL,
                    text=f"<b>{self.namebot} Restarted !</b>"
                )
            except Exception as e:
                logging.error(f"Error sending log message: {e}")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot Stopped 🛑")

bot = Bot()
bot.run()
