describe('Autenticación - Recuperación de Contraseña', () => {
  beforeEach(() => {
    cy.visit('/login')
  })

  it('debe mostrar formulario de recuperación de contraseña', () => {
    cy.get('[data-cy="forgot-password-link"]').click()
    
    cy.url().should('include', '/forgot-password')
    cy.get('[data-cy="forgot-password-form"]').should('be.visible')
    cy.get('[data-cy="email-input"]').should('be.visible')
    cy.get('[data-cy="send-reset-button"]').should('be.visible')
    cy.get('[data-cy="back-to-login-link"]').should('be.visible')
  })

  it('debe enviar email de recuperación exitosamente', () => {
    cy.fixture('users').then((users) => {
      const user = users.farmer
      
      cy.get('[data-cy="forgot-password-link"]').click()
      cy.get('[data-cy="email-input"]').type(user.email)
      cy.get('[data-cy="send-reset-button"]').click()
      
      cy.get('[data-cy="success-message"]')
        .should('be.visible')
        .and('contain', 'Email de recuperación enviado')
    })
  })

  it('debe mostrar error si el email no existe', () => {
    cy.get('[data-cy="forgot-password-link"]').click()
    cy.get('[data-cy="email-input"]').type('noexiste@test.com')
    cy.get('[data-cy="send-reset-button"]').click()
    
    cy.get('[data-cy="error-message"]')
      .should('be.visible')
      .and('contain', 'Email no encontrado')
  })

  it('debe validar formato de email en recuperación', () => {
    cy.get('[data-cy="forgot-password-link"]').click()
    cy.get('[data-cy="email-input"]').type('email-invalido')
    cy.get('[data-cy="send-reset-button"]').click()
    
    cy.get('[data-cy="email-error"]')
      .should('be.visible')
      .and('contain', 'Formato de email inválido')
  })

  it('debe navegar de vuelta al login', () => {
    cy.get('[data-cy="forgot-password-link"]').click()
    cy.get('[data-cy="back-to-login-link"]').click()
    
    cy.url().should('include', '/login')
  })
})

describe('Autenticación - Reset de Contraseña', () => {
  it('debe mostrar formulario de reset con token válido', () => {
    // Simular token válido en la URL
    cy.visit('/reset-password?token=valid-token-123')
    
    cy.get('[data-cy="reset-password-form"]').should('be.visible')
    cy.get('[data-cy="new-password-input"]').should('be.visible')
    cy.get('[data-cy="confirm-password-input"]').should('be.visible')
    cy.get('[data-cy="reset-button"]').should('be.visible')
  })

  it('debe resetear contraseña exitosamente', () => {
    cy.visit('/reset-password?token=valid-token-123')
    
    cy.get('[data-cy="new-password-input"]').type('NewPassword123!')
    cy.get('[data-cy="confirm-password-input"]').type('NewPassword123!')
    cy.get('[data-cy="reset-button"]').click()
    
    cy.get('[data-cy="success-message"]')
      .should('be.visible')
      .and('contain', 'Contraseña actualizada exitosamente')
    
    // Debería redirigir al login
    cy.url().should('include', '/login')
  })

  it('debe mostrar error con token inválido', () => {
    cy.visit('/reset-password?token=invalid-token')
    
    cy.get('[data-cy="error-message"]')
      .should('be.visible')
      .and('contain', 'Token inválido o expirado')
  })

  it('debe validar que las contraseñas coincidan en reset', () => {
    cy.visit('/reset-password?token=valid-token-123')
    
    cy.get('[data-cy="new-password-input"]').type('NewPassword123!')
    cy.get('[data-cy="confirm-password-input"]').type('DifferentPassword123!')
    cy.get('[data-cy="reset-button"]').click()
    
    cy.get('[data-cy="password-match-error"]')
      .should('be.visible')
      .and('contain', 'Las contraseñas no coinciden')
  })

  it('debe validar fortaleza de nueva contraseña', () => {
    cy.visit('/reset-password?token=valid-token-123')
    
    cy.get('[data-cy="new-password-input"]').type('123')
    cy.get('[data-cy="password-strength"]')
      .should('be.visible')
      .and('contain', 'Contraseña débil')
  })
})

describe('Autenticación - Verificación de Email', () => {
  it('debe mostrar mensaje de verificación pendiente', () => {
    cy.visit('/login')
    
    // Simular usuario no verificado
    cy.fixture('users').then((users) => {
      const unverifiedUser = users.farmerUnverified
      
      cy.get('[data-cy="email-input"]').type(unverifiedUser.email)
      cy.get('[data-cy="password-input"]').type(unverifiedUser.password)
      cy.get('[data-cy="login-button"]').click()
      
      cy.get('[data-cy="verification-message"]')
        .should('be.visible')
        .and('contain', 'Verifica tu email')
    })
  })

  it('debe permitir reenviar email de verificación', () => {
    cy.visit('/login')
    
    cy.fixture('users').then((users) => {
      const unverifiedUser = users.farmerUnverified
      
      cy.get('[data-cy="email-input"]').type(unverifiedUser.email)
      cy.get('[data-cy="password-input"]').type(unverifiedUser.password)
      cy.get('[data-cy="login-button"]').click()
      
      cy.get('[data-cy="resend-verification-button"]').click()
      
      cy.get('[data-cy="success-message"]')
        .should('be.visible')
        .and('contain', 'Email de verificación reenviado')
    })
  })

  it('debe verificar email con token válido', () => {
    cy.visit('/verify-email?token=valid-verification-token')
    
    cy.get('[data-cy="success-message"]')
      .should('be.visible')
      .and('contain', 'Email verificado exitosamente')
    
    // Debería redirigir al dashboard apropiado
    cy.url().should('not.include', '/verify-email')
  })

  it('debe mostrar error con token de verificación inválido', () => {
    cy.visit('/verify-email?token=invalid-token')
    
    cy.get('[data-cy="error-message"]')
      .should('be.visible')
      .and('contain', 'Token de verificación inválido')
  })
})
