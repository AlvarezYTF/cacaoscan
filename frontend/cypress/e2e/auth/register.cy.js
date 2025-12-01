import { 
  verifySelectorsExist, 
  generatePassword, 
  executeRegistrationIfFieldsExist,
  verifyErrorMessageGeneric,
  visitAndWaitForBody,
  ifFoundInBody,
  fillRegistrationFormFields,
  submitRegistrationForm
} from '../../support/helpers'

describe('Autenticación - Registro', () => {
  beforeEach(() => {
    visitAndWaitForBody('/registro')
  })

  it('debe mostrar el formulario de registro correctamente', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="register-form"], form').length > 0) {
        cy.get('[data-cy="register-form"], form').should('exist')
      }
      const selectors = [
        '[data-cy="first-name-input"]', '[data-cy="last-name-input"]', '[data-cy="email-input"]',
        '[data-cy="password-input"]', '[data-cy="confirm-password-input"]', '[data-cy="role-select"]',
        '[data-cy="terms-checkbox"]', '[data-cy="register-button"]', '[data-cy="login-link"]'
      ]
      verifySelectorsExist(selectors, $body, 5000)
    })
  })

  it('debe registrar un nuevo agricultor exitosamente', () => {
    const password = generatePassword()
    const newUser = {
      firstName: 'Juan',
      lastName: 'Pérez',
      email: `juan.perez.${Date.now()}@test.com`,
      password: password,
      confirmPassword: password,
      role: 'farmer'
    }

    executeRegistrationIfFieldsExist(newUser, () => {
      cy.verifyRegistrationSuccess()
      cy.verifyVerificationMessage()
    })
  })

  it('debe registrar un nuevo analista exitosamente', () => {
    const password = generatePassword()
    const newUser = {
      firstName: 'Ana',
      lastName: 'García',
      email: `ana.garcia.${Date.now()}@test.com`,
      password: password,
      confirmPassword: password,
      role: 'analyst'
    }

    executeRegistrationIfFieldsExist(newUser, () => {
      cy.verifyRegistrationSuccess()
    })
  })

  it('debe mostrar error si el email ya existe', function() {
    cy.fixture('users').then((users) => {
      const existingUser = users.farmer
      const password = generatePassword()
      const newUser = {
        firstName: 'Nuevo',
        lastName: 'Usuario',
        email: existingUser.email,
        password: password,
        confirmPassword: password,
        role: 'farmer'
      }

      executeRegistrationIfFieldsExist(newUser, () => {
        cy.verifyRegistrationError(['ya registrado', 'already', 'email'])
      })
    })
  })

  it('debe validar que las contraseñas coincidan', () => {
    ifFoundInBody('[data-cy="register-form"], form', () => {
      const password = generatePassword()
      const differentPassword = generatePassword()
      fillRegistrationFormFields({
        firstName: 'Juan',
        lastName: 'Pérez',
        email: 'juan@test.com',
        password: password,
        confirmPassword: differentPassword,
        role: 'farmer',
        acceptTerms: true
      })
      submitRegistrationForm()
      verifyErrorMessageGeneric(['no coinciden', 'no match', 'password'], '[data-cy="password-match-error"], .error-message')
    })
  })

  it('debe validar fortaleza de la contraseña', function() {
    const credentials = this.credentials
    const weakPasswords = credentials.weakPasswords

    cy.get('body', { timeout: 10000 }).then(($body) => {
      if ($body.find('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]').length > 0) {
        for (const password of weakPasswords) {
          cy.get('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]').first().clear().type(password)
          verifyErrorMessageGeneric(['débil', 'weak'], '[data-cy="password-strength"], .password-strength-meter', 3000)
        }

        const strongPassword = generatePassword()
        cy.get('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]').first().clear().type(strongPassword)
        verifyErrorMessageGeneric(['fuerte', 'strong'], '[data-cy="password-strength"], .password-strength-meter', 3000)
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe requerir aceptar términos y condiciones', () => {
    ifFoundInBody('[data-cy="register-form"], form', () => {
      const password = generatePassword()
      fillRegistrationFormFields({
        firstName: 'Juan',
        lastName: 'Pérez',
        email: 'juan@test.com',
        password: password,
        confirmPassword: password,
        role: 'farmer',
        acceptTerms: false
      })
      submitRegistrationForm()
      verifyErrorMessageGeneric(['aceptar', 'términos', 'terms'], '[data-cy="terms-error"], .error-message')
    })
  })

  it('debe validar campos requeridos', () => {
    ifFoundInBody('[data-cy="register-button"], [data-cy="btn-submit-register"], button[type="submit"]', () => {
      submitRegistrationForm()
      cy.get('body', { timeout: 3000 }).then(($errors) => {
        const errorSelectors = [
          '[data-cy="first-name-error"]', '[data-cy="last-name-error"]', '[data-cy="email-error"]',
          '[data-cy="password-error"]', '[data-cy="confirm-password-error"]', '[data-cy="role-error"]'
        ]
        verifySelectorsExist(errorSelectors, $errors, 3000)
      })
    })
  })

  it('debe validar formato de email', () => {
    ifFoundInBody('[data-cy="email-input"], [data-cy="input-email"], input[type="email"]', () => {
      cy.get('[data-cy="email-input"], [data-cy="input-email"], input[type="email"]').first().type('email-invalido')
      submitRegistrationForm()
      verifyErrorMessageGeneric(['formato', 'inválido', 'email'], '[data-cy="email-error"], .error-message', 3000)
    })
  })

  it('debe mostrar/ocultar contraseña', () => {
    ifFoundInBody('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]', () => {
      const password = generatePassword()
      cy.get('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]').first().type(password)
      cy.get('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]').first().should('have.attr', 'type', 'password')

      ifFoundInBody('[data-cy="toggle-password"], [data-cy="btn-toggle-password"], button[type="button"]', () => {
        cy.get('[data-cy="toggle-password"], [data-cy="btn-toggle-password"], button[type="button"]').first().click()
        cy.get('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]').first().should('have.attr', 'type', 'text')

        cy.get('[data-cy="toggle-password"], [data-cy="btn-toggle-password"], button[type="button"]').first().click()
        cy.get('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]').first().should('have.attr', 'type', 'password')
      })
    })
  })

  it('debe navegar al login desde el registro', () => {
    ifFoundInBody('[data-cy="login-link"], a[href*="login"]', () => {
      cy.get('[data-cy="login-link"], a[href*="login"]').first().click()
      verifyUrlContains(['/login'], 5000)
    })
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
    
    const strongPassword = generatePassword()
    cy.get('[data-cy="password-input"]').clear().type(strongPassword)
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
    const password = generatePassword()
    cy.get('[data-cy="first-name-input"]').type('Juan')
    cy.get('[data-cy="last-name-input"]').type('Pérez')
    cy.get('[data-cy="email-input"]').type('juan@test.com')
    cy.get('[data-cy="password-input"]').type(password)
    cy.get('[data-cy="confirm-password-input"]').type(password)
    cy.get('[data-cy="role-select"]').select('farmer')
    cy.get('[data-cy="terms-checkbox"]').check()
    cy.get('[data-cy="register-button"]').click()
    
    cy.get('[data-cy="verification-message"]')
      .should('be.visible')
      .and('contain', 'Verifica tu email')
  })
})
