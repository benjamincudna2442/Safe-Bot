from datetime import datetime, timedelta
import pytz
import asyncio
from devgagan import app
from config import OWNER_ID
from devgagan.core.func import get_seconds
from devgagan.core.mongo import plans_db
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.raw.functions.messages import SendMedia, SetBotPrecheckoutResults, SetBotShippingResults
from pyrogram.raw.types import (
    InputMediaInvoice,
    Invoice,
    DataJSON,
    LabeledPrice,
    UpdateBotPrecheckoutQuery,
    UpdateBotShippingQuery,
    UpdateNewMessage,
    MessageService,
    MessageActionPaymentSentMe,
    PeerUser,
    PeerChat,
    PeerChannel,
    ReplyInlineMarkup,
    KeyboardButtonRow,
    KeyboardButtonBuy
)
import uuid
import hashlib
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Shared Strings and Emojis
PLAN_OPTIONS_TEXT = """
💎 **Unlock Premium Plans for Restricted Content Downloads!** 💎
**✘ ━━━━━━━━━━━━━━━━━━ ✘**
🌟 **Why Choose Our Plans?** 🌟
Gain access to exclusive features for downloading restricted content from 30+ sites! 🚀
Highly customizable plans are available through the owner—contact for tailored options! ✨

👇 **Select a Plan to Unlock Premium Access:** 👀

🔥 **Plan Benefits** 🔥
- **Plan 1**: 1-day access for 5 Stars
- **Plan 2**: 7-day access for 150 Stars
- **Plan 3**: 30-day access for 250 Stars
- Download up to 100,000 files per batch! 📥
- Use /pay or /buy to start your subscription! 💸

**Unlock the Power of Premium Now!** 💥
"""

PAYMENT_SUCCESS_TEXT = """
**✅ Subscription Activated!**

🎉 Thank you **{0}** for subscribing to **Plan {1}** with **{2} Stars**! 
Your premium access to restricted content downloads is now active! 🚀

**🧾 Transaction ID:** `{3}`
"""

ADMIN_NOTIFICATION_TEXT = """
🌟 **New Premium Subscription!** 🌟
✨ **User:** {0}
⁉️ **User ID:** `{1}`
🌐 **Username:** {2}
💥 **Plan:** Plan {3} ({4} Stars)
📝 **Transaction ID:** `{5}`
"""

INVOICE_CREATION_TEXT = "Generating invoice for Plan {0} ({1} Stars)...\nPlease wait ⏳"
INVOICE_CONFIRMATION_TEXT = "**✅ Invoice for Plan {0} ({1} Stars) generated! Proceed to pay below.**"
DUPLICATE_INVOICE_TEXT = "**🚫 Subscription in Progress! Please complete or cancel the current payment.**"
INVALID_INPUT_TEXT = "**❌ Invalid Input! Use /pay or /buy to view plans.**"
INVOICE_FAILED_TEXT = "**❌ Invoice Creation Failed! Try Again or Contact Support.**"
PAYMENT_FAILED_TEXT = "**❌ Payment Declined! Contact Support for Assistance.**"

# Store active invoices to prevent duplicates (in-memory, replace with DB for production)
active_invoices = {}

@app.on_message(filters.command("rem") & filters.user(OWNER_ID))
async def remove_premium(client, message):
    try:
        if len(message.command) == 2:
            user_id = int(message.command[1])
            user = await client.get_users(user_id)
            data = await plans_db.check_premium(user_id)

            if data and data.get("_id"):
                await plans_db.remove_premium(user_id)
                await message.reply_text("✅ User removed from premium successfully!")
                await client.send_message(
                    chat_id=user_id,
                    text=f"👋 Hey {user.mention},\n\nYour premium access has been removed.\nThank you for using our service! 😊"
                )
            else:
                await message.reply_text("❌ User is not a premium member!")
        else:
            await message.reply_text("Usage: /rem user_id")
    except Exception as e:
        await message.reply_text(f"❌ Error removing premium: {str(e)}")

