from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot_instance import bot
from datetime import datetime, timedelta
from wallets import SOL_WALLET
from project_details_formatter import send_project_details_confirmation, format_payment_summary_with_project_details, fetch_project_details_from_dexscreener
import time
import requests

# Store sponsorship data for each user
sponsorship_data = {}

def handle_sponsorship(call):
    """Handle sponsorship button click"""
    chat_id = call.message.chat.id
    
    text = """🔥 Secure a Prime Sponsorship slot in our daily Livestream (⌀ 2h duration)!

⭐️ Your token will be featured prominently in the show, including multiple shoutouts and strong community visibility.

📺 You will also have the chance to join live and present your project during the stream.

✅ Support: @Pumpfun_admin01

➔ Choose your preferred sponsorship duration:"""

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("📅 1 day - $390", callback_data="sponsor_1day"))
    markup.add(InlineKeyboardButton("📅 3 days - $990", callback_data="sponsor_3days"))
    markup.add(InlineKeyboardButton("📅 7 days - $1990", callback_data="sponsor_7days"))
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="sponsor_back"))
    
    try:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=markup,
            parse_mode="HTML"
        )
    except Exception:
        # If editing fails (e.g., original message was a photo), send a new message
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")

def handle_sponsorship_duration(call):
    """Handle sponsorship duration selection"""
    chat_id = call.message.chat.id
    data = call.data
    
    # Extract duration and price from callback data
    if data == "sponsor_1day":
        duration = 1
        price = 390
    elif data == "sponsor_3days":
        duration = 3
        price = 990
    elif data == "sponsor_7days":
        duration = 7
        price = 1990
    else:
        return
    
    # Store sponsorship data
    sponsorship_data[chat_id] = {
        'duration': duration,
        'price': price,
        'timestamp': time.time(),
        'state': 'selecting_date'
    }
    
    # Generate available dates (starting from tomorrow)
    today = datetime.now()
    available_dates = []
    
    for i in range(1, 5):  # Show next 4 available slots
        start_date = today + timedelta(days=i)
        end_date = start_date + timedelta(days=duration-1)
        
        start_str = start_date.strftime("%m/%d/%Y")
        end_str = end_date.strftime("%m/%d/%Y")
        available_dates.append((start_str, end_str, f"sponsor_date_{i}"))
    
    text = f"""⚡️ Choose Your Date! Here are the next available dates for a {duration}-day sponsorship.

➔ When would you like to start your sponsorship?"""

    markup = InlineKeyboardMarkup(row_width=1)
    for start_date, end_date, callback_data in available_dates:
        markup.add(InlineKeyboardButton(f"📅 {start_date} - {end_date}", callback_data=callback_data))
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="sponsor_back"))
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=markup,
        parse_mode="HTML"
    )

def handle_sponsorship_date(call):
    """Handle sponsorship date selection"""
    chat_id = call.message.chat.id
    data = call.data
    
    if chat_id not in sponsorship_data:
        bot.answer_callback_query(call.id, "❌ Session expired. Please start over.")
        return
    
    # Extract date index from callback data
    date_index = int(data.split("_")[-1])
    
    # Calculate the actual start date
    today = datetime.now()
    start_date = today + timedelta(days=date_index)
    end_date = start_date + timedelta(days=sponsorship_data[chat_id]['duration']-1)
    
    # Update sponsorship data with selected dates
    sponsorship_data[chat_id]['start_date'] = start_date
    sponsorship_data[chat_id]['end_date'] = end_date
    
    # Set state to wait for contract address
    sponsorship_data[chat_id]['state'] = 'waiting_contract'
    
    text = """📄 Please provide your Contract Address.

Example: 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU

➔ Send your contract address now:"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="sponsor_back"))
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=markup,
        parse_mode="HTML"
    )

def handle_contract_address(message):
    """Handle contract address input with DexScreener integration"""
    chat_id = message.chat.id
    
    if chat_id not in sponsorship_data or sponsorship_data[chat_id].get('state') != 'waiting_contract':
        return False
    
    contract_address = message.text.strip()
    
    # Basic validation for contract address (Solana addresses are typically 32-44 characters)
    if len(contract_address) < 32 or len(contract_address) > 44:
        text = """❌ Invalid Contract Address

