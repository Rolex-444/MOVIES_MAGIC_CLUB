from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import Database
from info import ADMINS, BATCH_FILE_CAPTION, CHANNELS
import asyncio

db = Database()

@Client.on_message(filters.command("batch") & filters.user(ADMINS))
async def batch_command(client, message):
    """Create batch link"""
    
    if len(message.command) < 3:
        await message.reply(
            "Usage: /batch <first_message_id> <last_message_id>\n\n"
            "Example: /batch 100 150"
        )
        return
    
    try:
        first_id = int(message.command[1])
        last_id = int(message.command[2])
        
        if first_id >= last_id:
            await message.reply("Last ID must be greater than First ID!")
            return
        
        # Create batch link
        batch_id = f"{first_id}_{last_id}"
        link = f"https://t.me/{client.username}?start=batch_{batch_id}"
        
        await message.reply(
            f"✅ <b>Batch Link Created!</b>\n\n"
            f"<b>Total Files:</b> {last_id - first_id + 1}\n"
            f"<b>Link:</b> <code>{link}</code>\n\n"
            f"Share this link with your users!\n\n"
            f"Join: @movies_magic_club3",
            disable_web_page_preview=True
        )
        
    except Exception as e:
        await message.reply(f"Error: {e}")


async def handle_batch(client, message, batch_id):
    """Send batch files"""
    
    try:
        first_id, last_id = map(int, batch_id.split('_'))
        
        status = await message.reply("Sending files...")
        
        sent = 0
        for msg_id in range(first_id, last_id + 1):
            try:
                if CHANNELS:
                    msg = await client.get_messages(CHANNELS[0], msg_id)
                    
                    if msg.media:
                        caption = BATCH_FILE_CAPTION if BATCH_FILE_CAPTION else msg.caption
                        await msg.copy(message.from_user.id, caption=caption)
                        sent += 1
                        await asyncio.sleep(1)
            except:
                continue
        
        await status.delete()
        await message.reply(
            f"✅ <b>Batch Completed!</b>\n\n"
            f"📁 Files sent: {sent}\n\n"
            f"Join: @movies_magic_club3"
        )
        
    except Exception as e:
        await message.reply(f"Error: {e}")
