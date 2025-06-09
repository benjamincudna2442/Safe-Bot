from datetime import timedelta
import pytz
import datetime
import time
import logging
from devgagan import app
from devgagan.core.func import get_seconds
from devgagan.core.mongo import plans_db
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.raw.functions.messages import SendMedia, SetBotPrecheckoutResults, SetBotShippingResults
from pyrogram.raw.types import InputMediaInvoice, Invoice, DataJSON, LabeledPrice, UpdateBotPrecheckoutQuery, UpdateBotShippingQuery, UpdateNewMessage, MessageService, MessageActionPaymentSentMe, PeerUser, PeerChat, PeerChannel, ReplyInlineMarkup, KeyboardButtonRow, KeyboardButtonBuy
from config import OWNER_ID
import uuid
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Strings for premium plan purchase
PLAN_PURCHASE_TEXT = """
💎 **Unlock Premium Downloads with Smart Tools** 💎
**✘ ━━━━━━━━━━━━━━━━━━━━━ ✘**
🌟 **Why Go Premium?** 🌟
Access restricted content downloads from 30+ sites with blazing-fast speeds! 🚀
Choose a plan below to unlock exclusive features and support our service. ✨

👇 **Select Your Plan:** 👀

🔥 **Plan Benefits:**
- 📥 Download up to 100,000 files per batch
- 🎥 Access restricted video and audio content
- ⚡ Priority support and faster processing
- 🔒 Exclusive access to premium features

**Plans are highly customizable!** Contact the owner for tailored plans or use /pay or /buy for instant access. 🚀
"""

PAYMENT_SUCCESS_TEXT = """
**✅ Premium Plan Purchased!**

🎉 Thank you **{0}** for subscribing to **Plan {1}** with **{2} Stars**!  
Your premium access is now active. Enjoy restricted content downloads! 🚀

**🧾 Transaction ID:** `{3}`
"""

ADMIN_NOTIFICATION_TEXT = """
🌟 **New Premium Subscription!**  
✨ **User:** {0}  
⁉️ **User ID:** `{1}`  
🌐 **Username:** {2}  
💥 **Plan:** Plan {3} ({4} Stars)  
📝 **Transaction ID:** `{5}`
"""

INVOICE_CREATION_TEXT = "Generating invoice for Plan {0} ({1} Stars)...\nPlease wait ⏳"
INVOICE_CONFIRMATION_TEXT = "**✅ Invoice for Plan {0} ({1} Stars) generated! Proceed to pay below.**"
DUPLICATE_INVOICE_TEXT = "**🚫 Wait! A plan purchase is already in progress!**"
INVALID_INPUT_TEXT = "**❌ Invalid input! Please select a valid plan.**"
INVOICE_FAILED_TEXT = "**❌ Invoice creation failed! Try again or contact support.**"
PAYMENT_FAILED_TEXT = "**❌ Payment declined! Contact support for assistance.**"

# Active invoices to prevent duplicates
active_invoices = {}

@app.on_message(filters.command("rem") & filters.user(OWNER_ID))
async def remove_premium(client, message):
    try:
        if len(message.command) != 2:
            await message.reply_text("⚠️ **Usage:** /rem user_id")
            return

        user_id = int(message.command[1])
        user = await client.get_users(user_id)
        data = await plans_db.check_premium(user_id)

        if data and data.get("_id"):
            await plans_db.remove_premium(user_id)
            await message.reply_text("✅ **User removed from premium successfully!**")
            await client.send_message(
                chat_id=user_id,
                text=f"👋 **Hey {user.mention},**\n\nYour premium access has been removed.\nThank you for using Smart Tools! 😊"
            )
        else:
            await message.reply_text("⚠️ **Error:** Not a premium user ID!")
    except Exception as e:
        await message.reply_text(f"❌ **Error removing premium:** {str(e)}")
        logger.error(f"Error in remove_premium for user {user_id}: {str(e)}")

@app.on_message(filters.command("myplan") & filters.private)
async def myplan(client, message):
    try:
        user_id = message.from_user.id
        user = message.from_user.mention
        data = await plans_db.check_premium(user_id)

        if data and data.get("expire_date"):
            expiry = data.get("expire_date")
            expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
            expiry_str_in_ist = expiry_ist.strftime("%d-%m-%Y\n⏱️ **Expiry Time:** %I:%M:%S %p")

            current_time = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
            time_left = expiry_ist - current_time

            days = time_left.days
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            time_left_str = f"{days} days, {hours} hours, {minutes} minutes"
            await message.reply_text(
                f"⚜️ **Your Premium Plan** ⚜️\n\n"
                f"👤 **User:** {user}\n"
                f"⚡ **User ID:** <code>{user_id}</code>\n"
                f"⏰ **Time Left:** {time_left_str}\n"
                f"⌛ **Expiry Date:** {expiry_str_in_ist}"
            )
        else:
            await message.reply_text(f"👋 **Hey {user},**\n\nYou don't have an active premium plan.")
    except Exception as e:
        await message.reply_text(f"❌ **Error checking plan:** {str(e)}")
        logger.error(f"Error in myplan for user {user_id}: {str(e)}")

