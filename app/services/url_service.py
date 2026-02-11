from sqlalchemy.orm import Session

from ..models import URL
from ..shortener import encode_id, decode_code


def get_or_create_short_code(db: Session, original_url: str) -> str:
    """
    Regra de negócio para encurtar uma URL.

    - Se a URL já existir, reaproveita o mesmo código.
    - Caso contrário, cria um novo registro e gera um código curto.
    """
    existing = db.query(URL).filter(URL.original_url == original_url).first()
    if existing:
        return encode_id(existing.id)

    url = URL(original_url=original_url)
    db.add(url)
    db.commit()
    db.refresh(url)

    return encode_id(url.id)


def get_original_url_by_code(db: Session, code: str) -> str:
    """
    Regra de negócio para resolver um código curto em URL original.

    Levanta ValueError se o código for inválido ou não existir.
    """
    try:
        url_id = decode_code(code)
    except ValueError:
        raise

    url = db.query(URL).filter(URL.id == url_id).first()
    if not url:
        raise ValueError("URL not found")

    return url.original_url

