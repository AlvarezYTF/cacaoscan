describe('Autenticación - Login', () => {
  beforeEach(() => {
    cy.visit('/login')
  })

  it('debe mostrar el formulario de login correctamente', () => {
    cy.get('[data-cy="login-form"]').should('be.visible')
    cy.get('[data-cy="email-input"]').should('be.visible')
    cy.get('[data-cy="password-input"]').should('be.visible')
    cy.get('[data-cy="login-button"]').should('be.visible')
    cy.get('[data-cy="forgot-password-link"]').should('be.visible')
    cy.get('[data-cy="register-link"]').should('be.visible')
  })

  it('debe hacer login exitoso como administrador', () => {
    cy.fixture('users').then((users) => {
      const admin = users.admin
      
      cy.get('[data-cy="email-input"]').type(admin.email)
      cy.get('[data-cy="password-input"]').type(admin.password)
      cy.get('[data-cy="login-button"]').click()
      
      // Verificar redirección al dashboard de admin
      cy.url().should('include', '/admin/dashboard')
      cy.get('[data-cy="admin-dashboard"]').should('be.visible')
      cy.get('[data-cy="user-menu"]').should('contain', admin.firstName)
    })
  })

  it('debe hacer login exitoso como analista', () => {
    cy.fixture('users').then((users) => {
      const analyst = users.analyst
      
      cy.get('[data-cy="email-input"]').type(analyst.email)
      cy.get('[data-cy="password-input"]').type(analyst.password)
      cy.get('[data-cy="login-button"]').click()
      
      // Verificar redirección al dashboard de analista
      cy.url().should('include', '/analisis')
      cy.get('[data-cy="analyst-dashboard"]').should('be.visible')
    })
  })

  it('debe hacer login exitoso como agricultor', () => {
    cy.fixture('users').then((users) => {
      const farmer = users.farmer
      
      cy.get('[data-cy="email-input"]').type(farmer.email)
      cy.get('[data-cy="password-input"]').type(farmer.password)
      cy.get('[data-cy="login-button"]').click()
      
      // Verificar redirección al dashboard de agricultor
      cy.url().should('include', '/agricultor-dashboard')
      cy.get('[data-cy="farmer-dashboard"]').should('be.visible')
    })
  })

  it('debe mostrar error con credenciales inválidas', () => {
    cy.fixture('users').then((users) => {
      const invalidUser = users.invalidUser
      
      cy.get('[data-cy="email-input"]').type(invalidUser.email)
      cy.get('[data-cy="password-input"]').type(invalidUser.password)
      cy.get('[data-cy="login-button"]').click()
      
      // Verificar mensaje de error
      cy.get('[data-cy="error-message"]')
        .should('be.visible')
        .and('contain', 'Credenciales inválidas')
      
      // Verificar que permanece en la página de login
      cy.url().should('include', '/login')
    })
  })

  it('debe validar campos requeridos', () => {
    cy.get('[data-cy="login-button"]').click()
    
    cy.get('[data-cy="email-input"]').should('have.attr', 'required')
    cy.get('[data-cy="password-input"]').should('have.attr', 'required')
    
    // Verificar mensajes de validación
    cy.get('[data-cy="email-error"]').should('be.visible')
    cy.get('[data-cy="password-error"]').should('be.visible')
  })

  it('debe validar formato de email', () => {
    cy.get('[data-cy="email-input"]').type('email-invalido')
    cy.get('[data-cy="password-input"]').type('password123')
    cy.get('[data-cy="login-button"]').click()
    
    cy.get('[data-cy="email-error"]')
      .should('be.visible')
      .and('contain', 'Formato de email inválido')
  })

  it('debe recordar credenciales si está habilitado', () => {
    cy.fixture('users').then((users) => {
      const admin = users.admin
      
      cy.get('[data-cy="remember-me"]').check()
      cy.get('[data-cy="email-input"]').type(admin.email)
      cy.get('[data-cy="password-input"]').type(admin.password)
      cy.get('[data-cy="login-button"]').click()
      
      // Logout y verificar que se recuerdan las credenciales
      cy.logout()
      cy.visit('/login')
      
      cy.get('[data-cy="email-input"]').should('have.value', admin.email)
      cy.get('[data-cy="remember-me"]').should('be.checked')
    })
  })

  it('debe redirigir a página solicitada después del login', () => {
    cy.fixture('users').then((users) => {
      const admin = users.admin
      
      // Intentar acceder a una página protegida
      cy.visit('/admin/agricultores')
      
      // Debería redirigir al login
      cy.url().should('include', '/login')
      
      // Hacer login
      cy.get('[data-cy="email-input"]').type(admin.email)
      cy.get('[data-cy="password-input"]').type(admin.password)
      cy.get('[data-cy="login-button"]').click()
      
      // Debería redirigir a la página originalmente solicitada
      cy.url().should('include', '/admin/agricultores')
    })
  })
})
