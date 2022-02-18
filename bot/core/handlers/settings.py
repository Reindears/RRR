# (c) @AbirHasan2005

import asyncio
from pyrogram import types, errors
from configs import Config
from bot.core.db.database import db


async def show_settings(m: "types.Message"):
    usr_id = m.chat.id
    user_data = await db.get_user_data(usr_id)
    if not user_data:
        await m.edit("Failed to fetch your data from database!")
        return
    upload_as_doc = user_data.get("upload_as_doc", False)
    caption = user_data.get("caption", None)
    apply_caption = user_data.get("apply_caption", True)
    thumbnail = user_data.get("thumbnail", None)
    buttons_markup = [
        [types.InlineKeyboardButton(f"Upload - {'Document' if upload_as_doc else 'Video'}",
                                    callback_data="triggerUploadMode")],
        [types.InlineKeyboardButton("Set Thumbnail",
                                    callback_data="setThumbnail")],
        [types.InlineKeyboardButton("Add Caption",
                                    callback_data="setCustomCaption")],
        [types.InlineKeyboardButton(f"Default Caption {'❌' if caption else '☑️'}",
                                    callback_data="triggerApplyDefaultCaption")],
        [types.InlineKeyboardButton(f"Default Thumbanil {'❌' if thumbnail else '☑️'}",
                                    callback_data="deleteThumbnail")]
    ]
    if thumbnail:
        buttons_markup.append([types.InlineKeyboardButton("Show Thumbnail",
                                                          callback_data="showThumbnail")])
    if caption:
        buttons_markup.append([types.InlineKeyboardButton("Show Caption",
                                                          callback_data="showCaption")])

    try:
        await m.edit(
            text="**Customize Rename Settings:**",
            reply_markup=types.InlineKeyboardMarkup(buttons_markup),
            disable_web_page_preview=True,
            parse_mode="Markdown"
        )
    except errors.MessageNotModified: pass
    except errors.FloodWait as e:
        await asyncio.sleep(e.x)
        await show_settings(m)
    except Exception as err:
        Config.LOGGER.getLogger(__name__).error(err)
