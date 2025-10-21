from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import Database
from info import ADMINS

db = Database()

@Client.on_message(filters.command("connect") & filters.group)
async def connect_group(client, message):
    group_id = message.chat.id
    group_name = message.chat.title

    await db.add_group(group_id, group_name)
    
    buttons = [
        [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
    ]

    await message.reply(
        f"✅ <b><i>Group connected successfully!</i></b>\n\n<b>Group:</b> {group_name}\n<b>ID:</b> <code>{group_id}</code>\n\nNow you can search movies here!",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="html"
    )


@Client.on_message(filters.command("disconnect") & filters.group & filters.user(ADMINS))
async def disconnect_group(client, message):
    group_id = message.chat.id
    await db.delete_group(group_id)
    await message.reply("✅ <b><i>Group disconnected!</i></b>", parse_mode="html")
    
