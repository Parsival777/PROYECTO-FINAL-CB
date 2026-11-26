# Procedimiento de Respuesta a Incidentes
## Clínica Tecmi Health

**Versión:** 1.0  
**Fecha:** Noviembre 2026  
**Preparado por:** Equipo "By The Power Rangers"  
**Escenario:** Ransomware Cipherware

---

## 1. Detección

### Indicadores de Compromiso (IOCs)
- Actividad en puerto TCP 445 (SMB) sin autorización
- Múltiples intentos de login fallidos en rápida sucesión
- Archivos con extensión `.locked_sr` en repositorios
- Actividad sospechosa en endpoint `/debug`

### Señales de alerta
- Tiempo de respuesta a queries > umbral normal
- Intentos de acceso a múltiples perfiles de usuario
- Tráfico HTTP sin cifrar en red local
- Errores en logs al consultar tablas

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

### Medidas técnicas
- Aplicar ACLs NTFS restringidas
- Deshabilitar SMBv1
- Bloquear puertos críticos (445, 3389)

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

3. **Restablecimiento de credenciales:**
   - Cambiar contraseñas de todas las cuentas
   - Reemplazar API keys de personal médico
   - Revocar y regenerar certificados

### Implementación de controles
- Aplicar las correcciones de `security_fixes.py`
- Configurar backups aislados
- Implementar segmentación VLAN

---

## 5. Recuperación

### Recuperación de datos
1. **Restaurar desde backups (90 días):**
   ```cmd
   # Verificar integridad de backup
   robocopy \\NAS\Backups\Daily_07112026 C:\Restore /verify
   
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

### Documentación
- Generar informe de incidente
- Actualizar registro de incidentes
- Comunicar a personal médico

---

## 7. Lecciones Aprendidas

### Errores identificados
1. **Red plana sin segmentación** - Permite movimiento lateral
2. **Credenciales compartidas** - Falta de separación de roles
3. **Backups en mismo servidor** - Facilita destrucción por ransomware
4. **Sin autenticación multifactor** - Facilita acceso no autorizado

### Controles a implementar
| Control | Prioridad | Responsable | Fecha objetivo |
|---------|-----------|-------------|----------------|
| Segmentación VLAN | Alta | TI | Inmediato |
| MFA para cuentas críticas | Alta | TI | 7 días |
| Backups aislados | Alta | TI | 7 días |
| Firewall restrictivo | Media | TI | 14 días |
| CSP Headers HTTPS | Media | TI | 14 días |

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
```

### Contactos de emergencia
- **Incident Response Team:** Equipo TI - 555-1234
- **Soporte médico:** Coordinador médico - 555-5678
- **Comunicación:** Directora clínica - 555-9012

---

**Este procedimiento fue desarrollado como parte del proyecto final de ciberseguridad y debe actualizarse tras cada incidente real.**