#!/usr/bin/env bash
set -euo pipefail
BACKUP_DIR="deploy/scripts/backups/cometbft-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
for i in 0 1 2 3; do
    echo "Backing up node${i}..."
    docker cp "sage-cometbft${i}-1:/cometbft/data" "${BACKUP_DIR}/node${i}-data" 2>/dev/null || echo "Node ${i} not running, skipping"
done
echo "Backup saved to ${BACKUP_DIR}"
