from bot_instance import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from user_sessions import set_user_price, set_user_ca, get_user_price
from ca_input_handler import send_ca_prompt
import requests

# Temporary storage for CA info for volume flow
volume_temp_ca_info = {}

PACKAGE_PRICES = {
    'vol_iron': '1.50',
    'vol_bronze': '2.50',
    'vol_gold': '3.50',
    'vol_platinum': '5.00',
    'vol_silver': '7.50',
    'vol_diamond': '10.05',
}

def handle_volume(call):
    chat_id = call.message.chat.id
    image_url = 'https://github.com/raccityy/smartbrother/blob/main/volume.jpg?raw=true'
    short_caption = "Choose the desired Volume Boost package:"
    text = """
    🧪Iron Package - $50,000 Volume

    🧪Bronze Package - $250,000 Volume

    🧪Silver Package - $100,000,000 Volume

    🧪Gold Package - $100,000 Volume

    🧪Platinum Package - $500,000 Volume

    🧪 Diamond Package - $2,500,000 Volume

    Please select the package below:
    """
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("1.50 SOL - Irion⛓️", callback_data="vol_iron"),
        InlineKeyboardButton("2.50 SOL - Bronze 🥉", callback_data="vol_bronze"),
        InlineKeyboardButton("3.50 SOL - Gold", callback_data="vol_gold"),
        InlineKeyboardButton("7.50 SOL - Platinum ⏺️", callback_data="vol_platinum"),
        InlineKeyboardButton("5.00 SOL - Silver 🥈", callback_data="vol_silver"),
        InlineKeyboardButton("10.50 SOL - Diamond💎", callback_data="vol_diamond"),
        InlineKeyboardButton("🔙 Back", callback_data="vol_back"),
        InlineKeyboardButton("🔝 Main Menu", callback_data="vol_mainmenu")
    )
    try:
        # bot.send_photo(chat_id, image_url, caption=short_caption)
        bot.send_photo(chat_id, image_url, caption=text, reply_markup=markup)
    except Exception:
        bot.send_message(chat_id, short_caption)

def handle_volume_package(call):
    chat_id = call.message.chat.id
    package = call.data
    price = PACKAGE_PRICES.get(package)
    if not price:
        bot.send_message(chat_id, "Unknown package selected.")
        return
    set_user_price(chat_id, price)
    send_ca_prompt(chat_id, f"{price} SOL", "volume")

# This function is now handled by the new CA input handler
# Keeping for backward compatibility but it's no longer used
