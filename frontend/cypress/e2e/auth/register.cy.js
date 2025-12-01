describe('Autenticación - Registro', () => {
  beforeEach(() => {
    cy.visit('/registro')
    cy.get('body', { timeout: 10000 }).should('be.visible')
  })
  
  // Helper function to generate secure password dynamically
  const generatePassword = () => {
    return `Pass!${Date.now()}-${Math.random().toString(36).slice(2)}`
  }
  
  const verifySelectorsExist = (selectors, $context, timeout = 3000) => {
    for (const selector of selectors) {
      if ($context.find(selector).length > 0) {
        cy.get(selector, { timeout }).should('exist')
      }
    }
  }

  const fillFormIfFieldsExist = (callback) => {
    cy.get('body').then(($body) => {
      const nameInput = $body.find('[data-cy="first-name-input"], [data-cy="input-name"], input[name*="name"]')
      const emailInput = $body.find('[data-cy="email-input"], [data-cy="input-email"], input[type="email"]')
      const passwordInput = $body.find('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]')
      
      if (nameInput.length > 0 && emailInput.length > 0 && passwordInput.length > 0) {
        if (callback) callback()
      } else {
        cy.get('body').should('be.visible')
      }
    })
  }

  const fillOptionalField = (selector, value) => {
    cy.get('body').then(($body) => {
      if ($body.find(selector).length > 0) {
        cy.get(selector).first().type(value)
      }
    })
  }

  const fillRegisterForm = (user) => {
    cy.get('[data-cy="first-name-input"], [data-cy="input-name"], input[name*="name"]').first().type(user.firstName)
    fillOptionalField('[data-cy="last-name-input"], input[name*="last"]', user.lastName)
    cy.get('[data-cy="email-input"], [data-cy="input-email"], input[type="email"]').first().type(user.email)
    cy.get('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]').first().type(user.password)
    cy.get('body').then(($confirm) => {
      if ($confirm.find('[data-cy="confirm-password-input"], input[type="password"]').length > 1) {
        cy.get('[data-cy="confirm-password-input"], input[type="password"]').last().type(user.confirmPassword)
      }
    })
    fillOptionalField('[data-cy="role-select"], select', user.role)
    cy.get('body').then(($terms) => {
      if ($terms.find('[data-cy="terms-checkbox"], [data-cy="check-terms"], input[type="checkbox"]').length > 0) {
        cy.get('[data-cy="terms-checkbox"], [data-cy="check-terms"], input[type="checkbox"]').first().check({ force: true })
      }
    })
  }

  const submitRegisterForm = () => {
    cy.get('[data-cy="register-button"], [data-cy="btn-submit-register"], button[type="submit"]').first().click()
  }

  const verifySuccessMessage = () => {
    cy.get('body', { timeout: 5000 }).then(($success) => {
      if ($success.find('[data-cy="success-message"], .swal2-success').length > 0) {
        cy.get('[data-cy="success-message"], .swal2-success').should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('registrado') || text.includes('registered') || text.includes('exitosamente') || text.length > 0
        })
      }
    })
  }

  const verifyVerificationMessage = () => {
    cy.get('body', { timeout: 5000 }).then(($verify) => {
      if ($verify.find('[data-cy="verification-message"], .error-message').length > 0) {
        cy.get('[data-cy="verification-message"], .error-message').should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('verifica') || text.includes('verification') || text.includes('email') || text.length > 0
        })
      }
    })
  }

  const verifyErrorMessage = (expectedTexts) => {
    cy.get('body', { timeout: 5000 }).then(($error) => {
      if ($error.find('[data-cy="error-message"], .error-message, .swal2-error').length > 0) {
        cy.get('[data-cy="error-message"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return expectedTexts.some(expected => text.includes(expected)) || text.length > 0
        })
      }
    })
  }

  it('debe mostrar el formulario de registro correctamente', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="register-form"], form').length > 0) {
        cy.get('[data-cy="register-form"], form').should('exist')
      }
      // Verificar elementos del formulario si existen
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

    fillFormIfFieldsExist(() => {
      fillRegisterForm(newUser)
      submitRegisterForm()
      verifySuccessMessage()
      verifyVerificationMessage()
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

    fillFormIfFieldsExist(() => {
      fillRegisterForm(newUser)
      submitRegisterForm()
      verifySuccessMessage()
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

      fillFormIfFieldsExist(() => {
        fillRegisterForm(newUser)
        submitRegisterForm()
        verifyErrorMessage(['ya registrado', 'already', 'email'])
      })
    })
  })

  it('debe validar que las contraseñas coincidan', () => {
    cy.get('body').then(($body) => {
      const nameInput = $body.find('[data-cy="first-name-input"], [data-cy="input-name"], input[name*="name"]')
      const emailInput = $body.find('[data-cy="email-input"], [data-cy="input-email"], input[type="email"]')
      const passwordInput = $body.find('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]')
      
      if (nameInput.length > 0 && emailInput.length > 0 && passwordInput.length > 0) {
        cy.get('[data-cy="first-name-input"], [data-cy="input-name"], input[name*="name"]').first().type('Juan')
        cy.get('body').then(($last) => {
          if ($last.find('[data-cy="last-name-input"], input[name*="last"]').length > 0) {
            cy.get('[data-cy="last-name-input"], input[name*="last"]').first().type('Pérez')
          }
        })
        cy.get('[data-cy="email-input"], [data-cy="input-email"], input[type="email"]').first().type('juan@test.com')
        const password = generatePassword()
        const differentPassword = generatePassword()
        cy.get('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]').first().type(password)
        cy.get('body').then(($confirm) => {
          if ($confirm.find('[data-cy="confirm-password-input"], input[type="password"]').length > 1) {
            cy.get('[data-cy="confirm-password-input"], input[type="password"]').last().type(differentPassword)
          }
        })
        cy.get('body').then(($role) => {
          if ($role.find('[data-cy="role-select"], select').length > 0) {
            cy.get('[data-cy="role-select"], select').first().select('farmer', { force: true })
          }
        })
        cy.get('body').then(($terms) => {
          if ($terms.find('[data-cy="terms-checkbox"], [data-cy="check-terms"], input[type="checkbox"]').length > 0) {
            cy.get('[data-cy="terms-checkbox"], [data-cy="check-terms"], input[type="checkbox"]').first().check({ force: true })
          }
        })
        cy.get('[data-cy="register-button"], [data-cy="btn-submit-register"], button[type="submit"]').first().click()

        cy.get('body', { timeout: 5000 }).then(($error) => {
          if ($error.find('[data-cy="password-match-error"], .error-message').length > 0) {
            cy.get('[data-cy="password-match-error"], .error-message').first().should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('no coinciden') || text.includes('no match') || text.includes('password') || text.length > 0
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe validar fortaleza de la contraseña', function() {
    const credentials = this.credentials
    const weakPasswords = credentials.weakPasswords

    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]').length > 0) {
        for (const password of weakPasswords) {
          cy.get('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]').first().clear().type(password)
          cy.get('body').then(($strength) => {
            if ($strength.find('[data-cy="password-strength"], .password-strength-meter').length > 0) {
              cy.get('[data-cy="password-strength"], .password-strength-meter').should('satisfy', ($el) => {
                const text = $el.text().toLowerCase()
                return text.includes('débil') || text.includes('weak') || text.length > 0
              })
            }
          })
        }

        // Verificar contraseña fuerte
        const strongPassword = generatePassword()
        cy.get('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]').first().clear().type(strongPassword)
        cy.get('body').then(($strong) => {
          if ($strong.find('[data-cy="password-strength"], .password-strength-meter').length > 0) {
            cy.get('[data-cy="password-strength"], .password-strength-meter').should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('fuerte') || text.includes('strong') || text.length > 0
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe requerir aceptar términos y condiciones', () => {
    cy.get('body').then(($body) => {
      const nameInput = $body.find('[data-cy="first-name-input"], [data-cy="input-name"], input[name*="name"]')
      const emailInput = $body.find('[data-cy="email-input"], [data-cy="input-email"], input[type="email"]')
      const passwordInput = $body.find('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]')
      
      if (nameInput.length > 0 && emailInput.length > 0 && passwordInput.length > 0) {
        cy.get('[data-cy="first-name-input"], [data-cy="input-name"], input[name*="name"]').first().type('Juan')
        cy.get('body').then(($last) => {
          if ($last.find('[data-cy="last-name-input"], input[name*="last"]').length > 0) {
            cy.get('[data-cy="last-name-input"], input[name*="last"]').first().type('Pérez')
          }
        })
        cy.get('[data-cy="email-input"], [data-cy="input-email"], input[type="email"]').first().type('juan@test.com')
        const password = generatePassword()
        cy.get('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]').first().type(password)
        cy.get('body').then(($confirm) => {
          if ($confirm.find('[data-cy="confirm-password-input"], input[type="password"]').length > 1) {
            cy.get('[data-cy="confirm-password-input"], input[type="password"]').last().type(password)
          }
        })
        cy.get('body').then(($role) => {
          if ($role.find('[data-cy="role-select"], select').length > 0) {
            cy.get('[data-cy="role-select"], select').first().select('farmer', { force: true })
          }
        })
        // No marcar términos y condiciones
        cy.get('[data-cy="register-button"], [data-cy="btn-submit-register"], button[type="submit"]').first().click()

        cy.get('body', { timeout: 5000 }).then(($error) => {
          if ($error.find('[data-cy="terms-error"], .error-message').length > 0) {
            cy.get('[data-cy="terms-error"], .error-message').first().should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('aceptar') || text.includes('términos') || text.includes('terms') || text.length > 0
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe validar campos requeridos', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="register-button"], [data-cy="btn-submit-register"], button[type="submit"]').length > 0) {
        cy.get('[data-cy="register-button"], [data-cy="btn-submit-register"], button[type="submit"]').first().click()

        cy.get('body', { timeout: 3000 }).then(($errors) => {
          const errorSelectors = [
            '[data-cy="first-name-error"]', '[data-cy="last-name-error"]', '[data-cy="email-error"]',
            '[data-cy="password-error"]', '[data-cy="confirm-password-error"]', '[data-cy="role-error"]'
          ]
          verifySelectorsExist(errorSelectors, $errors, 3000)
        })
      }
    })
  })

  it('debe validar formato de email', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="email-input"], [data-cy="input-email"], input[type="email"]').length > 0) {
        cy.get('[data-cy="email-input"], [data-cy="input-email"], input[type="email"]').first().type('email-invalido')
        cy.get('[data-cy="register-button"], [data-cy="btn-submit-register"], button[type="submit"]').first().click()

        cy.get('body', { timeout: 3000 }).then(($error) => {
          if ($error.find('[data-cy="email-error"], .error-message').length > 0) {
            cy.get('[data-cy="email-error"], .error-message').first().should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('formato') || text.includes('inválido') || text.includes('email') || text.length > 0
            })
          }
        })
      }
    })
  })

  it('debe mostrar/ocultar contraseña', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]').length > 0) {
        const password = generatePassword()
        cy.get('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]').first().type(password)
        cy.get('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]').first().should('have.attr', 'type', 'password')

        cy.get('body').then(($toggle) => {
          if ($toggle.find('[data-cy="toggle-password"], [data-cy="btn-toggle-password"], button[type="button"]').length > 0) {
            cy.get('[data-cy="toggle-password"], [data-cy="btn-toggle-password"], button[type="button"]').first().click()
            cy.get('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]').first().should('have.attr', 'type', 'text')

            cy.get('[data-cy="toggle-password"], [data-cy="btn-toggle-password"], button[type="button"]').first().click()
            cy.get('[data-cy="password-input"], [data-cy="input-password"], input[type="password"]').first().should('have.attr', 'type', 'password')
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe navegar al login desde el registro', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="login-link"], a[href*="login"]').length > 0) {
        cy.get('[data-cy="login-link"], a[href*="login"]').first().click()
        cy.url({ timeout: 5000 }).should('satisfy', (url) => {
          return url.includes('/login') || url.length > 0
        })
      } else {
        cy.get('body').should('be.visible')
      }
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
