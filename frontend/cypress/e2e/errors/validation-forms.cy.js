/* eslint-disable sonarjs/no-hardcoded-password */
// NOSONAR S2068 - All passwords in this test file are generated dynamically at runtime
// using helper functions (generateTestPassword, generateStrongPassword, generateDifferentPassword, generateWeakPasswords)
// No hardcoded passwords are present in this file.
// CSS selector strings containing the word "password" (e.g., '[data-cy="password-input"]') are NOT hardcoded passwords.
// Variable names containing "password" refer to CSS selectors or dynamically generated test values, not hardcoded credentials.
import {
  visitAndWaitForBody,
  openModalAndExecute,
  verifyErrorMessageWithSelectors,
  testPasswordStrength,
  validateRealTimeField,
  clickIfExistsAndContinue
} from '../../support/helpers'
import { generateStrongPassword, generateWeakPasswords, generateTestPassword, generateDifferentPassword } from '../../support/test-data'
import {
  validateFieldInModal,
  validateRequiredFieldsInModal,
  validateFieldFormat,
  validateMultipleFieldsInModal,
  validateConditionalFieldInModal,
  validatePasswordMatch
} from '../../support/validation-helpers'

describe('Manejo de Errores - Validación y Formularios', () => {
  beforeEach(() => {
    cy.login('farmer')
    cy.fixture('testCredentials').as('credentials')
  })

  it('debe validar campos requeridos en formulario de finca', () => {
    validateRequiredFieldsInModal(
      '/mis-fincas',
      '[data-cy="add-finca-button"], button',
      '[data-cy="save-finca"], button[type="submit"]',
      [
        '[data-cy="finca-nombre-error"]',
        '[data-cy="finca-ubicacion-error"]',
        '[data-cy="finca-area-error"]'
      ]
    )
  })

  it('debe validar formato de email en registro', () => {
    validateFieldFormat(
      '/registro',
      '[data-cy="email-input"], input[type="email"], input[type="text"]',
      'email-invalido',
      '[data-cy="register-button"], button[type="submit"]',
      '[data-cy="email-error"], .error-message, [data-cy="error"]',
      ['email', 'válido', 'formato']
    )
  })

  it('debe validar fortaleza de contraseña', () => {
    visitAndWaitForBody('/registro')
    const weakPasswords = generateWeakPasswords()
    const strongPassword = generateStrongPassword()
    testPasswordStrength(weakPasswords, strongPassword)
  })

  it('debe validar coincidencia de contraseñas', () => {
    // NOSONAR S2068 - Passwords generated dynamically, not hardcoded
    const testPwd = generateTestPassword() // NOSONAR S2068
    const differentPwd = generateDifferentPassword() // NOSONAR S2068
    // NOSONAR S2068 - CSS selector strings, not hardcoded passwords
    const pwdInputSelector = '[data-cy="password-input"], input[type="password"]' // NOSONAR S2068
    const confirmPwdInputSelector = '[data-cy="confirm-password-input"], input[type="password"]' // NOSONAR S2068
    const pwdErrorSelector = '[data-cy="password-match-error"], .error-message' // NOSONAR S2068
    validatePasswordMatch({
      pageUrl: '/registro',
      passwordSelector: pwdInputSelector, // NOSONAR S2068
      passwordValue: testPwd, // NOSONAR S2068
      confirmPasswordSelector: confirmPwdInputSelector, // NOSONAR S2068
      confirmPasswordValue: differentPwd, // NOSONAR S2068
      submitSelector: '[data-cy="register-button"], button[type="submit"]',
      errorSelectors: [pwdErrorSelector], // NOSONAR S2068
      expectedTexts: ['coinciden', 'match', 'contraseña']
    })
  })

  it('debe validar longitud de campos de texto', () => {
    validateFieldInModal(
      '/mis-fincas',
      '[data-cy="add-finca-button"], button',
      '[data-cy="finca-nombre"], input',
      'A',
      '[data-cy="save-finca"], button[type="submit"]',
      '[data-cy="finca-nombre-error"], .error-message',
      ['caracteres', 'al menos', '3']
    )
  })

  it('debe validar rangos numéricos', () => {
    validateFieldInModal(
      '/mis-fincas',
      '[data-cy="add-finca-button"], button',
      '[data-cy="finca-area"], input[type="number"]',
      '-10',
      '[data-cy="save-finca"], button[type="submit"]',
      '[data-cy="finca-area-error"], .error-message',
      ['positiva', 'negativo', 'área']
    )
  })

  it('debe validar fechas', () => {
    validateFieldInModal(
      '/mis-lotes',
      '[data-cy="add-lote-button"], button',
      '[data-cy="lote-fecha-plantacion"], input[type="date"]',
      '2030-01-01',
      '[data-cy="save-lote"], button[type="submit"]',
      '[data-cy="lote-fecha-error"], .error-message',
      ['futura', 'fecha', 'no puede']
    )
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
    clickIfExistsAndContinue('[data-cy="register-button"], button[type="submit"]', () => {
      verifyErrorMessageWithSelectors(
        ['[data-cy="terms-error"], .error-message'],
        ['términos', 'aceptar', 'requerido']
      )
    })
  })

  it('debe validar en tiempo real', () => {
    visitAndWaitForBody('/mis-fincas')
    openModalAndExecute('[data-cy="add-finca-button"], button', ($modal) => {
      if ($modal.find('[data-cy="finca-nombre"], input').length > 0) {
        validateRealTimeField(
          '[data-cy="finca-nombre"], input',
          'A',
          '[data-cy="finca-nombre-error"], .error-message',
          ['caracteres', 'al menos', '3']
        )
      }
    })
  })

  it('debe validar formularios complejos', () => {
    validateMultipleFieldsInModal(
      '/mis-lotes',
      '[data-cy="add-lote-button"], button',
      [
        { selector: '[data-cy="lote-nombre"], input', value: 'Lote Test' },
        { selector: '[data-cy="lote-area"], input[type="number"]', value: '5' }
      ],
      '[data-cy="save-lote"], button[type="submit"]',
      ['[data-cy="lote-variedad-error"], .error-message']
    )
  })

  it('debe validar dependencias entre campos', () => {
    validateMultipleFieldsInModal(
      '/mis-lotes',
      '[data-cy="add-lote-button"], button',
      [
        { selector: '[data-cy="finca-select"], select', value: '1' },
        { selector: '[data-cy="lote-area"], input[type="number"]', value: '100' }
      ],
      '[data-cy="save-lote"], button[type="submit"]',
      ['[data-cy="lote-area-error"], .error-message']
    )
  })

  it('debe validar formatos específicos', () => {
    validateFieldInModal(
      '/mis-fincas',
      '[data-cy="add-finca-button"], button',
      '[data-cy="finca-codigo-postal"], input',
      '123',
      '[data-cy="save-finca"], button[type="submit"]',
      '[data-cy="codigo-postal-error"], .error-message',
      ['código', 'postal', 'inválido', 'formato']
    )
  })

  it('debe validar unicidad de datos', () => {
    validateFieldInModal(
      '/mis-fincas',
      '[data-cy="add-finca-button"], button',
      '[data-cy="finca-nombre"], input',
      'Finca Existente',
      '[data-cy="save-finca"], button[type="submit"]',
      '[data-cy="finca-nombre-error"], .error-message',
      ['existe', 'duplicado', 'nombre']
    )
  })

  it('debe validar caracteres especiales', () => {
    validateFieldInModal(
      '/mis-fincas',
      '[data-cy="add-finca-button"], button',
      '[data-cy="finca-nombre"], input',
      'Finca<script>alert("xss")</script>',
      '[data-cy="save-finca"], button[type="submit"]',
      '[data-cy="finca-nombre-error"], .error-message',
      ['permitidos', 'caracteres', 'inválido']
    )
  })

  it('debe validar límites de caracteres en textarea', () => {
    const longDescription = 'A'.repeat(1001)
    validateFieldInModal(
      '/mis-fincas',
      '[data-cy="add-finca-button"], button',
      '[data-cy="finca-descripcion"], textarea',
      longDescription,
      '[data-cy="save-finca"], button[type="submit"]',
      '[data-cy="finca-descripcion-error"], .error-message',
      ['larga', 'descripción', 'demasiado']
    )
  })

  it('debe validar múltiples errores simultáneos', () => {
    validateMultipleFieldsInModal(
      '/mis-fincas',
      '[data-cy="add-finca-button"], button',
      [
        { selector: '[data-cy="finca-nombre"], input', value: 'A' },
        { selector: '[data-cy="finca-area"], input[type="number"]', value: '-5' }
      ],
      '[data-cy="save-finca"], button[type="submit"]',
      [
        '[data-cy="finca-nombre-error"]',
        '[data-cy="finca-area-error"]',
        '[data-cy="finca-ubicacion-error"]'
      ]
    )
  })

  it('debe validar formularios con campos condicionales', () => {
    validateConditionalFieldInModal({
      pageUrl: '/mis-lotes',
      buttonSelector: '[data-cy="add-lote-button"], button',
      triggerSelector: '[data-cy="lote-tipo-cultivo"], select',
      triggerValue: 'organico',
      conditionalSelector: '[data-cy="certificacion-organica"], input, select',
      submitSelector: '[data-cy="save-lote"], button[type="submit"]',
      errorSelector: '[data-cy="certificacion-error"], .error-message',
      expectedTexts: ['requerido', 'orgánicos', 'certificación']
    })
  })

  it('debe validar formato de teléfono', () => {
    validateFieldFormat(
      '/registro',
      '[data-cy="phone-input"]',
      '123',
      '[data-cy="register-button"]',
      '[data-cy="phone-error"]',
      ['teléfono', 'inválido', 'formato']
    )
  })

  it('debe validar formato de documento', () => {
    validateFieldFormat(
      '/registro',
      '[data-cy="document-input"]',
      '123',
      '[data-cy="register-button"]',
      '[data-cy="document-error"]',
      ['documento', 'inválido', 'formato']
    )
  })

  it('debe validar edad mínima en fecha de nacimiento', () => {
    const futureDate = new Date()
    futureDate.setFullYear(futureDate.getFullYear() - 10)
    const dateString = futureDate.toISOString().split('T')[0]
    validateFieldFormat(
      '/registro',
      '[data-cy="birthdate-input"]',
      dateString,
      '[data-cy="register-button"]',
      '[data-cy="birthdate-error"]',
      ['14 años', 'edad', 'mínima']
    )
  })

  it('debe validar campos de dirección', () => {
    validateFieldInModal(
      '/mis-fincas',
      '[data-cy="add-finca-button"]',
      '[data-cy="finca-direccion"]',
      'A'.repeat(501),
      '[data-cy="save-finca"]',
      '[data-cy="direccion-error"]',
      ['dirección', 'demasiado', 'larga']
    )
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
