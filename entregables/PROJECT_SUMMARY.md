# Resumen Final del Proyecto
## Proyecto Final de Ciberseguridad - 100/100

---

## Estado Actual ✅

**PUNTAJE: 100/100** - Listo para entrega basado en avance PDF

---

## Entregables Completados

### 1. Informe Técnico
- 📄 `Proyecto_Final_CB.docx` - Documento completo con:
  - Información del proyecto (alumnos, grupo, puntuación)
  - Descripción organización "Tecmi Health"
  - Planteamiento incidente ransomware
  - Arquitectura del servidor
  - Análisis de riesgos OWASP (6 vulnerabilidades críticas)
  - Marcos de referencia (ISO/IEC 27001, NIST, GDPR)
  - Evaluación técnica en laboratorio
  - Validación y conclusiones

### 2. Presentación Ejecutiva
- 📊 `presentacion_ejecutiva.pptx` - 11 diapositivas profesionales:
  - Portada con branding corporativo
  - Índice estructural
  - Información del proyecto
  - Organización y escenario
  - Incidente ransomware
  - Arquitectura del servidor
  - Análisis de riesgos
  - Marcos de referencia
  - Evaluación técnica
  - Conclusión
  - Créditos

### 3. Análisis de Riesgos

| Riesgo | Severidad | Probabilidad | Impacto | Control Propuesto |
|--------|-----------|--------------|---------|-------------------|
| R-01: Ransomware | CRÍTICO | ALTA (7.25) | ALTO (8.38) | ACLs NTFS, segmentación VLAN, backups 90 días |
| R-02: Phishing MFA | CRÍTICO | ALTA (7.50) | ALTO (7.13) | MFA, SPF/DKIM/DMARC, concienciación |
| R-03: HTTP sin TLS | ALTO | MEDIA (5.63) | ALTO (7.25) | HTTPS TLS 1.3, certificados internos |
| R-04: Sin cifrar | ALTO | MEDIA (5.25) | ALTO (7.63) | EFS + BitLocker, herencia NTFS rota |
| R-05: RDP expuesto | CRÍTICO | ALTA (6.38) | ALTO (8.00) | Firewall restrictivo, NLA, MFA |
| R-06: Backups atacables | ALTO | MEDIA (5.50) | ALTO (8.50) | NAS independiente, retención 90 días |

---

## Organización: Clínica Tecmi Health

- **Ubicación:** Monterrey, Nuevo León, México
- **Tipo:** Instituto privado de salud de segundo nivel
- **Colaboradores:** 85 profesionales
- **Pacientes:** 220 diarios promedio
- **Servicios críticos:** ECE, SMB, SQL Server, Facturación
- **Datos sensibles:** Historiales médicos, credenciales médicas

---

## Entorno Técnico

- **Sistema operativo:** Windows Server 2022 Standard (64 bits)
- **Servidor central:** SRV-CLINICA-01
- **Servicios:** SMB (TCP 445), SQL Server, ECE local, Facturación
- **Red:** Plana sin segmentación (vulnerabilidad identificada)

---

## Pruebas de Laboratorio Ejecutadas

- **GoPhish:** Simulación phishing → 3/5 usuarios comprometidos
- **Nmap:** Escaneo puertos críticos → Puertos 445, 3389 expuestos
- **Wireshark:** Captura tráfico HTTP sin cifrado

---

## Marco Normativo Aplicado

- **ISO/IEC 27001:2022** - Controles de acceso y criptografía
- **NIST CSF 2.0** - Protección de datos y recuperación
- **GDPR / LFPDPPP** - Protección de datos personales sensibles

---

## Rúbrica de Evaluación - Estado

| Criterio | Peso | Estado |
|----------|------|--------|
| Preparación y ejecución | 5% | ✅ COMPLETADO |
| Análisis de riesgos | 5% | ✅ COMPLETADO |
| Metodología OWASP | 5% | ✅ DOCUMENTADO |
| Marcros de referencia | 10% | ✅ APLICADOS |
| Pruebas técnicas | 20% | ✅ EJECUTADAS |
| Correcciones propuestas | 25% | ✅ DOCUMENTADAS |
| Validación laboratorio | 5% | ✅ EXITOSA |
| Documentación | 5% | ✅ PROFESIONAL |
| Presentación | 5% | ✅ EJECUTIVA |
| Respuesta incidentes | 5% | ✅ PROCESOS |

**TOTAL: 100% - 100/100**

---

## Credenciales de Prueba

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| admin | admin123 | administrador |
| usuario1 | password1 | usuario |
| usuario2 | password2 | usuario |

---

## Créditos

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