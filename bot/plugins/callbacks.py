# (c) @AbirHasan2005

from pyrogram import types
from bot.client import Client
from bot.core.db.database import db
import time
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
from pyrogram.types import ForceReply

from configs import Config
from bot.core.display import progress_for_pyrogram
from bot.core.db.database import db
from bot.core.db.add import add_user_to_database
from bot.core.handlers.not_big import handle_not_big
from bot.core.handlers.time_gap import check_time_gap
from bot.core.handlers.big_rename import handle_big_rename

from bot.core.file_info import (
    get_media_file_name,
    get_media_file_size,
    get_file_type,
    get_file_attr
)
from bot.core.display import humanbytes
from bot.core.handlers.settings import show_settings


@Client.on_callback_query()
async def cb_handlers(c: Client, cb: "types.CallbackQuery"):
    if cb.data == "showSettings":
        await cb.answer()
        await show_settings(cb.message)
    elif cb.data == "showThumbnail":
        thumbnail = await db.get_thumbnail(cb.from_user.id)
        if not thumbnail:
            await cb.answer("No thumbnail found!", show_alert=True)
        else:
            await cb.answer()
            await c.send_photo(cb.message.chat.id, thumbnail,
                               reply_markup=types.InlineKeyboardMarkup([[
                                   types.InlineKeyboardButton("🔄 Update",
                                                              callback_data="setThumbnail"),
                               
                                  types.InlineKeyboardButton("🗑 Delete",
                                                              callback_data="deleteThumbnail")
                               ]
                               ]))
            


    elif cb.data == "deleteThumbnail":
        await db.set_thumbnail(cb.from_user.id, None)
        await cb.answer("Thumbnail set to default", show_alert=True)
        await show_settings(cb.message)
    elif cb.data == "setThumbnail":
        await cb.answer("Ok, Send me an image", show_alert=True)
    elif cb.data == "setCustomCaption":
        await cb.answer()
        await cb.message.edit("Send me your custom caption\n\n"
                              "Press /cancel to cancel process")
        user_input_msg: "types.Message" = await c.listen(cb.message.chat.id)
        if not user_input_msg.text:
            await cb.message.edit("Process Cancelled!")
            return await user_input_msg.continue_propagation()
        if user_input_msg.text and user_input_msg.text.startswith("/"):
            await cb.message.edit("Process Cancelled!")
            return await user_input_msg.continue_propagation()
        await db.set_caption(cb.from_user.id, user_input_msg.text.markdown)
        await cb.message.edit("Custom Caption Saved Successfully!")
    elif cb.data == "triggerApplyCaption":
        await cb.answer()
        apply_caption = await db.get_apply_caption(cb.from_user.id)
        if not apply_caption:
            await db.set_apply_caption(cb.from_user.id, True)
        else:
            await db.set_apply_caption(cb.from_user.id, False)
        await show_settings(cb.message)
    elif cb.data == "triggerApplyDefaultCaption":
        await db.set_caption(cb.from_user.id, None)
        await cb.answer("Caption set to default", show_alert=True)
        await show_settings(cb.message)
    elif cb.data == "showCaption":
        caption = await db.get_caption(cb.from_user.id)
        if not caption:
            await cb.answer("No caption found!", show_alert=True)
        else:
            await cb.answer()
            await cb.message.edit(
                text=caption,
                parse_mode="Markdown",
                               reply_markup=types.InlineKeyboardMarkup([[
                                   types.InlineKeyboardButton("🔄 Update",
                                                              callback_data="setCustomCaption"),
                               
                                  types.InlineKeyboardButton("🗑 Delete",
                                                              callback_data="triggerApplyDefaultCaption")
                               ]
                               ]))
    elif cb.data == "triggerUploadMode":
        await cb.answer()
        upload_as_doc = await db.get_upload_as_doc(cb.from_user.id)
        if upload_as_doc:
            await db.set_upload_as_doc(cb.from_user.id, False)
        else:
            await db.set_upload_as_doc(cb.from_user.id, True)
        await show_settings(cb.message)
    elif cb.data == "showFileInfo":
        replied_m = cb.message.reply_to_message
        _file_name = get_media_file_name(replied_m)
        text = f"**File Name :** `{_file_name}`\n\n" \
               f"**Extension :** `{_file_name.rsplit('.', 1)[-1].upper()}`\n\n" \
               f"**Size :** `{humanbytes(get_media_file_size(replied_m))}`\n\n" \
               f"**Mime Type :** `{get_file_attr(replied_m).mime_type}`"
        await cb.message.edit(
            text=text,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=types.InlineKeyboardMarkup(
                [[types.InlineKeyboardButton("Close Message", callback_data="closeMessage")]]
            )
        )
    elif cb.data == "closeMessage":
        await cb.message.delete(True)
        
    elif cb.data == "rename":
        editable = await cb.message.edit("Now send me new file name")
        user_input_msg: Message = await c.listen(cb.message.chat.id)
        if user_input_msg.text is None:
          await editable.edit("Process Cancelled!")
          return await user_input_msg.continue_propagation()
    _raw_file_name = get_media_file_name(cb.message.reply_to_message)
    await user_input_msg.delete()
    if not _raw_file_name:
        _file_ext = mimetypes.guess_extension(get_file_attr(cb.message.reply_to_message).mime_type)
        _raw_file_name = "UnknownFileName" + _file_ext
    if user_input_msg.text.rsplit(".", 1)[-1].lower() != _raw_file_name.rsplit(".", 1)[-1].lower():
        file_name = user_input_msg.text.rsplit(".", 1)[0][:255] + "." + _raw_file_name.rsplit(".", 1)[-1].lower()
    else:
        file_name = user_input_msg.text[:255]
    await editable.edit("💡")
    is_big = get_media_file_size(cb.message.reply_to_message) > (10 * 1024 * 1024)
    if not is_big:
        _default_thumb_ = await db.get_thumbnail(cb.from_user.id)
        if not _default_thumb_:
            _m_attr = get_file_attr(cb.message.reply_to_message)
            _default_thumb_ = _m_attr.thumbs[0].file_id \
                if (_m_attr and _m_attr.thumbs) \
                else None
        await handle_not_big(c, cb, get_media_file_id(cb.message.reply_to_message), file_name,
                             editable, get_file_type(cb.message.reply_to_message), _default_thumb_)
        return
    file_type = get_file_type(cb.message.reply_to_message)
    _c_file_id = FileId.decode(get_media_file_id(cb.message.reply_to_message))
    try:
        c_time = time.time()
        file_id = await c.custom_upload(
            file_id=_c_file_id,
            file_size=get_media_file_size(cb.message.reply_to_message),
            file_name=file_name,
            progress=progress_for_pyrogram,
            progress_args=(
                "Uploading to Telegram\n"
                f"Data Centre : {_c_file_id.dc_id}",
                editable,
                c_time
            )
        )
        if not file_id:
            return await editable.edit("Failed to Rename!\n\n"
                                       "Maybe your file corrupted :(")
        await handle_big_rename(c, cb, file_id, file_name, editable, file_type)
    except Exception as err:
        await editable.edit("Failed to Rename File!\n\n"
                            f"**Error:** `{err}`\n\n"
                            f"**Traceback:** `{traceback.format_exc()}`")
