#!/usr/bin/env bash

set -euo pipefail

# Debian 11 custom runtime ships Python 3.12 here.
if [ -d "/var/fc/lang/python3.12/bin" ]; then
  export PATH="/var/fc/lang/python3.12/bin:${PATH}"
fi

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.prod}"
export PYTHONUNBUFFERED=1

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
else
  echo "No python interpreter found in PATH: ${PATH}" >&2
  exit 127
fi

PORT="${FC_SERVER_PORT:-9000}"
WORKERS="${GUNICORN_WORKERS:-1}"
THREADS="${GUNICORN_THREADS:-4}"
TIMEOUT="${GUNICORN_TIMEOUT:-120}"
RUN_MIGRATE_ON_START="${RUN_MIGRATE_ON_START:-false}"
RUN_DEMO_SEED_ON_START="${RUN_DEMO_SEED_ON_START:-false}"
DEMO_SEED_COMMAND="${DEMO_SEED_COMMAND:-seed_demo_data_light}"

if [ "${RUN_MIGRATE_ON_START}" = "true" ]; then
  "${PYTHON_BIN}" manage.py migrate --noinput --settings="${DJANGO_SETTINGS_MODULE}"
fi

if [ "${RUN_DEMO_SEED_ON_START}" = "true" ]; then
  if ! "${PYTHON_BIN}" manage.py shell --settings="${DJANGO_SETTINGS_MODULE}" -c "from apps.users.models import User; raise SystemExit(0 if User.objects.exists() else 1)"; then
    "${PYTHON_BIN}" manage.py "${DEMO_SEED_COMMAND}" --settings="${DJANGO_SETTINGS_MODULE}"
  fi
fi

exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WORKERS}" \
  --threads "${THREADS}" \
  --timeout "${TIMEOUT}"
