from exiftool import ExifToolHelper
import pathlib
from datetime import datetime
from exiftool.exceptions import ExifToolExecuteError

from app.models import MediaType
from app.utils import formate_date_to_iso, formate_date_for_windows, string_to_datetime, get_min_date, convert_timezones

path = pathlib.Path().resolve() / "tools" / "exiftool.exe"


# setting fields EXIF:DateTimeOriginal, EXIF:CreateDate, EXIF:ModifyDate, XMP:CreateDate,
# XMP:ModifyDate, XMP:DateCreated, QuickTime:CreateDate, QuickTime:ModifyDate
# which are important for all systems(Android, Apple, etc.)
def set_metadata_date(image_path, date):
    with ExifToolHelper(executable=path) as et:
        iso_date = formate_date_to_iso(date)
        try:
            et.set_tags(
                image_path,
                tags={
                    "EXIF:DateTimeOriginal": iso_date,
                    "EXIF:CreateDate": iso_date,
                    "EXIF:ModifyDate": iso_date,
                    "XMP:CreateDate": iso_date,
                    "XMP:ModifyDate": iso_date,
                    "XMP:DateCreated": iso_date,
                    "QuickTime:CreateDate": iso_date,
                    "QuickTime:ModifyDate": iso_date},
                params=["-overwrite_original"]
            )
        except ExifToolExecuteError as error:
            print("STDOUT:", error.stdout)
            print("STDERR:", error.stderr)


# setting fields File:FileCreateDate, File:FileModifyDate which are important for windows explorer
def set_metadata_windows_date(image_path, date):
    with ExifToolHelper(executable=path) as et:
        windows_format_date = formate_date_for_windows(date)
        try:
            et.set_tags(
                image_path,
                tags={
                    "File:FileCreateDate": windows_format_date,
                    "File:FileModifyDate": windows_format_date,
                },
                params=["-overwrite_original"]
            )
        except ExifToolExecuteError as error:
            print("STDOUT:", error.stdout)
            print("STDERR:", error.stderr)


def get_metadata_date(filepath):
    with ExifToolHelper(executable=path) as et:
        metadata_dict = et.get_metadata(filepath)[0]

        exif_createdate = string_to_datetime(metadata_dict.get("EXIF:CreateDate", None))
        exif_modifydate = string_to_datetime(metadata_dict.get("EXIF:ModifyDate", None))
        xmp_createdate = string_to_datetime(metadata_dict.get("XMP:CreateDate", None))
        xmp_modifydate = string_to_datetime(metadata_dict.get("XMP:ModifyDate", None))
        xmp_datecreated = string_to_datetime(metadata_dict.get("XMP:DateCreated", None))
        file_filecreatedate = string_to_datetime(metadata_dict.get("File:FileCreateDate", None))
        file_filemodifydate = string_to_datetime(metadata_dict.get("File:FileModifyDate", None))
        quicktime_createdate = string_to_datetime(metadata_dict.get("QuickTime:CreateDate", None))
        quicktime_modifydate = string_to_datetime(metadata_dict.get("QuickTime:ModifyDate", None))

    date_dict = {"EXIF:CreateDate": exif_createdate,
                 "EXIF:ModifyDate": exif_modifydate,
                 "XMP:CreateDate": xmp_createdate,
                 "XMP:ModifyDate": xmp_modifydate,
                 "XMP:DateCreated": xmp_datecreated,
                 "File:FileCreateDate": file_filecreatedate,
                 "File:FileModifyDate": file_filemodifydate,
                 "QuickTime:CreateDate": quicktime_createdate,
                 "QuickTime:ModifyDate": quicktime_modifydate}

    convert_timezones(date_dict)

    return date_dict


def process_metadata_changes(filepath: str, media_type: MediaType, last_date_from_message: datetime):
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
