#!/usr/bin/env python3
"""
Documentación de Correcciones de Seguridad
Proyecto Final de Ciberseguridad
Versión con defensa en profundidad aplicada
"""

# ============== CORRECCIÓN 1: SQL INJECTION ==============
#
# ubicación: app.py - login() y search()
# riesgo: INYECCIÓN SQL - CRÍTICA - OWASP Top 10 #3
#
# VULNERABLE (app.py):
# ---------------------
# query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
# cursor.execute(query)
#
# CORREGIDO (app_secure.py):
# ---------------------------
# query = "SELECT * FROM users WHERE username = ? AND password = ?"
# cursor.execute(query, (username, password))
#
# DEFENSA EN PROFUNDIDAD APLICADA:
# ---------------------------------
# 1. ✅ Consultas parametrizadas con placeholders (?)
# 2. ✅ Validación estricta de tipos con isinstance()
# 3. ✅ Validación de longitud (username <= 50, password <= 100)
# 4. ✅ Detección de patrones SQL sospechosos (' -- ; /* etc.)
# 5. ✅ Sanitización con bleach (lista blanca)
# 6. ✅ Logging de intentos de inyección
# 7. ✅ Manejo seguro de errores sin exposición de detalles
#
# JUSTIFICACIÓN:
# - Uso de consultas parametrizadas previene que el input del usuario
#   sea interpretado como código SQL
# - El motor de base de datos maneja la escapada automáticamente
# - Elimina la posibilidad de alterar la lógica de la consulta
# - Validación previa reduce la superficie de ataque
# - Logging permite detección temprana de ataques

# ============== CORRECCIÓN 2: XSS (CROSS-SITE SCRIPTING) ==============
#
# ubicación: app.py - search()
# riesgo: XSS REFLEJADO - ALTA - OWASP Top 10 #10
#
# VULNERABLE (app.py):
# ---------------------
# <td>{{ p[2] | safe }}</td>  # "safe" deshabilita el escape HTML
#
# CORREGIDO (app_secure.py):
# ---------------------------
# <li><strong>{{ p[1] }}</strong> - ${{ p[3] }}: {{ p[2] }}</li>
# (Sin el filtro "safe", Flask escapa automáticamente el contenido)
#
# DEFENSA EN PROFUNDIDAD APLICADA:
# ---------------------------------
# 1. ✅ Escape automático de caracteres especiales (<, >, &, ", ')
# 2. ✅ Eliminación del filtro | safe en templates
# 3. ✅ Sanitización con bleach.clean() con lista blanca estricta (tags=[], attributes={})
# 4. ✅ Content-Security-Policy: default-src 'self'; script-src 'self'
# 5. ✅ X-XSS-Protection: 1; mode=block
# 6. ✅ X-Content-Type-Options: nosniff
# 7. ✅ Referrer-Policy: strict-origin-when-cross-origin
#
# JUSTIFICACIÓN:
# - Escape automático convierte <script> en &lt;script&gt;
# - Previene ejecución de JavaScript no confiable
# - CSP actúa como defensa de defensa (sandbox del navegador)
# - Headers de seguridad proporcionan defensa adicional
# - Bleach sanitiza cualquier caracteres sospechosos

# ============== CORRECCIÓN 3: IDOR (INSECURE DIRECT OBJECT REFERENCE) ==============
#
# ubicación: app.py - profile() y api_user()
# riesgo: IDOR - ALTA - OWASP Top 10 #1
#
# VULNERABLE (app.py):
# ---------------------
# view_id = request.args.get('user_id', type=int)
# cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (view_id,))
# # Sin verificar que el usuario actual tenga permiso para ver este perfil
#
# CORREGIDO (app_secure.py):
# ---------------------------
# # En profile(): Validación de propiedad con logging
# if view_id:
#     log_security_event("IDOR_UNAUTHORIZED_ACCESS", 403, ...)
#     abort(404)  # No revelar existencia del recurso
#
# # En api_user(): Verificación de propietario en consulta SQL
# if user_id != session['user_id'] and session.get('role') != 'admin':
#     return {'error': 'No autorizado'}, 403
#
# DEFENSA EN PROFUNDIDAD APLICADA:
# ---------------------------------
# 1. ✅ Validación de propiedad en consulta SQL
#    SELECT * FROM user_profiles WHERE id = ? AND user_id = ?
# 2. ✅ Role-based access control (RBAC) para administradores
# 3. ✅ Logging de intentos de acceso no autorizados
# 4. ✅ Respuesta 404 en lugar de 403 para no enumerar recursos
# 5. ✅ Eliminación de exposición de API keys sensibles
# 6. ✅ Principio de mínimo privilegio
# 7. ✅ Autenticación obligatoria para API
#
# JUSTIFICACIÓN:
# - Verificación de propietario antes de acceder a recursos
# - Role-based access control (RBAC) para administradores
# - Eliminación de exposición de API keys sensibles
# - Principio de mínimo privilegio
# - Logging permite detección de actividad anómala

