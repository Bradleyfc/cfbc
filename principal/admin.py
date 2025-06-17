from django.contrib import admin
from.models import Curso, Matriculas, Asistencia, Calificaciones
# Register your models here.

class CursoAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'class_quantity')
    list_filter = ('teacher',)

admin.site.register(Curso, CursoAdmin)   

class MatriculasAdmin(admin.ModelAdmin):
    list_display= ('course' , 'student', 'activo')
    list_filter = ('course', 'student', 'activo')

admin.site.register(Matriculas, MatriculasAdmin) 

class AsistenciaAdmin(admin.ModelAdmin):
    list_display= ('course' , 'student', 'date', 'presente')
    list_filter = ('course', 'student', 'date', 'presente')

admin.site.register(Asistencia, AsistenciaAdmin)   


class CalificacionesAdmin(admin.ModelAdmin):
    list_display= ('course' , 'student', 'nota_1', 'nota_2', 'nota_3', 'nota_4', 'nota_5', 'nota_6', 'average')
    list_filter = ('course', )
    exclude=('average',)

admin.site.register(Calificaciones, CalificacionesAdmin)  

