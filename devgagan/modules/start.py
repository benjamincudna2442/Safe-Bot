from pyrogram import filters
from devgagan import app
from config import OWNER_ID
from devgagan.core.func import subscribe
import asyncio
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.raw.functions.bots import SetBotInfo
from pyrogram.raw.types import InputUserSelf
from pyrogram.types import BotCommand

@app.on_message(filters.command("set") & filters.user(OWNER_ID))
async def set_commands(_, message):
    try:
        await app.set_bot_commands([
            BotCommand("start", "🚀 Start the bot"),
            BotCommand("batch", "🫠 Extract in bulk"),
            BotCommand("login", "🔑 Get into the bot"),
            BotCommand("logout", "🚪 Get out of the bot"),
            BotCommand("token", "🎲 Get 3 hours free access"),
            BotCommand("adl", "👻 Download audio from 30+ sites"),
            BotCommand("dl", "💀 Download videos from 30+ sites"),
            BotCommand("freez", "🧊 Remove all expired users"),
            BotCommand("pay", "₹ Pay now to get subscription"),
            BotCommand("status", "⟳ Refresh Payment status"),
            BotCommand("transfer", "💘 Gift premium to others"),
            BotCommand("myplan", "⌛ Get your plan details"),
            BotCommand("add", "➕ Add user to premium"),
            BotCommand("rem", "➖ Remove from premium"),
            BotCommand("session", "🧵 Generate Pyrogramv2 session"),
            BotCommand("settings", "⚙️ Personalize things"),
            BotCommand("stats", "📊 Get stats of the bot"),
            BotCommand("plan", "🗓️ Check our premium plans"),
            BotCommand("terms", "🥺 Terms and conditions"),
            BotCommand("speedtest", "🚅 Speed of server"),
            BotCommand("lock", "🔒 Protect channel from extraction"),
            BotCommand("gcast", "⚡ Broadcast message to bot users"),
            BotCommand("help", "❓ If you're a noob, still!"),
            BotCommand("cancel", "🚫 Cancel batch process")
        ])
        await message.reply("✅ Commands configured successfully!")
    except Exception as e:
        await message.reply(f"❌ Error setting commands: {str(e)}")

help_pages = [
    (
        "📝 **Bot Commands Overview (1/2)**:\n\n"
        "1. **/add userID**\n"
        "> Add user to premium (Owner only)\n\n"
        "2. **/rem userID**\n"
        "> Remove user from premium (Owner only)\n\n"
        "3. **/transfer userID**\n"
        "> Transfer premium to another user (Premium members only)\n\n"
        "4. **/get**\n"
        "> Get all user IDs (Owner only)\n\n"
        "5. **/lock**\n"
        "> Lock channel from extraction (Owner only)\n\n"
        "6. **/dl link**\n"
        "> Download videos (Not available in v3)\n\n"
        "7. **/adl link**\n"
        "> Download audio (Not available in v3)\n\n"
        "8. **/login**\n"
        "> Log into the bot for private channel access\n\n"
        "9. **/batch**\n"
        "> Bulk extraction for posts (After login)\n\n"
    ),
    (
        "📝 **Bot Commands Overview (2/2)**:\n\n"
        "10. **/logout**\n"
        "> Logout from the bot\n\n"
        "11. **/stats**\n"
        "> Get bot stats\n\n"
        "12. **/plan**\n"
        "> Check premium plans\n\n"
        "13. **/speedtest**\n"
        "> Test the server speed (Not available in v3)\n\n"
        "14. **/terms**\n"
        "> Terms and conditions\n\n"
        "15. **/cancel**\n"
        "> Cancel ongoing batch process\n\n"
        "16. **/myplan**\n"
        "> Get details about your plans\n\n"
        "17. **/session**\n"
        "> Generate Pyrogram V2 session\n\n"
        "18. **/settings**\n"
        "> 1. SETCHATID: Directly upload to a channel, group, or user's DM using -100[chatID]\n"
        "> 2. SETRENAME: Add custom rename tag or username for your channels\n"
        "> 3. CAPTION: Add custom caption\n"
        "> 4. REPLACEWORDS: Replace specified words in content\n"
        "> 5. RESET: Restore default settings\n\n"
        "> Additional settings: Set CUSTOM THUMBNAIL, PDF WATERMARK, VIDEO WATERMARK, SESSION-based login, etc.\n\n"
        "**Powered by Team SPY**"
    )
]

