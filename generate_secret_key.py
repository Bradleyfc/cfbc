#!/usr/bin/env python
"""
Script para generar una nueva SECRET_KEY para Django
"""
from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    secret_key = get_random_secret_key()
    print("Nueva SECRET_KEY generada:")
    print(secret_key)
    print("\nCopia esta clave y úsala en tus variables de entorno de Render")