# BackStab Desktop Distribution (macOS Intel x86_64)

This folder packages the React frontend and Django backend into a one-click macOS app using Electron.

## Prerequisites on build machine

- macOS Intel (x86_64) machine
- Node.js and npm
- Python virtual environment already created at `backend/venv`
- Backend dependencies installed into `backend/venv`

## Build the `.app` / `.dmg`

From repository root:

```bash
cd desktop
npm install
npm run build:mac:x64
```

Build artifacts will be under `desktop/dist/`.

## Runtime behavior

- Double-clicking `BackStab.app` launches the desktop window.
- Electron starts Django in background via:
  - Python: `backend/venv/bin/python`
  - Runner: `backend/desktop_runner.py`
- Django binds to `127.0.0.1:8000`.
- On app quit, Electron sends `SIGTERM` to backend.

## Important packaging note

This setup includes your local `backend/venv` inside the app resources.
Build on the same architecture you target (Intel x86_64) so the Python runtime is compatible.
