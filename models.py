from enum import StrEnum
from dataclasses import dataclass

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

    def is_allowed(self, media_type: MediaType) -> bool:
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
