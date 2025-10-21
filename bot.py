import asyncio
import logging
from aiohttp import web
from pyrogram import Client, idle
from info import API_ID, API_HASH, BOT_TOKEN
from database.verify import VerifyDB

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize database
verify_db = VerifyDB()

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="MoviesBot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="plugins"),
            sleep_threshold=60
        )
    
    async def start(self):
        await super().start()
        me = await self.get_me()
        logger.info(f"✅ Bot started as @{me.username}")
        logger.info(f"Pyrogram version: {self.__version__}")
        print("MOVIES MAGIC CLUB Started ⚡")
    
    async def stop(self):
        await super().stop()
        logger.info("Bot stopped!")

# Health check server for Koyeb
async def health_check(request):
    return web.Response(text="OK", status=200)

async def start_health_server():
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    logger.info("Health check server started on port 8080")

async def main():
    # Start health check server
    await start_health_server()
    
    # Start bot
    bot = Bot()
    await bot.start()
    
    # Keep running
    await idle()
    
    # Stop bot
    await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
    
