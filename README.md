# SimpleBank Django

SimpleBank is a small REST API service built with Django REST Framework.
It includes user registration, JWT authentication, account balance, transaction history, transfers, and OpenAPI documentation.

## Features

- Register user with `email + password`
- Login and get JWT auth tokens
- Automatically create a unique 10-digit account on registration
- Deposit €10,000 welcome bonus on registration
- Get current balance
- List transactions with optional `from` / `to` datetime filtering
- Transfer money between accounts
- Apply transfer fee: `2.5%` of amount or minimum `€5`
- Credit transfer fees to a dedicated service account
- Record sender debit, receiver credit, and service-account fee transactions
- Atomic balance updates using `transaction.atomic()` and `select_for_update()`
- OpenAPI schema + Swagger UI + ReDoc via drf-spectacular

## Tech stack

- Django
- Django REST Framework
- SimpleJWT
- drf-spectacular
- PostgreSQL
- Docker Compose

## Run locally with Docker

```bash
cp .env.example .env
docker compose up --build
```

The web container applies migrations before starting Gunicorn with five worker
processes. All workers connect to the same PostgreSQL service configured by
`POSTGRES_HOST`, `POSTGRES_NAME`, `POSTGRES_USER`, and the related environment
variables.

API base URL:

- `http://localhost:8000`

## API documentation

- OpenAPI schema: `http://localhost:8000/api/schema/`
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

## Run tests

```bash
docker compose run --rm web python manage.py test
```

## Generate concurrent test transfers

Install the project requirements, start the API with `docker compose up`, then run:

```bash
python scripts/async_transfers.py
```

The script creates 15 uniquely named test accounts and submits 30 concurrent randomized transfers. Override the defaults with `--base-url`, `--accounts`, `--transfers`, `--concurrency`, `--min-amount`, and `--max-amount`.

To stress simultaneous transfers in both directions between the same two accounts, run:

```bash
python scripts/opposing_transfers.py --rounds 30 --amount 10.00
```

Each round releases the two authenticated transfer requests together. Gunicorn distributes concurrent requests among available workers, though the script cannot guarantee which individual workers receive each request.

## Main endpoints

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `GET /api/accounts/me/balance/`
- `GET /api/transactions/?from=...&to=...`
- `POST /api/transfers/`

## Example register request

```bash
curl -X POST http://localhost:8000/api/auth/register/   -H "Content-Type: application/json"   -d '{
    "email": "user1@example.com",
    "password": "strongpass123"
  }'
```

## Example login request

```bash
curl -X POST http://localhost:8000/api/auth/login/   -H "Content-Type: application/json"   -d '{
    "email": "user1@example.com",
    "password": "strongpass123"
  }'
```
