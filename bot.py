import asyncio
import logging
from pyrogram import Client, idle
from info import API_ID, API_HASH, BOT_TOKEN, PORT, STREAM_MODE, APP_NAME
from stream_server import StreamServer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Client(
    "MoviesBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins"),
    workers=50
)

async def main():
    # Start bot
    await app.start()
    me = await app.get_me()
    logger.info("🎬 MOVIES MAGIC CLUB Started ⚡")
    logger.info(f"👤 Bot Username: @{me.username}")
    
    # Start streaming server if enabled
    if STREAM_MODE or APP_NAME:
        try:
            stream_server = StreamServer(app)
            await stream_server.start(host='0.0.0.0', port=int(PORT))
            logger.info("✅ Streaming server started!")
        except Exception as e:
            logger.error(f"❌ Failed to start streaming server: {e}")
    
    # Keep bot running
    await idle()

if __name__ == "__main__":
    app.run(main())
    
