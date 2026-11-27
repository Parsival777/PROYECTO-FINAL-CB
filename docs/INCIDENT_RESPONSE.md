# Procedimiento de Respuesta a Incidentes
## Clínica Tecmi Health

**Versión:** 2.0 - Actualizado  
**Fecha:** Noviembre 2026  
**Preparado por:** Equipo "By The Power Rangers"  
**Escenario:** Ransomware Cipherware

---

## Tabla de Separación de Alcance

| Aspecto | Implementado en Laboratorio (Este Repo) | Recomendación Propuesta |
|---------|-----------------------------------------|--------------------------|
| **Patch de código SQLi** | ✅ Consultas parametrizadas en app_secure.py | Implementar WAF para detección adicional |
| **Patch de código XSS** | ✅ Escape automático + CSP en templates | Escanear contenido estático con herramientas |
| **Patch de código IDOR** | ✅ Validación de propietario en app_secure.py | Implementar Access Control Lists (ACLs) en BD |
| **Reverse Proxy Nginx** | ✅ rate limiting 10r/s, CSP headers, server_tokens off | Habilitar HTTPS con certificado Let's Encrypt |
| **Security Logging** | ✅ security.log con eventos estructurados | Integrar con SIEM (Splunk/ELK) para correlación |
| **OWASP ZAP scanning** | ✅ zap_vulnerable.html, zap_segura.html | Automatizar en CI/CD pipeline |
| **EDR/XDR Endpoints** | ❌ No implementado | Desplegar CrowdStrike/Falcon o SentinelOne |
| **Backups inmutables** | ❌ No implementado | Implementar regla 3-2-1-1-0 con CaaS offsite |
| **SIEM/SOAR centralizado** | ❌ No implementado | Desplegar Splunk/SIEM o usar servicio MSSP |
| **MFA en accesos admin** | ❌ No implementado | Habilitar MFA con authenticator o hardware token |

---

## 1. Detección

### Indicadores de Compromiso (IOCs)
- Actividad en puerto TCP 445 (SMB) sin autorización
- Múltiples intentos de login fallidos en rápida sucesión
- Archivos con extensión `.locked_sr` en repositorios
- Actividad sospechosa en endpoint `/debug`
- Headers HTTP incompletos (faltan CSP, X-Frame-Options)

### Señales de alerta
- Tiempo de respuesta a queries > umbral normal
- Intentos de acceso a múltiples perfiles de usuario (IDOR)
- Tráfico HTTP sin cifrar en red local
- Errores en logs al consultar tablas
- **429 Too Many Requests** en Nginx (rate limiting activado)
- **403 Forbidden** en Flask (acceso denegado)

### Tiempos críticos del escenario ransomware
```
07:45 - Empleado recepción abre correo phishing
08:02 - Ransomware descarga e inicia ejecución
08:15 - Cifrado de archivos inicia
08:30 - Sistema inaccesible, alerta generada
09:00 - Equipo TI confirma incidente
09:15 - Inicio procedimiento de contención
```

---

## 2. Análisis

### Acciones inmediatas
1. **Isolar el servidor** - Desconectar SRV-CLINICA-01 de la red
2. **Preservar evidencias** - Captura de memoria y logs
3. **Identificar alcance** - Revisar logs de acceso y auditoría

### Información recopilada
- Timestamp del primer acceso sospechoso
- IPs de origen de los intentos
- Archivos afectados por el cifrado
- Credenciales comprometidas

### Evaluación de impacto
- **Servicios críticos afectados:** ECE, Laboratorio, Imagenología
- **Pacientes impactados:** Estimado 180 consultas pendientes
- **Ubicación:** Servidor local, sin replicación en nube

