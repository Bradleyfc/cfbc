from typing import override
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.contrib import messages
from .forms import CustomUserCreationForm, CourseForm, CalificacionesForm
from django.contrib.auth.models import Group, User
from django.db.models import Q
from datetime import date, datetime # Añade 'datetime' aquí
from django.db.models import Q, Max # Asegúrate de que 'Max' esté importado

# Create your views here.

from django.views.generic import DetailView
from .models import CursoAcademico, Curso, Matriculas, Calificaciones, Asistencia

class CursoAcademicoDetailView(DetailView):
    model = CursoAcademico
    template_name = 'curso_academico_detail.html'
    context_object_name = 'curso_academico'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curso_academico = self.get_object()
        
        # Get all courses associated with this academic course
        # This assumes a direct or indirect link between Curso and CursoAcademico
        # If Curso does not have a direct link, you might need to filter through Matriculas
        context['cursos'] = Curso.objects.filter(matriculas__curso_academico=curso_academico).distinct()
        
        # Get all enrollments for this academic course
        context['matriculas'] = Matriculas.objects.filter(curso_academico=curso_academico)
        
        # Get all grades for this academic course
        context['calificaciones'] = Calificaciones.objects.filter(curso_academico=curso_academico)
        
        # Get all attendance records for this academic course
        # This might be more complex if Asistencia is not directly linked to CursoAcademico
        # For now, assuming it can be filtered via Matriculas or Curso
        context['asistencias'] = Asistencia.objects.filter(course__matriculas__curso_academico=curso_academico).distinct()

        return context
from django.views.generic import TemplateView, CreateView, ListView
from .models import Calificaciones, Curso, Matriculas, CursoAcademico
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin # Importar LoginRequiredMixin


class BaseContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        group_name = None
        if user.is_authenticated:
            group = Group.objects.filter(user=user).first()
            if group:
                group_name = group.name
            context['group_name'] = group_name
        return context


class HomeView(BaseContextMixin, TemplateView):
    template_name = 'home.html'

    @override
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        courses = Curso.objects.all()
        # Group courses into chunks of four for the carousel
        grouped_courses = [courses[i:i + 4] for i in range(0, len(courses), 4)]
        context['grouped_courses'] = grouped_courses
        student = self.request.user if self.request.user.is_authenticated else None

        for item in courses:
            if student:
                registration = Matriculas.objects.filter(
                    course=item, student=student).first()
                item.is_enrolled = registration is not None
            else:
                item.is_enrolled = False

            enrollment_count = Matriculas.objects.filter(course=item).count()
            item.enrollment_count = enrollment_count

        context['courses'] = courses
        return context



class ListadoCursosView(BaseContextMixin, TemplateView):
    template_name = 'cursos.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

# para cerrar sesion


def logout_view(request):
    logout(request)
    return redirect('principal:home')


# pagina de Registro
""" class RegisterView(View):
    def get(self, request):
        data = {
            'form': RegisterForm()
        }
        return render(request, 'registration/registro.html', data)

    def post(self, request):
        user_creation_form=RegisterForm(data=request.POST)
        if user_creation_form.is_valid():
            user_creation_form.save()  
            user = authenticate(username=user_creation_form.cleaned_data['username'],
                                password=user_creation_form.cleaned_data['password'])
            login(request, user)
            return redirect('principal:home')
        data = {
            'form':user_creation_form
        }   
        return render(request, 'registration/registro.html', data) """


def registro(request):
    data = {
        'form': CustomUserCreationForm()
    }

    if request.method == 'POST':
        user_creation_form = CustomUserCreationForm(
            data=request.POST, files=request.FILES)

        if user_creation_form.is_valid():
            # Guardamos el formulario y aseguramos que se procesen los archivos
            user = user_creation_form.save(commit=True)
            # Añadimos mensaje de éxito que se mostrará en el navegador
            messages.success(
                request, f"Usuario {user.username} creado correctamente")
            return redirect('login')
        else:
            # Añadimos mensaje de error para depuración
            print(f"Errores en el formulario: {user_creation_form.errors}")

    return render(request, 'registration/registro.html', data)

# Vista para manejar la redirección después del login

class LoginRedirectView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.groups.filter(name='Profesores').exists() or user.groups.filter(name='Administración').exists():
                return redirect('principal:profile')  # Redirige a la página de perfil del profesor o el admin
            else:
                return redirect('principal:cursos')  # Redirige a la página de cursos para otros usuarios
        return redirect('principal:home') # Redirige a home si no está autenticado (aunque LoginRequiredMixin ya lo manejaría)



    # Pagina de Perfil


