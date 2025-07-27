"""
Vista temporal para crear superusuario desde el navegador
IMPORTANTE: Eliminar después de usar por seguridad
"""
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import os

@csrf_exempt
def create_admin_user(request):
    """Vista para crear superusuario - SOLO PARA SETUP INICIAL"""
    
    # Solo permitir en modo DEBUG o con una clave especial
    setup_key = request.GET.get('key', '')
    expected_key = os.getenv('SETUP_KEY', 'setup123')
    
    if setup_key != expected_key:
        return HttpResponse("Acceso denegado. Clave incorrecta.", status=403)
    
    username = os.getenv('ADMIN_USERNAME', 'admin')
    email = os.getenv('ADMIN_EMAIL', 'admin@cfbc.edu.ni')
    password = os.getenv('ADMIN_PASSWORD', 'changeme123')
    
    try:
        # Eliminar usuario existente si existe
        User.objects.filter(username=username).delete()
        
        # Crear nuevo superusuario
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        response = f"""
        <h2>✅ Superusuario creado exitosamente</h2>
        <p><strong>Username:</strong> {username}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Password:</strong> {'*' * len(password)}</p>
        <p><a href="/admin/">Ir al Admin</a></p>
        <hr>
        <p><strong>IMPORTANTE:</strong> Elimina esta vista después de usar por seguridad</p>
        """
        
        return HttpResponse(response)
        
    except Exception as e:
        return HttpResponse(f"❌ Error: {str(e)}", status=500)