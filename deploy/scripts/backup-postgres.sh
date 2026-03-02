#!/usr/bin/env bash
set -euo pipefail
BACKUP_DIR="deploy/scripts/backups"
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="${BACKUP_DIR}/sage-postgres-$(date +%Y%m%d-%H%M%S).sql.gz"
echo "Backing up PostgreSQL..."
docker exec sage-postgres-1 pg_dump -U sage sage | gzip > "$BACKUP_FILE"
echo "Backup saved to ${BACKUP_FILE}"
