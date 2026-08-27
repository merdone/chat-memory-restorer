import telethon
from dotenv import load_dotenv
from os import getenv
from telethon import TelegramClient
import random
import pathlib
import string

load_dotenv()

api_id = int(getenv("api_id"))
api_hash = getenv("api_hash")
phone_number = getenv("phone_number")
account_password = getenv("account_password")
client = TelegramClient('anon', api_id, api_hash)


# client.start(phone=phone_number, password=account_password)

async def process_message(message: telethon.types.Message) -> dict | None:
    chat_id = message.peer_id.user_id

    message_id = message.id
    message_send_date = message.date

    media_date = None
    downloadable = False
    media_type = "unknown"

    if message.media:
        message_media = message.media
        if isinstance(message_media, telethon.types.MessageMediaDocument):
            if message_media.voice:
                media_type = "voice"
            elif message_media.round:
                media_type = "round"
            elif message.media.video:
                media_type = "video"
            else:
                media_type = "document"
            document = message_media.document
            media_date = document.date
        elif isinstance(message_media, telethon.types.MessageMediaPhoto):
            media_type = "photo"
            photo = message_media.photo
            media_date = photo.date
        downloadable = True
    else:
        media_type = "text"

    return {"chat_id": chat_id,
            "message_id": message_id,
            "media_type": media_type,
            "message_send_date": message_send_date,
            "media_date": media_date,
            "downloadable": downloadable}

async def generate_name(date) -> str:
    random_part = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=10))
    return date.strftime('%d_%m_%Y_') + random_part


async def process_downloading(message, processed_dict):
    if processed_dict.get("downloadable"):
        chat_id = str(processed_dict.get("chat_id"))
        # process metadata changing
        if processed_dict.get("media_date"):
            # set this to metadate
            filename = await generate_name(processed_dict.get("media_date"))

            path = pathlib.Path().resolve() / chat_id /filename

            await message.download_media(file=path)



async def main():
    # min_id, от старых к новому
    read_message = await client.get_messages(911873858, limit=None, reverse=True)

    # print(read_message[-1].stringify())
    a = await process_message(read_message[-1])
    print(a)

    print("")
    await process_downloading(read_message[-1], a)
    # path = await read_message[-1].download_media()
    # print('File saved to', path)  # printed after download is done

    # async for message in client.iter_messages(911873858, reverse=True):
    #     print(message.id, message.text)

    # dialogs = await client.get_dialogs()
    # print(dialogs[0].stringify())
    # print(read_message[0].message )

    # async for dialog in client.iter_dialogs():
    #     print(dialog.name, 'has ID', dialog.id)
    #
    #
    # # You can, of course, use markdown in your messages:
    # message = await client.send_message(
    #     'me',
    #     'This message has **bold**, `code`, __italics__ and '
    #     'a [nice website](https://example.com)!',
    #     link_preview=False
    # )
    #
    # # Sending a message returns the sent message object, which you can use
    # print(message.id)
    #
    # # You can reply to messages directly if you have a message object
    # await message.reply('Cool!')
    #
    # # Or send files, songs, documents, albums...
    # await client.send_file('me', '/home/me/Pictures/holidays.jpg')
    #
    # # You can print the message history of any chat:
    # async for message in client.iter_messages('me'):
    #     print(message.id, message.text)
    #
    #     # You can download media from messages, too!
    #     # The method will return the path where the file was saved.
    #     if message.photo:
    #         path = await message.download_media()
    #         print('File saved to', path)  # printed after download is done


with client:
    client.loop.run_until_complete(main())
    # client.run_until_disconnected()
