import os
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .db import tb  # Importing the necessary db functions
from .fsub import get_fsub
from Script import text
from config import (
    ADMIN, IS_FSUB, API_ID, API_HASH, LOG_CHANNEL,
    APPROVED_IMAGE_URL, APPROVED_BUTTON_URL, NEW_REQ_MODE
)

# /start command
@Client.on_message(filters.command("start"))
async def start_cmd(client, message):
    if await tb.get_user(message.from_user.id) is None:
        await tb.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(
            LOG_CHANNEL,
            text.LOG.format(message.from_user.mention, message.from_user.id)
        )
    if IS_FSUB and not await get_fsub(client, message): return
    await message.reply_text(
        text.START.format(message.from_user.mention),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('⇆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘs ⇆', url=f"https://telegram.me/Pending_Request_Auto_Accept_Bot?startgroup=true&admin=invite_users")],
            [InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about'),
             InlineKeyboardButton('ʜᴇʟᴘ', callback_data='help')],
            [InlineKeyboardButton('⇆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ⇆', url=f"https://telegram.me/Pending_Request_Auto_Accept_Bot?startchannel=true&admin=invite_users")]
        ])
    )

# /add_admin command
@Client.on_message(filters.command("add_admin") & filters.user(ADMIN))
async def add_admin(client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: /add_admin <user_id>")
    try:
        user_id = int(message.command[1])
        if await tb.add_admin(user_id):
            await message.reply("✅ Admin added successfully!")
        else:
            await message.reply("⚠️ User is already an admin!")
    except Exception as e:
        await message.reply(f"Error: {str(e)}")

# /remove_admin command
@Client.on_message(filters.command("remove_admin") & filters.user(ADMIN))
async def remove_admin(client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: /remove_admin <user_id>")
    try:
        user_id = int(message.command[1])
        if await tb.remove_admin(user_id):
            await message.reply("✅ Admin removed successfully!")
        else:
            await message.reply("⚠️ User is not an admin!")
    except Exception as e:
        await message.reply(f"Error: {str(e)}")

# /admins command
@Client.on_message(filters.command("admins") & filters.user(ADMIN))
async def list_admins(client, message):
    try:
        admins = await tb.get_all_admins()
        admin_list = "\n".join([f"`{admin}`" for admin in admins])
        await message.reply(f"**Admins:**\n{admin_list}")
    except Exception as e:
        await message.reply(f"Error: {str(e)}")

# /setimg command
@Client.on_message(filters.command("setimg") & filters.user(ADMIN))
async def set_start_image(client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: /setimg <image_url>")
    try:
        image_url = message.command[1]
        if await tb.set_start_image(image_url):
            await message.reply("✅ Start image updated successfully!")
        else:
            await message.reply("⚠️ Failed to update start image.")
    except Exception as e:
        await message.reply(f"Error: {str(e)}")

# /removeimg command
@Client.on_message(filters.command("removeimg") & filters.user(ADMIN))
async def remove_start_image(client, message):
    try:
        if await tb.remove_start_image():
            await message.reply("❌ Start image removed successfully.")
        else:
            await message.reply("⚠️ No start image to remove.")
    except Exception as e:
        await message.reply(f"Error: {str(e)}")

# /stats command
@Client.on_message(filters.command("stats") & filters.private & filters.user(ADMIN))
async def total_users(client, message):
    try:
        users = await tb.get_all_users()
        await message.reply(
            f"👥 **Total Users:** {len(users)}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎭 Close", callback_data="close")]
            ])
        )
    except Exception as e:
        r = await message.reply(f"❌ *Error:* `{str(e)}`")
        await asyncio.sleep(30)
        await r.delete()

# /accept command
@Client.on_message(filters.command('accept') & filters.private)
async def accept(client, message):
    show = await message.reply("**Please Wait.....**")
    user_data = await tb.get_session(message.from_user.id)
    if user_data is None:
        return await show.edit("**To accept join requests, please /login first.**")

    try:
        acc = Client("joinrequest", session_string=user_data, api_id=API_ID, api_hash=API_HASH)
        await acc.connect()
    except:
        return await show.edit("**Your login session has expired. Use /logout first, then /login again.**")

    await show.edit("**Forward a message from your Channel or Group (with forward tag).\n\nMake sure your logged-in account is an admin there with full rights.**")
    try:
        fwd_msg = await client.listen(message.chat.id, timeout=60)
    except asyncio.TimeoutError:
        return await show.edit("⏳ Timeout: You didn't forward a message in time.")

    if fwd_msg.forward_from_chat and fwd_msg.forward_from_chat.type not in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
        chat_id = fwd_msg.forward_from_chat.id
        try:
            info = await acc.get_chat(chat_id)
        except:
            return await show.edit("**Error: Ensure your account is admin in this Channel/Group with required rights.**")
    else:
        return await message.reply("**Message not forwarded from a valid Channel/Group.**")

    await fwd_msg.delete()
    msg = await show.edit("**Accepting all join requests... Please wait.**")
    try:
        while True:
            await acc.approve_all_chat_join_requests(chat_id)
            await asyncio.sleep(1)
            join_requests = [req async for req in acc.get_chat_join_requests(chat_id)]
            if not join_requests:
                break
        await msg.edit("✅ Successfully accepted all join requests.")
    except Exception as e:
        await msg.edit(f"**An error occurred:** `{str(e)}`")

# Auto approve new requests
@Client.on_chat_join_request()
async def approve_new(client, m):
    if not NEW_REQ_MODE:
        return
    try:
        await client.approve_chat_join_request(m.chat.id, m.from_user.id)
        try:
            await client.send_photo(
                m.from_user.id,
                photo=APPROVED_IMAGE_URL,
                caption=f"{m.from_user.mention},\n\n𝖸𝗈𝗎𝗋 𝖱𝖾𝗊𝗎𝗌𝗍 𝖳𝗈 𝖩𝗈𝗂𝗇 {m.chat.title} 𝖧𝖺𝗌 𝖡𝖾𝖾𝗇 𝖠𝖼𝖼𝖾𝗉𝗍𝖾𝖽.",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("↗ Visit Channel", url=APPROVED_BUTTON_URL),
                        InlineKeyboardButton("➕ Add Me To Group", url="https://t.me/Pending_Request_Auto_Accept_Bot?startgroup=true")
                    ],
                    [
                        InlineKeyboardButton("ʜᴇɴᴛᴀɪ ɪɴᴅᴀɪɴ 𝟷", url="https://t.me/Adult_Union"),
                        InlineKeyboardButton("sᴇʀɪs", url="https://t.me/Series_Union"),
                        InlineKeyboardButton("ʜᴇɴᴛᴀɪ ɪɴᴅɪᴀɴ 𝟸", url="https://t.me/+xvsmvQrvxSlmYWE1")
                    ]
                ])
            )
        except:
            pass
    except Exception as e:
        print(str(e))

# Help callback
@Client.on_callback_query(filters.regex("help"))
async def help_cb(client, callback_query):
    await callback_query.message.edit(
        "ℹ️ **Help Menu**:\n\nUse /accept to approve requests.\nCommands:\n/setimg\n/removeimg\n/add_admin\n/remove_admin\n/admins\n/stats"
    )

# About callback
@Client.on_callback_query(filters.regex("about"))
async def about_cb(client, callback_query):
    await callback_query.message.edit(
        "🤖 **About This Bot**\n\nThis bot automatically accepts join requests in your channels or groups.\nMade with ❤️ by @Union_Botss"
    )
