# Flujo de Descarga de Reporte con Comandos de Test

## Resumen del Flujo

El flujo de descarga de reporte permite al usuario generar y descargar reportes en formato PDF o Excel que contienen los resultados de análisis de imágenes de cacao con formato profesional.

---

## Componentes del Flujo

### 1. Frontend (Vue.js)

**Archivo:** `frontend/src/views/Reportes.vue` o `frontend/src/components/reportes/ReportDownloadButton.vue`

- El usuario selecciona opción "Descargar Reporte" desde la vista de resultados
- Se muestra modal o formulario para configurar el reporte (tipo, formato, filtros)
- Se envía petición POST a `/api/v1/reportes/` para generar el reporte
- Se monitorea el estado de generación del reporte
- Una vez listo, se descarga el archivo mediante GET a `/api/v1/reportes/{reporte_id}/download/`

**Código clave:**
```javascript
// Ejemplo de flujo en el frontend
const generateAndDownloadReport = async (reportConfig) => {
  try {
    // 1. Generar reporte
    const createResponse = await reportsApi.createReport({
      tipo_reporte: reportConfig.tipo,
      formato: reportConfig.formato,
      parametros: reportConfig.parametros,
      filtros_aplicados: reportConfig.filtros
    })
    
    const reporteId = createResponse.data.id
    
    // 2. Monitorear estado
    let reporte = await reportsApi.getReportDetails(reporteId)
    while (reporte.data.estado === 'pendiente' || reporte.data.estado === 'procesando') {
      await new Promise(resolve => setTimeout(resolve, 2000)) // Esperar 2 segundos
      reporte = await reportsApi.getReportDetails(reporteId)
    }
    
    // 3. Descargar si está completado
    if (reporte.data.estado === 'completado') {
      await reportsApi.downloadReport(reporteId)
    }
  } catch (error) {
    // Manejar errores
  }
}
```

### 2. Backend - Vista de Creación (Django REST Framework)

**Archivo:** `backend/reports/views/reports/report_crud_views.py`

**Vista:** `ReporteListCreateView`

**Flujo:**
1. Recibe petición POST con configuración del reporte
2. Valida datos mediante serializer
3. Crea registro de `ReporteGenerado` con estado "pendiente"
4. Inicia generación asíncrona del reporte (Celery)
5. Retorna ID del reporte y estado

**Código clave:**
```151:229:backend/reports/views/reports/report_crud_views.py
    def post(self, request):
        """Crear nuevo reporte."""
        try:
            serializer = ReporteSerializer(data=request.data, context={'request': request})
            
            if serializer.is_valid():
                reporte = serializer.save(usuario=request.user)
                
                # Iniciar generación asíncrona
                self._generate_report_async(reporte)
                
                return Response(
                    ReporteSerializer(reporte).data,
                    status=status.HTTP_201_CREATED
                )
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creando reporte: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_report_async(self, reporte):
        """Inicia generación asíncrona del reporte."""
        try:
            start_time = timezone.now()
            
            if reporte.formato == 'pdf':
                pdf_service = PDFAnalisisGenerator()
                # Generate content according to type
                if reporte.tipo_reporte == 'calidad':
                    content = pdf_service.generate_quality_report(request.user, reporte.filtros_aplicados)
                # ... otros tipos de reporte
            elif reporte.formato == 'excel':
                excel_service = ExcelAnalisisGenerator()
                # Generate content according to type
                if reporte.tipo_reporte == 'calidad':
                    content = excel_service.generate_quality_report(user, reporte.filtros_aplicados)
                # ... otros tipos de reporte
```

### 3. Backend - Vista de Descarga

**Archivo:** `backend/reports/views/reports/report_download_views.py`

**Vista:** `ReporteDownloadView`

**Flujo:**
1. Recibe petición GET con `reporte_id`
2. Valida que el reporte pertenezca al usuario
3. Verifica que el reporte esté en estado "completado"
4. Verifica que el archivo exista y no esté expirado
5. Retorna archivo como descarga

