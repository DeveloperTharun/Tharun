

import os
import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from bot import Bot
from config import ADMINS, CHANNEL_ID, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT
from helper_func import encode, get_media_file_size

def human_readable_size(size):
    if size < 1024:
        return f"{size} Bytes"
    size /= 1024.0
    if size < 1024:
        return f"{size:.2f} KB"
    size /= 1024.0
    if size < 1024:
        return f"{size:.2f} MB"
    size /= 1024.0
    return f"{size:.2f} GB"

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command("setforcesub"))
async def setCommand(client: Bot, message: Message):
    try:
        channel_id = message.text.split(maxsplit=1)[1]
    except IndexError:
        await message.reply_text("Provide a force sub id to update.")
        return
    try:
        await client.refresh_invite(int(channel_id), raise_exit=False)
    except Exception as er:
        await message.reply_text(f"{er}")
        return
    os.environ["FORCE_SUB_CHANNEL"] = channel_id
    await message.reply_text(f"Force Sub Updated to {channel_id}")

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command("toggleprotect"))
async def setProtect(client: Client, message: Message):
    protectOn = PROTECT_CONTENT()
    os.environ["PROTECT_CONTENT"] = str(not protectOn)
    await message.reply_text(f"Protect changed to `{not protectOn}`")


@Bot.on_message(filters.private & filters.user(ADMINS) & ~filters.command(['start','users','broadcast','batch','genlink','stats', 'setforcesub', 'toggleprotect']))
async def channel_post(client: Client, message: Message):
    reply_text = await message.reply_text("Please Wait...!", quote = True)
    try:
        post_message = await message.copy(chat_id = client.db_channel.id, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        post_message = await message.copy(chat_id = client.db_channel.id, disable_notification=True)
    except Exception as e:
        print(e)
        await reply_text.edit_text("Something went Wrong..!")
        return
    filesize = human_readable_size(get_media_file_size(message))
    converted_id = post_message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://filestore.rapidbots.workers.dev?start={base64_string}"

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])

    await reply_text.edit(f"{previouscaption} {filesize} - <a href='{link}'>Click Here To Download</a>", reply_markup=reply_markup, disable_web_page_preview = True)

    if not DISABLE_CHANNEL_BUTTON:
        await post_message.edit_reply_markup(reply_markup)

@Bot.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(client: Client, message: Message):

    if DISABLE_CHANNEL_BUTTON:
        return

    converted_id = message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://filestore.rapidbots.workers.dev?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    try:
        await message.edit_reply_markup(reply_markup)
    except Exception as e:
        print(e)
        pass
