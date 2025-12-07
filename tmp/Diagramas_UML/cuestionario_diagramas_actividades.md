# Cuestionario Completo para Diagramas de Actividades UML - CacaoScan

Este documento contiene las respuestas al cuestionario para generar Diagramas de Actividades UML para todos los procesos del sistema CacaoScan.

---

## 1. REGISTRAR USUARIO

### 1.1 Identificación del Proceso
- **Proceso:** Registro de Usuario
- **Objetivo:** Permitir a nuevos usuarios crear una cuenta en el sistema, validando sus datos y generando tokens JWT automáticamente.

### 1.2 Actores y Participantes
- **Iniciador:** Usuario no autenticado (público)
- **Actores:**
  - Usuario no autenticado
  - Sistema de autenticación
  - Sistema de verificación de email
  - Base de datos PostgreSQL
- **Sistemas externos:**
  - Base de datos PostgreSQL
  - Servicio de email (opcional, para verificación)

### 1.3 Puntos de Inicio y Fin
- **Inicio:** Usuario accede al formulario de registro y envía datos
- **Fin exitoso:** Usuario creado, tokens JWT generados, respuesta HTTP 201
- **Fin con error:** Respuesta HTTP 400 con errores de validación
- **Fin con verificación requerida:** Usuario creado pero inactivo hasta verificación de email

### 1.4 Flujo Principal
1. Usuario completa formulario de registro (username, email, password, password_confirm, first_name, last_name)
2. Frontend valida campos requeridos
3. Petición HTTP POST a `/api/v1/auth/register/`
4. Backend valida permisos (AllowAny - público)
5. Serializer (`RegisterSerializer`) valida estructura y tipos
6. Servicio (`RegistrationService.register_user()`):
   - Valida campos requeridos
   - Valida que email no exista
   - Valida formato de email
   - Valida fortaleza de contraseña
   - Valida que passwords coincidan
   - Crea usuario con `is_active=False` (requiere verificación)
   - Crea token de verificación de email
   - Genera tokens JWT (access y refresh)
   - Crea log de auditoría
7. Modelo `User` ejecuta validaciones
8. PostgreSQL inserta registro
9. Retorna respuesta con usuario y tokens (o indicación de verificación requerida)

### 1.5 Decisiones y Bifurcaciones
- ¿Email único? → No: Error de validación
- ¿Formato de email válido? → No: Error de validación
- ¿Contraseña cumple requisitos? → No: Error de validación
- ¿Passwords coinciden? → No: Error de validación
- ¿Nombre y apellido presentes? → No: Error de validación
- ¿Verificación de email configurada? → Sí: Usuario inactivo hasta verificación; No: Usuario activo

### 1.6 Flujos Alternativos
- Email duplicado: Retornar error específico, no crear usuario
- Validación falla: Retornar errores específicos, no crear usuario
- Error de BD: Retornar 500, registrar en logs

### 1.7 Validaciones y Reglas de Negocio
- Email único en el sistema
- Formato de email válido
- Contraseña con fortaleza mínima (validación de seguridad)
- Passwords deben coincidir
- Nombre y apellido requeridos
- Username se establece igual al email automáticamente

### 1.8 Actividades Paralelas
- No hay paralelismo

### 1.9 Manejo de Errores
- **Errores posibles:**
  - 400: Validación fallida (email duplicado, formato inválido, contraseña débil)
  - 500: Error de BD o sistema
- **Manejo:** Captura de excepciones, logging, respuesta estructurada

### 1.10 Sistemas Externos
- Base de datos PostgreSQL (síncrono)
- Servicio de email (asíncrono, opcional)

---

## 2. INICIAR SESIÓN

### 2.1 Identificación del Proceso
- **Proceso:** Inicio de Sesión (Login)
- **Objetivo:** Autenticar un usuario con credenciales válidas y generar tokens JWT para acceso al sistema.

### 2.2 Actores y Participantes
- **Iniciador:** Usuario no autenticado
- **Actores:**
  - Usuario no autenticado
  - Sistema de autenticación Django
  - Sistema JWT
  - Base de datos PostgreSQL
- **Sistemas externos:**
  - Base de datos PostgreSQL
  - Sistema de auditoría (LoginHistory)

### 2.3 Puntos de Inicio y Fin
- **Inicio:** Usuario envía credenciales (username/email y password)
- **Fin exitoso:** Tokens JWT generados, usuario autenticado, respuesta HTTP 200
- **Fin con error:** Respuesta HTTP 401 con mensaje de credenciales inválidas

### 2.4 Flujo Principal
1. Usuario ingresa username/email y password en formulario
2. Frontend valida campos no vacíos
3. Petición HTTP POST a `/api/v1/auth/login/`
4. Backend valida permisos (AllowAny - público)
5. Serializer (`LoginSerializer`) valida estructura
6. Servicio (`LoginService.login_user()`):
   - Valida campos requeridos
   - Autentica usuario con `authenticate(username, password)`
   - Verifica que usuario exista
   - Verifica que usuario esté activo (`is_active=True`)
   - Genera tokens JWT (refresh y access)
   - Registra login en `LoginHistory`
   - Crea log de auditoría
   - Actualiza última actividad
7. Retorna respuesta con tokens y datos de usuario

### 2.5 Decisiones y Bifurcaciones
- ¿Credenciales válidas? → No: 401 Unauthorized
- ¿Usuario existe? → No: 401 Unauthorized
- ¿Usuario activo? → No: Error de validación
- ¿Autenticación exitosa? → Sí: Generar tokens; No: 401

### 2.6 Flujos Alternativos
- Credenciales inválidas: Retornar 401, no generar tokens
- Usuario inactivo: Retornar error específico
- Error de sistema: Retornar 500, registrar en logs

### 2.7 Validaciones y Reglas de Negocio
- Username/email y password requeridos
- Credenciales deben ser válidas
- Usuario debe existir
- Usuario debe estar activo
- Tokens JWT con expiración (access: 1 hora, refresh: 7 días)

