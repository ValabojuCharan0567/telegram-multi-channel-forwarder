import time
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

        # Get a list of all the dialogs (chats)
        dialogs = await self.client.get_dialogs()
        chats_file = open(f"chats_of_{self.phone_number}.txt", "w", encoding="utf-8")

        for dialog in dialogs:
            print(f"Chat ID: {dialog.id}, Title: {dialog.title}")
            chats_file.write(f"Chat ID: {dialog.id}, Title: {dialog.title}\n")

        chats_file.close()
        print("✅ List of groups printed successfully!")

    async def forward_messages_to_channel(self, source_chat_id, destination_channel_id, keywords):
        await self.client.connect()

        # Ensure you're authorized
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Enter the code: '))

        last_message = await self.client.get_messages(source_chat_id, limit=1)
        last_message_id = last_message[0].id if last_message else 0

        print(f"🔍 Monitoring chat {source_chat_id} → forwarding to {destination_channel_id}")

        while True:
            messages = await self.client.get_messages(source_chat_id, min_id=last_message_id, limit=None)

            for message in reversed(messages):
                if message.text:
                    if keywords:
                        if any(keyword in message.text.lower() for keyword in keywords):
                            await self.client.send_message(destination_channel_id, message.text)
                            print(f"✅ Forwarded from {source_chat_id}: {message.text[:50]}")
                    else:
                        await self.client.send_message(destination_channel_id, message.text)
                        print(f"✅ Forwarded from {source_chat_id}: {message.text[:50]}")

                last_message_id = max(last_message_id, message.id)

            await asyncio.sleep(5)  # check every 5 seconds


# Function to read credentials from file
def read_credentials():
    try:
        with open("credentials.txt", "r") as file:
            lines = file.readlines()
            api_id = lines[0].strip()
            api_hash = lines[1].strip()
            phone_number = lines[2].strip()
            return api_id, api_hash, phone_number
    except FileNotFoundError:
        print("⚠️ Credentials file not found.")
        return None, None, None

# Function to write credentials to file
def write_credentials(api_id, api_hash, phone_number):
    with open("credentials.txt", "w") as file:
        file.write(api_id + "\n")
        file.write(api_hash + "\n")
        file.write(phone_number + "\n")

async def main():
    # Attempt to read credentials from file
    api_id, api_hash, phone_number = read_credentials()

    # If credentials not found in file, prompt the user to input them
    if api_id is None or api_hash is None or phone_number is None:
        api_id = input("Enter your API ID: ")
        api_hash = input("Enter your API Hash: ")
        phone_number = input("Enter your phone number (with country code, e.g., +9180xxxxxxx): ")
        write_credentials(api_id, api_hash, phone_number)

    forwarder = TelegramForwarder(api_id, api_hash, phone_number)
    
    print("\nChoose an option:")
    print("1. List Chats")
    print("2. Forward Messages")
    
    choice = input("Enter your choice: ")
    
    if choice == "1":
        await forwarder.list_chats()
    elif choice == "2":
        source_chat_ids = input("Enter the source chat IDs (comma separated): ").split(",")
        source_chat_ids = [int(chat.strip()) for chat in source_chat_ids]

        destination_channel_id = int(input("Enter the destination chat ID: "))

        print("Enter keywords if you want to forward messages with specific keywords, or leave blank to forward every message!")
        keywords = input("Put keywords (comma separated if multiple, or leave blank): ").split(",")
        keywords = [kw.strip().lower() for kw in keywords if kw.strip()]

        # Create async tasks for all source chats
        tasks = []
        for source_chat_id in source_chat_ids:
            tasks.append(asyncio.create_task(
                forwarder.forward_messages_to_channel(source_chat_id, destination_channel_id, keywords)
            ))

        # Keep running all tasks
        await asyncio.gather(*tasks)
    else:
        print("❌ Invalid choice")

# Start the event loop and run the main function
if __name__ == "__main__":
    asyncio.run(main())

