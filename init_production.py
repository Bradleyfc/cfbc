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
    
    print(f"Configuración del superusuario:")
    print(f"  Username: {username}")
    print(f"  Email: {email}")
    print(f"  Password: {'*' * len(password)}")
    
    try:
        # Verificar si el usuario ya existe
        existing_user = User.objects.filter(username=username).first()
        
        if existing_user:
            print(f"Usuario '{username}' ya existe")
            print(f"  Es superusuario: {existing_user.is_superuser}")
            print(f"  Es staff: {existing_user.is_staff}")
            
            # Actualizar permisos si no es superusuario
            if not existing_user.is_superuser:
                existing_user.is_superuser = True
                existing_user.is_staff = True
                existing_user.save()
                print("✅ Permisos de superusuario actualizados")
            
            # Actualizar contraseña
            existing_user.set_password(password)
            existing_user.save()
            print("✅ Contraseña actualizada")
            
        else:
            # Crear nuevo superusuario
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            print(f"✅ Superusuario '{username}' creado exitosamente")
        
        print(f"Puedes acceder al admin en: /admin/")
        print(f"Credenciales: {username} / {password}")
        
    except Exception as e:
        print(f"❌ Error al crear superusuario: {e}")
        raise

if __name__ == '__main__':
    create_superuser()