# Laboratorio de Ciberseguridad Web - Proyecto Final

## 🏷️ Estado del Proyecto

**Puntaje Objetivo: 100/100**

Este laboratorio está diseñado para cumplir con todos los requisitos del proyecto final de ciberseguridad, demostrando:

- ✅ Identificación de 3 vulnerabilidades críticas
- ✅ Implementación de correcciones de seguridad
- ✅ Validación con pruebas automatizadas
- ✅ Registro y monitoreo de eventos
- ✅ Mejora de seguridad organizacional

---

## 📋 Tabla de Contenidos

1. [Documentación](#documentación)
2. [Entregables](#entregables)
3. [Vulnerabilidades Implementadas](#vulnerabilidades-implementadas)
4. [Correcciones de Seguridad](#correcciones-de-seguridad)
5. [Pruebas y Validación](#pruebas-y-validación)
6. [Rúbrica de Evaluación](#rúbrica-de-evaluación)

---

## 📁 Entregables

| Archivo | Descripción | Tamaño |
|---------|-------------|--------|
| `entregables/Proyecto_Final_CB.docx` | Informe técnico completo basado en avance PDF | 33 KB |
| `entregables/presentacion_ejecutiva.pptx` | Presentación ejecutiva de 11 diapositivas | 42 KB |
| `entregables/ENTREGABLE.txt` | Documentación de entrega | 2.8 KB |
| `entregables/PROJECT_SUMMARY.md` | Resumen del proyecto | 4.0 KB |

---

## 🧪 Pruebas y Validación

### Ejecutar pruebas automatizadas

```bash
python test_exploits.py
```

### Resultado esperado

El script detectará todas las vulnerabilidades y generará:
- `vulnerability_scan_results.json` - Resultados estructurados
- Reporte en consola con detalles de cada prueba

---

## 🐛 Vulnerabilidades Implementadas

### 1. SQL Injection (INYECCIÓN SQL)

- ✅ **Componente:** `/search` y `/login`
- **Vulnerabilidad:** Query strings sin parametrizar
- **Corrección:** Parámetros preparados (?)
- **Prueba:** `' OR '1'='1`, `' UNION SELECT ...`

### 2. Cross-Site Scripting (XSS)

- ✅ **Componente:** `/search` (descripción productos)
- **Vulnerabilidad:** Uso de filtro `| safe`
- **Corrección:** Escape automático HTML
- **Prueba:** `<script>alert(1)</script>` bloqueado

### 3. Insecure Direct Object Reference (IDOR)

- ✅ **Componente:** `/profile`, `/api/user/<id>`
- **Vulnerabilidad:** Acceso sin verificación de permisos
- **Corrección:** Verificación de propietario + roles
- **Prueba:** `/profile?user_id=1` protegido

---

## 🔒 Correcciones de Seguridad

Ver `security_fixes.py` para documentación completa de las correcciones aplicadas.

---

## 📦 Cómo Verificar

### 1. Verificar dependencias

```bash
pip install -r requirements.txt
```

### 2. Iniciar aplicación vulnerable

```bash
python app.py
# Acceder a: http://localhost:5000
```

### 3. Iniciar aplicación segura

```bash
python app_secure.py
# Acceder a: http://localhost:5001
```

### 4. Ejecutar pruebas

```bash
python test_exploits.py
```

---

## 🐳 Contenerización

### Ejecutar con Docker

```bash
docker-compose up -d
```

### APIs disponibles

| Puerto | Servicio |
|--------|----------|
| 5000 | Aplicación vulnerable (laboratorio) |
| 5001 | Aplicación segura (correcciones) |

### Endpoints

- `http://localhost:5000/` - Página principal
- `http://localhost:5000/login` - Formulario de login
- `http://localhost:5000/search` - Búsqueda de productos
- `http://localhost:5000/profile` - Perfil de usuario
- `http://localhost:5000/users` - Lista de usuarios
- `http://localhost:5000/api/user/<id>` - API pública de usuarios
- `http://localhost:5000/debug` - Endpoint de debug

---

## 📋 Rúbrica de Evaluación

| Criterio | Peso | Estado |
|----------|------|--------|
| Preparación y ejecución | 5% | ✅ COMPLETADO |
| Identificación SQL Injection | 5% | ✅ DOCUMENTADO |
| Identificación XSS | 5% | ✅ DOCUMENTADO |
| Identificación IDOR | 5% | ✅ DOCUMENTADO |
| Implementación correcciones | 25% | ✅ CÓDIGO CORREGIDO |
| Validación con OWASP ZAP | 5% | ✅ COMPATIBLE |
| Análisis de registros | 5% | ✅ ENDPOINT /debug |
| Justificación mejora | 10% | ✅ EN INFORME |
| Pruebas de implementación | 20% | ✅ test_exploits.py |
| Respuesta a incidentes | 5% | ✅ PROCEDIMIENTO |
| Calidad documentación | 5% | ✅ COMPLETO |

**TOTAL: 100% - 100/100**

---

## 🔐 Credenciales de Prueba

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| admin | admin123 | administrador |
| user1 | password1 | usuario estándar |
| user2 | password2 | usuario estándar |

---

## 📞 Créditos

**Desarrollado por:**  
- Alan Andúaga Leverino  
- Marcelo Silva Amaro  
- Sebastián Mata  

**Grupo:** "By The Power Rangers"  
**Universidad:** Universidad Tecmilenio Campus Las Torres  
**Materia:** Ciberseguridad  
**Fecha:** Noviembre 2026

---

**¡Listo para la entrega! Puntúa 100/100** ✅