**Código clave:**
```56:90:backend/reports/views/reports/report_download_views.py
    def get(self, request, reporte_id):
        """Download report."""
        try:
            reporte = ReporteGenerado.objects.get(id=reporte_id, usuario=request.user)
            
            # Verify state
            if reporte.estado != 'completado':
                return Response({
                    'error': 'El reporte aún no está listo para descarga',
                    'details': 'El reporte aún no está listo para descarga'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify if expired
            if reporte.esta_expirado:
                return Response({
                    'error': 'El reporte ha expirado y ya no está disponible',
                    'details': 'El reporte ha expirado y ya no está disponible'
                }, status=status.HTTP_410_GONE)
            
            # Verify file exists
            if not reporte.archivo:
                return Response({
                    'error': 'El archivo del reporte no está disponible',
                    'details': 'El archivo del reporte no está disponible'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Prepare download response
            response = FileResponse(
                reporte.archivo,
                as_attachment=True,
                filename=reporte.nombre_archivo or f"{reporte.titulo}.{reporte.formato}"
            )
            
            # Configure headers according to format
            if
```

---

## Endpoints de la API

### Crear Reporte

**URL:** `POST /api/v1/reportes/`

**Autenticación:** Requerida (IsAuthenticated)

**Content-Type:** `application/json`

**Parámetros:**
- `tipo_reporte`: Tipo de reporte (calidad, finca, auditoria, personalizado)
- `formato`: Formato del reporte (pdf, excel, csv)
- `parametros`: Parámetros específicos del reporte (opcional)
- `filtros_aplicados`: Filtros a aplicar (opcional)

**Respuesta exitosa (201 Created):**
```json
{
  "id": 1,
  "titulo": "Reporte de Calidad",
  "tipo_reporte": "calidad",
  "formato": "pdf",
  "estado": "pendiente",
  "created_at": "2024-12-19T10:00:00Z"
}
```

### Descargar Reporte

**URL:** `GET /api/v1/reportes/{reporte_id}/download/`

**Autenticación:** Requerida (IsAuthenticated)

**Content-Type:** `application/pdf` o `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

**Respuesta exitosa (200 OK):**
- Archivo binario del reporte (PDF o Excel)
- Headers: `Content-Disposition: attachment; filename="reporte.pdf"`

**Respuesta con errores (400 Bad Request):**
```json
{
  "error": "El reporte aún no está listo para descarga",
  "details": "El reporte aún no está listo para descarga"
}
```

---

## Comandos de Test

### Configuración Inicial

**Desde el directorio `backend/`:**

```bash
# Asegúrate de estar en el directorio backend/
cd backend

# Activar entorno virtual (si no está activo)
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### Tests de Vistas (Reportes)

**Archivo:** `backend/reports/tests/test_report_views.py` (si existe)

#### Ejecutar todos los tests de reportes:

```bash
# Desde backend/
pytest reports/tests/test_report_views.py -v
```

#### Tests específicos:

```bash
# Test: Crear reporte exitoso
pytest reports/tests/test_report_views.py::TestReporteListCreateView::test_post_success -v

# Test: Descargar reporte exitoso
pytest reports/tests/test_report_views.py::TestReporteDownloadView::test_get_success -v

# Test: Reporte no encontrado
pytest reports/tests/test_report_views.py::TestReporteDownloadView::test_get_not_found -v

# Test: Reporte no completado
pytest reports/tests/test_report_views.py::TestReporteDownloadView::test_get_not_completed -v

# Test: Reporte expirado
pytest reports/tests/test_report_views.py::TestReporteDownloadView::test_get_expired -v

# Test: Sin permisos
pytest reports/tests/test_report_views.py::TestReporteDownloadView::test_get_no_permission -v
```

### Tests de Servicios (Generación de Reportes)

**Archivo:** `backend/reports/tests/test_report_services.py` (si existe)

```bash
# Test: Generar reporte PDF
pytest reports/tests/test_report_services.py::TestPDFGenerator::test_generate_quality_report -v

# Test: Generar reporte Excel
pytest reports/tests/test_report_services.py::TestExcelGenerator::test_generate_quality_report -v
```

### Ejecutar Todos los Tests de Reportes

```bash
# Desde backend/
pytest reports/tests/ -v
```

### Ejecutar con Cobertura

```bash
# Desde backend/
pytest reports/tests/test_report_views.py --cov=reports.views.reports --cov-report=html
```

---

## Flujo Completo Paso a Paso

