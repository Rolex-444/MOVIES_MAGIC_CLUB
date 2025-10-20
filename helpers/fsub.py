from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from info import FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL2

async def check_fsub(client, message):
    """Check force subscribe"""
    
    user_id = message.from_user.id
    
    # Check first channel
    if FORCE_SUB_CHANNEL:
        try:
            member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
            if member.status == "kicked":
                await message.reply("You are banned from using this bot!")
                return False
        except UserNotParticipant:
            # User not in channel
            try:
                invite_link = await client.create_chat_invite_link(FORCE_SUB_CHANNEL)
                buttons = [[InlineKeyboardButton("📢 Join Channel", url=invite_link.invite_link)]]
                
                await message.reply(
                    "⚠️ <b>You must join our channel to use this bot!</b>\n\n"
                    "Click the button below to join:",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return False
            except:
                pass
    
    # Check second channel
    if FORCE_SUB_CHANNEL2:
        try:
            member = await client.get_chat_member(FORCE_SUB_CHANNEL2, user_id)
            if member.status == "kicked":
                await message.reply("You are banned from using this bot!")
                return False
        except UserNotParticipant:
            try:
                invite_link = await client.create_chat_invite_link(FORCE_SUB_CHANNEL2)
                buttons = [[InlineKeyboardButton("📢 Join Channel 2", url=invite_link.invite_link)]]
                
                await message.reply(
                    "⚠️ <b>You must join our second channel too!</b>\n\n"
                    "Click the button below to join:",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return False
            except:
                pass
    
    return True
