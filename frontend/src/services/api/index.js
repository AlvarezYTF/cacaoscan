/**
 * Unified API module exports
 * Centralizes all API domain modules for consistent access
 */

// Re-export HTTP client methods
export { get, post, put, patch, delete as del, upload, download, httpClient } from '../httpClient'

// Re-export domain APIs using export...from
export * as fincasApi from '../fincasApi'
export * as lotesApi from '../lotesApi'
export * as personasApi from '../personasApi'
export * as reportsApi from '../reportsApi'
export * as catalogosApi from '../catalogosApi'
export * as auditApi from '../auditApi'
export * as predictionApi from '../predictionApi'
export * as datasetApi from '../datasetApi'
export * as adminApi from '../adminApi'
export * as configApi from '../configApi'

// Import for default export (needed for namespace access)
import { httpClient } from '../httpClient'
import * as fincasApiModule from '../fincasApi'
import * as lotesApiModule from '../lotesApi'
import * as personasApiModule from '../personasApi'
import * as reportsApiModule from '../reportsApi'
import * as catalogosApiModule from '../catalogosApi'
import * as auditApiModule from '../auditApi'
import * as predictionApiModule from '../predictionApi'
import * as datasetApiModule from '../datasetApi'
import * as adminApiModule from '../adminApi'
import * as configApiModule from '../configApi'

// Default export with all APIs organized
export default {
  // HTTP methods
  http: httpClient,
  
  // Domain APIs
  fincas: fincasApiModule,
  lotes: lotesApiModule,
  personas: personasApiModule,
  reports: reportsApiModule,
  catalogos: catalogosApiModule,
  audit: auditApiModule,
  prediction: predictionApiModule,
  dataset: datasetApiModule,
  admin: adminApiModule,
  config: configApiModule
}

