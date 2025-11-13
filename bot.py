# bot/main.py
import logging, asyncio
from pyrogram import Client, filters, idle
from .config import settings
from .handlers import start, group, inline, search, callbacks, admin

app = Client("movie-bot",
             api_id=settings.API_ID,
             api_hash=settings.API_HASH,
             bot_token=settings.BOT_TOKEN,
             workers=50,
             sleep_threshold=2)

def register_handlers():
    start.register(app)   # register /start first to avoid being shadowed [web:278]
    group.register(app)
    inline.register(app)
    search.register(app)
    callbacks.register(app)
    admin.register(app)

    # Catch-all logger: remove after debugging
    @app.on_message(filters.private | filters.group)
    async def _debug_any(c, m):
        print("Got message:", getattr(m.chat, "type", "?"), getattr(m, "text", None))  # [web:277]

async def main():
    register_handlers()  # bind decorators to this Client instance before starting [web:306]
    await app.start()    # start client before invoking any API like get_me [web:307]
    me = await app.get_me()
    print(f"Bot online as @{me.username} (id={me.id})")  # confirms you’re DMing the correct bot [web:394]
    await idle()         # keep process alive, dispatch handlers [web:401]
    await app.stop()     # graceful shutdown [web:405]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    asyncio.run(main())  # correct event-loop management on Python 3.11+ [web:371]
