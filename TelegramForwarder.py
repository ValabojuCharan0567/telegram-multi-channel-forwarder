import asyncio
import json
import logging
from telethon import TelegramClient, errors

# ---------------------- CONFIG ---------------------- #
API_ID = 26531485
API_HASH = "7ae9b39f4acdc709219b8ef1f073d067"
PHONE_NUMBER = "+918074526151"

SOURCE_CHAT_IDS = [-1001422047391, -1001670336143, -1001865098968, -1001389782464]
DESTINATION_CHAT = '@ExtraPeBot'

KEYWORDS = []  # Add lowercase keywords like ['deal', 'offer'], leave empty to forward all
MEDIA_TYPES = ['photo', 'video', 'document']  # Options: 'photo', 'video', 'document', etc.
POLL_INTERVAL = 5  # seconds

LAST_IDS_FILE = "last_ids.json"
LOG_FILE = "forwarder.log"

# ------------------ Logging Setup ------------------ #
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ------------------ Forwarder Class ------------------ #
class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient('session_' + phone_number, api_id, api_hash)

    async def authorize(self):
        """Ensure the client is authorized."""
        await self.client.connect()
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            try:
                await self.client.sign_in(self.phone_number, input('Enter the code: '))
            except errors.SessionPasswordNeededError:
                password = input('Two-step verification is enabled. Enter password: ')
                await self.client.sign_in(password=password)

    async def list_chats(self):
        """List all chats for the authorized account."""
        await self.authorize()
        dialogs = await self.client.get_dialogs()
        print("📜 Available Chats:")
        for dialog in dialogs:
            print(f"Chat ID: {dialog.id}, Title: {dialog.title}")

    async def forward_messages_to_channel(self, source_chat_ids, destination_chat, keywords):
        await self.authorize()

        # Load last forwarded message IDs
        try:
            with open(LAST_IDS_FILE) as f:
                last_message_ids = json.load(f)
                last_message_ids = {int(k): v for k, v in last_message_ids.items()}
        except FileNotFoundError:
            last_message_ids = {chat_id: 0 for chat_id in source_chat_ids}

        # Resolve destination entity
        try:
            destination_entity = await self.client.get_entity(destination_chat)
        except Exception as e:
            print(f"❌ Failed to resolve destination '{destination_chat}': {e}")
            return

        print(f"🔍 Monitoring chats {source_chat_ids} → forwarding to {destination_chat}")

        while True:
            for chat_id in source_chat_ids:
                try:
                    messages = await self.client.get_messages(chat_id, min_id=last_message_ids.get(chat_id, 0), limit=20)
                except Exception as e:
                    print(f"❌ Failed to fetch messages from {chat_id}: {e}")
                    continue

                for message in reversed(messages):
                    # Skip already forwarded messages
                    if message.fwd_from:
                        continue

                    # Forward text messages
                    if message.text:
                        text_lower = message.text.lower()
                        if not keywords or any(keyword in text_lower for keyword in keywords):
                            try:
                                await self.client.send_message(destination_entity, message.text)
                                logging.info(f"Forwarded text from {chat_id}: {message.text[:50]}")
                                print(f"✅ Forwarded text from {chat_id}: {message.text[:50]}")
                            except Exception as e:
                                logging.error(f"Failed to forward text message: {e}")
                                print(f"❌ Failed to forward text message: {e}")

                    # Forward media messages with optional filtering
                    if message.media:
                        media_type = None
                        if message.photo:
                            media_type = 'photo'
                        elif message.video:
                            media_type = 'video'
                        elif message.document:
                            media_type = 'document'

                        if media_type and media_type in MEDIA_TYPES:
                            caption = message.text or ""
                            if not keywords or any(keyword in caption.lower() for keyword in keywords):
                                try:
                                    await self.client.send_file(destination_entity, message.media, caption=caption)
                                    logging.info(f"Forwarded media ({media_type}) from {chat_id}")
                                    print(f"✅ Forwarded media ({media_type}) from {chat_id}")
                                except Exception as e:
                                    logging.error(f"Failed to forward media: {e}")
                                    print(f"❌ Failed to forward media: {e}")

                if messages:
                    last_message_ids[chat_id] = messages[0].id

            # Save last message IDs persistently
            with open(LAST_IDS_FILE, "w") as f:
                json.dump(last_message_ids, f)

            await asyncio.sleep(POLL_INTERVAL)

# ------------------------ Main ------------------------ #
async def main():
    forwarder = TelegramForwarder(API_ID, API_HASH, PHONE_NUMBER)
    await forwarder.forward_messages_to_channel(SOURCE_CHAT_IDS, DESTINATION_CHAT, KEYWORDS)

if __name__ == "__main__":
    asyncio.run(main())
