import asyncio
from telethon import TelegramClient, errors

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
        """Forward messages from source chats to a destination channel/bot/group with optional keyword filtering."""
        await self.authorize()
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
                    messages = await self.client.get_messages(chat_id, min_id=last_message_ids[chat_id], limit=20)
                except Exception as e:
                    print(f"❌ Failed to fetch messages from {chat_id}: {e}")
                    continue

                for message in reversed(messages):
                    if message.text:
                        text_lower = message.text.lower()
                        if not keywords or any(keyword in text_lower for keyword in keywords):
                            try:
                                await self.client.send_message(destination_entity, message.text)
                                print(f"✅ Forwarded from {chat_id}: {message.text[:50]}")
                            except Exception as e:
                                print(f"❌ Failed to forward message: {e}")

                if messages:
                    last_message_ids[chat_id] = messages[0].id

            await asyncio.sleep(5)

# ----------------------- Settings ----------------------- #
API_ID = 26531485
API_HASH = "7ae9b39f4acdc709219b8ef1f073d067"
PHONE_NUMBER = "+918074526151"

SOURCE_CHAT_IDS = [-1001422047391, -1001670336143, -1001865098968, -1001389782464]

# Destination is your bot username
DESTINATION_CHAT = '@ExtraPeBot'

KEYWORDS = []  # Leave empty to forward all messages, or add lowercase keywords like ['deal', 'offer']

# ------------------------------------------------------------------- #

async def main():
    forwarder = TelegramForwarder(API_ID, API_HASH, PHONE_NUMBER)
    await forwarder.forward_messages_to_channel(SOURCE_CHAT_IDS, DESTINATION_CHAT, KEYWORDS)

if __name__ == "__main__":
    asyncio.run(main())