Please provide a valid Solana contract address:
• Length: 32-44 characters
• Alphanumeric characters only

Example: 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"""
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔄 Retry", callback_data="sponsor_retry_contract"),
            InlineKeyboardButton("🔙 Back", callback_data="sponsor_back")
        )
        
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
        return True
    
    # Store contract address
    sponsorship_data[chat_id]['contract_address'] = contract_address
    
    # Fetch and store project details using standardized formatter
    project_data = fetch_project_details_from_dexscreener(contract_address)
    
    # Store all project details in sponsorship data
    sponsorship_data[chat_id].update(project_data)
    sponsorship_data[chat_id]['state'] = 'confirming_project'
    
    # Send standardized project details confirmation
    send_project_details_confirmation(
        chat_id=chat_id,
        contract_address=contract_address,
        confirm_callback="sponsor_confirm_project",
        back_callback="sponsor_back"
    )
    
    return True

# handle_token_details function removed - now using DexScreener API

def handle_telegram_address(message):
    """Handle telegram address input"""
    chat_id = message.chat.id
    
    if chat_id not in sponsorship_data or sponsorship_data[chat_id].get('state') != 'waiting_telegram':
        return False
    
    telegram_address = message.text.strip()
    
    # Basic validation for telegram address
    if not (telegram_address.startswith('@') or 't.me/' in telegram_address):
        text = """❌ Invalid Telegram Address

Please provide a valid Telegram address format:
• @username
• https://t.me/username

Example: @Pumpfun_admin01 or https://t.me/Pumpfun_admin01"""
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔄 Retry", callback_data="sponsor_retry_telegram"),
            InlineKeyboardButton("🔙 Back", callback_data="sponsor_back")
        )
        
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
        return True
    
    # Store telegram address
    sponsorship_data[chat_id]['telegram_address'] = telegram_address
    sponsorship_data[chat_id]['state'] = 'confirming_telegram'
    
    text = f"""📱 Telegram Address Confirmation

✅ Telegram Address: <code>{telegram_address}</code>

Please confirm this is the correct telegram address before proceeding to the next step.

➔ Click 'Confirm' to continue or 'Back' to change the address."""
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✅ Confirm", callback_data="sponsor_confirm_telegram"),
        InlineKeyboardButton("🔙 Back", callback_data="sponsor_back")
    )
    
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
    return True

def handle_design_media(message):
    """Handle design media input"""
    chat_id = message.chat.id
    
    if chat_id not in sponsorship_data or sponsorship_data[chat_id].get('state') != 'waiting_design':
        return False
    
    # Check if message contains media
    if not (message.photo or message.video or message.document or message.animation):
        text = """❌ Invalid Media File

Please send a valid media file:
• 📷 Image/Photo
• 🎬 Video
• 📄 Document
• 🎭 Animation/GIF

Supported formats: JPG, PNG, MP4, GIF, PDF, etc."""
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔄 Retry", callback_data="sponsor_retry_design"),
            InlineKeyboardButton("🔙 Back", callback_data="sponsor_back")
        )
        
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
        return True
    
    # Store media file info
    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        file_type = "video"
    elif message.document:
        file_id = message.document.file_id
        file_type = "document"
    elif message.animation:
        file_id = message.animation.file_id
        file_type = "animation"
    
    sponsorship_data[chat_id]['design_file_id'] = file_id
    sponsorship_data[chat_id]['design_file_type'] = file_type
    
    # Send payment summary
    send_payment_summary(chat_id)
    return True