@app.on_message(filters.command("check") & filters.user(OWNER_ID))
async def check_premium(client, message):
    try:
        if len(message.command) != 2:
            await message.reply_text("⚠️ **Usage:** /check user_id")
            return

        user_id = int(message.command[1])
        user = await client.get_users(user_id)
        data = await plans_db.check_premium(user_id)

        if data and data.get("expire_date"):
            expiry = data.get("expire_date")
            expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
            expiry_str_in_ist = expiry_ist.strftime("%d-%m-%Y\n⏱️ **Expiry Time:** %I:%M:%S %p")

            current_time = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
            time_left = expiry_ist - current_time

            days = time_left.days
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            time_left_str = f"{days} days, {hours} hours, {minutes} minutes"
            await message.reply_text(
                f"⚜️ **Premium User Data** ⚜️\n\n"
                f"👤 **User:** {user.mention}\n"
                f"⚡ **User ID:** <code>{user_id}</code>\n"
                f"⏰ **Time Left:** {time_left_str}\n"
                f"⌛ **Expiry Date:** {expiry_str_in_ist}"
            )
        else:
            await message.reply_text("⚠️ **No premium data found for this user!**")
    except Exception as e:
        await message.reply_text(f"❌ **Error checking premium:** {str(e)}")
        logger.error(f"Error in check_premium for user {user_id}: {str(e)}")

