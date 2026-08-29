import os
from dataclasses import dataclass

import telethon
from dotenv import load_dotenv
from os import getenv

from telethon import TelegramClient
from datetime import datetime

import pathlib

from enum import StrEnum

from metadata_processing import *

load_dotenv()

api_id = int(getenv("api_id"))
api_hash = getenv("api_hash")
phone_number = getenv("phone_number")
account_password = getenv("account_password")
client = TelegramClient('anon', api_id, api_hash)


# client.start(phone=phone_number, password=account_password)

class MediaType(StrEnum):
    UNKNOWN = "unknown"
    VOICE = "voice"
    ROUND = "round"
    VIDEO = "video"
    DOCUMENT = "document"
    PHOTO = "photo"
    TEXT = "text"


class SortType(StrEnum):
    NONE = "none"
    YEAR = "year"
    YEAR_MONTH = "year_month"
    FULL_DATE = "full_date"


class SortOptions:
    def __init__(self, sort_type: SortType, sort_by_chat_id: bool, sort_by_media_type: bool):
        self.sort_type = sort_type
        self.sort_by_chat_id = sort_by_chat_id
        self.sort_by_media_type = sort_by_media_type


@dataclass(frozen=True)
class DownloadOptions:
    allowed_media_types: frozenset[MediaType]

    def allow(self, media_type: MediaType) -> bool:
        return media_type in self.allowed_media_types

    @classmethod
    def only(cls, *allowed_types: MediaType):
        return cls(allowed_media_types=frozenset(allowed_types))

    @classmethod
    def allow_all(cls):
        return cls(allowed_media_types=frozenset(MediaType))

    @classmethod
    def allow_none(cls):
        return cls(allowed_media_types=frozenset())


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


async def process_downloading(message: telethon.types.Message, processed_dict: dict,
                              sort_options: SortOptions, options: DownloadOptions) -> str | None:
    downloaded_path = None
    if processed_dict.get("downloadable") and options.allow(processed_dict.get("media_type")):
        correct_date = datetime.now()

        if processed_dict.get("media_date"):
            correct_date = processed_dict.get("media_date")
        else:
            correct_date = processed_dict.get("message_send_date")

        filename = await generate_file_name(correct_date)
        basic_path = pathlib.Path() / "data"
        temporary_path = basic_path / filename

        media_type = processed_dict.get("media_type")

        if media_type != MediaType.UNKNOWN:
            downloaded_path = await message.download_media(file=temporary_path)

        saved_filename = pathlib.Path(downloaded_path).name

        match media_type:
            case MediaType.PHOTO | MediaType.ROUND:
                set_metadata_date(downloaded_path, correct_date)
                set_metadata_windows_date(downloaded_path, correct_date)
            case MediaType.DOCUMENT | MediaType.VIDEO:
                metadata = get_metadata_date(downloaded_path)
                correct_date = get_min_date(metadata, correct_date)
                set_metadata_date(downloaded_path, correct_date)
                set_metadata_windows_date(downloaded_path, correct_date)
            case MediaType.VOICE:
                set_metadata_windows_date(downloaded_path, correct_date)

        additional_path = build_path(processed_dict, correct_date, sort_options)
        full_directory = basic_path / additional_path
        if not os.path.isdir(full_directory):
            os.makedirs(full_directory, exist_ok=True)

        full_file_path = full_directory / saved_filename
        os.replace(downloaded_path, full_file_path)
    return downloaded_path


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

    #options = DownloadOptions.allow_all()
    options = DownloadOptions.only(
        MediaType.VIDEO,
        MediaType.PHOTO,
    )
    # options = DownloadOptions.allow_none()
    sort_options = SortOptions(SortType.YEAR, True, True)
    async for message in client.iter_messages(911873858, reverse=True, limit=100):
        processed_dict = await process_message(message)
        await process_downloading(message, processed_dict, sort_options, options)

    # dialogs = await client.get_dialogs()
    # async for dialog in client.iter_dialogs():
    #     print(dialog.name, 'has ID', dialog.id)


with client:
    client.loop.run_until_complete(main())
