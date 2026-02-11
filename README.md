# URL Shortener

API para encurtar URLs: recebe um link longo e devolve um link curto que redireciona para o original.

## Tecnologias

- **FastAPI** – API REST
- **SQLAlchemy** – ORM (SQLite)
- **Hashids** – geração de códigos curtos a partir do ID
- **Pydantic** – validação de dados
- **python-dotenv** – variáveis de ambiente via `.env`

## Como rodar

### 1. Clonar e entrar no projeto

```bash
cd url-shortener
```

### 2. Ambiente virtual (recomendado)

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env` conforme necessário (veja a tabela abaixo). Para desenvolvimento os valores em `.env.example` já funcionam.

### 5. Subir o servidor

```bash
python3 -m uvicorn app.main:app --reload
```

A API fica em **http://127.0.0.1:8000**. A documentação interativa (Swagger) em **http://127.0.0.1:8000/docs**.

## Uso da API

### Encurtar uma URL

**POST** `/shorten`

Corpo (JSON):

```json
{
  "url": "https://exemplo.com/pagina-muito-longa"
}
```

Resposta (exemplo):

```json
{
  "short_url": "http://localhost:8000/m8A"
}
```

Se a mesma URL for enviada de novo, a API devolve o mesmo `short_url` (sem criar outro registro).

### Acessar o link curto

**GET** `/{code}`

Exemplo: **GET** `http://localhost:8000/m8A2bc1`  
→ redireciona (307) para a URL original.

## Variáveis de ambiente

| Variável    | Obrigatória | Descrição |
|------------|-------------|-----------|
| `BASE_URL`  | Não         | URL base do serviço (usada nos links curtos devolvidos). Padrão: `http://localhost:8000`. |
| `HASH_SALT` | Não         | Sal usado pelo Hashids para gerar os códigos. Em produção use uma string longa e aleatória. Padrão: `my_secret_key_dev_only`. |

## Estrutura do projeto

```
url-shortener/
├── app/
│   ├── __init__.py
│   ├── config.py      # Configuração (Hashids, dotenv)
│   ├── database.py    # Engine e sessão SQLAlchemy
│   ├── main.py        # Rotas FastAPI
│   ├── models.py      # Modelo URL
│   ├── schemas.py     # Schemas Pydantic
│   └── shortener.py   # encode_id / decode_code (Hashids)
├── .env.example
├── requirements.txt
└── README.md
```

## Licença

Uso livre para estudo e projetos pessoais.