### 2.8 Actividades Paralelas
- No hay paralelismo

### 2.9 Manejo de Errores
- **Errores posibles:**
  - 401: Credenciales inválidas, usuario inactivo
  - 500: Error de sistema
- **Manejo:** Captura de excepciones, logging, respuesta estructurada

### 2.10 Sistemas Externos
- Base de datos PostgreSQL (síncrono)
- Sistema de auditoría (síncrono)

---

## 3. SUBIR IMAGEN

*(Ya documentado anteriormente - ver respuesta inicial)*

---

## 4. PROCESAR IMAGEN

*(Ya documentado anteriormente como "Procesamiento de imagen de cacao" - ver respuesta inicial)*

---

## 5. ANALIZAR IMAGEN

### 5.1 Identificación del Proceso
- **Proceso:** Análisis de Imagen de Cacao
- **Objetivo:** Analizar una imagen de grano de cacao usando modelos ML para obtener predicciones de dimensiones y peso.

### 5.2 Actores y Participantes
- **Iniciador:** Usuario autenticado
- **Actores:**
  - Usuario autenticado
  - Servicio de análisis (`AnalysisService`)
  - Modelos ML (YOLOv8, modelos de regresión)
  - Base de datos PostgreSQL
- **Sistemas externos:**
  - Modelos ML (PyTorch)
  - Base de datos PostgreSQL
  - Sistema de archivos

### 5.3 Puntos de Inicio y Fin
- **Inicio:** Usuario envía imagen a `POST /api/v1/scan/measure/`
- **Fin exitoso:** Análisis completado, predicciones guardadas, respuesta HTTP 200 con resultados
- **Fin con error:** Respuesta HTTP 400/500 con mensaje de error

### 5.4 Flujo Principal
1. Usuario selecciona imagen y envía petición
2. Vista `ScanMeasureView` valida archivo
3. `AnalysisService.process_image_with_segmentation()`:
   - Valida imagen (tipo, tamaño, dimensiones)
   - Guarda imagen con segmentación
   - Carga imagen para predicción
   - Ejecuta predicción ML
   - Guarda predicción en BD
4. Retorna resultados con dimensiones, peso y confianzas

### 5.5 Decisiones y Bifurcaciones
- ¿Usuario autenticado? → No: 401
- ¿Imagen válida? → No: Error de validación
- ¿Modelos ML disponibles? → No: Error de sistema
- ¿Predicción exitosa? → No: Error de ML

### 5.6 Flujos Alternativos
- Validación falla: Retornar error específico
- Error de ML: Retornar 500, registrar en logs
- Error de almacenamiento: Retornar 500

### 5.7 Validaciones y Reglas de Negocio
- Autenticación requerida
- Tipo de archivo: JPG, PNG, BMP
- Tamaño máximo: 8MB
- Dimensiones mínimas requeridas
- Modelos ML deben estar disponibles

### 5.8 Actividades Paralelas
- No hay paralelismo explícito

### 5.9 Manejo de Errores
- **Errores posibles:**
  - 401: No autenticado
  - 400: Validación fallida
  - 500: Error de ML, almacenamiento o BD
- **Manejo:** Captura de excepciones, logging detallado

### 5.10 Sistemas Externos
- Modelos ML (PyTorch) - síncrono
- Base de datos PostgreSQL - síncrono
- Sistema de archivos - síncrono

---

## 6. VER RESULTADOS

### 6.1 Identificación del Proceso
- **Proceso:** Visualización de Resultados de Análisis
- **Objetivo:** Mostrar al usuario los resultados de un análisis de imagen previamente realizado.

### 6.2 Actores y Participantes
- **Iniciador:** Usuario autenticado
- **Actores:**
  - Usuario autenticado
  - Sistema de visualización frontend
  - API de consulta de predicciones
  - Base de datos PostgreSQL
- **Sistemas externos:**
  - Base de datos PostgreSQL
  - Sistema de archivos (imágenes)

### 6.3 Puntos de Inicio y Fin
- **Inicio:** Usuario solicita ver resultados (navegación o selección)
- **Fin exitoso:** Resultados mostrados en UI
- **Fin con error:** Mensaje de error en UI

### 6.4 Flujo Principal
1. Usuario navega a vista de resultados o selecciona análisis
2. Frontend solicita datos a API (`GET /api/v1/predictions/{id}/`)
3. Backend valida autenticación
4. Backend valida permisos (usuario puede ver su propio análisis)
5. Consulta `CacaoPrediction` en BD
6. Consulta `CacaoImage` asociada
7. Retorna datos serializados (dimensiones, peso, confianzas, imagen)
8. Frontend renderiza componentes (`PredictionResults`, `YoloResultsCard`)
9. Muestra métricas, gráficos y visualizaciones

### 6.5 Decisiones y Bifurcaciones
- ¿Usuario autenticado? → No: Redirigir a login
- ¿Análisis existe? → No: 404 Not Found
- ¿Usuario tiene permisos? → No: 403 Forbidden
- ¿Método de análisis YOLO? → Sí: Mostrar `YoloResultsCard`; No: Mostrar `PredictionResults`

### 6.6 Flujos Alternativos
- Análisis no encontrado: Mostrar mensaje, redirigir
- Sin permisos: Mostrar error 403
- Error de carga: Mostrar mensaje de error

### 6.7 Validaciones y Reglas de Negocio
- Autenticación requerida
- Usuario solo puede ver sus propios análisis (excepto admin)
- Análisis debe existir

### 6.8 Actividades Paralelas
- No hay paralelismo

### 6.9 Manejo de Errores
- **Errores posibles:**
  - 401: No autenticado
  - 403: Sin permisos
  - 404: Análisis no encontrado
  - 500: Error de sistema
- **Manejo:** Captura de excepciones, mensajes de error en UI

