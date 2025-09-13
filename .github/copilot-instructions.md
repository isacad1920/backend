# Copilot Instructions for SOFinance Backend

## Project Overview
- **SOFinance** is a full-featured Point of Sale (POS) and Financial Management system for retail and multi-branch businesses.
- Backend: **FastAPI** (Python 3.13), **Pydantic v2**, **PostgreSQL**, **Prisma ORM**.
- Frontend: Next.js 14 (see `/frontend`).

## Architecture & Key Patterns
- **Modular Structure:**
  - Core logic in `app/` (submodules: `core/`, `db/`, `middlewares/`, `modules/`, `utils/`).
  - API routes and business logic are separated by domain (e.g., sales, inventory, users).
- **Database:**
  - Models and schema in `prisma/schema.prisma`.
  - Use Prisma ORM for DB access; avoid raw SQL unless necessary.
- **Audit & Permissions:**
  - User roles, permissions, and audit logging are first-class (see `app/modules/` and `app/core/`).
- **Partial Payments:**
  - Sales support incremental payments; see endpoints `/api/v1/sales/ar/summary` and `/api/v1/sales/{sale_id}/payments`.

## Developer Workflows
- **Run server:** `python run.py` or use `quick_server_start.py` for fast startup.
- **Health check:** Use the VS Code task "Probe backend health" or `curl http://localhost:8000/health`.
- **Tests:**
  - Run all: `pytest`
  - Test files: `tests/` (see `tests/README.md` for structure and coverage)
- **Migrations:**
  - Use Prisma for DB migrations. Edit `prisma/schema.prisma` and run `prisma migrate dev`.
- **Debugging:**
  - Use scripts like `debug_*.py` for targeted troubleshooting.

## Project Conventions
- **API versioning:** All endpoints are under `/api/v1/`.
- **Response Models:** Use Pydantic models for all API responses (see `app/core/response.py`).
- **Error Handling:** Centralized in `app/core/`.
- **Permissions:** Enforced via decorators/middleware; see `app/middlewares/`.
- **Testing:**
  - Use Pytest fixtures in `tests/conftest.py`.
  - Test coverage is prioritized for all major endpoints.

## Integration Points
- **Frontend:** Communicates via REST API (`/api/v1/`).
- **Database:** PostgreSQL via Prisma ORM.
- **External:** Minimal; most logic is internal.

## Examples
- To add a new API route: create a module in `app/modules/`, define Pydantic models, register the route in `app/main.py`.
- To add a test: add a file in `tests/api/` or `tests/unit/` and use existing fixtures.

---
For more details, see `README.md` and `tests/README.md`.
