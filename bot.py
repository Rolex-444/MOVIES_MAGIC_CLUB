import asyncio
import logging
from aiohttp import web
from pyrogram import Client, idle
from info import API_ID, API_HASH, BOT_TOKEN

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Pyrogram Client
app = Client(
    "MoviesBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins"),
    workers=50
)

# Health check server for Koyeb
async def health(request):
    return web.Response(text="OK", status=200)

async def start_health_server():
    web_app = web.Application()
    web_app.router.add_get('/', health)
    web_app.router.add_get('/health', health)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    logger.info("Health check server started on port 8080")

async def main():
    # Start health check
    await start_health_server()
    
    # Start bot
    await app.start()
    me = await app.get_me()
    logger.info("MOVIES MAGIC CLUB Started ⚡")
    logger.info(f"Bot Username: @{me.username}")
    
    # Keep running
    await idle()

if __name__ == "__main__":
    app.run(main())