async def send_or_edit_help_page(client, message, page_number):
    if page_number < 0 or page_number >= len(help_pages):
        await message.reply("❌ Invalid page number.")
        return

    prev_button = InlineKeyboardButton("◀️ Previous", callback_data=f"help_prev_{page_number}")
    next_button = InlineKeyboardButton("Next ▶️", callback_data=f"help_next_{page_number}")

    buttons = []
    if page_number > 0:
        buttons.append(prev_button)
    if page_number < len(help_pages) - 1:
        buttons.append(next_button)

    keyboard = InlineKeyboardMarkup([buttons])

    try:
        if isinstance(message, CallbackQuery):
            await message.message.edit_text(
                help_pages[page_number],
                reply_markup=keyboard
            )
        else:
            await message.reply(
                help_pages[page_number],
                reply_markup=keyboard
            )
    except Exception as e:
        await message.reply(f"❌ Error displaying help page: {str(e)}")

@app.on_message(filters.command("help") & filters.private)
async def help_command(client, message):
    if await subscribe(client, message) == 1:
        return
    await send_or_edit_help_page(client, message, 0)

@app.on_callback_query(filters.regex(r"help_(prev|next)_(\d+)"))
async def on_help_navigation(client, callback_query):
    try:
        action, page_number = callback_query.data.split("_")[1], int(callback_query.data.split("_")[2])
        page_number = page_number - 1 if action == "prev" else page_number + 1
        await send_or_edit_help_page(client, callback_query, page_number)
        await callback_query.answer()
    except Exception as e:
        await callback_query.message.reply(f"❌ Error navigating help: {str(e)}")
        await callback_query.answer()

@app.on_message(filters.command("terms") & filters.private)
async def terms_command(client, message):
    try:
        terms_text = (
            "📜 **Terms and Conditions** 📜\n\n"
            "✨ We are not responsible for user actions and do not promote copyrighted content. Users are solely responsible for their activities.\n"
            "✨ Purchasing a plan does not guarantee uptime, downtime, or plan validity. Authorization and banning of users are at our discretion.\n"
            "✨ Payment does not guarantee authorization for the /batch command. All authorization decisions are made at our discretion.\n"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 See Plans", callback_data="see_plan")],
            [InlineKeyboardButton("💬 Contact Now", url="https://t.me/kingofpatal")]
        ])
        await message.reply_text(terms_text, reply_markup=buttons)
    except Exception as e:
        await message.reply(f"❌ Error displaying terms: {str(e)}")

@app.on_message(filters.command("plan") & filters.private)
async def plan_command(client, message):
    try:
        plan_text = (
            "💰 **Premium Price**:\n\n Starting from $2 or 200 INR via **Amazon Gift Card** (terms and conditions apply).\n"
            "📥 **Download Limit**: Up to 100,000 files in a single batch command.\n"
            "🛑 **Batch**: Includes /bulk and /batch modes.\n"
            "   - Wait for the process to cancel automatically before proceeding with downloads or uploads.\n\n"
            "📜 **Terms and Conditions**: Send /terms for details.\n"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 See Terms", callback_data="see_terms")],
            [InlineKeyboardButton("💬 Contact Now", url="https://t.me/kingofpatal")]
        ])
        await message.reply_text(plan_text, reply_markup=buttons)
    except Exception as e:
        await message.reply(f"❌ The error is: {str(e)}")

@app.on_callback_query(filters.regex("see_plan"))
async def see_plan_callback(client, callback_query):
    try:
        plan_text = (
            "💰 **Premium Price**:\n\n Starting from $2 or 200 INR via **Amazon Gift Card** (terms and conditions apply).\n"
            "📥 **Download Limit**: Up to 100,000 files in a single batch command.\n"
            "🛑 **Batch**: Includes /bulk and /batch modes.\n"
            "   - Wait for the process to cancel automatically before proceeding with downloads or uploads.\n\n"
            "📜 **Terms and Conditions**: Send /terms or click 'See Terms' below for details.\n"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 See Terms", callback_data="see_terms")],
            [InlineKeyboardButton("💬 Contact Now", url="https://t.me/kingofpatal")]
        ])
        await callback_query.message.edit_text(plan_text, reply_markup=buttons)
        await callback_query.answer()
    except Exception as e:
        await callback_query.message.reply(f"❌ Error displaying plan: {str(e)}")
        await callback_query.answer()

@app.on_callback_query(filters.regex("see_terms"))
async def see_terms_callback(client, callback_query):
    try:
        terms_text = (
            "📜 **Terms and Conditions** 📜\n\n"
            "✨ We are not responsible for user actions and do not promote copyrighted content. Users are solely responsible for their activities.\n"
            "✨ Purchasing a plan does not guarantee uptime, downtime, or plan validity. Authorization and banning of users are at our discretion.\n"
            "✨ Payment does not guarantee authorization for the /batch command. All authorization decisions are made at our discretion.\n"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 See Plans", callback_data="see_plan")],
            [InlineKeyboardButton("💬 Contact Now", url="https://t.me/kingofpatal")]
        ])
        await callback_query.message.edit_text(terms_text, reply_markup=buttons)
        await callback_query.answer()
    except Exception as e:
        await callback_query.message.reply(f"❌ Error displaying terms: {str(e)}")
        await callback_query.answer()
