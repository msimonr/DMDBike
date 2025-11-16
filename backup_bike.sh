#!/bin/bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

FECHA=$(date +%F_%H-%M)
DEST="$SCRIPT_DIR/backups_bike"
mkdir -p "$DEST"

ARCHIVO="$DEST/bike_backup_$FECHA.tar.gz"

#compresion
tar -czf "$ARCHIVO" -C "$SCRIPT_DIR" bici.db static/uploads

echo "Backup generado: $ARCHIVO"
