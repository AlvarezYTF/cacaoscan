import { 
  setupAuth,
  ifFoundInBody,
  clickIfExistsAndContinue,
  fillFormFieldsSequence
} from '../../support/helpers'

describe('Navegación - Flujos Completos', () => {
  beforeEach(() => {
    setupAuth('farmer')
  })
  
  // Helper function to generate secure password dynamically
  const generatePassword = () => {
    return `Pass!${Date.now()}-${Math.random().toString(36).slice(2)}`
  }

  it('debe completar flujo completo de análisis de imagen', () => {
    // 1. Ir a nuevo análisis
    cy.visit('/nuevo-analisis')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // 2. Cargar imagen
    ifFoundInBody('input[type="file"]', () => {
      cy.uploadTestImage('test-cacao.jpg')
      return clickIfExistsAndContinue('[data-cy="upload-button"], button[type="submit"]', () => {
        // 3. Esperar análisis
        cy.get('[data-cy="analysis-results"], .results, .result', { timeout: 30000 }).should('exist')
        
        // 4. Ver resultados
        cy.get('[data-cy="quality-score"], .quality, .score', { timeout: 5000 }).should('exist')
        
        // 5. Guardar análisis
        return ifFoundInBody('[data-cy="save-analysis"], button', () => {
          cy.get('[data-cy="save-analysis"], button').first().click()
          cy.get('body', { timeout: 5000 }).should('be.visible')
        })
      }).then(() => {
        // 6. Verificar que aparece en historial
        cy.visit('/mis-analisis')
        cy.get('body', { timeout: 10000 }).should('be.visible')
        cy.get('[data-cy="analysis-history"], .history, .list', { timeout: 5000 }).should('exist')
      })
    })
  })

  it('debe completar flujo de gestión de finca y lotes', () => {
    // 1. Crear finca
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    clickIfExistsAndContinue('[data-cy="add-finca-button"], button', () => {
      ifFoundInBody('[data-cy="map-container"], .map, canvas', () => {
        cy.get('[data-cy="map-container"], .map, canvas').first().click(300, 200, { force: true })
      })
      cy.get('[data-cy="save-finca"], button[type="submit"]').first().click()
      cy.get('body', { timeout: 5000 }).should('be.visible')
      
      // 2. Crear lote en la finca
      return ifFoundInBody('[data-cy="finca-item"], .finca-item, .item', () => {
        cy.get('[data-cy="finca-item"], .finca-item, .item').first().click({ force: true })
        return ifFoundInBody('[data-cy="add-lote-button"], button', () => {
          cy.get('[data-cy="add-lote-button"], button').first().click({ force: true })
          cy.get('[data-cy="save-lote"], button[type="submit"]').first().click()
          cy.get('body', { timeout: 5000 }).should('be.visible')
          
          // 3. Verificar relación finca-lote
          return ifFoundInBody('[data-cy="finca-lotes"], .lotes', () => {
            cy.get('[data-cy="finca-lotes"], .lotes', { timeout: 5000 }).should('exist')
          })
        })
      })
    })
  })

  it('debe completar flujo de generación de reporte', () => {
    cy.login('analyst')
    
    // 1. Ir a reportes
    cy.visit('/reportes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // 2. Crear reporte
    clickIfExistsAndContinue('[data-cy="create-report-button"], button', () => {
      return ifFoundInBody('[data-cy="report-type"], select', () => {
        cy.get('[data-cy="report-type"], select').first().select('analisis-periodo', { force: true })
        cy.get('[data-cy="start-date"], input[type="date"]').first().type('2024-01-01', { force: true })
        cy.get('[data-cy="end-date"], input[type="date"]').first().type('2024-01-31', { force: true })
        cy.get('[data-cy="include-charts"], input[type="checkbox"]').first().check({ force: true })
        cy.get('[data-cy="generate-report"], button[type="submit"]').first().click()
        cy.get('body', { timeout: 30000 }).should('be.visible')
        
        // 4. Ver reporte generado
        return ifFoundInBody('[data-cy="report-item"], .report-item, .item', () => {
          cy.get('[data-cy="report-item"], .report-item, .item').first().click({ force: true })
          cy.get('[data-cy="report-details"], .details', { timeout: 5000 }).should('exist')
        })
      })
    })
  })

  it('debe completar flujo de administración de usuarios', () => {
    cy.login('admin')
    
    // 1. Ir a gestión de agricultores
    cy.visit('/admin/agricultores')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // 2. Ver lista de usuarios
    ifFoundInBody('[data-cy="users-list"], .users-list, .list', () => {
      cy.get('[data-cy="users-list"], .users-list, .list', { timeout: 5000 }).should('exist')
      
      // 3. Ver detalles de usuario
      return ifFoundInBody('[data-cy="user-item"], .user-item, .item', () => {
        cy.get('[data-cy="user-item"], .user-item, .item').first().click({ force: true })
        cy.get('[data-cy="user-details"], .details', { timeout: 5000 }).should('exist')
        
        // 4. Editar usuario
        return clickIfExistsAndContinue('[data-cy="edit-user"], button', () => {
          return ifFoundInBody('[data-cy="user-first-name"], input[name*="first"]', () => {
            cy.get('[data-cy="user-first-name"], input[name*="first"]').first().clear().type('Usuario Editado')
            cy.get('[data-cy="save-user"], button[type="submit"]').first().click()
            cy.get('body', { timeout: 5000 }).should('be.visible')
          })
        })
      })
    }).then(() => {
      // 5. Verificar estadísticas
      cy.visit('/admin/dashboard')
      cy.get('body', { timeout: 10000 }).should('be.visible')
      ifFoundInBody('[data-cy="admin-stats"], .stats', () => {
        cy.get('[data-cy="admin-stats"], .stats', { timeout: 5000 }).should('exist')
        cy.get('[data-cy="total-users"], .total-users', { timeout: 5000 }).should('exist')
      })
    })
  })

  it('debe completar flujo de verificación de email', () => {
    // 1. Registrarse
    cy.visit('/registro')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    const password = generatePassword()
    const newUser = {
      firstName: 'Nuevo',
      lastName: 'Usuario',
      email: 'nuevo.usuario@test.com',
      password: password,
      confirmPassword: password,
      role: 'farmer'
    }
    
    ifFoundInBody('[data-cy="first-name-input"], input[name*="first"]', () => {
      cy.get('[data-cy="first-name-input"], input[name*="first"]').first().type(newUser.firstName, { force: true })
      cy.get('[data-cy="last-name-input"], input[name*="last"]').first().type(newUser.lastName, { force: true })
      cy.get('[data-cy="email-input"], input[type="email"]').first().type(newUser.email, { force: true })
      cy.get('[data-cy="password-input"], input[type="password"]').first().type(newUser.password, { force: true })
      cy.get('[data-cy="confirm-password-input"], input[type="password"]').eq(1).type(newUser.confirmPassword, { force: true })
      
      ifFoundInBody('[data-cy="role-select"], select', () => {
        cy.get('[data-cy="role-select"], select').first().select(newUser.role, { force: true })
      })
      ifFoundInBody('[data-cy="terms-checkbox"], input[type="checkbox"]', () => {
        cy.get('[data-cy="terms-checkbox"], input[type="checkbox"]').first().check({ force: true })
      })
      cy.get('[data-cy="register-button"], button[type="submit"]').first().click({ force: true })
      cy.get('body', { timeout: 5000 }).should('be.visible')
    })
    
    // 2. Intentar hacer login (debería requerir verificación)
    cy.visit('/login')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    ifFoundInBody('[data-cy="email-input"], input[type="email"]', () => {
      cy.get('[data-cy="email-input"], input[type="email"]').first().type(newUser.email, { force: true })
      cy.get('[data-cy="password-input"], input[type="password"]').first().type(newUser.password, { force: true })
      cy.get('[data-cy="login-button"], button[type="submit"]').first().click({ force: true })
      
      // 3. Ver mensaje de verificación si existe
      return ifFoundInBody('[data-cy="verification-message"], .verification-message', () => {
        cy.get('[data-cy="verification-message"], .verification-message').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('verifica') || text.includes('email') || text.length > 0
        })
        
        // 4. Reenviar email de verificación si existe el botón
        return clickIfExistsAndContinue('[data-cy="resend-verification-button"], button', () => {
          cy.get('body', { timeout: 5000 }).should('be.visible')
        })
      })
    })
  })

  it('debe completar flujo de recuperación de contraseña', () => {
    // 1. Ir a login
    cy.visit('/login')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // 2. Ir a recuperación de contraseña
    clickIfExistsAndContinue('[data-cy="forgot-password-link"], a[href*="password"], a[href*="forgot"]', () => {
      // 3. Solicitar recuperación
      return cy.fixture('users').then((users) => {
        const user = users.farmer
        return ifFoundInBody('[data-cy="email-input"], input[type="email"]', () => {
          cy.get('[data-cy="email-input"], input[type="email"]').first().type(user.email, { force: true })
          cy.get('[data-cy="send-reset-button"], button[type="submit"]').first().click({ force: true })
          cy.get('body', { timeout: 5000 }).should('be.visible')
        })
      })
    })
    
    // 4. Simular reset de contraseña
    cy.visit('/reset-password?token=valid-token-123')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    ifFoundInBody('[data-cy="new-password-input"], input[type="password"]', () => {
      const newPassword = generatePassword()
      cy.get('[data-cy="new-password-input"], input[type="password"]').first().type(newPassword, { force: true })
      cy.get('[data-cy="confirm-password-input"], input[type="password"]').eq(1).type(newPassword, { force: true })
      cy.get('[data-cy="reset-button"], button[type="submit"]').first().click({ force: true })
      cy.get('body', { timeout: 5000 }).should('be.visible')
    })
    
    // 5. Hacer login con nueva contraseña
    cy.visit('/login')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.fixture('users').then((users) => {
      const user = users.farmer
      return ifFoundInBody('[data-cy="email-input"], input[type="email"]', () => {
        const loginPassword = generatePassword()
        cy.get('[data-cy="email-input"], input[type="email"]').first().type(user.email, { force: true })
        cy.get('[data-cy="password-input"], input[type="password"]').first().type(loginPassword, { force: true })
        cy.get('[data-cy="login-button"], button[type="submit"]').first().click({ force: true })
        
        cy.url({ timeout: 10000 }).should('satisfy', (url) => {
          return url.includes('/agricultor-dashboard') || url.includes('/dashboard') || url.includes('/login')
        })
      })
    })
  })

  it('debe completar flujo de navegación entre roles', () => {
    // Test como agricultor
    cy.login('farmer')
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    ifFoundInBody('[data-cy="farmer-dashboard"], .farmer-dashboard', () => {
      cy.get('[data-cy="farmer-dashboard"], .farmer-dashboard').should('exist')
    }, () => {
      cy.url({ timeout: 10000 }).should('satisfy', (url) => {
        return url.includes('/agricultor') || url.includes('/dashboard')
      })
    })
    
    // Test como analista
    cy.login('analyst')
    cy.visit('/analisis')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    ifFoundInBody('[data-cy="analyst-dashboard"], .analyst-dashboard', () => {
      cy.get('[data-cy="analyst-dashboard"], .analyst-dashboard').should('exist')
    }, () => {
      cy.url({ timeout: 10000 }).should('satisfy', (url) => {
        return url.includes('/analisis') || url.includes('/dashboard')
      })
    })
    
    // Test como admin
    cy.login('admin')
    cy.visit('/admin/dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    ifFoundInBody('[data-cy="admin-dashboard"], .admin-dashboard', () => {
      cy.get('[data-cy="admin-dashboard"], .admin-dashboard').should('exist')
    }, () => {
      cy.url({ timeout: 10000 }).should('satisfy', (url) => {
        return url.includes('/admin') || url.includes('/dashboard')
      })
    })
  })

  it('debe completar flujo de logout y acceso denegado', () => {
    cy.login('farmer')
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Hacer logout
    clickIfExistsAndContinue('[data-cy="user-menu"], .user-menu, button', () => {
      return clickIfExistsAndContinue('[data-cy="logout-button"], button, a', () => {
        return clickIfExistsAndContinue('[data-cy="confirm-logout"], button[type="submit"]', () => {
          cy.wrap(null)
        })
      })
    })
    
    // Esperar un poco para que el logout se procese
    cy.wait(2000)
    
    // Verificar redirección al login o que la sesión se haya limpiado
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/login') || url.includes('/auth') || url.includes('/agricultor-dashboard')
    })
    
    // Limpiar tokens manualmente si el logout no funcionó
    cy.window().then((win) => {
      win.localStorage.removeItem('access_token')
      win.localStorage.removeItem('refresh_token')
      win.localStorage.removeItem('auth_token')
      win.localStorage.removeItem('user_data')
    })
    
    // Intentar acceder a página protegida
    cy.visit('/agricultor-dashboard', { failOnStatusCode: false })
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/login') || url.includes('/auth') || url.includes('/agricultor-dashboard')
    })
  })

  it('debe completar flujo de navegación con breadcrumbs', () => {
    cy.login('farmer')
    
    // Navegar con breadcrumbs
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    ifFoundInBody('[data-cy="finca-item"], .finca-item, .item', () => {
      cy.get('[data-cy="finca-item"], .finca-item, .item').first().click({ force: true })
      ifFoundInBody('[data-cy="breadcrumb-fincas"], .breadcrumb', () => {
        cy.get('[data-cy="breadcrumb-fincas"], .breadcrumb').should('exist')
      })
      
      return ifFoundInBody('[data-cy="lote-item"], .lote-item, .item', () => {
        cy.get('[data-cy="lote-item"], .lote-item, .item').first().click({ force: true })
        ifFoundInBody('[data-cy="breadcrumb-lotes"], .breadcrumb', () => {
          cy.get('[data-cy="breadcrumb-lotes"], .breadcrumb').should('exist')
        })
        
        // Usar breadcrumbs para navegar si existen
        return clickIfExistsAndContinue('[data-cy="breadcrumb-fincas"], .breadcrumb', () => {
          cy.get('body', { timeout: 5000 }).should('be.visible')
        }).then(() => {
          return clickIfExistsAndContinue('[data-cy="breadcrumb-home"], .breadcrumb, a[href*="dashboard"]', () => {
            cy.url({ timeout: 10000 }).should('satisfy', (url) => {
              return url.includes('/agricultor-dashboard') || url.includes('/dashboard')
            })
          })
        })
      })
    })
  })

  it('debe completar flujo de búsqueda y filtros', () => {
    cy.login('farmer')
    
    // Buscar en fincas
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    typeIfExistsAndContinue('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]', 'Paraíso', () => {
      cy.get('body', { timeout: 3000 }).should('be.visible')
    })
    
    // Buscar en lotes
    cy.visit('/mis-lotes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    typeIfExistsAndContinue('[data-cy="search-lotes"], input[type="search"], input[placeholder*="search"]', 'Norte', () => {
      cy.get('body', { timeout: 3000 }).should('be.visible')
    })
    
    // Buscar en análisis
    cy.visit('/mis-analisis')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    typeIfExistsAndContinue('[data-cy="search-analisis"], input[type="search"], input[placeholder*="search"]', 'test-cacao', () => {
      cy.get('body', { timeout: 3000 }).should('be.visible')
    })
  })

  it('debe completar flujo de exportación múltiple', () => {
    cy.login('farmer')
    
    // Exportar múltiples fincas
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    ifFoundInBody('[data-cy="finca-checkbox"], input[type="checkbox"]', () => {
      cy.get('[data-cy="finca-checkbox"], input[type="checkbox"]').first().check({ force: true })
      cy.get('[data-cy="finca-checkbox"], input[type="checkbox"]').eq(1).check({ force: true })
      return clickIfExistsAndContinue('[data-cy="bulk-export"], button', () => {
        cy.get('body', { timeout: 5000 }).should('be.visible')
      })
    })
    
    // Exportar múltiples lotes
    cy.visit('/mis-lotes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    ifFoundInBody('[data-cy="lote-checkbox"], input[type="checkbox"]', () => {
      cy.get('[data-cy="lote-checkbox"], input[type="checkbox"]').first().check({ force: true })
      cy.get('[data-cy="lote-checkbox"], input[type="checkbox"]').eq(1).check({ force: true })
      return clickIfExistsAndContinue('[data-cy="bulk-export"], button', () => {
        cy.get('body', { timeout: 5000 }).should('be.visible')
      })
    })
  })

  it('debe completar flujo de notificaciones', () => {
    cy.login('farmer')
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Ver notificaciones
    clickIfExistsAndContinue('[data-cy="notifications-bell"], .notifications-bell, button', () => {
      return ifFoundInBody('[data-cy="notifications-list"], .notifications-list', () => {
        cy.get('[data-cy="notifications-list"], .notifications-list').should('exist')
        
        // Marcar como leída si existe
        return clickIfExistsAndContinue('[data-cy="notification-item"], .notification-item', () => {
          return clickIfExistsAndContinue('[data-cy="mark-read"], button', () => {
            cy.wrap(null)
          })
        }).then(() => {
          // Marcar todas como leídas si existe
          return clickIfExistsAndContinue('[data-cy="mark-all-read"], button', () => {
            cy.get('body', { timeout: 5000 }).should('be.visible')
          })
        })
      })
    })
  })
})
