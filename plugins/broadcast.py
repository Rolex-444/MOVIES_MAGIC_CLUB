from pyrogram import Client, filters
from database.users import UserDB
from info import ADMINS
import asyncio

user_db = UserDB()

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_handler(client, message):
    """Broadcast message to all users"""
    
    users = await user_db.get_all_users()
    broadcast_msg = message.reply_to_message
    
    status = await message.reply("Starting broadcast...")
    
    success = 0
    failed = 0
    blocked = 0
    
    for user in users:
        try:
            await broadcast_msg.copy(user['user_id'])
            success += 1
        except Exception as e:
            if "blocked" in str(e).lower():
                blocked += 1
            failed += 1
        
        if (success + failed) % 50 == 0:
            try:
                await status.edit(
                    f"Broadcasting...\n\n"
                    f"✅ Success: {success}\n"
                    f"❌ Failed: {failed}\n"
                    f"🚫 Blocked: {blocked}"
                )
            except:
                pass
        
        await asyncio.sleep(1)
    
    await status.edit(
        f"<b>Broadcast Completed!</b>\n\n"
        f"✅ <b>Success:</b> {success}\n"
        f"❌ <b>Failed:</b> {failed}\n"
        f"🚫 <b>Blocked:</b> {blocked}"
    )
