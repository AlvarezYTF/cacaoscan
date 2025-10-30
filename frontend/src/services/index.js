/**
 * Índice centralizado de servicios de API
 * 
 * Este archivo exporta todos los servicios de API disponibles
 * para facilitar las importaciones en componentes y vistas.
 * 
 * Uso:
 * import { notificationsApi, auditApi, calibrationApi } from '@/services'
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

// Servicios nuevos (completando integración backend-frontend)
export { default as notificationsApi } from './notificationsApi'
export { default as auditApi } from './auditApi'
export { default as calibrationApi } from './calibrationApi'
export { default as modelMetricsApi } from './modelMetricsApi'
export { default as incrementalTrainingApi } from './incrementalTrainingApi'
export { default as modelsApi } from './modelsApi'

/**
 * Mapa de servicios por funcionalidad
 * Útil para importaciones dinámicas o configuración avanzada
 */
export const SERVICE_MAP = {
  // Autenticación y usuarios
  auth: () => import('./authApi'),
  
  // Análisis y predicción
  prediction: () => import('./predictionApi'),
  analysis: () => import('./servicioAnalisis'),
  
  // Gestión de fincas y lotes
  fincas: () => import('./fincasApi'),
  lotes: () => import('./lotesApi'),
  
  // Reportes
  reports: () => import('./reportsService'),
  
  // Administración
  admin: () => import('./adminApi'),
  dataset: () => import('./datasetApi'),
  
  // Sistema
  notifications: () => import('./notificationsApi'),
  audit: () => import('./auditApi'),
  calibration: () => import('./calibrationApi'),
  modelMetrics: () => import('./modelMetricsApi'),
  incrementalTraining: () => import('./incrementalTrainingApi'),
  models: () => import('./modelsApi'),
  
  // Dashboard
  dashboardStats: () => import('./dashboardStatsService')
}

/**
 * Categorías de servicios
 */
export const SERVICE_CATEGORIES = {
  AUTHENTICATION: ['auth'],
  ANALYSIS: ['prediction', 'analysis'],
  FARM_MANAGEMENT: ['fincas', 'lotes'],
  REPORTS: ['reports'],
  ADMIN: ['admin', 'dataset'],
  SYSTEM: ['notifications', 'audit', 'calibration', 'modelMetrics', 'incrementalTraining', 'models'],
  DASHBOARD: ['dashboardStats']
}

/**
 * Obtiene un servicio de forma dinámica
 * @param {string} serviceName - Nombre del servicio
 * @returns {Promise<Object>} - Módulo del servicio
 */
export async function getService(serviceName) {
  if (!SERVICE_MAP[serviceName]) {
    throw new Error(`Servicio no encontrado: ${serviceName}`)
  }
  
  const module = await SERVICE_MAP[serviceName]()
  return module.default
}

/**
 * Obtiene múltiples servicios de forma dinámica
 * @param {Array<string>} serviceNames - Nombres de los servicios
 * @returns {Promise<Object>} - Objeto con los servicios cargados
 */
export async function getServices(serviceNames) {
  const services = {}
  
  await Promise.all(
    serviceNames.map(async (name) => {
      services[name] = await getService(name)
    })
  )
  
  return services
}

/**
 * Obtiene todos los servicios de una categoría
 * @param {string} category - Categoría de servicios
 * @returns {Promise<Object>} - Objeto con los servicios de la categoría
 */
export async function getServicesByCategory(category) {
  const serviceNames = SERVICE_CATEGORIES[category]
  
  if (!serviceNames) {
    throw new Error(`Categoría no encontrada: ${category}`)
  }
  
  return await getServices(serviceNames)
}

// Exportación por defecto con todos los servicios
export default {
  // API base
  api: () => import('./api'),
  
  // Servicios principales
  authApi: () => import('./authApi'),
  predictionApi: () => import('./predictionApi'),
  fincasApi: () => import('./fincasApi'),
  lotesApi: () => import('./lotesApi'),
  reportsService: () => import('./reportsService'),
  datasetApi: () => import('./datasetApi'),
  adminApi: () => import('./adminApi'),
  dashboardStatsService: () => import('./dashboardStatsService'),
  servicioAnalisis: () => import('./servicioAnalisis'),
  
  // Servicios del sistema
  notificationsApi: () => import('./notificationsApi'),
  auditApi: () => import('./auditApi'),
  calibrationApi: () => import('./calibrationApi'),
  modelMetricsApi: () => import('./modelMetricsApi'),
  incrementalTrainingApi: () => import('./incrementalTrainingApi'),
  modelsApi: () => import('./modelsApi'),
  
  // Utilidades
  getService,
  getServices,
  getServicesByCategory
}

