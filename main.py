import telethon
from dotenv import load_dotenv
from os import getenv
from telethon import TelegramClient

load_dotenv()

api_id = int(getenv("api_id"))
api_hash = getenv("api_hash")
phone_number = getenv("phone_number")
account_password = getenv("account_password")
client = TelegramClient('anon', api_id, api_hash)
# client.start(phone=phone_number, password=account_password)

async def process_photo(message):
    print("processing photo")
    message_id = message.id
    message_send_date = message.date

    message_media_photo = message.media.photo
    photo_date = message_send_date.date()

    return message_id, message_send_date, photo_date

async def process_document(message):
    print("processing document")
    message_id = message.id
    message_send_date = message.date

    message_media_document = message.media.document
    document_date = message_media_document.date()

async def process_message(message):
    pass

async def main():
    # min_id, от старых к новому
    read_message = await client.get_messages(911873858, limit=None, reverse=True)

    print(read_message[-1].stringify())

    if (read_message[-1].media):
        pass
    else:
        print("it's not a photo/document")

    if (isinstance(read_message[-1].media, telethon.types.MessageMediaPhoto)):
        print(await process_photo(read_message[-1]))
    elif(isinstance(read_message[-1].media, telethon.types.MessageMediaDocument) and read_message[-1].media.video):
        print("VIDEO")

    path = await read_message[-1].download_media()
    print('File saved to', path)  # printed after download is done

    # async for message in client.iter_messages(911873858, reverse=True):
    #     print(message.id, message.text)

    # dialogs = await client.get_dialogs()
    #print(dialogs[0].stringify())
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