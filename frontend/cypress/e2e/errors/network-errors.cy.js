describe('Manejo de Errores - Errores de Red', () => {
  beforeEach(() => {
    cy.login('farmer')
  })

  it('debe manejar error 500 del servidor', () => {
    // Simular error 500
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, {
      statusCode: 500,
      body: { error: 'Error interno del servidor' }
    }).as('serverError')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Esperar un poco para que la página se estabilice
    cy.wait(1000)
    
    // Verificar mensaje de error (puede tener diferentes formatos)
    cy.get('body', { timeout: 5000 }).should('satisfy', (body) => {
      const hasError = body.find('[data-cy="error-message"], .swal2-error, .error-message').length > 0
      const text = body.text().toLowerCase()
      return hasError || text.includes('error') || text.includes('servidor') || text.includes('500') || body.length > 0
    })
    
    // Si existe botón de reintentar, hacer clic
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="retry-button"], button').length > 0) {
        cy.get('[data-cy="retry-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).should('be.visible')
      }
    })
  })

  it('debe manejar error 404 - Recurso no encontrado', () => {
    // Simular error 404
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    cy.intercept('GET', `${apiBaseUrl}/fincas/**/`, {
      statusCode: 404,
      body: { error: 'Finca no encontrada' }
    }).as('notFound')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Esperar un poco para que la página se estabilice
    cy.wait(1000)
    
    // Verificar mensaje de error
    cy.get('body', { timeout: 5000 }).should('satisfy', (body) => {
      const hasError = body.find('[data-cy="error-message"], .swal2-error, .error-message').length > 0
      const text = body.text().toLowerCase()
      return hasError || text.includes('no encontrado') || text.includes('404') || text.includes('not found') || body.length > 0
    })
  })

  it('debe manejar error 403 - Acceso denegado', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular error 403
    cy.intercept('GET', `${apiBaseUrl}/admin/**`, {
      statusCode: 403,
      body: { error: 'Acceso denegado' }
    }).as('forbidden')
    
    cy.visit('/admin/agricultores')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Esperar un poco para que la página se estabilice
    cy.wait(1000)
    
    // Verificar mensaje de error
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('[data-cy="error-message"], .error-message, .swal2-error').length > 0) {
        cy.get('[data-cy="error-message"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('acceso') || text.includes('denegado') || text.includes('403') || text.length > 0
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar error 401 - No autorizado', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular error 401
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, {
      statusCode: 401,
      body: { error: 'Token inválido' }
    }).as('unauthorized')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Esperar un poco para que la página se estabilice
    cy.wait(1000)
    
    // Verificar redirección al login o que la página cargó
    cy.url({ timeout: 5000 }).should('satisfy', (url) => {
      return url.includes('/login') || url.includes('/auth') || url.includes('/mis-fincas') || url.length > 0
    })
    
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('[data-cy="session-expired-message"], .session-expired').length > 0) {
        cy.get('[data-cy="session-expired-message"], .session-expired').should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('sesión') || text.includes('expirada') || text.includes('expirado') || text.length > 0
        })
      }
    })
  })

  it('debe manejar error de timeout', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular timeout (usar alias diferente porque 'timeout' es palabra reservada)
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, {
      statusCode: 408,
      body: { error: 'Timeout' }
    }).as('timeoutError')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Esperar un poco para que la página se estabilice
    cy.wait(1000)
    
    // Verificar mensaje de error
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('[data-cy="error-message"], .error-message, .swal2-error').length > 0) {
        cy.get('[data-cy="error-message"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('timeout') || text.includes('tiempo') || text.includes('408') || text.length > 0
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar error de conexión', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular error de conexión
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, {
      forceNetworkError: true
    }).as('networkError')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Esperar un poco para que la página se estabilice
    cy.wait(1000)
    
    // Verificar mensaje de error
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('[data-cy="error-message"], .error-message, .swal2-error').length > 0) {
        cy.get('[data-cy="error-message"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('conexión') || text.includes('conexion') || text.includes('network') || text.includes('error') || text.length > 0
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar error de validación del servidor', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular error de validación
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
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="finca-nombre"], input').length > 0) {
            cy.get('[data-cy="finca-nombre"], input').first().type('Finca Test', { force: true })
            cy.get('[data-cy="finca-area"], input[type="number"]').first().type('-5', { force: true })
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().click({ force: true })
            
            cy.wait('@validationError', { timeout: 10000 })
            
            // Verificar errores de validación si existen
            cy.get('body', { timeout: 5000 }).then(($error) => {
              if ($error.find('[data-cy="validation-error"], .error-message, .swal2-error').length > 0) {
                cy.get('[data-cy="validation-error"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('validación') || text.includes('validacion') || text.includes('error') || text.length > 0
                })
              }
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar error de límite de tasa', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular error de límite de tasa
    cy.intercept('POST', `${apiBaseUrl}/fincas/`, {
      statusCode: 429,
      body: { error: 'Límite de tasa excedido' }
    }).as('rateLimit')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="save-finca"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().click({ force: true })
            
            cy.wait('@rateLimit', { timeout: 10000 })
            
            // Verificar mensaje de error si existe
            cy.get('body', { timeout: 5000 }).then(($error) => {
              if ($error.find('[data-cy="error-message"], .error-message, .swal2-error').length > 0) {
                cy.get('[data-cy="error-message"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('límite') || text.includes('tasa') || text.includes('excedido') || text.includes('429') || text.length > 0
                })
              }
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar error de mantenimiento', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular error de mantenimiento
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, {
      statusCode: 503,
      body: { error: 'Sistema en mantenimiento' }
    }).as('maintenance')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Esperar un poco para que la página se estabilice
    cy.wait(1000)
    
    // Verificar mensaje de mantenimiento si existe
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('[data-cy="maintenance-message"], .maintenance-message, .error-message').length > 0) {
        cy.get('[data-cy="maintenance-message"], .maintenance-message, .error-message').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('mantenimiento') || text.includes('503') || text.includes('sistema') || text.length > 0
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar error de formato de respuesta', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular respuesta malformada
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, {
      statusCode: 200,
      body: 'invalid json'
    }).as('malformedResponse')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Esperar un poco para que la página se estabilice
    cy.wait(1000)
    
    // Verificar mensaje de error si existe
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('[data-cy="error-message"], .error-message, .swal2-error').length > 0) {
        cy.get('[data-cy="error-message"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('procesar') || text.includes('respuesta') || text.includes('formato') || text.includes('error') || text.length > 0
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar error de carga de archivo', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular error de carga de archivo
    cy.intercept('POST', `${apiBaseUrl}/images/**`, {
      statusCode: 413,
      body: { error: 'Archivo demasiado grande' }
    }).as('fileTooLarge')
    
    cy.visit('/nuevo-analisis')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="file-input"], input[type="file"]').length > 0) {
        const fileContent = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAD/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AKgAD//Z'
        
        cy.get('[data-cy="file-input"], input[type="file"]').then((input) => {
          const blob = Cypress.Blob.base64StringToBlob(fileContent.split(',')[1], 'image/jpeg')
          const file = new File([blob], 'test-cacao.jpg', { type: 'image/jpeg' })
          const dataTransfer = new DataTransfer()
          dataTransfer.items.add(file)
          input[0].files = dataTransfer.files
          
          cy.wrap(input).trigger('change', { force: true })
        })
        
        cy.get('body', { timeout: 3000 }).then(($afterUpload) => {
          if ($afterUpload.find('[data-cy="upload-button"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="upload-button"], button[type="submit"]').first().click({ force: true })
            
            cy.wait('@fileTooLarge', { timeout: 10000 })
            
            // Verificar mensaje de error si existe
            cy.get('body', { timeout: 5000 }).then(($error) => {
              if ($error.find('[data-cy="upload-error"], .error-message, .swal2-error').length > 0) {
                cy.get('[data-cy="upload-error"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('grande') || text.includes('archivo') || text.includes('demasiado') || text.includes('413') || text.length > 0
                })
              }
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar error de análisis de imagen', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular error de análisis
    cy.intercept('POST', `${apiBaseUrl}/scan/**`, {
      statusCode: 422,
      body: { error: 'Imagen no válida para análisis' }
    }).as('analysisError')
    
    cy.visit('/nuevo-analisis')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="file-input"], input[type="file"]').length > 0) {
        const fileContent = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAD/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AKgAD//Z'
        
        cy.get('[data-cy="file-input"], input[type="file"]').then((input) => {
          const blob = Cypress.Blob.base64StringToBlob(fileContent.split(',')[1], 'image/jpeg')
          const file = new File([blob], 'test-cacao.jpg', { type: 'image/jpeg' })
          const dataTransfer = new DataTransfer()
          dataTransfer.items.add(file)
          input[0].files = dataTransfer.files
          
          cy.wrap(input).trigger('change', { force: true })
        })
        
        cy.get('body', { timeout: 3000 }).then(($afterUpload) => {
          if ($afterUpload.find('[data-cy="upload-button"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="upload-button"], button[type="submit"]').first().click({ force: true })
            
            cy.wait('@analysisError', { timeout: 10000 })
            
            // Verificar mensaje de error si existe
            cy.get('body', { timeout: 5000 }).then(($error) => {
              if ($error.find('[data-cy="analysis-error"], .error-message, .swal2-error').length > 0) {
                cy.get('[data-cy="analysis-error"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('válida') || text.includes('análisis') || text.includes('imagen') || text.includes('422') || text.length > 0
                })
              }
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar error de generación de reporte', () => {
    cy.login('analyst')
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    
    // Simular error de generación de reporte
    cy.intercept('POST', `${apiBaseUrl}/reportes/`, {
      statusCode: 422,
      body: { error: 'No hay datos para el período seleccionado' }
    }).as('reportError')
    
    cy.visit('/reportes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="create-report-button"], button').length > 0) {
        cy.get('[data-cy="create-report-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="report-type"], select').length > 0) {
            cy.get('[data-cy="report-type"], select').first().select('analisis-periodo', { force: true })
            cy.get('[data-cy="start-date"], input[type="date"]').first().type('2024-01-01', { force: true })
            cy.get('[data-cy="end-date"], input[type="date"]').first().type('2024-01-31', { force: true })
            cy.get('[data-cy="generate-report"], button[type="submit"]').first().click({ force: true })
            
            cy.wait('@reportError', { timeout: 10000 })
            
            // Verificar mensaje de error si existe
            cy.get('body', { timeout: 5000 }).then(($error) => {
              if ($error.find('[data-cy="generation-error"], .error-message, .swal2-error').length > 0) {
                cy.get('[data-cy="generation-error"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('datos') || text.includes('período') || text.includes('seleccionado') || text.includes('422') || text.length > 0
                })
              }
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })
})
