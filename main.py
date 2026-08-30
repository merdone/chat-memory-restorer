import os

import telethon
from dotenv import load_dotenv
from os import getenv

from telethon import TelegramClient
from datetime import datetime

import pathlib

from models import MediaType, SortType, DownloadOptions, SortOptions

from database import Database
from metadata_processing import *

load_dotenv()

api_id = int(getenv("api_id"))
api_hash = getenv("api_hash")
phone_number = getenv("phone_number")
account_password = getenv("account_password")
client = TelegramClient('anon', api_id, api_hash)


# client.start(phone=phone_number, password=account_password)


basic_path = pathlib.Path() / "data"


async def process_message(message: telethon.types.Message) -> dict | None:
    chat_id = message.peer_id.user_id

    message_id = message.id
    message_send_date = message.date

    media_date = None
    downloadable = False
    media_type = MediaType.UNKNOWN

    if message.media:
        message_media = message.media
        if isinstance(message_media, telethon.types.MessageMediaDocument):
            if message_media.voice:
                media_type = MediaType.VOICE
            elif message_media.round:
                media_type = MediaType.ROUND
            elif message.media.video:
                media_type = MediaType.VIDEO
            else:
                media_type = MediaType.DOCUMENT
            document = message_media.document
            media_date = document.date
        elif isinstance(message_media, telethon.types.MessageMediaPhoto):
            media_type = MediaType.PHOTO
            photo = message_media.photo
            media_date = photo.date

        if media_type != MediaType.UNKNOWN:
            downloadable = True
    else:
        media_type = MediaType.TEXT

    return {"chat_id": chat_id,
            "message_id": message_id,
            "media_type": media_type,
            "message_send_date": message_send_date,
            "media_date": media_date,
            "downloadable": downloadable}


def build_path(processed_dict: dict, correct_date: datetime, sort_options: SortOptions) -> pathlib.Path:
    sort_type = sort_options.sort_type
    sort_by_chat_id = sort_options.sort_by_chat_id
    sort_by_media_type = sort_options.sort_by_media_type

    chat_id = str(processed_dict.get("chat_id"))
    media_type = processed_dict.get("media_type")

    additional_path = pathlib.Path()

    if sort_by_chat_id:
        additional_path = additional_path / chat_id

    if sort_by_media_type:
        additional_path = additional_path / media_type

    day = str(correct_date.day)
    month = str(correct_date.month)
    year = str(correct_date.year)

    match sort_type:
        case SortType.YEAR:
            additional_path = additional_path / year
        case SortType.YEAR_MONTH:
            additional_path = additional_path / year / month
        case SortType.FULL_DATE:
            additional_path = additional_path / year / month / day

    return additional_path


async def get_last_date_from_message_data(processed_dict: dict):
    last_date_from_message = datetime.now()

    if processed_dict.get("media_date"):
        last_date_from_message = processed_dict.get("media_date")
    else:
        last_date_from_message = processed_dict.get("message_send_date")

    return last_date_from_message


async def download_message(message: telethon.types.Message, last_date_from_message) -> str | None:
    filename = await generate_file_name(last_date_from_message)
    temporary_path = basic_path / filename
    downloaded_path = await message.download_media(file=temporary_path)
    return downloaded_path


async def process_metadata_changes(filepath: str, media_type: MediaType, last_date_from_message):
    match media_type:
        case MediaType.PHOTO | MediaType.ROUND:
            set_metadata_date(filepath, last_date_from_message)
            set_metadata_windows_date(filepath, last_date_from_message)
            return last_date_from_message
        case MediaType.DOCUMENT | MediaType.VIDEO:
            metadata = get_metadata_date(filepath)
            final_last_date = get_min_date(metadata, last_date_from_message)
            set_metadata_date(filepath, final_last_date)
            set_metadata_windows_date(filepath, final_last_date)
            return final_last_date
        case MediaType.VOICE:
            set_metadata_windows_date(filepath, last_date_from_message)
            return last_date_from_message
    return None


async def replace_file(downloaded_path, additional_path):
    saved_filename = pathlib.Path(downloaded_path).name
    full_directory = basic_path / additional_path

    if not os.path.isdir(full_directory):
        os.makedirs(full_directory, exist_ok=True)

    full_file_path = full_directory / saved_filename
    os.replace(downloaded_path, full_file_path)

    return full_file_path


async def message_pipeline(message: telethon.types.Message, database: Database,
                           sort_options: SortOptions, download_options: DownloadOptions):
    processed_dict = await process_message(message)
    chat_id = processed_dict.get("chat_id")
    message_id = processed_dict.get("message_id")
    media_type = processed_dict.get("media_type")
    downloadable = processed_dict.get("downloadable")
    message_send_date = processed_dict.get("message_send_date")

    last_date_from_message = await get_last_date_from_message_data(processed_dict)

    allowed_to_download = download_options.is_allowed(media_type)
    if downloadable and allowed_to_download:
        downloaded_path = await download_message(message, last_date_from_message)

        source_hash = get_sha256_hash(downloaded_path)
        database_path = database.get_media_file_by_hash(source_hash)

        # update date if it's older
        if database_path is None:
            final_date = await process_metadata_changes(downloaded_path, media_type, last_date_from_message)
            additional_path = build_path(processed_dict, final_date, sort_options)
            saved_filepath = await replace_file(downloaded_path, additional_path)
            database.add_media_file(source_hash, final_date, str(saved_filepath))  # date
        else:
            os.remove(downloaded_path)

        database.add_message(message_id, media_type, source_hash, message_send_date, chat_id)


async def main():
    # min_id, от старых к новому
    # read_message = await client.get_messages(911873858, limit=None, reverse=True)
    # print(read_message[-1].stringify())
    # message_dict = await process_message(read_message[-1])
    # print(message_dict)
    # sort_options = SortOptions(SortType.YEAR, True, True)
    # print(await process_downloading(read_message[-1], message_dict, sort_options))
    # path = await read_message[-1].download_media()
    # print('File saved to', path)
    # 1399234159
    test_chat_id = 911873858

    database = Database("test.db")
    database.add_chat(test_chat_id, "test")
    # download_options = DownloadOptions.allow_all()
    # download_options = DownloadOptions.allow_none()
    download_options = DownloadOptions.only(
        # MediaType.VIDEO,
        MediaType.PHOTO,
        MediaType.ROUND,
        MediaType.VOICE
    )

    sort_options = SortOptions(SortType.YEAR, True, True)

    # last_id = database.get_max_message_id(test_chat_id)
    # min_id=last_id,
    async for message in client.iter_messages(test_chat_id, reverse=False, limit=100):
        await message_pipeline(message, database, sort_options, download_options)

    # dialogs = await client.get_dialogs()
    # async for dialog in client.iter_dialogs():
    #     print(dialog.name, 'has ID', dialog.id)


with client:
    client.loop.run_until_complete(main())
