describe('Navegación - Rutas y Permisos', () => {
  it('debe verificar rutas públicas accesibles sin autenticación', () => {
    const publicRoutes = ['/', '/login', '/registro']
    
    for (const route of publicRoutes) {
      cy.visit(route)
      cy.url().should('include', route)
      cy.get('body').should('be.visible')
    }
  })

  it('debe redirigir a login desde rutas protegidas sin autenticación', () => {
    const protectedRoutes = [
      '/agricultor-dashboard',
      '/analisis',
      '/admin/dashboard',
      '/mis-fincas',
      '/mis-lotes',
      '/nuevo-analisis'
    ]
    
    for (const route of protectedRoutes) {
      cy.visit(route)
      cy.url().should('include', '/login')
    }
  })

  it('debe verificar acceso de agricultor a sus rutas permitidas', () => {
    cy.login('farmer')
    
    const farmerRoutes = [
      '/agricultor-dashboard',
      '/mis-fincas',
      '/mis-lotes',
      '/nuevo-analisis',
      '/mis-analisis',
      '/mi-perfil'
    ]
    
    for (const route of farmerRoutes) {
      cy.visit(route)
      cy.url().should('include', route)
      cy.get('body').should('be.visible')
    }
  })

  it('debe denegar acceso de agricultor a rutas de analista', () => {
    cy.login('farmer')
    
    const analystRoutes = ['/analisis', '/reportes']
    
    for (const route of analystRoutes) {
      cy.visit(route)
      cy.url().should('include', '/acceso-denegado')
      cy.get('[data-cy="access-denied-message"]')
        .should('be.visible')
        .and('contain', 'No tienes permisos')
    }
  })

  it('debe denegar acceso de agricultor a rutas de admin', () => {
    cy.login('farmer')
    
    const adminRoutes = [
      '/admin/dashboard',
      '/admin/agricultores',
      '/admin/configuracion',
      '/admin/dataset',
      '/admin/training'
    ]
    
    for (const route of adminRoutes) {
      cy.visit(route)
      cy.url().should('include', '/acceso-denegado')
      cy.get('[data-cy="access-denied-message"]')
        .should('be.visible')
        .and('contain', 'No tienes permisos')
    }
  })

  it('debe verificar acceso de analista a sus rutas permitidas', () => {
    cy.login('analyst')
    
    const analystRoutes = [
      '/analisis',
      '/reportes',
      '/mi-perfil'
    ]
    
    for (const route of analystRoutes) {
      cy.visit(route)
      cy.url().should('include', route)
      cy.get('body').should('be.visible')
    }
  })

  it('debe denegar acceso de analista a rutas de agricultor', () => {
    cy.login('analyst')
    
    const farmerRoutes = [
      '/agricultor-dashboard',
      '/mis-fincas',
      '/mis-lotes',
      '/nuevo-analisis'
    ]
    
    for (const route of farmerRoutes) {
      cy.visit(route)
      cy.url().should('include', '/acceso-denegado')
      cy.get('[data-cy="access-denied-message"]')
        .should('be.visible')
        .and('contain', 'No tienes permisos')
    }
  })

  it('debe verificar acceso de admin a todas las rutas', () => {
    cy.login('admin')
    
    const allRoutes = [
      '/admin/dashboard',
      '/admin/agricultores',
      '/admin/configuracion',
      '/admin/dataset',
      '/admin/training',
      '/analisis',
      '/reportes',
      '/mi-perfil'
    ]
    
    for (const route of allRoutes) {
      cy.visit(route)
      cy.url().should('include', route)
      cy.get('body').should('be.visible')
    }
  })

  it('debe verificar redirección automática según rol', () => {
    // Test agricultor
    cy.login('farmer')
    cy.visit('/dashboard')
    cy.url().should('include', '/agricultor-dashboard')
    
    // Test analista
    cy.login('analyst')
    cy.visit('/dashboard')
    cy.url().should('include', '/analisis')
    
    // Test admin
    cy.login('admin')
    cy.visit('/dashboard')
    cy.url().should('include', '/admin/dashboard')
  })

  it('debe verificar navegación con parámetros de URL', () => {
    cy.login('farmer')
    
    // Navegar con parámetros
    cy.visit('/detalle-analisis/123')
    cy.url().should('include', '/detalle-analisis/123')
    cy.get('[data-cy="analysis-details"]').should('be.visible')
    
    // Navegar con query parameters
    cy.visit('/mis-fincas?search=Paraíso&filter=activas')
    cy.url().should('include', 'search=Paraíso')
    cy.url().should('include', 'filter=activas')
  })

  it('debe verificar navegación con estado de la aplicación', () => {
    cy.login('farmer')
    
    // Navegar y verificar que se mantiene el estado
    cy.visit('/mis-fincas')
    cy.get('[data-cy="search-fincas"]').type('test')
    
    // Navegar a otra página
    cy.visit('/mis-lotes')
    
    // Volver y verificar que se mantiene el estado
    cy.visit('/mis-fincas')
    cy.get('[data-cy="search-fincas"]').should('have.value', 'test')
  })

  it('debe verificar navegación con guards de verificación', () => {
    // Test usuario no verificado
    cy.login('farmerUnverified')
    
    // Intentar acceder a nuevo análisis (requiere verificación)
    cy.visit('/nuevo-analisis')
    cy.url().should('include', '/verificacion-pendiente')
    cy.get('[data-cy="verification-required"]')
      .should('be.visible')
      .and('contain', 'Verifica tu email')
  })

  it('debe verificar navegación con guards de rol específico', () => {
    cy.login('farmer')
    
    // Intentar acceder a ruta que requiere rol específico
    cy.visit('/admin/agricultores')
    cy.url().should('include', '/acceso-denegado')
    
    // Verificar que se mantiene la sesión
    cy.visit('/agricultor-dashboard')
    cy.url().should('include', '/agricultor-dashboard')
  })

  it('debe verificar navegación con guards de autenticación', () => {
    // Sin autenticación
    cy.visit('/agricultor-dashboard')
    cy.url().should('include', '/login')
    
    // Con autenticación
    cy.login('farmer')
    cy.visit('/agricultor-dashboard')
    cy.url().should('include', '/agricultor-dashboard')
  })

  it('debe verificar navegación con guards de invitado', () => {
    // Usuario autenticado intentando acceder a login
    cy.login('farmer')
    cy.visit('/login')
    cy.url().should('include', '/agricultor-dashboard')
    
    // Usuario no autenticado puede acceder a login
    cy.logout()
    cy.visit('/login')
    cy.url().should('include', '/login')
  })

  it('debe verificar navegación con guards de verificación de email', () => {
    cy.login('farmerUnverified')
    
    // Rutas que requieren verificación
    const verifiedRoutes = ['/nuevo-analisis', '/mis-fincas', '/mis-lotes']
    
    for (const route of verifiedRoutes) {
      cy.visit(route)
      cy.url().should('include', '/verificacion-pendiente')
    }
  })

  it('debe verificar navegación con guards de sesión expirada', () => {
    cy.login('farmer')
    cy.visit('/agricultor-dashboard')
    
    // Simular token expirado
    cy.window().then((win) => {
      win.localStorage.setItem('auth_token', 'expired-token')
    })
    
    // Intentar navegar
    cy.visit('/mis-fincas')
    cy.url().should('include', '/login')
    cy.get('[data-cy="session-expired-message"]')
      .should('be.visible')
      .and('contain', 'Sesión expirada')
  })

  it('debe verificar navegación con guards de permisos granulares', () => {
    cy.login('admin')
    
    // Admin puede acceder a todas las rutas
    cy.visit('/admin/agricultores')
    cy.url().should('include', '/admin/agricultores')
    
    cy.visit('/analisis')
    cy.url().should('include', '/analisis')
    
    cy.visit('/reportes')
    cy.url().should('include', '/reportes')
  })

  it('debe verificar navegación con guards de estado de la aplicación', () => {
    cy.login('farmer')
    
    // Verificar que se puede navegar normalmente
    cy.visit('/agricultor-dashboard')
    cy.get('[data-cy="farmer-dashboard"]').should('be.visible')
    
    // Simular estado de mantenimiento
    cy.intercept('GET', '/api/status/', {
      statusCode: 503,
      body: { status: 'maintenance' }
    }).as('maintenanceMode')
    
    cy.visit('/agricultor-dashboard')
    cy.wait('@maintenanceMode')
    
    // Verificar redirección a página de mantenimiento
    cy.url().should('include', '/mantenimiento')
    cy.get('[data-cy="maintenance-message"]')
      .should('be.visible')
      .and('contain', 'Sistema en mantenimiento')
  })
})
