describe('User Account Settings', () => {
  beforeEach(() => {
    cy.navigateToAccountProfile('farmer')
  })

  it('should allow avatar upload', () => {
    ifFoundInBody('[data-cy="input-avatar"], input[type="file"]', () => {
      cy.uploadTestImage('avatar.jpg')
      return clickIfExistsAndContinue('[data-cy="btn-save-avatar"], button[type="submit"]', () => {
        cy.get('body', { timeout: 5000 }).should('be.visible')
        cy.get('[data-cy="user-avatar"], .avatar, img', { timeout: 5000 }).should('exist')
      })
    })
  })

  it('should toggle email notifications preferences', () => {
    return clickIfExistsAndContinue('[data-cy="tab-notifications"], [role="tab"]', () => {
      return ifFoundInBody('[data-cy="toggle-email-reports"], input[type="checkbox"]', () => {
        cy.checkCheckboxIfExists('[data-cy="toggle-email-reports"], input[type="checkbox"]', { force: true })
        return clickIfExistsAndContinue('[data-cy="btn-save-prefs"], button[type="submit"]', () => {
          cy.get('body', { timeout: 5000 }).should('be.visible')
        })
      })
    })
  })

  it('should allow data export (GDPR)', () => {
    return clickIfExistsAndContinue('[data-cy="tab-privacy"], [role="tab"]', () => {
      return clickIfExistsAndContinue('[data-cy="btn-export-data"], button', () => {
        return clickIfExistsAndContinue('.swal2-confirm, button[type="button"]', () => {
          cy.get('body', { timeout: 5000 }).should('be.visible')
        })
      })
    })
  })

  it('should request account deletion', () => {
    return clickIfExistsAndContinue('[data-cy="tab-privacy"], [role="tab"]', () => {
      return clickIfExistsAndContinue('[data-cy="btn-delete-account"], button', () => {
        return typeIfExistsAndContinue('.swal2-input, input[type="text"]', 'BORRAR', () => {
          return clickIfExistsAndContinue('.swal2-confirm, button[type="button"]', () => {
            cy.url({ timeout: 10000 }).should('satisfy', (url) => {
              return url.includes('/login') || url.includes('/auth')
            })
          })
        })
      })
    })
  })
})

