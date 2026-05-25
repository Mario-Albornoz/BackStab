#!/bin/bash

# Check Docker is running
if ! docker info > /dev/null 2>&1; then
  osascript -e 'display alert "Docker is not running" message "Please open Docker Desktop and wait for it to start, then run this script again."'
  exit 1
fi

# Move to the folder where this script lives (works when double-clicked)
cd "$(dirname "$0")"

# Generate a .env with a random SECRET_KEY on first run
if [ ! -f .env ]; then
  echo "SECRET_KEY=$(LC_ALL=C tr -dc 'A-Za-z0-9!@#$%^&*' < /dev/urandom | head -c 50)" > .env
  echo ".env created with a random secret key."
fi

# Build and start
docker compose up --build &

# Wait for the app to be ready then open the browser
echo "Starting BackStab... this may take a minute on first run."
until curl -sf http://localhost:8080 > /dev/null 2>&1; do
  sleep 2
done

open http://localhost:8080
