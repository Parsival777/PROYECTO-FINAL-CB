#!/usr/bin/env python3
"""
Aplicación Segura - Proyecto Final de Ciberseguridad
Versión con correcciones aplicadas: SQL Injection, XSS e IDOR
Incluye logging estructurado para SOC
"""

import os
import sqlite3
import logging
import logging.handlers
from datetime import datetime
from flask import Flask, request, render_template_string, g, redirect, url_for, session, abort
import bleach

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_change_in_production')

DATABASE = 'lab_app_secure.db'

# ============================================================================
# CONFIGURACIÓN DE LOGGING ESTRUCTURADO PARA SOC
# ============================================================================
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'evidencias')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'security.log')

# Configurar logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# Handler de archivo con rotación
file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, maxBytes=10*1024*1024, backupCount=5
)
file_handler.setLevel(logging.INFO)

# Formato estructurado ISO-8601
formatter = logging.Formatter(
    '{"timestamp": "%(asctime)s", '
    '"level": "%(levelname)s", '
    '"ip": "%(ip)s", '
    '"user": "%(user)s", '
    '"endpoint": "%(endpoint)s", '
    '"method": "%(method)s", '
    '"status": %(status)s, '
    '"type": "%(event_type)s", '
    '"details": "%(details)s"}',
    datefmt='%Y-%m-%dT%H:%M:%S%z'
)
file_handler.setFormatter(formatter)
security_logger.addHandler(file_handler)

def log_security_event(event_type, status, details="", user="anonymous", endpoint="/"):
    """Registra eventos de seguridad en formato estructurado"""
    ip = request.remote_addr if request else "0.0.0.0"
    method = request.method if request else "GET"
    
    security_logger.info(
        "",
        extra={
            'ip': ip,
            'user': user,
            'endpoint': endpoint,
            'method': method,
            'status': status,
            'event_type': event_type,
            'details': details
        }
    )

# ============================================================================
# VALIDACIÓN DE INPUT CON DEFENSA EN PROFUNDIDAD
# ============================================================================
def validate_product_input(query):
    """Valida y sanitiza input de búsqueda con lista blanca estricta"""
    if not query:
        return ""
    
    # Validación estricta de tipo y rango
    if not isinstance(query, str):
        log_security_event("INVALID_INPUT_BLOCKED", 400, f"Tipo inválido: {type(query)}")
        raise ValueError("Tipo de entrada inválido")
    
    # Límite de longitud
    if len(query) > 100:
        log_security_event("INVALID_INPUT_BLOCKED", 400, f"Input demasiado largo: {len(query)} chars")
        raise ValueError("Input excede longitud máxima")
    
    # Sanitización con bleach (lista blanca estricta)
    sanitized = bleach.clean(
        query,
        tags=[],
        attributes={},
        strip=True
    )
    
    # Detectar caracteres sospechosos
    suspicious_patterns = ["'", '"', "--", ";", "/*", "*/", "<", ">", "script", "union", "select"]
    for pattern in suspicious_patterns:
        if pattern.lower() in sanitized.lower():
            log_security_event("INVALID_INPUT_BLOCKED", 400, f"Patrón sospechoso detectado: {pattern}")
            raise ValueError(f"Caracteres no permitidos detectados")
    
    return sanitized

