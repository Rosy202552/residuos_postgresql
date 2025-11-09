#!/usr/bin/env bash
set -euo pipefail

echo "Python version: $(python -V 2>&1)"
echo "Upgrading packaging tools..."
pip install --upgrade pip setuptools wheel

echo "Installing requirements..."
pip install -r requirements.txt

echo "Checking installed DB drivers (psycopg / psycopg2)..."
python - <<'PY'
import importlib, sys
print('psycopg3 installed:', importlib.util.find_spec('psycopg') is not None)
print('psycopg2 installed:', importlib.util.find_spec('psycopg2') is not None)
try:
    import psycopg
    print('psycopg version:', getattr(psycopg, '__version__', 'unknown'))
except Exception:
    pass
try:
    import psycopg2
    print('psycopg2 version:', getattr(psycopg2, '__version__', 'unknown'))
except Exception:
    pass
PY

echo "Running DB migrations (flask db upgrade)..."
flask db upgrade

echo "Build script finished."
