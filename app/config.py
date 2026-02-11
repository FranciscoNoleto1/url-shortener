import os
from dotenv import load_dotenv
from hashids import Hashids

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
HASH_SALT = os.getenv("HASH_SALT", "my_secret_key_dev_only")
HASH_MIN_LENGTH = 7
HASH_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

hashids = Hashids(
    salt=HASH_SALT,
    min_length=HASH_MIN_LENGTH,
    alphabet=HASH_ALPHABET
)
