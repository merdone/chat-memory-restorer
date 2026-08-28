import datetime

import telethon
from dotenv import load_dotenv
from os import getenv
from telethon import TelegramClient
from datetime import datetime

from metadata_processing import *

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


async def process_downloading(message: telethon.types.Message, processed_dict: dict) -> str | None:
    if processed_dict.get("downloadable"):
        chat_id = str(processed_dict.get("chat_id"))
        correct_date = datetime.now()

        if processed_dict.get("media_date"):
            correct_date = processed_dict.get("media_date")
        else:
            correct_date = processed_dict.get("message_send_date")

        filename = await generate_file_name(correct_date)
        filepath = pathlib.Path().resolve() / chat_id / filename

        downloaded_path = await message.download_media(file=filepath)

        if processed_dict.get("media_type") in ("photo", "round"):
            set_metadata_date(downloaded_path, correct_date)

        elif processed_dict.get("media_type") in ("document", "video"):
            metadata = get_metadata_date(downloaded_path)
            correct_date = get_min_date(metadata, correct_date)
            set_metadata_date(downloaded_path, correct_date)
        else:
            # process voice metadata
            pass
        return downloaded_path
    return None


async def main():
    # min_id, от старых к новому
    # read_message = await client.get_messages(911873858, limit=None, reverse=True)
    # print(read_message[-1].stringify())
    # message_dict = await process_message(read_message[-1])
    # print(await process_downloading(read_message[-1], message_dict))
    # path = await read_message[-1].download_media()
    # print('File saved to', path)

    async for message in client.iter_messages(911873858, reverse=True, limit=None):
        processed_dict = await process_message(message)
        await process_downloading(message, processed_dict)

    # dialogs = await client.get_dialogs()
    # async for dialog in client.iter_dialogs():
    #     print(dialog.name, 'has ID', dialog.id)


with client:
    client.loop.run_until_complete(main())
