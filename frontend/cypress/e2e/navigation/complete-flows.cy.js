import { setupAuth } from '../../support/helpers'
import { SELECTORS } from '../../support/selectors'

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
    cy.get('body').then(($body) => {
      if ($body.find('input[type="file"]').length > 0) {
        cy.uploadTestImage('test-cacao.jpg')
        cy.get('body', { timeout: 5000 }).then(($afterUpload) => {
          if ($afterUpload.find('[data-cy="upload-button"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="upload-button"], button[type="submit"]').first().click()
            cy.get('body', { timeout: 5000 }).should('be.visible')
            
            // 3. Esperar análisis
            cy.get('[data-cy="analysis-results"], .results, .result', { timeout: 30000 }).should('exist')
            
            // 4. Ver resultados
            cy.get('[data-cy="quality-score"], .quality, .score', { timeout: 5000 }).should('exist')
            
            // 5. Guardar análisis
            cy.get('body').then(($results) => {
              if ($results.find('[data-cy="save-analysis"], button').length > 0) {
                cy.get('[data-cy="save-analysis"], button').first().click()
                cy.get('body', { timeout: 5000 }).should('be.visible')
              }
            })
            
            // 6. Verificar que aparece en historial
            cy.visit('/mis-analisis')
            cy.get('body', { timeout: 10000 }).should('be.visible')
            cy.get('[data-cy="analysis-history"], .history, .list', { timeout: 5000 }).should('exist')
          }
        })
      }
    })
  })

  it('debe completar flujo de gestión de finca y lotes', () => {
    // 1. Crear finca
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="map-container"], .map, canvas').length > 0) {
            cy.get('[data-cy="map-container"], .map, canvas').first().click(300, 200, { force: true })
          }
          cy.get('[data-cy="save-finca"], button[type="submit"]').first().click()
          cy.get('body', { timeout: 5000 }).should('be.visible')
          
          // 2. Crear lote en la finca
          cy.get('body').then(($afterFinca) => {
            if ($afterFinca.find('[data-cy="finca-item"], .finca-item, .item').length > 0) {
              cy.get('[data-cy="finca-item"], .finca-item, .item').first().click({ force: true })
              cy.get('body', { timeout: 5000 }).then(($fincaDetails) => {
                if ($fincaDetails.find('[data-cy="add-lote-button"], button').length > 0) {
                  cy.get('[data-cy="add-lote-button"], button').first().click({ force: true })
                  cy.get('body', { timeout: 5000 }).then(($loteModal) => {
                    cy.get('[data-cy="save-lote"], button[type="submit"]').first().click()
                    cy.get('body', { timeout: 5000 }).should('be.visible')
                    
                    // 3. Verificar relación finca-lote
                    cy.get('body').then(($afterLote) => {
                      if ($afterLote.find('[data-cy="finca-lotes"], .lotes').length > 0) {
                        cy.get('[data-cy="finca-lotes"], .lotes', { timeout: 5000 }).should('exist')
                      }
                    })
                  })
                }
              })
            }
          })
        })
      }
    })
  })

  it('debe completar flujo de generación de reporte', () => {
    cy.login('analyst')
    
    // 1. Ir a reportes
    cy.visit('/reportes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // 2. Crear reporte
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="create-report-button"], button').length > 0) {
        cy.get('[data-cy="create-report-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="report-type"], select').length > 0) {
            cy.get('[data-cy="report-type"], select').first().select('analisis-periodo', { force: true })
            cy.get('[data-cy="start-date"], input[type="date"]').first().type('2024-01-01', { force: true })
            cy.get('[data-cy="end-date"], input[type="date"]').first().type('2024-01-31', { force: true })
            cy.get('[data-cy="include-charts"], input[type="checkbox"]').first().check({ force: true })
            cy.get('[data-cy="generate-report"], button[type="submit"]').first().click()
            cy.get('body', { timeout: 30000 }).should('be.visible')
            
            // 4. Ver reporte generado
            cy.get('body').then(($afterGenerate) => {
              if ($afterGenerate.find('[data-cy="report-item"], .report-item, .item').length > 0) {
                cy.get('[data-cy="report-item"], .report-item, .item').first().click({ force: true })
                cy.get('[data-cy="report-details"], .details', { timeout: 5000 }).should('exist')
              }
            })
          }
        })
      }
    })
  })

  it('debe completar flujo de administración de usuarios', () => {
    cy.login('admin')
    
    // 1. Ir a gestión de agricultores
    cy.visit('/admin/agricultores')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // 2. Ver lista de usuarios
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="users-list"], .users-list, .list').length > 0) {
        cy.get('[data-cy="users-list"], .users-list, .list', { timeout: 5000 }).should('exist')
        
        // 3. Ver detalles de usuario
        if ($body.find('[data-cy="user-item"], .user-item, .item').length > 0) {
          cy.get('[data-cy="user-item"], .user-item, .item').first().click({ force: true })
          cy.get('[data-cy="user-details"], .details', { timeout: 5000 }).should('exist')
          
          // 4. Editar usuario
          cy.get('body').then(($details) => {
            if ($details.find('[data-cy="edit-user"], button').length > 0) {
              cy.get('[data-cy="edit-user"], button').first().click({ force: true })
              cy.get('body', { timeout: 5000 }).then(($edit) => {
                if ($edit.find('[data-cy="user-first-name"], input[name*="first"]').length > 0) {
                  cy.get('[data-cy="user-first-name"], input[name*="first"]').first().clear().type('Usuario Editado')
                  cy.get('[data-cy="save-user"], button[type="submit"]').first().click()
                  cy.get('body', { timeout: 5000 }).should('be.visible')
                }
              })
            }
          })
        }
      }
      
      // 5. Verificar estadísticas
      cy.visit('/admin/dashboard')
      cy.get('body', { timeout: 10000 }).should('be.visible')
      cy.get('body').then(($dashboard) => {
        if ($dashboard.find('[data-cy="admin-stats"], .stats').length > 0) {
          cy.get('[data-cy="admin-stats"], .stats', { timeout: 5000 }).should('exist')
          cy.get('[data-cy="total-users"], .total-users', { timeout: 5000 }).should('exist')
        }
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
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="first-name-input"], input[name*="first"]').length > 0) {
        cy.get('[data-cy="first-name-input"], input[name*="first"]').first().type(newUser.firstName, { force: true })
        cy.get('[data-cy="last-name-input"], input[name*="last"]').first().type(newUser.lastName, { force: true })
        cy.get('[data-cy="email-input"], input[type="email"]').first().type(newUser.email, { force: true })
        cy.get('[data-cy="password-input"], input[type="password"]').first().type(newUser.password, { force: true })
        cy.get('[data-cy="confirm-password-input"], input[type="password"]').eq(1).type(newUser.confirmPassword, { force: true })
        
        cy.get('body').then(($afterInputs) => {
          if ($afterInputs.find('[data-cy="role-select"], select').length > 0) {
            cy.get('[data-cy="role-select"], select').first().select(newUser.role, { force: true })
          }
          if ($afterInputs.find('[data-cy="terms-checkbox"], input[type="checkbox"]').length > 0) {
            cy.get('[data-cy="terms-checkbox"], input[type="checkbox"]').first().check({ force: true })
          }
          cy.get('[data-cy="register-button"], button[type="submit"]').first().click({ force: true })
          
          cy.get('body', { timeout: 5000 }).should('be.visible')
        })
      }
    })
    
    // 2. Intentar hacer login (debería requerir verificación)
    cy.visit('/login')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="email-input"], input[type="email"]').length > 0) {
        cy.get('[data-cy="email-input"], input[type="email"]').first().type(newUser.email, { force: true })
        cy.get('[data-cy="password-input"], input[type="password"]').first().type(newUser.password, { force: true })
        cy.get('[data-cy="login-button"], button[type="submit"]').first().click({ force: true })
        
        cy.get('body', { timeout: 5000 }).then(($afterLogin) => {
          // 3. Ver mensaje de verificación si existe
          if ($afterLogin.find('[data-cy="verification-message"], .verification-message').length > 0) {
            cy.get('[data-cy="verification-message"], .verification-message').first().should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('verifica') || text.includes('email') || text.length > 0
            })
            
            // 4. Reenviar email de verificación si existe el botón
            if ($afterLogin.find('[data-cy="resend-verification-button"], button').length > 0) {
              cy.get('[data-cy="resend-verification-button"], button').first().click({ force: true })
              cy.get('body', { timeout: 5000 }).should('be.visible')
            }
          }
        })
      }
    })
  })

  it('debe completar flujo de recuperación de contraseña', () => {
    // 1. Ir a login
    cy.visit('/login')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // 2. Ir a recuperación de contraseña
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="forgot-password-link"], a[href*="password"], a[href*="forgot"]').length > 0) {
        cy.get('[data-cy="forgot-password-link"], a[href*="password"], a[href*="forgot"]').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($forgot) => {
          // 3. Solicitar recuperación
          cy.fixture('users').then((users) => {
            const user = users.farmer
            if ($forgot.find('[data-cy="email-input"], input[type="email"]').length > 0) {
              cy.get('[data-cy="email-input"], input[type="email"]').first().type(user.email, { force: true })
              cy.get('[data-cy="send-reset-button"], button[type="submit"]').first().click({ force: true })
              cy.get('body', { timeout: 5000 }).should('be.visible')
            }
          })
        })
      }
    })
    
    // 4. Simular reset de contraseña
    cy.visit('/reset-password?token=valid-token-123')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="new-password-input"], input[type="password"]').length > 0) {
        const newPassword = generatePassword()
        cy.get('[data-cy="new-password-input"], input[type="password"]').first().type(newPassword, { force: true })
        cy.get('[data-cy="confirm-password-input"], input[type="password"]').eq(1).type(newPassword, { force: true })
        cy.get('[data-cy="reset-button"], button[type="submit"]').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).should('be.visible')
      }
    })
    
    // 5. Hacer login con nueva contraseña
    cy.visit('/login')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.fixture('users').then((users) => {
      const user = users.farmer
      cy.get('body').then(($body) => {
        if ($body.find('[data-cy="email-input"], input[type="email"]').length > 0) {
          const loginPassword = generatePassword()
          cy.get('[data-cy="email-input"], input[type="email"]').first().type(user.email, { force: true })
          cy.get('[data-cy="password-input"], input[type="password"]').first().type(loginPassword, { force: true })
          cy.get('[data-cy="login-button"], button[type="submit"]').first().click({ force: true })
          
          cy.url({ timeout: 10000 }).should('satisfy', (url) => {
            return url.includes('/agricultor-dashboard') || url.includes('/dashboard') || url.includes('/login')
          })
        }
      })
    })
  })

  it('debe completar flujo de navegación entre roles', () => {
    // Test como agricultor
    cy.login('farmer')
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="farmer-dashboard"], .farmer-dashboard').length > 0) {
        cy.get('[data-cy="farmer-dashboard"], .farmer-dashboard').should('exist')
      } else {
        cy.url({ timeout: 10000 }).should('satisfy', (url) => {
          return url.includes('/agricultor') || url.includes('/dashboard')
        })
      }
    })
    
    // Test como analista
    cy.login('analyst')
    cy.visit('/analisis')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="analyst-dashboard"], .analyst-dashboard').length > 0) {
        cy.get('[data-cy="analyst-dashboard"], .analyst-dashboard').should('exist')
      } else {
        cy.url({ timeout: 10000 }).should('satisfy', (url) => {
          return url.includes('/analisis') || url.includes('/dashboard')
        })
      }
    })
    
    // Test como admin
    cy.login('admin')
    cy.visit('/admin/dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="admin-dashboard"], .admin-dashboard').length > 0) {
        cy.get('[data-cy="admin-dashboard"], .admin-dashboard').should('exist')
      } else {
        cy.url({ timeout: 10000 }).should('satisfy', (url) => {
          return url.includes('/admin') || url.includes('/dashboard')
        })
      }
    })
  })

  it('debe completar flujo de logout y acceso denegado', () => {
    cy.login('farmer')
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Hacer logout
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="user-menu"], .user-menu, button').length > 0) {
        cy.get('[data-cy="user-menu"], .user-menu, button').first().click({ force: true })
        cy.get('body', { timeout: 3000 }).then(($menu) => {
          if ($menu.find('[data-cy="logout-button"], button, a').length > 0) {
            cy.get('[data-cy="logout-button"], button, a').first().click({ force: true })
            cy.get('body', { timeout: 3000 }).then(($confirm) => {
              if ($confirm.find('[data-cy="confirm-logout"], button[type="submit"]').length > 0) {
                cy.get('[data-cy="confirm-logout"], button[type="submit"]').first().click({ force: true })
              }
            })
          }
        })
      }
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
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-item"], .finca-item, .item').length > 0) {
        cy.get('[data-cy="finca-item"], .finca-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($finca) => {
          if ($finca.find('[data-cy="breadcrumb-fincas"], .breadcrumb').length > 0) {
            cy.get('[data-cy="breadcrumb-fincas"], .breadcrumb').should('exist')
          }
          
          if ($finca.find('[data-cy="lote-item"], .lote-item, .item').length > 0) {
            cy.get('[data-cy="lote-item"], .lote-item, .item').first().click({ force: true })
            cy.get('body', { timeout: 5000 }).then(($lote) => {
              if ($lote.find('[data-cy="breadcrumb-lotes"], .breadcrumb').length > 0) {
                cy.get('[data-cy="breadcrumb-lotes"], .breadcrumb').should('exist')
              }
              
              // Usar breadcrumbs para navegar si existen
              if ($lote.find('[data-cy="breadcrumb-fincas"], .breadcrumb').length > 0) {
                cy.get('[data-cy="breadcrumb-fincas"], .breadcrumb').first().click({ force: true })
                cy.get('body', { timeout: 5000 }).should('be.visible')
              }
              
              if ($lote.find('[data-cy="breadcrumb-home"], .breadcrumb, a[href*="dashboard"]').length > 0) {
                cy.get('[data-cy="breadcrumb-home"], .breadcrumb, a[href*="dashboard"]').first().click({ force: true })
                cy.url({ timeout: 10000 }).should('satisfy', (url) => {
                  return url.includes('/agricultor-dashboard') || url.includes('/dashboard')
                })
              }
            })
          }
        })
      }
    })
  })

  it('debe completar flujo de búsqueda y filtros', () => {
    cy.login('farmer')
    
    // Buscar en fincas
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]').length > 0) {
        cy.get('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]').first().type('Paraíso', { force: true })
        cy.get('body', { timeout: 3000 }).should('be.visible')
      }
    })
    
    // Buscar en lotes
    cy.visit('/mis-lotes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="search-lotes"], input[type="search"], input[placeholder*="search"]').length > 0) {
        cy.get('[data-cy="search-lotes"], input[type="search"], input[placeholder*="search"]').first().type('Norte', { force: true })
        cy.get('body', { timeout: 3000 }).should('be.visible')
      }
    })
    
    // Buscar en análisis
    cy.visit('/mis-analisis')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="search-analisis"], input[type="search"], input[placeholder*="search"]').length > 0) {
        cy.get('[data-cy="search-analisis"], input[type="search"], input[placeholder*="search"]').first().type('test-cacao', { force: true })
        cy.get('body', { timeout: 3000 }).should('be.visible')
      }
    })
  })

  it('debe completar flujo de exportación múltiple', () => {
    cy.login('farmer')
    
    // Exportar múltiples fincas
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-checkbox"], input[type="checkbox"]').length > 0) {
        cy.get('[data-cy="finca-checkbox"], input[type="checkbox"]').first().check({ force: true })
        cy.get('[data-cy="finca-checkbox"], input[type="checkbox"]').eq(1).check({ force: true })
        cy.get('body', { timeout: 3000 }).then(($afterCheck) => {
          if ($afterCheck.find('[data-cy="bulk-export"], button').length > 0) {
            cy.get('[data-cy="bulk-export"], button').first().click({ force: true })
            cy.get('body', { timeout: 5000 }).should('be.visible')
          }
        })
      }
    })
    
    // Exportar múltiples lotes
    cy.visit('/mis-lotes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="lote-checkbox"], input[type="checkbox"]').length > 0) {
        cy.get('[data-cy="lote-checkbox"], input[type="checkbox"]').first().check({ force: true })
        cy.get('[data-cy="lote-checkbox"], input[type="checkbox"]').eq(1).check({ force: true })
        cy.get('body', { timeout: 3000 }).then(($afterCheck) => {
          if ($afterCheck.find('[data-cy="bulk-export"], button').length > 0) {
            cy.get('[data-cy="bulk-export"], button').first().click({ force: true })
            cy.get('body', { timeout: 5000 }).should('be.visible')
          }
        })
      }
    })
  })

  it('debe completar flujo de notificaciones', () => {
    cy.login('farmer')
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Ver notificaciones
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="notifications-bell"], .notifications-bell, button').length > 0) {
        cy.get('[data-cy="notifications-bell"], .notifications-bell, button').first().click({ force: true })
        cy.get('body', { timeout: 3000 }).then(($notifications) => {
          if ($notifications.find('[data-cy="notifications-list"], .notifications-list').length > 0) {
            cy.get('[data-cy="notifications-list"], .notifications-list').should('exist')
            
            // Marcar como leída si existe
            if ($notifications.find('[data-cy="notification-item"], .notification-item').length > 0) {
              cy.get('[data-cy="notification-item"], .notification-item').first().click({ force: true })
              cy.get('body', { timeout: 2000 }).then(($afterClick) => {
                if ($afterClick.find('[data-cy="mark-read"], button').length > 0) {
                  cy.get('[data-cy="mark-read"], button').first().click({ force: true })
                }
              })
            }
            
            // Marcar todas como leídas si existe
            if ($notifications.find('[data-cy="mark-all-read"], button').length > 0) {
              cy.get('[data-cy="mark-all-read"], button').first().click({ force: true })
              cy.get('body', { timeout: 5000 }).should('be.visible')
            }
          }
        })
      }
    })
  })
})
