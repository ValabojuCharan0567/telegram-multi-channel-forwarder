import asyncio
from telethon.sync import TelegramClient
from telethon import errors

class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient('session_' + phone_number, api_id, api_hash)

    async def list_chats(self):
        await self.client.connect()

        # Ensure you're authorized
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            try:
                await self.client.sign_in(self.phone_number, input('Enter the code: '))
            except errors.rpcerrorlist.SessionPasswordNeededError:
                password = input('Two-step verification is enabled. Enter your password: ')
                await self.client.sign_in(password=password)

        dialogs = await self.client.get_dialogs()
        for dialog in dialogs:
            print(f"Chat ID: {dialog.id}, Title: {dialog.title}")

    async def forward_messages_to_channel(self, source_chat_ids, destination_channel_id, keywords):
        await self.client.connect()

        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Enter the code: '))

        last_message_ids = {chat_id: 0 for chat_id in source_chat_ids}
        print(f"🔍 Monitoring chats {source_chat_ids} → forwarding to {destination_channel_id}")

        while True:
            for chat_id in source_chat_ids:
                messages = await self.client.get_messages(chat_id, min_id=last_message_ids[chat_id], limit=None)
                for message in reversed(messages):
                    if message.text:
                        if keywords:
                            if any(keyword in message.text.lower() for keyword in keywords):
                                await self.client.send_message(destination_channel_id, message.text)
                                print(f"✅ Forwarded from {chat_id}: {message.text[:50]}")
                        else:
                            await self.client.send_message(destination_channel_id, message.text)
                            print(f"✅ Forwarded from {chat_id}: {message.text[:50]}")
                    last_message_ids[chat_id] = max(last_message_ids[chat_id], message.id)
            await asyncio.sleep(5)

# ----------------------- Predefined Settings ----------------------- #
API_ID = 26531485
API_HASH = "7ae9b39f4acdc709219b8ef1f073d067"
PHONE_NUMBER = "+918074526151"

SOURCE_CHAT_IDS = [-1001422047391, -1001670336143, -1001865098968]  # List of source chat IDs
DESTINATION_CHAT_ID = 2015117555  # Destination chat ID
KEYWORDS = []  # Leave empty to forward all messages, or add keywords in lowercase ['deal', 'offer']

# ------------------------------------------------------------------- #

async def main():
    forwarder = TelegramForwarder(API_ID, API_HASH, PHONE_NUMBER)
    await forwarder.forward_messages_to_channel(SOURCE_CHAT_IDS, DESTINATION_CHAT_ID, KEYWORDS)

if __name__ == "__main__":
    asyncio.run(main())
