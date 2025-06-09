from pyrogram import filters
from devgagan import app
from config import OWNER_ID
from devgagan.core.func import subscribe
import asyncio
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import BotCommand

@app.on_message(filters.command("set") & filters.user(OWNER_ID))
async def set_commands(_, message):
    try:
        await app.set_bot_commands([
            BotCommand("start", "Initiate bot interaction"),
            BotCommand("batch", "Extract posts in bulk"),
            BotCommand("login", "Access private channels"),
            BotCommand("logout", "End bot session"),
            BotCommand("token", "Gain 3-hour free access"),
            BotCommand("adl", "Download audio from sites"),
            BotCommand("dl", "Download videos from sites"),
            BotCommand("freez", "Clear expired users"),
            BotCommand("pay", "Purchase subscription"),
            BotCommand("status", "Check payment status"),
            BotCommand("transfer", "Gift premium access"),
            BotCommand("myplan", "View plan details"),
            BotCommand("add", "Grant premium to user"),
            BotCommand("rem", "Revoke premium from user"),
            BotCommand("session", "Create Pyrogram V2 session"),
            BotCommand("settings", "Customize bot options"),
            BotCommand("stats", "Display bot statistics"),
            BotCommand("plan", "Explore premium plans"),
            BotCommand("terms", "Read terms and conditions"),
            BotCommand("speedtest", "Test server speed"),
            BotCommand("lock", "Secure channel extraction"),
            BotCommand("gcast", "Broadcast to users"),
            BotCommand("help", "Show command guide"),
            BotCommand("cancel", "Stop batch process")
        ])
        await message.reply("✅ Commands set successfully!")
    except Exception as e:
        await message.reply(f"❌ Error setting commands: {str(e)}")

help_pages = [
    (
        "✨ **Command Guide (1/2)** ✨\n\n"
        "🔹 **/start** - Initiate bot interaction\n"
        "🔹 **/batch** - Extract posts in bulk\n"
        "🔹 **/login** - Access private channels\n"
        "🔹 **/logout** - End bot session\n"
        "🔹 **/token** - Gain 3-hour free access\n"
        "🔹 **/adl** - Download audio from sites (v3 unavailable)\n"
        "🔹 **/dl** - Download videos from sites (v3 unavailable)\n"
        "🔹 **/freez** - Clear expired users (Owner only)\n"
        "🔹 **/pay** - Purchase subscription\n"
        "🔹 **/status** - Check payment status\n"
        "🔹 **/transfer** - Gift premium access (Premium only)\n"
        "🔹 **/myplan** - View plan details\n"
    ),
    (
        "✨ **Command Guide (2/2)** ✨\n\n"
        "🔹 **/add** - Grant premium to user (Owner only)\n"
        "🔹 **/rem** - Revoke premium from user (Owner only)\n"
        "🔹 **/session** - Create Pyrogram V2 session\n"
        "🔹 **/settings** - Customize bot options\n"
        "🔹 **/stats** - Display bot statistics\n"
        "🔹 **/plan** - Explore premium plans\n"
        "🔹 **/terms** - Read terms and conditions\n"
        "🔹 **/speedtest** - Test server speed (v3 unavailable)\n"
        "🔹 **/lock** - Secure channel extraction (Owner only)\n"
        "🔹 **/gcast** - Broadcast to users (Owner only)\n"
        "🔹 **/help** - Show command guide\n"
        "🔹 **/cancel** - Stop batch process\n"
        "\n**Powered by Team SPY**"
    )
]

async def send_or_edit_help_page(client, message, page_number):
    if page_number < 0 or page_number >= len(help_pages):
        await message.reply("❌ Invalid page number.")
        return

    prev_button = InlineKeyboardButton("⬅️ Prev", callback_data=f"help_prev_{page_number}")
    next_button = InlineKeyboardButton("Next ➡️", callback_data=f"help_next_{page_number}")

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
            "🔸 Users are solely responsible for their actions; we do not endorse copyrighted content.\n"
            "🔸 Plan purchase does not guarantee uptime or validity; user authorization is at our discretion.\n"
            "🔸 Payment does not ensure /batch command access; authorization decisions are final.\n"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Plans", callback_data="see_plan")],
            [InlineKeyboardButton("💬 Contact", url="https://t.me/kingofpatal")]
        ])
        await message.reply_text(terms_text, reply_markup=buttons)
    except Exception as e:
        await message.reply(f"❌ Error displaying terms: {str(e)}")

@app.on_message(filters.command("plan") & filters.private)
async def plan_command(client, message):
    try:
        plan_text = (
            "💰 **Premium Plans** 💰\n\n"
            "🔸 **Price**: From $2 or 200 INR via Amazon Gift Card (terms apply).\n"
            "🔸 **Download Limit**: Up to 100,000 files per batch command.\n"
            "🔸 **Batch Modes**: Access /bulk and /batch; wait for process completion before new actions.\n"
            "🔸 **Details**: Use /terms for full terms and conditions.\n"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 Terms", callback_data="see_terms")],
            [InlineKeyboardButton("💬 Contact", url="https://t.me/kingofpatal")]
        ])
        await message.reply_text(plan_text, reply_markup=buttons)
    except Exception as e:
        await message.reply(f"❌ Error displaying plan: {str(e)}")

@app.on_callback_query(filters.regex("see_plan"))
async def see_plan_callback(client, callback_query):
    try:
        plan_text = (
            "💰 **Premium Plans** 💰\n\n"
            "🔸 **Price**: From $2 or 200 INR via Amazon Gift Card (terms apply).\n"
            "🔸 **Download Limit**: Up to 100,000 files per batch command.\n"
            "🔸 **Batch Modes**: Access /bulk and /batch; wait for process completion before new actions.\n"
            "🔸 **Details**: Use /terms or click 'Terms' below for full conditions.\n"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 Terms", callback_data="see_terms")],
            [InlineKeyboardButton("💬 Contact", url="https://t.me/kingofpatal")]
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
            "🔸 Users are solely responsible for their actions; we do not endorse copyrighted content.\n"
            "🔸 Plan purchase does not guarantee uptime or validity; user authorization is at our discretion.\n"
            "🔸 Payment does not ensure /batch command access; authorization decisions are final.\n"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Plans", callback_data="see_plan")],
            [InlineKeyboardButton("💬 Contact", url="https://t.me/kingofpatal")]
        ])
        await callback_query.message.edit_text(terms_text, reply_markup=buttons)
        await callback_query.answer()
    except Exception as e:
        await callback_query.message.reply(f"❌ Error displaying terms: {str(e)}")
        await callback_query.answer()