### Análisis forense de security.log
**Fragmento real de security.log:**
```json
{"timestamp": "2026-11-26T10:15:32.456Z", "level": "WARNING", "ip": "192.168.1.100", "type": "INVALID_INPUT_BLOCKED", "details": "Patrón sospechoso detectado: <script>"}
{"timestamp": "2026-11-26T10:20:45.789Z", "level": "WARNING", "ip": "192.168.1.105", "type": "IDOR_UNAUTHORIZED_ACCESS", "details": "Intento de consulta de recursos pertenecientes a otro usuario"}
{"timestamp": "2026-11-26T10:35:00.333Z", "level": "WARNING", "ip": "192.168.1.108", "type": "RATE_LIMIT_TRIGGERED", "details": "Bloqueo ejecutado por Nginx por demasiadas peticiones"}
```

**Correlación SOC:**
1. **Línea 1 (10:15:32):** Intento XSS bloqueado - Posible reconocimiento automatizado
2. **Línea 2 (10:20:45):** Intento IDOR - Acceso a recurso ajeno (perfil usuario 1)
3. **Línea 3 (10:35:00):** Rate limit activado - Escaneo o fuerza bruta

**Patrón detectado:** Secuencia de 3 eventos diferentes (XSS → IDOR → Rate limit) desde IPs distintas pero dentro de 20 minutos sugiere fase de reconocimiento antes de ataque masivo. Acción requerida: Bloqueo de IPs y escalamiento a SOC.

---

## 3. Contención

### Contención inmediata
1. **Aislamiento de red:**
   ```
   - Desconectar SRV-CLINICA-01 de red local
   - Bloquear acceso RDP (TCP 3389) desde internet
   - Deshabilitar SMB en estaciones de trabajo
   ```

2. **Contención de procesos:**
   ```
   - Suspender procesos críticos
   - Deshabilitar logins administrativos
   - Revocar sesiones activas
   ```

3. **Contención de contenedores Docker:**
   ```bash
   docker-compose stop
   docker-compose pause
   # Mantener contenedores en estado pausado para forensics
   ```

### Medidas técnicas
- Aplicar ACLs NTFS restringidas
- Deshabilitar SMBv1
- Bloquear puertos críticos (445, 3389)
- **Aislamiento de contenedores afectados** (Docker)

---

## 4. Erradicación

### Limpieza del sistema
1. **Verificación de integridad:**
   ```powershell
   # Verificar hashes de archivos críticos
   Get-ChildItem -Path "C:\ClinicaTecmiHealth" -Recurse | 
   Get-FileHash | Export-Csv "C:\hashes.csv"
   ```

2. **Eliminación de malware:**
   ```cmd
   # Varredura con antivirus
   "C:\Program Files\Antivirus\scan.exe" /full /quarantine
   
   # Eliminar archivos .locked_sr
   del /s /q "C:\*.locked_sr"
   ```

3. **Limpieza de contenedores:**
   ```bash
   # Eliminar contenedores afectados
   docker-compose down --remove-orphans
   docker system prune -a --volumes
   ```

4. **Restablecimiento de credenciales:**
   - Cambiar contraseñas de todas las cuentas
   - Reemplazar API keys de personal médico
   - Revocar y regenerar certificados
   - **Rotación de SECRET_KEY en Flask**

### Implementación de controles
- Aplicar las correcciones de `security_fixes.py`
- Configurar backups aislados
- Implementar segmentación VLAN
- **Hardening de Nginx:** rate limiting, CSP headers, server_tokens off

---

## 5. Recuperación

### Recuperación de datos
1. **Restaurar desde backups (90 días):**
   ```cmd
   # Verificar integridad de backup
   robocopy \\NAS\Backups\Daily_07112026 C:\Restore /verify
   
   # Verificar hashes SHA-256 antes de restaurar
   Get-FileHash C:\Restore\database.db
   
   # Restaurar base de datos
   sqlite3 C:\ClinicaTecmiHealth\database.db < restore_backup.sql
   ```

2. **Verificar datos restaurados:**
   - Comparar hashes con versión previa
   - Validar integridad referencial
   - Verificar permisos de acceso

### Restablecimiento de servicios
1. **Servicios ordenados:**
   - Base de datos primero (SQL Server)
   - Sistema de archivos (SMB con ACLs nuevas)
   - Aplicaciones (ECE)
   - Facturación (en última instancia)

2. **Pruebas de funcionalidad:**
   - Verificar acceso de usuarios
   - Probar funcionalidades críticas
   - Confirmar integridad de datos

