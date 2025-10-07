from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot_instance import bot
from wallets import SOL_WALLET

def handle_exclusive_ads(call):
    """Handle exclusive ads button click"""
    chat_id = call.message.chat.id
    
    text = """🎩 Exclusive Ads – High Impact Promotion for Your Project

🔥 Reach thousands of real users with our top tier ad options across the PumpFun ecosystem.

⚡️ Choose one of the options below to learn more and boost your project visibility."""

    markup = InlineKeyboardMarkup()
    # First column - 1 button
    markup.add(InlineKeyboardButton("🚀 PumpFun Ultimate Boost", callback_data="exclusive_ultimate"))
    # Second column - 1 button
    markup.add(InlineKeyboardButton("🗳️ Voting Requirement", callback_data="exclusive_voting"))
    # Third column - 2 buttons
    markup.add(
        InlineKeyboardButton("📢 Mass DM", callback_data="exclusive_massdm"),
        InlineKeyboardButton("🔘 Button Ads", callback_data="exclusive_buttonads")
    )
    # Fourth column - 2 buttons
    markup.add(
        InlineKeyboardButton("🎤 PumpFun AMA", callback_data="exclusive_majorama"),
        InlineKeyboardButton("🔙 Back", callback_data="exclusive_back")
    )
    
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

def handle_exclusive_ultimate(call):
    """Handle PumpFun Ultimate Boost"""
    chat_id = call.message.chat.id
    
    text = """🎩 PumpFun Ultimate Boost

⭐️ Maximum reach guaranteed! For ambitious tokens and presales, we offer an all-in-one package for maximum reach. By choosing one of our packages, you save a lot of money and, most importantly, time when it comes to organization. We have put together two packages for you.

🔥 GOLD PACK
✅ 24h Join Requirement
✅ 1 Mass DM
✅ 1 Day Button Ad
✅ PumpFun AMA
✅ 24h Trending (Top 3)
✅ 1 Day Livestream Sponsoring
✅ Call, X & AMA with Pin @Pumpfun_admin01
✅ Call @Pumpfun_admin01

🔥 PLATINUM PACK
✅ 72h Join Requirement
✅ 2 Mass DM
✅ PumpFun AMA
✅ 72h Trending (Top 3)
✅ 7 Days Livestream Sponsoring
✅ Call, X & AMA @Pumpfun_admin01
✅ Call @Pumpfun_admin01

❗️ Contact us for more info!"""

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📞 Contact", url="https://t.me/Pumpfun_admin01"),
        InlineKeyboardButton("🔙 Back", callback_data="exclusive_back")
    )
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=markup
    )

def handle_exclusive_voting(call):
    """Handle Voting Requirement"""
    chat_id = call.message.chat.id
    
    text = """🎩 Voting Requirement for Community Trending

🔥 The ultimate tool for generating new members. All tokens participating in PumpFun Community Trending (Voting) trend through user votes. Every user who wants to vote must first join your token group (see video). This is insane!

✅ Expected New Members: 4000 - 8000
✅ Duration: 24h or 72h

❗️ Contact us for more info!"""

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📞 Contact", url="https://t.me/Pumpfun_admin01"),
        InlineKeyboardButton("🔙 Back", callback_data="exclusive_back")
    )
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=markup
    )

def handle_exclusive_massdm(call):
    """Handle Mass DM"""
    chat_id = call.message.chat.id
    
    text = """🎩 Mass DM via @PumpFunBuyBot

🔥 One of our most popular and effective marketing tools. Do you have an upcoming launch? Does your token need more attention? Or do you want to promote a tool or channel? Our Mass DM tool is perfect for this and highly effective.

✅ Totally Members: +550.000 DM's
✅ Expected New Members: 500 - 1500
✅ Options: 1 or 2 DM's

❗️ Contact us for more info!"""

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📞 Contact", url="https://t.me/Pumpfun_admin01"),
        InlineKeyboardButton("🔙 Back", callback_data="exclusive_back")
    )
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=markup
    )

def handle_exclusive_buttonads(call):
    """Handle Button Ads"""
    chat_id = call.message.chat.id
    
    text = """🔥 Button Ad is one of our most frequently booked ads. With this ad, you reach thousands of users at the same time. Whether it's our Trending, all Hype Post notifications, or Buy notifications in all groups – the button is exclusively yours, generating high visibility.

⭐️ Highlight: No rotation!

✅ Totally Groups: +120.000
✅ Totally User: +17M
✅ Daily Impressions: +9M
✅ Expected New Members: 300 - 1500
✅ Options: 1, 3 or 7 Days

❗️ Contact us for more info!"""

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📞 Contact", url="https://t.me/Pumpfun_admin01"),
        InlineKeyboardButton("🔙 Back", callback_data="exclusive_back")
    )
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=markup
    )

def handle_exclusive_majorama(call):
    """Handle PumpFun AMA"""
    chat_id = call.message.chat.id
    
    text = """🎩 PumpFun AMA

Through our livestreams, we are known for live reviews. In our daily livestreams, we offer 3-6 minutes of speaking time for developers. If you want more time to present your project and have the full spotlight, we offer our Exclusive PumpFun AMA. Here, we give both our community and yours a fully transparent insight. For smart investors, an AMA is a highly effective decision-making tool. You can also reuse the video recording later to introduce your project to new investors.

✅ Members @PumpFunTrending: +105.000
✅ Members @PumpFunCommunityChat: +60.000
✅ Expected AMA Listener: 300 - 500
✅ Duration: 30 - 45 minutes
✅ Giveaways: $100-$200 (paid by us)

⭐️ Book 24h trending and get a free dedicated AMA!"""

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📞 Contact", url="https://t.me/Pumpfun_admin01"),
        InlineKeyboardButton("🔙 Back", callback_data="exclusive_back")
    )
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=markup
    )


def handle_exclusive_back(call):
    """Handle back button in exclusive ads flow"""
    chat_id = call.message.chat.id
    
    from menu import start_message
    bot.delete_message(chat_id, call.message.message_id)
    start_message(call.message)
