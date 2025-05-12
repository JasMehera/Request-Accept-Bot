from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from Script import text
from .db import tb  # Importing the necessary db functions

@Client.on_callback_query()
async def callback_query_handler(client, query: CallbackQuery):
    if query.data == "start":
        await query.message.edit_text(
            text.START.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('⇆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘs ⇆', url=f"https://telegram.me/Pending_Request_Auto_Accept_Bot?startgroup=true&admin=invite_users")],
                [InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about'),
                 InlineKeyboardButton('ʜᴇʟᴘ', callback_data='help')],
                [InlineKeyboardButton('⇆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ⇆', url=f"https://telegram.me/Pending_Request_Auto_Accept_Bot?startchannel=true&admin=invite_users")]
            ])
        )

    elif query.data == "help":
        await query.message.edit_text(
            text.HELP.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('ᴜᴩᴅᴀᴛᴇꜱ', url='https://telegram.me/Union_Botss'),
                 InlineKeyboardButton('ꜱᴜᴩᴩᴏʀᴛ', url='https://telegram.me/Union_Botss')],
                [InlineKeyboardButton('ʙᴀᴄᴋ', callback_data="start"),
                 InlineKeyboardButton('ᴄʟᴏꜱᴇ', callback_data="close")]
            ])
        )

    elif query.data == "about":
        await query.message.edit_text(
            text.ABOUT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('💥 ʀᴇᴘᴏ', url='https://t.me/Union_Botss'),
                 InlineKeyboardButton('👨‍💻 ᴏᴡɴᴇʀ', url='https://telegram.me/Union_Botss')],
                [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="start"),
                 InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data="close")]
            ])
        )

    elif query.data == "close":
        await query.message.delete()

    # New feature: show admins list
    elif query.data == "admins":
        admins = await tb.get_all_admins()  # Fetch all admins from the database
        admin_list = "\n".join([str(admin) for admin in admins])  # Format admin list
        await query.message.edit_text(
            f"**Admins:**\n{admin_list}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("↩ Back", callback_data="start"),
                 InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data="close")]
            ])
        )

    # New feature: Add admin button clicked
    elif query.data.startswith("add_admin_"):
        try:
            user_id = int(query.data.split("_")[2])  # Extract user ID from callback data
            if await tb.add_admin(user_id):  # Add user to admin list
                await query.message.edit_text(f"User {user_id} added as an admin successfully.")
            else:
                await query.message.edit_text(f"User {user_id} is already an admin.")
        except Exception as e:
            await query.message.edit_text(f"Error: {str(e)}")

    # New feature: Remove admin button clicked
    elif query.data.startswith("remove_admin_"):
        try:
            user_id = int(query.data.split("_")[2])  # Extract user ID from callback data
            if await tb.remove_admin(user_id):  # Remove user from admin list
                await query.message.edit_text(f"User {user_id} removed from admins successfully.")
            else:
                await query.message.edit_text(f"User {user_id} is not an admin.")
        except Exception as e:
            await query.message.edit_text(f"Error: {str(e)}")

    # Handling setting/removing start image
    elif query.data == "set_start_image":
        await query.message.edit_text(
            "Send the image URL you want to set as the start image."
        )
        await client.listen(query.message.chat.id)

    elif query.data == "remove_start_image":
        if await tb.remove_start_image():  # Check if there's a start image set
            await query.message.edit_text("Start image removed successfully!")
        else:
            await query.message.edit_text("No start image to remove.")