class ProfileView(BaseContextMixin, TemplateView):
    template_name = 'profile/profile.html'

    @override
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.groups.first().name == 'Profesores':
            # Obtener todos los cursos asignados al profesor
            assigned_courses = Curso.objects.filter(teacher=user)
            context['assigned_courses'] = assigned_courses

        return context

# Vista de los Cursos


class CoursesView(BaseContextMixin, TemplateView):
    template_name = 'cursos.html'

    @override
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        courses = Curso.objects.all()
        student = self.request.user if self.request.user.is_authenticated else None

        for item in courses:
            if student:
                registration = Matriculas.objects.filter(
                    course=item, student=student).first()
                item.is_enrolled = registration is not None
            else:
                item.is_enrolled = False

            # Calcular el conteo de inscripciones para todos los cursos
            enrollment_count = Matriculas.objects.filter(course=item).count()
            item.enrollment_count = enrollment_count

        context['courses'] = courses
        # Asegurarse de que group_name esté en el contexto
        user = self.request.user
        if user.is_authenticated:
            group = Group.objects.filter(user=user).first()
            if group:
                context['group_name'] = group.name
            else:
                context['group_name'] = None
        else:
            context['group_name'] = None

        return context

# Crear nuevo Curso


class CourseCreateView(BaseContextMixin, CreateView):
    model = Curso
    form_class = CourseForm
    template_name = 'create_course.html'
    success_url = reverse_lazy('principal:cursos')

    @override
    def form_valid(self, form):
        messages.success(self.request, 'El Curso se guardo correctamente')
        return super().form_valid(form)

    @override
    def form_invalid(self, form):
        messages.error(
            self.request, 'Ha ocurrido un ERROR al guardar el Curso')
        return self.render_to_response(self.get_context_data(form=form))

# Vista para inscribirse a un curso


@login_required
def inscribirse_curso(request, curso_id):
    # Obtener el curso
    curso = Curso.objects.get(id=curso_id)
    estudiante = request.user

    # Verificar si ya está inscrito
    inscripcion_existente = Matriculas.objects.filter(
        course=curso, student=estudiante).exists()

    if not inscripcion_existente:
        # Obtener el curso académico activo
        curso_academico = CursoAcademico.objects.filter(activo=True).first()
        
        if not curso_academico:
            messages.error(request, 'No hay un curso académico activo configurado. Contacte al administrador.')
            return redirect('principal:cursos')
            
        # Crear nueva matrícula asignada al curso académico activo
        matricula = Matriculas(
            course=curso, 
            student=estudiante, 
            activo=True,
            curso_academico=curso_academico,
            estado='P'  # Estado inicial: Pendiente
        )
        matricula.save()
        messages.success(
            request, f'Te has inscrito exitosamente al curso {curso.name} para el año académico {curso_academico.nombre}')
    else:
        messages.info(request, 'Ya estás inscrito en este curso')

    return redirect('principal:cursos')

# Vista para editar un curso


class CourseUpdateView(BaseContextMixin, UpdateView):
    model = Curso
    form_class = CourseForm
    template_name = 'create_course.html'  # Reutilizamos el mismo template
    success_url = reverse_lazy('principal:cursos')

    @override
    def form_valid(self, form):
        messages.success(self.request, 'El Curso se actualizó correctamente')
        return super().form_valid(form)

    @override
    def form_invalid(self, form):
        messages.error(
            self.request, 'Ha ocurrido un ERROR al actualizar el Curso')
        return self.render_to_response(self.get_context_data(form=form))


# Vista para eliminar un curso
@login_required
def eliminar_curso(request, curso_id):
    # Verificar si el usuario pertenece al grupo 'Secretaría'
    if request.user.groups.filter(name='Secretaría').exists():
        try:
            # Obtener el curso
            curso = Curso.objects.get(id=curso_id)
            nombre_curso = curso.name

            # Eliminar el curso
            curso.delete()
            messages.success(
                request, f'El curso {nombre_curso} ha sido eliminado correctamente')
        except Curso.DoesNotExist:
            messages.error(request, 'El curso no existe')
    else:
        messages.error(request, 'No tienes permisos para eliminar cursos')

    return redirect('principal:cursos')

# Mostrar lista de alumnos y notas a los profesores


