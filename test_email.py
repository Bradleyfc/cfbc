#!/usr/bin/env python
"""
Script de prueba para verificar que el envío de correos funcione correctamente.
Ejecutar desde el directorio raíz del proyecto con: python test_email.py
"""

import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cfbc.settings')
django.setup()

from django.core.mail import send_mail

def test_email_aprobacion():
    """Función para probar el envío de correos de aprobación"""
    try:
        # Correo de aprobación
        asunto = '¡Enhorabuena! Su aplicación al curso Curso de Prueba ha sido aprobada'
        mensaje = '''¡Enhorabuena! Su aplicación al curso "Curso de Prueba" ha sido aprobada.

Ya puede acceder al curso y comenzar con las actividades académicas.

Saludos cordiales,
Centro Fray Bartolomé de las Casas'''
        
        # Cambiar este email por uno real para la prueba
        email_destino = 'test@example.com'  # Cambiar por un email real
        
        print(f"Enviando correo de APROBACIÓN a: {email_destino}")
        
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [email_destino],
            fail_silently=False,
        )
        
        print("✅ Correo de aprobación enviado exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error al enviar correo de aprobación: {str(e)}")
        return False

def test_email_denegacion():
    """Función para probar el envío de correos de denegación"""
    try:
        # Correo de denegación
        asunto = 'Su aplicación al curso Curso de Prueba ha sido denegada'
        mensaje = '''Lo sentimos! Su aplicación al curso "Curso de Prueba" ha sido denegada.

Le recomendamos revisar los requisitos del curso y considerar aplicar en futuras convocatorias.

Si tiene alguna pregunta, no dude en contactarnos.

Saludos cordiales,
Centro Fray Bartolomé de las Casas'''
        
        # Cambiar este email por uno real para la prueba
        email_destino = 'test@example.com'  # Cambiar por un email real
        
        print(f"Enviando correo de DENEGACIÓN a: {email_destino}")
        
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [email_destino],
            fail_silently=False,
        )
        
        print("✅ Correo de denegación enviado exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error al enviar correo de denegación: {str(e)}")
        return False

def test_email_cambio_contrasena():
    """Función para probar el envío de correos de cambio de contraseña"""
    try:
        from django.utils import timezone
        
        # Correo de cambio de contraseña
        asunto = 'Su contraseña ha sido cambiada satisfactoriamente'
        mensaje = f'''Estimado/a Usuario de Prueba,

Su contraseña ha sido cambiada satisfactoriamente en el Centro Fray Bartolomé de las Casas.

Si usted no realizó este cambio, por favor contacte inmediatamente con el administrador del sistema.

Fecha y hora del cambio: {timezone.now().strftime('%d/%m/%Y a las %H:%M')}

Saludos cordiales,
Centro Fray Bartolomé de las Casas'''
        
        # Cambiar este email por uno real para la prueba
        email_destino = 'test@example.com'  # Cambiar por un email real
        
        print(f"Enviando correo de CAMBIO DE CONTRASEÑA a: {email_destino}")
        
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [email_destino],
            fail_silently=False,
        )
        
        print("✅ Correo de cambio de contraseña enviado exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error al enviar correo de cambio de contraseña: {str(e)}")
        return False

if __name__ == '__main__':
    print("=== Prueba de configuración de correo ===")
    print(f"Configuración:")
    print(f"- Desde: {settings.DEFAULT_FROM_EMAIL}")
    print(f"- Host SMTP: {settings.EMAIL_HOST}")
    print(f"- Puerto: {settings.EMAIL_PORT}")
    print(f"- Usuario: {settings.EMAIL_HOST_USER}")
    print()
    
    print("1. Probando correo de APROBACIÓN...")
    test_email_aprobacion()
    print()
    
    print("2. Probando correo de DENEGACIÓN...")
    test_email_denegacion()
    print()
    
    print("3. Probando correo de CAMBIO DE CONTRASEÑA...")
    test_email_cambio_contrasena()
    print()
    
    print("=== Pruebas completadas ===")
    print("NOTA: Recuerda cambiar 'test@example.com' por un email real para las pruebas")