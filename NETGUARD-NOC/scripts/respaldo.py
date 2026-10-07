"""Copia SQLite consistente sin borrar ni sobrescribir la base de uso."""
import sqlite3
from datetime import datetime
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit('Uso: python scripts/respaldo.py RUTA_BASE')
source = Path(sys.argv[1]).resolve()
if not source.is_file():
    raise SystemExit('Base no encontrada')
destination = source.parent / ('respaldo-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.db')
with sqlite3.connect(source.as_uri() + '?mode=ro', uri=True) as original:
    with sqlite3.connect(destination) as backup:
        original.backup(backup)
        assert backup.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
print(destination)
