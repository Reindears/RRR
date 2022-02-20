# (c) @AbirHasan2005

from bot.client import Client
from pyrogram import filters
from pyrogram import types
from bot.core.db.add import add_user_to_database
from pyrogram.types import ReplyKeyboardMarkup
import asyncio
from pyrogram import types, errors
from configs import Config
from bot.core.db.database import db

buttonz=ReplyKeyboardMarkup(
            [
                ["Help","Settings"]
                        
            ],
            resize_keyboard=True

)


@Client.on_message(filters.command(["start", "ping"]) & filters.private & ~filters.edited)
async def ping_handler(c: Client, m: "types.Message"):
    await add_user_to_database(c, m)
    await c.send_flooded_message(
        chat_id=m.chat.id,
        
        text="Hi **{}**!\n\nI'm **Rename X bot**. Just send me any File or Video and I'll rename file and Upload remotely to Telegram.\n\n**Don't forget to check Settings before uploading file.**".format(m.from_user.mention),
        reply_markup=buttonz

    )


@Client.on_message(filters.regex("Help"))
async def help_handler(c: Client, m: "types.Message"):
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    await add_user_to_database(c, m)
    await c.delete_messages(
                    chat_id = m.chat.id,
                    message_ids = m.message_id
                )
    await c.send_flooded_message(
        chat_id=m.chat.id,
        text="I can rename media without downloading it!\n"
             "Speed depends on your media DC.\n\n"
             "To set custom thumbnail send me an image\n\n"
             "To see custom thumbnail press /show_thumbnail\n\n"
             "/video_info change-title new title change-video-title new video title change-audio-title new audio title change-subtitle-title new subtitle title change file-name new file name",
    )

@Client.on_message(filters.regex("Settings"))
async def show_ettings(client, message):
    usr_id = message.chat.id
    await client.delete_messages(
                    chat_id = message.chat.id,
                    message_ids = message.message_id
                )
    await add_user_to_database(client, message)
    user_data = await db.get_user_data(usr_id)
    if not user_data:
        await message.reply_text("Failed to fetch your data from database!")
        return
    upload_as_doc = user_data.get("upload_as_doc", False)
    caption = user_data.get("caption", None)
    apply_caption = user_data.get("apply_caption", True)
    thumbnail = user_data.get("thumbnail", None)
    buttons_markup = [
        [types.InlineKeyboardButton(f"📤 Upload - {'Document' if upload_as_doc else 'Video'}",
                                    callback_data="triggerUploadMode")],
        [types.InlineKeyboardButton("🖼 Custom Thumbnail",
                                    callback_data="setThumbnail")],
        [types.InlineKeyboardButton("📚 Custom Caption",
                                    callback_data="setCustomCaption")],
        [types.InlineKeyboardButton(f"Default Caption {'OFF' if caption else 'ON'}",
                                    callback_data="triggerApplyDefaultCaption")],
        [types.InlineKeyboardButton(f"Default Thumbanil {'OFF' if thumbnail else 'ON'}",
                                    callback_data="deleteThumbnail")]
    ]
    if thumbnail:
        buttons_markup.append([types.InlineKeyboardButton("Show Thumbnail",
                                                          callback_data="showThumbnail")])
    if caption:
        buttons_markup.append([types.InlineKeyboardButton("Show Caption",
                                                          callback_data="showCaption")])

    try:
        await message.reply_text(
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
