from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.users import UserDB
import os

user_db = UserDB()

@Client.on_message(filters.command("rename") & filters.private)
async def rename_command(client, message):
    """Rename file command"""
    
    if not message.reply_to_message:
        await message.reply("Reply to a file with /rename <new_name>")
        return
    
    if not message.reply_to_message.media:
        await message.reply("Reply to a media file!")
        return
    
    if len(message.command) < 2:
        await message.reply("Provide new file name!\n\nUsage: /rename <new_name>")
        return
    
    new_name = message.text.split(None, 1)[1]
    
    status = await message.reply("Processing...")
    
    try:
        # Download file
        await status.edit("Downloading...")
        file = await message.reply_to_message.download()
        
        # Upload with new name
        await status.edit("Uploading with new name...")
        
        buttons = [
            [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
        ]
        
        await client.send_document(
            chat_id=message.chat.id,
            document=file,
            file_name=new_name,
            caption=f"<b>Renamed File</b>\n\n<b>New Name:</b> <code>{new_name}</code>\n\n<b>Owner:</b> @Siva9789",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        
        await status.delete()
        
        # Delete downloaded file
        try:
            os.remove(file)
        except:
            pass
        
    except Exception as e:
        await status.edit(f"Error: {e}")