# ============== HEADERS DE SEGURIDAD EN NGINX ==============
#
# ubicación: nginx.conf
#
# Headers implementados con valores recomendados por OWASP:

# Header | Valor | Propósito
# ------|-------|----------
# X-Frame-Options | DENY | Previene clickjacking
# X-Content-Type-Options | nosniff | Previene MIME sniffing
# X-XSS-Protection | 1; mode=block | XSS filter del navegador
# Content-Security-Policy | default-src 'self' | Previene XSS y inyección
# Referrer-Policy | strict-origin-when-cross-origin | Controla referencia
# Permissions-Policy | geolocation=(), microphone=() | Restringe APIs
# Strict-Transport-Security | max-age=31536000 | Fuerza HTTPS
# Cache-Control | no-store | Previene cache de datos sensibles

# ============== CONTROLES NGINX ADICIONALES ==============
#
# Implementados según Actividad 7:
#
# 1. Limitación de tasa (limit_req_zone):
#    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
#    limit_req zone=api_limit burst=20 nodelay;
#    limit_req_status 429;
#
# 2. Ocultamiento de huella tecnológica:
#    server_tokens off;
#    more_clear_headers 'Server';
#
# 3. Restricción de métodos HTTP:
#    if ($request_method !~ ^(GET|POST|PUT|DELETE)$) { return 405; }
#
# 4. Límite de tamaño de carga:
#    client_max_body_size 1M;

# ============== LOGGING ESTRUCTURADO PARA SOC ==============
#
# Ubicación: app_secure.py - evidencias/security.log
#
# Formato JSON con campos:
# {
#   "timestamp": "ISO-8601",
#   "level": "INFO/WARNING/ERROR",
#   "ip": "client IP",
#   "user": "username",
#   "endpoint": "/api/users",
#   "method": "GET/POST",
#   "status": 403,
#   "type": "IDOR_UNAUTHORIZED_ACCESS",
#   "details": "Descripción del evento"
# }
#
# Tipos de eventos loggeados:
# - AUTH_FAILED: Intentos de inicio de sesión fallidos
# - AUTH_SUCCESS: Login exitoso
# - IDOR_UNAUTHORIZED_ACCESS: Intentos de acceso a recursos ajenos
# - INVALID_INPUT_BLOCKED: Entradas rechazadas por validación
# - SQL_INJECTION_ATTEMPT: Intentos detectados de inyección SQL
# - RATE_LIMIT_TRIGGERED: Bloqueos por rate limiting

# ============== RESUMEN DE CONTROLES IMPLEMENTADOS ==============
#
# CONTRAS:
# 1. ✅ Consultas SQL parametrizadas
# 2. ✅ Escape automático de contenido (XSS)
# 3. ✅ Validación de permisos/roles (IDOR)
# 4. ✅ Headers de seguridad HTTP
# 5. ✅ Autenticación obligatoria para API
# 6. ✅ Registro de eventos de seguridad (/debug)
# 7. ✅ Rate limiting en NGINX (10r/s)
# 8. ✅ Ocultamiento de versión (server_tokens off)
# 9. ✅ Validación de método HTTP
# 10. ✅ Límite de tamaño de carga (1MB)

# CONTROLES ADICIONALES RECOMENDADOS (Parte B - Mejora organizacional):
# - Implementar HTTPS con certificado SSL/TLS
# - Agregar autenticación multifactor (MFA)
# - Configurar firewall de aplicación web (WAF)
# - Implementar sistema de detección de intrusiones (IDS)
# - Configurar alertas de seguridad
# - Políticas de contraseñas fuertes
# - Habilitar HTTP Strict Transport Security (HSTS)
# - Implementar logging centralizado
# - Integrar con SIEM/SOAR
# - Despliegue de EDR/XDR en endpoints

if __name__ == "__main__":
    print("=" * 60)
    print("CORRECCIONES DE SEGURIDAD - PROYECTO FINAL")
    print("=" * 60)
    print("\n1. SQL Injection ✅ CORREGIDA (Defensa en profundidad)")
    print("   - Consultas parametrizadas")
    print("   - Validación de tipos y rango")
    print("   - Sanitización con bleach")
    print("   - Logging de intentos")
    print("\n2. XSS ✅ CORREGIDA (Defensa en profundidad)")
    print("   - Escape automático HTML")
    print("   - Content-Security-Policy estricto")
    print("   - Headers de seguridad")
    print("\n3. IDOR ✅ CORREGIDA (Defensa en profundidad)")
    print("   - Validación de propietario en SQL")
    print("   - RBAC para admin")
    print("   - Logging de intentos")
    print("\n4. Headers de seguridad ✅ CONFIGURADOS")
    print("   X-Frame-Options, CSP, HSTS, etc.")
    print("\n5. NGINX ✅ CONFIGURADO")
    print("   Rate limiting, method restriction, size limits")
    print("=" * 60)