# (c) @AbirHasan2005

import time
import mimetypes
import traceback
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot.core.display import humanbytes

from bot.client import (
    Client
)
from pyrogram import filters
from pyrogram.file_id import FileId
from pyrogram.types import Message
from bot.core.file_info import (
    get_media_file_id,
    get_media_file_size,
    get_media_file_name,
    get_file_type,
    get_file_attr
)
from configs import Config
from bot.core.display import progress_for_pyrogram
from bot.core.db.database import db
from bot.core.db.add import add_user_to_database
from bot.core.handlers.not_big import handle_not_big
from bot.core.handlers.time_gap import check_time_gap
from bot.core.handlers.big_rename import handle_big_rename



@Client.on_message((filters.video | filters.audio | filters.document) & ~filters.edited)
async def renamestart(c: Client, m: Message): 
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    await add_user_to_database(c, m)

    if m.from_user.id not in Config.PRO_USERS:
        is_in_gap, sleep_time = await check_time_gap(m.from_user.id)
        if is_in_gap:
            await m.reply_text("🚧 Flood Wait\n\n"
                               f"Send After `{str(sleep_time)}s`",
                               quote=True)
            return
    if Config.LOG_CHANNEL:
        try:
            media = await m.copy(chat_id=Config.LOG_CHANNEL)
            trace_msg = await media.reply_text(f'**User Name:** {m.from_user.mention(style="md")}\n\n**User Id:** `{m.from_user.id}`\n\n <a href="tg://user?id={m.from_user.mention}"><b>Click Here</b></a>')
        except PeerIdInvalid:
            logger.warning("Give the correct Channel or Group ID.")
    replied_m = m
    _file_name = get_media_file_name(replied_m)
    text = f"**File Name :** `{_file_name}`\n\n" \
               f"**Extension Type :** `{_file_name.rsplit('.', 1)[-1].upper()}`\n\n" \
               f"**File Size :** `{humanbytes(get_media_file_size(replied_m))}`\n\n" \
               f"**Mime Type :** `{get_file_attr(replied_m).mime_type}`"

    await m.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("✏️ Rename", callback_data="rename"),
              InlineKeyboardButton("📄 Caption", callback_data="capx")]
            ]
        ),
        disable_web_page_preview=True,
        reply_to_message_id=m.message_id
    )

