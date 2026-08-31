# Memory Restorer
Memory Restorer is a Python application for downloading media from Telegram chats, restoring file timestamps, organizing files into folders, and preventing duplicate downloads.

> The project is primarily developed and tested on Windows.

## Main Features
- Downloads media from Telegram chats
- Supports photos, videos, video messages, voice messages, and documents
- Restores media metadata using ExifTool
- Organizes files by:
  - chat
  - media type
  - year, month, or full date
- Detects duplicate files using SHA-256
- Stores information about chats, messages, and downloaded files in SQLite
- Continues downloading from the last processed message
- Allows selecting which media types should be downloaded

## Tech Stack
- Python 3.13+
- Telethon
- SQLite
- ExifTool
- uv

## Requirements
Before installation, make sure you have:
- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/)
- [ExifTool](https://exiftool.org/)
- Telegram API credentials from [my.telegram.org](https://my.telegram.org/)

## Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/merdone/chat-memory-restorer
   cd chat-memory-restorer
    ```
    
2. **Install dependencies:**
Make sure you have `uv` installed. Then, sync the environment:
   ```bash
   uv sync
   ```

3. Install ExifTool:
   Download ExifTool from its official website. On Windows, rename the executable to:
   ```text
   exiftool.exe
   ```

4. Create a `.env` file in the project root:
    ```env
   api_id=your_telegram_api_id
   api_hash=your_telegram_api_hash
   phone_number=your_phone_number
   account_password=your_telegram_2fa_password
    ```