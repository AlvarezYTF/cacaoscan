import {
  getApiBaseUrl,
  visitAndWaitForBody,
  verifyErrorMessageWithSelectors,
  openModalAndExecute,
  setupErrorInterceptAndVerify,
  uploadFileAndVerifyErrorAfterIntercept,
  setupDirectInterceptAndVerify
} from '../../support/helpers'

describe('Manejo de Errores - Errores de Red', () => {
  beforeEach(() => {
    cy.login('farmer')
  })

  it('debe manejar error 500 del servidor', () => {
    setupErrorInterceptAndVerify(
      {
        method: 'GET',
        urlPattern: '/fincas/**',
        statusCode: 500,
        errorBody: { error: 'Error interno del servidor' },
        alias: 'serverError'
      },
      '/mis-fincas',
      ['[data-cy="error-message"], .error-message, .swal2-error'],
      ['error', 'servidor', '500']
    )
    cy.retryIfAvailable()
  })

  it('debe manejar error 404 - Recurso no encontrado', () => {
    setupErrorInterceptAndVerify(
      {
        method: 'GET',
        urlPattern: '/fincas/**/',
        statusCode: 404,
        errorBody: { error: 'Finca no encontrada' },
        alias: 'notFound'
      },
      '/mis-fincas',
      ['[data-cy="error-message"], .error-message, .swal2-error'],
      ['no encontrado', '404', 'not found']
    )
  })

  it('debe manejar error 403 - Acceso denegado', () => {
    setupErrorInterceptAndVerify(
      {
        method: 'GET',
        urlPattern: '/admin/**',
        statusCode: 403,
        errorBody: { error: 'Acceso denegado' },
        alias: 'forbidden'
      },
      '/admin/agricultores',
      ['[data-cy="error-message"], .error-message, .swal2-error'],
      ['acceso', 'denegado', '403']
    )
  })

  it('debe manejar error 401 - No autorizado', () => {
    cy.interceptError('GET', '/fincas/**', 401, { error: 'Token inválido' }, 'unauthorized')
    visitAndWaitForBody('/mis-fincas')
    cy.url({ timeout: 5000 }).should('satisfy', (url) => {
      return url.includes('/login') || url.includes('/auth') || url.includes('/mis-fincas') || url.length > 0
    })
    verifyErrorMessageWithSelectors(
      ['[data-cy="session-expired-message"], .session-expired'],
      ['sesión', 'expirada', 'expirado']
    )
  })

  it('debe manejar error de timeout', () => {
    setupErrorInterceptAndVerify(
      {
        method: 'GET',
        urlPattern: '/fincas/**',
        statusCode: 408,
        errorBody: { error: 'Timeout' },
        alias: 'timeoutError'
      },
      '/mis-fincas',
      ['[data-cy="error-message"], .error-message, .swal2-error'],
      ['timeout', 'tiempo', '408']
    )
  })

  it('debe manejar error de conexión', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, {
      forceNetworkError: true
    }).as('networkError')
    visitAndWaitForBody('/mis-fincas')
    verifyErrorMessageWithSelectors(
      ['[data-cy="error-message"], .error-message, .swal2-error'],
      ['conexión', 'conexion', 'network', 'error']
    )
  })

  it('debe manejar error de validación del servidor', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('POST', `${apiBaseUrl}/fincas/`, {
      statusCode: 400,
      body: { 
        error: 'Error de validación',
        details: {
          nombre: ['Este campo es requerido'],
          area: ['El área debe ser positiva']
        }
      }
    }).as('validationError')
    visitAndWaitForBody('/mis-fincas')
    openModalAndExecute('[data-cy="add-finca-button"], button', ($modal) => {
      if ($modal.find('[data-cy="finca-nombre"], input').length > 0) {
        cy.get('[data-cy="finca-nombre"], input').first().type('Finca Test', { force: true })
        cy.get('[data-cy="finca-area"], input[type="number"]').first().type('-5', { force: true })
        cy.get('[data-cy="save-finca"], button[type="submit"]').first().click({ force: true })
        cy.wait('@validationError', { timeout: 10000 })
        verifyErrorMessageWithSelectors(
          ['[data-cy="validation-error"], .error-message, .swal2-error'],
          ['validación', 'validacion', 'error']
        )
      }
    })
  })

  it('debe manejar error de límite de tasa', () => {
    cy.interceptError('POST', '/fincas/', 429, { error: 'Límite de tasa excedido' }, 'rateLimit')
    visitAndWaitForBody('/mis-fincas')
    openModalAndExecute('[data-cy="add-finca-button"], button', ($modal) => {
      if ($modal.find('[data-cy="save-finca"], button[type="submit"]').length > 0) {
        cy.get('[data-cy="save-finca"], button[type="submit"]').first().click({ force: true })
        cy.wait('@rateLimit', { timeout: 10000 })
        verifyErrorMessageWithSelectors(
          ['[data-cy="error-message"], .error-message, .swal2-error'],
          ['límite', 'tasa', 'excedido', '429']
        )
      }
    })
  })

  it('debe manejar error de mantenimiento', () => {
    cy.interceptError('GET', '/fincas/**', 503, { error: 'Sistema en mantenimiento' }, 'maintenance')
    visitAndWaitForBody('/mis-fincas')
    verifyErrorMessageWithSelectors(
      ['[data-cy="maintenance-message"], .maintenance-message, .error-message'],
      ['mantenimiento', '503', 'sistema']
    )
  })

  it('debe manejar error de formato de respuesta', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, {
      statusCode: 200,
      body: 'invalid json'
    }).as('malformedResponse')
    visitAndWaitForBody('/mis-fincas')
    verifyErrorMessageWithSelectors(
      ['[data-cy="error-message"], .error-message, .swal2-error'],
      ['procesar', 'respuesta', 'formato', 'error']
    )
  })

  it('debe manejar error de carga de archivo', () => {
    cy.interceptError('POST', '/images/**', 413, { error: 'Archivo demasiado grande' }, 'fileTooLarge')
    visitAndWaitForBody('/nuevo-analisis')
    const fileContent = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAD/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AKgAD//Z'
    uploadFileAndVerifyErrorAfterIntercept(
      '[data-cy="file-input"], input[type="file"]',
      fileContent,
      'test-cacao.jpg',
      '[data-cy="upload-button"], button[type="submit"]',
      'fileTooLarge',
      ['[data-cy="upload-error"], .error-message, .swal2-error'],
      ['grande', 'archivo', 'demasiado', '413']
    )
  })

  it('debe manejar error de análisis de imagen', () => {
    cy.interceptError('POST', '/scan/**', 422, { error: 'Imagen no válida para análisis' }, 'analysisError')
    visitAndWaitForBody('/nuevo-analisis')
    const fileContent = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAD/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AKgAD//Z'
    uploadFileAndVerifyErrorAfterIntercept(
      '[data-cy="file-input"], input[type="file"]',
      fileContent,
      'test-cacao.jpg',
      '[data-cy="upload-button"], button[type="submit"]',
      'analysisError',
      ['[data-cy="analysis-error"], .error-message, .swal2-error'],
      ['válida', 'análisis', 'imagen', '422']
    )
  })

  it('debe manejar error de generación de reporte', () => {
    cy.login('analyst')
    cy.interceptError('POST', '/reportes/', 422, { error: 'No hay datos para el período seleccionado' }, 'reportError')
    visitAndWaitForBody('/reportes')
    openModalAndExecute('[data-cy="create-report-button"], button', ($modal) => {
      if ($modal.find('[data-cy="report-type"], select').length > 0) {
        cy.get('[data-cy="report-type"], select').first().select('analisis-periodo', { force: true })
        cy.get('[data-cy="start-date"], input[type="date"]').first().type('2024-01-01', { force: true })
        cy.get('[data-cy="end-date"], input[type="date"]').first().type('2024-01-31', { force: true })
        cy.get('[data-cy="generate-report"], button[type="submit"]').first().click({ force: true })
        cy.wait('@reportError', { timeout: 10000 })
        verifyErrorMessageWithSelectors(
          ['[data-cy="generation-error"], .error-message, .swal2-error'],
          ['datos', 'período', 'seleccionado', '422']
        )
      }
    })
  })

  it('debe manejar error de servicio no disponible', () => {
    const apiBaseUrl = getApiBaseUrl()
    setupDirectInterceptAndVerify(
      {
        method: 'GET',
        url: `${apiBaseUrl}/fincas/`,
        statusCode: 503,
        body: { error: 'Servicio no disponible' },
        alias: 'serviceUnavailable'
      },
      '/mis-fincas',
      '[data-cy="error-message"]',
      'Servicio no disponible'
    )
  })

  it('debe manejar error de gateway', () => {
    const apiBaseUrl = getApiBaseUrl()
    setupDirectInterceptAndVerify(
      {
        method: 'GET',
        url: `${apiBaseUrl}/fincas/`,
        statusCode: 502,
        body: { error: 'Bad Gateway' },
        alias: 'badGateway'
      },
      '/mis-fincas',
      '[data-cy="error-message"]',
      'Error del servidor'
    )
  })

  it('debe manejar error de versión no soportada', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('GET', `${apiBaseUrl}/fincas/`, {
      statusCode: 505,
      body: { error: 'Versión HTTP no soportada' }
    }).as('versionError')
    visitAndWaitForBody('/mis-fincas')
    cy.wait('@versionError')
    cy.get('[data-cy="error-message"]').should('be.visible')
  })

  it('debe manejar error de payload demasiado grande', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('POST', `${apiBaseUrl}/images/`, {
      statusCode: 413,
      body: { error: 'Payload demasiado grande' }
    }).as('payloadTooLarge')
    visitAndWaitForBody('/nuevo-analisis')
    cy.get('[data-cy="upload-button"]').click()
    cy.wait('@payloadTooLarge')
    cy.get('[data-cy="upload-error"]')
      .should('be.visible')
      .and('contain', 'Archivo demasiado grande')
  })

  it('debe manejar error de método no permitido', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('PATCH', `${apiBaseUrl}/fincas/1/`, {
      statusCode: 405,
      body: { error: 'Método no permitido' }
    }).as('methodNotAllowed')
    visitAndWaitForBody('/mis-fincas')
    cy.wait('@methodNotAllowed')
    cy.get('[data-cy="error-message"]').should('be.visible')
  })
})
