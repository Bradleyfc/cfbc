#!/usr/bin/env python
"""
Script para codificar URLs de base de datos con caracteres especiales
"""
import urllib.parse

def encode_database_url(url):
    """Codifica una URL de base de datos"""
    # Ejemplo de uso:
    # postgresql://user:pass@word@host:5432/db
    # Se convierte en:
    # postgresql://user:pass%40word@host:5432/db
    
    print("URL original:", url)
    
    # Separar las partes de la URL
    parts = urllib.parse.urlparse(url)
    
    # Codificar el password si tiene caracteres especiales
    if parts.password:
        encoded_password = urllib.parse.quote(parts.password, safe='')
        encoded_url = url.replace(f':{parts.password}@', f':{encoded_password}@')
        print("URL codificada:", encoded_url)
        return encoded_url
    
    return url

if __name__ == '__main__':
    # Ejemplo de uso
    example_url = "postgresql://user:pass@word@host:5432/database"
    encode_database_url(example_url)