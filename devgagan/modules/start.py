from pyrogram import filters
from devgagan import app
from config import OWNER_ID
from devgagan.core.func import subscribe
import asyncio
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

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
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        else:
            await message.reply(
                help_pages[page_number],
                reply_markup=keyboard,
                disable_web_page_preview=True
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
        if await subscribe(client, message) == 1:
            return
        terms_text = (
            "📜 **Terms and Conditions** 📜\n\n"
            "🔸 Users are solely responsible for their actions; we do not endorse copyrighted content.\n"
            "🔸 Plan purchase does not guarantee uptime or validity; user authorization is at our discretion.\n"
            "🔸 Payment does not ensure /batch command access; authorization decisions are final.\n"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Plans", callback_data="see_plan")],
            [InlineKeyboardButton("💬 Contact", url="https://t.me/ISmartCoder")]
        ])
        await message.reply_text(terms_text, reply_markup=buttons, disable_web_page_preview=True)
    except Exception as e:
        await message.reply(f"❌ Error displaying terms: {str(e)}")

@app.on_message(filters.command("plan") & filters.private)
async def plan_command(client, message):
    try:
        if await subscribe(client, message) == 1:
            return
        plan_text = (
            "💰 **Premium Plans** 💰\n\n"
            "🔸 **Price**: From $2 or 200 INR via Amazon Gift Card (terms apply).\n"
            "🔸 **Download Limit**: Up to 100,000 files per batch command.\n"
            "🔸 **Batch Modes**: Access /bulk and /batch; wait for process completion before new actions.\n"
            "🔸 **Details**: Use /terms for full terms and conditions.\n"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 Terms", callback_data="see_terms")],
            [InlineKeyboardButton("💬 Contact", url="https://t.me/ISmartCoder")]
        ])
        await message.reply_text(plan_text, reply_markup=buttons, disable_web_page_preview=True)
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
            [InlineKeyboardButton("💬 Contact", url="https://t.me/ISmartCoder")]
        ])
        await callback_query.message.edit_text(plan_text, reply_markup=buttons, disable_web_page_preview=True)
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
            [InlineKeyboardButton("💬 Contact", url="https://t.me/ISmartCoder")]
        ])
        await callback_query.message.edit_text(terms_text, reply_markup=buttons, disable_web_page_preview=True)
        await callback_query.answer()
    except Exception as e:
        await callback_query.message.reply(f"❌ Error displaying terms: {str(e)}")
        await callback_query.answer()
