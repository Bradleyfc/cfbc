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
# Create your views here.
from django.views.generic import TemplateView, CreateView
from .models import Calificaciones, Curso, Matriculas
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
#obteniendo los datos de cursos
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        courses = Curso.objects.all()
        # Group courses into chunks of four for the carousel
        grouped_courses = [courses[i:i + 4] for i in range(0, len(courses), 4)]
        context['grouped_courses'] = grouped_courses
        return context


class ListadoCursosView(BaseContextMixin, TemplateView):
    template_name = 'cursos.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

# para cerrar sesion


def logout_view(request):
    logout(request)
    return redirect('home')


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
            return redirect('home')
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
            if user.groups.filter(name='Profesores').exists():
                return redirect('profile')  # Redirige a la página de perfil del profesor
            else:
                return redirect('cursos')  # Redirige a la página de cursos para otros usuarios
        return redirect('home') # Redirige a home si no está autenticado (aunque LoginRequiredMixin ya lo manejaría)



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
    success_url = reverse_lazy('cursos')

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
        # Crear nueva matrícula
        matricula = Matriculas(course=curso, student=estudiante, activo=True)
        matricula.save()
        messages.success(
            request, f'Te has inscrito exitosamente al curso {curso.name}')
    else:
        messages.info(request, 'Ya estás inscrito en este curso')

    return redirect('cursos')

# Vista para editar un curso


class CourseUpdateView(BaseContextMixin, UpdateView):
    model = Curso
    form_class = CourseForm
    template_name = 'create_course.html'  # Reutilizamos el mismo template
    success_url = reverse_lazy('cursos')

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

    return redirect('cursos')

# Mostrar lista de alumnos y notas a los profesores


class StudentListNotasView(BaseContextMixin, TemplateView):
    template_name = 'student_list_notas.html'

    @override
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Curso, id=course_id)
        
        # Obtener solo las matrículas activas para este curso
        active_enrollments = Matriculas.objects.filter(course=course, activo=True)
        
        student_data = []
        for enrollment in active_enrollments:
            student = enrollment.student
            # Cambiado de .get() a .filter().first() para evitar MultipleObjectsReturned
            nota = Calificaciones.objects.filter(course=course, student=student).first()
            
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
                # Si no hay calificación para un estudiante matriculado, puedes decidir si lo incluyes
                # o no. Aquí lo incluimos con notas vacías para que el profesor pueda agregarlas.
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
        return context
# Agregar Notas de los estudiantes

class AddNotaView(BaseContextMixin, TemplateView):

    def get(self, request, matricula_id):
        matricula = get_object_or_404(Matriculas, id=matricula_id)
        try:
            # Buscar calificación por curso y estudiante de la matrícula
            calificacion = Calificaciones.objects.get(course=matricula.course, student=matricula.student)
            form = CalificacionesForm(instance=calificacion)
        except Calificaciones.DoesNotExist:
            form = CalificacionesForm()
        
        context = {
            'form': form,
            'matricula': matricula
        }
        return render(request, 'add_nota.html', context )
        
    def post(self, request, matricula_id):
        matricula = get_object_or_404(Matriculas, id=matricula_id)
        
        # Intenta obtener una calificación existente para esta matrícula
        try:
            # Buscar calificación por curso y estudiante de la matrícula
            calificacion = Calificaciones.objects.get(course=matricula.course, student=matricula.student)
            form = CalificacionesForm(request.POST, instance=calificacion)
        except Calificaciones.DoesNotExist:
            form = CalificacionesForm(request.POST)
    
        if form.is_valid():
            calificacion = form.save(commit=False)
            calificacion.matricula = matricula # Esta línea puede ser redundante si no hay un campo 'matricula' en Calificaciones
            calificacion.course = matricula.course
            calificacion.student = matricula.student
            calificacion.save()
            messages.success(request, 'Calificación guardada exitosamente.')
            return redirect('student_list_notas', course_id=matricula.course.id)
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