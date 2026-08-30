import datetime
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


@dataclass(frozen=True)
class MessageInfo:
    chat_id: int
    message_id: int
    media_type: MediaType
    message_send_date: datetime.datetime
    media_date: datetime.datetime | None
    downloadable: bool


@dataclass(frozen=True)
class SortOptions:
    sort_type: SortType
    sort_by_chat_id: bool
    sort_by_media_type: bool


@dataclass(frozen=True)
class Config:
    api_id: int
    api_hash: str
    phone_number: str
    account_password: str


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
