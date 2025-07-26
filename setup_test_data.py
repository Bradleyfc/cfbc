#!/usr/bin/env python
"""
Script para configurar datos de prueba para el estado de matrícula
"""
import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cfbc.settings')
django.setup()

from django.contrib.auth.models import User, Group
from principal.models import Curso, CursoAcademico, SolicitudInscripcion, Matriculas
from django.utils import timezone

def setup_test_data():
    print("=== Configurando datos de prueba ===\n")
    
    # Obtener curso académico activo
    curso_academico = CursoAcademico.objects.filter(activo=True).first()
    if not curso_academico:
        print("❌ No hay curso académico activo")
        return
    
    # Obtener un estudiante de prueba
    grupo_estudiantes = Group.objects.get(name='Estudiantes')
    estudiante = grupo_estudiantes.user_set.first()
    
    if not estudiante:
        print("❌ No hay estudiantes registrados")
        return
    
    # Obtener un profesor para las revisiones
    grupo_profesores = Group.objects.get(name='Profesores')
    profesor = grupo_profesores.user_set.first()
    
    if not profesor:
        print("❌ No hay profesores registrados")
        return
    
    # Obtener cursos en estado de inscripción
    cursos_inscripcion = Curso.objects.filter(
        curso_academico=curso_academico,
        status__in=['I', 'IT']
    )
    
    if cursos_inscripcion.count() < 3:
        print("❌ Se necesitan al menos 3 cursos en estado de inscripción")
        return
    
    cursos_list = list(cursos_inscripcion[:3])
    
    # Crear diferentes estados de solicitud
    estados_prueba = [
        ('aprobada', 'Solicitud aprobada'),
        ('rechazada', 'Solicitud rechazada'),
        ('pendiente', 'Solicitud pendiente')
    ]
    
    for i, (estado, descripcion) in enumerate(estados_prueba):
        if i < len(cursos_list):
            curso = cursos_list[i]
            
            # Crear o actualizar solicitud
            solicitud, created = SolicitudInscripcion.objects.get_or_create(
                estudiante=estudiante,
                curso=curso,
                defaults={
                    'formulario': curso.formulario_aplicacion,
                    'estado': estado
                }
            )
            
            if not created:
                solicitud.estado = estado
            
            # Si no es pendiente, agregar información de revisión
            if estado != 'pendiente':
                solicitud.fecha_revision = timezone.now()
                solicitud.revisado_por = profesor
            else:
                solicitud.fecha_revision = None
                solicitud.revisado_por = None
            
            solicitud.save()
            
            # Crear matrícula si la solicitud está aprobada
            if estado == 'aprobada':
                matricula, created = Matriculas.objects.get_or_create(
                    student=estudiante,
                    course=curso,
                    curso_academico=curso_academico,
                    defaults={
                        'activo': True,
                        'estado': 'P'  # Pendiente
                    }
                )
                print(f"✅ {descripcion} - Curso: {curso.name} (con matrícula)")
            else:
                # Eliminar matrícula si existe y la solicitud no está aprobada
                Matriculas.objects.filter(
                    student=estudiante,
                    course=curso,
                    curso_academico=curso_academico
                ).delete()
                print(f"✅ {descripcion} - Curso: {curso.name}")
    
    print(f"\n✅ Datos de prueba configurados para el estudiante: {estudiante.get_full_name() or estudiante.username}")
    print("Ahora puedes acceder al perfil del estudiante para ver los diferentes estados de matrícula.")

if __name__ == "__main__":
    setup_test_data()