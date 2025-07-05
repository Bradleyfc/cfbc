from gc import enable
from pyexpat import model
from tabnanny import verbose
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# CURSOS
class Curso(models.Model):
    STATUS_CHOICES = [
        ('I', 'En etapa de inscripcion'),
        ('P', 'En progreso'),
        ('F', 'Finalizado'),
    ]
    image = models.ImageField(default='default/plantilla.jpg', upload_to='imagenes/', verbose_name='Imagen de curso')
    name = models.CharField(max_length=90, verbose_name='Nombre')
    description= models.TextField(blank=True, null=True, verbose_name='Descripcion')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'groups__name': 'Profesores'}, verbose_name='Profesor')
    class_quantity = models.PositiveIntegerField(default=0, verbose_name='Catidad de Clases')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='I', verbose_name='Estado')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'

        
# Curso y cambio de curso escolar

class CursoAcademico(models.Model):
    
    nombre = models.CharField(max_length=50, unique=True)  # Ej: "2025-2026"
    activo = models.BooleanField(default=False)
    archivado = models.BooleanField(default=False, verbose_name='Archivado')
    fecha_creacion = models.DateField(default=timezone.now, verbose_name='Fecha de creación')
    
    def archivar(self):
        """Archiva este curso académico y todas sus matrículas"""
        self.archivado = True
        self.activo = False
        self.save()
        
        # También podríamos desactivar todas las matrículas de este curso
        # Matriculas.objects.filter(curso_academico=self).update(activo=False)
        
        return True
    
    def activar(self):
        """Activa este curso y desactiva todos los demás"""
        # Desactivar todos los cursos
        CursoAcademico.objects.all().update(activo=False)
        # Activar este curso
        self.activo = True
        self.archivado = False  # Si estaba archivado, lo desarchivamos
        self.save()
        return True

    def __str__(self):
        estado = "(Activo)" if self.activo else "(Inactivo)"
        if self.archivado:
            estado = "(Archivado)"
        return f"{self.nombre} {estado}"

# MATRICULAS

class Matriculas(models.Model):
    ESTADO_CHOICES = [
        ('P', 'Pendiente'),
        ('A', 'Aprobado'),
        ('R', 'Reprobado'),
        ('L', 'Licencia'),
        ('B', 'Baja'),
    ]
    course = models.ForeignKey(Curso, on_delete=models.CASCADE, verbose_name="Curso")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matriculas', limit_choices_to={'groups__name': 'Estudiantes'}, verbose_name='Estudiante')
    activo = models.BooleanField(default=True, verbose_name='Habilitado')
    curso_academico = models.ForeignKey(CursoAcademico, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Curso Académico')
    fecha_matricula = models.DateField(auto_now_add=True, verbose_name='Fecha de Matrícula')
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='P', verbose_name='Estado')
    
    @property
    def esta_aprobado(self):
        return self.estado == 'A'


    def __str__(self):
        return f'{self.student.username} - {self.course.name}'

    class Meta:
        verbose_name = 'Matricula'
        verbose_name_plural = 'Matriculas'
        unique_together = [['student', 'course', 'curso_academico']]


# ASISTENCIAS    

class Asistencia(models.Model):
    course = models.ForeignKey(Curso, on_delete=models.CASCADE, verbose_name="Curso")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='asistencias', limit_choices_to={'groups__name': 'Estudiantes'}, verbose_name='Estudiante') 
    presente = models.BooleanField(default=False, blank=True, null=True, verbose_name='Asistió')
    date = models.DateField(null=False, blank=False, verbose_name='Fecha')
    
    class Meta:
        unique_together = ('student', 'date', 'course')

    def __str__(self):
        return f"Asistencia de {self.student.first_name} {self.student.last_name} en {self.course.nombre} el {self.date}"

    def __str__(self):
        return f'Asistencia {self.id}'

    class Meta:
        verbose_name= 'Asistencia'
        verbose_name_plural= 'Asistencias'


# CALIFICACIONES

class Calificaciones(models.Model):
    matricula = models.OneToOneField(Matriculas, on_delete=models.CASCADE, related_name='calificaciones', verbose_name='Matrícula', null=True, blank=True)
    course = models.ForeignKey(Curso, on_delete=models.CASCADE, verbose_name="Curso")
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'groups__name': 'Estudiantes'}, verbose_name='Estudiante') 
    curso_academico = models.ForeignKey(CursoAcademico, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Curso Académico')
    # para 6 evaluaciones
    nota_1 = models.PositiveIntegerField(null=True, blank=True, verbose_name='Nota 1')
    nota_2 = models.PositiveIntegerField(null=True, blank=True, verbose_name='Nota 2')
    nota_3 = models.PositiveIntegerField(null=True, blank=True, verbose_name='Nota 3')
    nota_4 = models.PositiveIntegerField(null=True, blank=True, verbose_name='Nota 4')
    nota_5 = models.PositiveIntegerField(null=True, blank=True, verbose_name='Nota 5')
    nota_6 = models.PositiveIntegerField(null=True, blank=True, verbose_name='Nota 6')
    average = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name='Promedio', editable='False')


    def __str__(self):
        return str(self.course)

# Calcular el promedio 

    def calcular_promedio(self):
        notas = [self.nota_1, self.nota_2, self.nota_3, self.nota_4, self.nota_5, self.nota_6 ]
        notas_validas = [nota for nota in notas if nota is not None]
        if notas_validas:
            return sum(notas_validas) / len(notas_validas)
        return None


    def save(self, *args, **kwargs):
    #verificando si alguna nota cambio
        if self.nota_1 or self.nota_2 or self.nota_3 or self.nota_4 or self.nota_5 or self.nota_6:
         self.average = self.calcular_promedio()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name= 'Calificacion'
        verbose_name_plural= 'Calificaciones'
        unique_together = ('course', 'student', 'curso_academico')
      


    
    