@app.on_message(filters.command("myplan") & filters.private)
async def myplan(client, message):
    try:
        user_id = message.from_user.id
        user = message.from_user.mention
        data = await plans_db.check_premium(user_id)
        if data and data.get("expire_date"):
            expiry = data.get("expire_date")
            expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
            expiry_str = expiry_ist.strftime("%d-%m-%Y\n⏱️ Expiry Time: %I:%M:%S %p")

            current_time = datetime.now(pytz.timezone("Asia/Kolkata"))
            time_left = expiry_ist - current_time

            days = time_left.days
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            time_left_str = f"{days} days, {hours} hours, {minutes} minutes"
            await message.reply_text(
                f"⚜️ **Premium Plan Details** ⚜️\n\n"
                f"👤 **User**: {user}\n"
                f"⚡ **User ID**: <code>{user_id}</code>\n"
                f"⏰ **Time Left**: {time_left_str}\n"
                f"⌛ **Expiry Date**: {expiry_str}"
            )
        else:
            await message.reply_text(f"👋 Hey {user},\n\nYou don't have an active premium plan.")
    except Exception as e:
        await message.reply_text(f"❌ Error checking plan: {str(e)}")

@app.on_message(filters.command("check") & filters.user(OWNER_ID))
async def check_premium(client, message):
    try:
        if len(message.command) == 2:
            user_id = int(message.command[1])
            user = await client.get_users(user_id)
            data = await plans_db.check_premium(user_id)
            if data and data.get("expire_date"):
                expiry = data.get("expire_date")
                expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
                expiry_str = expiry_ist.strftime("%d-%m-%Y\n⏱️ Expiry Time: %I:%M:%S %p")

                current_time = datetime.now(pytz.timezone("Asia/Kolkata"))
                time_left = expiry_ist - current_time

                days = time_left.days
                hours, remainder = divmod(time_left.seconds, 3600)
                minutes, _ = divmod(remainder, 60)

                time_left_str = f"{days} days, {hours} hours, {minutes} minutes"
                await message.reply_text(
                    f"⚜️ **Premium User Data** ⚜️\n\n"
                    f"👤 **User**: {user.mention}\n"
                    f"⚡ **User ID**: <code>{user_id}</code>\n"
                    f"⏰ **Time Left**: {time_left_str}\n"
                    f"⌛ **Expiry Date**: {expiry_str}"
                )
            else:
                await message.reply_text("❌ No premium data found for this user!")
        else:
            await message.reply_text("Usage: /check user_id")
    except Exception as e:
        await message.reply_text(f"❌ Error checking premium: {str(e)}")

@app.on_message(filters.command("add") & filters.user(OWNER_ID))
async def give_premium(client, message):
    try:
        if len(message.command) == 4:
            time_zone = datetime.now(pytz.timezone("Asia/Kolkata"))
            current_time = time_zone.strftime("%d-%m-%Y\n⏱️ Joining Time: %I:%M:%S %p")
            user_id = int(message.command[1])
            user = await client.get_users(user_id)
            time_input = message.command[2] + " " + message.command[3]
            seconds = await get_seconds(time_input)

            if seconds > 0:
                expiry_time = datetime.now() + timedelta(seconds=seconds)
                await plans_db.add_premium(user_id, expiry_time)
                data = await plans_db.check_premium(user_id)
                expiry = data.get("expire_date")
                expiry_str = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y\n⏱️ Expiry Time: %I:%M:%S %p")

                await message.reply_text(
                    f"✅ **Premium Added Successfully** ✅\n\n"
                    f"👤 **User**: {user.mention}\n"
                    f"⚡ **User ID**: <code>{user_id}</code>\n"
                    f"⏰ **Premium Duration**: <code>{time_input}</code>\n"
                    f"⏳ **Joining Date**: {current_time}\n"
                    f"⌛ **Expiry Date**: {expiry_str}\n\n"
                    f"**Powered by Team SPY** 🚀",
                    disable_web_page_preview=True
                )
                await client.send_message(
                    chat_id=user_id,
                    text=(
                        f"👋 **Hey {user.mention},**\n"
                        f"🎉 **Your Premium Plan is Active!**\n\n"
                        f"⏰ **Premium Duration**: <code>{time_input}</code>\n"
                        f"⏳ **Joining Date**: {current_time}\n"
                        f"⌛ **Expiry Date**: {expiry_str}\n\n"
                        f"**Enjoy Premium Features!** ✨"
                    ),
                    disable_web_page_preview=True
                )
            else:
                await message.reply_text("❌ Invalid time format. Use: '1 day', '1 hour', '1 min', '1 month', or '1 year'.")
        else:
            await message.reply_text("Usage: /add user_id time (e.g., '1 day', '1 hour', '1 min', '1 month', or '1 year')")
    except Exception as e:
        await message.reply_text(f"❌ Error adding premium: {str(e)}")