@app.on_message(filters.command("add") & filters.user(OWNER_ID))
async def add_premium(client, message):
    try:
        if len(message.command) != 4:
            await message.reply_text(
                "⚠️ **Usage:** /add user_id time (e.g., '1 day', '1 hour', '1 min', '1 month', '1 year')"
            )
            return

        time_zone = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        current_time = time_zone.strftime("%d-%m-%Y\n⏱️ **Joining Time:** %I:%M:%S %p")
        user_id = int(message.command[1])
        user = await client.get_users(user_id)
        time_input = message.command[2] + " " + message.command[3]
        seconds = await get_seconds(time_input)

        if seconds <= 0:
            await message.reply_text(
                "⚠️ **Invalid time format.** Use '1 day', '1 hour', '1 min', '1 month', or '1 year'."
            )
            return

        expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        await plans_db.add_premium(user_id, expiry_time)
        data = await plans_db.check_premium(user_id)
        expiry = data.get("expire_date")
        expiry_str_in_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime(
            "%d-%m-%Y\n⏱️ **Expiry Time:** %I:%M:%S %p"
        )

        await message.reply_text(
            f"✅ **Premium Added Successfully** ✅\n\n"
            f"👤 **User:** {user.mention}\n"
            f"⚡ **User ID:** <code>{user_id}</code>\n"
            f"⏰ **Premium Access:** <code>{time_input}</code>\n"
            f"⏳ **Joining Date:** {current_time}\n"
            f"⌛ **Expiry Date:** {expiry_str_in_ist}\n\n"
            f"**Powered by Team SPY** 🚀",
            disable_web_page_preview=True
        )
        await client.send_message(
            chat_id=user_id,
            text=(
                f"👋 **Hey {user.mention},**\n\n"
                f"🎉 **Premium Access Granted!**\n"
                f"⏰ **Duration:** <code>{time_input}</code>\n"
                f"⏳ **Joining Date:** {current_time}\n"
                f"⌛ **Expiry Date:** {expiry_str_in_ist}\n\n"
                f"**Enjoy Premium Downloads!** ✨"
            ),
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply_text(f"❌ **Error adding premium:** {str(e)}")
        logger.error(f"Error in add_premium for user {user_id}: {str(e)}")

@app.on_message(filters.command("transfer") & filters.private)
async def transfer_premium(client, message):
    try:
        if len(message.command) != 2:
            await message.reply_text("⚠️ **Usage:** /transfer user_id")
            return

        new_user_id = int(message.command[1])
        sender_user_id = message.from_user.id
        sender_user = await client.get_users(sender_user_id)
        new_user = await client.get_users(new_user_id)

        data = await plans_db.check_premium(sender_user_id)
        if not data or not data.get("_id"):
            await message.reply_text("⚠️ **You are not a premium user!** Only premium users can transfer plans.")
            return

        expiry = data.get("expire_date")
        await plans_db.remove_premium(sender_user_id)
        await plans_db.add_premium(new_user_id, expiry)

        expiry_str_in_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime(
            "%d-%m-%Y\n⏱️ **Expiry Time:** %I:%M:%S %p"
        )
        time_zone = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        current_time = time_zone.strftime("%d-%m-%Y\n⏱️ **Transfer Time:** %I:%M:%S %p")

        await message.reply_text(
            f"✅ **Premium Plan Transferred Successfully!** ✅\n\n"
            f"👤 **From:** {sender_user.mention}\n"
            f"👤 **To:** {new_user.mention}\n"
            f"⏳ **Expiry Date:** {expiry_str_in_ist}\n\n"
            f"**Powered by Team SPY** 🚀"
        )
        await client.send_message(
            chat_id=new_user_id,
            text=(
                f"👋 **Hey {new_user.mention},**\n\n"
                f"🎉 **Premium Plan Transferred!**\n"
                f"🛡️ **From:** {sender_user.mention}\n"
                f"⏳ **Expiry Date:** {expiry_str_in_ist}\n"
                f"📅 **Transferred On:** {current_time}\n\n"
                f"**Enjoy Premium Downloads!** ✨"
            )
        )
    except Exception as e:
        await message.reply_text(f"❌ **Error transferring premium:** {str(e)}")
        logger.error(f"Error in transfer_premium for user {sender_user_id} to {new_user_id}: {str(e)}")

@app.on_message(filters.command("freez") & filters.user(OWNER_ID))
async def refresh_users(client, message):
    try:
        all_users = await plans_db.premium_users()
        removed_users = []
        not_removed_users = []

        for user_id in all_users:
            try:
                user = await client.get_users(user_id)
                chk_time = await plans_db.check_premium(user_id)

                if chk_time and chk_time.get("expire_date"):
                    expiry_date = chk_time["expire_date"]

                    if expiry_date <= datetime.datetime.now():
                        name = user.first_name
                        await plans_db.remove_premium(user_id)
                        await client.send_message(
                            user_id,
                            text=f"👋 **Hello {name},**\n\nYour premium subscription has expired."
                        )
                        logger.info(f"{name} ({user_id}) premium subscription expired.")
                        removed_users.append(f"{name} ({user_id})")
                    else:
                        name = user.first_name
                        current_time = datetime.datetime.now()
                        time_left = expiry_date - current_time

                        days = time_left.days
                        hours, remainder = divmod(time_left.seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)

                        remaining_time = f"{days} days, {hours} hours, {minutes} minutes"
                        logger.info(f"{name} ({user_id}): Remaining Time: {remaining_time}")
                        not_removed_users.append(f"{name} ({user_id})")
                else:
                    await plans_db.remove_premium(user_id)
                    logger.info(f"Unknown user {user_id} removed from premium.")
                    removed_users.append(f"Unknown ({user_id})")
            except Exception as e:
                await plans_db.remove_premium(user_id)
                logger.error(f"Error processing user {user_id}: {str(e)}")
                removed_users.append(f"Unknown ({user_id})")

        removed_text = "\n".join(removed_users) if removed_users else "No users removed."
        not_removed_text = "\n".join(not_removed_users) if not_removed_users else "No users with active premium."
        summary = (
            f"📊 **Premium Cleanup Summary** 📊\n\n"
            f"🗑️ **Removed Users:**\n{removed_text}\n\n"
            f"✅ **Active Users:**\n{not_removed_text}"
        )
        await message.reply_text(summary)
    except Exception as e:
        await message.reply_text(f"❌ **Error refreshing users:** {str(e)}")
        logger.error(f"Error in refresh_users: {str(e)}")

@app.on_message(filters.command(["pay", "buy"]) & filters.private)
async def buy_plan(client, message):
    try:
        user_id = message.from_user.id
        if user_id in banned_users:
            await message.reply_text("✘ **Sorry, you're banned from using this bot!**")
            return

        plan_text = (
            f"💎 **Choose Your Premium Plan** 💎\n\n"
            f"🔥 **Plan 1** - 5 Stars\n"
            f"   ⏰ Duration: 1 Day\n"
            f"   📥 Download restricted content with ease\n\n"
            f"🔥 **Plan 2** - 150 Stars\n"
            f"   ⏰ Duration: 7 Days\n"
            f"   📥 Enhanced download limits and priority support\n\n"
            f"🔥 **Plan 3** - 250 Stars\n"
            f"   ⏰ Duration: 1 Month\n"
            f"   📥 Full premium access with maximum benefits\n\n"
            f"**Custom Plans:** Contact the owner for tailored options! ✨\n"
            f"**Powered by Team SPY** 🚀"
        )
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Plan 1 (5 🌟)", callback_data="buy_plan_1"),
                InlineKeyboardButton("Plan 2 (150 🌟)", callback_data="buy_plan_2")
            ],
            [InlineKeyboardButton("Plan 3 (250 🌟)", callback_data="buy_plan_3")],
            [InlineKeyboardButton("📞 Contact Owner", url="https://t.me/kingofpatal")]
        ])
        await message.reply_text(plan_text, reply_markup=buttons)
    except Exception as e:
        await message.reply_text(f"❌ **Error displaying plans:** {str(e)}")
        logger.error(f"Error in buy_plan for user {message.from_user.id}: {str(e)}")