### 6.10 Sistemas Externos
- Base de datos PostgreSQL (síncrono)
- Sistema de archivos (síncrono, para cargar imágenes)

---

## 7. DESCARGAR REPORTE

### 7.1 Identificación del Proceso
- **Proceso:** Generación y Descarga de Reportes
- **Objetivo:** Generar reportes en formato Excel/PDF con información del sistema y permitir su descarga.

### 7.2 Actores y Participantes
- **Iniciador:** Usuario autenticado (con permisos)
- **Actores:**
  - Usuario autenticado
  - Servicio de generación de reportes
  - Generadores Excel/PDF
  - Base de datos PostgreSQL
- **Sistemas externos:**
  - Base de datos PostgreSQL
  - Sistema de archivos (almacenamiento temporal)
  - Librerías de generación (openpyxl, reportlab)

### 7.3 Puntos de Inicio y Fin
- **Inicio:** Usuario solicita generar reporte con filtros
- **Fin exitoso:** Archivo generado y descargado, respuesta HTTP 200 con archivo
- **Fin con error:** Respuesta HTTP 400/500 con mensaje de error

### 7.4 Flujo Principal
1. Usuario selecciona tipo de reporte y filtros
2. Frontend envía petición a API (`POST /api/v1/reports/` o endpoints específicos)
3. Backend valida autenticación y permisos
4. Servicio de generación (`ExcelAnalisisGenerator`, `ExcelAgricultoresGenerator`, etc.):
   - Valida tipo de reporte y formato
   - Consulta datos según filtros
   - Genera contenido Excel/PDF
   - Crea registro `ReporteGenerado`
   - Marca como "generando"
5. Genera archivo (Excel: openpyxl, PDF: reportlab)
6. Guarda archivo en almacenamiento
7. Marca reporte como "completado"
8. Retorna archivo para descarga o URL de descarga

### 7.5 Decisiones y Bifurcaciones
- ¿Usuario autenticado? → No: 401
- ¿Usuario tiene permisos? → No: 403
- ¿Tipo de reporte válido? → No: Error de validación
- ¿Formato válido? → No: Error de validación
- ¿Datos disponibles? → No: Reporte vacío o error
- ¿Generación exitosa? → No: Marcar como fallido

### 7.6 Flujos Alternativos
- Sin permisos: Retornar 403
- Tipo de reporte inválido: Retornar error de validación
- Error de generación: Marcar reporte como fallido, retornar 500
- Sin datos: Generar reporte vacío o retornar mensaje

### 7.7 Validaciones y Reglas de Negocio
- Autenticación requerida
- Permisos según tipo de reporte (admin para algunos)
- Tipos de reporte: calidad, finca, auditoría, usuarios, agricultores, personalizado
- Formatos: Excel, PDF, CSV, JSON
- Filtros opcionales (fechas, usuarios, fincas, etc.)

### 7.8 Actividades Paralelas
- Generación puede ser asíncrona (Celery) para reportes grandes

### 7.9 Manejo de Errores
- **Errores posibles:**
  - 401: No autenticado
  - 403: Sin permisos
  - 400: Validación fallida
  - 500: Error de generación
- **Manejo:** Captura de excepciones, logging, estados de reporte (pendiente, generando, completado, fallido)

### 7.10 Sistemas Externos
- Base de datos PostgreSQL (síncrono)
- Sistema de archivos (síncrono)
- Celery (asíncrono, opcional para reportes grandes)

---

## 8. CREAR FINCA

### 8.1 Identificación del Proceso
- **Proceso:** Creación de Finca Agrícola
- **Objetivo:** Permitir a usuarios autenticados crear una nueva finca asociada a un agricultor.

### 8.2 Actores y Participantes
- **Iniciador:** Usuario autenticado (agricultor, técnico o admin)
- **Actores:**
  - Usuario autenticado
  - Servicio de fincas (`FincaCRUDService`)
  - Base de datos PostgreSQL
- **Sistemas externos:**
  - Base de datos PostgreSQL
  - Sistema de auditoría

### 8.3 Puntos de Inicio y Fin
- **Inicio:** Usuario envía formulario con datos de finca
- **Fin exitoso:** Finca creada en BD, respuesta HTTP 201
- **Fin con error:** Respuesta HTTP 400/500 con mensaje de error

### 8.4 Flujo Principal
1. Usuario completa formulario (`FincaForm.vue`)
2. Frontend valida campos requeridos
3. Composable `useFincas` formatea datos
4. Servicio API envía POST a `/api/v1/fincas/`
5. Vista `FincaListCreateView` valida permisos
6. Serializer (`FincaSerializer`) valida estructura
7. Servicio (`FincaCRUDService.create_finca()`):
   - Valida permisos del usuario
   - Valida datos de finca (nombre, ubicación, hectáreas)
   - Valida que hectáreas sean positivas
   - Crea instancia `Finca`
   - Asocia con agricultor (usuario o especificado)
   - Crea log de auditoría
8. Modelo `Finca` ejecuta validaciones
9. PostgreSQL inserta registro
10. Retorna respuesta con finca creada

### 8.5 Decisiones y Bifurcaciones
- ¿Usuario autenticado? → No: 401
- ¿Usuario tiene permisos? → No: 403
- ¿Datos válidos? → No: 400
- ¿Hectáreas positivas? → No: Error de validación
- ¿Agricultor existe? (si se especifica) → No: Error de validación

### 8.6 Flujos Alternativos
- Validación falla: Retornar errores específicos
- Sin permisos: Retornar 403
- Error de BD: Retornar 500

### 8.7 Validaciones y Reglas de Negocio
- Autenticación requerida
- Campos requeridos: nombre, ubicación, municipio, departamento, hectáreas
- Hectáreas deben ser > 0
- Agricultor debe existir (si se especifica)
- Usuario debe poder gestionar fincas

### 8.8 Actividades Paralelas
- No hay paralelismo

