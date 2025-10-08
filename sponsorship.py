from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot_instance import bot
from datetime import datetime, timedelta
from wallets import SOL_WALLET
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
        'timestamp': time.time()
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
    
    # Try to get token info from DexScreener
    dexscreener_url = f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}"
    try:
        resp = requests.get(dexscreener_url, timeout=10)
        data = resp.json()
        found = bool(data.get('pairs') and len(data['pairs']) > 0)

        if found:
            pair = data['pairs'][0]
            token_name = pair['baseToken'].get('name', 'Unknown')
            token_symbol = pair['baseToken'].get('symbol', 'Unknown')
            price_usd = pair.get('priceUsd', '0')
            market_cap = pair.get('marketCap', '0')
            volume_24h = pair.get('volume', {}).get('h24', '0')
            liquidity_usd = pair.get('liquidity', {}).get('usd', '0')
            dex_id = pair.get('dexId', 'Unknown')
            chain_id = pair.get('chainId', 'Unknown')
            
            # Format numbers
            try:
                price_formatted = f"${float(price_usd):.6f}" if price_usd != '0' else 'N/A'
                market_cap_formatted = f"${float(market_cap):,.0f}" if market_cap != '0' else 'N/A'
                volume_formatted = f"${float(volume_24h):,.0f}" if volume_24h != '0' else 'N/A'
                liquidity_formatted = f"${float(liquidity_usd):,.0f}" if liquidity_usd != '0' else 'N/A'
            except (ValueError, TypeError):
                price_formatted = 'N/A'
                market_cap_formatted = 'N/A'
                volume_formatted = 'N/A'
                liquidity_formatted = 'N/A'
            
            # Store project details
            sponsorship_data[chat_id]['token_name'] = token_name
            sponsorship_data[chat_id]['token_symbol'] = token_symbol
            sponsorship_data[chat_id]['price_usd'] = price_usd
            sponsorship_data[chat_id]['market_cap'] = market_cap
            sponsorship_data[chat_id]['volume_24h'] = volume_24h
            sponsorship_data[chat_id]['liquidity_usd'] = liquidity_usd
            sponsorship_data[chat_id]['dex_id'] = dex_id
            sponsorship_data[chat_id]['chain_id'] = chain_id
            sponsorship_data[chat_id]['state'] = 'confirming_project'
            
            # Show project details confirmation
            text = f"""📄 <b>Project Details Found!</b>

✅ <b>Contract Address:</b> <code>{contract_address}</code>

📊 <b>Token Information:</b>
• <b>Name:</b> {token_name}
• <b>Symbol:</b> {token_symbol}
• <b>Price:</b> {price_formatted}
• <b>Market Cap:</b> {market_cap_formatted}
• <b>24h Volume:</b> {volume_formatted}
• <b>Liquidity:</b> {liquidity_formatted}
• <b>DEX:</b> {dex_id}
• <b>Chain:</b> {chain_id}

Please confirm these project details are correct before proceeding."""
            
        else:
            # Token not found on DexScreener
            sponsorship_data[chat_id]['token_name'] = 'Unknown Token'
            sponsorship_data[chat_id]['token_symbol'] = 'UNKNOWN'
            sponsorship_data[chat_id]['state'] = 'confirming_project'
            
            text = f"""⚠️ <b>Project Not Found on DexScreener</b>

✅ <b>Contract Address:</b> <code>{contract_address}</code>

📊 <b>Token Information:</b>
• <b>Name:</b> Unknown Token
• <b>Symbol:</b> UNKNOWN
• <b>Status:</b> Not listed on DexScreener

The contract address is valid but the token details could not be fetched from DexScreener. You can still proceed with the sponsorship."""
            
    except Exception as e:
        # Error fetching from DexScreener
        sponsorship_data[chat_id]['token_name'] = 'Unknown Token'
        sponsorship_data[chat_id]['token_symbol'] = 'UNKNOWN'
        sponsorship_data[chat_id]['state'] = 'confirming_project'
        
        text = f"""⚠️ <b>Could Not Fetch Project Details</b>

✅ <b>Contract Address:</b> <code>{contract_address}</code>

📊 <b>Token Information:</b>
• <b>Name:</b> Unknown Token
• <b>Symbol:</b> UNKNOWN
• <b>Status:</b> Error fetching from DexScreener

There was an error fetching token details. You can still proceed with the sponsorship."""
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✅ Confirm & Continue", callback_data="sponsor_confirm_project"),
        InlineKeyboardButton("🔙 Back", callback_data="sponsor_back")
    )
    
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
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
    duration = data['duration']
    price = data['price']
    start_date = data['start_date']
    contract_address = data.get('contract_address', 'Not provided')
    token_name = data.get('token_name', 'Not provided')
    token_symbol = data.get('token_symbol', 'Not provided')
    telegram_address = data.get('telegram_address', 'Not provided')
    
    # Get additional project details from DexScreener if available
    price_usd = data.get('price_usd', '0')
    market_cap = data.get('market_cap', '0')
    volume_24h = data.get('volume_24h', '0')
    liquidity_usd = data.get('liquidity_usd', '0')
    dex_id = data.get('dex_id', 'Unknown')
    chain_id = data.get('chain_id', 'Unknown')
    
    # Calculate SOL amount (assuming 1 SOL = $50 for example)
    sol_amount = price / 50  # Adjust this rate as needed
    
    # Format start date
    start_date_str = start_date.strftime("%A, %d %B %Y")
    
    # Format numbers
    try:
        price_formatted = f"${float(price_usd):.6f}" if price_usd != '0' else 'N/A'
        market_cap_formatted = f"${float(market_cap):,.0f}" if market_cap != '0' else 'N/A'
        volume_formatted = f"${float(volume_24h):,.0f}" if volume_24h != '0' else 'N/A'
        liquidity_formatted = f"${float(liquidity_usd):,.0f}" if liquidity_usd != '0' else 'N/A'
    except (ValueError, TypeError):
        price_formatted = 'N/A'
        market_cap_formatted = 'N/A'
        volume_formatted = 'N/A'
        liquidity_formatted = 'N/A'
    
    text = f"""⚙️ One last Step: Payment Required

Thank you for providing your project details. Please complete the payment within the next 15 minutes.

🔥 <b>Sponsorship Order Summary</b>

📊 <b>Project Details:</b>
• <b>Token Name:</b> {token_name}
• <b>Symbol:</b> {token_symbol}
• <b>Contract Address:</b> <code>{contract_address}</code>
• <b>Price:</b> {price_formatted}
• <b>Market Cap:</b> {market_cap_formatted}
• <b>24h Volume:</b> {volume_formatted}
• <b>Liquidity:</b> {liquidity_formatted}
• <b>DEX:</b> {dex_id}
• <b>Chain:</b> {chain_id}

📺 <b>Sponsorship Details:</b>
• <b>Duration:</b> {duration} Days
• <b>Livestream Ticket:</b> 1
• <b>Shared on:</b> TG & X
• <b>Telegram Group:</b> {telegram_address}
• <b>Start Date:</b> {start_date_str}
• <b>Amount:</b> {sol_amount:.3f} SOL (${price})

▶️ Please complete the payment of <b>{sol_amount:.3f} SOL</b> to the following wallet address:

<code>{SOL_WALLET}</code>

Click /sent to verify pending transactions"""

    bot.send_message(chat_id, text, parse_mode="HTML")
    
    # Clear sponsorship data
    sponsorship_data.pop(chat_id, None)

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
    if current_state == 'waiting_contract':
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
    return chat_id in sponsorship_data and sponsorship_data[chat_id].get('state') in ['waiting_contract', 'confirming_project', 'waiting_telegram', 'confirming_telegram', 'waiting_design']