class StudentListNotasView(BaseContextMixin, ListView):
    model = Matriculas
    template_name = 'student_list_notas.html'
    context_object_name = 'matriculas'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'student',
            'course',
            'course__teacher',
            'calificaciones'
        )

        # Verificar si se está accediendo desde la URL con course_id
        course_id = self.kwargs.get('course_id')
        if course_id:
            queryset = queryset.filter(course__id=course_id)
            return queryset

        # Si no hay course_id en la URL, usar los filtros normales
        search_query = self.request.GET.get('search_query')
        course_filter = self.request.GET.get('course')
        teacher_filter = self.request.GET.get('teacher')

        if search_query:
            queryset = queryset.filter(
                Q(student__username__icontains=search_query) |
                Q(student__first_name__icontains=search_query) |
                Q(student__last_name__icontains=search_query)
            )


        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        course_id = self.kwargs.get('course_id')
        if course_id:
            course = get_object_or_404(Curso, id=course_id)
            context['course'] = course

            # Obtener el curso académico activo
            curso_academico_activo = CursoAcademico.objects.filter(activo=True).first()
            context['curso_academico'] = curso_academico_activo

            # Obtener solo las matrículas activas para este curso y curso académico activo
            active_enrollments = Matriculas.objects.filter(
                course=course,
                activo=True,
                curso_academico=curso_academico_activo
            )

            student_data = []
            for enrollment in active_enrollments:
                student = enrollment.student
                # Buscar calificación por curso, estudiante y curso académico
                nota = Calificaciones.objects.filter(
                    course=course,
                    student=student,
                    curso_academico=curso_academico_activo
                ).first()

                if nota:
                    matricula_id = enrollment.id

                    student_data.append({
                        'nota_id': nota.id,
                        'name': student.get_full_name(),
                        'nota_1': nota.nota_1,
                        'nota_2': nota.nota_2,
                        'nota_3': nota.nota_3,
                        'nota_4': nota.nota_4,
                        'nota_5': nota.nota_5,
                        'nota_6': nota.nota_6,
                        'average': nota.average,
                        'matricula_id': matricula_id,
                    })
                else:
                    # Si no hay calificación para un estudiante matriculado, lo incluimos con notas vacías
                    student_data.append({
                        'nota_id': None,
                        'name': student.get_full_name(),
                        'nota_1': None,
                        'nota_2': None,
                        'nota_3': None,
                        'nota_4': None,
                        'nota_5': None,
                        'nota_6': None,
                        'average': None,
                        'matricula_id': enrollment.id,
                    })
            context['student_data'] = student_data
        else:
            context['courses'] = CursoAcademico.objects.all()
            context['teachers'] = User.objects.filter(groups__name='Docente')
        
        # Obtener el curso académico activo
        curso_academico_activo = CursoAcademico.objects.filter(activo=True).first()
        
        # Obtener solo las matrículas activas para este curso y curso académico activo
        active_enrollments = Matriculas.objects.filter(
            course=course, 
            activo=True,
            curso_academico=curso_academico_activo
        )
        
        student_data = []
        for enrollment in active_enrollments:
            student = enrollment.student
            # Buscar calificación por curso, estudiante y curso académico
            nota = Calificaciones.objects.filter(
                course=course, 
                student=student,
                curso_academico=curso_academico_activo
            ).first()
            
            if nota:
                matricula_id = enrollment.id

                student_data.append({
                    'nota_id': nota.id,
                    'name': student.get_full_name(),
                    'nota_1': nota.nota_1,
                    'nota_2': nota.nota_2,
                    'nota_3': nota.nota_3,
                    'nota_4': nota.nota_4,
                    'nota_5': nota.nota_5,
                    'nota_6': nota.nota_6,
                    'average': nota.average,
                    'matricula_id': matricula_id,
                })
            else:
                # Si no hay calificación para un estudiante matriculado, lo incluimos con notas vacías
                student_data.append({
                    'nota_id': None,
                    'name': student.get_full_name(),
                    'nota_1': None,
                    'nota_2': None,
                    'nota_3': None,
                    'nota_4': None,
                    'nota_5': None,
                    'nota_6': None,
                    'average': None,
                    'matricula_id': enrollment.id,
                })

        context['course'] = course
        context['student_data'] = student_data
        context['curso_academico'] = curso_academico_activo
        return context
# Agregar Notas de los estudiantes

