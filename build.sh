#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Crear superusuario automáticamente (se ejecuta en cada deploy)
echo "Creando superusuario..."
python init_production.py