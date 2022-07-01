import os
import math
import json
import time
import shutil
import heroku3
import requests
import random
import asyncio

from pyrogram import filters
from pyrogram import Client as trojanz
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

from script import Script
from plugins.helpers import humanbytes
from database.filters_mdb import filter_stats
from database.users_mdb import add_user, find_user, all_users

PHOTO = [
    "https://telegra.ph/file/deff330b37cbd94edb8f5.jpg",
    "https://telegra.ph/file/16918ea9f0328b33f1ef3.jpg",
    "https://telegra.ph/file/abe81ce6cd523b91f5345.jpg",
    "https://telegra.ph/file/3e0198294139e145f31bb.jpg",
    "https://telegra.ph/file/05332ecebfda209f294bd.jpg",
    "https://telegra.ph/file/40dd134de09eb8d69866e.jpg",
    "https://telegra.ph/file/a09d0ef056ce5a734b584.jpg",
    "https://telegra.ph/file/26d4b8ecfac381b362794.jpg",
    "https://telegra.ph/file/4a9cd6cf90f547c0a1100.jpg",
    "https://telegra.ph/file/224c1799f4f813fb6dfc1.jpg",
    "https://telegra.ph/file/dbfac4a2fa33c715bec8e.jpg"
]

@trojanz.on_message(filters.command('id') & (filters.private | filters.group))
async def showid(client, message):
    chat_type = message.chat.type

    if chat_type == "private":
        user_id = message.chat.id
        await message.reply_text(
            f"Your ID : `{user_id}`",
            parse_mode="md",
            quote=True
        )
    elif (chat_type == "group") or (chat_type == "supergroup"):
        user_id = message.from_user.id
        chat_id = message.chat.id
        if message.reply_to_message:
            reply_id = f"Replied User ID : `{message.reply_to_message.from_user.id}`"
        else:
            reply_id = ""
        await message.reply_text(
            f"Your ID : `{user_id}`\nThis Group ID : `{chat_id}`\n\n{reply_id}",
            parse_mode="md",
            quote=True
        )   


@trojanz.on_message(filters.command('info') & (filters.private | filters.group))
async def showinfo(client, message):
    try:
        cmd, id = message.text.split(" ", 1)
    except:
        id = False
        pass

    if id:
        if (len(id) == 10 or len(id) == 9):
            try:
                checkid = int(id)
            except:
                await message.reply_text("__Enter a valid USER ID__", quote=True, parse_mode="md")
                return
        else:
            await message.reply_text("__Enter a valid USER ID__", quote=True, parse_mode="md")
            return           

        if Config.SAVE_USER == "yes":
            name, username, dcid = await find_user(str(id))
        else:
            try:
                user = await client.get_users(int(id))
                name = str(user.first_name + (user.last_name or ""))
                username = user.username
                dcid = user.dc_id
            except:
                name = False
                pass

        if not name:
            await message.reply_text("__USER Details not found!!__", quote=True, parse_mode="md")
            return
    else:
        if message.reply_to_message:
            name = str(message.reply_to_message.from_user.first_name\
                    + (message.reply_to_message.from_user.last_name or ""))
            id = message.reply_to_message.from_user.id
            username = message.reply_to_message.from_user.username
            dcid = message.reply_to_message.from_user.dc_id
        else:
            name = str(message.from_user.first_name\
                    + (message.from_user.last_name or ""))
            id = message.from_user.id
            username = message.from_user.username
            dcid = message.from_user.dc_id
    
    if not str(username) == "None":
        user_name = f"@{username}"
    else:
        user_name = "none"

    await message.reply_text(
        f"<b>Name</b> : {name}\n\n"
        f"<b>User ID</b> : <code>{id}</code>\n\n"
        f"<b>Username</b> : {user_name}\n\n"
        f"<b>Permanant USER link</b> : <a href='tg://user?id={id}'>Click here!</a>\n\n"
        f"<b>DC ID</b> : {dcid}\n\n",
        quote=True,
        parse_mode="html"
    )


