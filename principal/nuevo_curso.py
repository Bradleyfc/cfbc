from django.core.management.base import BaseCommand
from principal.models import CursoAcademico, Matriculas

class Command(BaseCommand):
    help = 'Crea un nuevo curso académico y copia matrículas'

    def handle(self, *args, **options):
        # Pedir al usuario el nombre del nuevo curso académico
        nombre_curso = input("Ingrese el nombre del nuevo curso académico (ej: 2025-2026): ")
        
        # Desactivar todos los cursos académicos existentes
        CursoAcademico.objects.all().update(activo=False)
        
        # Crear nuevo curso y activarlo
        nuevo_curso = CursoAcademico.objects.create(
            nombre=nombre_curso,
            activo=True
        )
        
        # Obtener el curso anterior (que acaba de ser desactivado) y archivarlo
        curso_anterior = CursoAcademico.objects.filter(activo=False, archivado=False).order_by('-id').first()
        if curso_anterior:
            # Archivar el curso anterior
            curso_anterior.archivado = True
            curso_anterior.save()
            self.stdout.write(self.style.SUCCESS(f'Curso anterior {curso_anterior.nombre} archivado correctamente'))
            

        
        self.stdout.write(self.style.SUCCESS(f'Nuevo curso creado: {nuevo_curso.nombre}'))


# Matrículas del curso actual
matriculas_actuales = Matriculas.objects.filter(curso_academico__activo=True)

# Histórico de matrículas de un alumno
matriculas_juan = Matriculas.objects.filter(alumno__nombre="Juan Pérez").order_by('curso_academico__nombre')

# Todos los alumnos matriculados en 2023-2024
alumnos_2025 = Matriculas.objects.filter(
    curso_academico__nombre="2025-2026"
).values_list('student', flat=True).distinct()