### 8.9 Manejo de Errores
- **Errores posibles:**
  - 401: No autenticado
  - 403: Sin permisos
  - 400: Validación fallida
  - 500: Error de BD
- **Manejo:** Captura de excepciones, logging, respuesta estructurada

### 8.10 Sistemas Externos
- Base de datos PostgreSQL (síncrono)
- Sistema de auditoría (síncrono)

---

## 9. EDITAR FINCA

### 9.1 Identificación del Proceso
- **Proceso:** Actualización de Finca Agrícola
- **Objetivo:** Permitir a usuarios autenticados actualizar información de una finca existente.

### 9.2 Actores y Participantes
- **Iniciador:** Usuario autenticado con permisos sobre la finca
- **Actores:**
  - Usuario autenticado
  - Servicio de fincas (`FincaCRUDService`)
  - Base de datos PostgreSQL
- **Sistemas externos:**
  - Base de datos PostgreSQL
  - Sistema de auditoría

### 9.3 Puntos de Inicio y Fin
- **Inicio:** Usuario envía datos actualizados
- **Fin exitoso:** Finca actualizada, respuesta HTTP 200
- **Fin con error:** Respuesta HTTP 400/404/500

### 9.4 Flujo Principal
1. Usuario modifica datos en formulario
2. Frontend valida cambios
3. Composable `useFincas` formatea datos
4. Servicio API envía PUT/PATCH a `/api/v1/fincas/{id}/`
5. Vista `FincaDetailView` valida permisos
6. Serializer valida datos actualizados
7. Servicio (`FincaCRUDService.update_finca()`):
   - Valida que finca exista
   - Valida permisos del usuario
   - Valida datos actualizados
   - Actualiza campos permitidos
   - Crea log de auditoría
8. PostgreSQL actualiza registro
9. Retorna respuesta con finca actualizada

### 9.5 Decisiones y Bifurcaciones
- ¿Usuario autenticado? → No: 401
- ¿Finca existe? → No: 404
- ¿Usuario tiene permisos? → No: 403
- ¿Datos válidos? → No: 400

### 9.6 Flujos Alternativos
- Finca no encontrada: Retornar 404
- Sin permisos: Retornar 403
- Validación falla: Retornar 400

### 9.7 Validaciones y Reglas de Negocio
- Autenticación requerida
- Finca debe existir
- Usuario debe tener permisos sobre la finca
- Hectáreas deben ser positivas (si se actualiza)
- Campos requeridos deben estar presentes

### 9.8 Actividades Paralelas
- No hay paralelismo

### 9.9 Manejo de Errores
- **Errores posibles:**
  - 401: No autenticado
  - 403: Sin permisos
  - 404: Finca no encontrada
  - 400: Validación fallida
  - 500: Error de BD
- **Manejo:** Captura de excepciones, logging

### 9.10 Sistemas Externos
- Base de datos PostgreSQL (síncrono)
- Sistema de auditoría (síncrono)

---

## 10. CREAR LOTE

*(Ya documentado anteriormente - ver respuesta inicial)*

---

## 11. EDITAR LOTE

### 11.1 Identificación del Proceso
- **Proceso:** Actualización de Lote Agrícola
- **Objetivo:** Permitir a usuarios autenticados actualizar información de un lote existente.

### 11.2 Actores y Participantes
- **Iniciador:** Usuario autenticado con permisos sobre el lote
- **Actores:**
  - Usuario autenticado
  - Servicio de lotes (`LoteService`)
  - Base de datos PostgreSQL
- **Sistemas externos:**
  - Base de datos PostgreSQL
  - Sistema de auditoría

### 11.3 Puntos de Inicio y Fin
- **Inicio:** Usuario envía datos actualizados
- **Fin exitoso:** Lote actualizado, respuesta HTTP 200
- **Fin con error:** Respuesta HTTP 400/404/500

### 11.4 Flujo Principal
1. Usuario modifica datos en formulario
2. Frontend valida cambios
3. Composable `useLotes` formatea datos
4. Servicio API envía PUT/PATCH a `/api/v1/lotes/{id}/`
5. Vista `LoteUpdateView` valida permisos
6. Serializer (`LoteSerializer`) valida datos
7. Servicio (`LoteService.update_lote()`):
   - Valida que lote exista
   - Valida permisos del usuario
   - Valida reglas de negocio
   - Actualiza campos permitidos
   - Crea log de auditoría
8. PostgreSQL actualiza registro
9. Retorna respuesta con lote actualizado

### 11.5 Decisiones y Bifurcaciones
- ¿Usuario autenticado? → No: 401
- ¿Lote existe? → No: 404
- ¿Usuario tiene permisos? → No: 403
- ¿Datos válidos? → No: 400
- ¿Área válida? → No: Error de validación
- ¿Fechas válidas? → No: Error de validación

### 11.6 Flujos Alternativos
- Lote no encontrado: Retornar 404
- Sin permisos: Retornar 403
- Validación falla: Retornar 400

### 11.7 Validaciones y Reglas de Negocio
- Autenticación requerida
- Lote debe existir
- Usuario debe tener permisos sobre la finca del lote
- Área debe ser > 0
- Fecha de cosecha >= fecha de plantación
- Identificador único por finca (si se actualiza)

### 11.8 Actividades Paralelas
- No hay paralelismo

### 11.9 Manejo de Errores
- **Errores posibles:**
  - 401: No autenticado
  - 403: Sin permisos
  - 404: Lote no encontrado
  - 400: Validación fallida
  - 500: Error de BD
- **Manejo:** Captura de excepciones, logging

### 11.10 Sistemas Externos
- Base de datos PostgreSQL (síncrono)
- Sistema de auditoría (síncrono)

---

## 12. ELIMINAR LOTE

### 12.1 Identificación del Proceso
- **Proceso:** Eliminación de Lote Agrícola
- **Objetivo:** Permitir a usuarios autenticados eliminar un lote del sistema, validando que no tenga dependencias.

