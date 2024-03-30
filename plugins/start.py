#(©)lcu_bots



import os
import re
import asyncio
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from bot import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT
from helper_func import subscribed, encode, decode, get_messages, check_token, get_token, verify_user, check_verification
from database.database import db
import logging

logging.basicConfig(level=logging.INFO)

async def delete_file(message: Message):
    await asyncio.sleep(3600)
    await message.delete()

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    await db.add_user(client, message)  
    text = message.text
    is_admin = id in ADMINS
    command_params = " ".join(message.command[1:])
    
    # Log command parameters
    logging.info(f"Command Parameters: {command_params}")

    if command_params:
        if command_params.startswith("verify"):
            parts = command_params.split("-", 2)
            if len(parts) == 3:
                verify_userid, token = parts[1:]
                if str(id) == verify_userid:
                    is_valid = await check_token(id, token)
                    if is_valid:
                        await message.reply_text(text=f"<b>You Are Successfully Verified For 12hrs ❤️‍🩹\n\nYou Can Get Any Movie Files Without Verifiy Untill Next 12Hrs.</b>")
                        await verify_user(id, token)
                    else:
                        return await message.reply_text(
                            text="<b>Expired or invalid Verification Link 🫣</b>"
                        )
    
    if not is_admin: 
        text = message.text
        is_verified = await check_verification(id)
        
            if (hour>1 and hour<6):  
                 howto ="https://t.me/TamilSk_Demo"
           elif (hour>6 and hour<11):  
                 howto ="https://t.me/TamilSk_Dema"
           else:
                 howto ="https://t.me/TamilSk_Demk"
       
        if not is_verified:
            btn = [[
                InlineKeyboardButton("👨‍💻 Verify", url=await get_token(id, f"https://filestore.rapidbots.workers.dev?start="))
                ],[
                InlineKeyboardButton("🔻 How to open and Verify 🔺", url=howto)
            ]]
            await message.reply_text(
                text="<b>Hello 👋🏻, You Need To Verify The Link To Get Movie Files, Verification Will Be Expired After 12 Hours.\n\nif You Don't Know how To Verify. Click Below Button To See Your To Verify The Link.</b>",
                protect_content=True,
                
                reply_markup=InlineKeyboardMarkup(btn)
            )
            return
        
    if len(text)>7:
        try:
            base64_string = text.split(" ", 1)[1]
        except Exception as e:
            logging.error(f"Exception occurred while splitting text: {e}")
            return
        
        string = await decode(base64_string)
        argument = string.split("-")
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except Exception as e:
                logging.error(f"Exception occurred while calculating start and end: {e}")
                return
            if start <= end:
                ids = range(start,end+1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except Exception as e:
                logging.error(f"Exception occurred while processing IDs: {e}")
                return
        temp_msg = await message.reply("Please wait...")
        try:
            messages = await get_messages(client, ids)
        except Exception as e:
            logging.error(f"Exception occurred while getting messages: {e}")
            await message.reply_text("Something went wrong..!")
            return
        await temp_msg.delete()

        delete_tasks = []

        for msg in messages:

            if bool(CUSTOM_CAPTION) & bool(msg.document):
                caption = CUSTOM_CAPTION.format(previouscaption = "" if not msg.caption else msg.caption.html, filename = msg.document.file_name)
            elif bool(CUSTOM_CAPTION) & bool(msg.video):
                caption = CUSTOM_CAPTION.format(previouscaption = "" if not msg.caption else msg.caption.html, filename="Video")
            else:
                caption = "" if not msg.caption else msg.caption.html

            if DISABLE_CHANNEL_BUTTON:
                reply_markup = msg.reply_markup
            else:
                reply_markup = None

            try:
                ss = await msg.copy(chat_id=message.from_user.id, caption = caption, parse_mode = ParseMode.HTML, reply_markup = reply_markup, protect_content=PROTECT_CONTENT())
                tt = await ss.reply_text(f"<b>𝙄𝙈𝙋𝙊𝙍𝙏𝘼𝙉𝙏  ↦↦↦⃟👉 This Movie File will be deleted in 1 Hour. So Please forward this File Before Download 📥</b>",disable_web_page_preview=True, quote=True)
                delete_tasks.append(asyncio.create_task(delete_file(ss))) 
                delete_tasks.append(asyncio.create_task(delete_file(tt)))
                await asyncio.sleep(0.5)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                ss = await msg.copy(chat_id=message.from_user.id, caption = caption, parse_mode = ParseMode.HTML, reply_markup = reply_markup, protect_content=PROTECT_CONTENT())
                tt = await ss.reply_text(f"<b>𝙄𝙈𝙋𝙊𝙍𝙏𝘼𝙉𝙏  ↦↦↦⃟👉 This Movie File will be deleted in 1 Hour. So Please forward this File Before Download 📥</b>",disable_web_page_preview=True, quote=True)
                delete_tasks.append(asyncio.create_task(delete_file(ss))) 
                delete_tasks.append(asyncio.create_task(delete_file(tt)))
            except Exception as e:
                # Log exceptions
                logging.error(f"Exception occurred while processing messages: {e}")
                pass
        await asyncio.gather(*delete_tasks)
        return
    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("😊 About Me", callback_data = "about"),
                    InlineKeyboardButton("🔒 Close", callback_data = "close")
                ]
            ]
        )
        await message.reply_text(
            text = START_MSG.format(
                first = message.from_user.first_name,
                last = message.from_user.last_name,
                username = None if not message.from_user.username else '@' + message.from_user.username,
                mention = message.from_user.mention,
                id = message.from_user.id
            ),
            reply_markup = reply_markup,
            disable_web_page_preview = True,
            quote = True
        )
        return
    