3. **Verificación Docker:**
   ```bash
   # Levantar entorno seguro
   docker-compose up -d
   # Verificar estado de contenedores
   docker-compose ps
   # Ejecutar pruebas de seguridad
   python test_exploits.py
   ```

---

## 6. Verificación

### Validación post-recuperación
1. **Pruebas de seguridad:**
   - Ejecutar `test_exploits.py` en ambiente seguro
   - Verificar que todas las correcciones funcionan
   - Validar headers de seguridad HTTP

2. **Monitorización:**
   - Configurar alertas de seguridad
   - Monitorear acceso a archivos sensibles
   - Verificar logs de auditoría

### Checklist de verificación

| Control | Estado | Verificado |
|---------|--------|------------|
| SQL Injection | ✅ Parcheado | ✅ test_exploits.py |
| XSS | ✅ Parcheado | ✅ OWASP ZAP |
| IDOR | ✅ Parcheado | ✅ test_exploits.py |
| Nginx Rate Limiting | ✅ Activo | ✅ 429 test |
| CSP Headers | ✅ Configurado | ✅ curl -I |
| Security Logging | ✅ Activo | ✅ security.log |
| Server Tokens | ✅ Oculto | ✅ curl -I |

---

## 7. Lecciones Aprendidas

### Errores identificados
1. **Red plana sin segmentación** - Permite movimiento lateral
2. **Credenciales compartidas** - Falta de separación de roles
3. **Backups en mismo servidor** - Facilita destrucción por ransomware
4. **Sin autenticación multifactor** - Facilita acceso no autorizado
5. **Sin rate limiting inicial** - Permite escaneo de puertos
6. **Sin headers CSP** - XSS sin limitaciones
7. **Sin logging estructurado** - Dificulta correlación forense

### Controles a implementar

| Control | Prioridad | Responsable | Fecha objetivo |
|---------|-----------|-------------|----------------|
| Segmentación VLAN | Alta | TI | Inmediato |
| MFA para cuentas críticas | Alta | TI | 7 días |
| Backups aislados | Alta | TI | 7 días |
| Firewall restrictivo | Media | TI | 14 días |
| CSP Headers HTTPS | Media | TI | 14 días |
| EDR/XDR Endpoints | Alta | SOC | 30 días |
| SIEM/SOAR centralizado | Alta | SOC | 60 días |

### Recomendaciones técnicas adicionales

1. **Implementar autenticación basada en certificados** para acceso administrativo
2. **Habilitar detección de anomalías** con machine learning en logs
3. **Crear red de zonas (DMZ, Internal, Critical)** con firewalls entre ellas
4. **Implementar honeypots** para detección temprana de movimiento lateral
5. **Crear playbook automatizado** con SOAR para respuesta rápida

---

## Anexos

### Cronología del incidente
```
07:45 - Empleado recepción abre correo phishing
08:02 - Ransomware descarga e inicia ejecución
08:15 - Cifrado de archivos inicia
08:30 - Sistema inaccesible, alerta generada
09:00 - Equipo TI confirma incidente
09:15 - Inicio procedimiento de contención
10:00 - Identificación alcance completo
11:30 - Eliminación malware confirmada
14:00 - Restauración desde backup iniciada
16:00 - Servicios críticos operativos
18:00 - Verificación completa
```

### Contactos de emergencia
- **Incident Response Team:** Equipo TI - 555-1234
- **Soporte médico:** Coordinador médico - 555-5678
- **Comunicación:** Directora clínica - 555-9012

### Referencias
- NIST SP 800-61r2 - Computer Security Incident Handling Guide
- ISO/IEC 27035 - Information Security Incident Management
- MITRE ATT&CK Framework - Enterprise Matrix
- OWASP Incident Response Cheat Sheet

---

**Este procedimiento fue desarrollado como parte del proyecto final de ciberseguridad y debe actualizarse tras cada incidente real.**

**Versión 2.0 - Actualizado con implementaciones del laboratorio Docker, Nginx hardening y logging estructurado.**