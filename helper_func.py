#(©)lcu_bots

import base64
import re
import asyncio
import random
import string
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from typing import Any, Optional
from pyrogram.types import Message
from config import FORCE_SUB_CHANNEL, ADMINS
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from database.database import db
from pyrogram.errors import FloodWait
from datetime import datetime, timedelta
from shortzy import Shortzy 

TOKENS = {}

async def is_subscribed(filter, client, update):
    if not FORCE_SUB_CHANNEL():
        return True
    user_id = update.from_user.id
    if user_id in ADMINS:
        return True
    try:
        member = await client.get_chat_member(chat_id = FORCE_SUB_CHANNEL(), user_id = user_id)
    except UserNotParticipant:
        return False

    if not member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
        return False
    else:
        return True

async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("ascii")).strip("=")
    return base64_string

async def decode(base64_string):
    base64_string = base64_string.strip("=") # links generated before this commit will be having = sign, hence striping them to handle padding errors.
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes) 
    string = string_bytes.decode("ascii")
    return string

async def get_messages(client, message_ids):
    messages = []
    total_messages = 0
    while total_messages != len(message_ids):
        temb_ids = message_ids[total_messages:total_messages+200]
        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except:
            pass
        total_messages += len(temb_ids)
        messages.extend(msgs)
    return messages

async def get_message_id(client, message):
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
        else:
            return 0
    elif message.forward_sender_name:
        return 0
    elif message.text:
        pattern = "https://t.me/(?:c/)?(.*)/(\d+)"
        matches = re.match(pattern,message.text)
        if not matches:
            return 0
        channel_id = matches.group(1)
        msg_id = int(matches.group(2))
        if channel_id.isdigit():
            if f"-100{channel_id}" == str(client.db_channel.id):
                return msg_id
        else:
            if channel_id == client.db_channel.username:
                return msg_id
    else:
        return 0


def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    hmm = len(time_list)
    for x in range(hmm):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time


subscribed = filters.create(is_subscribed)

def get_media_from_message(message: "Message") -> Any:
    media_types = (
        "audio",
        "document",
        "photo",
        "sticker",
        "animation",
        "video",
        "voice",
        "video_note",
    )
    for attr in media_types:
        media = getattr(message, attr, None)
        if media:
            return media

def get_media_file_size(m):
    media = get_media_from_message(m)
    return getattr(media, "file_size", 0)
    

async def short_link(link):
    current_time = datetime.now() + timedelta(hours=5, minutes=30) 
    hour = current_time.hour
    
    if (hour>1 and hour<6):  
        api = "8b2aa79be0fe87e9299264924b6909117f2c0f22"
        site = "modijiurl.com"
    elif (hour>6 and hour<11):  
        api = "acda894b4b12a377de4341efe6232b6e6d0c5ea5"
        site = "publicearn.com"
    else:
        api = "3giDj1BZD5SL5uGj4SMqWucTiU32"
        site = "shareus.io"
    
    shortzy = Shortzy(api, site) 
    short_link = await shortzy.convert(link)
    return short_link

async def howtov(link):
    current_time = datetime.now() + timedelta(hours=5, minutes=30) 
    hour = current_time.hour
    
    if (hour>1 and hour<6):  
        howto = "https://t.me/TamilSk_Demo"
    elif (hour>6 and hour<11):  
        howto = "https://t.me/TamilSk_Demo"
    else:
        howto = "https://t.me/TamilSk_Demo"

howtov = howto
return howtov


async def check_token(userid, token):
    if userid in TOKENS:
        user_tokens = TOKENS[userid]
        if token in user_tokens and not user_tokens[token]:
            return True
    return False

async def get_token(userid, link):
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    TOKENS.setdefault(userid, {})[token] = False
    ids = f"verify-{userid}-{token}"
    verification_link = f"{link}{ids}"
    shortened_link = await short_link(verification_link)
    return shortened_link

async def verify_user(userid, token):
    if userid in TOKENS:
        user_tokens = TOKENS[userid]
        if token in user_tokens:
            user_tokens[token] = True
            verifyt = datetime.now() + timedelta(hours=12)
            await db.update_user_info(userid, {"verify": verifyt}) 

async def check_verification(userid):
    user = await db.get_userdata(userid)
    verifyt = user.get("verify", None)  
    if verifyt is not None:
        expiration_date = verifyt
        return expiration_date >= datetime.now()
    return False
