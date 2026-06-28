# Django + React TypeScript Project Template


## Tech Stack

**Backend**
- Python / Django
- Django REST Framework
- Simple JWT (authentication)
- PostgreSQL
- django-cors-headers
- django-environ

**Frontend**
- React + TypeScript
- Vite
- Axios

---

## Prerequisites

Make sure you have the following installed before starting:

- Python 3.10+
- Node.js 18+
- PostgreSQL
- npm or yarn

---

## Running Containers
### 1. How to run the cointainer for use
```bash
docker compose -f docker-compose.yml up -d
```


### 2. Open browser

Open your broswer at localhost:8080/

## Getting Started Local Development

### 1. Backend Setup

#### Create and activate a virtual environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate       # Mac/Linux
# or
venv\Scripts\activate          # Windows
```

#### Install dependencies

```bash
pip install -r requirements.txt
```

#### Set up environment variables

Create and Open `.env` and configure the following:

```bash
SECRET_KEY=        # Generate a new one — see instructions below
```

> **Generating a SECRET_KEY**
> Never reuse the secret key from another project. Generate a fresh one with:
> ```bash
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```
> The `SECRET_KEY` is used by Django to sign sessions, CSRF tokens, and password reset links.
> If it leaks, rotate it immediately — but note this will invalidate all active sessions and tokens.

#### Create the database

```bash
createdb your_db_name
```

#### Run migrations

```bash
python manage.py migrate
```

#### Create a superuser (optional)

```bash
python manage.py createsuperuser
```

#### Start the development server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000`.

---

### 3. Frontend Setup

```bash
cd frontend
npm install
```

#### Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and configure:

```bash
VITE_API_URL=http://localhost:8000/api
```

#### Start the development server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`.

---
## Authentication

Authentication uses JWT via `djangorestframework-simplejwt`.

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/login/` | POST | Obtain access + refresh tokens |
| `/api/auth/refresh/` | POST | Refresh access token |
| `/api/auth/logout/` | POST | Blacklist refresh token |

**Token lifetimes:**
- Access token: 15 minutes
- Refresh token: 7 days

Include the access token in all authenticated requests:
```
Authorization: Bearer <access_token>
```

---

## Creating a New App

```bash
cd backend
python manage.py startapp your_app_name apps/your_app_name
```

Then register it in `core/settings/base.py`:
```python
INSTALLED_APPS = [
    ...
    'apps.your_app_name',
]
```

---

## Running Tests

```bash
cd backend
pytest
```

---

## Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key — must be unique per project |

### Frontend (`frontend/.env`)

| Variable | Description |
|---|---|
| `VITE_API_URL` | Base URL for the Django API |

---

## Important Notes

- **Never commit `.env` files** — they are listed in `.gitignore`
- **Always generate a new `SECRET_KEY`** when cloning this template
- **Never reuse a `SECRET_KEY` across different projects**
- The `venv/` folder and `node_modules/` are also excluded from git