class AddNotaView(BaseContextMixin, TemplateView):

    def get(self, request, matricula_id):
        matricula = get_object_or_404(Matriculas, id=matricula_id)
        print(f"[GET] Matricula ID: {matricula_id}")
        print(f"[GET] Matricula Course ID: {matricula.course.id}")
        print(f"[GET] Matricula Student ID: {matricula.student.id}")
        print(f"[GET] Matricula Curso Academico ID: {matricula.curso_academico.id if matricula.curso_academico else 'None'}")

        try:
            # Buscar calificación por curso, estudiante y curso académico de la matrícula
            calificacion = Calificaciones.objects.get(
                course=matricula.course, 
                student=matricula.student,
                curso_academico=matricula.curso_academico
            )
            print("[GET] Existing Calificacion found.")
            form = CalificacionesForm(instance=calificacion)
        except Calificaciones.DoesNotExist:
            print("[GET] Calificaciones.DoesNotExist raised. No existing Calificacion found.")
            form = CalificacionesForm()
        
        context = {
            'form': form,
            'matricula': matricula
        }
        return render(request, 'add_nota.html', context)
        
    def post(self, request, matricula_id):
        matricula = get_object_or_404(Matriculas, id=matricula_id)
        print(f"[POST] Matricula ID: {matricula_id}")
        print(f"[POST] Matricula Course ID: {matricula.course.id}")
        print(f"[POST] Matricula Student ID: {matricula.student.id}")
        print(f"[POST] Matricula Curso Academico ID: {matricula.curso_academico.id if matricula.curso_academico else 'None'}")

        # Intenta obtener una calificación existente para esta matrícula
        try:
            # Buscar calificación por curso, estudiante y curso académico de la matrícula
            calificacion = Calificaciones.objects.get(
                course=matricula.course, 
                student=matricula.student,
                curso_academico=matricula.curso_academico
            )
            print("[POST] Existing Calificacion found.")
            form = CalificacionesForm(request.POST, instance=calificacion)
        except Calificaciones.DoesNotExist:
            print("[POST] Calificaciones.DoesNotExist raised. No existing Calificacion found. Creating new one.")
            # Si no existe, crea una nueva instancia de Calificaciones
            calificacion = Calificaciones(
                course=matricula.course,
                student=matricula.student,
                matricula=matricula,
                curso_academico=matricula.curso_academico
            )
            form = CalificacionesForm(request.POST, instance=calificacion)
        
        if form.is_valid():
            calificacion = form.save(commit=False)
            # Asegurarse de que los campos de relación estén correctamente asignados
            calificacion.matricula = matricula
            calificacion.course = matricula.course
            calificacion.student = matricula.student
            calificacion.curso_academico = matricula.curso_academico
            print(f"[POST] Saving Calificacion with Course ID: {calificacion.course.id}, Student ID: {calificacion.student.id}, Curso Academico ID: {calificacion.curso_academico.id if calificacion.curso_academico else 'None'}")
            calificacion.save()
            messages.success(request, 'Calificación guardada exitosamente.')
            return redirect('principal:student_list_notas_by_course', course_id=matricula.course.id)
        context = {
            'form': form,
            'matricula': matricula
        }
        return render(request, 'add_nota.html', context)

#esto es de la ia
""" def crear_cursos(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES) # Asegúrate de incluir request.FILES aquí
        if form.is_valid():
            form.save()
            # Por ejemplo, puedes añadir un mensaje de éxito y redirigir
            # messages.success(request, 'Curso creado exitosamente!')
            # return redirect('nombre_de_tu_url_de_cursos')
    else:
        form = CourseForm()
    return render(request, 'create_course.html', {'form': form})


def editar_curso(request, course_id):
    course = get_object_or_404(Curso, id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course) # Asegúrate de incluir request.FILES aquí
        if form.is_valid():
            form.save()
            # Por ejemplo, puedes añadir un mensaje de éxito y redirigir
            # messages.success(request, 'Curso actualizado exitosamente!')
            # return redirect('nombre_de_tu_url_de_cursos')
    else:
        form = CourseForm(instance=course)
    return render(request, 'edit_course.html', {'form': form, 'course': course})

 """

#vistas para historicos

def historico_alumno(request, student_id):
        matriculas = Matriculas.objects.filter(student_id=student_id).select_related('curso_academico')
        return render(request, 'historico.html', {'matriculas': matriculas})


# Agregando asistencias

class AsistenciaView(BaseContextMixin, TemplateView):
    template_name = 'asistencias.html'
    
    @override
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = kwargs['course_id']
        course = get_object_or_404(Curso, id=course_id)
        
        # Obtener el curso académico activo
        curso_academico_activo = CursoAcademico.objects.filter(activo=True).first()
        
        # Filtrar asistencias por curso y ordenar por fecha descendente
        asistencias = Asistencia.objects.filter(
            course=course,
            student__matriculas__curso_academico=curso_academico_activo,
            student__matriculas__activo=True
        ).select_related('student', 'course').order_by('-date')
        
        # Obtener todas las matrículas activas para este curso en el curso académico activo
        matriculas = Matriculas.objects.filter(
            course=course,
            activo=True,
            curso_academico=curso_academico_activo
        ).select_related('student')  # Optimizar consulta de estudiantes
        
        # Filtrar por fecha si se proporciona en la solicitud
        fecha_filtro = self.request.GET.get('fecha')
        if fecha_filtro:
            asistencias = asistencias.filter(date=fecha_filtro)
        
        # Calcular la cantidad de asistencias registradas (fechas únicas)
        asistencias_registradas = Asistencia.objects.filter(course=course).values('date').distinct().count()
        
        # Obtener la cantidad total de clases del curso
        cantidad_total_clases = course.class_quantity
        
        # Calcular las clases restantes
        clases_restantes = cantidad_total_clases - asistencias_registradas

        context['course'] = course
        context['asistencias'] = asistencias
        context['matriculas'] = matriculas
        context['curso_academico'] = curso_academico_activo
        context['cantidad_total_clases'] = cantidad_total_clases
        context['asistencias_registradas'] = asistencias_registradas
        context['clases_restantes'] = clases_restantes
        return context


