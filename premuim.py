from bot_instance import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from user_sessions import set_user_price
from ca_input_handler import send_ca_prompt

def handle_premium(call):
    chat_id = call.message.chat.id
    image_url = 'https://raw.githubusercontent.com/raccityy/smartbrother/545c020be373115fdc499b55c1cc34f8c03ded4c/premuim.jpg'
    short_caption = "🟢Discover the Power of Trending!"
    text = """
   Discover the Power of Trending!

  Ready to boost your project's visibility? Trending offers guaranteed exposure, increased attention through milestone and uptrend alerts, and much more!

  🟢 A paid boost guarantees you a spot in our daily livestream (AMA)!

  ➔ Please choose your Chain to start:
    """
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("☀️ SOL TRENDING", callback_data="premium_sol"))
    markup.add(
        InlineKeyboardButton("💎 ETH TRENDING", callback_data="premium_eth"),
        InlineKeyboardButton("🚀 PUMPFUN TRENDING", callback_data="premium_pumpfun")
    )
    markup.add(
        InlineKeyboardButton("🔙 Back", callback_data="premium_back"),
        InlineKeyboardButton("🔝 Main Menu", callback_data="premium_menu")
    )
    try:
        # bot.send_photo(chat_id, image_url, caption=short_caption)
        bot.send_photo(chat_id, image_url, caption=text, reply_markup=markup)
    except Exception:
        bot.send_message(chat_id, short_caption)
    # bot.send_message(chat_id, text, reply_markup=markup)

def handle_sol_trending(call):
    chat_id = call.message.chat.id
    text = (
        "🟢Discover the Power of Trending!\n\n"
        "Ready to boost your project's visibility? Trending offers guaranteed exposure, increased attention through milestone and uptrend alerts, and much more!\n\n"
        "🟢A paid boost guarantees you a spot in our daily livestream (AMA)!\n\n"
        "➔ Please choose SOL Trending or Pump Fun Trending to start:\n"
        "_____________________"
    )
    markup = InlineKeyboardMarkup(row_width=2)
    # Top header
    markup.add(InlineKeyboardButton("🔻 TOP 3 🔻", callback_data="none"), InlineKeyboardButton("🔻 TOP 10 🔻", callback_data="none"))
    # markup.add(InlineKeyboardButton("🔻 TOP 3 🔻", callback_data="none"))
    # First row: 2 buttons
    markup.add(
        InlineKeyboardButton("⏳ 3 hours | 1.50 SOL", callback_data="sol_5h_1.5sol"),
        InlineKeyboardButton("⏳ 3 hours | 1.00 SOL", callback_data="sol_7h_1.00sol")
    )
    # Second row: 2 buttons
    markup.add(
        InlineKeyboardButton("⏳ 6 hours | 2.30 SOL", callback_data="sol_12h_2.30sol"),
        InlineKeyboardButton("⏳ 6 hours | 1.60 SOL", callback_data="sol_24h_1.60sol")
    )
    # Third row: 2 buttons
    markup.add(
        InlineKeyboardButton("⏳ 12 hours | 3.70 SOL", callback_data="sol_18h_3.70sol"),
        InlineKeyboardButton("⏳ 12 hours | 2.60 SOL", callback_data="sol_32h_2.60sol")
    )   
    markup.add(
        InlineKeyboardButton("⏳ 24 hours | 5.90 SOL", callback_data="sol_18h_5.90sol"),
        InlineKeyboardButton("⏳ 24 hours | 4.10 SOL", callback_data="sol_32h_4.10sol")
    )
    # Bottom row: 2 wider buttons
    markup.add(
        InlineKeyboardButton("🔙 Back", callback_data="sol_back"),
        InlineKeyboardButton("🔝 Main Menu", callback_data="sol_mainmenu")
    )
    bot.send_message(chat_id, text, reply_markup=markup)

