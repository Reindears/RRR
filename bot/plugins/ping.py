# (c) @AbirHasan2005

from bot.client import Client
from pyrogram import filters
from pyrogram import types
from bot.core.db.add import add_user_to_database


@Client.on_message(filters.command(["start", "ping"]) & filters.private & ~filters.edited)
async def ping_handler(c: Client, m: "types.Message"):
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    await add_user_to_database(c, m)
    await m.reply_sticker("CAACAgIAAxkBAAEDoeVh2A-XwOItIFx4cvNQ_RbdtSkwTgACLgADTlzSKUAuvTVpmIdGIwQ")
    await c.send_flooded_message(
        chat_id=m.chat.id,
        
        text="👋🏻 Hey, **{}**\n\nI'm a rename bot with multiple functions. Check help for usage\n\nI can rename media without downloading it! Speed depends on your media DC.\n\nMade With ❤️ By @Sybots".format(m.from_user.mention),
        reply_markup=types.InlineKeyboardMarkup([
            [
           types.InlineKeyboardButton("Settings",
                                      callback_data="showSettings")
            ],[
           types.InlineKeyboardButton("Help",
                                      callback_data="showSettings"),
           types.InlineKeyboardButton("About",
                                      callback_data="showSettings")],
            [
           types.InlineKeyboardButton("Close",
                                      callback_data="closeMessage")
                
        ]])
    )


@Client.on_message(filters.command("help") & filters.private & ~filters.edited)
async def help_handler(c: Client, m: "types.Message"):
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    await add_user_to_database(c, m)
    await c.send_flooded_message(
        chat_id=m.chat.id,
        text="I can rename media without downloading it!\n"
             "Speed depends on your media DC.\n\n"
             "Just send me media and reply to it with /rename command.\n\n"
             "To set custom thumbnail reply to any image with /set_thumbnail\n\n"
             "To see custom thumbnail press /show_thumbnail",
        reply_markup=types.InlineKeyboardMarkup([[
           types.InlineKeyboardButton("Show Settings",
                                      callback_data="showSettings")]])
    )
