#!/usr/bin/env python
"""
Script para inicializar datos en producción
Ejecutar después del primer despliegue
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cfbc.settings')
django.setup()

from django.contrib.auth.models import User

def create_superuser():
    """Crear superusuario si no existe"""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@cfbc.edu.ni',
            password=os.getenv('ADMIN_PASSWORD', 'changeme123')
        )
        print("Superusuario creado exitosamente")
    else:
        print("Superusuario ya existe")

if __name__ == '__main__':
    create_superuser()