from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode
import random
import string
from devgagan import app
from devgagan.core.func import *
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB, LOG_GROUP

tclient = AsyncIOMotorClient(MONGO_DB)
tdb = tclient["telegram_bot"]
token = tdb["tokens"]

async def create_ttl_index():
    await token.create_index("expires_at", expireAfterSeconds=0)

Param = {}

async def generate_random_param(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def get_shortened_url(deep_link):
    return deep_link

async def is_user_verified(user_id):
    session = await token.find_one({"user_id": user_id})
    return session is not None

@app.on_message(filters.command("start"))
async def token_handler(client, message):
    join = await subscribe(client, message)
    if join == 1:
        return
    chat_id = "TheSmartDev"
    msg = await app.get_messages(chat_id, 2595)
    user_id = message.chat.id
    user = await app.get_users(user_id)
    fullname = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
    if len(message.command) <= 1:
        buttons = [
            [
                InlineKeyboardButton("Update Channel", url="https://t.me/TheSmartDev"),
                InlineKeyboardButton("Source Repo", url="https://github.com/abirxdhack/RestrictedContentDL")
            ],
            [
                InlineKeyboardButton("Help Menu", b"help"),
                InlineKeyboardButton("Close Menu", b"close")
            ]
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        if msg.photo:
            await message.reply_photo(
                msg.photo.file_id,
                caption=(
                    f"**Hi {fullname}! Welcome To This Bot**\n"
                    "**━━━━━━━━━━━━━━━━━━━━━━**\n"
                    "**RestrictedDL ⚙️:** The ultimate toolkit on Telegram, offering Downloading Any Type Of Resticted Content From Both Public & Private Source!\n"
                    "**━━━━━━━━━━━━━━━━━━━━━━**\n"
                    "**Don't Forget To [Join Here](https://t.me/TheSmartDev) For Updates!**"
                ),
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await message.reply(
                f"**Hi {fullname}! Welcome To This Bot**\n"
                "**━━━━━━━━━━━━━━━━━━━━━━**\n"
                "**RestrictedDL ⚙️:** The ultimate toolkit on Telegram, offering Downloading Any Type Of Resticted Content From Both Public & Private Source!\n"
                "**━━━━━━━━━━━━━━━━━━━━━━**\n"
                "**Don't Forget To [Join Here](https://t.me/TheSmartDev) For Updates!**",
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
        return

    param = message.command[1] if len(message.command) > 1 else None
    freecheck = await chk_user(message, user_id)
    if freecheck != 1:
        await message.reply("You are a premium user no need of token 😉")
        return

    if param:
        if user_id in Param and Param[user_id] == param:
            await token.insert_one({
                "user_id": user_id,
                "param": param,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=3),
            })
            del Param[user_id]
            await message.reply("✅ You have been verified successfully! Enjoy your session for next 3 hours.")
            return
        else:
            await message.reply("❌ Invalid or expired verification link. Please generate a new token.")
            return

@app.on_message(filters.command("token"))
async def smart_handler(client, message):
    user_id = message.chat.id
    freecheck = await chk_user(message, user_id)
    if freecheck != 1:
        await message.reply("You are a premium user no need of token 😉")
        return
    if await is_user_verified(user_id):
        await message.reply("✅ Your free session is already active enjoy!")
    else:
        param = await generate_random_param()
        Param[user_id] = param
        deep_link = f"https://t.me/{client.me.username}?start={param}"
        shortened_url = await get_shortened_url(deep_link)
        if not shortened_url:
            await message.reply("❌ Failed to generate the token link. Please try again.")
            return
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Verify the token now...", url=shortened_url)]]
        )
        await message.reply("Click the button below to verify your free access token: \n\n> What will you get ? \n1. No time bound upto 3 hours \n2. Batch command limit will be FreeLimit + 20 \n3. All functions unlocked", reply_markup=button)

@app.on_callback_query(filters.regex(b"help"))
async def help_callback(client, callback_query):
    user_id = callback_query.from_user.id
    chat_id = "TheSmartDev"
    msg = await app.get_messages(chat_id, 2595)
    buttons = [[InlineKeyboardButton("Back", b"back")]]
    keyboard = InlineKeyboardMarkup(buttons)
    help_text = (
        "**📝 Bot Commands Overview:**\n\n"
        "1. **/add userID** - Add user to premium (Owner only)\n"
        "2. **/rem userID** - Remove user from premium (Owner only)\n"
        "3. **/transfer userID** - Transfer premium to another user (Premium only)\n"
        "4. **/get** - Get all user IDs (Owner only)\n"
        "5. **/lock** - Lock channel from extraction (Owner only)\n"
        "6. **/dl link** - Download videos\n"
        "7. **/adl link** - Download audio\n"
        "8. **/login** - Log in for private channel access\n"
        "9. **/batch** - Bulk extraction for posts (After login)\n"
        "10. **/logout** - Log out from the bot\n"
        "11. **/stats** - Get bot stats\n"
        "12. **/plan** - Check premium plans\n"
        "13. **/speedtest** - Test server speed\n"
        "14. **/terms** - Terms and conditions\n"
        "15. **/cancel** - Cancel ongoing batch process\n"
        "16. **/myplan** - Get details about your plans\n"
        "17. **/session** - Generate Pyrogram V2 session\n"
        "18. **/settings** - Configure settings (chat ID, rename, caption, etc.)\n"
        "19. **/tera** or **/terabox link** - Download from TeraBox\n"
        "20. **/activate** - Activate downloader for private chats (5 min)\n"
    )
    if msg.photo:
        await callback_query.message.edit_media(
            media=msg.photo,
            caption=help_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await callback_query.message.edit_text(
            help_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )

@app.on_callback_query(filters.regex(b"back"))
async def back_callback(client, callback_query):
    user_id = callback_query.from_user.id
    user = await app.get_users(user_id)
    fullname = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
    chat_id = "TheSmartDev"
    msg = await app.get_messages(chat_id, 2595)
    buttons = [
        [
            InlineKeyboardButton("Update Channel", url="https://t.me/TheSmartDev"),
            InlineKeyboardButton("Source Repo", url="https://github.com/abirxdhack/RestrictedContentDL")
        ],
        [
            InlineKeyboardButton("Help Menu", b"help"),
            InlineKeyboardButton("Close Menu", b"close")
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    if msg.photo:
        await callback_query.message.edit_media(
            media=msg.photo,
            caption=(
                f"**Hi {fullname}! Welcome To This Bot**\n"
                "**━━━━━━━━━━━━━━━━━━━━━━**\n"
                "**RestrictedDL ⚙️:** The ultimate toolkit on Telegram, offering Downloading Any Type Of Resticted Content From Both Public & Private Source!\n"
                "**━━━━━━━━━━━━━━━━━━━━━━**\n"
                "**Don't Forget To [Join Here](https://t.me/TheSmartDev) For Updates!**"
            ),
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await callback_query.message.edit_text(
            f"**Hi {fullname}! Welcome To This Bot**\n"
            "**━━━━━━━━━━━━━━━━━━━━━━**\n"
            "**RestrictedDL ⚙️:** The ultimate toolkit on Telegram, offering Downloading Any Type Of Resticted Content From Both Public & Private Source!\n"
            "**━━━━━━━━━━━━━━━━━━━━━━**\n"
            "**Don't Forget To [Join Here](https://t.me/TheSmartDev) For Updates!**",
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )

@app.on_callback_query(filters.regex(b"close"))
async def close_callback(client, callback_query):
    await callback_query.message.delete()