### 12.2 Actores y Participantes
- **Iniciador:** Usuario autenticado con permisos sobre el lote
- **Actores:**
  - Usuario autenticado
  - Servicio de lotes (`LoteService`)
  - Base de datos PostgreSQL
- **Sistemas externos:**
  - Base de datos PostgreSQL
  - Sistema de auditoría

### 12.3 Puntos de Inicio y Fin
- **Inicio:** Usuario solicita eliminar lote
- **Fin exitoso:** Lote eliminado, respuesta HTTP 204
- **Fin con error:** Respuesta HTTP 400/404/500

### 12.4 Flujo Principal
1. Usuario confirma eliminación
2. Frontend envía DELETE a `/api/v1/lotes/{id}/`
3. Vista `LoteDeleteView` valida permisos
4. Servicio (`LoteService.delete_lote()`):
   - Valida que lote exista
   - Valida permisos del usuario
   - Verifica si tiene análisis asociados (`cacao_images.exists()`)
   - Si tiene análisis: Retornar error 400
   - Si no tiene análisis:
     - Crea log de auditoría antes de eliminar
     - Elimina lote
5. PostgreSQL elimina registro (CASCADE si aplica)
6. Retorna respuesta 204 No Content

### 12.5 Decisiones y Bifurcaciones
- ¿Usuario autenticado? → No: 401
- ¿Lote existe? → No: 404
- ¿Usuario tiene permisos? → No: 403
- ¿Tiene análisis asociados? → Sí: Error 400; No: Continuar eliminación

### 12.6 Flujos Alternativos
- Lote no encontrado: Retornar 404
- Sin permisos: Retornar 403
- Tiene análisis: Retornar 400 con mensaje específico
- Error de BD: Retornar 500

### 12.7 Validaciones y Reglas de Negocio
- Autenticación requerida
- Lote debe existir
- Usuario debe tener permisos sobre la finca del lote
- Lote no debe tener análisis asociados (restricción de integridad)

### 12.8 Actividades Paralelas
- No hay paralelismo

### 12.9 Manejo de Errores
- **Errores posibles:**
  - 401: No autenticado
  - 403: Sin permisos
  - 404: Lote no encontrado
  - 400: Tiene análisis asociados
  - 500: Error de BD
- **Manejo:** Captura de excepciones, logging, mensajes específicos

### 12.10 Sistemas Externos
- Base de datos PostgreSQL (síncrono)
- Sistema de auditoría (síncrono)

---

## 13. VER HISTORIAL

### 13.1 Identificación del Proceso
- **Proceso:** Visualización de Historial de Análisis
- **Objetivo:** Permitir a usuarios autenticados consultar y visualizar todos los análisis de imágenes realizados anteriormente.

### 13.2 Actores y Participantes
- **Iniciador:** Usuario autenticado
- **Actores:**
  - Usuario autenticado
  - Servicio de análisis (`AnalysisService`)
  - Base de datos PostgreSQL
- **Sistemas externos:**
  - Base de datos PostgreSQL

### 13.3 Puntos de Inicio y Fin
- **Inicio:** Usuario accede a vista de historial
- **Fin exitoso:** Historial mostrado con paginación
- **Fin con error:** Mensaje de error en UI

### 13.4 Flujo Principal
1. Usuario navega a vista de historial
2. Frontend solicita datos a API (`GET /api/v1/analysis/history/`)
3. Backend valida autenticación
4. Servicio (`AnalysisService.get_analysis_history()`):
   - Construye queryset de `CacaoPrediction` del usuario
   - Aplica filtros (fechas, confianza, etc.)
   - Ordena por fecha descendente
   - Pagina resultados
   - Formatea datos
5. Retorna datos paginados
6. Frontend renderiza lista con componentes (`ImageHistoryCard`, `BaseHistoryCard`)
7. Muestra análisis con filtros y paginación

### 13.5 Decisiones y Bifurcaciones
- ¿Usuario autenticado? → No: Redirigir a login
- ¿Hay filtros aplicados? → Sí: Aplicar filtros; No: Mostrar todos
- ¿Hay más páginas? → Sí: Mostrar botón "Cargar más"; No: Fin

### 13.6 Flujos Alternativos
- Sin autenticación: Redirigir a login
- Sin resultados: Mostrar mensaje "Sin análisis"
- Error de carga: Mostrar mensaje de error

### 13.7 Validaciones y Reglas de Negocio
- Autenticación requerida
- Usuario solo ve sus propios análisis (excepto admin)
- Filtros opcionales: fechas, confianza mínima/máxima
- Paginación por defecto (20 por página)

### 13.8 Actividades Paralelas
- No hay paralelismo

### 13.9 Manejo de Errores
- **Errores posibles:**
  - 401: No autenticado
  - 500: Error de sistema
- **Manejo:** Captura de excepciones, mensajes en UI

### 13.10 Sistemas Externos
- Base de datos PostgreSQL (síncrono)

---

## 14. BUSCAR ANÁLISIS

### 14.1 Identificación del Proceso
- **Proceso:** Búsqueda y Filtrado de Análisis
- **Objetivo:** Permitir a usuarios autenticados filtrar y localizar análisis específicos utilizando criterios de búsqueda.

### 14.2 Actores y Participantes
- **Iniciador:** Usuario autenticado
- **Actores:**
  - Usuario autenticado
  - Servicio de análisis (`AnalysisService`)
  - Base de datos PostgreSQL
- **Sistemas externos:**
  - Base de datos PostgreSQL

### 14.3 Puntos de Inicio y Fin
- **Inicio:** Usuario ingresa criterios de búsqueda
- **Fin exitoso:** Resultados filtrados mostrados
- **Fin con error:** Mensaje de error

