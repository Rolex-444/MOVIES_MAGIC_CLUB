from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import Database
from info import ADMINS

db = Database()

@Client.on_message(filters.command("connect") & filters.group)
async def connect_group(client, message):
    """Connect group to bot"""
    
    group_id = message.chat.id
    group_name = message.chat.title
    
    await db.add_group(group_id, group_name)
    
    buttons = [
        [InlineKeyboardButton("🎬 Join Channel", url="https://t.me/movies_magic_club3")]
    ]
    
    await message.reply(
        f"✅ <b>Group Connected Successfully!</b>\n\n"
        f"<b>Group:</b> {group_name}\n"
        f"<b>ID:</b> <code>{group_id}</code>\n\n"
        f"Now you can search movies here!",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_message(filters.command("disconnect") & filters.group & filters.user(ADMINS))
async def disconnect_group(client, message):
    """Disconnect group from bot"""
    
    group_id = message.chat.id
    
    await db.delete_group(group_id)
    
    await message.reply("✅ Group disconnected!")


@Client.on_message(filters.command("connections") & filters.user(ADMINS))
async def show_connections(client, message):
    """Show all connected groups"""
    
    groups = await db.get_all_groups()
    
    if not groups:
        await message.reply("No groups connected!")
        return
    
    text = "<b>Connected Groups:</b>\n\n"
    for i, group in enumerate(groups, 1):
        text += f"{i}. {group['group_name']} - <code>{group['group_id']}</code>\n"
    
    await message.reply(text)
