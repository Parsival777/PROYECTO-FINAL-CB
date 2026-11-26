#!/usr/bin/env python3
"""
Aplicación de Laboratorio - Proyecto Final de Ciberseguridad
Laboratorio vulnerable con: SQL Injection, XSS e IDOR
"""

import os
import sqlite3
from flask import Flask, request, render_template_string, g, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'lab_ciberseguridad_2026_secret_key'

DATABASE = 'lab_app.db'


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


# Templates
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
    <p>Demostración SQL Injection: <a href="/search">Buscar productos</a></p>
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
    <table border="1">
        <tr><th>ID</th><th>Nombre</th><th>Descripción</th><th>Precio</th></tr>
        {% for p in results %}
        <tr>
            <td>{{ p[0] }}</td>
            <td>{{ p[1] }}</td>
            <td>{{ p[2] | safe }}</td>
            <td>${{ p[3] }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}
    <p><a href="/login">Volver al login</a></p>
    <p><a href="/profile">Ver mi perfil</a></p>
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
    <p><strong>Ver otros perfiles (IDOR):</strong></p>
    <form method="get">
        <input type="number" name="user_id" placeholder="ID de usuario">
        <button type="submit">Ver perfil</button>
    </form>
    {% if other_profile %}
    <h2>Perfil del usuario ID: {{ view_id }}</h2>
    <table border="1">
        <tr><th>Datos del Perfil</th><th>Valor</th></tr>
        <tr><td>Nombre completo</td><td>{{ other_profile.full_name }}</td></tr>
        <tr><td>Breve biografía</td><td>{{ other_profile.bio }}</td></tr>
        <tr><td>Historial médico</td><td>{{ other_profile.medical_history }}</td></tr>
        <tr><td>API Key</td><td>{{ other_api_key }}</td></tr>
    </table>
    {% endif %}
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
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor()
        
        # VULNERABILIDAD SQL INJECTION: Consulta sin parametrizar
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        
        try:
            cursor.execute(query)
            user = cursor.fetchone()
            
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                return redirect(url_for('profile'))
            else:
                error = 'Credenciales inválidas'
        except Exception as e:
            error = f'Error en la consulta: {str(e)}'
    
    return render_template_string(LOGIN_TEMPLATE, error=error)


@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = None
    
    if query:
        db = get_db()
        cursor = db.cursor()
        
        # VULNERABILIDAD SQL INJECTION: Consulta sin parametrizar
        sql_query = f"SELECT * FROM products WHERE name LIKE '%{query}%' OR description LIKE '%{query}%'"
        
        try:
            cursor.execute(sql_query)
            results = cursor.fetchall()
        except Exception as e:
            results = [('Error', str(e), 'Error', 0)]
    
    return render_template_string(SEARCH_TEMPLATE, query=query, results=results)


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    username = session['username']
    view_id = request.args.get('user_id', type=int)
    
    db = get_db()
    cursor = db.cursor()
    
    # Obtener perfil del usuario actual
    cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
    profile = cursor.fetchone()
    
    # Obtener API key del usuario actual
    cursor.execute('SELECT api_key FROM users WHERE id = ?', (user_id,))
    api_key = cursor.fetchone()[0]
    
    other_profile = None
    other_api_key = None
    
    # VULNERABILIDAD IDOR: Acceso a perfiles de otros usuarios sin verificación
    if view_id:
        cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (view_id,))
        other_profile = cursor.fetchone()
        cursor.execute('SELECT api_key FROM users WHERE id = ?', (view_id,))
        other_api_key = cursor.fetchone()[0] if cursor.fetchone() else None
    
    return render_template_string(
        PROFILE_TEMPLATE,
        username=username,
        profile=profile,
        api_key=api_key,
        other_profile=other_profile,
        other_api_key=other_api_key,
        view_id=view_id
    )


@app.route('/users')
def users():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, username, email, role FROM users')
    users = cursor.fetchall()
    
    html = '<h1>Lista de Usuarios</h1><table border="1"><tr><th>ID</th><th>Usuario</th><th>Email</th><th>Rol</th></tr>'
    for user in users:
        html += f'<tr><td>{user[0]}</td><td>{user[1]}</td><td>{user[2]}</td><td>{user[3]}</td></tr>'
    html += '</table>'
    
    return html


@app.route('/api/user/<int:user_id>')
def api_user(user_id):
    db = get_db()
    cursor = db.cursor()
    
    # VULNERABILIDAD IDOR: API pública sin autenticación
    cursor.execute('SELECT id, username, email, role, api_key FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    if user:
        return {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'role': user[3],
            'api_key': user[4]
        }
    return {'error': 'Usuario no encontrado'}, 404


@app.route('/debug')
def debug():
    """Endpoint de debug para generar eventos de prueba"""
    db = get_db()
    cursor = db.cursor()
    
    # Generar eventos de prueba para análisis de logs
    events = []
    
    # Evento SQL Injection intentado
    events.append({
        'type': 'SQL_INJECTION_ATTEMPT',
        'ip': '192.168.1.100',
        'endpoint': '/search',
        'payload': "' OR '1'='1",
        'timestamp': '2026-11-25T10:15:30Z'
    })
    
    # Evento IDOR intentado
    events.append({
        'type': 'IDOR_ATTEMPT',
        'ip': '192.168.1.101',
        'endpoint': '/api/user/1',
        'user_agent': 'Mozilla/5.0',
        'timestamp': '2026-11-25T10:20:45Z'
    })
    
    # Evento XSS intentado
    events.append({
        'type': 'XSS_ATTEMPT',
        'ip': '192.168.1.102',
        'endpoint': '/search',
        'payload': '<script>alert(1)</script>',
        'timestamp': '2026-11-25T10:25:00Z'
    })
    
    return {'debug_events': events, 'count': len(events)}


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    print("=" * 60)
    print("LAB DE CIBERSEGURIDAD - PROYECTO FINAL")
    print("=" * 60)
    print("Aplicación vulnerable con defectos intencionales")
    print("Propósito: Educativo/Demostrativo")
    print("=" * 60)
    print("\nCredenciales de prueba:")
    print("  admin / admin123 (rol: administrador)")
    print("  user1 / password1 (rol: usuario)")
    print("  user2 / password2 (rol: usuario)")
    print("\nAcceder a: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)