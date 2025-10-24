describe('Autenticación - Logout', () => {
  beforeEach(() => {
    cy.login('admin')
  })

  it('debe hacer logout exitosamente desde el menú de usuario', () => {
    cy.visit('/admin/dashboard')
    
    // Abrir menú de usuario
    cy.get('[data-cy="user-menu"]').click()
    cy.get('[data-cy="logout-button"]').click()
    
    // Confirmar logout si hay modal de confirmación
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="confirm-logout"]').length > 0) {
        cy.get('[data-cy="confirm-logout"]').click()
      }
    })
    
    // Verificar redirección al login
    cy.url().should('include', '/login')
    
    // Verificar que los tokens se eliminaron
    cy.window().then((win) => {
      expect(win.localStorage.getItem('auth_token')).to.be.null
      expect(win.localStorage.getItem('refresh_token')).to.be.null
      expect(win.localStorage.getItem('user_data')).to.be.null
    })
  })

  it('debe hacer logout desde cualquier página', () => {
    const pages = ['/admin/dashboard', '/analisis', '/agricultor-dashboard']
    
    pages.forEach(page => {
      cy.visit(page)
      
      cy.get('[data-cy="user-menu"]').click()
      cy.get('[data-cy="logout-button"]').click()
      
      cy.url().should('include', '/login')
      
      // Volver a hacer login para la siguiente página
      if (page !== pages[pages.length - 1]) {
        cy.login('admin')
      }
    })
  })

  it('debe limpiar datos de sesión al hacer logout', () => {
    cy.visit('/admin/dashboard')
    
    // Verificar que hay datos en localStorage
    cy.window().then((win) => {
      expect(win.localStorage.getItem('auth_token')).to.not.be.null
      expect(win.localStorage.getItem('user_data')).to.not.be.null
    })
    
    cy.get('[data-cy="user-menu"]').click()
    cy.get('[data-cy="logout-button"]').click()
    
    // Verificar que se limpiaron los datos
    cy.window().then((win) => {
      expect(win.localStorage.getItem('auth_token')).to.be.null
      expect(win.localStorage.getItem('refresh_token')).to.be.null
      expect(win.localStorage.getItem('user_data')).to.be.null
    })
  })

  it('debe redirigir a página solicitada después del logout', () => {
    cy.visit('/admin/dashboard')
    
    // Intentar acceder a una página protegida después del logout
    cy.get('[data-cy="user-menu"]').click()
    cy.get('[data-cy="logout-button"]').click()
    
    // Intentar acceder a página protegida
    cy.visit('/admin/agricultores')
    
    // Debería redirigir al login
    cy.url().should('include', '/login')
  })

  it('debe mostrar mensaje de confirmación antes del logout', () => {
    cy.visit('/admin/dashboard')
    
    cy.get('[data-cy="user-menu"]').click()
    cy.get('[data-cy="logout-button"]').click()
    
    // Verificar modal de confirmación
    cy.get('[data-cy="logout-confirmation-modal"]')
      .should('be.visible')
      .and('contain', '¿Estás seguro de que quieres cerrar sesión?')
    
    cy.get('[data-cy="cancel-logout"]').click()
    
    // Verificar que permanece en la página
    cy.url().should('include', '/admin/dashboard')
  })

  it('debe cancelar logout desde modal de confirmación', () => {
    cy.visit('/admin/dashboard')
    
    cy.get('[data-cy="user-menu"]').click()
    cy.get('[data-cy="logout-button"]').click()
    
    cy.get('[data-cy="cancel-logout"]').click()
    
    // Verificar que permanece en la página
    cy.url().should('include', '/admin/dashboard')
    cy.get('[data-cy="admin-dashboard"]').should('be.visible')
  })

  it('debe hacer logout automático cuando el token expira', () => {
    cy.visit('/admin/dashboard')
    
    // Simular token expirado
    cy.window().then((win) => {
      win.localStorage.setItem('auth_token', 'expired-token')
    })
    
    // Intentar hacer una acción que requiera autenticación
    cy.get('[data-cy="some-protected-action"]').click()
    
    // Debería redirigir automáticamente al login
    cy.url().should('include', '/login')
    
    // Verificar mensaje de sesión expirada
    cy.get('[data-cy="session-expired-message"]')
      .should('be.visible')
      .and('contain', 'Sesión expirada')
  })
})
