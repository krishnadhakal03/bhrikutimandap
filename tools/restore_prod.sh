#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 /path/to/db_YYYY-MM-DD_HHMMSS.dump|.sql" >&2
  exit 2
fi

DUMP_FILE="$1"

APP_DIR="${APP_DIR:-/opt/bhrikutimandap}"
COMPOSE_FILE="${COMPOSE_FILE:-$APP_DIR/compose.prod.yml}"
ENV_FILE="${ENV_FILE:-$APP_DIR/.env.prod}"

cd "$APP_DIR"

if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: env file not found: $ENV_FILE" >&2
  exit 1
fi

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "ERROR: compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi

if [ ! -f "$DUMP_FILE" ]; then
  echo "ERROR: dump file not found: $DUMP_FILE" >&2
  exit 1
fi

echo "[restore] Restoring $DUMP_FILE ..."

case "$DUMP_FILE" in
  *.dump)
    # --clean drops objects before recreating
    cat "$DUMP_FILE" | docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T db pg_restore -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" --clean --if-exists
    ;;
  *.sql)
    cat "$DUMP_FILE" | docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T db psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"
    ;;
  *)
    echo "ERROR: Unknown file type (expect .dump or .sql)" >&2
    exit 2
    ;;
esac

echo "[restore] Done."