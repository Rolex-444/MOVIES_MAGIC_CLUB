from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import Database
from database.users import UserDB
from info import ADMINS, LOG_CHANNEL
import asyncio

db = Database()
user_db = UserDB()

@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats_command(client, message):
    total_users = await user_db.total_users_count()
    total_groups = await db.total_groups_count()
    total_files = await db.total_files_count()

    text = f"""
📊 <b><i>Bot Statistics</i></b>

👥 <b>Total Users:</b> {total_users}
👨‍👩‍👧‍👦 <b>Total Groups:</b> {total_groups}
📁 <b>Total Files:</b> {total_files}

<b>Bot:</b> @{client.username}
<b>Owner:</b> @Siva9789
"""

    await message.reply(text, parse_mode="html", disable_web_page_preview=True)


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_command(client, message):
    users = await user_db.get_all_users()
    broadcast_msg = message.reply_to_message

    status = await message.reply("📤 Starting broadcast...", parse_mode="html")

    success = 0
    failed = 0

    for user in users:
        try:
            await broadcast_msg.copy(user['user_id'])
            success += 1
        except:
            failed += 1

        if (success + failed) % 20 == 0:
            await status.edit(f"Broadcasting...\nSuccess: {success}\nFailed: {failed}")

    await status.edit(f"✅ Broadcast completed!\nSuccess: {success}\nFailed: {failed}")


@Client.on_message(filters.command("delete") & filters.user(ADMINS))
async def delete_all_files(client, message):
    buttons = [
        [InlineKeyboardButton("✅ <b><i>Yes, Delete All</i></b>", callback_data="confirm_delete_all")],
        [InlineKeyboardButton("❌ <b><i>Cancel</i></b>", callback_data="close")]
    ]
    await message.reply(
        "⚠️ <b><i>Are you sure you want to delete ALL files from the database?</i></b>",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="html",
        disable_web_page_preview=True
    )


@Client.on_callback_query(filters.regex("^confirm_delete_all$") & filters.user(ADMINS))
async def confirm_delete(client, query):
    await db.delete_all_files()
    await query.message.edit(
        "✅ <b><i>All files deleted successfully!</i></b>",
        parse_mode="html"
    )


@Client.on_message(filters.command("deletegroup") & filters.user(ADMINS))
async def delete_group_command(client, message):
    if len(message.command) < 2:
        await message.reply("Usage: /deletegroup <group_id>", parse_mode="html")
        return
    try:
        group_id = int(message.command[1])
        await db.delete_group(group_id)
        await message.reply(f"✅ <b><i>Group {group_id} removed from the database!</i></b>", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ <b><i>Error:</i></b> {e}", parse_mode="html")


@Client.on_message(filters.command("ban") & filters.user(ADMINS))
async def ban_user_command(client, message):
    if len(message.command) < 2:
        await message.reply("Usage: /ban <user_id>", parse_mode="html")
        return
    try:
        user_id = int(message.command[1])
        await user_db.delete_user(user_id)
        await message.reply(f"✅ <b><i>User {user_id} banned!</i></b>", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ <b><i>Error:</i></b> {e}", parse_mode="html")
    
