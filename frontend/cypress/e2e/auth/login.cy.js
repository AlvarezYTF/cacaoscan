describe('Autenticación - Login', () => {
  beforeEach(() => {
    cy.navigateTo('/login')
  })

  it('debe mostrar el formulario de login correctamente', () => {
    cy.get(SELECTORS.forms.login).should('be.visible')
    cy.get(SELECTORS.inputs.email).should('be.visible')
    cy.get(SELECTORS.inputs.password).should('be.visible')
    cy.get(SELECTORS.buttons.login).should('be.visible')
    cy.get('[data-cy="forgot-password-link"]').should('be.visible')
    cy.get('[data-cy="register-link"]').should('be.visible')
  })

  it('debe hacer login exitoso como administrador', () => {
    cy.fixture('users').then((users) => {
      const admin = users.admin
      
      cy.fillForm({ email: admin.email, password: admin.password }, 'login')
      cy.get(SELECTORS.buttons.login).click()
      
      // Verificar redirección al dashboard de admin
      cy.url().should('include', '/admin/dashboard')
      cy.get('[data-cy="admin-dashboard"]').should('be.visible')
      cy.get('[data-cy="user-menu"]').should('contain', admin.firstName)
    })
  })

  it('debe hacer login exitoso como analista', () => {
    cy.fixture('users').then((users) => {
      const analyst = users.analyst
      
      cy.fillForm({ email: analyst.email, password: analyst.password }, 'login')
      cy.get(SELECTORS.buttons.login).click()
      
      // Verificar redirección al dashboard de analista
      cy.url().should('include', '/analisis')
      cy.get('[data-cy="analyst-dashboard"]').should('be.visible')
    })
  })

  it('debe hacer login exitoso como agricultor', () => {
    cy.fixture('users').then((users) => {
      const farmer = users.farmer
      
      cy.fillForm({ email: farmer.email, password: farmer.password }, 'login')
      cy.get(SELECTORS.buttons.login).click()
      
      // Verificar redirección al dashboard de agricultor
      cy.url().should('include', '/agricultor-dashboard')
      cy.get('[data-cy="farmer-dashboard"]').should('be.visible')
    })
  })

  it('debe mostrar error con credenciales inválidas', () => {
    cy.fixture('users').then((users) => {
      const invalidUser = users.invalidUser
      
      cy.fillForm({ email: invalidUser.email, password: invalidUser.password }, 'login')
      cy.get(SELECTORS.buttons.login).click()
      
      // Verificar mensaje de error
      cy.get(SELECTORS.errors.errorMessage)
        .should('be.visible')
        .and('contain', 'Credenciales inválidas')
      
      // Verificar que permanece en la página de login
      cy.url().should('include', '/login')
    })
  })

  it('debe validar campos requeridos', () => {
    cy.get(SELECTORS.buttons.login).click()
    
    cy.get(SELECTORS.inputs.email).should('have.attr', 'required')
    cy.get(SELECTORS.inputs.password).should('have.attr', 'required')
    
    // Verificar mensajes de validación
    cy.get('[data-cy="email-error"]').should('be.visible')
    cy.get('[data-cy="password-error"]').should('be.visible')
  })

  it('debe validar formato de email', () => {
    cy.fixture('users').then((users) => {
      const validationUser = users.validationTestUser
      
      cy.fillForm({ email: validationUser.email, password: validationUser.password }, 'login')
      cy.get(SELECTORS.buttons.login).click()
      
      cy.get('[data-cy="email-error"]')
        .should('be.visible')
        .and('contain', 'Formato de email inválido')
    })
  })

  it('debe recordar credenciales si está habilitado', () => {
    cy.fixture('users').then((users) => {
      const admin = users.admin
      
      cy.get('[data-cy="remember-me"]').check()
      cy.fillForm({ email: admin.email, password: admin.password }, 'login')
      cy.get(SELECTORS.buttons.login).click()
      
      // Logout y verificar que se recuerdan las credenciales
      cy.logout()
      cy.navigateTo('/login')
      
      cy.get(SELECTORS.inputs.email).should('have.value', admin.email)
      cy.get('[data-cy="remember-me"]').should('be.checked')
    })
  })

  it('debe redirigir a página solicitada después del login', () => {
    cy.fixture('users').then((users) => {
      const admin = users.admin
      
      // Intentar acceder a una página protegida
      cy.navigateTo('/admin/agricultores')
      
      // Debería redirigir al login
      cy.url().should('include', '/login')
      
      // Hacer login
      cy.fillForm({ email: admin.email, password: admin.password }, 'login')
      cy.get(SELECTORS.buttons.login).click()
      
      // Debería redirigir a la página originalmente solicitada
      cy.url().should('include', '/admin/agricultores')
    })
  })
})
