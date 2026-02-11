from .config import hashids

def encode_id(id: int) -> str:
    return hashids.encode(id)

def decode_code(code: str) -> int:
    decoded = hashids.decode(code)
    if not decoded:
        raise ValueError("Invalid short URL")
    return decoded[0]
