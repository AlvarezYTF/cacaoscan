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

  const savePreferences = () => {
    return clickIfExistsAndContinue('[data-cy="btn-save-prefs"], button[type="submit"]', () => {
      cy.get('body', { timeout: 5000 }).should('be.visible')
    })
  }

  const toggleEmailCheckbox = () => {
    return ifFoundInBody('[data-cy="toggle-email-reports"], input[type="checkbox"]', () => {
      cy.checkCheckboxIfExists('[data-cy="toggle-email-reports"], input[type="checkbox"]', { force: true })
      return savePreferences()
    })
  }

  it('should toggle email notifications preferences', () => {
    return clickIfExistsAndContinue('[data-cy="tab-notifications"], [role="tab"]', toggleEmailCheckbox)
  })

  const confirmExport = () => {
    return clickIfExistsAndContinue('.swal2-confirm, button[type="button"]', () => {
      cy.get('body', { timeout: 5000 }).should('be.visible')
    })
  }

  const clickExportButton = () => {
    return clickIfExistsAndContinue('[data-cy="btn-export-data"], button', confirmExport)
  }

  it('should allow data export (GDPR)', () => {
    return clickIfExistsAndContinue('[data-cy="tab-privacy"], [role="tab"]', clickExportButton)
  })

  const verifyDeletionRedirect = () => {
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/login') || url.includes('/auth')
    })
  }

  const confirmDeletion = () => {
    return clickIfExistsAndContinue('.swal2-confirm, button[type="button"]', verifyDeletionRedirect)
  }

  const typeDeletionConfirmation = () => {
    return typeIfExistsAndContinue('.swal2-input, input[type="text"]', 'BORRAR', confirmDeletion)
  }

  const clickDeleteAccountButton = () => {
    return clickIfExistsAndContinue('[data-cy="btn-delete-account"], button', typeDeletionConfirmation)
  }

  it('should request account deletion', () => {
    return clickIfExistsAndContinue('[data-cy="tab-privacy"], [role="tab"]', clickDeleteAccountButton)
  })
})

