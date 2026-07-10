# Synapse AI-SEOS

## JWT Configuration

Environment variables:

- `JWT_ALGORITHM` (required, e.g. `HS256`)
- `JWT_SECRET_KEY` (required for HS* algorithms)
- `JWT_ISSUER` (optional)
- `JWT_AUDIENCE` (optional)
- `APP_NAME` (optional, default: `Synapse AI-SEOS`)
- `LOG_LEVEL` (optional, default: `INFO`)

## Auth behavior

- Protected routes require `Authorization: Bearer <jwt>`.
- Failure responses return `401` with `WWW-Authenticate: Bearer` and JSON:
  - `{ "code": "missing_token|malformed_token|invalid_token|expired_token", "message": "..." }`

## Endpoints

- `GET /health` (public)
- `GET /backlog` (protected)
- `POST /backlog` (protected)
- `GET /users/me` (protected)
