from pyrogram import Client, filters, enums
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
    
    await message.reply(text, disable_web_page_preview=True)


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_command(client, message):
    users = await user_db.get_all_users()
    broadcast_msg = message.reply_to_message
    status = await message.reply("📤 Starting broadcast...")
    
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
        disable_web_page_preview=True
    )


@Client.on_callback_query(filters.regex("^confirm_delete_all$") & filters.user(ADMINS))
async def confirm_delete(client, query):
    await db.delete_all_files()
    await query.message.edit("✅ All files deleted successfully!")


@Client.on_message(filters.command("deletegroup") & filters.user(ADMINS))
async def delete_group_command(client, message):
    if len(message.command) < 2:
        await message.reply("Usage: /deletegroup <group_id>")
        return
    
    try:
        group_id = int(message.command[1])
        await db.delete_group(group_id)
        await message.reply(f"✅ Group {group_id} removed from the database!")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")


@Client.on_message(filters.command("ban") & filters.user(ADMINS))
async def ban_user_command(client, message):
    if len(message.command) < 2:
        await message.reply("Usage: /ban <user_id>")
        return
    
    try:
        user_id = int(message.command[1])
        await user_db.delete_user(user_id)
        await message.reply(f"✅ User {user_id} banned!")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")


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
                f"📊 <b>Duplicate Files Report</b>\n\n"
                f"🔁 <b>Total Duplicate Files:</b> {total_dupes}\n"
                f"📁 <b>Duplicate Groups:</b> {groups}\n\n"
                f"💡 Use /cleandupes to remove all duplicates!",
                parse_mode=enums.ParseMode.HTML
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
        "⚠️ <b>WARNING</b>\n\n"
        "This will remove ALL duplicate files from database!\n"
        "Only the newest file will be kept for each duplicate.\n\n"
        "Are you sure?",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^confirm_clean_dupes$") & filters.user(ADMINS))
async def confirm_clean_duplicates(client, query):
    """Confirm and execute duplicate cleaning"""
    await query.message.edit("🗑️ Cleaning duplicates... Please wait...")
    
    try:
        deleted_count = await db.delete_duplicate_files(keep_latest=True)
        
        await query.message.edit(
            f"✅ <b>Duplicate Cleaning Complete!</b>\n\n"
            f"🗑️ Deleted: <b>{deleted_count} files</b>\n"
            f"✨ Your database is now clean!",
            parse_mode=enums.ParseMode.HTML
        )
        
        # Send notification to log channel
        if LOG_CHANNEL:
            try:
                await client.send_message(
                    LOG_CHANNEL,
                    f"🗑️ <b>Duplicate Files Cleaned</b>\n\n"
                    f"Admin: {query.from_user.mention}\n"
                    f"Deleted: {deleted_count} duplicate files",
                    parse_mode=enums.ParseMode.HTML
                )
            except:
                pass
                
    except Exception as e:
        await query.message.edit(f"❌ Error cleaning duplicates: {e}")


@Client.on_callback_query(filters.regex("^close$"))
async def close_callback(client, query):
    """Handle close button"""
    await query.message.delete()
    await query.answer()