def send_payment_summary(chat_id):
    """Send payment summary and instructions with project details"""
    if chat_id not in sponsorship_data:
        return
    
    data = sponsorship_data[chat_id]
    
    # Calculate SOL amount (1 SOL = $222)
    sol_amount = data['price'] / 222
    
    # Prepare project data for standardized formatter
    project_data = {
        'contract_address': data.get('contract_address', 'Not provided'),
        'token_name': data.get('token_name', 'Not provided'),
        'token_symbol': data.get('token_symbol', 'Not provided'),
        'found': data.get('found', False),
        'price_formatted': data.get('price_formatted', 'N/A'),
        'market_cap_formatted': data.get('market_cap_formatted', 'N/A'),
        'volume_formatted': data.get('volume_formatted', 'N/A'),
        'liquidity_formatted': data.get('liquidity_formatted', 'N/A'),
        'dex_id': data.get('dex_id', 'Unknown'),
        'chain_id': data.get('chain_id', 'Unknown'),
        'status': data.get('status', 'Unknown')
    }
    
    # Prepare order details
    order_details = {
        'price': data['price'],
        'duration': data['duration'],
        'start_date': data['start_date'],
        'telegram_address': data.get('telegram_address', 'Not provided'),
        'sol_amount': f"{sol_amount:.3f}",
        'usdt_amount': f"${data['price']}",
        'wallet_address': SOL_WALLET
    }
    
    # Use standardized payment summary formatter
    text = format_payment_summary_with_project_details(project_data, order_details)
    
    bot.send_message(chat_id, text, parse_mode="HTML")
    
    # Keep sponsorship data for /sent command - don't clear immediately
    sponsorship_data[chat_id]['state'] = 'payment_pending'

def send_sponsorship_tx_hash_prompt(chat_id, sol_amount, usdt_amount=None):
    """Send sponsorship-specific tx hash input prompt with cancel button"""
    # Update state to waiting for transaction hash
    if chat_id in sponsorship_data:
        sponsorship_data[chat_id]['state'] = 'waiting_tx_hash'
    
    # Format amount display
    if usdt_amount:
        amount_display = f"<b>{sol_amount} SOL</b> ({usdt_amount} USDT)"
    else:
        amount_display = f"<b>{sol_amount} SOL</b>"
    
    text = f"""💳 <b>Transaction Verification Required</b>

You selected sponsorship payment of {amount_display}

Please send your transaction hash below and await immediate confirmation.

⏰ You have 15 minutes to submit your transaction hash."""
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("❌ Cancel", callback_data="sponsor_tx_cancel"),
        InlineKeyboardButton("🔄 Retry", callback_data="sponsor_tx_retry")
    )
    
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")

def send_sponsorship_verification_to_group(user, data, tx_hash, user_chat_id=None):
    """Send sponsorship verification message to group"""
    from bot_interations import group_chat_id, reply_targets
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    # Prepare sponsorship details
    duration = data['duration']
    price = data['price']
    start_date = data['start_date']
    telegram_address = data.get('telegram_address', 'Not provided')
    contract_address = data.get('contract_address', 'Not provided')
    token_name = data.get('token_name', 'Not provided')
    token_symbol = data.get('token_symbol', 'Not provided')
    
    start_date_str = start_date.strftime("%A, %d %B %Y")
    sol_amount = f"{price / 222:.3f}"
    
    text = f"""🔥 <b>SPONSORSHIP PAYMENT VERIFICATION</b>

👤 <b>User:</b> @{user}
💳 <b>Amount:</b> {sol_amount} SOL (${price} USDT)
📅 <b>Duration:</b> {duration} Days
📅 <b>Start Date:</b> {start_date_str}
📱 <b>Telegram:</b> {telegram_address}

📊 <b>Project Details:</b>
• <b>Token:</b> {token_name} ({token_symbol})
• <b>Contract:</b> <code>{contract_address}</code>

🔗 <b>Transaction Hash:</b> <code>{tx_hash}</code>

⏰ Please verify this transaction immediately to start the sponsorship."""
    
    markup = InlineKeyboardMarkup()
    reply_btn = InlineKeyboardButton("reply", callback_data=f"group_reply_{user_chat_id}")
    close_btn = InlineKeyboardButton("close", callback_data=f"group_close_{user_chat_id}")
    markup.add(reply_btn, close_btn)
    
    sent = bot.send_message(group_chat_id, text, reply_markup=markup, parse_mode="HTML")
    if user_chat_id:
        reply_targets[sent.message_id] = user_chat_id

