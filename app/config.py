from dotenv import load_dotenv
from os import getenv

from app.models import Config

load_dotenv()

api_id = int(getenv("api_id"))
api_hash = getenv("api_hash")
phone_number = getenv("phone_number")
account_password = getenv("account_password")

config = Config(api_id, api_hash, phone_number, account_password)
