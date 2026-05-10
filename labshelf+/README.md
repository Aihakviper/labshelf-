# LabShelf+

LabShelf+ is a Django + React library management system for Nigerian schools and institutions. This implementation follows the provided PRD and SDD: multi-tenant institutions, catalog inventory, borrowing and returns, reservations, overdue fines, and role-aware library users.

## Run locally

```bash
python manage.py migrate
python manage.py seed_labshelf
python manage.py runserver 127.0.0.1:8000
```

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173.

If another local service already owns port 8000, run:

```bash
python manage.py runserver 127.0.0.1:8015
```

## Included workflows

- Add books with copies, categories, ISBNs, and shelf locations.
- Check books out to members with the configured five-day loan policy.
- Renew loans up to the tenant renewal limit.
- Return books, calculate overdue fines, and advance the reservation queue.
- Switch between institutions to demonstrate tenant isolation.

## Stack

- Django 5
- SQLite for local development
- React 18 with Vite
- Django JSON endpoints for product data and circulation actions

The SDD calls for PostgreSQL in production; SQLite is used here so the product can run immediately in this workspace.

## Project layout

```text
backend/
  config/          Django settings, URL routing, ASGI/WSGI
  apps/            Domain apps: tenants, catalog, circulation, core
frontend/
  index.html       Vite app shell
  src/             React components, API service, and styles
```

The Vite dev server proxies `/api/*` to Django. If Django is not running on port 8000, set `VITE_DJANGO_API_URL` in `frontend/.env`.

## Root scripts

```bash
npm run backend:dev
npm run frontend:dev
npm run frontend:build
npm run test
```
