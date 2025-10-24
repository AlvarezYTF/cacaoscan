describe('Manejo de Errores - Errores de Red', () => {
  beforeEach(() => {
    cy.login('farmer')
  })

  it('debe manejar error 500 del servidor', () => {
    // Simular error 500
    cy.intercept('GET', '/api/fincas/', {
      statusCode: 500,
      body: { error: 'Error interno del servidor' }
    }).as('serverError')
    
    cy.visit('/mis-fincas')
    cy.wait('@serverError')
    
    // Verificar mensaje de error
    cy.get('[data-cy="error-message"]')
      .should('be.visible')
      .and('contain', 'Error del servidor')
    
    // Verificar opción de reintentar
    cy.get('[data-cy="retry-button"]').should('be.visible')
    
    // Reintentar
    cy.get('[data-cy="retry-button"]').click()
    cy.wait('@serverError')
  })

  it('debe manejar error 404 - Recurso no encontrado', () => {
    // Simular error 404
    cy.intercept('GET', '/api/fincas/999/', {
      statusCode: 404,
      body: { error: 'Finca no encontrada' }
    }).as('notFound')
    
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Simular acceso a finca inexistente
    cy.visit('/mis-fincas/999')
    cy.wait('@notFound')
    
    // Verificar mensaje de error
    cy.get('[data-cy="error-message"]')
      .should('be.visible')
      .and('contain', 'No encontrado')
  })

  it('debe manejar error 403 - Acceso denegado', () => {
    // Simular error 403
    cy.intercept('GET', '/api/admin/users/', {
      statusCode: 403,
      body: { error: 'Acceso denegado' }
    }).as('forbidden')
    
    cy.visit('/admin/agricultores')
    cy.wait('@forbidden')
    
    // Verificar mensaje de error
    cy.get('[data-cy="error-message"]')
      .should('be.visible')
      .and('contain', 'Acceso denegado')
  })

  it('debe manejar error 401 - No autorizado', () => {
    // Simular error 401
    cy.intercept('GET', '/api/fincas/', {
      statusCode: 401,
      body: { error: 'Token inválido' }
    }).as('unauthorized')
    
    cy.visit('/mis-fincas')
    cy.wait('@unauthorized')
    
    // Verificar redirección al login
    cy.url().should('include', '/login')
    cy.get('[data-cy="session-expired-message"]')
      .should('be.visible')
      .and('contain', 'Sesión expirada')
  })

  it('debe manejar error de timeout', () => {
    // Simular timeout
    cy.intercept('GET', '/api/fincas/', {
      statusCode: 408,
      body: { error: 'Timeout' }
    }).as('timeout')
    
    cy.visit('/mis-fincas')
    cy.wait('@timeout')
    
    // Verificar mensaje de error
    cy.get('[data-cy="error-message"]')
      .should('be.visible')
      .and('contain', 'Timeout')
  })

  it('debe manejar error de conexión', () => {
    // Simular error de conexión
    cy.intercept('GET', '/api/fincas/', {
      forceNetworkError: true
    }).as('networkError')
    
    cy.visit('/mis-fincas')
    cy.wait('@networkError')
    
    // Verificar mensaje de error
    cy.get('[data-cy="error-message"]')
      .should('be.visible')
      .and('contain', 'Error de conexión')
  })

  it('debe manejar error de validación del servidor', () => {
    // Simular error de validación
    cy.intercept('POST', '/api/fincas/', {
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
    cy.get('[data-cy="add-finca-button"]').click()
    
    cy.get('[data-cy="finca-nombre"]').type('Finca Test')
    cy.get('[data-cy="finca-area"]').type('-5')
    cy.get('[data-cy="save-finca"]').click()
    
    cy.wait('@validationError')
    
    // Verificar errores de validación
    cy.get('[data-cy="validation-error"]')
      .should('be.visible')
      .and('contain', 'Error de validación')
  })

  it('debe manejar error de límite de tasa', () => {
    // Simular error de límite de tasa
    cy.intercept('POST', '/api/fincas/', {
      statusCode: 429,
      body: { error: 'Límite de tasa excedido' }
    }).as('rateLimit')
    
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    cy.fixture('testData').then((data) => {
      const fincaData = data.fincas[0]
      cy.fillFincaForm(fincaData)
    })
    
    cy.get('[data-cy="save-finca"]').click()
    cy.wait('@rateLimit')
    
    // Verificar mensaje de error
    cy.get('[data-cy="error-message"]')
      .should('be.visible')
      .and('contain', 'Límite de tasa excedido')
  })

  it('debe manejar error de mantenimiento', () => {
    // Simular error de mantenimiento
    cy.intercept('GET', '/api/fincas/', {
      statusCode: 503,
      body: { error: 'Sistema en mantenimiento' }
    }).as('maintenance')
    
    cy.visit('/mis-fincas')
    cy.wait('@maintenance')
    
    // Verificar mensaje de mantenimiento
    cy.get('[data-cy="maintenance-message"]')
      .should('be.visible')
      .and('contain', 'Sistema en mantenimiento')
  })

  it('debe manejar error de formato de respuesta', () => {
    // Simular respuesta malformada
    cy.intercept('GET', '/api/fincas/', {
      statusCode: 200,
      body: 'invalid json'
    }).as('malformedResponse')
    
    cy.visit('/mis-fincas')
    cy.wait('@malformedResponse')
    
    // Verificar mensaje de error
    cy.get('[data-cy="error-message"]')
      .should('be.visible')
      .and('contain', 'Error al procesar respuesta')
  })

  it('debe manejar error de carga de archivo', () => {
    // Simular error de carga de archivo
    cy.intercept('POST', '/api/images/', {
      statusCode: 413,
      body: { error: 'Archivo demasiado grande' }
    }).as('fileTooLarge')
    
    cy.visit('/nuevo-analisis')
    
    cy.fixture('test-cacao.jpg').then((fileContent) => {
      const blob = new Blob([fileContent], { type: 'image/jpeg' })
      const file = new File([blob], 'test-cacao.jpg', { type: 'image/jpeg' })
      
      cy.get('[data-cy="file-input"]').then((input) => {
        const dataTransfer = new DataTransfer()
        dataTransfer.items.add(file)
        input[0].files = dataTransfer.files
        
        cy.wrap(input).trigger('change', { force: true })
      })
    })
    
    cy.get('[data-cy="upload-button"]').click()
    cy.wait('@fileTooLarge')
    
    // Verificar mensaje de error
    cy.get('[data-cy="upload-error"]')
      .should('be.visible')
      .and('contain', 'Archivo demasiado grande')
  })

  it('debe manejar error de análisis de imagen', () => {
    // Simular error de análisis
    cy.intercept('POST', '/api/scan/measure/', {
      statusCode: 422,
      body: { error: 'Imagen no válida para análisis' }
    }).as('analysisError')
    
    cy.visit('/nuevo-analisis')
    
    cy.fixture('test-cacao.jpg').then((fileContent) => {
      const blob = new Blob([fileContent], { type: 'image/jpeg' })
      const file = new File([blob], 'test-cacao.jpg', { type: 'image/jpeg' })
      
      cy.get('[data-cy="file-input"]').then((input) => {
        const dataTransfer = new DataTransfer()
        dataTransfer.items.add(file)
        input[0].files = dataTransfer.files
        
        cy.wrap(input).trigger('change', { force: true })
      })
    })
    
    cy.get('[data-cy="upload-button"]').click()
    cy.wait('@analysisError')
    
    // Verificar mensaje de error
    cy.get('[data-cy="analysis-error"]')
      .should('be.visible')
      .and('contain', 'Imagen no válida para análisis')
  })

  it('debe manejar error de generación de reporte', () => {
    cy.login('analyst')
    
    // Simular error de generación de reporte
    cy.intercept('POST', '/api/reportes/', {
      statusCode: 422,
      body: { error: 'No hay datos para el período seleccionado' }
    }).as('reportError')
    
    cy.visit('/reportes')
    cy.get('[data-cy="create-report-button"]').click()
    
    cy.get('[data-cy="report-type"]').select('analisis-periodo')
    cy.get('[data-cy="start-date"]').type('2024-01-01')
    cy.get('[data-cy="end-date"]').type('2024-01-31')
    cy.get('[data-cy="generate-report"]').click()
    
    cy.wait('@reportError')
    
    // Verificar mensaje de error
    cy.get('[data-cy="generation-error"]')
      .should('be.visible')
      .and('contain', 'No hay datos para el período seleccionado')
  })
})
