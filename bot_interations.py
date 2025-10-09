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

# Handler to process admin replies in the group
@bot.message_handler(func=lambda message: message.chat.id == group_chat_id)
def handle_admin_reply(message):
    admin_id = message.from_user.id
    if admin_id in admin_reply_state:
        user_chat_id = admin_reply_state[admin_id]
        
        # Handle cancel command
        if message.text and message.text.lower() in ['/cancel', '/exit', '/stop']:
            admin_reply_state.pop(admin_id, None)
            bot.send_message(message.chat.id, "❌ Reply mode cancelled.")
            return
        
        # Handle different types of messages
        try:
            if message.text:
                # Text message (including emojis)
                bot.send_message(user_chat_id, f"{message.text}")
                bot.send_message(message.chat.id, "✅ Text reply sent to user.")
            elif message.photo:
                # Image message
                bot.send_photo(user_chat_id, message.photo[-1].file_id, caption=message.caption)
                bot.send_message(message.chat.id, "✅ Image reply sent to user.")
            elif message.sticker:
                # Sticker message
                bot.send_sticker(user_chat_id, message.sticker.file_id)
                bot.send_message(message.chat.id, "✅ Sticker reply sent to user.")
            elif message.animation:
                # GIF/Animation message
                bot.send_animation(user_chat_id, message.animation.file_id, caption=message.caption)
                bot.send_message(message.chat.id, "✅ Animation reply sent to user.")
            elif message.video:
                # Video message
                bot.send_video(user_chat_id, message.video.file_id, caption=message.caption)
                bot.send_message(message.chat.id, "✅ Video reply sent to user.")
            elif message.document:
                # Document message
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
                bot.send_message(user_chat_id, "Admin sent a message (unsupported format)")
                bot.send_message(message.chat.id, "⚠️ Unsupported message type sent to user.")
            
            # Keep admin in reply mode for multiple messages
            # admin_reply_state.pop(admin_id, None)  # Commented out to allow multiple replies
            
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error sending reply: {str(e)}")
            admin_reply_state.pop(admin_id, None)

# Command handler for admins to exit reply mode
@bot.message_handler(commands=['exitreply', 'stopreply'], func=lambda message: message.chat.id == group_chat_id)
def handle_exit_reply_mode(message):
    admin_id = message.from_user.id
    if admin_id in admin_reply_state:
        admin_reply_state.pop(admin_id, None)
        bot.send_message(message.chat.id, "✅ Reply mode exited successfully.")
    else:
        bot.send_message(message.chat.id, "ℹ️ You are not currently in reply mode.")
