from datetime import datetime
import os
import pathlib

from models import SortOptions, SortType, MediaType


class FileStorage:
    def __init__(self, basic_path):
        self._basic_path = basic_path

    @staticmethod
    def build_path(chat_id: int, media_type: MediaType, correct_date: datetime,
                   sort_options: SortOptions) -> pathlib.Path:
        sort_type = sort_options.sort_type
        sort_by_chat_id = sort_options.sort_by_chat_id
        sort_by_media_type = sort_options.sort_by_media_type

        chat_id = str(chat_id)

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

    def get_basic_path(self):
        return self._basic_path

    def replace_file(self, downloaded_path, additional_path):
        saved_filename = pathlib.Path(downloaded_path).name
        full_directory = self._basic_path / additional_path

        if not os.path.isdir(full_directory):
            os.makedirs(full_directory, exist_ok=True)

        full_file_path = full_directory / saved_filename
        os.replace(downloaded_path, full_file_path)

        return full_file_path