@app.on_message(filters.command("transfer") & filters.private)
async def transfer_premium(client, message):
    try:
        if len(message.command) == 2:
            new_user_id = int(message.command[1])
            sender_user_id = message.from_user.id
            sender_user = await client.get_users(sender_user_id)
            new_user = await client.get_users(new_user_id)

            data = await plans_db.check_premium(sender_user_id)
            if data and data.get("_id"):
                expiry = data.get("expire_date")
                await plans_db.remove_premium(sender_user_id)
                await plans_db.add_premium(new_user_id, expiry)

                expiry_str = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime(
                    "%d-%m-%Y\n⏱️ Expiry Time: %I:%M:%S %p"
                )
                current_time = datetime.now(pytz.timezone("Asia/Kolkata")).strftime(
                    "%d-%m-%Y\n⏱️ Transfer Time: %I:%M:%S %p"
                )

                await message.reply_text(
                    f"✅ **Premium Transferred Successfully!** ✅\n\n"
                    f"👤 **From**: {sender_user.mention}\n"
                    f"👤 **To**: {new_user.mention}\n"
                    f"⏳ **Expiry Date**: {expiry_str}\n\n"
                    f"**Powered by Team SPY** 🚀"
                )
                await client.send_message(
                    chat_id=new_user_id,
                    text=(
                        f"👋 **Hey {new_user.mention},**\n"
                        f"🎉 **Premium Plan Transferred!** 🎉\n"
                        f"🛡️ **Transferred From**: {sender_user.mention}\n\n"
                        f"⏳ **Expiry Date**: {expiry_str}\n"
                        f"📅 **Transferred On**: {current_time}\n\n"
                        f"**Enjoy Premium Features!** ✨"
                    )
                )
            else:
                await message.reply_text("⚠️ You are not a premium user! Only premium users can transfer plans.")
        else:
            await message.reply_text("Usage: /transfer user_id")
    except Exception as e:
        await message.reply_text(f"❌ Error transferring premium: {str(e)}")

async def premium_remover():
    try:
        all_users = await plans_db.premium_users()
        removed_users = []
        not_removed_users = []

        for user_id in all_users:
            try:
                user = await app.get_users(user_id)
                chk_time = await plans_db.check_premium(user_id)

                if chk_time and chk_time.get("expire_date"):
                    expiry_date = chk_time["expire_date"]

                    if expiry_date <= datetime.now():
                        name = user.first_name
                        await plans_db.remove_premium(user_id)
                        await app.send_message(user_id, text=f"👋 Hello {name}, your premium subscription has expired.")
                        logger.info(f"{name} ({user_id}) premium subscription expired.")
                        removed_users.append(f"{name} ({user_id})")
                    else:
                        name = user.first_name
                        current_time = datetime.now()
                        time_left = expiry_date - current_time

                        days = time_left.days
                        hours, remainder = divmod(time_left.seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)

                        if days > 0:
                            remaining_time = f"{days} days, {hours} hours, {minutes} minutes"
                        elif hours > 0:
                            remaining_time = f"{hours} hours, {minutes} minutes"
                        elif minutes > 0:
                            remaining_time = f"{minutes} minutes"
                        else:
                            remaining_time = f"{seconds} seconds"

                        logger.info(f"{name} ({user_id}) : Remaining Time: {remaining_time}")
                        not_removed_users.append(f"{name} ({user_id})")
            except Exception as e:
                await plans_db.remove_premium(user_id)
                logger.error(f"Unknown user {user_id} removed: {str(e)}")
                removed_users.append(f"Unknown ({user_id})")

        return removed_users, not_removed_users
    except Exception as e:
        logger.error(f"Error in premium_remover: {str(e)}")
        return [], []

