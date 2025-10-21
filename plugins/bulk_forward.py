from pyrogram import Client, filters
from info import ADMINS
import logging
import asyncio
from datetime import datetime
import re

logger = logging.getLogger(__name__)

forwarding_active = {}


@Client.on_message(filters.command("bulkforward") & filters.user(ADMINS))
async def bulk_forward_files(client, message):
    """Bulk forward with better input parsing"""
    
    try:
        # Clean the message text and remove extra spaces
        text = message.text.strip()
        # Split by spaces and filter out empty strings
        parts = [p.strip() for p in text.split() if p.strip()]
        
        logger.info(f"Received command parts: {parts}")
        
        if len(parts) != 5:
            await message.reply(
                "<b>📤 Bulk Forward Command</b>\n\n"
                "<b>Usage:</b> /bulkforward FROM TO START END\n\n"
                "<b>Example:</b>\n"
                "<code>/bulkforward -1002498541249 -1003000499044 1 3710</code>\n\n"
                "<b>Note:</b> Make sure bot is admin in BOTH channels!",
                parse_mode="HTML"
            )
            return
        
        # Parse numbers - handle negative signs properly
        try:
            from_channel = int(parts[1])
            to_channel = int(parts[2])
            start_id = int(parts[3])
            end_id = int(parts[4])
        except ValueError as e:
            logger.error(f"Parse error: {e}, Parts: {parts}")
            await message.reply(
                f"❌ Error parsing numbers!\n\n"
                f"Received: {parts}\n\n"
                f"Make sure format is:\n"
                f"/bulkforward -1002498541249 -1003000499044 1 3710"
            )
            return
        
        if start_id > end_id:
            await message.reply("❌ Start ID must be less than End ID!")
            return
        
        total = end_id - start_id + 1
        
        # Check if already forwarding
        if forwarding_active.get(message.from_user.id):
            await message.reply("⚠️ You already have an active forwarding task!")
            return
        
        forwarding_active[message.from_user.id] = True
        
        start_time = datetime.now()
        
        status_msg = await message.reply(
            f"<b>🚀 BULK FORWARDING STARTED</b>\n\n"
            f"<b>From:</b> <code>{from_channel}</code>\n"
            f"<b>To:</b> <code>{to_channel}</code>\n"
            f"<b>Range:</b> {start_id} - {end_id}\n"
            f"<b>Total:</b> {total} messages\n\n"
            f"<b>⏳ Initializing...</b>",
            parse_mode="HTML"
        )
        
        # Forward files
        success = 0
        failed = 0
        skipped = 0
        last_update = 0
        
        for msg_id in range(start_id, end_id + 1):
            # Check if user stopped
            if not forwarding_active.get(message.from_user.id):
                break
                
            try:
                await client.forward_messages(
                    chat_id=to_channel,
                    from_chat_id=from_channel,
                    message_ids=msg_id
                )
                success += 1
                
                # Smart delay
                if success < 100:
                    await asyncio.sleep(0.3)
                elif success < 500:
                    await asyncio.sleep(0.5)
                else:
                    await asyncio.sleep(0.7)
                
                # Update every 50 messages
                if success - last_update >= 50:
                    last_update = success
                    elapsed = (datetime.now() - start_time).seconds
                    speed = success / max(elapsed, 1) * 60
                    remaining = total - success - failed - skipped
                    eta = int(remaining / max(speed, 1))
                    
                    await status_msg.edit_text(
                        f"<b>🔄 FORWARDING IN PROGRESS...</b>\n\n"
                        f"<b>From:</b> <code>{from_channel}</code>\n"
                        f"<b>To:</b> <code>{to_channel}</code>\n"
                        f"<b>Total:</b> {total} messages\n\n"
                        f"<b>✅ Success:</b> {success}\n"
                        f"<b>❌ Failed:</b> {failed}\n"
                        f"<b>⏭️ Skipped:</b> {skipped}\n\n"
                        f"<b>📊 Progress:</b> {int((success + failed + skipped) / total * 100)}%\n"
                        f"<b>⚡ Speed:</b> {int(speed)} files/min\n"
                        f"<b>⏱️ ETA:</b> ~{eta} min",
                        parse_mode="HTML"
                    )
                
            except Exception as e:
                error_msg = str(e)
                
                if "FLOOD_WAIT" in error_msg:
                    # Extract wait time
                    wait_time = 60
                    try:
                        wait_time = int(''.join(filter(str.isdigit, error_msg)))
                    except:
                        pass
                    
                    await status_msg.edit_text(
                        f"⚠️ <b>FLOOD WAIT DETECTED</b>\n\n"
                        f"Pausing for {wait_time} seconds...\n"
                        f"Progress: {success}/{total}",
                        parse_mode="HTML"
                    )
                    await asyncio.sleep(wait_time)
                    
                    # Retry
                    try:
                        await client.forward_messages(
                            chat_id=to_channel,
                            from_chat_id=from_channel,
                            message_ids=msg_id
                        )
                        success += 1
                    except:
                        failed += 1
                
                elif "MESSAGE_ID_INVALID" in error_msg or "not found" in error_msg.lower():
                    skipped += 1
                else:
                    failed += 1
                    logger.error(f"Error forwarding {msg_id}: {e}")
        
        # Final status
        forwarding_active[message.from_user.id] = False
        
        elapsed_total = (datetime.now() - start_time).seconds
        elapsed_min = elapsed_total // 60
        elapsed_sec = elapsed_total % 60
        
        await status_msg.edit_text(
            f"<b>✅ FORWARDING COMPLETE!</b>\n\n"
            f"<b>From:</b> <code>{from_channel}</code>\n"
            f"<b>To:</b> <code>{to_channel}</code>\n"
            f"<b>Total:</b> {total} messages\n\n"
            f"<b>✅ Success:</b> {success}\n"
            f"<b>❌ Failed:</b> {failed}\n"
            f"<b>⏭️ Skipped:</b> {skipped}\n\n"
            f"<b>⏱️ Time Taken:</b> {elapsed_min}m {elapsed_sec}s\n"
            f"<b>📊 Success Rate:</b> {int(success / max(total, 1) * 100)}%",
            parse_mode="HTML"
        )
        
    except Exception as e:
        forwarding_active[message.from_user.id] = False
        logger.error(f"Bulk forward error: {e}")
        await message.reply(f"❌ Error: {str(e)}")


@Client.on_message(filters.command("stopforward") & filters.user(ADMINS))
async def stop_forwarding(client, message):
    """Stop active forwarding"""
    if forwarding_active.get(message.from_user.id):
        forwarding_active[message.from_user.id] = False
        await message.reply("⏹️ Forwarding will stop after current message.")
    else:
        await message.reply("❌ No active forwarding task found.")
        