### 14.4 Flujo Principal
1. Usuario ingresa criterios de búsqueda (fechas, lote, finca, rango de peso, dimensiones, variedad)
2. Frontend valida criterios
3. Petición GET a `/api/v1/analysis/history/` con parámetros de búsqueda
4. Backend valida autenticación
5. Servicio aplica filtros al queryset:
   - Filtro por fechas (`date_from`, `date_to`)
   - Filtro por confianza (`min_confidence`, `max_confidence`)
   - Filtro por lote/finca
   - Filtro por rango de peso
   - Filtro por dimensiones
6. Retorna resultados filtrados y paginados
7. Frontend muestra resultados

### 14.5 Decisiones y Bifurcaciones
- ¿Usuario autenticado? → No: Redirigir
- ¿Criterios válidos? → No: Mostrar error de validación
- ¿Hay resultados? → Sí: Mostrar; No: Mensaje "Sin resultados"

### 14.6 Flujos Alternativos
- Criterios inválidos: Mostrar error de validación
- Sin resultados: Mostrar mensaje
- Error de sistema: Mostrar mensaje de error

### 14.7 Validaciones y Reglas de Negocio
- Autenticación requerida
- Fechas deben ser válidas
- Rangos deben ser coherentes (fecha_inicio <= fecha_fin)
- Usuario solo ve sus propios análisis (excepto admin)

### 14.8 Actividades Paralelas
- No hay paralelismo

### 14.9 Manejo de Errores
- **Errores posibles:**
  - 401: No autenticado
  - 400: Criterios inválidos
  - 500: Error de sistema
- **Manejo:** Captura de excepciones, mensajes en UI

### 14.10 Sistemas Externos
- Base de datos PostgreSQL (síncrono)

---

## 15. ENTRENAR MODELO

### 15.1 Identificación del Proceso
- **Proceso:** Entrenamiento de Modelos de Machine Learning
- **Objetivo:** Permitir a administradores o técnicos iniciar el proceso de entrenamiento automático de modelos ML para mejorar la precisión de las predicciones.

### 15.2 Actores y Participantes
- **Iniciador:** Usuario autenticado con rol admin o técnico
- **Actores:**
  - Administrador/Técnico
  - Pipeline de entrenamiento (`CacaoTrainingPipeline`)
  - Modelos ML (PyTorch, YOLOv8)
  - Base de datos PostgreSQL
  - Sistema de tareas asíncronas (Celery, opcional)
- **Sistemas externos:**
  - Modelos ML (PyTorch)
  - Base de datos PostgreSQL
  - Sistema de archivos (datasets, modelos)
  - GPU/CPU para entrenamiento

### 15.3 Puntos de Inicio y Fin
- **Inicio:** Administrador configura parámetros e inicia entrenamiento
- **Fin exitoso:** Modelos entrenados y guardados, respuesta HTTP 200
- **Fin con error:** Respuesta HTTP 400/500 con mensaje de error

### 15.4 Flujo Principal
1. Administrador accede a panel de entrenamiento
2. Configura parámetros (épocas, batch_size, learning_rate, modelo)
3. Frontend envía petición a API (`POST /api/v1/ml/train/` o `/api/v1/ml/auto-train/`)
4. Backend valida autenticación y permisos (admin)
5. Valida configuración
6. Pipeline de entrenamiento (`run_training_pipeline()`):
   - Valida dataset disponible
   - Carga datos (crops, targets, pixel_calibration.json)
   - Normaliza targets
   - Crea splits (train/val/test)
   - Crea DataLoaders
   - Crea modelo (HybridCacaoRegression, YOLOv8, etc.)
   - Entrena modelo (training loop con checkpoints, early stopping)
   - Evalúa modelo
   - Guarda modelo entrenado
   - Guarda métricas y logs
7. Retorna resultados del entrenamiento

### 15.5 Decisiones y Bifurcaciones
- ¿Usuario autenticado? → No: 401
- ¿Usuario es admin? → No: 403
- ¿Dataset disponible? → No: Error de validación
- ¿Configuración válida? → No: Error de validación
- ¿Entrenamiento síncrono o asíncrono? → Síncrono: Esperar; Asíncrono: Retornar job_id
- ¿GPU disponible? → Sí: Usar GPU; No: Usar CPU

### 15.6 Flujos Alternativos
- Sin permisos: Retornar 403
- Dataset no disponible: Retornar error específico
- Error durante entrenamiento: Marcar como fallido, retornar 500
- Entrenamiento asíncrono: Retornar job_id para monitoreo

### 15.7 Validaciones y Reglas de Negocio
- Autenticación requerida
- Rol admin o técnico requerido
- Dataset debe estar disponible y validado
- Parámetros de entrenamiento válidos (épocas > 0, batch_size > 0, etc.)
- Modelos ML deben estar disponibles

### 15.8 Actividades Paralelas
- Entrenamiento puede ejecutarse en background (Celery)
- Monitoreo de progreso puede ser paralelo

### 15.9 Manejo de Errores
- **Errores posibles:**
  - 401: No autenticado
  - 403: Sin permisos
  - 400: Validación fallida (dataset, configuración)
  - 500: Error durante entrenamiento
- **Manejo:** Captura de excepciones, logging detallado, estados de job (pending, running, completed, failed)

### 15.10 Sistemas Externos
- Modelos ML (PyTorch) - síncrono/asíncrono
- Base de datos PostgreSQL - síncrono
- Sistema de archivos - síncrono
- Celery (opcional, asíncrono)
- GPU/CPU (hardware)

---

## 16. CREAR AGRICULTOR

### 16.1 Identificación del Proceso
- **Proceso:** Creación de Agricultor por Administrador
- **Objetivo:** Permitir a un administrador registrar un nuevo agricultor en el sistema, creando su cuenta de usuario.

### 16.2 Actores y Participantes
- **Iniciador:** Administrador
- **Actores:**
  - Administrador
  - Servicio de registro (`PersonaRegistroView`, `RegistrationService`)
  - Base de datos PostgreSQL