@app.on_message(filters.command("freez") & filters.user(OWNER_ID))
async def refresh_users(client, message):
    try:
        removed_users, not_removed_users = await premium_remover()
        removed_text = "\n".join(removed_users) if removed_users else "No users removed."
        not_removed_text = "\n".join(not_removed_users) if not_removed_users else "No users with active premium."
        summary = (
            f"⚜️ **Premium Cleanup Summary** ⚜️\n\n"
            f"🗑️ **Removed Users**:\n{removed_text}\n\n"
            f"✅ **Active Users**:\n{not_removed_text}"
        )
        await message.reply(summary)
    except Exception as e:
        await message.reply(f"❌ Error refreshing users: {str(e)}")

@app.on_message(filters.command(["pay", "buy"]) & filters.private)
async def plan_command(client, message):
    try:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Plan 1 (5 Stars)", callback_data="plan_1"),
             InlineKeyboardButton("Plan 2 (150 Stars)", callback_data="plan_2")],
            [InlineKeyboardButton("Plan 3 (250 Stars)", callback_data="plan_3")],
            [InlineKeyboardButton("💬 Contact Owner", url="https://t.me/kingofpatal")]
        ])
        await client.send_message(
            chat_id=message.chat.id,
            text=(
                f"💎 **Choose Your Premium Plan** 💎\n\n"
                f"🌟 **Plan 1**: 1-day access for **5 Stars** ✨\n"
                f"🌟 **Plan 2**: 7-day access for **150 Stars** ✨\n"
                f"🌟 **Plan 3**: 30-day access for **250 Stars** ✨\n\n"
                f"🔥 **Features**:\n"
                f"- Download restricted content from 30+ sites\n"
                f"- Up to 100,000 files per batch command\n"
                f"- Access /bulk and /batch modes\n\n"
                f"📌 **Custom Plans**: Contact the owner for highly customizable plans!\n"
                f"📩 Use the buttons below to subscribe or contact the owner."
            ),
            reply_markup=reply_markup
        )
    except Exception as e:
        await message.reply(f"❌ Error displaying plans: {str(e)}")

