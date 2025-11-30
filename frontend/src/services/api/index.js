/**
 * Unified API module exports
 * Centralizes all API domain modules for consistent access
 */
import * as httpClient from '../httpClient'
import * as fincasApi from '../fincasApi'
import * as lotesApi from '../lotesApi'
import * as personasApi from '../personasApi'
import * as reportsApi from '../reportsApi'
import * as catalogosApi from '../catalogosApi'
import * as auditApi from '../auditApi'
import * as predictionApi from '../predictionApi'
import * as datasetApi from '../datasetApi'
import * as adminApi from '../adminApi'
import * as configApi from '../configApi'

// Re-export HTTP client methods
export const { get, post, put, patch, delete: del, upload, download } = httpClient

// Export domain APIs
export {
  fincasApi,
  lotesApi,
  personasApi,
  reportsApi,
  catalogosApi,
  auditApi,
  predictionApi,
  datasetApi,
  adminApi,
  configApi
}

// Export HTTP client for advanced usage
export { httpClient }

// Default export with all APIs organized
export default {
  // HTTP methods
  http: httpClient,
  
  // Domain APIs
  fincas: fincasApi,
  lotes: lotesApi,
  personas: personasApi,
  reports: reportsApi,
  catalogos: catalogosApi,
  audit: auditApi,
  prediction: predictionApi,
  dataset: datasetApi,
  admin: adminApi,
  config: configApi
}

