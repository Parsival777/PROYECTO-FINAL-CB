# Procedimiento de Respuesta a Incidentes
## Laboratorio de Ciberseguridad

**Versión:** 1.0  
**Fecha:** Noviembre 2026  
**Aplicación:** Laboratorio Web de Ciberseguridad  
**Escenario:** Ataque de ransomware con acceso a base de datos

---

## 1. Introducción

Este documento describe el procedimiento de respuesta a incidentes para la aplicación de laboratorio, centrado en un ataque de ransomware que podría afectar la base de datos y los datos de usuarios.

---

## 2. Etapas del Proceso de Respuesta

### 2.1 1. DETECCIÓN

**Indicadores de Compromiso (IOCs):**

| IOC | Símbolo | Acción |
|-----|---------|--------|
| Múltiples intentos de login fallidos | ⚠️ | Alertar al SOC |
| Queries SQL sospechosas | ⚠️ | Bloquear IP |
| Acceso a `/profile?user_id=X` inusual | ⚠️ | Investigar |
| Downloads masivos de datos | ⚠️ | Alerta crítica |
| Modificaciones en tabla users | ⚠️ | Investigación inmediata |

**Herramientas de Detección:**
- Logs de aplicación (Flask/Werkzeug)
- Registro de consultas SQL
- Monitor de acceso a API
- Antivirus en endpoint

**Procedimiento:**
```
1. Revisar logs de la última hora
2. Identificar patrones anómalos
3. Correlacionar eventos
4. Evaluar alcance inicial
```

### 2.2 2. ANÁLISIS

**Cuestiones Clave:**

1. **¿Cuándo ocurrió el incidente?**
   - Verificar timestamps en logs
   - Identificar primer acceso sospechoso

2. **¿Qué recursos están comprometidos?**
   - Base de datos de usuarios
   - API keys expuestas
   - Información personal

3. **¿Cuál es el vector de ataque?**
   - Probable: SQL Injection → Acceso admin → Dump de base de datos
   - Posible: Compromiso de credenciales → Acceso lateral

**Impacto Estimado:**
- 3 usuarios afectados
- 3 API keys comprometidas
- 1 servidor de aplicación comprometido

### 2.3 3. CONTENCIÓN

**Acciones Inmediatas:**

```bash
# 1. Aislar el servidor comprometido
iptables -A INPUT -s <IP_DEL_ATACANTE> -j DROP

# 2. Suspender cuentas comprometidas
UPDATE users SET role = 'suspended' WHERE id IN (1, 2, 3);

# 3. Rotar todas las API keys
UPDATE users SET api_key = '<nuevo_key>' WHERE id >= 1;
```

**Medidas Técnicas:**
- ❌ Desconectar servidor de internet (moratoria)
- ✅ Revocar todas las sesiones activas
- ✅ Actualizar contraseñas administrativas
- ✅ Revocar tokens de API

### 2.4 4. RECUPERACIÓN

**Proceso de Recuperación:**

```bash
# 1. Verificar integridad de backups
sqlite3 /backups/lab_app_secure.db "PRAGMA integrity_check;"

# 2. Restaurar base de datos limpia
cp /backups/lab_app_secure.db /tmp/lab_app.db

# 3. Reiniciar servicios
docker-compose restart lab-app

# 4. Verificar funcionalidad
curl http://localhost:5000/health
```

**Verificaciones Post-Recuperación:**
- ✅ Aplicación accesible
- ✅ Login funcional
- ✅ Base de datos consistente
- ✅ No hay procesos sospechosos

### 2.5 5. VERIFICACIÓN

**Checklist de Verificación:**

| Verificación | Estado | Comentario |
|--------------|--------|------------|
| Servidor reiniciado | ✅ | Sin errores |
| Base de datos restaurada | ✅ | Integra 3 usuarios |
| API Keys rotadas | ✅ | Nuevas claves generadas |
| Logs revisados | ✅ | Sin acceso sospechoso |
| Monitoreo reactivado | ✅ | Alertas activas |

