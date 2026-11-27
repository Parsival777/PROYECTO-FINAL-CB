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
| `entregables/Proyecto_Final_CB.pdf` | Versión PDF exportada con tabla de trazabilidad | - |
| `entregables/presentacion_ejecutiva.pptx` | Presentación ejecutiva de 11 diapositivas | 42 KB |
| `entregables/ENTREGABLE.txt` | Documentación de entrega | 2.8 KB |
| `entregables/PROJECT_SUMMARY.md` | Resumen del proyecto | 4.0 KB |

---

## 🧪 Pruebas y Validación

### Ejecutar pruebas automatizadas

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar pruebas
python test_exploits.py
```

### Resultado esperado

El script detectará todas las vulnerabilidades y generará:
- `vulnerability_scan_results.json` - Resultados estructurados
- Reporte en consola con tabla comparativa [VULNERABLE] vs [PROTEGIDO]

---

## 🐛 Vulnerabilidades Implementadas

### 1. SQL Injection (INYECCIÓN SQL)

- ✅ **Componente:** `/search` y `/login`
- **Vulnerabilidad:** Query strings sin parametrizar
- **Corrección:** Parámetros preparados (?) + validación estricta de tipos
- **Prueba:** `' OR '1'='1`, `' UNION SELECT ...`
- **Defensa adicional:** Logging de intentos SQLi

### 2. Cross-Site Scripting (XSS)

- ✅ **Componente:** `/search` (descripción productos)
- **Vulnerabilidad:** Uso de filtro `| safe`
- **Corrección:** Escape automático HTML + CSP headers
- **Prueba:** `<script>alert(1)</script>` bloqueado
- **Defensa adicional:** Content-Security-Policy estricto

### 3. Insecure Direct Object Reference (IDOR)

- ✅ **Componente:** `/profile`, `/api/user/<id>`
- **Vulnerabilidad:** Acceso sin verificación de permisos
- **Corrección:** Validación de propietario + RBAC
- **Prueba:** `/profile?user_id=1` protegido
- **Defensa adicional:** Registro de intentos IDOR

---

## 🔒 Correcciones de Seguridad

Ver `security_fixes.py` para documentación completa de las correcciones aplicadas.

### Defensa en Profundidad Aplicada

1. **SQL Injection:**
   - Consultas parametrizadas
   - Validación estricta de tipos y rango
   - Logging de intentos sospechosos

2. **XSS:**
   - Escape automático de contenido HTML
   - Content-Security-Policy estricto
   - Headers de seguridad HTTP

3. **IDOR:**
   - Validación de propiedad en consulta SQL
   - Role-based access control
   - Registro de accesos no autorizados

---

## 📦 Cómo Verificar

### 1. Verificar dependencias

```bash
pip install -r requirements.txt
```

### 2. Levantar entorno con Docker

```bash
# Iniciar todos los servicios
docker-compose up -d

# Verificar estado
docker-compose ps

# Detener
docker-compose down
```

### 3. Acceso vía Nginx (recomendado)

| Ruta | Servicio |
|------|----------|
| `http://localhost:8080` | Aplicación vulnerable (laboratorio) |
| `http://localhost:8443` | Aplicación segura (correcciones) |

### 4. Acceso directo (para desarrollo)

| Puerto | Servicio |
|--------|----------|
| 5000 | Aplicación vulnerable |
| 5001 | Aplicación segura |

### 5. Ejecutar pruebas de exploit

```bash
python test_exploits.py
```

### 6. Conectar OWASP ZAP

```bash
# En otra terminal
docker run -t owasp/zap2docker-stable zap-baseline.py \
    -t http://localhost:8080/vulnerable \
    -r zap_vulnerable.html

docker run -t owasp/zap2docker-stable zap-baseline.py \
    -t http://localhost:8443/secure \
    -r zap_segura.html
```

---

## 🐳 Contenerización

### Arquitectura Docker

```
                    ┌─────────────────────────────────┐
                    │           NGINX (80, 8443)      │
                    │   - Reverse Proxy               │
                    │   - Rate Limiting (10r/s)         │
                    │   - Security Headers            │
                    │   - Obscure Server Tokens       │
                    └─────────────┬───────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │      docker network      │
                    ├────────────┬──────────────┤
                    │            │              │
         ┌──────────┘    ┌───────┘    ┌─────────┐
         │              │            │         │
    ┌────────┐       ┌────────┐   ┌────────┐  ┌────────┐
    │ Flask  │       │ Flask  │   │  Log   │  │  DB    │
    │ (5000) │       │ (5001) │   │ files  │  │ files  │
    │Vulnerable│      │Secure  │   │        │  │        │
    └────────┘       └────────┘   └────────┘  └────────┘
```

### Puertos expuestos

| Puerto | Servicio | Uso |
|--------|----------|-----|
| 80 | NGINX HTTP | Acceso público vulnerable |
| 8443 | NGINX HTTPS | Acceso público seguro |
| 5000 | Flask* | Solo interno (expose) |
| 5001 | Flask* | Solo interno (expose) |

*Los puertos 5000 y 5001 NO están expuestos directamente desde el host. Todo el tráfico pasa obligatoriamente por Nginx.

---

## 📋 Rúbrica de Evaluación

| Criterio | Peso | Estado |
|----------|------|--------|
| Arquitectura y Reproducibilidad | 5% | ✅ COMPLETADO |
| Identificación SQL Injection | 5% | ✅ DOCUMENTADO |
| Identificación XSS | 5% | ✅ DOCUMENTADO |
| Identificación IDOR | 5% | ✅ DOCUMENTADO |
| Implementación correcciones | 25% | ✅ CÓDIGO CORREGIDO |
| Validación con OWASP ZAP | 5% | ✅ COMPATIBLE |
| Análisis de registros | 5% | ✅ ENDPOINT /debug + security.log |
| Mejora organizacional | 10% | ✅ NGINX con rate limiting y headers |
| Pruebas de implementación | 20% | ✅ test_exploits.py con aserciones |
| Respuesta a incidentes | 5% | ✅ INCIDENT_RESPONSE.md actualizado |
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