async def generate_invoice(client, chat_id, user_id, plan_number, amount, duration_seconds):
    try:
        if active_invoices.get(user_id):
            await client.send_message(chat_id, DUPLICATE_INVOICE_TEXT)
            return

        back_button = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="show_plan_options")]])
        loading_message = await client.send_message(
            chat_id,
            INVOICE_CREATION_TEXT.format(plan_number, amount),
            reply_markup=back_button
        )

        active_invoices[user_id] = True
        timestamp = int(time.time())
        unique_id = str(uuid.uuid4())[:8]
        invoice_payload = f"plan_{plan_number}_{user_id}_{amount}_{timestamp}_{unique_id}"
        random_id = int(hashlib.sha256(invoice_payload.encode()).hexdigest(), 16) % (2**63)

        title = f"Premium Plan {plan_number}"
        description = f"Unlock {['1 day', '7 days', '30 days'][plan_number-1]} of premium access to download restricted content from 30+ sites! 🚀"
        currency = "XTR"

        invoice = Invoice(
            currency=currency,
            prices=[LabeledPrice(label=f"Plan {plan_number} ({amount} Stars)", amount=amount)],
            max_tip_amount=0,
            suggested_tip_amounts=[],
            recurring=False,
            test=False,
            name_requested=False,
            phone_requested=False,
            email_requested=False,
            shipping_address_requested=False,
            flexible=False
        )

        media = InputMediaInvoice(
            title=title,
            description=description,
            invoice=invoice,
            payload=invoice_payload.encode(),
            provider="STARS",
            provider_data=DataJSON(data="{}")
        )

        markup = ReplyInlineMarkup(
            rows=[
                KeyboardButtonRow(
                    buttons=[
                        KeyboardButtonBuy(text=f"💸 Buy Plan {plan_number}")
                    ]
                )
            ]
        )

        peer = await client.resolve_peer(chat_id)
        await client.invoke(
            SendMedia(
                peer=peer,
                media=media,
                message="",
                random_id=random_id,
                reply_markup=markup
            )
        )

        await client.edit_message_text(
            chat_id,
            loading_message.id,
            INVOICE_CONFIRMATION_TEXT.format(plan_number, amount),
            reply_markup=back_button
        )
        logger.info(f"✅ Invoice sent for Plan {plan_number} ({amount} Stars) to user {user_id}")
    except Exception as e:
        logger.error(f"❌ Failed to generate invoice for user {user_id}: {str(e)}")
        await client.edit_message_text(
            chat_id,
            loading_message.id,
            INVOICE_FAILED_TEXT,
            reply_markup=back_button
        )
    finally:
        active_invoices.pop(user_id, None)

@app.on_callback_query(filters.regex(r"^(plan_\d+|show_plan_options)$"))
async def handle_plan_callback(client, callback_query):
    try:
        data = callback_query.data
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id

        if data == "show_plan_options":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Plan 1 (5 Stars)", callback_data="plan_1"),
                 InlineKeyboardButton("Plan 2 (150 Stars)", callback_data="plan_2")],
                [InlineKeyboardButton("Plan 3 (250 Stars)", callback_data="plan_3")],
                [InlineKeyboardButton("💬 Contact Owner", url="https://t.me/kingofpatal")]
            ])
            await client.edit_message_text(
                chat_id,
                callback_query.message.id,
                (
                    f"💎 **Choose Your Premium Plan** 💎\n\n"
                    f"🌟 **Plan 1**: 1-day access for **5 Stars** ✨\n"
                    f"🌟 **Plan 2**: 7-day access for **150 Stars** ✨\n"
                    f"🌟 **Plan 3**: 30-day access for **250 Stars** ✨\n\n"
                    f"🔥 **Features**:\n"
                    f"- Download restricted content from 30+ sites\n"
                    f"- Up to 100,000 files per batch command\n"
                    f"- Access /bulk and /batch modes\n\n"
                    f"📌 **Custom Plans**: Contact the owner for highly customizable plans!\n"
                    f"📩 Use the buttons below to subscribe or contact the owner."
                ),
                reply_markup=reply_markup
            )
            await callback_query.answer()
        elif data.startswith("plan_"):
            plan_number = int(data.split("_")[1])
            plans = [
                {"amount": 5, "duration": 1 * 24 * 60 * 60},  # 1 day
                {"amount": 150, "duration": 7 * 24 * 60 * 60},  # 7 days
                {"amount": 250, "duration": 30 * 24 * 60 * 60}  # 30 days
            ]
            plan = plans[plan_number - 1]
            await generate_invoice(client, chat_id, user_id, plan_number, plan["amount"], plan["duration"])
            await callback_query.answer(f"✅ Invoice Generated for Plan {plan_number}!")
    except Exception as e:
        await callback_query.message.reply(f"❌ Error processing plan: {str(e)}")
        await callback_query.answer()

