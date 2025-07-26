#!/usr/bin/env python
"""
Script de prueba para verificar el estado de matrícula en el perfil del estudiante
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cfbc.settings')
django.setup()

from django.contrib.auth.models import User, Group
from principal.models import Curso, CursoAcademico, SolicitudInscripcion, Matriculas
from accounts.models import Registro

def test_matricula_status():
    print("=== Prueba de Estado de Matrícula ===\n")
    
    # Obtener curso académico activo
    curso_academico = CursoAcademico.objects.filter(activo=True).first()
    if not curso_academico:
        print("❌ No hay curso académico activo")
        return
    
    print(f"✅ Curso académico activo: {curso_academico.nombre}")
    
    # Obtener un estudiante de prueba
    grupo_estudiantes = Group.objects.get(name='Estudiantes')
    estudiante = grupo_estudiantes.user_set.first()
    
    if not estudiante:
        print("❌ No hay estudiantes registrados")
        return
    
    print(f"✅ Estudiante de prueba: {estudiante.get_full_name() or estudiante.username}")
    
    # Obtener cursos del curso académico activo
    cursos = Curso.objects.filter(curso_academico=curso_academico)
    
    if not cursos.exists():
        print("❌ No hay cursos en el curso académico activo")
        return
    
    print(f"✅ Cursos disponibles: {cursos.count()}")
    
    # Verificar matrículas del estudiante
    matriculas = Matriculas.objects.filter(
        student=estudiante,
        curso_academico=curso_academico
    )
    
    print(f"✅ Matrículas del estudiante: {matriculas.count()}")
    
    # Verificar solicitudes de inscripción
    solicitudes = SolicitudInscripcion.objects.filter(estudiante=estudiante)
    
    print(f"✅ Solicitudes de inscripción: {solicitudes.count()}")
    
    # Separar cursos por estado (simulando la lógica de la vista)
    approved_courses = []
    pending_courses = []
    
    print("\n=== SEPARACIÓN DE CURSOS ===")
    
    # Mostrar detalles de cada matrícula y su estado de solicitud
    for matricula in matriculas:
        curso = matricula.course
        print(f"\n--- Curso: {curso.name} ---")
        print(f"Estado del curso: {curso.get_status_display()}")
        print(f"Estado de matrícula: {matricula.get_estado_display()}")
        
        # Buscar solicitud correspondiente
        try:
            solicitud = SolicitudInscripcion.objects.get(
                estudiante=estudiante,
                curso=curso
            )
            print(f"Estado de solicitud: {solicitud.get_estado_display()}")
            if solicitud.fecha_revision:
                print(f"Fecha de revisión: {solicitud.fecha_revision}")
            if solicitud.revisado_por:
                print(f"Revisado por: {solicitud.revisado_por.get_full_name() or solicitud.revisado_por.username}")
            
            # Lógica de separación
            if curso.status in ['I', 'IT'] and solicitud.estado == 'pendiente':
                pending_courses.append(curso)
                print("📋 Se mostrará en: CURSOS PENDIENTES")
            else:
                approved_courses.append(curso)
                print("✅ Se mostrará en: CURSOS INSCRITOS")
                
        except SolicitudInscripcion.DoesNotExist:
            print("Estado de solicitud: Sin solicitud")
            approved_courses.append(curso)
            print("✅ Se mostrará en: CURSOS INSCRITOS")
    
    print(f"\n=== RESUMEN ===")
    print(f"📚 Cursos Inscritos: {len(approved_courses)}")
    for curso in approved_courses:
        print(f"  - {curso.name}")
    
    print(f"⏳ Cursos Pendientes: {len(pending_courses)}")
    for curso in pending_courses:
        print(f"  - {curso.name}")

if __name__ == "__main__":
    test_matricula_status()