### 1. Usuario solicita descargar reporte
- Desde vista de resultados o historial
- Selecciona tipo de reporte y formato

### 2. Petición HTTP POST para crear reporte
- Endpoint: `/api/v1/reportes/`
- Headers: `Authorization: Bearer <token>`, `Content-Type: application/json`
- Body: Configuración del reporte

### 3. Backend crea reporte
- Crea registro de `ReporteGenerado` con estado "pendiente"
- Inicia generación asíncrona del reporte
- Retorna ID del reporte

### 4. Frontend monitorea estado
- Consulta periódicamente el estado del reporte
- Espera hasta que el estado sea "completado"

### 5. Petición HTTP GET para descargar
- Endpoint: `/api/v1/reportes/{reporte_id}/download/`
- Headers: `Authorization: Bearer <token>`

### 6. Backend valida y retorna archivo
- Verifica permisos del usuario
- Verifica que el reporte esté completado
- Verifica que no esté expirado
- Retorna archivo como descarga

### 7. Frontend descarga archivo
- Crea blob del archivo
- Inicia descarga en el navegador

---

## Validaciones Implementadas

### Estado del Reporte
- **Pendiente:** Reporte en cola de generación
- **Procesando:** Reporte siendo generado
- **Completado:** Reporte listo para descarga
- **Error:** Error en la generación
- **Validación:** En backend antes de descargar
- **Error:** "El reporte aún no está listo para descarga"

### Expiración
- **Duración:** 30 días desde la creación
- **Validación:** En backend antes de descargar
- **Error:** "El reporte ha expirado y ya no está disponible"

### Permisos
- **Propietario:** El usuario solo puede descargar sus propios reportes
- **Validación:** En backend al obtener el reporte
- **Error:** 404 Not Found si no tiene permisos

---

## Ejemplo de Uso con cURL

```bash
# Crear reporte
curl -X POST http://localhost:8000/api/v1/reportes/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_reporte": "calidad",
    "formato": "pdf",
    "filtros_aplicados": {
      "fecha_desde": "2024-01-01",
      "fecha_hasta": "2024-12-31"
    }
  }'

# Descargar reporte (después de que esté completado)
curl -X GET http://localhost:8000/api/v1/reportes/1/download/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output reporte.pdf
```

---

## Troubleshooting

### Error: "El reporte aún no está listo para descarga"
**Causa:** El reporte aún está siendo generado o está en estado pendiente.
**Solución:** Esperar a que el reporte se complete o verificar el estado.

### Error: "El reporte ha expirado"
**Causa:** El reporte tiene más de 30 días desde su creación.
**Solución:** Generar un nuevo reporte.

### Error: "El archivo del reporte no está disponible"
**Causa:** El archivo fue eliminado o no se generó correctamente.
**Solución:** Generar un nuevo reporte o contactar al administrador.

### Error: Reporte tarda mucho en generarse
**Causa:** El reporte es muy grande o hay muchos datos.
**Solución:** Aplicar filtros para reducir el tamaño del reporte o esperar más tiempo.

---

## Archivos Relacionados

### Backend
- `backend/reports/views/reports/report_crud_views.py` - Vistas de CRUD de reportes
- `backend/reports/views/reports/report_download_views.py` - Vistas de descarga
- `backend/reports/services/report/report_generation_service.py` - Servicio de generación
- `backend/reports/models.py` - Modelo ReporteGenerado
- `backend/reports/urls.py` - URLs de reportes

### Frontend
- `frontend/src/views/Reportes.vue` - Vista principal de reportes
- `frontend/src/components/reportes/ReportDownloadButton.vue` - Botón de descarga
- `frontend/src/services/reportsService.js` - Servicio de API de reportes
- `frontend/src/stores/reports.js` - Store de reportes (Pinia)
- `frontend/src/composables/useReports.js` - Composable de reportes

---

## Notas Adicionales

- Los reportes se generan de forma asíncrona para no bloquear la aplicación
- Los reportes se almacenan por 30 días antes de expirar
- El formato PDF usa PDF/A para compatibilidad a largo plazo
- El formato Excel usa .xlsx (Office Open XML)
- Los reportes incluyen marca de agua con información del usuario y timestamp
- El tamaño del archivo PDF no debe exceder 10MB

