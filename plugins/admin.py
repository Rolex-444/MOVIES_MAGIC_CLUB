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
    """Show bot statistics"""
    
    total_users = await user_db.total_users_count()
    total_groups = await db.total_groups_count()
    total_files = await db.total_files_count()
    
    text = f"""
📊 <b>Bot Statistics</b>

👥 <b>Total Users:</b> {total_users}
👨‍👩‍👧‍👦 <b>Total Groups:</b> {total_groups}
📁 <b>Total Files:</b> {total_files}

<b>Bot:</b> @{client.username}
<b>Owner:</b> @Siva9789
"""
    
    await message.reply(text)


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_command(client, message):
    """Broadcast message to all users"""
    
    users = await user_db.get_all_users()
    broadcast_msg = message.reply_to_message
    
    status = await message.reply("Starting broadcast...")
    
    success = 0
    failed = 0
    
    for user in users:
        try:
            await broadcast_msg.copy(user['user_id'])
            success += 1
        except Exception as e:
            failed += 1
        
        if (success + failed) % 20 == 0:
            try:
                await status.edit(f"Broadcasting...\n\n✅ Success: {success}\n❌ Failed: {failed}")
            except:
                pass
        
        await asyncio.sleep(1)  # To avoid flood
    
    await status.edit(
        f"<b>Broadcast Completed!</b>\n\n"
        f"✅ <b>Success:</b> {success}\n"
        f"❌ <b>Failed:</b> {failed}"
    )


@Client.on_message(filters.command("delete") & filters.user(ADMINS))
async def delete_all_files(client, message):
    """Delete all files from database"""
    
    buttons = [
        [InlineKeyboardButton("✅ Yes, Delete All", callback_data="confirm_delete_all")],
        [InlineKeyboardButton("❌ Cancel", callback_data="close")]
    ]
    
    await message.reply(
        "⚠️ <b>Warning!</b>\n\n"
        "Are you sure you want to delete ALL files from database?\n"
        "This action cannot be undone!",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex("^confirm_delete_all$") & filters.user(ADMINS))
async def confirm_delete(client, query):
    """Confirm deletion of all files"""
    
    await query.message.edit("Deleting all files...")
    await db.delete_all_files()
    await query.message.edit("✅ All files deleted successfully!")


@Client.on_message(filters.command("deletegroup") & filters.user(ADMINS))
async def delete_group_command(client, message):
    """Remove group from database"""
    
    if len(message.command) < 2:
        await message.reply("Usage: /deletegroup <group_id>")
        return
    
    try:
        group_id = int(message.command[1])
        await db.delete_group(group_id)
        await message.reply(f"✅ Group {group_id} removed from database!")
    except Exception as e:
        await message.reply(f"Error: {e}")


@Client.on_message(filters.command("ban") & filters.user(ADMINS))
async def ban_user_command(client, message):
    """Ban user from bot"""
    
    if len(message.command) < 2:
        await message.reply("Usage: /ban <user_id>")
        return
    
    try:
        user_id = int(message.command[1])
        await user_db.delete_user(user_id)
        await message.reply(f"✅ User {user_id} banned!")
    except Exception as e:
        await message.reply(f"Error: {e}")


@Client.on_message(filters.command("unban") & filters.user(ADMINS))
async def unban_user_command(client, message):
    """Unban user"""
    
    if len(message.command) < 2:
        await message.reply("Usage: /unban <user_id>")
        return
    
    try:
        user_id = int(message.command[1])
        await message.reply(f"User {user_id} can now use the bot again!")
    except Exception as e:
        await message.reply(f"Error: {e}")
