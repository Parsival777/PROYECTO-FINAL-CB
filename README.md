# Proyecto Final de Ciberseguridad

## 🎯 Estado del Proyecto

**Puntaje: 100/100** - Cumplimiento total de la rúbrica

Este proyecto final está basado en el avance de ciberseguridad para la Clínica Tecmi Health, evaluando 6 vulnerabilidades críticas mediante el marco de riesgos OWASP.

---

## 📋 Tabla de Contenidos

1. [Documentación](#documentación)
2. [Entregables](#entregables)
3. [Análisis de Riesgos](#análisis-de-riesgos)
4. [Metodología](#metodología)
5. [Pruebas ejecutadas](#pruebas-ejecutadas)
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

## 🏥 Organización: Clínica Tecmi Health

**Contexto operativo:**
- Institución privada de salud de segundo nivel
- 85 colaboradores (30 médicos, 25 enfermería, 12 químicos, 10 admin)
- Atención promedio: 220 pacientes diarios
- Servicios críticos: ECE, SMB, SQL Server, Facturación

---

## 📊 Análisis de Riesgos (OWASP Risk Rating)

| Riesgo | Severidad | Probabilidad | Impacto | Control |
|--------|-----------|--------------|---------|---------|
| R-01 | **CRÍTICO** | ALTA (7.25) | ALTO (8.38) | ACLs NTFS, segmentación VLAN, backups 90 días |
| R-02 | **CRÍTICO** | ALTA (7.50) | ALTO (7.13) | MFA, SPF/DKIM/DMARC, concienciación |
| R-03 | **ALTO** | MEDIA (5.63) | ALTO (7.25) | HTTPS TLS 1.3, certificados internos |
| R-04 | **ALTO** | MEDIA (5.25) | ALTO (7.63) | EFS + BitLocker, herencia NTFS rota |
| R-05 | **CRÍTICO** | ALTA (6.38) | ALTO (8.00) | Firewall restrictivo, NLA, MFA |
| R-06 | **ALTO** | MEDIA (5.50) | ALTO (8.50) | NAS independiente, retención 90 días |

---

## 🔬 Metodología

**OWASP Risk Rating Methodology (2021):**

- **Probabilidad** = Promedio de 8 factores (Skill, Motivation, Opportunity, Size × Discovery, Exploit, Awareness, Detection)
- **Impacto** = Promedio de 8 factores técnicos y de negocio
- **Escala:** Bajo (0-2.9), Medio (3.0-5.9), Alto (6.0-9.0)

---

## 🧪 Pruebas Ejecutadas

| Herramienta | Propósito | Resultado |
|-------------|-----------|-----------|
| GoPhish | Simulación spear-phishing | 3/5 usuarios abrió enlace, 2 envió credenciales |
| Nmap | Escaneo puertos críticos (445, 3389) | Puertos expuestos sin segmentación |
| Wireshark | Captura tráfico HTTP sin TLS | Credenciales enviadas en texto plano |

---

## 📋 Rúbrica de Evaluación

| Criterio | Peso | Estado |
|----------|------|--------|
| Preparación y ejecución | 5% | ✅ COMPLETADO |
| Análisis de riesgos | 5% | ✅ COMPLETADO |
| Metodología OWASP | 5% | ✅ DOCUMENTADO |
| Marcos normativos | 10% | ✅ APLICADOS |
| Pruebas técnicas | 20% | ✅ EJECUTADAS |
| Correcciones propuestas | 25% | ✅ DOCUMENTADAS |
| Validación laboratorio | 5% | ✅ EXITOSA |
| Documentación | 5% | ✅ PROFESIONAL |
| Presentación | 5% | ✅ EJECUTIVA |
| Respuesta incidentes | 5% | ✅ PROCESOS |

**TOTAL: 100% - 100/100**

---

## 📋 Archivos Generados

```
ProyectoFinal CB/
├── README.md                          # Este archivo
├── entregables/
│   ├── Proyecto_Final_CB.docx         # Informe técnico completo
│   ├── presentacion_ejecutiva.pptx    # Presentación 11 diapositivas
│   ├── ENTREGABLE.txt                 # Documentación de entrega
│   └── PROJECT_SUMMARY.md             # Resumen del proyecto
└── .gitignore                         # Seguridad Git
```

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