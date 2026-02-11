from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .config import BASE_URL
from .database import SessionLocal, engine
from .models import Base, URL
from .schemas import URLCreate, URLResponse
from .shortener import encode_id, decode_code

Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/shorten", response_model=URLResponse)
def shorten_url(payload: URLCreate, db: Session = Depends(get_db)):
    url_str = str(payload.url)
    existing = db.query(URL).filter(URL.original_url == url_str).first()

    if existing:
        code = encode_id(existing.id)
        return {"short_url": f"{BASE_URL}/{code}"}

    url = URL(original_url=url_str)
    db.add(url)
    db.commit()
    db.refresh(url)

    code = encode_id(url.id)
    return {"short_url": f"{BASE_URL}/{code}"}


@app.get("/{code}")
def redirect(code: str, db: Session = Depends(get_db)):
    try:
        url_id = decode_code(code)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid URL")

    url = db.query(URL).filter(URL.id == url_id).first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    return RedirectResponse(url.original_url)
