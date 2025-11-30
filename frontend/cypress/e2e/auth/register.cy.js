describe('Autenticación - Registro', () => {
  beforeEach(() => {
    cy.visit('/registro')
    cy.fixture('testCredentials').as('credentials')
  })

  it('debe mostrar el formulario de registro correctamente', () => {
    cy.get('[data-cy="register-form"]').should('be.visible')
    cy.get('[data-cy="first-name-input"]').should('be.visible')
    cy.get('[data-cy="last-name-input"]').should('be.visible')
    cy.get('[data-cy="email-input"]').should('be.visible')
    cy.get('[data-cy="password-input"]').should('be.visible')
    cy.get('[data-cy="confirm-password-input"]').should('be.visible')
    cy.get('[data-cy="role-select"]').should('be.visible')
    cy.get('[data-cy="terms-checkbox"]').should('be.visible')
    cy.get('[data-cy="register-button"]').should('be.visible')
    cy.get('[data-cy="login-link"]').should('be.visible')
  })

  it('debe registrar un nuevo agricultor exitosamente', function() {
    const newUser = this.credentials.testUsers.farmer

    cy.get('[data-cy="first-name-input"]').type(newUser.firstName)
    cy.get('[data-cy="last-name-input"]').type(newUser.lastName)
    cy.get('[data-cy="email-input"]').type(newUser.email)
    cy.get('[data-cy="password-input"]').type(newUser.password)
    cy.get('[data-cy="confirm-password-input"]').type(newUser.confirmPassword)
    cy.get('[data-cy="role-select"]').select(newUser.role)
    cy.get('[data-cy="terms-checkbox"]').check()
    cy.get('[data-cy="register-button"]').click()

    // Verificar mensaje de éxito
    cy.get('[data-cy="success-message"]')
      .should('be.visible')
      .and('contain', 'Usuario registrado exitosamente')

    // Verificar que se muestra mensaje de verificación de email
    cy.get('[data-cy="verification-message"]')
      .should('be.visible')
      .and('contain', 'Verifica tu email')
  })

  it('debe registrar un nuevo analista exitosamente', function() {
    const newUser = this.credentials.testUsers.analyst

    cy.get('[data-cy="first-name-input"]').type(newUser.firstName)
    cy.get('[data-cy="last-name-input"]').type(newUser.lastName)
    cy.get('[data-cy="email-input"]').type(newUser.email)
    cy.get('[data-cy="password-input"]').type(newUser.password)
    cy.get('[data-cy="confirm-password-input"]').type(newUser.confirmPassword)
    cy.get('[data-cy="role-select"]').select(newUser.role)
    cy.get('[data-cy="terms-checkbox"]').check()
    cy.get('[data-cy="register-button"]').click()

    cy.get('[data-cy="success-message"]')
      .should('be.visible')
      .and('contain', 'Usuario registrado exitosamente')
  })

  it('debe mostrar error si el email ya existe', function() {
    cy.fixture('users').then((users) => {
      const existingUser = users.farmer
      const testPassword = this.credentials.testUsers.farmer.password

      cy.get('[data-cy="first-name-input"]').type('Nuevo')
      cy.get('[data-cy="last-name-input"]').type('Usuario')
      cy.get('[data-cy="email-input"]').type(existingUser.email)
      cy.get('[data-cy="password-input"]').type(testPassword)
      cy.get('[data-cy="confirm-password-input"]').type(testPassword)
      cy.get('[data-cy="role-select"]').select('farmer')
      cy.get('[data-cy="terms-checkbox"]').check()
      cy.get('[data-cy="register-button"]').click()

      cy.get('[data-cy="error-message"]')
        .should('be.visible')
        .and('contain', 'Email ya registrado')
    })
  })

  it('debe validar que las contraseñas coincidan', function() {
    const credentials = this.credentials

    cy.get('[data-cy="first-name-input"]').type('Juan')
    cy.get('[data-cy="last-name-input"]').type('Pérez')
    cy.get('[data-cy="email-input"]').type('juan@test.com')
    cy.get('[data-cy="password-input"]').type(credentials.strongPassword)
    cy.get('[data-cy="confirm-password-input"]').type(credentials.mismatchPassword)
    cy.get('[data-cy="role-select"]').select('farmer')
    cy.get('[data-cy="terms-checkbox"]').check()
    cy.get('[data-cy="register-button"]').click()

    cy.get('[data-cy="password-match-error"]')
      .should('be.visible')
      .and('contain', 'Las contraseñas no coinciden')
  })

  it('debe validar fortaleza de la contraseña', function() {
    const credentials = this.credentials
    const weakPasswords = credentials.weakPasswords

    for (const password of weakPasswords) {
      cy.get('[data-cy="password-input"]').clear().type(password)
      cy.get('[data-cy="password-strength"]')
        .should('be.visible')
        .and('contain', 'Contraseña débil')
    }

    // Verificar contraseña fuerte
    cy.get('[data-cy="password-input"]').clear().type(credentials.strongPassword)
    cy.get('[data-cy="password-strength"]')
      .should('be.visible')
      .and('contain', 'Contraseña fuerte')
  })

  it('debe requerir aceptar términos y condiciones', function() {
    const credentials = this.credentials.testUsers.farmer

    cy.get('[data-cy="first-name-input"]').type(credentials.firstName)
    cy.get('[data-cy="last-name-input"]').type(credentials.lastName)
    cy.get('[data-cy="email-input"]').type(credentials.email)
    cy.get('[data-cy="password-input"]').type(credentials.password)
    cy.get('[data-cy="confirm-password-input"]').type(credentials.confirmPassword)
    cy.get('[data-cy="role-select"]').select(credentials.role)
    // No marcar términos y condiciones
    cy.get('[data-cy="register-button"]').click()

    cy.get('[data-cy="terms-error"]')
      .should('be.visible')
      .and('contain', 'Debes aceptar los términos')
  })

  it('debe validar campos requeridos', () => {
    cy.get('[data-cy="register-button"]').click()

    cy.get('[data-cy="first-name-error"]').should('be.visible')
    cy.get('[data-cy="last-name-error"]').should('be.visible')
    cy.get('[data-cy="email-error"]').should('be.visible')
    cy.get('[data-cy="password-error"]').should('be.visible')
    cy.get('[data-cy="confirm-password-error"]').should('be.visible')
    cy.get('[data-cy="role-error"]').should('be.visible')
  })

  it('debe validar formato de email', () => {
    cy.get('[data-cy="email-input"]').type('email-invalido')
    cy.get('[data-cy="register-button"]').click()

    cy.get('[data-cy="email-error"]')
      .should('be.visible')
      .and('contain', 'Formato de email inválido')
  })

  it('debe mostrar/ocultar contraseña', function() {
    const credentials = this.credentials

    cy.get('[data-cy="password-input"]').type(credentials.strongPassword)
    cy.get('[data-cy="password-input"]').should('have.attr', 'type', 'password')

    cy.get('[data-cy="toggle-password"]').click()
    cy.get('[data-cy="password-input"]').should('have.attr', 'type', 'text')

    cy.get('[data-cy="toggle-password"]').click()
    cy.get('[data-cy="password-input"]').should('have.attr', 'type', 'password')
  })

  it('debe navegar al login desde el registro', () => {
    cy.get('[data-cy="login-link"]').click()
    cy.url().should('include', '/login')
  })

  it('debe validar longitud mínima de nombre', () => {
    cy.get('[data-cy="first-name-input"]').type('A')
    cy.get('[data-cy="register-button"]').click()
    
    cy.get('[data-cy="first-name-error"]')
      .should('be.visible')
      .and('contain', 'El nombre debe tener al menos')
  })

  it('debe validar caracteres especiales en nombre', () => {
    cy.get('[data-cy="first-name-input"]').type('Juan123')
    cy.get('[data-cy="register-button"]').click()
    
    cy.get('[data-cy="first-name-error"]')
      .should('be.visible')
      .and('contain', 'Solo se permiten letras')
  })

  it('debe validar formato de teléfono', () => {
    cy.get('[data-cy="phone-input"]').type('123')
    cy.get('[data-cy="register-button"]').click()
    
    cy.get('[data-cy="phone-error"]')
      .should('be.visible')
      .and('contain', 'Formato de teléfono inválido')
  })

  it('debe validar edad mínima', () => {
    const futureDate = new Date()
    futureDate.setFullYear(futureDate.getFullYear() - 10)
    const dateString = futureDate.toISOString().split('T')[0]
    
    cy.get('[data-cy="birthdate-input"]').type(dateString)
    cy.get('[data-cy="register-button"]').click()
    
    cy.get('[data-cy="birthdate-error"]')
      .should('be.visible')
      .and('contain', 'Debes tener al menos')
  })

  it('debe mostrar indicador de fortaleza de contraseña en tiempo real', () => {
    cy.get('[data-cy="password-input"]').type('weak')
    cy.get('[data-cy="password-strength"]').should('contain', 'Débil')
    
    cy.get('[data-cy="password-input"]').clear().type('Medium123')
    cy.get('[data-cy="password-strength"]').should('contain', 'Media')
    
    cy.get('[data-cy="password-input"]').clear().type('StrongPassword123!')
    cy.get('[data-cy="password-strength"]').should('contain', 'Fuerte')
  })

  it('debe validar que el email no esté en uso', () => {
    cy.intercept('POST', '/api/auth/register/', {
      statusCode: 400,
      body: { email: ['Este email ya está en uso'] }
    }).as('emailExists')
    
    cy.get('[data-cy="email-input"]').type('existing@example.com')
    cy.get('[data-cy="register-button"]').click()
    cy.wait('@emailExists')
    
    cy.get('[data-cy="email-error"]')
      .should('be.visible')
      .and('contain', 'ya está en uso')
  })

  it('debe mostrar mensaje de verificación de email después del registro', () => {
    cy.get('[data-cy="first-name-input"]').type('Juan')
    cy.get('[data-cy="last-name-input"]').type('Pérez')
    cy.get('[data-cy="email-input"]').type('juan@test.com')
    cy.get('[data-cy="password-input"]').type('Password123!')
    cy.get('[data-cy="confirm-password-input"]').type('Password123!')
    cy.get('[data-cy="role-select"]').select('farmer')
    cy.get('[data-cy="terms-checkbox"]').check()
    cy.get('[data-cy="register-button"]').click()
    
    cy.get('[data-cy="verification-message"]')
      .should('be.visible')
      .and('contain', 'Verifica tu email')
  })
})
