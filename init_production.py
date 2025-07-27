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
    username = os.getenv('ADMIN_USERNAME', 'admin')
    email = os.getenv('ADMIN_EMAIL', 'admin@cfbc.edu.ni')
    password = os.getenv('ADMIN_PASSWORD', 'changeme123')
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"Superusuario '{username}' creado exitosamente")
        print(f"Email: {email}")
        print("Puedes acceder al admin en: /admin/")
    else:
        print(f"Superusuario '{username}' ya existe")

if __name__ == '__main__':
    create_superuser()