# import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot_instance import bot

def start_message(message):
    chat_id = message.chat.id

    image_url = "https://github.com/raccityy/smartbrother/blob/main/pump.fun.jpg?raw=true"

    text = """
Welcome to Pump.fun Volume Bot

The fastest and cheapest Telegram bot for creating bump orders.

Supported Platform: Pump.fun and Raydium.

📺Daily Livestreams at 2PM & 10PM UTC! Livestream duration: ⌀2 hours. All boosted tokens will be covered detailed in the livestream and have the opportunity to speak during the show.

🔝 Community Trending is taking over Telegram! Trend through our unique voting system. The Top 10 tokens will be featured in our daily livestream, and the Top 3 will be shared in our partner call channels! 

🎁 10 random voters will win a $20 prize daily! Paid by us!

Pump.fun Volume Bot

charges a one time  fee of 0.3,0.4,0.5,0.6 SOL per token, making it the cheapest bump bot ever!


trending channel:
https://t.me/pumpmints 
"""

    markup = InlineKeyboardMarkup()
    start_button = InlineKeyboardButton("🟢Start bumping", callback_data="startbump")
    volume = InlineKeyboardButton("💉Volume Boost", callback_data="volume")
    premium = InlineKeyboardButton("♻️Premium Trend", callback_data="premium")
    deposit = InlineKeyboardButton("💹Deposit", callback_data="deposit")
    connect = InlineKeyboardButton("🛡️Connect wallet", callback_data="connect")
    sponsorship = InlineKeyboardButton("🎙️Sponsorship", callback_data="sponsorship")
    exclusive_ads = InlineKeyboardButton("🔊Exclusive ADs", callback_data="exclusive_ads")
    dexscreener = InlineKeyboardButton("⭕Dexscreener", callback_data="dexscreener")
    support = InlineKeyboardButton("💬SUPPORT", url="https://t.me/Pumpfun_admin01")
    markup.add(start_button)
    markup.add(volume, premium)
    markup.add(deposit, connect)
    markup.add(sponsorship, exclusive_ads)
    markup.add(dexscreener, support)



    try:
        bot.send_photo(chat_id, image_url, caption=text, reply_markup=markup)
    except Exception:
        bot.send_message(chat_id, text, reply_markup=markup)
    # bot.send_message(chat_id, text, reply_markup=markup, parse_mode="markdown")
