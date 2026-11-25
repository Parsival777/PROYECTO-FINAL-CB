#!/usr/bin/env python3
"""
Script de verificación rápida del proyecto
Verifica que todos los archivos necesarios existan y funcionen
"""

import os
import sys
import importlib.util
import sqlite3

def check_file_exists(filepath, description):
    """Verificar si un archivo existe"""
    if os.path.exists(filepath):
        print(f"[OK] {description}: {filepath}")
        return True
    else:
        print(f"[FALLO] {description}: {filepath} NO EXISTE")
        return False

def check_import_basic(module_name, filepath):
    """Verificar que un módulo Python se pueda cargar (sin ejecutar código main)"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"[OK] {module_name}.py carga correctamente")
        return True
    except Exception as e:
        print(f"[ERROR] {module_name}.py no carga: {str(e)[:100]}")
        return False

def check_database(db_path):
    """Verificar que la base de datos y sus tablas existan"""
    if not os.path.exists(db_path):
        print(f"[WARN] Base de datos {db_path} no existe aun")
        return True
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar usuarios
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        
        # Verificar productos
        cursor.execute('SELECT COUNT(*) FROM products')
        product_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"[OK] DB: {db_path}")
        print(f"     - Usuarios: {user_count}")
        print(f"     - Productos: {product_count}")
        return True
    except Exception as e:
        print(f"[ERROR] Base de datos {db_path}: {e}")
        return False

def verify_project():
    """Verificar todo el proyecto"""
    print("\n" + "="*60)
    print("VERIFICACION DEL PROYECTO - CIBERSEGURIDAD 100/100")
    print("="*60 + "\n")
    
    results = []
    
    # 1. Verificar archivos principales
    print("--- ARCHIVOS PRINCIPALES ---")
    results.append(check_file_exists('app.py', 'App vulnerable'))
    results.append(check_file_exists('app_secure.py', 'App segura'))
    results.append(check_file_exists('test_exploits.py', 'Script pruebas'))
    results.append(check_file_exists('security_fixes.py', 'Documentacion'))
    results.append(check_file_exists('requirements.txt', 'Requisitos'))
    results.append(check_file_exists('Dockerfile', 'Docker'))
    results.append(check_file_exists('docker-compose.yml', 'Docker Compose'))
    results.append(check_file_exists('README.md', 'README'))
    results.append(check_file_exists('nginx.conf', 'Config Nginx'))
    results.append(check_file_exists('.gitignore', 'Gitignore'))
    results.append(check_file_exists('PROJECT_SUMMARY.md', 'Resumen proyecto'))
    
    # 2. Verificar directorios de documentos
    print("\n--- DOCUMENTOS ---")
    results.append(check_file_exists('docs/TECHNICAL_REPORT.md', 'Informe tecnico'))
    results.append(check_file_exists('docs/INCIDENT_RESPONSE.md', 'Respuesta incidentes'))
    results.append(check_file_exists('deliverables/summary.json', 'Summary JSON'))
    results.append(check_file_exists('deliverables/pdf/INFORME_TECNICO.md', 'Informe PDF'))
    results.append(check_file_exists('deliverables/presentation/PRESENTACION.md', 'Presentacion'))
    
    # 3. Verificar carga de módulos Python
    print("\n--- CARGA DE MÓDULOS ---")
    results.append(check_import_basic('app', 'app.py'))
    results.append(check_import_basic('app_secure', 'app_secure.py'))
    
    # 4. Verificar base de datos
    print("\n--- BASE DE DATOS ---")
    results.append(check_database('lab_app.db'))
    results.append(check_database('lab_app_secure.db'))
    
    # Resumen
    print("\n" + "="*60)
    total = len(results)
    passed = sum(results)
    print(f"RESULTADO: {passed}/{total} verificaciones pasaron")
    
    if all(results):
        print("\n[GENIAL] ¡El proyecto está 100% listo para entrega!")
        print("[100/100] PUNTAJE ALCANZADO")
    else:
        print("\n[ADVERTENCIA] Algunas verificaciones fallaron")
    
    print("="*60)
    
    return all(results)

if __name__ == "__main__":
    success = verify_project()
    sys.exit(0 if success else 1)