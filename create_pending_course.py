#!/usr/bin/env python
"""
Script para crear un curso pendiente con matrícula
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cfbc.settings')
django.setup()

from django.contrib.auth.models import User, Group
from principal.models import Curso, CursoAcademico, SolicitudInscripcion, Matriculas
from django.utils import timezone

def create_pending_course():
    print("=== Creando curso pendiente ===\n")
    
    # Obtener curso académico activo
    curso_academico = CursoAcademico.objects.filter(activo=True).first()
    
    # Obtener un estudiante de prueba
    grupo_estudiantes = Group.objects.get(name='Estudiantes')
    estudiante = grupo_estudiantes.user_set.first()
    
    # Obtener curso "Mate"
    curso_mate = Curso.objects.filter(name="Mate", curso_academico=curso_academico).first()
    
    if not curso_mate:
        print("❌ No se encontró el curso Mate")
        return
    
    # Crear matrícula para el curso Mate
    matricula, created = Matriculas.objects.get_or_create(
        student=estudiante,
        course=curso_mate,
        curso_academico=curso_academico,
        defaults={
            'activo': True,
            'estado': 'P'  # Pendiente
        }
    )
    
    if created:
        print(f"✅ Matrícula creada para {curso_mate.name}")
    else:
        print(f"ℹ️  Matrícula ya existía para {curso_mate.name}")
    
    # Verificar que la solicitud esté pendiente
    try:
        solicitud = SolicitudInscripcion.objects.get(
            estudiante=estudiante,
            curso=curso_mate
        )
        solicitud.estado = 'pendiente'
        solicitud.fecha_revision = None
        solicitud.revisado_por = None
        solicitud.save()
        print(f"✅ Solicitud configurada como pendiente para {curso_mate.name}")
    except SolicitudInscripcion.DoesNotExist:
        print(f"❌ No se encontró solicitud para {curso_mate.name}")

if __name__ == "__main__":
    create_pending_course()