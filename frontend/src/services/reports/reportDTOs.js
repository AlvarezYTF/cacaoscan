/**
 * Report DTO Normalization
 * Normalizes report data structures from API responses to consistent frontend format
 */

/**
 * Normalize report DTO from API response
 * @param {Object} apiReport - Report data from API
 * @returns {Object} Normalized report DTO
 */
export function normalizeReportDTO(apiReport) {
  if (!apiReport) return null
  
  return {
    id: apiReport.id,
    tipo_reporte: apiReport.tipo_reporte || '',
    tipo_reporte_display: apiReport.tipo_reporte_display || apiReport.tipo_reporte || '',
    formato: apiReport.formato || '',
    formato_display: apiReport.formato_display || apiReport.formato?.toUpperCase() || '',
    titulo: apiReport.titulo || '',
    descripcion: apiReport.descripcion || '',
    estado: apiReport.estado || 'pendiente',
    estado_display: apiReport.estado_display || apiReport.estado || '',
    fecha_solicitud: apiReport.fecha_solicitud || apiReport.fecha_inicio || apiReport.created_at || null,
    fecha_generacion: apiReport.fecha_generacion || apiReport.fecha_fin || null,
    fecha_expiracion: apiReport.fecha_expiracion || null,
    tiempo_generacion_segundos: apiReport.tiempo_generacion_segundos || apiReport.tiempo_generacion || 0,
    tamano_archivo_mb: apiReport.tamano_archivo_mb || apiReport.tamano_archivo || 0,
    tamaño_archivo: apiReport.tamano_archivo_mb ? apiReport.tamano_archivo_mb * 1024 * 1024 : (apiReport.tamano_archivo || 0),
    archivo_url: apiReport.archivo_url || apiReport.archivo || null,
    esta_expirado: apiReport.esta_expirado || false,
    mensaje_error: apiReport.mensaje_error || null,
    parametros: apiReport.parametros || {},
    filtros_aplicados: apiReport.filtros_aplicados || apiReport.filtros || {},
    usuario_nombre: apiReport.usuario_nombre || apiReport.usuario?.nombre || apiReport.usuario?.username || '',
    usuario_id: apiReport.usuario_id || apiReport.usuario?.id || null
  }
}

/**
 * Normalize report list response
 * @param {Object} apiResponse - API response with reports list
 * @returns {Object} Normalized response with reports array
 */
export function normalizeReportListResponse(apiResponse) {
  if (!apiResponse) {
    return {
      reports: [],
      pagination: {
        currentPage: 1,
        totalPages: 1,
        totalItems: 0,
        itemsPerPage: 20
      }
    }
  }
  
  const reports = Array.isArray(apiResponse.results || apiResponse.data || apiResponse) 
    ? (apiResponse.results || apiResponse.data || apiResponse)
    : []
  
  return {
    reports: reports.map(normalizeReportDTO),
    pagination: {
      currentPage: apiResponse.current_page || apiResponse.page || 1,
      totalPages: apiResponse.total_pages || apiResponse.num_pages || 1,
      totalItems: apiResponse.total_count || apiResponse.count || apiResponse.total || 0,
      itemsPerPage: apiResponse.page_size || apiResponse.per_page || apiResponse.pageSize || 20
    }
  }
}

/**
 * Normalize report stats response
 * @param {Object} apiResponse - API response with stats
 * @returns {Object} Normalized stats
 */
export function normalizeReportStatsResponse(apiResponse) {
  if (!apiResponse) {
    return {
      totalReports: 0,
      reportsChange: 0,
      completedReports: 0,
      completedChange: 0,
      inProgressReports: 0,
      inProgressChange: 0,
      errorReports: 0,
      errorChange: 0,
      reportsByType: {},
      reportsByFormat: {},
      recentReports: []
    }
  }
  
  return {
    totalReports: apiResponse.total_reportes || apiResponse.totalReports || 0,
    reportsChange: apiResponse.reportsChange || 0,
    completedReports: apiResponse.reportes_completados || apiResponse.completedReports || 0,
    completedChange: apiResponse.completedChange || 0,
    inProgressReports: apiResponse.reportes_generando || apiResponse.inProgressReports || 0,
    inProgressChange: apiResponse.inProgressChange || 0,
    errorReports: apiResponse.reportes_fallidos || apiResponse.errorReports || 0,
    errorChange: apiResponse.errorChange || 0,
    reportsByType: apiResponse.reportes_por_tipo || apiResponse.reportsByType || {},
    reportsByFormat: apiResponse.reportes_por_formato || apiResponse.reportsByFormat || {},
    recentReports: (apiResponse.reportes_recientes || apiResponse.recentReports || []).map(normalizeReportDTO)
  }
}

/**
 * Build report request payload
 * @param {Object} formData - Form data
 * @returns {Object} Normalized request payload
 */
export function buildReportRequestPayload(formData) {
  return {
    tipo_reporte: formData.tipo_reporte || '',
    formato: formData.formato || '',
    titulo: formData.titulo || '',
    descripcion: formData.descripcion || '',
    parametros: formData.parametros || {},
    filtros: formData.filtros || formData.filtros_aplicados || {}
  }
}

