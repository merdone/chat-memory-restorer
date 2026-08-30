import pathlib
import asyncio

from archive_service import ArchiveService
from models import MediaType, SortType, DownloadOptions, SortOptions

from database import Database
from storage import FileStorage
from config import config


async def main():
    test_id = 911873858
    database = Database("test.db")
    database.add_chat(test_id, "test")
    download_options = DownloadOptions.only(
        MediaType.PHOTO,
        MediaType.ROUND,
        MediaType.VOICE,
        # MediaType.VIDEO,
    )
    sort_options = SortOptions(sort_type=SortType.YEAR, sort_by_chat_id=True, sort_by_media_type=True)
    file_storage = FileStorage(pathlib.Path() / "data")
    service = ArchiveService(config, database, file_storage)

    await service.start()
    await service.process_chat(test_id, sort_options, download_options)

if __name__ == "__main__":
    asyncio.run(main())