from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..config import BASE_URL
from ..database import SessionLocal
from ..schemas import URLCreate, URLResponse
from ..services.url_service import (
    get_or_create_short_code,
    get_original_url_by_code,
)


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/shorten", response_model=URLResponse)
def shorten_url(payload: URLCreate, db: Session = Depends(get_db)):
    """
    Endpoint de encurtamento de URLs.

    Atua como "Controller" chamando a camada de serviço.
    """
    url_str = str(payload.url)

    code = get_or_create_short_code(db, url_str)
    short_url = f"{BASE_URL}/{code}"

    return {"short_url": short_url}


@router.get("/{code}")
def redirect(code: str, db: Session = Depends(get_db)):
    """
    Endpoint de resolução de código curto para redirecionar.
    """
    try:
        original_url = get_original_url_by_code(db, code)
    except ValueError:
        raise HTTPException(status_code=404, detail="URL not found")

    return RedirectResponse(original_url)