class AddAsistenciaView(LoginRequiredMixin, TemplateView):
    template_name='add_asistencias.html'

    @override
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = kwargs['course_id']
        course = Curso.objects.get(id=course_id)
        matriculas = Matriculas.objects.filter(course=course)
        # Obtener las asistencias existentes para este curso
        asistencias = Asistencia.objects.order_by('date')
        context['course'] = course
        context['matriculas'] = matriculas
        context['asistencias'] = asistencias
        context['today'] = date.today()
        return context

    def post(self, request, course_id):
        course = Curso.objects.get(id=course_id)
        matriculas = Matriculas.objects.filter(course=course)

        if request.method == 'POST':
            date = request.POST.get('date')

            for matricula in matriculas:
                absent = request.POST.get('asistencia_' + str(matricula.id))
                # Buscar si ya existe un registro de asistencia para este estudiante en esta fecha
                asistencia, created = Asistencia.objects.get_or_create(
                    student=matricula.student,
                    course=course,
                    date=date,
                    defaults={'presente': not bool(absent)}
                )
                # Si el registro ya existía, actualizar el estado de presente
                if not created:
                    asistencia.presente = not bool(absent)
                    asistencia.save()
        # Redirigir a la misma página para mostrar las asistencias actualizadas
        return redirect('principal:asistencias', course_id=course_id)


# Eliminar asistencia
def eliminar_asistencia(request, asistencia_id):
    # Obtener la asistencia o devolver 404 si no existe
    asistencia = get_object_or_404(Asistencia, id=asistencia_id)
    
    # Guardar el ID del curso antes de eliminar la asistencia
    course_id = asistencia.course.id
    
    # Eliminar la asistencia
    asistencia.delete()
    
    # Redirigir a la página de asistencias del curso
    return redirect('principal:asistencias', course_id=course_id)


def add_asistencias(request, course_id):
    course = get_object_or_404(Curso, id=course_id)
    matriculas = Matriculas.objects.filter(course=course, activo=True)

    if request.method == 'POST':
        date_str = request.POST.get('date')
        try:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Formato de fecha inválido.")
            return redirect('principal:add_asistencias', course_id=course.id)

        # Eliminar asistencias existentes para esta fecha y curso
        Asistencia.objects.filter(course=course, date=attendance_date).delete()

        for matricula in matriculas:
            is_absent = request.POST.get(f'asistencia_{matricula.id}')
            presente = not bool(is_absent) # Si está marcado, significa que está ausente, por lo tanto, no presente

            Asistencia.objects.create(
                course=course,
                student=matricula.student,
                date=attendance_date,
                presente=presente
            )
        messages.success(request, "Asistencias guardadas correctamente.")
        return redirect('principal:asistencias', course_id=course.id) # Redirige a la página de asistencias del curso
    
    today = date.today()
    context = {
        'course': course,
        'matriculas': matriculas,
        'today': today,
    }
    return render(request, 'add_asistencias.html', context)


@login_required
def undo_last_asistencia(request, course_id):
    course = get_object_or_404(Curso, id=course_id)

    # Encontrar la fecha más reciente para la que se registró asistencia en este curso
    latest_attendance_date_obj = Asistencia.objects.filter(course=course).aggregate(Max('date'))
    latest_attendance_date = latest_attendance_date_obj['date__max']

    if latest_attendance_date:
        # Eliminar todos los registros de asistencia para este curso en la fecha más reciente
        Asistencia.objects.filter(course=course, date=latest_attendance_date).delete()
        messages.success(request, f"La asistencia del {latest_attendance_date.strftime('%d-%m-%Y')} ha sido deshecha correctamente.")
    else:
        messages.info(request, "No hay asistencias registradas para deshacer en este curso.")

    return redirect('principal:asistencias', course_id=course.id)

    

