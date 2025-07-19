from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from accounts.models import Registro
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import date
from decimal import Decimal

# Create your models here.
# CURSOS
class Curso(models.Model):
    STATUS_CHOICES = [
        ('I', 'En etapa de inscripción'),
        ('IT', 'Plazo de Inscripción Terminado'),
        ('P', 'En progreso'),
        ('F', 'Finalizado'),
    ]
    image = models.ImageField(default='default/plantilla.jpg', upload_to='imagenes/', verbose_name='Imagen de curso')
    name = models.CharField(max_length=90, verbose_name='Nombre')
    description= models.TextField(blank=True, null=True, verbose_name='Descripcion')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'groups__name': 'Profesores'}, verbose_name='Profesor')
    class_quantity = models.PositiveIntegerField(default=0, verbose_name='Cantidad de Clases')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='I', verbose_name='Estado')
    curso_academico = models.ForeignKey('CursoAcademico', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Curso Académico')
    enrollment_deadline = models.DateField(verbose_name='Fecha límite de inscripción', null=True, blank=True)
    start_date = models.DateField(verbose_name='Fecha de inicio del curso', null=True, blank=True)

    def __str__(self):
        if self.curso_academico:
            return f"{self.name} ({self.curso_academico.nombre})"
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
         # Primero, obtener y actualizar todos los cursos activos anteriores
        cursos_activos = CursoAcademico.objects.filter(activo=True)
        for curso in cursos_activos:
            if curso != self:
                curso.activo = False
                curso.archivado = True
                curso.save()



        # Activar este curso
        self.activo = True
        self.archivado = False  # Si estaba archivado, lo desarchivamos
        self.save()
        return True


    def save(self, *args, **kwargs):
        if self.activo and not self.pk:  # Si es un nuevo curso y se marca como activo
            # Desactivar y archivar todos los demás cursos académicos activos
            CursoAcademico.objects.filter(activo=True).update(activo=False, archivado=True)
        elif self.activo and self.pk: # Si es un curso existente y se está activando
            # Desactivar y archivar todos los demás cursos académicos activos, excepto este
            CursoAcademico.objects.filter(activo=True).exclude(pk=self.pk).update(activo=False, archivado=True)
        
        # Asegurarse de que si este curso está activo, no esté archivado
        if self.activo:
            self.archivado = False

        super().save(*args, **kwargs)






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
    
    def __str__(self):
        return f"Asistencia de {self.student.first_name} {self.student.last_name} en {self.course.name} el {self.date}"

    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        unique_together = ('student', 'date', 'course')


# CALIFICACIONES

class Calificaciones(models.Model):
    matricula = models.OneToOneField(Matriculas, on_delete=models.CASCADE, related_name='calificaciones', verbose_name='Matrícula', null=True, blank=True)
    course = models.ForeignKey(Curso, on_delete=models.CASCADE, verbose_name="Curso")
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'groups__name': 'Estudiantes'}, verbose_name='Estudiante') 
    curso_academico = models.ForeignKey(CursoAcademico, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Curso Académico')
    # Las notas individuales ahora se manejarán a través del modelo NotaIndividual
    average = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name='Promedio', editable=False)


    def __str__(self):
        return str(self.course)

# Calcular el promedio 

    def calcular_promedio(self):
        # Obtener todas las notas individuales relacionadas con esta calificación
        notas_individuales = self.notas.all()
        notas_validas = [nota.valor for nota in notas_individuales if nota.valor is not None]
        if notas_validas:
            return sum(notas_validas) / len(notas_validas)
        return None


    def save(self, *args, **kwargs):
        # Save the instance first to ensure it has a primary key
        super().save(*args, **kwargs)
        
        # Now that the instance has a PK, calculate the average
        calculated_average = self.calcular_promedio()
        if calculated_average is not None:
            new_average = Decimal(str(calculated_average))
        else:
            new_average = None
        
        # Only update if the average has changed
        if self.average != new_average:
            self.average = new_average
            super().save(update_fields=['average'])

    class Meta:
        verbose_name= 'Calificacion'
        verbose_name_plural= 'Calificaciones'
        unique_together = ('course', 'student', 'curso_academico')
      

class NotaIndividual(models.Model):
    calificacion = models.ForeignKey(Calificaciones, on_delete=models.CASCADE, related_name='notas', verbose_name='Calificación')
    valor = models.PositiveIntegerField(verbose_name='Valor de la Nota')
    fecha_creacion = models.DateField(auto_now_add=True, verbose_name='Fecha de Creación')

    def __str__(self):
        return f"Nota {self.valor} para {self.calificacion.student.username} en {self.calificacion.course.name}"

    class Meta:
        verbose_name = 'Nota Individual'
        verbose_name_plural = 'Notas Individuales'
        ordering = ['fecha_creacion'] # Opcional: ordenar notas por fecha

@receiver(post_save, sender=NotaIndividual)
@receiver(post_delete, sender=NotaIndividual)
def update_calificaciones_average(sender, instance, **kwargs):
    calificacion = instance.calificacion
    calificacion.save() # This will trigger the calcular_promedio and update the average
      


    
    