- **Sistemas externos:**
  - Base de datos PostgreSQL
  - Servicio de email (opcional)

### 16.3 Puntos de Inicio y Fin
- **Inicio:** Administrador completa formulario de creación
- **Fin exitoso:** Agricultor creado, respuesta HTTP 201
- **Fin con error:** Respuesta HTTP 400/500

### 16.4 Flujo Principal
1. Administrador accede a gestión de usuarios
2. Selecciona "Crear Nuevo Agricultor"
3. Completa formulario (nombre, apellido, email, documento, teléfono, dirección, etc.)
4. Frontend valida campos
5. Petición POST a `/api/v1/personas/registro/`
6. Vista `PersonaRegistroView` valida que usuario sea admin
7. Si es admin: Crea usuario directamente sin verificación de email
8. Serializer (`PersonaRegistroSerializer`) valida datos
9. Crea usuario con rol "agricultor"
10. Crea registro de Persona asociado
11. Establece contraseña (temporal o generada)
12. Marca usuario como activo (skip_email_verification=True)
13. Crea log de auditoría
14. Retorna respuesta con datos del agricultor creado

### 16.5 Decisiones y Bifurcaciones
- ¿Usuario es admin? → No: 403
- ¿Email único? → No: Error de validación
- ¿Formato de email válido? → No: Error de validación
- ¿Documento único? (si se valida) → No: Error de validación
- ¿Admin creando? → Sí: Skip verificación de email; No: Flujo OTP normal

### 16.6 Flujos Alternativos
- Sin permisos: Retornar 403
- Email duplicado: Retornar error específico
- Validación falla: Retornar errores específicos
- Error de BD: Retornar 500

### 16.7 Validaciones y Reglas de Negocio
- Rol admin requerido
- Email único en el sistema
- Formato de email válido
- Documento único (si se valida)
- Campos obligatorios: nombre, apellido, email, documento
- Usuario creado con rol "agricultor" automáticamente
- Usuario activo inmediatamente (sin verificación de email si es admin)

### 16.8 Actividades Paralelas
- No hay paralelismo

### 16.9 Manejo de Errores
- **Errores posibles:**
  - 403: Sin permisos (no es admin)
  - 400: Validación fallida
  - 500: Error de BD
- **Manejo:** Captura de excepciones, logging, respuesta estructurada

### 16.10 Sistemas Externos
- Base de datos PostgreSQL (síncrono)
- Servicio de email (asíncrono, opcional)

---

## 17. EDITAR AGRICULTOR

### 17.1 Identificación del Proceso
- **Proceso:** Actualización de Agricultor por Administrador
- **Objetivo:** Permitir a un administrador actualizar la información de un agricultor existente.

### 17.2 Actores y Participantes
- **Iniciador:** Administrador
- **Actores:**
  - Administrador
  - Vista de actualización (`UserUpdateView`)
  - Base de datos PostgreSQL
- **Sistemas externos:**
  - Base de datos PostgreSQL
  - Sistema de auditoría

### 17.3 Puntos de Inicio y Fin
- **Inicio:** Administrador modifica datos del agricultor
- **Fin exitoso:** Agricultor actualizado, respuesta HTTP 200
- **Fin con error:** Respuesta HTTP 400/404/500

### 17.4 Flujo Principal
1. Administrador accede a detalles del agricultor
2. Selecciona "Editar"
3. Modifica campos (nombre, apellido, teléfono, dirección, estado, etc.)
4. Frontend valida cambios
5. Petición PATCH a `/api/v1/auth/users/{id}/`
6. Vista `UserUpdateView` valida permisos (admin)
7. Valida que usuario objetivo exista
8. Valida que no se desactive a sí mismo
9. Actualiza campos permitidos del usuario
10. Actualiza grupos/roles si se especifica
11. Crea log de auditoría
12. Retorna respuesta con usuario actualizado

### 17.5 Decisiones y Bifurcaciones
- ¿Usuario es admin? → No: 403
- ¿Agricultor existe? → No: 404
- ¿Admin intenta desactivarse a sí mismo? → Sí: Error de validación; No: Continuar
- ¿Datos válidos? → No: 400

### 17.6 Flujos Alternativos
- Sin permisos: Retornar 403
- Agricultor no encontrado: Retornar 404
- Auto-desactivación: Retornar error específico
- Validación falla: Retornar 400

### 17.7 Validaciones y Reglas de Negocio
- Rol admin requerido
- Agricultor debe existir
- No se puede desactivar a sí mismo
- Campos permitidos: first_name, last_name, is_active, groups
- Email no se puede cambiar desde aquí (requiere proceso separado)

### 17.8 Actividades Paralelas
- No hay paralelismo

### 17.9 Manejo de Errores
- **Errores posibles:**
  - 403: Sin permisos
  - 404: Agricultor no encontrado
  - 400: Validación fallida
  - 500: Error de BD
- **Manejo:** Captura de excepciones, logging

### 17.10 Sistemas Externos
- Base de datos PostgreSQL (síncrono)
- Sistema de auditoría (síncrono)

---

## 18. ASIGNAR ROL

### 18.1 Identificación del Proceso
- **Proceso:** Asignación de Rol a Usuario
- **Objetivo:** Permitir a un administrador definir y modificar los permisos de un usuario asignándole un rol específico.

### 18.2 Actores y Participantes
- **Iniciador:** Administrador
- **Actores:**
  - Administrador
  - Vista de actualización de usuario (`UserUpdateView`)
  - Sistema de grupos Django
  - Base de datos PostgreSQL
- **Sistemas externos:**
  - Base de datos PostgreSQL
  - Sistema de auditoría

### 18.3 Puntos de Inicio y Fin
- **Inicio:** Administrador selecciona usuario y nuevo rol
- **Fin exitoso:** Rol asignado, permisos actualizados, respuesta HTTP 200
- **Fin con error:** Respuesta HTTP 400/403/500