def handle_sponsorship_back(call):
    """Handle back button in sponsorship flow"""
    chat_id = call.message.chat.id
    
    if chat_id not in sponsorship_data:
        # If no data, go to main menu
        from menu import start_message
        bot.delete_message(chat_id, call.message.message_id)
        start_message(call.message)
        return
    
    current_state = sponsorship_data[chat_id].get('state', '')
    
    # Navigate back through the flow based on current state
    if current_state == 'selecting_date':
        # Go back to duration selection
        handle_sponsorship(call)
    elif current_state == 'waiting_contract':
        # Go back to date selection
        handle_sponsorship_duration(call)
    elif current_state == 'confirming_project':
        # Go back to contract address input
        text = """📄 Please provide your Contract Address.

Example: 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU

➔ Send your contract address now:"""
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="sponsor_back"))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=markup,
            parse_mode="HTML"
        )
        sponsorship_data[chat_id]['state'] = 'waiting_contract'
    elif current_state == 'waiting_telegram':
        # Go back to project confirmation
        contract_address = sponsorship_data[chat_id]['contract_address']
        token_name = sponsorship_data[chat_id].get('token_name', 'Unknown')
        token_symbol = sponsorship_data[chat_id].get('token_symbol', 'UNKNOWN')
        
        # Re-fetch and show project details
        text = f"""📄 <b>Project Details</b>

✅ <b>Contract Address:</b> <code>{contract_address}</code>

📊 <b>Token Information:</b>
• <b>Name:</b> {token_name}
• <b>Symbol:</b> {token_symbol}

Please confirm these project details are correct before proceeding."""
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✅ Confirm & Continue", callback_data="sponsor_confirm_project"),
            InlineKeyboardButton("🔙 Back", callback_data="sponsor_back")
        )
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=markup,
            parse_mode="HTML"
        )
        sponsorship_data[chat_id]['state'] = 'confirming_project'
    elif current_state == 'confirming_telegram':
        # Go back to telegram input
        text = """📱 Please provide your Telegram address.

Example: @Pumpfun_admin01 or https://t.me/Pumpfun_admin01

➔ Send your Telegram link now:"""
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="sponsor_back"))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=markup,
            parse_mode="HTML"
        )
        sponsorship_data[chat_id]['state'] = 'waiting_telegram'
    elif current_state == 'waiting_design':
        # Go back to telegram confirmation
        telegram_address = sponsorship_data[chat_id].get('telegram_address', 'Not provided')
        
        text = f"""📱 Telegram Address Confirmation

✅ Telegram Address: <code>{telegram_address}</code>

Please confirm this is the correct telegram address before proceeding to the next step.

➔ Click 'Confirm' to continue or 'Back' to change the address."""
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✅ Confirm", callback_data="sponsor_confirm_telegram"),
            InlineKeyboardButton("🔙 Back", callback_data="sponsor_back")
        )
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=markup,
            parse_mode="HTML"
        )
        sponsorship_data[chat_id]['state'] = 'confirming_telegram'
    elif current_state == 'waiting_design':
        # Go back to telegram confirmation
        telegram_address = sponsorship_data[chat_id].get('telegram_address', 'Not provided')
        
        text = f"""📱 Telegram Address Confirmation

✅ Telegram Address: <code>{telegram_address}</code>

Please confirm this is the correct telegram address before proceeding to the next step.

➔ Click 'Confirm' to continue or 'Back' to change the address."""
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✅ Confirm", callback_data="sponsor_confirm_telegram"),
            InlineKeyboardButton("🔙 Back", callback_data="sponsor_back")
        )
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=markup,
            parse_mode="HTML"
        )
        sponsorship_data[chat_id]['state'] = 'confirming_telegram'
    else:
        # Default: go back to duration selection
        handle_sponsorship_duration(call)

