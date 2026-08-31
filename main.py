import pathlib
import asyncio
from telethon import TelegramClient

from app.archive_service import ArchiveService
from app.models import MediaType, SortType, DownloadOptions, SortOptions

from app.database import Database
from app.storage import FileStorage
from app.config import config


async def main():
    test_id = 379805423
    database = Database("test.db")
    database.add_chat(test_id, "test")
    download_options = DownloadOptions.only(
        MediaType.PHOTO,
        MediaType.ROUND,
        MediaType.VOICE,
        MediaType.VIDEO,
    )
    sort_options = SortOptions(sort_type=SortType.YEAR, sort_by_chat_id=True, sort_by_media_type=True)
    file_storage = FileStorage(pathlib.Path() / "data")

    client = TelegramClient('anon', config.api_id, config.api_hash)
    await client.start(phone=config.phone_number, password=config.account_password)

    service = ArchiveService(client, database, file_storage)

    await service.process_chat(test_id, sort_options, download_options)

    database.close()


if __name__ == "__main__":
    asyncio.run(main())
