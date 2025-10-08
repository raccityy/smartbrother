"""
Standardized project details formatter for consistent display across all bot modules
"""
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot_instance import bot
import requests

def fetch_project_details_from_dexscreener(contract_address):
    """
    Fetch comprehensive project details from DexScreener API
    
    Returns:
        dict: Project details including token info, price, market data, etc.
    """
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
            
            return {
                'found': True,
                'token_name': token_name,
                'token_symbol': token_symbol,
                'price_usd': price_usd,
                'market_cap': market_cap,
                'volume_24h': volume_24h,
                'liquidity_usd': liquidity_usd,
                'dex_id': dex_id,
                'chain_id': chain_id,
                'price_formatted': price_formatted,
                'market_cap_formatted': market_cap_formatted,
                'volume_formatted': volume_formatted,
                'liquidity_formatted': liquidity_formatted,
                'contract_address': contract_address
            }
        else:
            return {
                'found': False,
                'token_name': 'Unknown Token',
                'token_symbol': 'UNKNOWN',
                'contract_address': contract_address,
                'status': 'Not listed on DexScreener'
            }
    except Exception:
        return {
            'found': False,
            'token_name': 'Unknown Token',
            'token_symbol': 'UNKNOWN',
            'contract_address': contract_address,
            'status': 'Error fetching from DexScreener'
        }

def format_project_details_message(project_data, show_confirm_buttons=True, confirm_callback=None, back_callback=None):
    """
    Format project details message with standardized layout
    
    Args:
        project_data: Dictionary containing project details
        show_confirm_buttons: Whether to show confirm/back buttons
        confirm_callback: Callback data for confirm button
        back_callback: Callback data for back button
    
    Returns:
        tuple: (formatted_text, markup)
    """
    contract_address = project_data['contract_address']
    token_name = project_data['token_name']
    token_symbol = project_data['token_symbol']
    
    if project_data['found']:
        # Project found on DexScreener
        text = f"""📄 <b>Project Details Found!</b>

✅ <b>Contract Address:</b> <code>{contract_address}</code>

📊 <b>Token Information:</b>
• <b>Name:</b> {token_name}
• <b>Symbol:</b> {token_symbol}
• <b>Price:</b> {project_data['price_formatted']}
• <b>Market Cap:</b> {project_data['market_cap_formatted']}
• <b>24h Volume:</b> {project_data['volume_formatted']}
• <b>Liquidity:</b> {project_data['liquidity_formatted']}
• <b>DEX:</b> {project_data['dex_id']}
• <b>Chain:</b> {project_data['chain_id']}

Please confirm these project details are correct before proceeding."""
    else:
        # Project not found or error
        status_msg = project_data.get('status', 'Unknown status')
        text = f"""⚠️ <b>Project Details</b>

✅ <b>Contract Address:</b> <code>{contract_address}</code>

📊 <b>Token Information:</b>
• <b>Name:</b> {token_name}
• <b>Symbol:</b> {token_symbol}
• <b>Status:</b> {status_msg}

The contract address is valid but the token details could not be fetched from DexScreener. You can still proceed with the order."""
    
    markup = None
    if show_confirm_buttons and confirm_callback and back_callback:
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✅ Confirm & Continue", callback_data=confirm_callback),
            InlineKeyboardButton("🔙 Back", callback_data=back_callback)
        )
    
    return text, markup

def send_project_details_confirmation(chat_id, contract_address, confirm_callback, back_callback, parse_mode="HTML"):
    """
    Send standardized project details confirmation message
    
    Args:
        chat_id: Telegram chat ID
        contract_address: Contract address to fetch details for
        confirm_callback: Callback data for confirm button
        back_callback: Callback data for back button
        parse_mode: Message parse mode (HTML or Markdown)
    """
    # Fetch project details
    project_data = fetch_project_details_from_dexscreener(contract_address)
    
    # Format message
    text, markup = format_project_details_message(
        project_data, 
        show_confirm_buttons=True,
        confirm_callback=confirm_callback,
        back_callback=back_callback
    )
    
    # Send message
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode=parse_mode)
    
    return project_data

def format_payment_summary_with_project_details(project_data, order_details):
    """
    Format payment summary with project details included
    
    Args:
        project_data: Dictionary containing project details
        order_details: Dictionary containing order information (price, duration, etc.)
    
    Returns:
        str: Formatted payment summary text
    """
    contract_address = project_data['contract_address']
    token_name = project_data['token_name']
    token_symbol = project_data['token_symbol']
    
    # Order details
    price = order_details.get('price', 'N/A')
    duration = order_details.get('duration', 'N/A')
    start_date = order_details.get('start_date', 'N/A')
    telegram_address = order_details.get('telegram_address', 'N/A')
    sol_amount = order_details.get('sol_amount', 'N/A')
    
    # Format start date if it's a datetime object
    if hasattr(start_date, 'strftime'):
        start_date_str = start_date.strftime("%A, %d %B %Y")
    else:
        start_date_str = str(start_date)
    
    if project_data['found']:
        # Project found on DexScreener - show full details
        text = f"""⚙️ One last Step: Payment Required

Thank you for providing your project details. Please complete the payment within the next 15 minutes.

🔥 <b>Order Summary</b>

📊 <b>Project Details:</b>
• <b>Token Name:</b> {token_name}
• <b>Symbol:</b> {token_symbol}
• <b>Contract Address:</b> <code>{contract_address}</code>
• <b>Price:</b> {project_data['price_formatted']}
• <b>Market Cap:</b> {project_data['market_cap_formatted']}
• <b>24h Volume:</b> {project_data['volume_formatted']}
• <b>Liquidity:</b> {project_data['liquidity_formatted']}
• <b>DEX:</b> {project_data['dex_id']}
• <b>Chain:</b> {project_data['chain_id']}

📺 <b>Order Details:</b>
• <b>Duration:</b> {duration} Days
• <b>Start Date:</b> {start_date_str}
• <b>Telegram Group:</b> {telegram_address}
• <b>Amount:</b> {sol_amount} SOL (${price})

▶️ Please complete the payment of <b>{sol_amount} SOL</b> to the following wallet address:

<code>{order_details.get('wallet_address', 'N/A')}</code>

Click /sent to verify pending transactions"""
    else:
        # Project not found - show basic details
        text = f"""⚙️ One last Step: Payment Required

Thank you for providing your project details. Please complete the payment within the next 15 minutes.

🔥 <b>Order Summary</b>

📊 <b>Project Details:</b>
• <b>Token Name:</b> {token_name}
• <b>Symbol:</b> {token_symbol}
• <b>Contract Address:</b> <code>{contract_address}</code>
• <b>Status:</b> {project_data.get('status', 'Unknown')}

📺 <b>Order Details:</b>
• <b>Duration:</b> {duration} Days
• <b>Start Date:</b> {start_date_str}
• <b>Telegram Group:</b> {telegram_address}
• <b>Amount:</b> {sol_amount} SOL (${price})

▶️ Please complete the payment of <b>{sol_amount} SOL</b> to the following wallet address:

<code>{order_details.get('wallet_address', 'N/A')}</code>

Click /sent to verify pending transactions"""
    
    return text
