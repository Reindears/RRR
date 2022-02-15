# (c) @AbirHasan2005

import time
import mimetypes
import traceback
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

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

@Client.on_message((filters.video | filters.audio | filters.document) & ~filters.channel & ~filters.edited)
async def renamestart(c: Client, m: Message):
    await m.reply_text(
        text="**Should I show File Information?**",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Yes", callback_data="rename"),
              InlineKeyboardButton("No", callback_data="closeMessage")]]
        ),
        disable_web_page_preview=True,
        reply_to_message_id=m.message_id
    )




