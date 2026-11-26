#!/usr/bin/env python3
"""
Aplicación Segura - Proyecto Final de Ciberseguridad
Versión con correcciones aplicadas: SQL Injection, XSS e IDOR
"""

import os
import sqlite3
from flask import Flask, request, render_template_string, g, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'lab_ciberseguridad_2026_secret_key'

DATABASE = 'lab_app_secure.db'


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
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor()
        
        # ✅ CORRECCIÓN SQL INJECTION: Consulta parametrizada
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('profile'))
        else:
            error = 'Credenciales inválidas'
    
    return render_template_string(LOGIN_TEMPLATE, error=error)


@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = None
    
    if query:
        db = get_db()
        cursor = db.cursor()
        
        # ✅ CORRECCIÓN SQL INJECTION: Consulta parametrizada
        sql_query = "SELECT * FROM products WHERE name LIKE ? OR description LIKE ?"
        search_term = f'%{query}%'
        
        cursor.execute(sql_query, (search_term, search_term))
        results = cursor.fetchall()
    
    # ✅ CORRECCIÓN XSS: Escape automático aplicado
    return render_template_string(SEARCH_TEMPLATE, query=query, results=results)


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    username = session['username']
    
    db = get_db()
    cursor = db.cursor()
    
    # ✅ CORRECCIÓN IDOR: Solo ver perfil del usuario autenticado
    cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
    profile = cursor.fetchone()
    
    cursor.execute('SELECT api_key FROM users WHERE id = ?', (user_id,))
    api_key = cursor.fetchone()[0]
    
    # ✅ CORRECCIÓN IDOR: Removido acceso a otros perfiles vía query params
    
    return render_template_string(
        PROFILE_TEMPLATE,
        username=username,
        profile=profile,
        api_key=api_key
    )


@app.route('/api/user/<int:user_id>')
def api_user(user_id):
    if 'user_id' not in session:
        return {'error': 'Autenticación requerida'}, 401
    
    # ✅ CORRECCIÓN IDOR: Verificar propiedad del recurso
    if user_id != session['user_id'] and session.get('role') != 'admin':
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
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    print("=" * 60)
    print("LAB DE CIBERSEGURIDAD - APLICACIÓN SEGURA")
    print("=" * 60)
    print("Versión con correcciones de seguridad aplicadas")
    print("=" * 60)
    print("\nCredenciales de prueba:")
    print("  admin / admin123 (rol: administrador)")
    print("  user1 / password1 (rol: usuario)")
    print("  user2 / password2 (rol: usuario)")
    print("\nAcceder a: http://localhost:5001")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5001)