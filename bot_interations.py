from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot_instance import bot

group_chat_id = -1003001274091  # Replace with your actual group chat ID

# Store mapping from group message_id to user chat_id
reply_targets = {}

# Store mapping from admin chat_id to user chat_id for reply flow
admin_reply_state = {}

def send_payment_verification_to_group(user, price, ca, tx_hash, user_chat_id=None):
    text = (
        f"this user @{user}\n\n"
        f"selected this {price}\n"
        f"with this ca {ca}\n"
        f"and you are awaiting payment to start working\n"
        f"so please verify this {tx_hash} immediately"
    )
    markup = InlineKeyboardMarkup()
    reply_btn = InlineKeyboardButton("reply", callback_data=f"group_reply_{user_chat_id}")
    close_btn = InlineKeyboardButton("close", callback_data=f"group_close_{user_chat_id}")
    markup.add(reply_btn, close_btn)
    sent = bot.send_message(group_chat_id, text, reply_markup=markup)
    if user_chat_id:
        reply_targets[sent.message_id] = user_chat_id


def handle_group_callback(call):
    if call.data.startswith("group_reply_"):
        # Extract user_chat_id from callback data
        user_chat_id = call.data.split("group_reply_")[1]
        admin_reply_state[call.from_user.id] = user_chat_id
        bot.send_message(call.message.chat.id, 
            "📝 <b>Reply Mode Activated</b>\n\n"
            "You can now send:\n"
            "• 📝 Text messages (with emojis)\n"
            "• 🖼️ Images/Photos\n"
            "• 😄 Stickers\n"
            "• 🎬 Videos/GIFs\n"
            "• 📄 Documents\n"
            "• 🎤 Voice messages\n"
            "• 📹 Video notes\n\n"
            "Send your reply now or type <code>/cancel</code> to exit reply mode.",
            parse_mode="HTML")
    elif call.data.startswith("group_close_"):
        bot.delete_message(call.message.chat.id, call.message.message_id)

# Group message handler moved to main.py for proper priority

# Command handler for admins to exit reply mode
@bot.message_handler(commands=['exitreply', 'stopreply'], func=lambda message: message.chat.id == group_chat_id)
def handle_exit_reply_mode(message):
    admin_id = message.from_user.id
    if admin_id in admin_reply_state:
        admin_reply_state.pop(admin_id, None)
        bot.send_message(message.chat.id, "✅ Reply mode exited successfully.")
    else:
        bot.send_message(message.chat.id, "ℹ️ You are not currently in reply mode.")
