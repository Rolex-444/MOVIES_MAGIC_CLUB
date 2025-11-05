from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import Database
from info import ADMINS, BATCH_FILE_CAPTION, CHANNELS
import asyncio
from pyrogram import enums

db = Database()

@Client.on_message(filters.command("batch") & filters.user(ADMINS))
async def batch_command(client, message):
    if len(message.command) < 3:
        await message.reply(
            "Usage: /batch <first_message_id> <last_message_id>\n\nExample: /batch 100 150",
            parse_mode=enums.ParseMode.HTML
            disable_web_page_preview=True
        )
        return
    try:
        first_id = int(message.command[1])
        last_id = int(message.command[2])
        if first_id >= last_id:
            await message.reply("Last ID must be greater than First ID!", parse_mode="html")
            return
        batch_id = f"{first_id}_{last_id}"
        link = f"https://t.me/{client.username}?start=batch_{batch_id}"
        await message.reply(
            f"✅ <b><i>Batch Link Created!</i></b>\n\n<b>Total Files:</b> {last_id - first_id + 1}\n<b>Link:</b> <code>{link}</code>\n\nShare this link with your users!\n\nJoin: @movies_magic_club3",
            parse_mode=enums.ParseMode.HTML
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply(f"❌ <b><i>Error:</i></b> {e}", parse_mode=enums.ParseMode.HTML)

async def handle_batch(client, message, batch_id):
    try:
        first_id, last_id = map(int, batch_id.split('_'))
        status = await message.reply("Sending files...", parse_mode=enums.ParseMode.HTML)
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
            f"✅ <b><i>Batch Completed!</i></b>\n\n📁 Files sent: {sent}\n\nJoin: @movies_magic_club3",
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        await message.reply(f"❌ <b><i>Error:</i></b> {e}", parse_mode=enums.ParseMode.HTML)
                    