@app.on_callback_query(filters.regex(r"buy_plan_\d"))
async def handle_plan_callback(client, callback_query):
    try:
        user_id = callback_query.from_user.id
        chat_id = callback_query.message.chat.id
        data = callback_query.data

        if user_id in banned_users:
            await callback_query.message.reply_text("✘ **Sorry, you're banned from using this bot!**")
            await callback_query.answer("You are banned!", show_alert=True)
            return

        plan_map = {
            "buy_plan_1": {"stars": 5, "duration": "1 day", "plan_name": "1"},
            "buy_plan_2": {"stars": 150, "duration": "7 days", "plan_name": "2"},
            "buy_plan_3": {"stars": 250, "duration": "1 month", "plan_name": "3"}
        }

        plan = plan_map.get(data)
        if not plan:
            await callback_query.message.reply_text(INVALID_INPUT_TEXT)
            await callback_query.answer()
            return

        stars = plan["stars"]
        plan_name = plan["plan_name"]
        duration = plan["duration"]

        if active_invoices.get(user_id):
            await callback_query.message.reply_text(DUPLICATE_INVOICE_TEXT)
            await callback_query.answer()
            return

        back_button = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="show_plan_options")]])
        loading_message = await client.send_message(
            chat_id,
            INVOICE_CREATION_TEXT.format(plan_name, stars),
            reply_markup=back_button
        )

        active_invoices[user_id] = True
        timestamp = int(time.time())
        unique_id = str(uuid.uuid4())[:8]
        invoice_payload = f"plan_{user_id}_{stars}_{timestamp}_{unique_id}"
        random_id = int(hashlib.sha256(invoice_payload.encode()).hexdigest(), 16) % (2**63)

        title = f"Smart Tools Premium Plan {plan_name}"
        description = f"Unlock Plan {plan_name} ({duration}) with {stars} Stars for restricted content downloads! 🚀"
        currency = "XTR"

        invoice = Invoice(
            currency=currency,
            prices=[LabeledPrice(label=f"🌟 {stars} Stars", amount=stars)],
            max_tip_amount=0,
            suggested_tip_amounts=[],
            recurring=False,
            test=False
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
            rows=[KeyboardButtonRow(buttons=[KeyboardButtonBuy(text=f"Buy Plan {plan_name}")])]
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
            INVOICE_CONFIRMATION_TEXT.format(plan_name, stars),
            reply_markup=back_button
        )
        await callback_query.answer(f"Invoice generated for Plan {plan_name}!")
        logger.info(f"Invoice sent for Plan {plan_name} ({stars} stars) to user {user_id}")
    except Exception as e:
        await client.edit_message_text(
            chat_id,
            loading_message.id,
            INVOICE_FAILED_TEXT,
            reply_markup=back_button
        )
        logger.error(f"Error generating invoice for user {user_id}: {str(e)}")
    finally:
        active_invoices.pop(user_id, None)

