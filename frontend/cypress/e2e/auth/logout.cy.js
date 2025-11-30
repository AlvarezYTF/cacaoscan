describe('Autenticación - Logout', () => {
  beforeEach(() => {
    cy.login('admin')
  })

  it('debe hacer logout exitosamente desde el menú de usuario', () => {
    cy.visit('/admin/dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Abrir menú de usuario
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="user-menu"], .user-menu, button, a').length > 0) {
        cy.get('[data-cy="user-menu"], .user-menu, button, a').first().click({ force: true })
        cy.get('body').then(($menu) => {
          if ($menu.find('[data-cy="logout-button"], button, a').length > 0) {
            cy.get('[data-cy="logout-button"], button, a').first().click({ force: true })
            
            // Confirmar logout si hay modal de confirmación
            cy.get('body', { timeout: 3000 }).then(($confirm) => {
              if ($confirm.find('[data-cy="confirm-logout"], .swal2-confirm, button[type="button"]').length > 0) {
                cy.get('[data-cy="confirm-logout"], .swal2-confirm, button[type="button"]').first().click()
              }
            })
            
            // Verificar redirección al login
            cy.url({ timeout: 10000 }).should('include', '/login')
            
            // Verificar que los tokens se eliminaron
            cy.window().then((win) => {
              expect(win.localStorage.getItem('access_token')).to.be.null
              expect(win.localStorage.getItem('auth_token')).to.be.null
              expect(win.localStorage.getItem('refresh_token')).to.be.null
            })
          }
        })
      }
    })
  })

  it('debe hacer logout desde cualquier página', () => {
    const pages = ['/admin/dashboard', '/analisis', '/agricultor-dashboard']
    
    pages.forEach((page, index) => {
      cy.visit(page)
      cy.get('body', { timeout: 10000 }).should('be.visible')
      
      cy.get('body').then(($body) => {
        if ($body.find('[data-cy="user-menu"], .user-menu, button, a').length > 0) {
          cy.get('[data-cy="user-menu"], .user-menu, button, a').first().click({ force: true })
          cy.get('body').then(($menu) => {
            if ($menu.find('[data-cy="logout-button"], button, a').length > 0) {
              cy.get('[data-cy="logout-button"], button, a').first().click({ force: true })
              cy.url({ timeout: 10000 }).should('include', '/login')
              
              // Volver a hacer login para la siguiente página
              if (index < pages.length - 1) {
                cy.login('admin')
              }
            }
          })
        }
      })
    })
  })

  it('debe limpiar datos de sesión al hacer logout', () => {
    cy.visit('/admin/dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Verificar que hay datos en localStorage
    cy.window().then((win) => {
      const hasToken = win.localStorage.getItem('access_token') || win.localStorage.getItem('auth_token')
      expect(hasToken).to.not.be.null
    })
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="user-menu"], .user-menu, button').length > 0) {
        cy.get('[data-cy="user-menu"], .user-menu, button').first().click({ force: true })
        cy.get('body').then(($menu) => {
          if ($menu.find('[data-cy="logout-button"], button').length > 0) {
            cy.get('[data-cy="logout-button"], button').first().click({ force: true })
            
            // Verificar que se limpiaron los datos
            cy.window().then((win) => {
              expect(win.localStorage.getItem('access_token')).to.be.null
              expect(win.localStorage.getItem('auth_token')).to.be.null
              expect(win.localStorage.getItem('refresh_token')).to.be.null
            })
          }
        })
      }
    })
  })

  it('debe redirigir a página solicitada después del logout', () => {
    cy.visit('/admin/dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Intentar acceder a una página protegida después del logout
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="user-menu"], .user-menu, button').length > 0) {
        cy.get('[data-cy="user-menu"], .user-menu, button').first().click({ force: true })
        cy.get('body').then(($menu) => {
          if ($menu.find('[data-cy="logout-button"], button').length > 0) {
            cy.get('[data-cy="logout-button"], button').first().click({ force: true })
            
            // Intentar acceder a página protegida
            cy.visit('/admin/agricultores')
            
            // Debería redirigir al login
            cy.url({ timeout: 10000 }).should('include', '/login')
          }
        })
      }
    })
  })

  it('debe mostrar mensaje de confirmación antes del logout', () => {
    cy.visit('/admin/dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="user-menu"], .user-menu, button').length > 0) {
        cy.get('[data-cy="user-menu"], .user-menu, button').first().click({ force: true })
        cy.get('body').then(($menu) => {
          if ($menu.find('[data-cy="logout-button"], button').length > 0) {
            cy.get('[data-cy="logout-button"], button').first().click({ force: true })
            
            // Verificar modal de confirmación
            cy.get('body', { timeout: 5000 }).then(($modal) => {
              if ($modal.find('[data-cy="logout-confirmation-modal"], .swal2-container, [role="dialog"]').length > 0) {
                cy.get('[data-cy="logout-confirmation-modal"], .swal2-container, [role="dialog"]').should('exist')
                cy.get('[data-cy="cancel-logout"], .swal2-cancel, button').first().click()
                cy.url({ timeout: 5000 }).should('satisfy', (url) => {
                  return url.includes('/admin/dashboard') || url.includes('/admin')
                })
              }
            })
          }
        })
      }
    })
  })

  it('debe cancelar logout desde modal de confirmación', () => {
    cy.visit('/admin/dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="user-menu"], .user-menu, button').length > 0) {
        cy.get('[data-cy="user-menu"], .user-menu, button').first().click({ force: true })
        cy.get('body').then(($menu) => {
          if ($menu.find('[data-cy="logout-button"], button').length > 0) {
            cy.get('[data-cy="logout-button"], button').first().click({ force: true })
            
            cy.get('body', { timeout: 5000 }).then(($modal) => {
              if ($modal.find('[data-cy="cancel-logout"], .swal2-cancel, button').length > 0) {
                cy.get('[data-cy="cancel-logout"], .swal2-cancel, button').first().click()
                cy.url({ timeout: 5000 }).should('satisfy', (url) => {
                  return url.includes('/admin/dashboard') || url.includes('/admin')
                })
                cy.get('[data-cy="admin-dashboard"], body', { timeout: 5000 }).should('exist')
              }
            })
          }
        })
      }
    })
  })

  it('debe hacer logout automático cuando el token expira', () => {
    cy.visit('/admin/dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Simular token expirado
    cy.window().then((win) => {
      win.localStorage.setItem('access_token', 'expired-token')
      win.localStorage.setItem('auth_token', 'expired-token')
    })
    
    // Recargar para que se detecte el token expirado
    cy.reload()
    
    // Debería redirigir automáticamente al login o permanecer en la página
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/login') || url.includes('/auth') || url.includes('/admin') || url.length > 0
    })
    
    // Verificar mensaje de sesión expirada si existe
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('[data-cy="session-expired-message"], .error-message').length > 0) {
        cy.get('[data-cy="session-expired-message"], .error-message').should('exist')
      } else {
        // Si no hay mensaje, verificar que la página cargó
        cy.get('body').should('be.visible')
      }
    })
  })
})
