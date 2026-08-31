import os

import telethon
from telethon import TelegramClient
from datetime import datetime

from database import Database
from metadata_processing import process_metadata_changes
from models import MessageInfo, SortOptions, DownloadOptions, MediaType, Config
from storage import FileStorage
from utils import get_sha256_hash, generate_file_name


class ArchiveService:
    def __init__(self, config: Config, database: Database, file_storage: FileStorage):
        self.database = database
        self.file_storage = file_storage
        self.config = config

        self.client = TelegramClient('anon', config.api_id, config.api_hash)

    async def start(self):
        await self.client.start(phone=self.config.phone_number, password=self.config.account_password)

    @staticmethod
    def process_message(message: telethon.types.Message) -> MessageInfo:
        chat_id = message.peer_id.user_id

        message_id = message.id
        message_send_date = message.date

        media_date = None
        downloadable = False
        media_type = MediaType.UNKNOWN

        if message.media:
            message_media = message.media
            try:
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
            except (AttributeError, ValueError):
                media_type = MediaType.UNKNOWN
            if media_type != MediaType.UNKNOWN:
                downloadable = True
        else:
            media_type = MediaType.TEXT
        return MessageInfo(chat_id, message_id, media_type, message_send_date, media_date, downloadable)

    async def message_pipeline(self, message: telethon.types.Message, database: Database,
                               sort_options: SortOptions, download_options: DownloadOptions):
        message_info = self.process_message(message)

        media_type = message_info.media_type
        downloadable = message_info.downloadable

        last_date_from_message = self.get_last_date_from_message_data(message_info)

        allowed_to_download = download_options.is_allowed(media_type)
        if downloadable and allowed_to_download:
            chat_id = message_info.chat_id
            message_id = message_info.message_id
            message_send_date = message_info.message_send_date

            downloaded_path = await self.download_message(message, last_date_from_message)

            source_hash = get_sha256_hash(downloaded_path)
            database_path = database.get_media_file_by_hash(source_hash)

            # update date if it's older
            if database_path is None:
                final_date = process_metadata_changes(downloaded_path, media_type, last_date_from_message)
                additional_path = self.file_storage.build_path(chat_id, media_type, final_date, sort_options)
                saved_filepath = self.file_storage.replace_file(downloaded_path, additional_path)
                database.add_media_file(source_hash, final_date, str(saved_filepath))  # date
            else:
                os.remove(downloaded_path)

            database.add_message(message_id, media_type, source_hash, message_send_date, chat_id)

    @staticmethod
    def get_last_date_from_message_data(message_info: MessageInfo):
        if message_info.media_date:
            last_date_from_message = message_info.media_date
        else:
            last_date_from_message = message_info.message_send_date
        return last_date_from_message

    async def process_chat(self, chat_id: int, sort_options: SortOptions, download_options: DownloadOptions):
        last_id = self.database.get_max_message_id(chat_id) or 0
        async for message in self.client.iter_messages(chat_id, reverse=True, limit=None, min_id=last_id):
            await self.message_pipeline(message, self.database, sort_options, download_options)

    async def download_message(self, message: telethon.types.Message, last_date_from_message: datetime) -> str | None:
        filename = generate_file_name(last_date_from_message)
        temporary_path = self.file_storage.get_basic_path() / filename
        downloaded_path = await message.download_media(file=temporary_path)
        return downloaded_path

    def __del__(self):
        self.database.close()
