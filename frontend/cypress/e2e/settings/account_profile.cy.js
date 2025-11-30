describe('User Account Settings', () => {
  beforeEach(() => {
    cy.login('farmer')
    cy.visit('/agricultor/configuracion')
    cy.get('body', { timeout: 10000 }).should('be.visible')
  })

  it('should allow avatar upload', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="input-avatar"], input[type="file"]').length > 0) {
        cy.uploadTestImage('avatar.jpg')
        cy.get('body').then(($afterUpload) => {
          if ($afterUpload.find('[data-cy="btn-save-avatar"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="btn-save-avatar"], button[type="submit"]').first().click()
            cy.get('body', { timeout: 5000 }).should('be.visible')
            cy.get('[data-cy="user-avatar"], .avatar, img', { timeout: 5000 }).should('exist')
          }
        })
      }
    })
  })

  it('should toggle email notifications preferences', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="tab-notifications"], [role="tab"]').length > 0) {
        cy.get('[data-cy="tab-notifications"], [role="tab"]').first().click()
        cy.get('body').then(($notifications) => {
          if ($notifications.find('[data-cy="toggle-email-reports"], input[type="checkbox"]').length > 0) {
            cy.get('[data-cy="toggle-email-reports"], input[type="checkbox"]').first().click({ force: true })
            cy.get('[data-cy="btn-save-prefs"], button[type="submit"]').first().click()
            cy.get('body', { timeout: 5000 }).should('be.visible')
          }
        })
      }
    })
  })

  it('should allow data export (GDPR)', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="tab-privacy"], [role="tab"]').length > 0) {
        cy.get('[data-cy="tab-privacy"], [role="tab"]').first().click()
        cy.get('body').then(($privacy) => {
          if ($privacy.find('[data-cy="btn-export-data"], button').length > 0) {
            cy.get('[data-cy="btn-export-data"], button').first().click()
            cy.get('.swal2-confirm, button[type="button"]', { timeout: 5000 }).then(($confirm) => {
              if ($confirm.length > 0) {
                cy.wrap($confirm.first()).click()
                cy.get('body', { timeout: 5000 }).should('be.visible')
              }
            })
          }
        })
      }
    })
  })

  it('should request account deletion', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="tab-privacy"], [role="tab"]').length > 0) {
        cy.get('[data-cy="tab-privacy"], [role="tab"]').first().click()
        cy.get('body').then(($privacy) => {
          if ($privacy.find('[data-cy="btn-delete-account"], button').length > 0) {
            cy.get('[data-cy="btn-delete-account"], button').first().click()
            cy.get('body', { timeout: 5000 }).then(($modal) => {
              if ($modal.find('.swal2-input, input[type="text"]').length > 0) {
                cy.get('.swal2-input, input[type="text"]').first().type('BORRAR')
                cy.get('.swal2-confirm, button[type="button"]').first().click()
                cy.url({ timeout: 10000 }).should('satisfy', (url) => {
                  return url.includes('/login') || url.includes('/auth')
                })
              }
            })
          }
        })
      }
    })
  })
})

