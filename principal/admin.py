from django.contrib import admin
from.models import Curso, Matriculas, Asistencia, Calificaciones, CursoAcademico, NotaIndividual # Importa NotaIndividual
# Register your models here.

from .models import CursoAcademico

class CursoAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'class_quantity', 'curso_academico')
    list_filter = ('teacher', 'curso_academico')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Only filter if the user is not a superuser
        if not request.user.is_superuser:
            # Check if a specific curso_academico is selected in the filter
            curso_academico_id = request.GET.get('curso_academico__id__exact') or request.GET.get('curso_academico__id__iexact')
            if curso_academico_id:
                # If a specific academic year is selected, filter by it
                qs = qs.filter(curso_academico__id=curso_academico_id)
            else:
                # If no specific academic year is selected, filter by the active one
                active_academic_year = CursoAcademico.objects.filter(activo=True).first()
                if active_academic_year:
                    qs = qs.filter(curso_academico=active_academic_year)
                else:
                    # If no active academic year and no filter, show no courses
                    qs = qs.none()
        return qs

admin.site.register(Curso, CursoAdmin)   

class MatriculasAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'curso_academico', 'estado', 'activo', 'fecha_matricula')
    list_filter = ('curso_academico', 'course', 'estado', 'activo')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'course__name')
    date_hierarchy = 'fecha_matricula'
    actions = ['aprobar_matriculas', 'promover_al_siguiente_curso']
    
    def aprobar_matriculas(self, request, queryset):
        queryset.update(estado='A')
    aprobar_matriculas.short_description = "Marcar matrículas seleccionadas como aprobadas"
    
    def promover_al_siguiente_curso(self, request, queryset):
        # Solo promover matrículas aprobadas
        aprobadas = queryset.filter(estado='A')
        curso_actual = CursoAcademico.objects.filter(activo=True).first()
        
        if not curso_actual:
            self.message_user(request, "No hay un curso académico activo configurado")
            return
            
        contador = 0
        for matricula in aprobadas:
            # Crear nueva matrícula en el curso actual
            Matriculas.objects.create(
                student=matricula.student,
                course=matricula.course,
                curso_academico=curso_actual,
                activo=True,
                estado='P'  # Comienza como pendiente en el nuevo curso
            )
            contador += 1
            
        self.message_user(request, f"{contador} matrículas han sido promovidas al curso {curso_actual}")
    promover_al_siguiente_curso.short_description = "Promover matrículas aprobadas al curso actual"

admin.site.register(Matriculas, MatriculasAdmin) 

class AsistenciaAdmin(admin.ModelAdmin):
    list_display= ('course' , 'student', 'date', 'presente')
    list_filter = ('course', 'student', 'date', 'presente')

admin.site.register(Asistencia, AsistenciaAdmin)   


class NotaIndividualInline(admin.TabularInline):
    model = NotaIndividual
    extra = 1 # Permite añadir una nota individual extra por defecto

class CalificacionesAdmin(admin.ModelAdmin):
    list_display= ('course' , 'student', 'average', 'display_notas_individuales') # Actualiza list_display
    list_filter = ('course', )
    exclude=('average',)
    inlines = [NotaIndividualInline] # Añade el inline para NotaIndividual

    def display_notas_individuales(self, obj):
        # Muestra las notas individuales como una lista en el admin
        notas = obj.notas.all().order_by('id')
        return ", ".join([f"{n.valor}" for n in notas])
    display_notas_individuales.short_description = 'Notas Individuales'

admin.site.register(Calificaciones, CalificacionesAdmin)  

class CursoAcademicoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo', 'archivado', 'fecha_creacion', 'ver_detalles_curso_academico')
    list_filter = ('activo', 'archivado')
    search_fields = ('nombre',)
    actions = ['activar_curso', 'archivar_curso', 'desarchivar_curso']
    
    def activar_curso(self, request, queryset):
        # Desactivar todos los cursos primero
        CursoAcademico.objects.all().update(activo=False)
        # Activar solo el seleccionado
        if queryset.count() > 0:
            curso = queryset.first()
            curso.activar()
            self.message_user(request, f"El curso {curso.nombre} ha sido activado")
    activar_curso.short_description = "Activar curso seleccionado (desactiva los demás)"
    
    def archivar_curso(self, request, queryset):
        # Archivar los cursos seleccionados
        contador = 0
        for curso in queryset:
            curso.archivar()
            contador += 1
        
        if contador == 1:
            self.message_user(request, f"El curso ha sido archivado")
        else:
            self.message_user(request, f"{contador} cursos han sido archivados")
    archivar_curso.short_description = "Archivar cursos seleccionados"
    
    def desarchivar_curso(self, request, queryset):
        # Desarchivar los cursos seleccionados (sin activarlos)
        queryset.update(archivado=False)
        contador = queryset.count()
        
        if contador == 1:
            self.message_user(request, f"El curso ha sido desarchivado")
        else:
            self.message_user(request, f"{contador} cursos han sido desarchivados")
    desarchivar_curso.short_description = "Desarchivar cursos seleccionados (sin activarlos)"

    def ver_detalles_curso_academico(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        url = reverse('principal:principal_cursoacademico_detail', args=[obj.pk])
        return format_html('<a href="{}">Detalles</a>', url)
    ver_detalles_curso_academico.short_description = 'Detalles'

admin.site.register(CursoAcademico, CursoAcademicoAdmin)

