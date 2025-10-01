Telegram Multi-Channel Forwarder 🚀

The Telegram Multi-Channel Forwarder is a Python-based tool developed by Valaboju Charan. It allows you to automatically forward messages from multiple Telegram groups or channels to your chosen destination channels. You can filter messages using keywords so only the content you care about gets forwarded.

This bot is simple, fast, and works with both groups and channels.

✨ Features

🔄 Forward messages from multiple source channels/groups to a single or multiple destination channels.

🔑 Filter messages using case-insensitive keywords.

✅ Supports both groups and public/private channels.

⚡ Lightweight and easy to configure.

⚙️ How It Works

The script uses the Telethon library to interact with the Telegram API.

Authenticate using your Telegram API ID, API Hash, and Phone Number.

Select which chats to monitor.

The script continuously listens for new messages in your chosen sources.

If a message contains the specified keywords, it gets forwarded to your destination channel.

🔑 Keywords

Add one or more keywords (comma-separated).

Keywords are not case-sensitive.

Example: If you set ["deal", "offer"], then messages containing deal, DEAL, Offer, etc. will be forwarded.

🚀 Setup & Usage
1. Clone the Repository
git clone https://github.com/ValabojuCharan0567/telegram-multi-channel-forwarder.git
cd telegram-multi-channel-forwarder

2. Install Dependencies
pip install -r requirements.txt

3. Configure

Open TelegramForwarder.py.

Replace these with your details:

api_id = "YOUR_API_ID"
api_hash = "YOUR_API_HASH"
phone = "+91XXXXXXXXXX"  # Your phone number with country code


Add your source channels, destination channel, and keywords inside the script.

4. Run
python TelegramForwarder.py

5. Options

List Chats → Shows all your chats so you can get their IDs.

Forward Messages → Start forwarding messages based on your rules.

📌 Notes

Keep your API credentials private.

Make sure you have permission to read/forward from the channels.

You can run this bot 24/7 using a free service like Render, Railway, or Heroku so you don’t need to keep your laptop on.

👨‍💻 Author

Created with ❤️ by Valaboju Charan
🌐 GitHub: ValabojuCharan0567
