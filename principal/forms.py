from cProfile import label
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from accounts.models import Registro
from .models import Curso, Calificaciones, NotaIndividual # Importa NotaIndividual
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from django.forms import inlineformset_factory # Importa inlineformset_factory

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(label='Nombre', max_length=150, required=True)
    last_name = forms.CharField(label='Apellidos', max_length=150, required=True)
    email = forms.EmailField(label='Email', required=True)
    
    # Personalización de los campos de contraseña
    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text="La contraseña debe tener al menos 8 caracteres y no puede ser similar a su información personal.",
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text="Ingrese la misma contraseña que antes, para verificación.",
    )
    # Campos adicionales del modelo Registro
    nacionalidad = forms.CharField(label='Nacionalidad', max_length=150, required=True)
    carnet = forms.CharField(label='Carnet', max_length=11, required=True)
    SEXO = [
        ('M', 'Masculino'),
        ('F', 'Femenino')
    ]
    sexo = forms.ChoiceField(label='Sexo', choices=SEXO, required=True)
    image = forms.ImageField(label='Imagen de perfil', required=False)
    address = forms.CharField(label='Dirección', max_length=150, required=True)
    location = forms.CharField(label='Municipio', max_length=150, required=True)
    provincia = forms.CharField(label='Provincia', max_length=150, required=True)
    telephone = forms.CharField(label='Teléfono', max_length=50, required=True)
    movil = forms.CharField(label='Móvil', max_length=50, required=True)
    GRADO = [
        ("grado1", "Ninguno"),
        ("grado2", "Noveno Grado"),
        ("grado3", "Bachiller"),
        ("grado4", "Superior"),
    ]
    grado = forms.ChoiceField(label='Grado Académico', choices=GRADO, required=True)
    OCUPACION = [
        ("ocupacion1", "Desocupado"),
        ("ocupacion2", "Ama de Casa"),
        ("ocupacion3", "Trabajador Estatal"),
        ("ocupacion4", "Trabajador por Cuenta Propia"),
    ]
    ocupacion = forms.ChoiceField(label='Ocupación', choices=OCUPACION, required=True)
    titulo = forms.CharField(label='Título', max_length=50, required=True)
    



   
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                "Las contraseñas no coinciden. Por favor, asegúrese de escribir la misma contraseña en ambos campos.",
                code='password_mismatch',
            )
        return password2
    
    def save(self, commit=True):
        # Primero guardamos el usuario usando el método save de UserCreationForm
        # Usamos commit=False para no guardar inmediatamente y poder modificar el registro
        user = super().save(commit=False)
        
        # Guardamos el usuario para que se cree el registro a través de la señal
        if commit:
            user.save()
            
            # Esperamos a que la señal cree el registro y luego lo actualizamos
            try:
                # Ahora actualizamos el modelo Registro asociado que fue creado por la señal
                registro = user.registro
                registro.nacionalidad = self.cleaned_data.get('nacionalidad', '')
                registro.carnet = self.cleaned_data.get('carnet', '')
                registro.sexo = self.cleaned_data.get('sexo', '')
                
                # Verificamos si hay una imagen en el formulario
                if 'image' in self.cleaned_data and self.cleaned_data['image']:
                    registro.image = self.cleaned_data['image']
                    
                registro.address = self.cleaned_data.get('address', '')
                registro.location = self.cleaned_data.get('location', '')
                registro.provincia = self.cleaned_data.get('provincia', '')
                registro.telephone = self.cleaned_data.get('telephone', '')
                registro.movil = self.cleaned_data.get('movil', '')
                registro.grado = self.cleaned_data.get('grado', '')
                registro.ocupacion = self.cleaned_data.get('ocupacion', '')
                registro.titulo = self.cleaned_data.get('titulo', '')
                
                # Guardamos el registro
                registro.save()
                print(f"Registro guardado correctamente: {registro}")
            except Exception as e:
                print(f"Error al guardar el registro: {e}")
        
        return user

 #formulario de creacion de cursos 

from .models import CursoAcademico

class CourseForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(queryset=User.objects.filter(groups__name = 'Profesores'), label = 'Profesor')
    status = forms.ChoiceField(choices=Curso.STATUS_CHOICES, initial='I', label = 'Estado')
    description = forms.CharField(widget=forms.Textarea(attrs={'rows':3}))
    enrollment_deadline = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False, label='Fecha límite de inscripción')
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False, label='Fecha de inicio del curso')

    class Meta:
        model = Curso
        fields = ['image', 'name', 'description', 'teacher', 'class_quantity', 'status', 'enrollment_deadline', 'start_date', 'curso_academico']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obtener el CursoAcademico activo y establecerlo como valor inicial
        active_academic_course = CursoAcademico.objects.filter(activo=True).first()
        if active_academic_course:
            self.fields['curso_academico'].initial = active_academic_course
            self.fields['curso_academico'].widget = forms.HiddenInput() # Ocultar el campo si se asigna automáticamente
        else:
            # Si no hay un curso académico activo, el campo puede ser visible para selección manual o mostrar un error
            self.fields['curso_academico'].queryset = CursoAcademico.objects.all()

    helper= FormHelper()    
    helper.layout = Layout(
        Field('image'),
        Field('name'),
        Field('description'),
        Field('teacher'),
        Field('class_quantity'),
        Field('status'),
        Field('curso_academico'),
        Submit('submit','Submit')
    )


# formulario de creacion de notas

class CalificacionesForm(forms.ModelForm):
    class Meta:
        model = Calificaciones
        # Eliminamos los campos de nota fijos, ya que serán manejados por el formset
        fields = [] 

# Formulario para una nota individual
class NotaIndividualForm(forms.ModelForm):
    valor = forms.IntegerField(
        min_value=0,
        max_value=100,
        required=True,
        widget=forms.NumberInput(attrs={'min': 0, 'max': 100})
    )
    class Meta:
        model = NotaIndividual
        fields = ['valor']
        # The 'DELETE' field is handled by the formset and should not be excluded here.


# Formset para manejar múltiples notas individuales relacionadas con una Calificacion
NotaIndividualFormSet = inlineformset_factory(
    Calificaciones, 
    NotaIndividual, 
    form=NotaIndividualForm, 
    extra=1, # Número inicial de formularios vacíos a mostrar
    can_delete=True, # Permite eliminar notas existentes
    can_order=False # No permite reordenar las notas
)




