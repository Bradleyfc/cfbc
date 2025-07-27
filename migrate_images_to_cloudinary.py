#!/usr/bin/env python
"""
Script para migrar imágenes existentes a Cloudinary
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cfbc.settings')
django.setup()

from accounts.models import Registro
from principal.models import Curso
import cloudinary.uploader

def migrate_images():
    """Migrar imágenes existentes a Cloudinary"""
    
    print("Migrando imágenes de usuarios...")
    for registro in Registro.objects.all():
        if registro.image and hasattr(registro.image, 'path'):
            try:
                # Subir imagen a Cloudinary
                result = cloudinary.uploader.upload(
                    registro.image.path,
                    folder="users/",
                    public_id=f"user_{registro.user.id}"
                )
                print(f"✅ Imagen de {registro.user.username} migrada")
            except Exception as e:
                print(f"❌ Error migrando imagen de {registro.user.username}: {e}")
    
    print("Migrando imágenes de cursos...")
    for curso in Curso.objects.all():
        if curso.image and hasattr(curso.image, 'path'):
            try:
                # Subir imagen a Cloudinary
                result = cloudinary.uploader.upload(
                    curso.image.path,
                    folder="cursos/",
                    public_id=f"curso_{curso.id}"
                )
                print(f"✅ Imagen de {curso.name} migrada")
            except Exception as e:
                print(f"❌ Error migrando imagen de {curso.name}: {e}")

if __name__ == '__main__':
    migrate_images()