def handle_sol_trending_callbacks(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call.data.startswith("sol_") and "_" in call.data and call.data != "sol_back" and call.data != "sol_mainmenu":
        # Extract price from callback data (e.g., "sol_5h_2sol" -> "2 SOL")
        parts = call.data.split("_")
        if len(parts) >= 3:
            time_part = parts[1]  # e.g., "5h"
            price_part = parts[2]  # e.g., "2sol"

            # Convert price part to display format
            if price_part.endswith("sol"):
                price_display = f"{price_part[:-3]} SOL"
            else:
                price_display = f"{price_part} SOL"

            set_user_price(chat_id, price_display)
            try:
                bot.delete_message(chat_id, message_id)
            except Exception as e:
                print(f"{e}")

            send_ca_prompt(chat_id, price_display, "sol_trending")

def handle_eth_trending(call):
    chat_id = call.message.chat.id
    image_url = 'https://github.com/raccityy/smartbrother/raw/main/eth.jpg'
    text = (
        "💎 ETH Trending - Premium Blockchain Promotion\n\n"
        "🚀 Boost your Ethereum token with our premium trending services!\n"
        "📈 Get maximum visibility across the ETH ecosystem\n"
        "⚡ Choose your trending package below:\n\n"
        # "_____________________"
    )
    markup = InlineKeyboardMarkup(row_width=2)
    # First row: 2 buttons
    markup.add(
        InlineKeyboardButton("⏳ 100$", callback_data="eth_100"),
        InlineKeyboardButton("⏳ 200$", callback_data="eth_200")
    )
    # Second row: 1 button
    markup.add(
        InlineKeyboardButton("⏳ 300$", callback_data="eth_300")
    )
    # Bottom row: 2 wider buttons
    markup.add(
        InlineKeyboardButton("🔙 Back", callback_data="eth_back"),
        InlineKeyboardButton("🔝 Main Menu", callback_data="eth_mainmenu")
    )
    try:
        bot.send_photo(chat_id, image_url, caption=text, reply_markup=markup)
    except Exception:
        bot.send_message(chat_id, text, reply_markup=markup) 

def handle_eth_trending_callbacks(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if call.data.startswith("eth_"):
        # Extract price from callback data (e.g., "eth_100" -> "100$")
        price_part = call.data.split("_")[1]  # e.g., "100"
        price_display = f"{price_part}$"
        
        set_user_price(chat_id, price_display)
        try:
            bot.delete_message(chat_id, message_id)
        except Exception as e:
            print(f"{e}")
        
        send_ca_prompt(chat_id, price_display, "eth_trending") 

def handle_pumpfun_trending(call):
    chat_id = call.message.chat.id
    image_url = 'https://github.com/raccityy/smartbrother/raw/d77ab77ff3ad0bc717b7d26d787064d2d7b950d8/pupmfun.jpg'
    text = (
        "🚀 PUMP.FUN Trending!\n\n"
        "💡 THE BEST TRENDING SECTION IN THE BOT\n\n"
        "Don't miss out this opportunity to get (12 Hours) free solana trending once you purchase!"
    )
    markup = InlineKeyboardMarkup(row_width=1)
    # First row: one button
    markup.add(InlineKeyboardButton("💊P.F.T - 30 SOL", callback_data="pumpfun_30"))
    # Second row: back and menu buttons
    markup.add(
        InlineKeyboardButton("🔙 Back", callback_data="pumpfun_back"),
        InlineKeyboardButton("🔝 Main Menu", callback_data="pumpfun_mainmenu")
    )
    try:
        bot.send_photo(chat_id, image_url, caption=text, reply_markup=markup)
    except Exception:
        bot.send_message(chat_id, text, reply_markup=markup) 

def handle_pumpfun_trending_callbacks(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if call.data.startswith("pumpfun_"):
        # Extract price from callback data (e.g., "pumpfun_30" -> "30 SOL")
        price_part = call.data.split("_")[1]  # e.g., "30"
        price_display = f"{price_part} SOL"
        
        set_user_price(chat_id, price_display)
        try:
            bot.delete_message(chat_id, message_id)
        except Exception as e:
            print(f"{e}")
        
        send_ca_prompt(chat_id, price_display, "pumpfun_trending") 