### 18.4 Flujo Principal
1. Administrador accede a gestión de usuarios
2. Selecciona usuario
3. Selecciona "Asignar Rol" o "Cambiar Rol"
4. Sistema muestra rol actual
5. Sistema muestra roles disponibles (admin, analyst, farmer)
6. Administrador selecciona nuevo rol
7. Frontend envía PATCH a `/api/v1/auth/users/{id}/` con campo `groups`
8. Vista `UserUpdateView` valida permisos (admin)
9. Valida que usuario objetivo exista
10. Valida que no se remueva el último admin
11. Actualiza grupos del usuario (`_update_user_groups()`)
12. Sistema actualiza permisos asociados al rol
13. Invalida sesiones activas del usuario (si aplica)
14. Crea log de auditoría
15. Retorna respuesta con usuario actualizado

### 18.5 Decisiones y Bifurcaciones
- ¿Usuario es admin? → No: 403
- ¿Usuario objetivo existe? → No: 404
- ¿Es el último admin? → Sí: Error de validación; No: Continuar
- ¿Rol válido? → No: Error de validación

### 18.6 Flujos Alternativos
- Sin permisos: Retornar 403
- Usuario no encontrado: Retornar 404
- Último admin: Retornar error específico
- Rol inválido: Retornar error de validación

### 18.7 Validaciones y Reglas de Negocio
- Rol admin requerido
- Usuario objetivo debe existir
- No se puede remover el último administrador del sistema
- Roles disponibles: admin, analyst (técnico), farmer (agricultor)
- Cambio de rol afecta permisos inmediatamente
- Sesiones activas se invalidan

### 18.8 Actividades Paralelas
- No hay paralelismo

### 18.9 Manejo de Errores
- **Errores posibles:**
  - 403: Sin permisos
  - 404: Usuario no encontrado
  - 400: Validación fallida (último admin, rol inválido)
  - 500: Error de BD
- **Manejo:** Captura de excepciones, logging, mensajes específicos

### 18.10 Sistemas Externos
- Base de datos PostgreSQL (síncrono)
- Sistema de auditoría (síncrono)
- Sistema de sesiones (síncrono, para invalidar)

---

## 19. EDITAR PERFIL

### 19.1 Identificación del Proceso
- **Proceso:** Actualización de Perfil de Usuario
- **Objetivo:** Permitir a un usuario autenticado actualizar sus propios datos personales e información de contacto.

### 19.2 Actores y Participantes
- **Iniciador:** Usuario autenticado
- **Actores:**
  - Usuario autenticado
  - Servicio de perfil (`ProfileService`)
  - Base de datos PostgreSQL
- **Sistemas externos:**
  - Base de datos PostgreSQL

### 19.3 Puntos de Inicio y Fin
- **Inicio:** Usuario modifica datos en formulario de perfil
- **Fin exitoso:** Perfil actualizado, respuesta HTTP 200
- **Fin con error:** Respuesta HTTP 400/500

### 19.4 Flujo Principal
1. Usuario accede a "Mi Perfil"
2. Modifica campos (nombre, apellido, teléfono, dirección, municipio, departamento)
3. Frontend valida cambios
4. Petición PATCH a `/api/v1/auth/profile/` o `/api/v1/personas/perfil/`
5. Backend valida autenticación
6. Servicio (`ProfileService.update_user_profile()` o `PersonaPerfilView.patch()`):
   - Separa campos de User y UserProfile/Persona
   - Valida campos permitidos
   - Valida email único (si se cambia)
   - Actualiza campos de User (first_name, last_name)
   - Actualiza campos de UserProfile/Persona (phone_number, etc.)
   - Guarda cambios
7. Retorna respuesta con perfil actualizado

### 19.5 Decisiones y Bifurcaciones
- ¿Usuario autenticado? → No: 401
- ¿Email único? (si se cambia) → No: Error de validación
- ¿Campos permitidos? → No: Error de validación
- ¿Datos válidos? → No: 400

### 19.6 Flujos Alternativos
- Sin autenticación: Retornar 401
- Email duplicado: Retornar error específico
- Campos no permitidos: Retornar error específico
- Validación falla: Retornar 400

### 19.7 Validaciones y Reglas de Negocio
- Autenticación requerida
- Usuario solo puede editar su propio perfil
- Campos permitidos: first_name, last_name, phone_number, dirección, municipio, departamento
- Email no se puede cambiar desde perfil (requiere proceso administrativo)
- Email debe ser único (si se permite cambiar)

### 19.8 Actividades Paralelas
- No hay paralelismo

### 19.9 Manejo de Errores
- **Errores posibles:**
  - 401: No autenticado
  - 400: Validación fallida
  - 500: Error de BD
- **Manejo:** Captura de excepciones, logging, respuesta estructurada

### 19.10 Sistemas Externos
- Base de datos PostgreSQL (síncrono)

---

## RESUMEN GENERAL

### Actores Comunes
- Usuario autenticado (agricultor, técnico, admin)
- Sistema de autenticación JWT
- Base de datos PostgreSQL
- Sistema de auditoría

### Validaciones Comunes
- Autenticación requerida (excepto registro y login)
- Permisos según rol
- Validación de datos de entrada
- Integridad referencial

### Manejo de Errores Común
- Captura de excepciones
- Logging estructurado
- Respuestas HTTP estandarizadas
- Sin fallbacks; errores explícitos

### Sistemas Externos Comunes
- Base de datos PostgreSQL (síncrono)
- Sistema de archivos (síncrono)
- Modelos ML (PyTorch) - síncrono/asíncrono
- Servicio de email (asíncrono, opcional)
- Celery (asíncrono, opcional)

---

**Nota:** Este documento contiene toda la información necesaria para generar Diagramas de Actividades UML para cada proceso. Cada proceso está documentado con el mismo nivel de detalle siguiendo el cuestionario estándar.

