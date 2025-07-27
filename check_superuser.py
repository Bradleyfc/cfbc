#!/usr/bin/env python
"""
Script para verificar el estado del superusuario
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cfbc.settings')
django.setup()

from django.contrib.auth.models import User

def check_superuser():
    """Verificar el estado del superusuario"""
    username = os.getenv('ADMIN_USERNAME', 'admin')
    
    print(f"Buscando usuario: {username}")
    
    try:
        user = User.objects.get(username=username)
        print(f"✅ Usuario encontrado: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Es superusuario: {user.is_superuser}")
        print(f"   Es staff: {user.is_staff}")
        print(f"   Está activo: {user.is_active}")
        print(f"   Fecha de creación: {user.date_joined}")
        
        # Verificar si la contraseña funciona
        password = os.getenv('ADMIN_PASSWORD', 'changeme123')
        if user.check_password(password):
            print("✅ La contraseña es correcta")
        else:
            print("❌ La contraseña NO es correcta")
            
    except User.DoesNotExist:
        print(f"❌ Usuario '{username}' NO existe")
        print("Usuarios existentes:")
        for user in User.objects.all():
            print(f"   - {user.username} (superuser: {user.is_superuser})")

def create_superuser_force():
    """Crear superusuario forzadamente"""
    username = os.getenv('ADMIN_USERNAME', 'admin')
    email = os.getenv('ADMIN_EMAIL', 'admin@cfbc.edu.ni')
    password = os.getenv('ADMIN_PASSWORD', 'changeme123')
    
    # Eliminar usuario existente si existe
    User.objects.filter(username=username).delete()
    
    # Crear nuevo superusuario
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f"✅ Superusuario '{username}' creado/recreado exitosamente")
    return user

if __name__ == '__main__':
    print("=== DIAGNÓSTICO DE SUPERUSUARIO ===")
    check_superuser()
    
    print("\n¿Quieres recrear el superusuario? (y/n)")
    # En producción, siempre recrear
    create_superuser_force()
    
    print("\n=== VERIFICACIÓN FINAL ===")
    check_superuser()