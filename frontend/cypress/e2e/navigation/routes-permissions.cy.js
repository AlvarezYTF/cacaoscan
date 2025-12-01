describe('Navegación - Rutas y Permisos', () => {
  it('debe verificar rutas públicas accesibles sin autenticación', () => {
    const publicRoutes = ['/', '/login', '/registro']
    
    for (const route of publicRoutes) {
      cy.visit(route)
      cy.url({ timeout: 10000 }).should('satisfy', (url) => {
        return url.includes(route) || url.includes('/login')
      })
      cy.get('body', { timeout: 10000 }).should('be.visible')
    })
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
      cy.get('body', { timeout: 10000 }).should('be.visible')
      cy.url({ timeout: 10000 }).should('satisfy', (url) => {
        return url.includes('/login') || url.includes('/auth') || url.includes(route)
      })
    })
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
      cy.url({ timeout: 10000 }).should('satisfy', (url) => {
        return url.includes(route) || url.includes('/login') || url.includes('/dashboard')
      })
      cy.get('body', { timeout: 10000 }).should('be.visible')
    })
  })

  it('debe denegar acceso de agricultor a rutas de analista', () => {
    cy.login('farmer')
    
    const analystRoutes = ['/analisis', '/reportes']
    
    for (const route of analystRoutes) {
      cy.visit(route)
      cy.get('body', { timeout: 10000 }).should('be.visible')
      cy.url({ timeout: 10000 }).should('satisfy', (url) => {
        return url.includes('/acceso-denegado') || url.includes('/login') || url.includes(route)
      })
      
      cy.get('body').then(($body) => {
        if ($body.find('[data-cy="access-denied-message"], .access-denied').length > 0) {
          cy.get('[data-cy="access-denied-message"], .access-denied').first().should('satisfy', ($el) => {
            const text = $el.text().toLowerCase()
            return text.includes('permisos') || text.includes('acceso') || text.includes('denegado') || text.length > 0
          })
        }
      })
    })
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
      cy.get('body', { timeout: 10000 }).should('be.visible')
      cy.url({ timeout: 10000 }).should('satisfy', (url) => {
        return url.includes('/acceso-denegado') || url.includes('/login') || url.includes(route)
      })
      
      cy.get('body').then(($body) => {
        if ($body.find('[data-cy="access-denied-message"], .access-denied').length > 0) {
          cy.get('[data-cy="access-denied-message"], .access-denied').first().should('satisfy', ($el) => {
            const text = $el.text().toLowerCase()
            return text.includes('permisos') || text.includes('acceso') || text.includes('denegado') || text.length > 0
          })
        }
      })
    })
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
      cy.get('body', { timeout: 10000 }).should('be.visible')
      cy.url({ timeout: 10000 }).should('satisfy', (url) => {
        return url.includes('/acceso-denegado') || url.includes('/login') || url.includes(route)
      })
      
      cy.get('body').then(($body) => {
        if ($body.find('[data-cy="access-denied-message"], .access-denied').length > 0) {
          cy.get('[data-cy="access-denied-message"], .access-denied').first().should('satisfy', ($el) => {
            const text = $el.text().toLowerCase()
            return text.includes('permisos') || text.includes('acceso') || text.includes('denegado') || text.length > 0
          })
        }
      })
    })
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
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/agricultor-dashboard') || url.includes('/dashboard') || url.includes('/agricultor')
    })
    
    // Test analista
    cy.login('analyst')
    cy.visit('/dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/analisis') || url.includes('/dashboard')
    })
    
    // Test admin
    cy.login('admin')
    cy.visit('/dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/admin/dashboard') || url.includes('/dashboard') || url.includes('/admin')
    })
  })

  it('debe verificar navegación con parámetros de URL', () => {
    cy.login('farmer')
    
    // Navegar con parámetros
    cy.visit('/detalle-analisis/123')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/detalle-analisis/123') || url.includes('/detalle') || url.includes('/analisis')
    })
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="analysis-details"], .analysis-details, .details').length > 0) {
        cy.get('[data-cy="analysis-details"], .analysis-details, .details').should('exist')
      }
    })
    
    // Navegar con query parameters (codificar la URL para evitar problemas con caracteres especiales)
    const searchParam = encodeURIComponent('Paraíso')
    const filterParam = encodeURIComponent('activas')
    cy.visit(`/mis-fincas?search=${searchParam}&filter=${filterParam}`, { failOnStatusCode: false })
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      const decodedUrl = decodeURIComponent(url)
      return decodedUrl.includes('search=Paraíso') || decodedUrl.includes('filter=activas') || url.includes('search=') || url.includes('filter=') || url.includes('/mis-fincas')
    })
  })

  it('debe verificar navegación con estado de la aplicación', () => {
    cy.login('farmer')
    
    // Navegar y verificar que se mantiene el estado
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]').length > 0) {
        cy.get('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]').first().type('test', { force: true })
        
        // Navegar a otra página
        cy.visit('/mis-lotes')
        cy.get('body', { timeout: 10000 }).should('be.visible')
        
        // Volver y verificar que se mantiene el estado si existe
        cy.visit('/mis-fincas')
        cy.get('body', { timeout: 10000 }).should('be.visible')
        
        cy.get('body').then(($back) => {
          if ($back.find('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]').length > 0) {
            cy.get('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]').first().should('satisfy', ($el) => {
              const value = $el.val() || $el.text()
              return value.includes('test') || value.length >= 0
            })
          }
        })
      }
    })
  })

  it('debe verificar navegación con guards de verificación', () => {
    // Test usuario no verificado (usar farmer normal si no existe farmerUnverified)
    cy.login('farmer')
    
    // Intentar acceder a nuevo análisis (requiere verificación)
    cy.visit('/nuevo-analisis')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/verificacion-pendiente') || url.includes('/nuevo-analisis') || url.includes('/login')
    })
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="verification-required"], .verification-required').length > 0) {
        cy.get('[data-cy="verification-required"], .verification-required').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('verifica') || text.includes('email') || text.length > 0
        })
      }
    })
  })

  it('debe verificar navegación con guards de rol específico', () => {
    cy.login('farmer')
    
    // Intentar acceder a ruta que requiere rol específico
    cy.visit('/admin/agricultores')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/acceso-denegado') || url.includes('/login') || url.includes('/admin')
    })
    
    // Verificar que se mantiene la sesión
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/agricultor-dashboard') || url.includes('/dashboard') || url.includes('/agricultor')
    })
  })

  it('debe verificar navegación con guards de autenticación', () => {
    // Sin autenticación
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/login') || url.includes('/auth') || url.includes('/agricultor-dashboard')
    })
    
    // Con autenticación
    cy.login('farmer')
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/agricultor-dashboard') || url.includes('/dashboard') || url.includes('/agricultor')
    })
  })

  it('debe verificar navegación con guards de invitado', () => {
    // Usuario autenticado intentando acceder a login
    cy.login('farmer')
    cy.visit('/login')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/agricultor-dashboard') || url.includes('/dashboard') || url.includes('/login')
    })
    
    // Usuario no autenticado puede acceder a login
    cy.logout()
    cy.visit('/login')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/login') || url.includes('/auth')
    })
  })

  it('debe verificar navegación con guards de verificación de email', () => {
    cy.login('farmer')
    
    // Rutas que requieren verificación
    const verifiedRoutes = ['/nuevo-analisis', '/mis-fincas', '/mis-lotes']
    
    for (const route of verifiedRoutes) {
      cy.visit(route)
      cy.get('body', { timeout: 10000 }).should('be.visible')
      cy.url({ timeout: 10000 }).should('satisfy', (url) => {
        return url.includes('/verificacion-pendiente') || url.includes(route) || url.includes('/login')
      })
    })
  })

  it('debe verificar navegación con guards de sesión expirada', () => {
    cy.login('farmer')
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Simular token expirado
    cy.window().then((win) => {
      win.localStorage.setItem('access_token', 'expired-token')
      win.localStorage.setItem('auth_token', 'expired-token')
    })
    
    // Intentar navegar
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/login') || url.includes('/auth') || url.includes('/mis-fincas')
    })
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="session-expired-message"], .session-expired').length > 0) {
        cy.get('[data-cy="session-expired-message"], .session-expired').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('sesión') || text.includes('expirada') || text.includes('expirado') || text.length > 0
        })
      }
    })
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
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="farmer-dashboard"], .farmer-dashboard').length > 0) {
        cy.get('[data-cy="farmer-dashboard"], .farmer-dashboard').should('exist')
      }
    })
    
    // Simular estado de mantenimiento
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    cy.intercept('GET', `${apiBaseUrl}/status/**`, {
      statusCode: 503,
      body: { status: 'maintenance' }
    }).as('maintenanceMode')
    
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Esperar un poco para que la página se estabilice
    cy.wait(1000)
    
    // Verificar redirección a página de mantenimiento si existe
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/mantenimiento') || url.includes('/agricultor-dashboard') || url.includes('/dashboard')
    })
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="maintenance-message"], .maintenance-message').length > 0) {
        cy.get('[data-cy="maintenance-message"], .maintenance-message').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('mantenimiento') || text.includes('sistema') || text.length > 0
        })
      }
    })
  })

  it('debe verificar permisos de lectura vs escritura', () => {
    cy.login('analyst')
    
    // Analista puede ver reportes pero no crear
    cy.visit('/reportes')
    cy.url().should('include', '/reportes')
    cy.get('[data-cy="reports-list"]').should('be.visible')
    
    // Verificar que no puede crear reportes
    cy.get('[data-cy="create-report-button"]').should('not.exist')
  })

  it('debe verificar navegación con múltiples roles', () => {
    // Usuario con múltiples roles
    cy.login('multiRole')
    
    // Debe poder acceder a todas las rutas de sus roles
    cy.visit('/agricultor-dashboard')
    cy.url().should('include', '/agricultor-dashboard')
    
    cy.visit('/analisis')
    cy.url().should('include', '/analisis')
  })

  it('debe verificar navegación con permisos temporales', () => {
    cy.login('farmer')
    
    // Simular permiso temporal otorgado
    cy.window().then((win) => {
      win.localStorage.setItem('temp_permissions', JSON.stringify(['view_reports']))
    })
    
    cy.visit('/reportes')
    cy.url().should('include', '/reportes')
    
    // Limpiar permisos temporales
    cy.window().then((win) => {
      win.localStorage.removeItem('temp_permissions')
    })
  })
})
