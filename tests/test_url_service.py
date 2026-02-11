from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import URL
from app.services.url_service import (
    get_or_create_short_code,
    get_original_url_by_code,
)
from app.shortener import encode_id


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


def create_test_session():
    """Cria uma sessão de banco em memória para uso nos testes de serviço."""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def test_get_or_create_short_code_creates_new_url():
    db = create_test_session()
    try:
        original_url = "https://example.com/page"

        code = get_or_create_short_code(db, original_url)

        # Deve existir um registro da URL original
        url = db.query(URL).filter_by(original_url=original_url).first()
        assert url is not None
        assert encode_id(url.id) == code
    finally:
        db.close()


def test_get_or_create_short_code_reuses_existing_url():
    db = create_test_session()
    try:
        original_url = "https://example.com/reused"

        # Cria uma URL manualmente
        url = URL(original_url=original_url)
        db.add(url)
        db.commit()
        db.refresh(url)

        first_code = encode_id(url.id)

        # Chama o serviço – deve reutilizar o mesmo código
        code = get_or_create_short_code(db, original_url)

        assert code == first_code
    finally:
        db.close()


def test_get_original_url_by_code_returns_url():
    db = create_test_session()
    try:
        original_url = "https://example.com/original"
        url = URL(original_url=original_url)
        db.add(url)
        db.commit()
        db.refresh(url)

        code = encode_id(url.id)

        resolved_url = get_original_url_by_code(db, code)

        assert resolved_url == original_url
    finally:
        db.close()


def test_get_original_url_by_code_invalid_code_raises_value_error():
    db = create_test_session()
    try:
        # Código que não é decodificável pelo Hashids
        invalid_code = "invalid_code"

        try:
            get_original_url_by_code(db, invalid_code)
            assert False, "Esperava ValueError para código inválido"
        except ValueError:
            # Comportamento esperado
            pass
    finally:
        db.close()


def test_get_original_url_by_code_not_found_raises_value_error():
    db = create_test_session()
    try:
        # Cria e remove um registro para gerar um ID que não existe mais
        url = URL(original_url="https://example.com/to-delete")
        db.add(url)
        db.commit()
        db.refresh(url)

        code = encode_id(url.id)

        # Remove o registro para simular "não encontrado"
        db.delete(url)
        db.commit()

        try:
            get_original_url_by_code(db, code)
            assert False, "Esperava ValueError para URL não encontrada"
        except ValueError:
            # Comportamento esperado
            pass
    finally:
        db.close()

