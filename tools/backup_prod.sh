#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/bhrikutimandap}"
BACKUP_DIR="${BACKUP_DIR:-$APP_DIR/backups}"
COMPOSE_FILE="${COMPOSE_FILE:-$APP_DIR/compose.prod.yml}"
ENV_FILE="${ENV_FILE:-$APP_DIR/.env.prod}"

INCLUDE_MEDIA="${INCLUDE_MEDIA:-0}"
KEEP_DAYS="${KEEP_DAYS:-14}"

STAMP="$(date +%F_%H%M%S)"

mkdir -p "$BACKUP_DIR"

cd "$APP_DIR"

if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: env file not found: $ENV_FILE" >&2
  exit 1
fi

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "ERROR: compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi

DB_DUMP="$BACKUP_DIR/db_${STAMP}.dump"
DB_SQL="$BACKUP_DIR/db_${STAMP}.sql"
MEDIA_ZIP="$BACKUP_DIR/media_${STAMP}.zip"

echo "[backup] Creating database backup..."
# Custom-format dump is best for restore flexibility
if docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T db pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -Fc > "$DB_DUMP"; then
  echo "[backup] Wrote $DB_DUMP"
else
  echo "[backup] pg_dump -Fc failed; trying plain SQL..." >&2
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T db pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" > "$DB_SQL"
  echo "[backup] Wrote $DB_SQL"
fi

if [ "$INCLUDE_MEDIA" = "1" ]; then
  if [ -d "$APP_DIR/media" ]; then
    echo "[backup] Creating media backup..."
    (cd "$APP_DIR" && zip -rq "$MEDIA_ZIP" media)
    echo "[backup] Wrote $MEDIA_ZIP"
  else
    echo "[backup] Skipping media: $APP_DIR/media not found" >&2
  fi
fi

if [ "$KEEP_DAYS" -gt 0 ]; then
  echo "[backup] Pruning backups older than $KEEP_DAYS days..."
  find "$BACKUP_DIR" -type f \( -name 'db_*.dump' -o -name 'db_*.sql' -o -name 'media_*.zip' \) -mtime "+$KEEP_DAYS" -delete || true
fi

echo "[backup] Done."