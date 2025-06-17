from django.urls import path
from . import views
from .views import ProfileView, CoursesView, CourseCreateView, CourseUpdateView, StudentListNotasView, AddNotaView

urlpatterns = [
    #pagina de inicio
    path('', views.HomeView.as_view(), name='home'),
    #pagona de lista de cursos
    #path('listadocursos/', views.ListadoCursosView.as_view(), name='listadocursos'),
    #pagina de cerrar sesion
    path('logout/', views.logout_view, name='logout_view'),
    #pagina de login y registro
    path('registro/', views.registro, name='registro'),
    #Pagina de vista del perfil
    path('profile/', ProfileView.as_view(), name='profile'),
    #pagina de vista de los cursos 
    path('cursos/', CoursesView.as_view(), name='cursos'),
    # pagina de creacion de cursos
    path('cursos/create/', CourseCreateView.as_view(), name='crear_cursos'),
    # ruta para inscribirse a un curso
    path('cursos/inscribirse/<int:curso_id>/', views.inscribirse_curso, name='inscribirse_curso'),
    # ruta para editar un curso
    path('cursos/editar/<int:pk>/', CourseUpdateView.as_view(), name='editar_curso'),
    # ruta para eliminar un curso
    path('cursos/eliminar/<int:curso_id>/', views.eliminar_curso, name='eliminar_curso'),
    # ruta de vista de notas en el perfil profesores
    path('cursos/<int:course_id>/', StudentListNotasView.as_view(), name='student_list_notas'),
    # ruta para agregar notas
     path('matricula/<int:matricula_id>/add_nota/', AddNotaView.as_view(), name='add_nota'),
    # ruta para redirigir despues del login
     path('login_redirect/', views.LoginRedirectView.as_view(), name='login_redirect'), 

]