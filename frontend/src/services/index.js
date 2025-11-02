/**
 * Índice centralizado de servicios de API
 * 
 * Este archivo exporta todos los servicios de API disponibles
 * para facilitar las importaciones en componentes y vistas.
 * 
 * Uso:
 * import { authApi, fincasApi, lotesApi } from '@/services'
 */

// Servicios principales
export { default as api } from './api'
export { default as authApi } from './authApi'
export { default as catalogosApi } from './catalogosApi'
export { default as personasApi } from './personasApi'
export { default as predictionApi } from './predictionApi'
export { default as fincasApi } from './fincasApi'
export { default as lotesApi } from './lotesApi'
export { default as reportsService } from './reportsService'
export { default as datasetApi } from './datasetApi'
export { default as adminApi } from './adminApi'
export { default as dashboardStatsService } from './dashboardStatsService'
export { default as servicioAnalisis } from './servicioAnalisis'
export { default as auditApi } from './auditApi'
export { default as configApi } from './configApi'

// Exportación por defecto con todos los servicios (para compatibilidad)
export default {
  api: () => import('./api'),
  authApi: () => import('./authApi'),
  catalogosApi: () => import('./catalogosApi'),
  personasApi: () => import('./personasApi'),
  predictionApi: () => import('./predictionApi'),
  fincasApi: () => import('./fincasApi'),
  lotesApi: () => import('./lotesApi'),
  reportsService: () => import('./reportsService'),
  datasetApi: () => import('./datasetApi'),
  adminApi: () => import('./adminApi'),
  dashboardStatsService: () => import('./dashboardStatsService'),
  servicioAnalisis: () => import('./servicioAnalisis'),
  auditApi: () => import('./auditApi'),
  configApi: () => import('./configApi')
}

