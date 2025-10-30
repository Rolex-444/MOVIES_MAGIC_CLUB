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
📊 Bot Statistics

👥 Total Users: {total_users}
👨‍👩‍👧‍👦 Total Groups: {total_groups}
📁 Total Files: {total_files}

Bot: @{client.username}
Owner: @Siva9789
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
        [InlineKeyboardButton("✅ Yes, Delete All", callback_data="confirm_delete_all")],
        [InlineKeyboardButton("❌ Cancel", callback_data="close")]
    ]
    
    await message.reply(
        "⚠️ Are you sure you want to delete ALL files from the database?",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="html",
        disable_web_page_preview=True
    )


@Client.on_callback_query(filters.regex("^confirm_delete_all$") & filters.user(ADMINS))
async def confirm_delete(client, query):
    await db.delete_all_files()
    await query.message.edit(
        "✅ All files deleted successfully!",
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
        await message.reply(f"✅ Group {group_id} removed from the database!", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ Error: {e}", parse_mode="html")


@Client.on_message(filters.command("ban") & filters.user(ADMINS))
async def ban_user_command(client, message):
    if len(message.command) < 2:
        await message.reply("Usage: /ban <user_id>", parse_mode="html")
        return
    
    try:
        user_id = int(message.command[1])
        await user_db.delete_user(user_id)
        await message.reply(f"✅ User {user_id} banned!", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ Error: {e}", parse_mode="html")


# ============ 🆕 DUPLICATE MANAGEMENT COMMANDS ============

@Client.on_message(filters.command("duplicates") & filters.user(ADMINS))
async def check_duplicates_command(client, message):
    """Check how many duplicate files exist"""
    status_msg = await message.reply("🔍 Checking for duplicates...")
    
    try:
        total_dupes, groups = await db.get_duplicate_count()
        
        if total_dupes == 0:
            await status_msg.edit("✅ No duplicate files found!\n\nYour database is clean!")
        else:
            await status_msg.edit(
                f"📊 **Duplicate Files Report**\n\n"
                f"🔁 **Total Duplicate Files:** {total_dupes}\n"
                f"📁 **Duplicate Groups:** {groups}\n\n"
                f"💡 Use /cleandupes to remove all duplicates!",
                parse_mode="markdown"
            )
            
    except Exception as e:
        await status_msg.edit(f"❌ Error checking duplicates: {e}")


@Client.on_message(filters.command("cleandupes") & filters.user(ADMINS))
async def clean_duplicates_command(client, message):
    """Clean all duplicate files from database"""
    buttons = [
        [InlineKeyboardButton("✅ Yes, Clean Duplicates", callback_data="confirm_clean_dupes")],
        [InlineKeyboardButton("❌ Cancel", callback_data="close")]
    ]
    
    await message.reply(
        "⚠️ **WARNING**\n\n"
        "This will remove ALL duplicate files from database!\n"
        "Only the newest file will be kept for each duplicate.\n\n"
        "Are you sure?",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="markdown"
    )


@Client.on_callback_query(filters.regex("^confirm_clean_dupes$") & filters.user(ADMINS))
async def confirm_clean_duplicates(client, query):
    """Confirm and execute duplicate cleaning"""
    await query.message.edit("🗑️ Cleaning duplicates... Please wait...")
    
    try:
        deleted_count = await db.delete_duplicate_files(keep_latest=True)
        
        await query.message.edit(
            f"✅ **Duplicate Cleaning Complete!**\n\n"
            f"🗑️ Deleted: **{deleted_count} files**\n"
            f"✨ Your database is now clean!",
            parse_mode="markdown"
        )
        
        # Send notification to log channel
        if LOG_CHANNEL:
            try:
                await client.send_message(
                    LOG_CHANNEL,
                    f"🗑️ **Duplicate Files Cleaned**\n\n"
                    f"Admin: {query.from_user.mention}\n"
                    f"Deleted: {deleted_count} duplicate files"
                )
            except:
                pass
                
    except Exception as e:
        await query.message.edit(f"❌ Error cleaning duplicates: {e}")
            
