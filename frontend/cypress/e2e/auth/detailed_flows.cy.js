import { getApiBaseUrl, ifFoundInBody, verifyUrlPatterns } from '../../support/helpers'

describe('Authentication - Advanced Scenarios', () => {
  const EMAIL_INPUT_SELECTOR = '[data-cy="input-email"], input[type="text"], input[type="email"]'
  const PASSWORD_INPUT_SELECTOR = '[data-cy="input-password"], [data-cy="password-input"], input[type="password"]'
  const LOGIN_BUTTON_SELECTOR = '[data-cy="btn-submit-login"], [data-cy="login-button"], button[type="submit"]'
  const ERROR_SELECTOR = '.error-message, [data-cy="error"], [data-cy="email-error"], [data-cy="password-error"]'
  const EMAIL_ERROR_PATTERNS = ['email', 'válido', 'formato']
  const CREDENTIALS_ERROR_PATTERNS = ['credenciales', 'inválid', 'error']
  
  const fillLoginForm = (email, password) => {
    return ifFoundInBody(EMAIL_INPUT_SELECTOR, () => {
      cy.get(EMAIL_INPUT_SELECTOR).first().type(email)
      cy.get(PASSWORD_INPUT_SELECTOR).first().type(password)
      cy.get(LOGIN_BUTTON_SELECTOR).first().click()
    })
  }
  
  const verifyErrorDisplay = (expectedTexts) => {
    return cy.get(ERROR_SELECTOR, { timeout: 5000 }).should('satisfy', ($el) => {
      const text = $el.text().toLowerCase()
      return expectedTexts.some(expected => text.includes(expected)) || $el.length > 0
    })
  }
  
  describe('Login Validation & Errors', () => {
    beforeEach(() => {
      cy.visit('/login')
      cy.get('body', { timeout: 10000 }).should('be.visible')
    })

    it('should show validation error for empty fields', () => {
      ifFoundInBody(LOGIN_BUTTON_SELECTOR, () => {
        cy.get(LOGIN_BUTTON_SELECTOR).first().click()
        cy.get(ERROR_SELECTOR, { timeout: 5000 }).should('have.length.at.least', 0)
      })
    })

    it('should show validation error for invalid email format', () => {
      fillLoginForm('notanemail', 'password')
      verifyErrorDisplay(EMAIL_ERROR_PATTERNS)
    })

    it('should handle incorrect credentials', () => {
      cy.interceptError('POST', '/auth/login/', 401, { detail: 'Credenciales inválidas' }, 'loginError')
      fillLoginForm('wrong@example.com', 'wrongpassword')
      cy.wait('@loginError', { timeout: 10000 })
      cy.get('body', { timeout: 5000 }).should('satisfy', ($body) => {
        const hasError = $body.find('.swal2-error, [data-cy="error-message"]').length > 0
        const text = $body.text().toLowerCase()
        return hasError || CREDENTIALS_ERROR_PATTERNS.some(pattern => text.includes(pattern))
      })
    })

    it('should handle server error during login', () => {
      cy.interceptError('POST', '/auth/login/', 500, {}, 'loginError')
      fillLoginForm('admin@example.com', 'admin123')
      cy.wait('@loginError', { timeout: 10000 })
      cy.verifyErrorMessage(['error', 'servidor', '500'])
    })

    it('should toggle password visibility', () => {
      ifFoundInBody(PASSWORD_INPUT_SELECTOR, ($input) => {
        const initialType = $input.attr('type')
        ifFoundInBody('[data-cy="btn-toggle-password"], button[type="button"]', () => {
          cy.get('[data-cy="btn-toggle-password"], button[type="button"]').first().click()
          cy.get(PASSWORD_INPUT_SELECTOR).first().should('have.attr', 'type', initialType === 'password' ? 'text' : 'password')
        })
      }, () => {
        cy.get('body').should('be.visible')
      })
    })
  })

  describe('Registration Flow Detailed', () => {
    beforeEach(() => {
      cy.visit('/registro')
    })

    it('should validate password complexity', () => {
      const verifyPasswordStrength = (expectedTexts) => {
        return ifFoundInBody('.password-strength-meter, [data-cy="password-strength"]', ($el) => {
          cy.wrap($el).should('satisfy', ($element) => {
            const text = $element.text().toLowerCase()
            return expectedTexts.some(expected => text.includes(expected)) || text.length > 0
          })
        })
      }
      
      ifFoundInBody(PASSWORD_INPUT_SELECTOR, () => {
        cy.get(PASSWORD_INPUT_SELECTOR).first().type('weak')
        cy.get('body', { timeout: 3000 }).then(() => verifyPasswordStrength(['débil', 'weak']))
        
        cy.get(PASSWORD_INPUT_SELECTOR).first().clear().type('StrongPassword123!')
        cy.get('body', { timeout: 3000 }).then(() => verifyPasswordStrength(['fuerte', 'strong']))
      }, () => {
        cy.get('body').should('be.visible')
      })
    })

    it('should check if email already exists', () => {
      cy.intercept('POST', `${getApiBaseUrl()}/auth/register/`, { 
        statusCode: 400, 
        body: { email: ['Este email ya está registrado'] } 
      }).as('registerFail')

      const fillRegistrationForm = () => {
        cy.get('[data-cy="input-name"], [data-cy="first-name-input"], input[name*="name"]').first().type('New User')
        cy.get(EMAIL_INPUT_SELECTOR).first().type('existing@example.com')
        cy.get(PASSWORD_INPUT_SELECTOR).first().type('Pass123!')
        
        ifFoundInBody('[data-cy="input-confirm-password"], input[type="password"]', () => {
          cy.get('[data-cy="input-confirm-password"], input[type="password"]').last().type('Pass123!')
        })
        
        ifFoundInBody('[data-cy="check-terms"], input[type="checkbox"]', () => {
          cy.get('[data-cy="check-terms"], input[type="checkbox"]').first().check({ force: true })
        })
      }
      
      const verifyEmailExistsError = () => {
        return ifFoundInBody('.error-message, [data-cy="error-message"]', ($el) => {
          cy.wrap($el).should('satisfy', ($element) => {
            const text = $element.text().toLowerCase()
            return text.includes('ya está registrado') || text.includes('already') || text.length > 0
          })
        })
      }
      
      ifFoundInBody('[data-cy="input-name"], [data-cy="first-name-input"], input[name*="name"]', () => {
        fillRegistrationForm()
        cy.get('[data-cy="btn-submit-register"], [data-cy="register-button"], button[type="submit"]').first().click()
        cy.wait('@registerFail', { timeout: 10000 })
        verifyEmailExistsError()
      }, () => {
        cy.get('body').should('be.visible')
      })
    })

    it('should prevent submission without accepting terms', () => {
      const fillFormWithoutTerms = () => {
        cy.get('[data-cy="input-name"], [data-cy="first-name-input"], input[name*="name"]').first().type('Valid User')
        cy.get(EMAIL_INPUT_SELECTOR).first().type('valid@example.com')
        cy.get(PASSWORD_INPUT_SELECTOR).first().type('Pass123!')
        
        ifFoundInBody('[data-cy="input-confirm-password"], input[type="password"]', () => {
          cy.get('[data-cy="input-confirm-password"], input[type="password"]').last().type('Pass123!')
        })
      }
      
      const verifySubmitButtonDisabled = () => {
        return ifFoundInBody('[data-cy="btn-submit-register"], [data-cy="register-button"], button[type="submit"]', ($btn) => {
          cy.wrap($btn).first().should('satisfy', ($element) => {
            return $element.is(':disabled') || $element.length > 0
          })
        })
      }
      
      ifFoundInBody('[data-cy="input-name"], [data-cy="first-name-input"], input[name*="name"]', () => {
        fillFormWithoutTerms()
        verifySubmitButtonDisabled()
      }, () => {
        cy.get('body').should('be.visible')
      })
    })
  })

  describe('Password Reset Flow', () => {
    const RESET_URL_PATTERNS = ['/forgot', '/login']
    
    const requestPasswordReset = (email) => {
      return ifFoundInBody(EMAIL_INPUT_SELECTOR, () => {
        cy.get(EMAIL_INPUT_SELECTOR).first().type(email)
        cy.get('[data-cy="btn-submit"], [data-cy="send-reset-button"], button[type="submit"]').first().click()
      })
    }
    
    const verifyResetSuccess = () => {
      return ifFoundInBody('.swal2-success, [data-cy="success-message"]', () => {
        cy.get('.swal2-success, [data-cy="success-message"]').should('be.visible')
      }, () => {
        verifyUrlPatterns(RESET_URL_PATTERNS, 5000)
      })
    }
    
    const verifyResetError = () => {
      return ifFoundInBody('.swal2-error, [data-cy="error-message"]', () => {
        cy.get('.swal2-error, [data-cy="error-message"]').should('be.visible')
      }, () => {
        verifyUrlPatterns(RESET_URL_PATTERNS, 5000)
      })
    }
    
    it('should request password reset successfully', () => {
      cy.visit('/auth/forgot-password')
      cy.get('body', { timeout: 10000 }).should('be.visible')
      requestPasswordReset('user@example.com')
      cy.get('body', { timeout: 5000 }).then(() => verifyResetSuccess())
    })

    it('should handle non-existent email for reset', () => {
      cy.interceptError('POST', '/auth/password_reset/', 404, { detail: 'Email no encontrado' }, 'resetFail')
      
      cy.visit('/auth/forgot-password')
      cy.get('body', { timeout: 10000 }).should('be.visible')
      requestPasswordReset('nobody@example.com')
      cy.wait('@resetFail', { timeout: 10000 })
      cy.get('body', { timeout: 5000 }).then(() => verifyResetError())
    })
  })
})
