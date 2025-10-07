from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot_instance import bot
from datetime import datetime, timedelta
from wallets import SOL_WALLET
import time

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
            reply_markup=markup
        )
    except Exception:
        # If editing fails (e.g., original message was a photo), send a new message
        bot.send_message(chat_id, text, reply_markup=markup)

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
        reply_markup=markup
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
    
    text = """📱 Please provide your Telegram address.

Example: @https://t.me/yourtelegram

➔ Send your Telegram link now:"""
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=text
    )
    
    # Set state to wait for telegram address
    sponsorship_data[chat_id]['state'] = 'waiting_telegram'

def handle_telegram_address(message):
    """Handle telegram address input"""
    chat_id = message.chat.id
    
    if chat_id not in sponsorship_data or sponsorship_data[chat_id].get('state') != 'waiting_telegram':
        return False
    
    telegram_address = message.text.strip()
    
    # Basic validation for telegram address
    if not (telegram_address.startswith('@') or 't.me/' in telegram_address):
        bot.send_message(chat_id, "❌ Please provide a valid Telegram address (e.g., @username or https://t.me/username)")
        return True
    
    # Store telegram address
    sponsorship_data[chat_id]['telegram_address'] = telegram_address
    sponsorship_data[chat_id]['state'] = 'waiting_design'
    
    text = """🎨 Send Your Design: Which image or video would you like to feature? (for all postings & livestream overlay)

➔ Send your media file now:"""
    
    bot.send_message(chat_id, text)
    return True

def handle_design_media(message):
    """Handle design media input"""
    chat_id = message.chat.id
    
    if chat_id not in sponsorship_data or sponsorship_data[chat_id].get('state') != 'waiting_design':
        return False
    
    # Check if message contains media
    if not (message.photo or message.video or message.document or message.animation):
        bot.send_message(chat_id, "❌ Please send an image or video file.")
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
    """Send payment summary and instructions"""
    if chat_id not in sponsorship_data:
        return
    
    data = sponsorship_data[chat_id]
    duration = data['duration']
    price = data['price']
    start_date = data['start_date']
    telegram_address = data['telegram_address']
    
    # Calculate SOL amount (assuming 1 SOL = $50 for example)
    sol_amount = price / 50  # Adjust this rate as needed
    
    # Format start date
    start_date_str = start_date.strftime("%A, %d %B %Y")
    
    text = f"""⚙️ One last Step: Payment Required

Thank you for providing your project details. Please complete the payment within the next 15 minutes.

🔥 Order Summary
· Sponsor Duration: {duration} Days
· Livestream Ticket: 1
· Shared on TG & X
· Telegram Group Link: {telegram_address}
· Start: {start_date_str}
· Amount to Sponsor: {sol_amount:.3f} SOL

▶️ Please complete the payment of {sol_amount:.3f} SOL to the following wallet address:

<code>{SOL_WALLET}</code>

hit /sent to verify pending transactions"""

    bot.send_message(chat_id, text, parse_mode="HTML")
    
    # Clear sponsorship data
    sponsorship_data.pop(chat_id, None)

def handle_sponsorship_back(call):
    """Handle back button in sponsorship flow"""
    chat_id = call.message.chat.id
    
    # Clear any stored data and go back to main menu
    sponsorship_data.pop(chat_id, None)
    
    from menu import start_message
    bot.delete_message(chat_id, call.message.message_id)
    start_message(call.message)

def is_user_in_sponsorship_flow(chat_id):
    """Check if user is currently in sponsorship flow"""
    return chat_id in sponsorship_data and sponsorship_data[chat_id].get('state') in ['waiting_telegram', 'waiting_design']