def validate_user_input(value, max_length=50, field_name="input"):
    """Valida input de usuario con reglas estrictas"""
    if not isinstance(value, str):
        return value
    
    if len(value) > max_length:
        log_security_event("INVALID_INPUT_BLOCKED", 400, f"{field_name} excede longitud")
        raise ValueError(f"{field_name} excede longitud máxima")
    
    # Detectar intentos de inyección
    sql_patterns = ["'", "--", ";", "/*", "*/", "xp_", "sp_", "exec(", "execute("]
    for pattern in sql_patterns:
        if pattern in value.lower():
            log_security_event("SQL_INJECTION_ATTEMPT", 400, f"Patrón SQL detectado: {pattern}")
            raise ValueError("Caracteres prohibidos detectados")
    
    return value


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'user',
                api_key TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL,
                category TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE user_profiles (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                bio TEXT,
                medical_history TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        users = [
            ('admin', 'admin123', 'admin@tecmihealth.edu', 'admin', 'sk_live_abc123xyz789'),
            ('user1', 'password1', 'user1@tecmihealth.edu', 'user', 'sk_live_def456uvw123'),
            ('user2', 'password2', 'user2@tecmihealth.edu', 'user', 'sk_live_ghi789rst345'),
            ('user3', 'password3', 'user3@tecmihealth.edu', 'user', 'sk_live_jkl012mno345'),
            ('reception1', 'pass_rec1', 'recep1@tecmihealth.edu', 'user', 'sk_live_pqr678stu901'),
        ]
        
        for username, password, email, role, api_key in users:
            cursor.execute(
                'INSERT INTO users (username, password, email, role, api_key) VALUES (?, ?, ?, ?, ?)',
                (username, password, email, role, api_key)
            )
        
        products = [
            ('Paracetamol', 'Analgésico y antipirético de primera línea', 125.50, 'Farmacia'),
            ('Ibuprofeno', 'Antiinflamatorio no esteroideo', 98.00, 'Farmacia'),
            ('Vitamin C', 'Suplemento vitalicioso con alta biodisponibilidad', 75.00, 'Farmacia'),
            ('Termómetro digital', 'Dispersión infrarroja de precisión clínica', 320.00, 'Equipos'),
            ('Mascarilla N95', 'Protección quirúrgica certificada', 180.00, 'Equipos'),
            ('Examen de sangre completo', 'Panel básico de hematología', 450.00, 'Laboratorio'),
            ('Rayos X torácico', 'Imagenología diagnóstica', 850.00, 'Imagenología'),
            ('Guitarra clínica Yamaha', 'Instrumento estetoscopio digital', 12500.00, 'Equipos'),
        ]
        
        for name, desc, price, category in products:
            cursor.execute(
                'INSERT INTO products (name, description, price, category) VALUES (?, ?, ?, ?)',
                (name, desc, price, category)
            )
        
        profiles = [
            (1, 'Dr. Carlos Méndez', 'Médico general con 15 años de experiencia', 'Hipertensión, Diabetes tipo 2'),
            (2, 'Ana Martínez', 'Recepcionista con certificación médica', 'Ninguna'),
            (3, 'Luis García', 'Paciente regular con historial completo', 'Asma, Alergias'),
            (4, 'María López', 'Paciente especial con condición crónica', 'EPOC, Obesidad mórbida'),
            (5, 'Pedro Sánchez', 'Recepcionista con formación clínica', 'Vacunas al día'),
        ]
        
        for user_id, name, bio, history in profiles:
            cursor.execute(
                'INSERT INTO user_profiles (user_id, full_name, bio, medical_history) VALUES (?, ?, ?, ?)',
                (user_id, name, bio, history)
            )
        
        conn.commit()
        conn.close()


# Base de datos inicial
if not os.path.exists(DATABASE):
    init_db()


# Templates CORREGIDOS
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head><title>Login - Tecmi Health</title></head>
<body>
    <h1>Iniciar Sesión - Tecmi Health</h1>
    {% if error %}<p style="color:red">{{ error }}</p>{% endif %}
    <form method="post">
        <label>Usuario: <input type="text" name="username" required></label><br><br>
        <label>Contraseña: <input type="password" name="password" required></label><br><br>
        <button type="submit">Entrar</button>
    </form>
    <p>Demostración: <a href="/search">Buscar productos</a></p>
</body>
</html>
'''

SEARCH_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head><title>Buscar Productos</title></head>
<body>
    <h1>Buscar Productos</h1>
    <form method="get">
        <input type="text" name="q" value="{{ query }}" placeholder="Buscar productos...">
        <button type="submit">Buscar</button>
    </form>
    {% if results %}
    <h2>Resultados:</h2>
    <ul>
        {% for p in results %}
        <li><strong>{{ p[1] }}</strong> - ${{ p[3] }}: {{ p[2] }}</li>
        {% endfor %}
    </ul>
    {% endif %}
    <p><a href="/login">Volver al login</a></p>
</body>
</html>
'''

PROFILE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head><title>Mi Perfil</title></head>
<body>
    <h1>Mi Perfil</h1>
    <p>Bienvenido, {{ username }}!</p>
    <table border="1">
        <tr><th>Datos del Perfil</th><th>Valor</th></tr>
        <tr><td>Nombre completo</td><td>{{ profile.full_name }}</td></tr>
        <tr><td>Breve biografía</td><td>{{ profile.bio }}</td></tr>
        <tr><td>Historial médico</td><td>{{ profile.medical_history }}</td></tr>
        <tr><td>API Key</td><td>{{ api_key }}</td></tr>
    </table>
    <p><a href="/search">Buscar productos</a></p>
    <p><a href="/logout">Cerrar sesión</a></p>
</body>
</html>
'''


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('profile'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # Validación de input
        try:
            username = validate_user_input(username, max_length=50, field_name="username")
            password = validate_user_input(password, max_length=100, field_name="password")
        except ValueError as e:
            log_security_event("AUTH_FAILED", 400, f"Validación rechazada: {str(e)}")
            error = 'Credenciales inválidas'
            return render_template_string(LOGIN_TEMPLATE, error=error)
        
        db = get_db()
        cursor = db.cursor()
        
        # ✅ DEFENSA EN PROFUNDIDAD SQL INJECTION:
        # 1. Consulta parametrizada
        # 2. Validación estricta de tipos
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        
        try:
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                log_security_event("AUTH_SUCCESS", 200, f"Login exitoso", user=user['username'])
                return redirect(url_for('profile'))
            else:
                log_security_event("AUTH_FAILED", 401, f"Credenciales inválidas para usuario: {username[:20]}")
                error = 'Credenciales inválidas'
        except Exception as e:
            log_security_event("AUTH_ERROR", 500, f"Error en autenticación: {str(e)}")
            error = 'Error en el sistema'
    
    return render_template_string(LOGIN_TEMPLATE, error=error)


@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = None
    
    if query:
        # ✅ DEFENSA EN PROFUNDIDAD SQL INJECTION:
        # 1. Validación estricta de input
        # 2. Sanitización con lista blanca
        # 3. Consulta parametrizada
        try:
            # Validar y sanitizar input
            sanitized_query = validate_product_input(query)
        except ValueError as e:
            log_security_event("INVALID_INPUT_BLOCKED", 400, f"Búsqueda rechazada: {str(e)}")
            return render_template_string(SEARCH_TEMPLATE, query="", results=None)
        
        db = get_db()
        cursor = db.cursor()
        
        # ✅ CORRECCIÓN SQL INJECTION: Consulta parametrizada
        sql_query = "SELECT * FROM products WHERE name LIKE ? OR description LIKE ?"
        search_term = f'%{sanitized_query}%'
        
        cursor.execute(sql_query, (search_term, search_term))
        results = cursor.fetchall()
    
    # ✅ CORRECCIÓN XSS: Escape automático aplicado
    # Flask templates escapan automáticamente {{ }}
    return render_template_string(SEARCH_TEMPLATE, query=query, results=results)


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    username = session['username']
    
    db = get_db()
    cursor = db.cursor()
    
    # ✅ DEFENSA EN PROFUNDIDAD IDOR:
    # 1. Solo acceder al perfil del usuario autenticado
    # 2. Validación de propiedad en consulta SQL
    cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
    profile = cursor.fetchone()
    
    cursor.execute('SELECT api_key FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    api_key = result[0] if result else None
    
    # ✅ CORRECCIÓN IDOR: Removido acceso a otros perfiles vía query params
    # Si alguien intenta acceder con user_id en query params, se registra
    view_id = request.args.get('user_id', type=int)
    if view_id:
        log_security_event("IDOR_UNAUTHORIZED_ACCESS", 403, 
                          f"Intento de acceso a perfil {view_id} por usuario {user_id}",
                          user=username)
        abort(404)  # Devolver 404 para no revelar existencia del recurso
    
    return render_template_string(
        PROFILE_TEMPLATE,
        username=username,
        profile=profile,
        api_key=api_key
    )


@app.route('/api/user/<int:user_id>')
def api_user(user_id):
    if 'user_id' not in session:
        log_security_event("AUTH_FAILED", 401, "API access without authentication")
        return {'error': 'Autenticación requerida'}, 401
    
    current_user_id = session['user_id']
    user_role = session.get('role')
    
    # ✅ DEFENSA EN PROFUNDIDAD IDOR:
    # 1. Validación de propiedad: usuario solo puede ver su propio recurso
    # 2. Admin puede ver todos
    if user_id != current_user_id and user_role != 'admin':
        log_security_event("IDOR_UNAUTHORIZED_ACCESS", 403, 
                          f"Usuario {current_user_id} intentó acceder a recurso {user_id}",
                          user=session.get('username', 'unknown'))
        return {'error': 'No autorizado'}, 403
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT id, username, email, role FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    if user:
        return {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'role': user[3]
            # ✅ CORRECCIÓN IDOR: API key no expuesto
        }
    return {'error': 'Usuario no encontrado'}, 404


@app.route('/logout')
def logout():
    username = session.get('username', 'unknown')
    session.clear()
    log_security_event("LOGOUT", 200, "Usuario cerró sesión", user=username)
    return redirect(url_for('login'))


# ============================================================================
# HEADERS DE SEGURIDAD CON CSP ESTRICTO
# ============================================================================
@app.after_request
def add_security_headers(response):
    """Añade headers de seguridad a todas las respuestas"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; frame-ancestors 'none'"
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response


# ============================================================================
# ENDPOINT DEBUG PARA GENERAR EVENTOS DE PRUEBA
# ============================================================================
@app.route('/debug')
def debug():
    """Endpoint de debug para generar eventos de prueba para SOC"""
    db = get_db()
    cursor = db.cursor()
    
    events = []
    
    # Evento SQL Injection intentado
    events.append({
        'type': 'SQL_INJECTION_ATTEMPT',
        'ip': '192.168.1.100',
        'endpoint': '/search',
        'payload': "' OR '1'='1",
        'timestamp': datetime.now().isoformat()
    })
    
    # Evento IDOR intentado
    events.append({
        'type': 'IDOR_ATTEMPT',
        'ip': '192.168.1.101',
        'endpoint': '/api/user/1',
        'user_agent': 'Mozilla/5.0',
        'timestamp': datetime.now().isoformat()
    })
    
    # Evento XSS intentado
    events.append({
        'type': 'XSS_ATTEMPT',
        'ip': '192.168.1.102',
        'endpoint': '/search',
        'payload': '<script>alert(1)</script>',
        'timestamp': datetime.now().isoformat()
    })
    
    # Evento auth fallido
    events.append({
        'type': 'AUTH_FAILED',
        'ip': '192.168.1.103',
        'endpoint': '/login',
        'details': 'Credenciales inválidas',
        'timestamp': datetime.now().isoformat()
    })
    
    # Evento rate limit
    events.append({
        'type': 'RATE_LIMIT_TRIGGERED',
        'ip': '192.168.1.104',
        'endpoint': '/search',
        'http_code': 429,
        'timestamp': datetime.now().isoformat()
    })
    
    return {'debug_events': events, 'count': len(events), 'endpoint': '/debug'}


@app.errorhandler(404)
def not_found(error):
    log_security_event("RESOURCE_NOT_FOUND", 404, "Recurso no encontrado")
    return {'error': 'No encontrado'}, 404


@app.errorhandler(429)
def rate_limited(error):
    log_security_event("RATE_LIMIT_TRIGGERED", 429, "Demasiadas peticiones")
    return {'error': 'Demasiadas peticiones'}, 429


if __name__ == '__main__':
    print("=" * 60)
    print("LAB DE CIBERSEGURIDAD - APLICACIÓN SEGURA")
    print("=" * 60)
    print("Versión con correcciones de seguridad aplicadas")
    print("Logging estructurado habilitado en: evidencias/security.log")
    print("=" * 60)
    print("\nCredenciales de prueba:")
    print("  admin / admin123 (rol: administrador)")
    print("  user1 / password1 (rol: usuario)")
    print("  user2 / password2 (rol: usuario)")
    print("\nAcceder a: http://localhost:5001")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5001)