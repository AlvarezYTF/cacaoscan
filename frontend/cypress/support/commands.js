// ***********************************************
// Comandos personalizados para CacaoScan E2E Tests
// ***********************************************

// Comando para login con diferentes roles
Cypress.Commands.add('login', (userType = 'admin') => {
  cy.fixture('users').then((users) => {
    const user = users[userType]
    cy.session([userType], () => {
      cy.request({
        method: 'POST',
        url: '/api/auth/login/',
        body: {
          email: user.email,
          password: user.password
        }
      }).then((response) => {
        expect(response.status).to.eq(200)
        window.localStorage.setItem('auth_token', response.body.access)
        window.localStorage.setItem('refresh_token', response.body.refresh)
        window.localStorage.setItem('user_data', JSON.stringify(response.body.user))
      })
    })
  })
})

// Comando para logout
Cypress.Commands.add('logout', () => {
  cy.window().then((win) => {
    win.localStorage.removeItem('auth_token')
    win.localStorage.removeItem('refresh_token')
    win.localStorage.removeItem('user_data')
  })
})

// Comando para navegar con autenticación
Cypress.Commands.add('visitWithAuth', (url, userType = 'admin') => {
  cy.login(userType)
  cy.visit(url)
})

// Comando para subir imagen de prueba
Cypress.Commands.add('uploadTestImage', (filename = 'test-cacao.jpg') => {
  cy.fixture(filename).then((fileContent) => {
    const blob = new Blob([fileContent], { type: 'image/jpeg' })
    const file = new File([blob], filename, { type: 'image/jpeg' })
    
    cy.get('input[type="file"]').then((input) => {
      const dataTransfer = new DataTransfer()
      dataTransfer.items.add(file)
      input[0].files = dataTransfer.files
      
      cy.wrap(input).trigger('change', { force: true })
    })
  })
})

// Comando para esperar que termine el análisis
Cypress.Commands.add('waitForAnalysis', (timeout = 30000) => {
  cy.get('[data-cy="analysis-status"]', { timeout })
    .should('contain', 'Completado')
})

// Comando para verificar notificaciones
Cypress.Commands.add('checkNotification', (message, type = 'success') => {
  cy.get(`[data-cy="notification-${type}"]`)
    .should('be.visible')
    .and('contain', message)
})

// Comando para llenar formulario de finca
Cypress.Commands.add('fillFincaForm', (fincaData) => {
  cy.get('[data-cy="finca-nombre"]').type(fincaData.nombre)
  cy.get('[data-cy="finca-ubicacion"]').type(fincaData.ubicacion)
  cy.get('[data-cy="finca-area"]').type(fincaData.area_total.toString())
  cy.get('[data-cy="finca-descripcion"]').type(fincaData.descripcion)
})

// Comando para llenar formulario de lote
Cypress.Commands.add('fillLoteForm', (loteData) => {
  cy.get('[data-cy="lote-nombre"]').type(loteData.nombre)
  cy.get('[data-cy="lote-area"]').type(loteData.area.toString())
  cy.get('[data-cy="lote-variedad"]').select(loteData.variedad)
  cy.get('[data-cy="lote-edad"]').type(loteData.edad_plantas.toString())
  cy.get('[data-cy="lote-descripcion"]').type(loteData.descripcion)
})

// Comando para simular respuesta de API
Cypress.Commands.add('mockApiResponse', (method, url, response, statusCode = 200) => {
  cy.intercept(method, url, {
    statusCode,
    body: response
  }).as('mockApi')
})

// Comando para verificar elementos de navegación según rol
Cypress.Commands.add('checkNavigationForRole', (role) => {
  const expectedRoutes = {
    admin: ['/admin/dashboard', '/admin/agricultores', '/admin/configuracion'],
    analyst: ['/analisis', '/reportes'],
    farmer: ['/agricultor-dashboard', '/nuevo-analisis', '/mis-fincas']
  }
  
  expectedRoutes[role].forEach(route => {
    cy.get(`[href="${route}"]`).should('be.visible')
  })
})

// Comando para verificar que no se puede acceder a rutas sin permisos
Cypress.Commands.add('checkAccessDenied', (url) => {
  cy.visit(url)
  cy.url().should('include', '/acceso-denegado')
  cy.get('[data-cy="access-denied-message"]')
    .should('be.visible')
    .and('contain', 'No tienes permisos')
})

// Comando para esperar carga de datos
Cypress.Commands.add('waitForDataLoad', (selector = '[data-cy="data-loaded"]') => {
  cy.get(selector, { timeout: 10000 }).should('be.visible')
})

// Comando para limpiar datos de prueba
Cypress.Commands.add('cleanupTestData', () => {
  cy.request({
    method: 'DELETE',
    url: '/api/test/cleanup/',
    headers: {
      'Authorization': `Bearer ${window.localStorage.getItem('auth_token')}`
    }
  })
})
