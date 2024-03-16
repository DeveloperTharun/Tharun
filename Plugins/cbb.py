#(©)Codexbotz

from pyrogram import __version__
from bot import Bot
from config import OWNER_ID
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "about":
        await query.message.edit_text(
            text = f"""<b>
╭────[ ᴛᴀᴍɪʟꜱᴋ ꜰɪʟᴇꜱ ]────⍟
├⍟ ʙᴏᴛ ɴᴀᴍᴇ : <a href='http://telegram.me/TamilSk_Files_Bot'>ᴛᴀᴍɪʟꜱᴋ ꜰɪʟᴇꜱ</a>
├⍟ ᴏᴡɴᴇʀ : <a href='https://telegram.me/King_Tharun'>𝗦𝗞ㅤ〆ㅤͲʜ‌ᴀʀᴜɴ</a>
├⍟ ʟᴀɴɢᴜᴀɢᴇ : <a href='https://www.python.org/download/releases/3.0/'>ᴘʏᴛʜᴏɴ 3</a>
├⍟ ᴍᴏᴠɪᴇꜱ : <a href='https://telegram.me/TamilSk_Moviez'>ᴛᴀᴍɪʟꜱᴋ ᴍᴏᴠɪᴇᴢ</a>
├⍟ ᴅᴇᴠᴇʟᴏᴘᴇʀ : <a href='https://telegram.me/Rapid_Bots'>ʀᴀᴘɪᴅ ʙᴏᴛꜱ</a>
├⍟ ᴍʏ ʙᴇsᴛ ꜰʀɪᴇɴᴅ : <a href='tg://settings'>ᴛʜɪs ᴘᴇʀsᴏɴ</a>
╰────────────────────⍟</b>""",
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔒 Close", callback_data = "close")
                    ]
                ]
            )
        )
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
