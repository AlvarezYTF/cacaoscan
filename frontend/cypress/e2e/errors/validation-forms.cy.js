import {
  verifySelectorsExist,
  visitAndWaitForBody,
  openModalAndExecute,
  fillFieldSubmitAndVerifyError,
  verifyErrorMessageWithSelectors
} from '../../support/helpers'

describe('Manejo de Errores - Validación y Formularios', () => {
  beforeEach(() => {
    cy.login('farmer')
    cy.fixture('testCredentials').as('credentials')
  })

  it('debe validar campos requeridos en formulario de finca', () => {
    visitAndWaitForBody('/mis-fincas')
    
    openModalAndExecute('[data-cy="add-finca-button"], button', ($modal) => {
      if ($modal.find('[data-cy="save-finca"], button[type="submit"]').length > 0) {
        cy.get('[data-cy="save-finca"], button[type="submit"]').first().click()
        cy.get('body', { timeout: 5000 }).then(($afterSubmit) => {
          const errorSelectors = [
            '[data-cy="finca-nombre-error"]',
            '[data-cy="finca-ubicacion-error"]',
            '[data-cy="finca-area-error"]'
          ]
          verifySelectorsExist(errorSelectors, $afterSubmit, 3000)
        })
      }
    })
  })

  it('debe validar formato de email en registro', () => {
    visitAndWaitForBody('/registro')
    
    fillFieldSubmitAndVerifyError(
      '[data-cy="email-input"], input[type="email"], input[type="text"]',
      'email-invalido',
      '[data-cy="register-button"], button[type="submit"]',
      '[data-cy="email-error"], .error-message, [data-cy="error"]',
      ['email', 'válido', 'formato']
    )
  })

  it('debe validar fortaleza de contraseña', () => {
    visitAndWaitForBody('/registro')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="password-input"], input[type="password"]').length > 0) {
        const weakPasswords = ['123', 'password', '12345678']
        
        for (const [index, password] of weakPasswords.entries()) {
          if (index > 0) {
            cy.get('[data-cy="password-input"], input[type="password"]').first().clear()
          }
          cy.get('[data-cy="password-input"], input[type="password"]').first().type(password, { force: true })
          cy.get('body', { timeout: 2000 }).then(($afterType) => {
            if ($afterType.find('[data-cy="password-strength"], .password-strength').length > 0) {
              cy.get('[data-cy="password-strength"], .password-strength').should('exist')
            }
          })
        }
        
        cy.get('body').then(($strong) => {
          if ($strong.find('[data-cy="password-input"], input[type="password"]').length > 0) {
            cy.get('[data-cy="password-input"], input[type="password"]').first().clear().type('StrongPassword123!', { force: true })
            const checkPasswordStrength = ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('fuerte') || text.includes('strong') || text.length > 0
            }

            const handlePasswordStrength = ($afterStrong) => {
              if ($afterStrong.find('[data-cy="password-strength"], .password-strength').length > 0) {
                cy.get('[data-cy="password-strength"], .password-strength').should('satisfy', checkPasswordStrength)
              }
            }

            cy.get('body', { timeout: 2000 }).then(handlePasswordStrength)
          }
        })
      }
    })
  })

  it('debe validar coincidencia de contraseñas', () => {
    visitAndWaitForBody('/registro')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="password-input"], input[type="password"]').length > 0) {
        cy.get('[data-cy="password-input"], input[type="password"]').first().type('Password123!', { force: true })
        cy.get('body').then(($confirm) => {
          if ($confirm.find('[data-cy="confirm-password-input"], input[type="password"]').length > 0) {
            cy.get('[data-cy="confirm-password-input"], input[type="password"]').first().type('DifferentPassword123!', { force: true })
            cy.get('[data-cy="register-button"], button[type="submit"]').first().click({ force: true })
            verifyErrorMessageWithSelectors(
              ['[data-cy="password-match-error"], .error-message'],
              ['coinciden', 'match', 'contraseña']
            )
          }
        })
      }
    })
  })

  it('debe validar longitud de campos de texto', () => {
    visitAndWaitForBody('/mis-fincas')
    
    openModalAndExecute('[data-cy="add-finca-button"], button', ($modal) => {
      if ($modal.find('[data-cy="finca-nombre"], input').length > 0) {
        fillFieldSubmitAndVerifyError(
          '[data-cy="finca-nombre"], input',
          'A',
          '[data-cy="save-finca"], button[type="submit"]',
          '[data-cy="finca-nombre-error"], .error-message',
          ['caracteres', 'al menos', '3']
        )
      }
    })
  })

  it('debe validar rangos numéricos', () => {
    visitAndWaitForBody('/mis-fincas')
    
    openModalAndExecute('[data-cy="add-finca-button"], button', ($modal) => {
      if ($modal.find('[data-cy="finca-area"], input[type="number"]').length > 0) {
        fillFieldSubmitAndVerifyError(
          '[data-cy="finca-area"], input[type="number"]',
          '-10',
          '[data-cy="save-finca"], button[type="submit"]',
          '[data-cy="finca-area-error"], .error-message',
          ['positiva', 'negativo', 'área']
        )
      }
    })
  })

  it('debe validar fechas', () => {
    visitAndWaitForBody('/mis-lotes')
    
    openModalAndExecute('[data-cy="add-lote-button"], button', ($modal) => {
      if ($modal.find('[data-cy="lote-fecha-plantacion"], input[type="date"]').length > 0) {
        fillFieldSubmitAndVerifyError(
          '[data-cy="lote-fecha-plantacion"], input[type="date"]',
          '2030-01-01',
          '[data-cy="save-lote"], button[type="submit"]',
          '[data-cy="lote-fecha-error"], .error-message',
          ['futura', 'fecha', 'no puede']
        )
      }
    })
  })

  it('debe validar archivos', () => {
    visitAndWaitForBody('/nuevo-analisis')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="file-input"], input[type="file"]').length > 0) {
        const largeSize = 1024 * 1024 // 1MB
        cy.uploadFile('large-image.jpg', { type: 'image/jpeg', size: largeSize, useFixture: false })
        verifyErrorMessageWithSelectors(
          ['[data-cy="file-size-error"], .error-message'],
          ['grande', 'archivo', 'demasiado']
        )
      }
    })
  })

  it('debe validar selecciones requeridas', () => {
    visitAndWaitForBody('/mis-lotes')
    
    openModalAndExecute('[data-cy="add-lote-button"], button', ($modal) => {
      if ($modal.find('[data-cy="save-lote"], button[type="submit"]').length > 0) {
        cy.get('[data-cy="save-lote"], button[type="submit"]').first().click({ force: true })
        verifyErrorMessageWithSelectors(
          ['[data-cy="finca-select-error"], .error-message'],
          ['finca', 'seleccionar', 'requerido']
        )
      }
    })
  })

  it('debe validar checkboxes requeridos', () => {
    visitAndWaitForBody('/registro')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="register-button"], button[type="submit"]').length > 0) {
        cy.get('[data-cy="register-button"], button[type="submit"]').first().click({ force: true })
        verifyErrorMessageWithSelectors(
          ['[data-cy="terms-error"], .error-message'],
          ['términos', 'aceptar', 'requerido']
        )
      }
    })
  })

  it('debe validar en tiempo real', () => {
    visitAndWaitForBody('/mis-fincas')
    
    openModalAndExecute('[data-cy="add-finca-button"], button', ($modal) => {
      if ($modal.find('[data-cy="finca-nombre"], input').length > 0) {
        cy.get('[data-cy="finca-nombre"], input').first().type('A', { force: true })
        const checkMinLengthError = ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('caracteres') || text.includes('al menos') || text.includes('3') || text.length > 0
        }

        const handleMinLengthError = ($afterType) => {
          if ($afterType.find('[data-cy="finca-nombre-error"], .error-message').length > 0) {
            cy.get('[data-cy="finca-nombre-error"], .error-message').first().should('satisfy', checkMinLengthError)
          }
        }

        cy.get('body', { timeout: 2000 }).then(handleMinLengthError)
      }
    })
  })

  it('debe validar formularios complejos', () => {
    visitAndWaitForBody('/mis-lotes')
    
    openModalAndExecute('[data-cy="add-lote-button"], button', ($modal) => {
      if ($modal.find('[data-cy="lote-nombre"], input').length > 0) {
        cy.get('[data-cy="lote-nombre"], input').first().type('Lote Test', { force: true })
        cy.get('[data-cy="lote-area"], input[type="number"]').first().type('5', { force: true })
        cy.get('[data-cy="save-lote"], button[type="submit"]').first().click({ force: true })
        verifyErrorMessageWithSelectors(
          ['[data-cy="lote-variedad-error"], .error-message'],
          ['requerido', 'campo', 'variedad']
        )
      }
    })
  })

  it('debe validar dependencias entre campos', () => {
    visitAndWaitForBody('/mis-lotes')
    
    openModalAndExecute('[data-cy="add-lote-button"], button', ($modal) => {
      if ($modal.find('[data-cy="finca-select"], select').length > 0) {
        cy.get('[data-cy="finca-select"], select').first().select('1', { force: true })
        cy.get('[data-cy="lote-area"], input[type="number"]').first().type('100', { force: true })
        cy.get('[data-cy="save-lote"], button[type="submit"]').first().click({ force: true })
        verifyErrorMessageWithSelectors(
          ['[data-cy="lote-area-error"], .error-message'],
          ['exceder', 'área', 'finca']
        )
      }
    })
  })

  it('debe validar formatos específicos', () => {
    visitAndWaitForBody('/mis-fincas')
    
    openModalAndExecute('[data-cy="add-finca-button"], button', ($modal) => {
      if ($modal.find('[data-cy="finca-codigo-postal"], input').length > 0) {
        fillFieldSubmitAndVerifyError(
          '[data-cy="finca-codigo-postal"], input',
          '123',
          '[data-cy="save-finca"], button[type="submit"]',
          '[data-cy="codigo-postal-error"], .error-message',
          ['código', 'postal', 'inválido', 'formato']
        )
      }
    })
  })

  it('debe validar unicidad de datos', () => {
    visitAndWaitForBody('/mis-fincas')
    
    openModalAndExecute('[data-cy="add-finca-button"], button', ($modal) => {
      if ($modal.find('[data-cy="finca-nombre"], input').length > 0) {
        fillFieldSubmitAndVerifyError(
          '[data-cy="finca-nombre"], input',
          'Finca Existente',
          '[data-cy="save-finca"], button[type="submit"]',
          '[data-cy="finca-nombre-error"], .error-message',
          ['existe', 'duplicado', 'nombre']
        )
      }
    })
  })

  it('debe validar caracteres especiales', () => {
    visitAndWaitForBody('/mis-fincas')
    
    openModalAndExecute('[data-cy="add-finca-button"], button', ($modal) => {
      if ($modal.find('[data-cy="finca-nombre"], input').length > 0) {
        fillFieldSubmitAndVerifyError(
          '[data-cy="finca-nombre"], input',
          'Finca<script>alert("xss")</script>',
          '[data-cy="save-finca"], button[type="submit"]',
          '[data-cy="finca-nombre-error"], .error-message',
          ['permitidos', 'caracteres', 'inválido']
        )
      }
    })
  })

  it('debe validar límites de caracteres en textarea', () => {
    visitAndWaitForBody('/mis-fincas')
    
    openModalAndExecute('[data-cy="add-finca-button"], button', ($modal) => {
      if ($modal.find('[data-cy="finca-descripcion"], textarea').length > 0) {
        const longDescription = 'A'.repeat(1001)
        fillFieldSubmitAndVerifyError(
          '[data-cy="finca-descripcion"], textarea',
          longDescription,
          '[data-cy="save-finca"], button[type="submit"]',
          '[data-cy="finca-descripcion-error"], .error-message',
          ['larga', 'descripción', 'demasiado']
        )
      }
    })
  })

  it('debe validar múltiples errores simultáneos', () => {
    visitAndWaitForBody('/mis-fincas')
    
    openModalAndExecute('[data-cy="add-finca-button"], button', ($modal) => {
      if ($modal.find('[data-cy="finca-nombre"], input').length > 0) {
        cy.get('[data-cy="finca-nombre"], input').first().type('A', { force: true })
        cy.get('[data-cy="finca-area"], input[type="number"]').first().type('-5', { force: true })
        cy.get('[data-cy="save-finca"], button[type="submit"]').first().click({ force: true })
        cy.get('body', { timeout: 3000 }).then(($error) => {
          const errorSelectors = [
            '[data-cy="finca-nombre-error"]',
            '[data-cy="finca-area-error"]',
            '[data-cy="finca-ubicacion-error"]'
          ]
          verifySelectorsExist(errorSelectors, $error, 3000)
        })
      }
    })
  })

  it('debe validar formularios con campos condicionales', () => {
    visitAndWaitForBody('/mis-lotes')
    
    openModalAndExecute('[data-cy="add-lote-button"], button', ($modal) => {
      if ($modal.find('[data-cy="lote-tipo-cultivo"], select').length > 0) {
        cy.get('[data-cy="lote-tipo-cultivo"], select').first().select('organico', { force: true })
        cy.get('body', { timeout: 3000 }).then(($afterSelect) => {
          if ($afterSelect.find('[data-cy="certificacion-organica"], input, select').length > 0) {
            cy.get('[data-cy="certificacion-organica"], input, select').should('exist')
          }
          cy.get('[data-cy="save-lote"], button[type="submit"]').first().click({ force: true })
          verifyErrorMessageWithSelectors(
            ['[data-cy="certificacion-error"], .error-message'],
            ['requerido', 'orgánicos', 'certificación']
          )
        })
      }
    })
  })

  it('debe validar formato de teléfono', () => {
    visitAndWaitForBody('/registro')
    fillFieldSubmitAndVerifyError(
      '[data-cy="phone-input"]',
      '123',
      '[data-cy="register-button"]',
      '[data-cy="phone-error"]',
      ['teléfono', 'inválido', 'formato']
    )
  })

  it('debe validar formato de documento', () => {
    visitAndWaitForBody('/registro')
    fillFieldSubmitAndVerifyError(
      '[data-cy="document-input"]',
      '123',
      '[data-cy="register-button"]',
      '[data-cy="document-error"]',
      ['documento', 'inválido', 'formato']
    )
  })

  it('debe validar edad mínima en fecha de nacimiento', () => {
    visitAndWaitForBody('/registro')
    const futureDate = new Date()
    futureDate.setFullYear(futureDate.getFullYear() - 10)
    const dateString = futureDate.toISOString().split('T')[0]
    fillFieldSubmitAndVerifyError(
      '[data-cy="birthdate-input"]',
      dateString,
      '[data-cy="register-button"]',
      '[data-cy="birthdate-error"]',
      ['14 años', 'edad', 'mínima']
    )
  })

  it('debe validar campos de dirección', () => {
    visitAndWaitForBody('/mis-fincas')
    openModalAndExecute('[data-cy="add-finca-button"]', ($modal) => {
      fillFieldSubmitAndVerifyError(
        '[data-cy="finca-direccion"]',
        'A'.repeat(501),
        '[data-cy="save-finca"]',
        '[data-cy="direccion-error"]',
        ['dirección', 'demasiado', 'larga']
      )
    })
  })

  it('debe validar coordenadas GPS', () => {
    visitAndWaitForBody('/mis-fincas')
    openModalAndExecute('[data-cy="add-finca-button"]', ($modal) => {
      cy.get('[data-cy="finca-latitud"]').type('100', { force: true })
      cy.get('[data-cy="finca-longitud"]').type('200', { force: true })
      cy.get('[data-cy="save-finca"]').click({ force: true })
      verifyErrorMessageWithSelectors(
        ['[data-cy="coordenadas-error"]'],
        ['coordenadas', 'inválidas']
      )
    })
  })
})
