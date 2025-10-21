from pyrogram import Client, filters
from info import *
from database.database import Database
import asyncio

db = Database()

# Define your Delete Channel ID (Add in .env or info.py)
DELETE_CHANNEL = int(os.environ.get("DELETE_CHANNEL", "0"))

@Client.on_message(filters.chat(DELETE_CHANNEL))
async def auto_delete_files(client, message):
    """Automatically delete files that are forwarded to the Delete Channel."""

    # 1. Check if message has file attached
    media = message.document or message.video or message.audio
    if not media:
        return await message.reply("⚠️ Not a valid media message!")

    file_id = media.file_id
    file_name = getattr(media, 'file_name', message.caption or "Unknown")

    # Log start
    await message.reply(f"🗑️ Deletion started for: {file_name}")

    # 2. Delete file from MongoDB
    deleted = await db.col.delete_many({'file_id': file_id})
    deleted_by_name = await db.col.delete_many({'file_name': file_name})

    deleted_count = deleted.deleted_count + deleted_by_name.deleted_count

    if deleted_count:
        # Optional: Delete from main file store channel also
        try:
            if 'channel_id' in message.forward_from_chat and 'message_id' in message.forward_from_message_id:
                await client.delete_messages(
                    message.forward_from_chat.id,
                    message.forward_from_message_id
                )
        except:
            pass

        await message.reply(
            f"✅ Successfully deleted {deleted_count} file entry(s) "
            f"from database.\n\nFile: <code>{file_name}</code>"
        )
    else:
        await message.reply(
            f"⚠️ File not found in database!\n\nMaybe it was already deleted or not indexed."
        )

    # Optional - Auto delete confirmation message itself after 30s
    await asyncio.sleep(30)
    try:
        await message.delete()
    except:
        pass