#=====================================================================================##

WAIT_MSG = """"<b>Processing ...</b>"""

REPLY_ERROR = """<code>Use this command as a replay to any telegram message with out any spaces.</code>"""

#=====================================================================================##

    
    
@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    buttons = [
        [
            InlineKeyboardButton(
                "Join Channel",
                url = client.invitelink)
        ]
    ]
    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text = 'Try Again',
                    url = f"https://telegram.me/{client.username}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        pass

    await message.reply(
        text = FORCE_MSG.format(
                first = message.from_user.first_name,
                last = message.from_user.last_name,
                username = None if not message.from_user.username else '@' + message.from_user.username,
                mention = message.from_user.mention,
                id = message.from_user.id
            ),
        reply_markup = InlineKeyboardMarkup(buttons),
        quote = True,
        disable_web_page_preview = True
    )

@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await db.total_users_count()
    await msg.edit(f"{users} users are using this bot")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, m: Message):
    all_users = await db.get_all_users()
    broadcast_msg = m.reply_to_message
    sts_msg = await m.reply_text("Bʀᴏᴀᴅᴄᴀꜱᴛ Sᴛᴀʀᴛᴇᴅ..!") 
    done = 0
    failed = 0
    success = 0
    start_time = time.time()
    total_users = await db.total_users_count()
    async for user in all_users:
        sts = await send_msg(user['_id'], broadcast_msg)
        if sts == 200:
           success += 1
        else:
           failed += 1
        if sts == 400:
           await db.delete_user(user['_id'])
        done += 1
        if not done % 20:
           await sts_msg.edit(f"Bʀᴏᴀᴅᴄᴀꜱᴛ Iɴ Pʀᴏɢʀᴇꜱꜱ: \nTᴏᴛᴀʟ Uꜱᴇʀ {total_users} \nCᴏᴍᴩʟᴇᴛᴇᴅ: {done} / {total_users}\nSᴜᴄᴄᴇꜱꜱ: {success}\nFᴀɪʟᴇᴅ: {failed}")
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(f"Bʀᴏᴀᴅᴄᴀꜱᴛ Cᴏᴍᴩʟᴇᴛᴇᴅ: \nCᴏᴍᴩʟᴇᴛᴇᴅ Iɴ `{completed_in}`.\n\nTᴏᴛᴀʟ Uꜱᴇʀꜱ {total_users}\nCᴏᴍᴩʟᴇᴛᴇᴅ: {done} / {total_users}\nSᴜᴄᴄᴇꜱꜱ: {success}\nFᴀɪʟᴇᴅ: {failed}")
           
async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        logger.info(f"{user_id} : Dᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ")
        return 400
    except UserIsBlocked:
        logger.info(f"{user_id} : Bʟᴏᴄᴋᴇᴅ Tʜᴇ Bᴏᴛ")
        return 400
    except PeerIdInvalid:
        logger.info(f"{user_id} : Uꜱᴇʀ Iᴅ Iɴᴠᴀʟɪᴅ")
        return 400
    except Exception as e:
        logger.error(f"{user_id} : {e}")
        return 500
 
