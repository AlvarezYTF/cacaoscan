describe('Autenticación - Registro', () => {
  beforeEach(() => {
    cy.visit('/registro')
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

  it('debe registrar un nuevo agricultor exitosamente', () => {
    const newUser = {
      firstName: 'Juan',
      lastName: 'Pérez',
      email: 'juan.perez@test.com',
      password: 'Password123!',
      confirmPassword: 'Password123!',
      role: 'farmer'
    }

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

  it('debe registrar un nuevo analista exitosamente', () => {
    const newUser = {
      firstName: 'Ana',
      lastName: 'García',
      email: 'ana.garcia@test.com',
      password: 'Password123!',
      confirmPassword: 'Password123!',
      role: 'analyst'
    }

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

  it('debe mostrar error si el email ya existe', () => {
    cy.fixture('users').then((users) => {
      const existingUser = users.farmer

      cy.get('[data-cy="first-name-input"]').type('Nuevo')
      cy.get('[data-cy="last-name-input"]').type('Usuario')
      cy.get('[data-cy="email-input"]').type(existingUser.email)
      cy.get('[data-cy="password-input"]').type('Password123!')
      cy.get('[data-cy="confirm-password-input"]').type('Password123!')
      cy.get('[data-cy="role-select"]').select('farmer')
      cy.get('[data-cy="terms-checkbox"]').check()
      cy.get('[data-cy="register-button"]').click()

      cy.get('[data-cy="error-message"]')
        .should('be.visible')
        .and('contain', 'Email ya registrado')
    })
  })

  it('debe validar que las contraseñas coincidan', () => {
    cy.get('[data-cy="first-name-input"]').type('Juan')
    cy.get('[data-cy="last-name-input"]').type('Pérez')
    cy.get('[data-cy="email-input"]').type('juan@test.com')
    cy.get('[data-cy="password-input"]').type('Password123!')
    cy.get('[data-cy="confirm-password-input"]').type('DifferentPassword123!')
    cy.get('[data-cy="role-select"]').select('farmer')
    cy.get('[data-cy="terms-checkbox"]').check()
    cy.get('[data-cy="register-button"]').click()

    cy.get('[data-cy="password-match-error"]')
      .should('be.visible')
      .and('contain', 'Las contraseñas no coinciden')
  })

  it('debe validar fortaleza de la contraseña', () => {
    const weakPasswords = ['123', 'password', '12345678']

    weakPasswords.forEach(password => {
      cy.get('[data-cy="password-input"]').clear().type(password)
      cy.get('[data-cy="password-strength"]')
        .should('be.visible')
        .and('contain', 'Contraseña débil')
    })

    // Verificar contraseña fuerte
    cy.get('[data-cy="password-input"]').clear().type('StrongPassword123!')
    cy.get('[data-cy="password-strength"]')
      .should('be.visible')
      .and('contain', 'Contraseña fuerte')
  })

  it('debe requerir aceptar términos y condiciones', () => {
    cy.get('[data-cy="first-name-input"]').type('Juan')
    cy.get('[data-cy="last-name-input"]').type('Pérez')
    cy.get('[data-cy="email-input"]').type('juan@test.com')
    cy.get('[data-cy="password-input"]').type('Password123!')
    cy.get('[data-cy="confirm-password-input"]').type('Password123!')
    cy.get('[data-cy="role-select"]').select('farmer')
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

  it('debe mostrar/ocultar contraseña', () => {
    cy.get('[data-cy="password-input"]').type('Password123!')
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
})