@app.on_callback_query(filters.regex("show_plan_options"))
async def show_plan_options(client, callback_query):
    try:
        plan_text = (
            f"💎 **Choose Your Premium Plan** 💎\n\n"
            f"🔥 **Plan 1** - 5 Stars\n"
            f"   ⏰ Duration: 1 Day\n"
            f"   📥 Download restricted content with ease\n\n"
            f"🔥 **Plan 2** - 150 Stars\n"
            f"   ⏰ Duration: 7 Days\n"
            f"   📥 Enhanced download limits and priority support\n\n"
            f"🔥 **Plan 3** - 250 Stars\n"
            f"   ⏰ Duration: 1 Month\n"
            f"   📥 Full premium access with maximum benefits\n\n"
            f"**Custom Plans:** Contact the owner for tailored options! ✨\n"
            f"**Powered by Team SPY** 🚀"
        )
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Plan 1 (5 🌟)", callback_data="buy_plan_1"),
                InlineKeyboardButton("Plan 2 (150 🌟)", callback_data="buy_plan_2")
            ],
            [InlineKeyboardButton("Plan 3 (250 🌟)", callback_data="buy_plan_3")],
            [InlineKeyboardButton("📞 Contact Owner", url="https://t.me/kingofpatal")]
        ])
        await callback_query.message.edit_text(plan_text, reply_markup=buttons)
        await callback_query.answer()
    except Exception as e:
        await callback_query.message.reply_text(f"❌ **Error displaying plans:** {str(e)}")
        logger.error(f"Error in show_plan_options for user {callback_query.from_user.id}: {str(e)}")

@app.on_raw_update()
async def handle_payment(client, update, users, chats):
    if isinstance(update, UpdateBotPrecheckoutQuery):
        try:
            await client.invoke(
                SetBotPrecheckoutResults(
                    query_id=update.query_id,
                    success=True
                )
            )
            logger.info(f"Pre-checkout query {update.query_id} OK for user {update.user_id}")
        except Exception as e:
            logger.error(f"Pre-checkout query {update.query_id} failed: {str(e)}")
            await client.invoke(
                SetBotPrecheckoutResults(
                    query_id=update.query_id,
                    success=False,
                    error="Failed to process pre-checkout."
                )
            )
    elif isinstance(update, UpdateBotShippingQuery):
        try:
            await client.invoke(
                SetBotShippingResults(
                    query_id=update.query_id,
                    shipping_options=[]
                )
            )
            logger.info(f"Shipping query {update.query_id} OK for user {update.user_id}")
        except Exception as e:
            logger.error(f"Shipping query {update.query_id} failed: {str(e)}")
            await client.invoke(
                SetBotShippingResults(
                    query_id=update.query_id,
                    error="Shipping not needed for premium plans."
                )
            )
    elif isinstance(update, UpdateNewMessage) and isinstance(update.message, MessageService) and isinstance(update.message.action, MessageActionPaymentSentMe):
        try:
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

            plan_map = {
                5: {"duration": "1 day", "plan_name": "1", "seconds": 86400},
                150: {"duration": "7 days", "plan_name": "2", "seconds": 604800},
                250: {"duration": "1 month", "plan_name": "3", "seconds": 2592000}
            }

            plan = plan_map.get(payment.total_amount)
            if not plan:
                raise ValueError(f"Invalid payment amount: {payment.total_amount}")

            expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=plan["seconds"])
            await plans_db.add_premium(user_id, expiry_time)
            expiry_str_in_ist = expiry_time.astimezone(pytz.timezone("Asia/Kolkata")).strftime(
                "%d-%m-%Y\n⏱️ **Expiry Time:** %I:%M:%S %p"
            )
            time_zone = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
            current_time = time_zone.strftime("%d-%m-%Y\n⏱️ **Joining Time:** %I:%M:%S %p")

            await client.send_message(
                chat_id=chat_id,
                text=PAYMENT_SUCCESS_TEXT.format(full_name, plan["plan_name"], payment.total_amount, payment.charge.id)
            )

            await client.send_message(
                chat_id=user_id,
                text=(
                    f"👋 **Hey {full_name},**\n\n"
                    f"🎉 **Premium Plan {plan['plan_name']} Activated!**\n"
                    f"⏰ **Duration:** {plan['duration']}\n"
                    f"⏳ **Joining Date:** {current_time}\n"
                    f"⌛ **Expiry Date:** {expiry_str_in_ist}\n\n"
                    f"**Enjoy Premium Downloads!** ✨"
                ),
                disable_web_page_preview=True
            )

            admin_text = ADMIN_NOTIFICATION_TEXT.format(
                full_name, user_id, username, plan["plan_name"], payment.total_amount, payment.charge.id
            )
            for admin_id in OWNER_ID:
                try:
                    await client.send_message(
                        chat_id=admin_id,
                        text=admin_text
                    )
                except Exception as e:
                    logger.error(f"Failed to notify admin {admin_id}: {str(e)}")
        except Exception as e:
            logger.error(f"Payment processing failed for user {user_id}: {str(e)}")
            await client.send_message(
                chat_id=chat_id,
                text=PAYMENT_FAILED_TEXT,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📞 Support", url=f"tg://user?id={OWNER_ID}")]])
            )
