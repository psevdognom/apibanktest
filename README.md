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
