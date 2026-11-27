# Resumen del Proyecto - Ciberseguridad Web

## Proyecto Final de Ciberseguridad
**Clínica Tecmi Health**  
**Grupo: "By The Power Rangers"**  
**Fecha: Noviembre 2026**  
**Puntaje: 100/100**

---

## Objetivo

Implementar un laboratorio de ciberseguridad web para identificar, analizar y mitigar tres vulnerabilidades críticas según OWASP Top 10 en el contexto de un escenario de ransomware en una clínica de salud.

---

## Vulnerabilidades Identificadas

### 1. SQL Injection (OWASP #3) - CRÍTICA
- **Endpoint:** `/login`, `/search`
- **Riesgo:** Acceso no autorizado a datos de pacientes y credenciales
- **Corrección:** Consultas parametrizadas + validación + logging

### 2. Cross-Site Scripting (OWASP #10) - ALTA
- **Endpoint:** `/search`
- **Riesgo:** Robo de sesiones y fuga de datos médicos
- **Corrección:** Escape HTML + CSP headers

### 3. Insecure Direct Object Reference (OWASP #1) - ALTA
- **Endpoint:** `/profile`, `/api/user/<id>`
- **Riesgo:** Acceso no autorizado a historiales médicos
- **Corrección:** Validación de propietario + RBAC

---

## Controles Implementados

### Defensa en Profundidad
- SQLi: Parámetros (?), validación estricta, bleach, logging
- XSS: Escape automático, CSP, X-XSS-Protection
- IDOR: Validación de propietario, RBAC, logging de intentos

### Nginx Hardening
- Rate limiting: 10r/s burst=20 nodelay
- server_tokens off
- 7 headers de seguridad HTTP
- Métodos restringidos a GET, POST, PUT, DELETE

---

## Estructura del Proyecto

```
├── README.md              # Documentación principal
├── .env.example           # Plantilla de variables de entorno
├── .gitignore             # Archivos a ignorar
├── Dockerfile             # Imagen Docker
├── docker-compose.yml     # Orquestación de contenedores
├── requirements.txt       # Dependencias
│
├── src/                   # Código fuente
│   ├── app.py             # Aplicación vulnerable
│   ├── app_secure.py      # Aplicación segura
│   └── security_fixes.py  # Documentación de correcciones
│
├── config/                # Configuraciones
│   └── nginx.conf         # Nginx hardened
│
├── tests/                 # Pruebas
│   └── test_exploits.py   # Suite de pruebas
│
├── docs/                  # Documentación
│   ├── INCIDENT_RESPONSE.md
│   └── PROJECT_SUMMARY.md
│
├── evidencias/            # Artefactos de auditoría
│   ├── zap_*.html
│   ├── vulnerability_scan_results.json
│   └── security.log
│
└── entregables/           # Entregables finales
    ├── Proyecto_Final_CB.pdf
    ├── Proyecto_Final_CB.docx
    └── presentacion_ejecutiva.pptx
```

---

## Resultados Verificables

| Métrica | Vulnerable | Seguro |
|---------|------------|--------|
| SQLi Login Bypass | ✅ 302 Redirect | ✅ 200 (bloqueado) |
| SQLi UNION | ✅ 200 (exfiltrado) | ✅ 200 (neutralizado) |
| XSS | ✅ Ejecutable | ✅ Neutralizado |
| IDOR API | ✅ 200 (clave expuesta) | ✅ 403 (denegado) |
| IDOR Profile | ✅ 200 (acceso) | ✅ 404 (bloqueado) |
| Headers | 4/7 | 7/7 ✅ |
| Rate Limit | ❌ | ✅ 429 |

---

## Escenario de Ransomware

**Fase inicial:** Phishing → Descarga → Escaneo → Movimientolateral → Cifrado

**Controles previos que permitiron el ataque:**
- App expuesta sin proxy inverso
- Sin rate limiting
- Sin headers CSP
- Sin logging estructurado

**Controles implementados que mitigan el escenario:**
- Nginx reverse proxy con rate limiting
- Logging para detección temprana
- Pruebas automatizadas de regresión

---

## Referencias

- OWASP Top 10 2021
- OWASP ASVS v4.0.3
- NIST SP 800-61r2
- ISO/IEC 27035