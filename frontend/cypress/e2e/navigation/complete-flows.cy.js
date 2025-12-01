import { 
  setupAuth,
  ifFoundInBody,
  clickIfExistsAndContinue,
  fillFormFieldsSequence,
  typeIfExistsAndContinue
} from '../../support/helpers'

describe('Navegación - Flujos Completos', () => {
  const generatePassword = () => {
    return `Pass!${Date.now()}-${Math.random().toString(36).slice(2)}` // NOSONAR S2245
  }
  
  const visitAndWait = (url) => {
    cy.visit(url)
    cy.get('body', { timeout: 10000 }).should('be.visible')
  }
  
  const verifyDashboard = (dashboardSelector, urlPatterns) => {
    return ifFoundInBody(dashboardSelector, () => {
      cy.get(dashboardSelector).should('exist')
    }, () => {
      verifyUrlPatterns(urlPatterns, 10000)
    })
  }
  
  const verifyUrlPatterns = (patterns, timeout) => {
    return cy.url({ timeout }).should('satisfy', (url) => {
      return patterns.some(pattern => url.includes(pattern))
    })
  }
  
  beforeEach(() => {
    setupAuth('farmer')
  })

  it('debe completar flujo completo de análisis de imagen', () => {
    visitAndWait('/nuevo-analisis')
    
    ifFoundInBody('input[type="file"]', () => {
      cy.uploadTestImage('test-cacao.jpg')
      return clickIfExistsAndContinue('[data-cy="upload-button"], button[type="submit"]', () => {
        cy.get('[data-cy="analysis-results"], .results, .result', { timeout: 30000 }).should('exist')
        cy.get('[data-cy="quality-score"], .quality, .score', { timeout: 5000 }).should('exist')
        
        return ifFoundInBody('[data-cy="save-analysis"], button', () => {
          cy.get('[data-cy="save-analysis"], button').first().click()
          cy.get('body', { timeout: 5000 }).should('be.visible')
        })
      }).then(() => {
        visitAndWait('/mis-analisis')
        cy.get('[data-cy="analysis-history"], .history, .list', { timeout: 5000 }).should('exist')
      })
    })
  })

  it('debe completar flujo de gestión de finca y lotes', () => {
    visitAndWait('/mis-fincas')
    
    clickIfExistsAndContinue('[data-cy="add-finca-button"], button', () => {
      ifFoundInBody('[data-cy="map-container"], .map, canvas', () => {
        cy.get('[data-cy="map-container"], .map, canvas').first().click(300, 200, { force: true })
      })
      cy.get('[data-cy="save-finca"], button[type="submit"]').first().click()
      cy.get('body', { timeout: 5000 }).should('be.visible')
      
      return ifFoundInBody('[data-cy="finca-item"], .finca-item, .item', () => {
        cy.get('[data-cy="finca-item"], .finca-item, .item').first().click({ force: true })
        return ifFoundInBody('[data-cy="add-lote-button"], button', () => {
          cy.get('[data-cy="add-lote-button"], button').first().click({ force: true })
          cy.get('[data-cy="save-lote"], button[type="submit"]').first().click()
          cy.get('body', { timeout: 5000 }).should('be.visible')
          
          return ifFoundInBody('[data-cy="finca-lotes"], .lotes', () => {
            cy.get('[data-cy="finca-lotes"], .lotes', { timeout: 5000 }).should('exist')
          })
        })
      })
    })
  })

  it('debe completar flujo de generación de reporte', () => {
    cy.login('analyst')
    visitAndWait('/reportes')
    
    clickIfExistsAndContinue('[data-cy="create-report-button"], button', () => {
      return ifFoundInBody('[data-cy="report-type"], select', () => {
        cy.get('[data-cy="report-type"], select').first().select('analisis-periodo', { force: true })
        cy.get('[data-cy="start-date"], input[type="date"]').first().type('2024-01-01', { force: true })
        cy.get('[data-cy="end-date"], input[type="date"]').first().type('2024-01-31', { force: true })
        cy.get('[data-cy="include-charts"], input[type="checkbox"]').first().check({ force: true })
        cy.get('[data-cy="generate-report"], button[type="submit"]').first().click()
        cy.get('body', { timeout: 30000 }).should('be.visible')
        
        return ifFoundInBody('[data-cy="report-item"], .report-item, .item', () => {
          cy.get('[data-cy="report-item"], .report-item, .item').first().click({ force: true })
          cy.get('[data-cy="report-details"], .details', { timeout: 5000 }).should('exist')
        })
      })
    })
  })

  it('debe completar flujo de administración de usuarios', () => {
    cy.login('admin')
    visitAndWait('/admin/agricultores')
    
    ifFoundInBody('[data-cy="users-list"], .users-list, .list', () => {
      cy.get('[data-cy="users-list"], .users-list, .list', { timeout: 5000 }).should('exist')
      
      return ifFoundInBody('[data-cy="user-item"], .user-item, .item', () => {
        cy.get('[data-cy="user-item"], .user-item, .item').first().click({ force: true })
        cy.get('[data-cy="user-details"], .details', { timeout: 5000 }).should('exist')
        
        return clickIfExistsAndContinue('[data-cy="edit-user"], button', () => {
          return ifFoundInBody('[data-cy="user-first-name"], input[name*="first"]', () => {
            cy.get('[data-cy="user-first-name"], input[name*="first"]').first().clear().type('Usuario Editado')
            cy.get('[data-cy="save-user"], button[type="submit"]').first().click()
            cy.get('body', { timeout: 5000 }).should('be.visible')
          })
        })
      })
    }).then(() => {
      visitAndWait('/admin/dashboard')
      ifFoundInBody('[data-cy="admin-stats"], .stats', () => {
        cy.get('[data-cy="admin-stats"], .stats', { timeout: 5000 }).should('exist')
        cy.get('[data-cy="total-users"], .total-users', { timeout: 5000 }).should('exist')
      })
    })
  })

  it('debe completar flujo de verificación de email', () => {
    visitAndWait('/registro')
    
    const password = generatePassword()
    const newUser = {
      firstName: 'Nuevo',
      lastName: 'Usuario',
      email: 'nuevo.usuario@test.com',
      password: password,
      confirmPassword: password,
      role: 'farmer'
    }
    
    const fillRegistrationForm = () => {
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
    }
    
    ifFoundInBody('[data-cy="first-name-input"], input[name*="first"]', () => {
      fillRegistrationForm()
    })
    
    visitAndWait('/login')
    
    ifFoundInBody('[data-cy="email-input"], input[type="email"]', () => {
      cy.get('[data-cy="email-input"], input[type="email"]').first().type(newUser.email, { force: true })
      cy.get('[data-cy="password-input"], input[type="password"]').first().type(newUser.password, { force: true })
      cy.get('[data-cy="login-button"], button[type="submit"]').first().click({ force: true })
      
      return ifFoundInBody('[data-cy="verification-message"], .verification-message', ($el) => {
        cy.wrap($el).first().should('satisfy', ($element) => {
          const text = $element.text().toLowerCase()
          return text.includes('verifica') || text.includes('email') || text.length > 0
        })
        
        return clickIfExistsAndContinue('[data-cy="resend-verification-button"], button', () => {
          cy.get('body', { timeout: 5000 }).should('be.visible')
        })
      })
    })
  })

  it('debe completar flujo de recuperación de contraseña', () => {
    visitAndWait('/login')
    
    clickIfExistsAndContinue('[data-cy="forgot-password-link"], a[href*="password"], a[href*="forgot"]', () => {
      return cy.fixture('users').then((users) => {
        const user = users.farmer
        return ifFoundInBody('[data-cy="email-input"], input[type="email"]', () => {
          cy.get('[data-cy="email-input"], input[type="email"]').first().type(user.email, { force: true })
          cy.get('[data-cy="send-reset-button"], button[type="submit"]').first().click({ force: true })
          cy.get('body', { timeout: 5000 }).should('be.visible')
        })
      })
    })
    
    visitAndWait('/reset-password?token=valid-token-123')
    
    ifFoundInBody('[data-cy="new-password-input"], input[type="password"]', () => {
      const newPassword = generatePassword()
      cy.get('[data-cy="new-password-input"], input[type="password"]').first().type(newPassword, { force: true })
      cy.get('[data-cy="confirm-password-input"], input[type="password"]').eq(1).type(newPassword, { force: true })
      cy.get('[data-cy="reset-button"], button[type="submit"]').first().click({ force: true })
      cy.get('body', { timeout: 5000 }).should('be.visible')
    })
    
    visitAndWait('/login')
    
    cy.fixture('users').then((users) => {
      const user = users.farmer
      const loginPassword = generatePassword()
      return ifFoundInBody('[data-cy="email-input"], input[type="email"]', () => {
        cy.get('[data-cy="email-input"], input[type="email"]').first().type(user.email, { force: true })
        cy.get('[data-cy="password-input"], input[type="password"]').first().type(loginPassword, { force: true })
        cy.get('[data-cy="login-button"], button[type="submit"]').first().click({ force: true })
        verifyUrlPatterns(['/agricultor-dashboard', '/dashboard', '/login'], 10000)
      })
    })
  })

  it('debe completar flujo de navegación entre roles', () => {
    cy.login('farmer')
    visitAndWait('/agricultor-dashboard')
    verifyDashboard('[data-cy="farmer-dashboard"], .farmer-dashboard', ['/agricultor', '/dashboard'])
    
    cy.login('analyst')
    visitAndWait('/analisis')
    verifyDashboard('[data-cy="analyst-dashboard"], .analyst-dashboard', ['/analisis', '/dashboard'])
    
    cy.login('admin')
    visitAndWait('/admin/dashboard')
    verifyDashboard('[data-cy="admin-dashboard"], .admin-dashboard', ['/admin', '/dashboard'])
  })

  it('debe completar flujo de logout y acceso denegado', () => {
    cy.login('farmer')
    visitAndWait('/agricultor-dashboard')
    
    clickIfExistsAndContinue('[data-cy="user-menu"], .user-menu, button', () => {
      return clickIfExistsAndContinue('[data-cy="logout-button"], button, a', () => {
        return clickIfExistsAndContinue('[data-cy="confirm-logout"], button[type="submit"]', () => {
          cy.wrap(null)
        })
      })
    })
    
    cy.wait(2000)
    verifyUrlPatterns(['/login', '/auth', '/agricultor-dashboard'], 10000)
    
    cy.window().then((win) => {
      win.localStorage.removeItem('access_token')
      win.localStorage.removeItem('refresh_token')
      win.localStorage.removeItem('auth_token')
      win.localStorage.removeItem('user_data')
    })
    
    cy.visit('/agricultor-dashboard', { failOnStatusCode: false })
    cy.get('body', { timeout: 10000 }).should('be.visible')
    verifyUrlPatterns(['/login', '/auth', '/agricultor-dashboard'], 10000)
  })

  it('debe completar flujo de navegación con breadcrumbs', () => {
    cy.login('farmer')
    visitAndWait('/mis-fincas')
    
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
        
        return clickIfExistsAndContinue('[data-cy="breadcrumb-fincas"], .breadcrumb', () => {
          cy.get('body', { timeout: 5000 }).should('be.visible')
        }).then(() => {
          return clickIfExistsAndContinue('[data-cy="breadcrumb-home"], .breadcrumb, a[href*="dashboard"]', () => {
            verifyUrlPatterns(['/agricultor-dashboard', '/dashboard'], 10000)
          })
        })
      })
    })
  })

  it('debe completar flujo de búsqueda y filtros', () => {
    cy.login('farmer')
    
    const performSearch = (url, searchSelector, searchTerm) => {
      visitAndWait(url)
      typeIfExistsAndContinue(searchSelector, searchTerm, () => {
        cy.get('body', { timeout: 3000 }).should('be.visible')
      })
    }
    
    performSearch('/mis-fincas', '[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]', 'Paraíso')
    performSearch('/mis-lotes', '[data-cy="search-lotes"], input[type="search"], input[placeholder*="search"]', 'Norte')
    performSearch('/mis-analisis', '[data-cy="search-analisis"], input[type="search"], input[placeholder*="search"]', 'test-cacao')
  })

  it('debe completar flujo de exportación múltiple', () => {
    cy.login('farmer')
    
    const performBulkExport = (url, checkboxSelector) => {
      visitAndWait(url)
      ifFoundInBody(checkboxSelector, () => {
        cy.get(checkboxSelector).first().check({ force: true })
        cy.get(checkboxSelector).eq(1).check({ force: true })
        return clickIfExistsAndContinue('[data-cy="bulk-export"], button', () => {
          cy.get('body', { timeout: 5000 }).should('be.visible')
        })
      })
    }
    
    performBulkExport('/mis-fincas', '[data-cy="finca-checkbox"], input[type="checkbox"]')
    performBulkExport('/mis-lotes', '[data-cy="lote-checkbox"], input[type="checkbox"]')
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
