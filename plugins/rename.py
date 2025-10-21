from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.users import UserDB
import os

user_db = UserDB()

@Client.on_message(filters.command("rename") & filters.private)
async def rename_command(client, message):
    if not message.reply_to_message:
        await message.reply("⚠️ <b><i>Reply to a file with /rename &lt;new_name&gt;</i></b>", parse_mode="html")
        return
    if not message.reply_to_message.media:
        await message.reply("⚠️ <b><i>Reply to a media file!</i></b>", parse_mode="html")
        return
    if len(message.command) < 2:
        await message.reply("⚠️ <b><i>Provide new file name!\n\nUsage: /rename &lt;new_name&gt;</i></b>", parse_mode="html")
        return

    new_name = message.text.split(None, 1)[1]
    status = await message.reply("Processing...", parse_mode="html")

    try:
        await status.edit("Downloading...", parse_mode="html")
        file = await message.reply_to_message.download()
        await status.edit("Uploading with new name...", parse_mode="html")
        buttons = [
            [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
        ]
        await client.send_document(
            chat_id=message.chat.id,
            document=file,
            file_name=new_name,
            caption=f"<b><i>Renamed File</i></b>\n\n<b><i>New Name:</i></b> <code>{new_name}</code>\n\n<b><i>Owner:</i></b> @Siva9789",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="html"
        )
        await status.delete()
        os.remove(file)
    except Exception as e:
        await status.edit(f"❌ <b><i>Error:</i></b> {e}", parse_mode="html")
        