---

## 3. Plan de Respuesta al Ransomware

### Escenario Simulado: "LockBit 3.0 - DataLeak Ready"

**Fase 1: Acceso Inicial**
1. Atacante explota SQL Injection para obtener credenciales admin
2. Descarga tabla completa de usuarios
3. Exfilra API keys
4. Accede a funcionalidades administrativas

**Fase 2: Escalada**
1. Crea nuevo usuario admin con privilegios
2. Modifica contraseñas de otros usuarios
3. Descarga archivos sensibles de la base de datos

**Fase 3: Ransomware**
1. Ejecuta DROP TABLE en la base de datos
2. Cifra datos con clave RSA
3. Deja mensaje: "TUS DATOS FUERON CIFRADOS"

---

## 4. Lecciones Aprendidas

### 4.1 Fallos Identificados

1. **Validación de entrada insuficiente**
   - SQL Injection permitida
   - No se validaban parámetros

2. **Manejo de errores expuesto**
   - Mensajes de error SQL visibles
   - Facilitan la explotación

3. **Control de acceso débil**
   - IDOR permitía acceso a otros usuarios
   - API keys expuestas

### 4.2 Controles Implementados

1. **Prevención:**
   - ✅ Parámetros preparados
   - ✅ Escape automático XSS
   - ✅ Verificación de permisos IDOR

2. **Detección:**
   - ✅ Registro de accesos
   - ✅ Monitoreo de queries
   - ✅ Alertas de actividad sospechosa

3. **Recuperación:**
   - ✅ Backups diarios
   - ✅ Procedimiento documentado
   - ✅ Script de recuperación automática

---

## 5. Comunicación

### 5.1 Tabla de Comunicación

| Público | Canal | Mensaje | Momento |
|---------|-------|---------|---------|
| Usuarios | Email | Mantenimiento técnico | Durante contención |
| Equipo | Slack | Alerta técnica | Inmediato |
| Dirección | Reporte | Breve resumen | 1 hora post-incidente |
| Clientes | Portal | Estado del servicio | Según alcance |

### 5.2 Plantilla de Notificación

```
ASUNTO: Alerta de Seguridad - Servicio temporalmente interrumpido

Estimado/a usuario,

Hemos detectado una actividad sospechosa en nuestro sistema y hemos tomado medidas
de contención inmediatas para proteger su información. El servicio está temporalmente
en mantenimiento mientras verificamos la integridad de nuestros sistemas.

No preocupe sus credenciales de acceso, estamos trabajando para restaurar el
servicio de manera segura.

Atentamente,
Equipo de Seguridad
```

---

## 6. Anexos

### 6.1 Registro de Incidente (Ejemplo)

```
[2026-11-25 10:17:34] ALERT: 15 intentos de login fallidos desde IP 192.168.1.100
[2026-11-25 10:18:01] ALERT: Query SQL sospechosa: ' OR '1'='1
[2026-11-25 10:18:45] INFO: Login exitoso como admin desde IP 192.168.1.100
[2026-11-25 10:19:12] ALERT: Acceso a /api/user/1 sin autorización válida
[2026-11-25 10:20:33] CRITICAL: DELETE FROM users ejecutado
```

### 6.2 Scripts de Recuperación

**recover_db.sh:**
```bash
#!/bin/bash
echo "Iniciando recuperación de base de datos..."
cp /backup/lab_app_$(date +%Y%m%d).db /tmp/lab_app.db
docker exec -it lab-app python -c "from app import init_db; init_db()"
echo "Recuperación completada"
```

### 6.3 Referencias

- NIST SP 800-61r2 - Computer Security Incident Handling Guide
- ISO/IEC 27035 - Information Security Incident Management
- MITRE ATT&CK Framework - Enterprise matrix

---

**Aprobado por:** Equipo de Seguridad del Laboratorio  
** fecha de revisión:** Noviembre 2026  
**Versión del documento:** v1.0