#!/usr/bin/env python3
"""
Script con las correcciones de seguridad implementadas
Para aplicar las correcciones a mano o para documentación
"""

# ============== CORRECCIÓN SQL INJECTION ==============
# 
# VULNERABILIDAD ORIGINAL (app.py):
# query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
# sql_query = f"SELECT * FROM products WHERE name LIKE '%{query}%' OR description LIKE '%{query}%'"
#
# CORRECCIÓN APLICADA:
# 
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username', '')
#         password = request.form.get('password', '')
#         
#         db = get_db()
#         cursor = db.cursor()
#         
#         # ✅ CORRECCIÓN: Consulta parametrizada
#         cursor.execute(
#             'SELECT * FROM users WHERE username = ? AND password = ?',
#             (username, password)
#         )
#         user = cursor.fetchone()
#         
#         if user:
#             session['user_id'] = user['id']
#             session['username'] = user['username']
#             return redirect(url_for('home'))
#         else:
#             flash('Credenciales inválidas')
#     
#     return render_template_string(LOGIN_TEMPLATE)
#
# @app.route('/search')
# def search():
#     query = request.args.get('q', '')
#     results = []
#     
#     if query:
#         db = get_db()
#         cursor = db.cursor()
#         
#         # ✅ CORRECCIÓN: Uso de placeholder y escapado seguro
#         search_term = f'%{query}%'
#         cursor.execute(
#             'SELECT * FROM products WHERE name LIKE ? OR description LIKE ?',
#             (search_term, search_term)
#         )
#         rows = cursor.fetchall()
#         
#         for row in rows:
#             results.append({
#                 'id': row['id'],
#                 'name': row['name'],
#                 'description': row['description'],
#                 'price': row['price']
#             })
#     
#     return render_template_string(SEARCH_TEMPLATE, query=query, results=results)


# ============== CORRECCIÓN XSS ==============
#
# VULNERABILIDAD ORIGINAL (en el template search.html):
# <p>Descripción: {{ product.description | safe }}</p>
#
# CORRECCIÓN APLICADA:
#
# @app.route('/search')
# def search():
#     query = request.args.get('q', '')
#     results = []
#     
#     if query:
#         db = get_db()
#         cursor = db.cursor()
#         
#         search_term = f'%{query}%'
#         cursor.execute(
#             'SELECT * FROM products WHERE name LIKE ? OR description LIKE ?',
#             (search_term, search_term)
#         )
#         rows = cursor.fetchall()
#         
#         for row in rows:
#             # ✅ CORRECCIÓN: Escapado automático de contenido (remover | safe)
#             # Flask escapa automáticamente por defecto
#             results.append({
#                 'id': row['id'],
#                 'name': row['name'],
#                 'description': row['description'],  # Sin | safe
#                 'price': row['price']
#             })
#     
#     # Además, aplicar Content Security Policy en nginx.conf:
#     # add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';" always;


# ============== CORRECCIÓN IDOR ==============
#
# VULNERABILIDAD ORIGINAL:
# @app.route('/profile')
# def profile():
#     current_user_id = session.get('user_id', 1)
#     requested_id = request.args.get('user_id', type=int, default=current_user_id)
#     
#     cursor.execute('SELECT * FROM users WHERE id = ?', (requested_id,))
#     user = cursor.fetchone()
#
# CORRECCIÓN APLICADA:
#
# @app.route('/profile')
# def profile():
#     # ✅ CORRECCIÓN: Verificar que el usuario esté autenticado
#     if 'user_id' not in session:
#         flash('Debes iniciar sesión primero')
#         return redirect(url_for('login'))
#     
#     current_user_id = session['user_id']
#     requested_id = request.args.get('user_id', type=int, default=current_user_id)
#     
#     # ✅ CORRECCIÓN: Solo el propio usuario puede ver su perfil
#     if requested_id != current_user_id:
#         # Preguntar: ¿El usuario es admin?
#         db = get_db()
#         cursor = db.cursor()
#         cursor.execute('SELECT role FROM users WHERE id = ?', (current_user_id,))
#         current_user_data = cursor.fetchone()
#         
#         if not current_user_data or current_user_data['role'] != 'admin':
#             flash('No tienes permiso para ver este perfil')
#             return redirect(url_for('profile'))
#     
#     cursor.execute('SELECT * FROM users WHERE id = ?', (requested_id,))
#     user = cursor.fetchone()


# ============== MEJORA API ==============
#
# @app.route('/api/user/<int:user_id>')
# def api_user(user_id):
#     # ✅ CORRECCIÓN: Requerir autenticación
#     if 'user_id' not in session:
#         return {'error': 'No autenticado'}, 401
#     
#     db = get_db()
#     cursor = db.cursor()
#     
#     # ✅ CORRECCIÓN: Solo usuarios autenticados pueden ver sus propios datos
#     if user_id != session['user_id']:
#         # Verificar si es admin
#         cursor.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],))
#         current_user_data = cursor.fetchone()
#         if not current_user_data or current_user_data['role'] != 'admin':
#             return {'error': 'No autorizado'}, 403
#     
#     cursor.execute('SELECT id, username, email, role FROM users WHERE id = ?', (user_id,))
#     user = cursor.fetchone()
#     
#     if user:
#         # ✅ CORRECCIÓN: No exponer api_key sensible
#         return {
#             'id': user['id'],
#             'username': user['username'],
#             'email': user['email'],
#             'role': user['role']
#         }
#     return {'error': 'Usuario no encontrado'}, 404


# ============== MEDIDAS DE SEGURIDAD ADICIONALES ==============

# 1. Rate Limiting (implementado en nginx.conf):
#    - Limitar peticiones al login: 5/min
#    - Limitar peticiones generales: 100/min

# 2. Security Headers (implementado en nginx.conf):
#    - X-Frame-Options: SAMEORIGIN
#    - X-Content-Type-Options: nosniff
#    - X-XSS-Protection: 1; mode=block
#    - Content-Security-Policy
#    - Referrer-Policy: strict-origin-when-cross-origin

# 3. Password Hashing:
#    En producción, usar bcrypt o argon2:
#    @bcrypt
#    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#    bcrypt.checkpw(password.encode('utf-8'), stored_hash)

# 4. HTTPS:
#    Configurar certificado SSL en nginx:
#    listen 443 ssl;
#    ssl_certificate /etc/nginx/certs/cert.pem;
#    ssl_certificate_key /etc/nginx/certs/key.pem;
#    ssl_protocols TLSv1.2 TLSv1.3;

# 5. Logging y monitoreo:
#    - Registrar intentos de login fallidos
#    - Alertar sobre queries SQL sospechosas
#    - Monitorear accesos a recursos sensibles

print("Script de documentación de correcciones de seguridad cargado")
print("Ver comentarios en el código para ver las implementaciones completas")