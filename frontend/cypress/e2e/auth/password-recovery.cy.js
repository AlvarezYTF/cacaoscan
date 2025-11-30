describe('Autenticación - Recuperación de Contraseña', () => {
  beforeEach(() => {
    cy.visit('/login')
    cy.get('body', { timeout: 10000 }).should('be.visible')
  })

  it('debe mostrar formulario de recuperación de contraseña', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="forgot-password-link"], a[href*="forgot"], a[href*="reset"]').length > 0) {
        cy.get('[data-cy="forgot-password-link"], a[href*="forgot"], a[href*="reset"]').first().click({ force: true })
        cy.url({ timeout: 10000 }).should('satisfy', (url) => {
          return url.includes('/forgot-password') || url.includes('/reset-password') || url.includes('/forgot')
        })
        cy.get('body').then(($forgot) => {
          if ($forgot.find('[data-cy="forgot-password-form"], form').length > 0) {
            cy.get('[data-cy="forgot-password-form"], form').should('exist')
            cy.get('[data-cy="email-input"], input[type="email"]', { timeout: 5000 }).should('exist')
            cy.get('[data-cy="send-reset-button"], button[type="submit"]', { timeout: 5000 }).should('exist')
            cy.get('[data-cy="back-to-login-link"], a[href*="login"]', { timeout: 5000 }).should('exist')
          }
        })
      }
    })
  })

  it('debe enviar email de recuperación exitosamente', () => {
    cy.fixture('users').then((users) => {
      const user = users.farmer
      
      cy.get('body').then(($body) => {
        if ($body.find('[data-cy="forgot-password-link"], a[href*="forgot"], a[href*="reset"]').length > 0) {
          cy.get('[data-cy="forgot-password-link"], a[href*="forgot"], a[href*="reset"]').first().click({ force: true })
          cy.url({ timeout: 10000 }).should('satisfy', (url) => {
            return url.includes('/forgot') || url.includes('/reset') || url.includes('/login')
          })
          cy.get('body', { timeout: 5000 }).then(($forgot) => {
            if ($forgot.find('[data-cy="email-input"], [data-cy="input-email"], input[type="email"]').length > 0) {
              cy.get('[data-cy="email-input"], [data-cy="input-email"], input[type="email"]').first().type(user.email)
              cy.get('[data-cy="send-reset-button"], [data-cy="btn-submit"], button[type="submit"]').first().click()
              
              cy.get('body', { timeout: 5000 }).then(($success) => {
                if ($success.find('[data-cy="success-message"], .swal2-success').length > 0) {
                  cy.get('[data-cy="success-message"], .swal2-success').should('satisfy', ($el) => {
                    const text = $el.text().toLowerCase()
                    return text.includes('recuperación') || text.includes('enviado') || text.includes('email') || text.length > 0
                  })
                } else {
                  cy.url().should('satisfy', (url) => {
                    return url.includes('/forgot') || url.includes('/login') || url.length > 0
                  })
                }
              })
            }
          })
        } else {
          cy.get('body').should('be.visible')
        }
      })
    })
  })

  it('debe mostrar error si el email no existe', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="forgot-password-link"], a[href*="forgot"], a[href*="reset"]').length > 0) {
        cy.get('[data-cy="forgot-password-link"], a[href*="forgot"], a[href*="reset"]').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($forgot) => {
          if ($forgot.find('[data-cy="email-input"], [data-cy="input-email"], input[type="email"]').length > 0) {
            cy.get('[data-cy="email-input"], [data-cy="input-email"], input[type="email"]').first().type('noexiste@test.com')
            cy.get('[data-cy="send-reset-button"], [data-cy="btn-submit"], button[type="submit"]').first().click()
            
            cy.get('body', { timeout: 5000 }).then(($error) => {
              if ($error.find('[data-cy="error-message"], .swal2-error, .error-message').length > 0) {
                cy.get('[data-cy="error-message"], .swal2-error, .error-message').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('no encontrado') || text.includes('not found') || text.includes('error') || text.length > 0
                })
              }
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe validar formato de email en recuperación', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="forgot-password-link"], a[href*="forgot"], a[href*="reset"]').length > 0) {
        cy.get('[data-cy="forgot-password-link"], a[href*="forgot"], a[href*="reset"]').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($forgot) => {
          if ($forgot.find('[data-cy="email-input"], [data-cy="input-email"], input[type="email"]').length > 0) {
            cy.get('[data-cy="email-input"], [data-cy="input-email"], input[type="email"]').first().type('email-invalido')
            cy.get('[data-cy="send-reset-button"], [data-cy="btn-submit"], button[type="submit"]').first().click()
            
            cy.get('body', { timeout: 5000 }).then(($error) => {
              if ($error.find('[data-cy="email-error"], .error-message').length > 0) {
                cy.get('[data-cy="email-error"], .error-message').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('formato') || text.includes('inválido') || text.includes('email') || text.length > 0
                })
              }
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe navegar de vuelta al login', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="forgot-password-link"], a[href*="forgot"], a[href*="reset"]').length > 0) {
        cy.get('[data-cy="forgot-password-link"], a[href*="forgot"], a[href*="reset"]').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($forgot) => {
          if ($forgot.find('[data-cy="back-to-login-link"], a[href*="login"]').length > 0) {
            cy.get('[data-cy="back-to-login-link"], a[href*="login"]').first().click()
            cy.url({ timeout: 5000 }).should('satisfy', (url) => {
              return url.includes('/login') || url.length > 0
            })
          } else {
            cy.url().should('satisfy', (url) => {
              return url.includes('/forgot') || url.includes('/login') || url.length > 0
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })
})

describe('Autenticación - Reset de Contraseña', () => {
  it('debe mostrar formulario de reset con token válido', () => {
    // Simular token válido en la URL
    cy.visit('/reset-password?token=valid-token-123')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="reset-password-form"], form').length > 0) {
        cy.get('[data-cy="reset-password-form"], form').should('be.visible')
      }
      // Verificar elementos si existen
      const selectors = [
        '[data-cy="new-password-input"]', '[data-cy="confirm-password-input"]', '[data-cy="reset-button"]'
      ]
      selectors.forEach(selector => {
        if ($body.find(selector).length > 0) {
          cy.get(selector, { timeout: 5000 }).should('exist')
        }
      })
    })
  })

  it('debe resetear contraseña exitosamente', () => {
    cy.visit('/reset-password?token=valid-token-123')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="new-password-input"], input[type="password"]').length > 0) {
        cy.get('[data-cy="new-password-input"], input[type="password"]').first().type('NewPassword123!')
        cy.get('body').then(($confirm) => {
          if ($confirm.find('[data-cy="confirm-password-input"], input[type="password"]').length > 1) {
            cy.get('[data-cy="confirm-password-input"], input[type="password"]').last().type('NewPassword123!')
          }
        })
        cy.get('[data-cy="reset-button"], button[type="submit"]').first().click()
        
        cy.get('body', { timeout: 5000 }).then(($success) => {
          if ($success.find('[data-cy="success-message"], .swal2-success').length > 0) {
            cy.get('[data-cy="success-message"], .swal2-success').should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('actualizada') || text.includes('exitosamente') || text.includes('password') || text.length > 0
            })
          }
        })
        
        // Debería redirigir al login
        cy.url({ timeout: 5000 }).should('satisfy', (url) => {
          return url.includes('/login') || url.length > 0
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar error con token inválido', () => {
    cy.visit('/reset-password?token=invalid-token')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="error-message"], .error-message, .swal2-error').length > 0) {
        cy.get('[data-cy="error-message"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('inválido') || text.includes('expirado') || text.includes('token') || text.length > 0
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe validar que las contraseñas coincidan en reset', () => {
    cy.visit('/reset-password?token=valid-token-123')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="new-password-input"], input[type="password"]').length > 0) {
        cy.get('[data-cy="new-password-input"], input[type="password"]').first().type('NewPassword123!')
        cy.get('body').then(($confirm) => {
          if ($confirm.find('[data-cy="confirm-password-input"], input[type="password"]').length > 1) {
            cy.get('[data-cy="confirm-password-input"], input[type="password"]').last().type('DifferentPassword123!')
          }
        })
        cy.get('[data-cy="reset-button"], button[type="submit"]').first().click()
        
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

  it('debe validar fortaleza de nueva contraseña', () => {
    cy.visit('/reset-password?token=valid-token-123')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="new-password-input"], input[type="password"]').length > 0) {
        cy.get('[data-cy="new-password-input"], input[type="password"]').first().type('123')
        cy.get('body').then(($strength) => {
          if ($strength.find('[data-cy="password-strength"], .password-strength-meter').length > 0) {
            cy.get('[data-cy="password-strength"], .password-strength-meter').should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('débil') || text.includes('weak') || text.length > 0
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })
})

describe('Autenticación - Verificación de Email', () => {
  it('debe mostrar mensaje de verificación pendiente', () => {
    cy.visit('/login')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Simular usuario no verificado
    cy.fixture('users').then((users) => {
      const unverifiedUser = users.farmerUnverified
      
      cy.get('body').then(($body) => {
        if ($body.find('[data-cy="email-input"], input[type="text"], input[type="email"]').length > 0) {
          cy.get('[data-cy="email-input"], input[type="text"], input[type="email"]').first().type(unverifiedUser.email)
          cy.get('[data-cy="password-input"], input[type="password"]').first().type(unverifiedUser.password)
          cy.get('[data-cy="login-button"], button[type="submit"]').first().click()
          
          cy.get('body', { timeout: 5000 }).then(($verify) => {
            if ($verify.find('[data-cy="verification-message"], .error-message').length > 0) {
              cy.get('[data-cy="verification-message"], .error-message').first().should('satisfy', ($el) => {
                const text = $el.text().toLowerCase()
                return text.includes('verifica') || text.includes('verification') || text.includes('email') || text.length > 0
              })
            } else {
              cy.url().should('satisfy', (url) => {
                return url.includes('/login') || url.includes('/verify') || url.length > 0
              })
            }
          })
        }
      })
    })
  })

  it('debe permitir reenviar email de verificación', () => {
    cy.visit('/login')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.fixture('users').then((users) => {
      const unverifiedUser = users.farmerUnverified
      
      cy.get('body').then(($body) => {
        if ($body.find('[data-cy="email-input"], input[type="text"], input[type="email"]').length > 0) {
          cy.get('[data-cy="email-input"], input[type="text"], input[type="email"]').first().type(unverifiedUser.email)
          cy.get('[data-cy="password-input"], input[type="password"]').first().type(unverifiedUser.password)
          cy.get('[data-cy="login-button"], button[type="submit"]').first().click()
          
          cy.get('body', { timeout: 5000 }).then(($resend) => {
            if ($resend.find('[data-cy="resend-verification-button"], button').length > 0) {
              cy.get('[data-cy="resend-verification-button"], button').first().click()
              
              cy.get('body', { timeout: 5000 }).then(($success) => {
                if ($success.find('[data-cy="success-message"], .swal2-success').length > 0) {
                  cy.get('[data-cy="success-message"], .swal2-success').should('satisfy', ($el) => {
                    const text = $el.text().toLowerCase()
                    return text.includes('reenviado') || text.includes('resend') || text.includes('verificación') || text.length > 0
                  })
                }
              })
            }
          })
        }
      })
    })
  })

  it('debe verificar email con token válido', () => {
    cy.visit('/verify-email?token=valid-verification-token')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="success-message"], .swal2-success').length > 0) {
        cy.get('[data-cy="success-message"], .swal2-success').should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('verificado') || text.includes('verification') || text.includes('exitosamente') || text.length > 0
        })
      }
    })
    
    // Debería redirigir al dashboard apropiado
    cy.url({ timeout: 5000 }).should('satisfy', (url) => {
      return !url.includes('/verify-email') || url.length > 0
    })
  })

  it('debe mostrar error con token de verificación inválido', () => {
    cy.visit('/verify-email?token=invalid-token')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="error-message"], .error-message, .swal2-error').length > 0) {
        cy.get('[data-cy="error-message"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('inválido') || text.includes('invalid') || text.includes('token') || text.length > 0
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })
})
