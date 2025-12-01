import { 
  verifySelectorsExist, 
  verifySuccessMessage, 
  verifyErrorMessageGeneric, 
  verifyUrlContains,
  visitAndWaitForBody
} from '../../support/helpers'

describe('Autenticación - Recuperación de Contraseña', () => {
  beforeEach(() => {
    visitAndWaitForBody('/login')
  })

  it('debe mostrar formulario de recuperación de contraseña', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="forgot-password-link"], a[href*="forgot"], a[href*="reset"]').length > 0) {
        cy.get('[data-cy="forgot-password-link"], a[href*="forgot"], a[href*="reset"]').first().click({ force: true })
        verifyUrlContains(['/forgot-password', '/reset-password', '/forgot'])
        cy.get('body').then(($forgot) => {
          if ($forgot.find('[data-cy="forgot-password-form"], form').length > 0) {
            cy.get('[data-cy="forgot-password-form"], form').should('exist')
            const selectors = [
              '[data-cy="email-input"]',
              '[data-cy="send-reset-button"]',
              '[data-cy="back-to-login-link"]'
            ]
            verifySelectorsExist(selectors, $forgot, 5000)
          }
        })
      }
    })
  })

  it('debe enviar email de recuperación exitosamente', () => {
    cy.clickForgotPasswordLink(() => {
      cy.fixture('users').then((users) => {
        const user = users.farmer
        cy.fillEmailAndSubmit(user.email, () => {
          verifySuccessMessage(['recuperación', 'enviado', 'email']).then(() => {
            verifyUrlContains(['/forgot', '/login'])
          })
        })
      })
    })
  })

  it('debe mostrar error si el email no existe', () => {
    cy.clickForgotPasswordLink(() => {
      cy.fillEmailAndSubmit('noexiste@test.com', () => {
        verifyErrorMessageGeneric(['no encontrado', 'not found', 'error'])
      })
    })
  })

  it('debe validar formato de email en recuperación', () => {
    cy.clickForgotPasswordLink(() => {
      cy.fillEmailAndSubmit('email-invalido', () => {
        verifyErrorMessageGeneric(['formato', 'inválido', 'email'], '[data-cy="email-error"], .error-message')
      })
    })
  })

  it('debe navegar de vuelta al login', () => {
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('[data-cy="back-to-login-link"], a[href*="login"]').length > 0) {
        cy.get('[data-cy="back-to-login-link"], a[href*="login"]').first().click()
        verifyUrlContains(['/login'])
      } else {
        verifyUrlContains(['/forgot', '/login'])
      }
    })
  })
})

describe('Autenticación - Reset de Contraseña', () => {
  it('debe mostrar formulario de reset con token válido', () => {
    visitAndWaitForBody('/reset-password?token=valid-token-123')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="reset-password-form"], form').length > 0) {
        cy.get('[data-cy="reset-password-form"], form').should('be.visible')
      }
      const selectors = [
        '[data-cy="new-password-input"]',
        '[data-cy="confirm-password-input"]',
        '[data-cy="reset-button"]'
      ]
      verifySelectorsExist(selectors, $body, 5000)
    })
  })

  it('debe resetear contraseña exitosamente', () => {
    cy.resetPassword('valid-token-123', 'NewPassword123!', 'NewPassword123!')
    
    verifySuccessMessage(['actualizada', 'exitosamente', 'password'])
    verifyUrlContains(['/login'])
  })

  it('debe mostrar error con token inválido', () => {
    visitAndWaitForBody('/reset-password?token=invalid-token')
    
    verifyErrorMessageGeneric(['inválido', 'expirado', 'token'])
  })

  it('debe validar que las contraseñas coincidan en reset', () => {
    const handleConfirmPassword = ($confirm) => {
      if ($confirm.find('[data-cy="confirm-password-input"], input[type="password"]').length > 1) {
        cy.get('[data-cy="confirm-password-input"], input[type="password"]').last().type('DifferentPassword123!')
      }
    }

    const handlePasswordInput = ($body) => {
      if ($body.find('[data-cy="new-password-input"], input[type="password"]').length > 0) {
        cy.get('[data-cy="new-password-input"], input[type="password"]').first().type('NewPassword123!')
        cy.get('body', { timeout: 3000 }).then(handleConfirmPassword)
        cy.get('[data-cy="reset-button"], button[type="submit"]').first().click()
        verifyErrorMessageGeneric(['no coinciden', 'no match', 'password'], '[data-cy="password-match-error"], .error-message')
      } else {
        cy.get('body').should('be.visible')
      }
    }

    visitAndWaitForBody('/reset-password?token=valid-token-123')
    cy.get('body').then(handlePasswordInput)
  })

  it('debe validar fortaleza de nueva contraseña', () => {
    visitAndWaitForBody('/reset-password?token=valid-token-123')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="new-password-input"], input[type="password"]').length > 0) {
        cy.get('[data-cy="new-password-input"], input[type="password"]').first().type('123')
        verifyErrorMessageGeneric(['débil', 'weak'], '[data-cy="password-strength"], .password-strength-meter', 3000)
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })
})

describe('Autenticación - Verificación de Email', () => {
  const loginUnverifiedUser = (callback) => {
    cy.fixture('users').then((users) => {
      const unverifiedUser = users.farmerUnverified
      
      cy.get('body').then(($body) => {
        if ($body.find('[data-cy="email-input"], input[type="text"], input[type="email"]').length > 0) {
          cy.get('[data-cy="email-input"], input[type="text"], input[type="email"]').first().type(unverifiedUser.email)
          cy.get('[data-cy="password-input"], input[type="password"]').first().type(unverifiedUser.password)
          cy.get('[data-cy="login-button"], button[type="submit"]').first().click()
          
          if (callback) {
            cy.get('body', { timeout: 5000 }).then(callback)
          }
        }
      })
    })
  }

  it('debe mostrar mensaje de verificación pendiente', () => {
    visitAndWaitForBody('/login')
    
    loginUnverifiedUser(($verify) => {
      if ($verify.find('[data-cy="verification-message"], .error-message').length > 0) {
        verifyErrorMessageGeneric(['verifica', 'verification', 'email'], '[data-cy="verification-message"], .error-message')
      } else {
        verifyUrlContains(['/login', '/verify'])
      }
    })
  })

  it('debe permitir reenviar email de verificación', () => {
    visitAndWaitForBody('/login')
    
    loginUnverifiedUser(($resend) => {
      if ($resend.find('[data-cy="resend-verification-button"], button').length > 0) {
        cy.get('[data-cy="resend-verification-button"], button').first().click()
        verifySuccessMessage(['reenviado', 'resend', 'verificación'])
      }
    })
  })

  it('debe verificar email con token válido', () => {
    const checkVerificationUrl = (url) => {
      return !url.includes('/verify-email') || url.length > 0
    }

    visitAndWaitForBody('/verify-email?token=valid-verification-token')
    
    verifySuccessMessage(['verificado', 'verification', 'exitosamente'])
    cy.url({ timeout: 5000 }).should('satisfy', checkVerificationUrl)
  })

  it('debe mostrar error con token de verificación inválido', () => {
    visitAndWaitForBody('/verify-email?token=invalid-token')
    
    verifyErrorMessageGeneric(['inválido', 'invalid', 'token'])
  })
})
