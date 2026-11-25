#!/usr/bin/env python3
"""
Aplicación de Laboratorio de Ciberseguridad - Flask
Aplicación intencionalmente vulnerable para demostración académica
"""

import os
import sqlite3
from flask import Flask, request, render_template_string, g, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DATABASE = os.path.join(os.path.dirname(__file__) or '.', 'lab_app.db')

# Templates
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Lab Ciberseguridad - Login</title>
    <style>
        body { font-family: Georgia, serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        input { width: 100%; padding: 10px; font-size: 16px; }
        button { background: #0b6e5c; color: white; padding: 12px 24px; border: none; cursor: pointer; }
        button:hover { background: #085a48; }
        .nav { margin-bottom: 20px; }
        .nav a { margin-right: 15px; color: #0b6e5c; text-decoration: none; }
    </style>
</head>
<body>
    <div class="nav">
        <a href="/">Inicio</a>
        <a href="/search">Búsqueda</a>
        <a href="/profile">Perfil</a>
        <a href="/users">Usuarios</a>
    </div>
    <h1>Iniciar Sesión</h1>
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            {% for message in messages %}
                <p style="color: red;">{{ message }}</p>
            {% endfor %}
        {% endif %}
    {% endwith %}
    <form method="POST">
        <div class="form-group">
            <label>Usuario:</label>
            <input type="text" name="username" required>
        </div>
        <div class="form-group">
            <label>Contraseña:</label>
            <input type="password" name="password" required>
        </div>
        <button type="submit">Entrar</button>
    </form>
    <p>Credenciales de prueba: admin/admin123, user1/password1</p>
</body>
</html>
'''

SEARCH_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Lab Ciberseguridad - Búsqueda</title>
    <style>
        body { font-family: Georgia, serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        input { width: 100%; padding: 10px; font-size: 16px; }
        button { background: #0b6e5c; color: white; padding: 12px 24px; border: none; cursor: pointer; }
        .nav { margin-bottom: 20px; }
        .nav a { margin-right: 15px; color: #0b6e5c; text-decoration: none; }
        .result { margin-top: 20px; padding: 15px; background: #f6f8f7; }
        .error { color: red; }
        .vulnerable { background: #fff1dc; padding: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="nav">
        <a href="/">Inicio</a>
        <a href="/search">Búsqueda</a>
        <a href="/profile">Perfil</a>
        <a href="/users">Usuarios</a>
    </div>
    <h1>Búsqueda de Productos</h1>
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            {% for message in messages %}
                <p style="color: red;">{{ message }}</p>
            {% endfor %}
        {% endif %}
    {% endwith %}
    <form method="GET">
        <div class="form-group">
            <input type="text" name="q" value="{{ query }}" placeholder="Buscar producto..." required>
        </div>
        <button type="submit">Buscar</button>
    </form>
    
    {% if results %}
        <div class="result">
            <h3>Resultados:</h3>
            {% for product in results %}
                <div class="vulnerable">
                    <strong>{{ product.name }}</strong> - ${{ product.price }}
                    <br>Descripción: {{ product.description | safe }}
                </div>
            {% endfor %}
        </div>
    {% endif %}
</body>
</html>
'''

PROFILE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Lab Ciberseguridad - Perfil</title>
    <style>
        body { font-family: Georgia, serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        .nav { margin-bottom: 20px; }
        .nav a { margin-right: 15px; color: #0b6e5c; text-decoration: none; }
        .profile { background: #e6f0ec; padding: 20px; border-radius: 8px; }
        .warning { background: #fff1dc; padding: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="nav">
        <a href="/">Inicio</a>
        <a href="/search">Búsqueda</a>
        <a href="/profile">Perfil</a>
        <a href="/users">Usuarios</a>
    </div>
    <h1>Mi Perfil</h1>
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            {% for message in messages %}
                <p style="color: red;">{{ message }}</p>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    {% if user %}
        <div class="profile">
            <p><strong>ID de Usuario:</strong> {{ user.id }}</p>
            <p><strong>Usuario:</strong> {{ user.username }}</p>
            <p><strong>Correo:</strong> {{ user.email }}</p>
            <p><strong>Rol:</strong> {{ user.role }}</p>
            {% if user.bio %}
            <p class="warning"><strong>Bio:</strong> {{ user.bio }}</p>
            {% endif %}
        </div>
        
        <h2>Otros Usuarios (IDOR Vulnerable)</h2>
        <p>Intenta cambiar el parámetro <code>user_id</code> en la URL para ver otros perfiles.</p>
        <p>Ejemplo: <a href="/profile?user_id=1">/profile?user_id=1</a></p>
    {% else %}
        <p>Usuario no encontrado.</p>
    {% endif %}
</body>
</html>
'''

USERS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Lab Ciberseguridad - Usuarios</title>
    <style>
        body { font-family: Georgia, serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        .nav { margin-bottom: 20px; }
        .nav a { margin-right: 15px; color: #0b6e5c; text-decoration: none; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background: #0b6e5c; color: white; }
        .admin { color: #0b6e5c; font-weight: bold; }
    </style>
</head>
<body>
    <div class="nav">
        <a href="/">Inicio</a>
        <a href="/search">Búsqueda</a>
        <a href="/profile">Perfil</a>
        <a href="/users">Usuarios</a>
    </div>
    <h1>Lista de Usuarios</h1>
    <table>
        <thead>
            <tr><th>ID</th><th>Usuario</th><th>Email</th><th>Rol</th></tr>
        </thead>
        <tbody>
            {% for user in users %}
            <tr>
                <td>{{ user.id }}</td>
                <td>{{ user.username }}</td>
                <td>{{ user.email }}</td>
                <td class="{{ 'admin' if user.role == 'admin' else '' }}">{{ user.role }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
'''

HOME_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Lab Ciberseguridad - Inicio</title>
    <style>
        body { font-family: Georgia, serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        .nav { margin-bottom: 20px; }
        .nav a { margin-right: 15px; color: #0b6e5c; text-decoration: none; }
        .welcome { background: #dff0ea; padding: 20px; border-left: 4px solid #0b6e5c; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="nav">
        <a href="/">Inicio</a>
        <a href="/search">Búsqueda</a>
        <a href="/profile">Perfil</a>
        <a href="/users">Usuarios</a>
    </div>
    <h1>Bienvenido al Laboratorio de Ciberseguridad</h1>
    <div class="welcome">
        <p>Esta aplicación está diseñada para fines educativos. Contiene vulnerabilidades intencionales para demostrar conceptos de seguridad.</p>
        <p><strong>Usuarios disponibles:</strong></p>
        <ul>
            <li>admin / admin123 (rol: admin)</li>
            <li>user1 / password1 (rol: user)</li>
            <li>user2 / password2 (rol: user)</li>
        </ul>
    </div>
    
    {% if current_user %}
    <h2>Usuario Actual: {{ current_user.username }}</h2>
    <p><a href="/logout">Cerrar Sesión</a></p>
    {% else %}
    <p><a href="/">Ingresar</a></p>
    {% endif %}
</body>
</html>
'''

ERROR_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Georgia, serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center; }
        color: #8a4b00;
    </style>
</head>
<body>
    <h1>Error</h1>
    <p>{{ error }}</p>
    <p><a href="/">Volver al inicio</a></p>
</body>
</html>
'''


def get_db():
    """Obtener conexión a la base de datos"""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    """Cerrar conexión a la base de datos"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Inicializar la base de datos con datos de ejemplo"""
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                bio TEXT,
                api_key TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL
            )
        ''')
        
        # Usuarios de ejemplo
        users = [
            ('admin', 'admin123', 'admin@empresa.com', 'admin', 'Administrador principal', 'sk-admin-secret-12345'),
            ('user1', 'password1', 'user1@empresa.com', 'user', 'Usuario estándar con acceso completo', 'sk-user1-abcde'),
            ('user2', 'password2', 'user2@empresa.com', 'user', 'Usuario con permisos limitados', 'sk-user2-fghij'),
            ('user3', 'password3', 'user3@empresa.com', 'user', 'Usuario novato', 'sk-user3-klmno'),
        ]
        
        cursor.executemany(
            'INSERT INTO users (username, password, email, role, bio, api_key) VALUES (?, ?, ?, ?, ?, ?)',
            users
        )
        
        # Productos de ejemplo (con XSS posible en descripción)
        products = [
            ('Laptop Dell XPS', 'Laptop de alta gama para trabajo', 1299.99),
            ('Monitor 27" 4K', 'Pantalla ultra-wide 4K para diseño gráfico <script>alert("XSS")</script>', 449.99),
            ('Teclado Mecánico RGB', 'Teclado switch azul con retroiluminación', 89.99),
            ('Mouse Logitech MX', 'Mouse preciso con sensores ópticos', 59.99),
            ('Auriculares Bose QC', 'Cancelación de ruido activa', 349.99),
        ]
        
        cursor.executemany(
            'INSERT INTO products (name, description, price) VALUES (?, ?, ?)',
            products
        )
        
        conn.commit()
        conn.close()


@app.route('/')
def home():
    """Página de inicio"""
    return render_template_string(
        HOME_TEMPLATE,
        current_user=get_current_user()
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login de usuario"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
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
                return redirect(url_for('home'))
            else:
                flash('Credenciales inválidas')
        except Exception as e:
            flash(f'Error en la consulta: {str(e)}')
    
    return render_template_string(LOGIN_TEMPLATE)


@app.route('/logout')
def logout():
    """Logout de usuario"""
    session.clear()
    return redirect(url_for('home'))


def get_current_user():
    """Obtener usuario actual de la sesión"""
    if 'user_id' in session:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
        return cursor.fetchone()
    return None


@app.route('/search')
def search():
    """Buscar productos - VULNERABILIDAD SQL INJECTION y XSS"""
    query = request.args.get('q', '')
    results = []
    
    if query:
        db = get_db()
        cursor = db.cursor()
        
        # VULNERABILIDAD SQL INJECTION: Uso de f-string en consulta
        # El atacante puede inyectar: ' OR 1=1 --
        # O para ver otras tablas: ' UNION SELECT id,username,password,role FROM users --
        sql_query = f"SELECT * FROM products WHERE name LIKE '%{query}%' OR description LIKE '%{query}%'"
        
        try:
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            
            for row in rows:
                results.append({
                    'id': row['id'],
                    'name': row['name'],
                    'description': row['description'],
                    'price': row['price']
                })
        except Exception as e:
            # Mostrar error como evidencia de la vulnerabilidad
            results.append({
                'name': 'Error SQL',
                'description': f'Consulta fallida: {str(e)}',
                'price': 0
            })
    
    return render_template_string(
        SEARCH_TEMPLATE,
        query=query,
        results=results
    )


@app.route('/profile')
def profile():
    """Ver perfil de usuario - VULNERABILIDAD IDOR"""
    # Si no hay sesión activa, usar el primer usuario por defecto
    current_user_id = session.get('user_id', 1)
    requested_id = request.args.get('user_id', type=int, default=current_user_id)
    
    db = get_db()
    cursor = db.cursor()
    
    # VULNERABILIDAD IDOR: Acceso a cualquier usuario sin verificación
    # Un usuario autenticado como user1 (id=2) puede ver el perfil de admin (id=1)
    # cambiando el parámetro user_id en la URL
    cursor.execute('SELECT * FROM users WHERE id = ?', (requested_id,))
    user = cursor.fetchone()
    
    return render_template_string(
        PROFILE_TEMPLATE,
        user=user,
        current_user=get_current_user()
    )


@app.route('/users')
def users():
    """Listar todos los usuarios"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, username, email, role FROM users')
    users_list = cursor.fetchall()
    
    return render_template_string(
        USERS_TEMPLATE,
        users=users_list
    )


@app.route('/api/user/<int:user_id>')
def api_user(user_id):
    """API pública para obtener datos de usuario"""
    db = get_db()
    cursor = db.cursor()
    
    # VULNERABILIDAD IDOR: Exposición de información sensible
    # Incluye api_key que no debería ser accesible públicamente
    cursor.execute('SELECT id, username, email, role, api_key FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    if user:
        return {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'api_key': user['api_key']  # ¡Información sensible expuesta!
        }
    return {'error': 'Usuario no encontrado'}, 404


@app.route('/debug')
def debug():
    """Endpoint de debug para ver variables de sesión"""
    return {
        'session': dict(session),
        'current_user': dict(get_current_user()) if get_current_user() else None
    }


# Inicializar base de datos al iniciar
with app.app_context():
    init_db()


if __name__ == '__main__':
    print("=" * 60)
    print("LAB DE CIBERSEGURIDAD - APLICACIÓN VULNERABLE")
    print("=" * 60)
    print("\n⚠️  ESTA APLICACIÓN CONTIENE VULNERABILIDADES INTENCIONALES")
    print("   PARA PROPÓSITOS EDUCATIVOS Y DE ACADEMIA")
    print("\nCredenciales de prueba:")
    print("  Admin:  admin / admin123")
    print("  User1:  user1 / password1")
    print("  User2:  user2 / password2")
    print("\nEjecutando en http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)