@trojanz.on_message((filters.private | filters.group) & filters.command('status'))
async def bot_status(client,message):
    if str(message.from_user.id) not in Config.AUTH_USERS:
        return

    chats, filters = await filter_stats()

    if Config.SAVE_USER == "yes":
        users = await all_users()
        userstats = f"> __**{users} users have interacted with your bot!**__\n\n"
    else:
        userstats = ""

    if Config.HEROKU_API_KEY:
        try:
            server = heroku3.from_key(Config.HEROKU_API_KEY)

            user_agent = (
                'Mozilla/5.0 (Linux; Android 10; SM-G975F) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/80.0.3987.149 Mobile Safari/537.36'
            )
            accountid = server.account().id
            headers = {
            'User-Agent': user_agent,
            'Authorization': f'Bearer {Config.HEROKU_API_KEY}',
            'Accept': 'application/vnd.heroku+json; version=3.account-quotas',
            }

            path = "/accounts/" + accountid + "/actions/get-quota"

            request = requests.get("https://api.heroku.com" + path, headers=headers)

            if request.status_code == 200:
                result = request.json()

                total_quota = result['account_quota']
                quota_used = result['quota_used']

                quota_left = total_quota - quota_used
                
                total = math.floor(total_quota/3600)
                used = math.floor(quota_used/3600)
                hours = math.floor(quota_left/3600)
                minutes = math.floor(quota_left/60 % 60)
                days = math.floor(hours/24)

                usedperc = math.floor(quota_used / total_quota * 100)
                leftperc = math.floor(quota_left / total_quota * 100)

                quota_details = f"""

**Heroku Account Status**

> __You have **{total} hours** of free dyno quota available each month.__

> __Dyno hours used this month__ ;
        - **{used} hours**  ( {usedperc}% )

> __Dyno hours remaining this month__ ;
        - **{hours} hours**  ( {leftperc}% )
        - **Approximately {days} days!**


"""
            else:
                quota_details = ""
        except:
            print("Check your Heroku API key")
            quota_details = ""
    else:
        quota_details = ""

    uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - Config.BOT_START_TIME))

    try:
        t, u, f = shutil.disk_usage(".")
        total = humanbytes(t)
        used = humanbytes(u)
        free = humanbytes(f)

        disk = "\n**Disk Details**\n\n" \
            f"> USED  :  {used} / {total}\n" \
            f"> FREE  :  {free}\n\n"
    except:
        disk = ""

    await message.reply_photo(
        photo=f"{random.choice(PHOTO)}",
        caption=f"**Current status of your bot!**\n\n"
        f"> __**{filters}** filters across **{chats}** chats__\n\n"
        f"{userstats}"
        f"> __BOT Uptime__ : **{uptime}**\n\n"
        f"{quota_details}"
        f"{disk}",
        quote=True,
        parse_mode="md"
    )


@trojanz.on_message(filters.command('start') & filters.private)
async def start(client, message):
    fmsg = await message.reply_photo(
            'https://telegra.ph/file/b0575fdffea6adde272e1.jpg',
        text=Script.START_MSG.format(message.from_user.mention),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('❤‍🔥 Group ❤‍🔥', url="https://t.me/+jDYSx5O_geQ1ZThl")
                ]
            ]
        ),
        reply_to_message_id=message.message_id
    )
   
    await asyncio.sleep(30)
    await fmsg.delete()
    await message.delete()

    if Config.SAVE_USER == "yes":
        try:
            await add_user(
                str(message.from_user.id),
                str(message.from_user.username),
                str(message.from_user.first_name + " " + (message.from_user.last_name or "")),
                str(message.from_user.dc_id)
            )
        except:
            pass


@trojanz.on_message(filters.command('help') & filters.private)
async def help(client, message):
     fmsg = await message.reply_photo(
            'https://telegra.ph/file/b0575fdffea6adde272e1.jpg',
        text=Script.HELP_MSG.format(message.from_user.mention),
        disable_web_page_preview=True,
        reply_markup=InlinexKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Onwer", url="https://t.me/Shiva_TG"),
                    InlineKeyboardButton("About", callback_data="about_data")
                ],
                [
                    InlineKeyboardButton("Channel", url="https://t.me/MovieHubOtt"),
                    InlineKeyboardButton("Group", url="https://t.me/+jDYSx5O_geQ1ZThl")
                ]
            ]
        ),
        reply_to_message_id=message.message_id
    )

    await asyncio.sleep(30)
    await fmsg.delete()
    await message.delete()

@trojanz.on_message(filters.command('about') & filters.private)
async def about(client, message):
    await message.reply_text(
        text=Script.ABOUT_MSG,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Join", url="https://t.me/MovieHubOtt")
                ],
                [
                    InlineKeyboardButton("Back", callback_data="help_data"),
                    InlineKeyboardButton("Close", callback_data="close_data"),
                ]                
            ]
        ),
        reply_to_message_id=message.message_id
    )