@app.on_raw_update()
async def raw_update_handler(client, update, users, chats):
    try:
        if isinstance(update, UpdateBotPrecheckoutQuery):
            await client.invoke(
                SetBotPrecheckoutResults(
                    query_id=update.query_id,
                    success=True
                )
            )
            logger.info(f"✅ Pre-checkout query {update.query_id} OK for user {update.user_id}")
        elif isinstance(update, UpdateBotShippingQuery):
            await client.invoke(
                SetBotShippingResults(
                    query_id=update.query_id,
                    shipping_options=[]
                )
            )
            logger.info(f"✅ Shipping query {update.query_id} OK for user {update.user_id}")
        elif isinstance(update, UpdateNewMessage) and isinstance(update.message, MessageService) and isinstance(update.message.action, MessageActionPaymentSentMe):
            payment = update.message.action
            user_id = update.message.from_id.user_id if update.message.from_id and hasattr(update.message.from_id, 'user_id') else None
            if not user_id and users:
                possible_user_ids = [uid for uid in users if uid > 0]
                user_id = possible_user_ids[0] if possible_user_ids else None

            if isinstance(update.message.peer_id, PeerUser):
                chat_id = update.message.peer_id.user_id
            elif isinstance(update.message.peer_id, PeerChat):
                chat_id = update.message.peer_id.chat_id
            elif isinstance(update.message.peer_id, PeerChannel):
                chat_id = update.message.peer_id.channel_id
            else:
                chat_id = user_id

            if not user_id or not chat_id:
                raise ValueError(f"Invalid chat_id ({chat_id}) or user_id ({user_id})")

            user = users.get(user_id)
            full_name = f"{user.first_name} {getattr(user, 'last_name', '')}".strip() or "Unknown" if user else "Unknown"
            username = f"@{user.username}" if user and user.username else "@N/A"

            plan_number = int(payment.payload.decode().split("_")[1])
            plans = [
                {"amount": 5, "duration": 1 * 24 * 60 * 60},  # 1 day
                {"amount": 150, "duration": 7 * 24 * 60 * 60},  # 7 days
                {"amount": 250, "duration": 30 * 24 * 60 * 60}  # 30 days
            ]
            plan = plans[plan_number - 1]

            expiry_time = datetime.now() + timedelta(seconds=plan["duration"])
            await plans_db.add_premium(user_id, expiry_time)

            await client.send_message(
                chat_id=chat_id,
                text=PAYMENT_SUCCESS_TEXT.format(full_name, plan_number, payment.total_amount, payment.charge.id)
            )

            expiry_str = expiry_time.astimezone(pytz.timezone("Asia/Kolkata")).strftime(
                "%d-%m-%Y\n⏱️ Expiry Time: %I:%M:%S %p"
            )
            current_time = datetime.now(pytz.timezone("Asia/Kolkata")).strftime(
                "%d-%m-%Y\n⏱️ Joining Time: %I:%M:%S %p"
            )
            await client.send_message(
                chat_id=user_id,
                text=(
                    f"👋 **Hey {full_name},**\n"
                    f"🎉 **Your Plan {plan_number} is Active!** 🎉\n\n"
                    f"⏰ **Premium Duration**: {['1 day', '7 days', '30 days'][plan_number-1]}\n"
                    f"⏳ **Joining Date**: {current_time}\n"
                    f"⌛ **Expiry Date**: {expiry_str}\n\n"
                    f"**Enjoy Premium Features!** ✨"
                )
            )

            admin_text = ADMIN_NOTIFICATION_TEXT.format(full_name, user_id, username, plan_number, payment.total_amount, payment.charge.id)
            for admin_id in OWNER_ID:
                try:
                    await client.send_message(
                        chat_id=admin_id,
                        text=admin_text
                    )
                except Exception as e:
                    logger.error(f"❌ Failed to notify admin {admin_id}: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Payment processing failed for user {user_id if user_id else 'unknown'}: {str(e)}")
        if 'chat_id' in locals() and chat_id:
            await client.send_message(
                chat_id=chat_id,
                text=PAYMENT_FAILED_TEXT,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📞 Support", url=f"tg://user?id={OWNER_ID[0]}")]])
            )