def handle_sponsorship_confirm_project(call):
    """Handle confirm project details button"""
    chat_id = call.message.chat.id
    
    if chat_id not in sponsorship_data:
        bot.answer_callback_query(call.id, "❌ Session expired. Please start over.")
        return
    
    # Update state to waiting for telegram address
    sponsorship_data[chat_id]['state'] = 'waiting_telegram'
    
    text = """📱 Please provide your Telegram address.

Example: @Pumpfun_admin01 or https://t.me/Pumpfun_admin01

➔ Send your Telegram link now:"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="sponsor_back"))
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=markup,
        parse_mode="HTML"
    )

def handle_sponsorship_confirm_contract(call):
    """Handle confirm contract address button (legacy - now handled by confirm_project)"""
    # This function is kept for compatibility but should redirect to confirm_project flow
    handle_sponsorship_confirm_project(call)

def handle_sponsorship_confirm_token_details(call):
    """Handle confirm token details button (legacy - now handled by confirm_project)"""
    # This function is kept for compatibility but should redirect to confirm_project flow
    handle_sponsorship_confirm_project(call)

def handle_sponsorship_confirm_telegram(call):
    """Handle confirm telegram address button"""
    chat_id = call.message.chat.id
    
    if chat_id not in sponsorship_data:
        bot.answer_callback_query(call.id, "❌ Session expired. Please start over.")
        return
    
    # Update state to waiting for design media
    sponsorship_data[chat_id]['state'] = 'waiting_design'
    
    text = """🎨 Send Your Design: Which image or video would you like to feature? (for all postings & livestream overlay)

➔ Send your media file now:"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="sponsor_back"))
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=markup,
        parse_mode="HTML"
    )


def handle_sponsorship_retry_contract(call):
    """Handle retry contract address button"""
    chat_id = call.message.chat.id
    
    if chat_id not in sponsorship_data:
        bot.answer_callback_query(call.id, "❌ Session expired. Please start over.")
        return
    
    text = """📄 Please provide your Contract Address.

Example: 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU

➔ Send your contract address now:"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="sponsor_back"))
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=markup,
        parse_mode="HTML"
    )

def handle_sponsorship_retry_telegram(call):
    """Handle retry telegram address button"""
    chat_id = call.message.chat.id
    
    if chat_id not in sponsorship_data:
        bot.answer_callback_query(call.id, "❌ Session expired. Please start over.")
        return
    
    text = """📱 Please provide your Telegram address.

Example: @https://t.me/yourtelegram

➔ Send your Telegram link now:"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="sponsor_back"))
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=markup,
        parse_mode="HTML"
    )

def handle_sponsorship_retry_design(call):
    """Handle retry design media button"""
    chat_id = call.message.chat.id
    
    if chat_id not in sponsorship_data:
        bot.answer_callback_query(call.id, "❌ Session expired. Please start over.")
        return
    
    text = """🎨 Send Your Design: Which image or video would you like to feature? (for all postings & livestream overlay)

➔ Send your media file now:"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="sponsor_back"))
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=markup,
        parse_mode="HTML"
    )

def is_user_in_sponsorship_flow(chat_id):
    """Check if user is currently in sponsorship flow"""
    return chat_id in sponsorship_data and sponsorship_data[chat_id].get('state') in ['selecting_date', 'waiting_contract', 'confirming_project', 'waiting_telegram', 'confirming_telegram', 'waiting_design', 'payment_pending', 'waiting_tx_hash']
