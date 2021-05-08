#(©)Codexbotz

import asyncio
import base64
from pyrogram import Client, filters, __version__
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait

from bot import Bot
from config import CHANNEL_ID, ADMINS, START_MSG, OWNER_ID
from helper_func import subscribed, encode, decode

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    text = message.text
    if len(text)>7:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return
        string = await decode(base64_string)
        argument = string.split("-")
        if len(argument) == 3:
            try:
                start = int(argument[1])
                end = int(argument[2])
            except:
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
                ids = [int(argument[1])]
            except:
                return
        try:
            msgs = await client.get_messages(
                chat_id=CHANNEL_ID,
                message_ids=ids
            )
        except:
            await message.reply_text("Something went wrong..!")
            return
        for msg in msgs:
            try:
                await msg.copy(chat_id=message.from_user.id)
                await asyncio.sleep(0.5)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await msg.copy(chat_id=message.from_user.id)
            except:
                pass
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
            text = START_MSG.format(firstname = message.chat.first_name),
            reply_markup = reply_markup,
            disable_web_page_preview = True,
            quote = True
        )
        return



@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "about":
        await query.message.edit_text(
            text = f"<b>○ Creator : <a href='tg://user?id={OWNER_ID}'>This Person</a>\n○ Language : <code>Python3</code>\n○ Library : <a href='https://docs.pyrogram.org/'>Pyrogram asyncio {__version__}</a>\n○ Source Code : <a href='https://github.com/CodeXBotz/File-Sharing-Bot'>Click here</a>\n○ Channel : @CodeXBotz\n○ Support Group : @CodeXBotzSupport</b>",
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


@Bot.on_message(filters.private & filters.user(ADMINS) & ~filters.command(['start','batch']))
async def channel_post(client: Client, message: Message):
    reply_text = await message.reply_text("Please Wait...!", quote = True)
    try:
        post_message = await message.copy(chat_id = CHANNEL_ID, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        post_message = await message.copy(chat_id = CHANNEL_ID, disable_notification=True)
    except:
        await reply_text.edit_text("Something went Wrong..!")
        return
    string = f"get-{post_message.message_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await reply_text.edit(f"<b>Here is your link</b>\n\n{link}", reply_markup=reply_markup, disable_web_page_preview = True)


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    while True:
        try:
            first_message = await client.ask(text = "Forward the First Message from the DB Channel (with Quotes)..", chat_id = message.from_user.id, filters=filters.forwarded, timeout=30)
        except:
            return
        if first_message.forward_from_chat:
            if first_message.forward_from_chat.id == CHANNEL_ID:
                f_msg_id = first_message.forward_from_message_id
                break
        await first_message.reply_text("Forward from the Assigned Channel only...", quote = True)
        continue
    while True:
        try:
            second_message = await client.ask(text = "Forward the Last Message from DB Channel (with Quotes)..", chat_id = message.from_user.id, filters=filters.forwarded, timeout=30)
        except:
            return
        if second_message.forward_from_chat:
            if second_message.forward_from_chat.id == CHANNEL_ID:
                s_msg_id = second_message.forward_from_message_id
                break
        await second_message.reply_text("Forward from the Assigned Channel only...", quote = True)
        continue
    string = f"get-{f_msg_id}-{s_msg_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await second_message.reply_text(f"<b>Here is your link</b>\n\n{link}", quote=True, reply_markup=reply_markup)

@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    text = "<b>You need to join in my Channel/Group to use me\n\nKindly Please join Channel</b>"
    message_text = message.text
    try:
        command, argument = message_text.split()
        text = text + f" <b>and <a href='https://t.me/{client.username}?start={argument}'>try again</a></b>"
    except ValueError:
        pass
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url = client.invitelink)]])
    await message.reply(
        text = text,
        reply_markup = reply_markup,
        quote = True,
        disable_web_page_preview = True
    )
