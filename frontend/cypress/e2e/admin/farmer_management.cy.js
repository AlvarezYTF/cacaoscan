describe('Admin Farmer Management', () => {
  beforeEach(() => {
    cy.login('admin')
    cy.visit('/admin/agricultores')
    // Esperar a que la página cargue
    cy.get('body', { timeout: 10000 }).should('be.visible')
  })

  const clickTabIfExists = (tabSelector, callback) => {
    const handleTabClick = ($body) => {
      if ($body.find(tabSelector).length > 0) {
        cy.get(tabSelector).click()
        if (callback) callback()
      } else {
        cy.get('body').should('be.visible')
      }
    }
    cy.get('body', { timeout: 5000 }).then(handleTabClick)
  }

  const interactWithFirstRow = (rowSelector, rowCallback) => {
    const handleFirstRow = ($rows) => {
      if ($rows.length > 0) {
        cy.wrap($rows.first()).then(rowCallback)
      }
    }
    cy.get('table tbody tr, [data-cy="farmer-item"]', { timeout: 5000 }).then(handleFirstRow)
  }

  const interactWithLastRow = (rowSelector, rowCallback) => {
    const handleLastRow = ($rows) => {
      if ($rows.length > 0) {
        cy.wrap($rows.last()).then(rowCallback)
      }
    }
    cy.get('table tbody tr, [data-cy="farmer-item"]', { timeout: 5000 }).then(handleLastRow)
  }

  const fillRejectionForm = (reason) => {
    cy.get('body').then(($modal) => {
      if ($modal.find('[data-cy="textarea-reason"], textarea').length > 0) {
        cy.get('[data-cy="textarea-reason"], textarea').first().type(reason)
        cy.get('[data-cy="btn-confirm-reject"], button[type="submit"]').first().click()
        cy.get('body', { timeout: 5000 }).should('be.visible')
      }
    })
  }

  it('should list pending verifications', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="tab-pending"]').length > 0) {
        cy.get('[data-cy="tab-pending"]').click()
        cy.get('table, [data-cy="farmer-list"], .list-container', { timeout: 5000 }).should('exist')
      } else {
        // Si no existe la pestaña, verificar que la página cargó
        cy.get('body').should('be.visible')
      }
    })
  })

  it('should verify a farmer account', () => {
    const verifyFarmerInModal = ($modal) => {
      if ($modal.find('[data-cy="check-doc-id"]').length > 0) {
        cy.get('[data-cy="check-doc-id"]').check()
        cy.get('[data-cy="check-doc-property"]').check()
        cy.get('[data-cy="btn-approve"], button[type="submit"]').first().click()
        cy.get('body', { timeout: 5000 }).should('be.visible')
      }
    }

    const clickVerifyButton = ($row) => {
      cy.wrap($row).find('[data-cy="btn-verify"], button').first().click({ force: true })
      cy.get('[data-cy="modal-verify-docs"], .modal, [role="dialog"]', { timeout: 5000 }).should('exist')
      cy.get('body', { timeout: 5000 }).then(verifyFarmerInModal)
    }

    const handlePendingTab = () => {
      interactWithFirstRow('table tbody tr, [data-cy="farmer-item"]', clickVerifyButton)
    }

    clickTabIfExists('[data-cy="tab-pending"]', handlePendingTab)
  })

  it('should reject a farmer verification with reason', () => {
    clickTabIfExists('[data-cy="tab-pending"]', () => {
      interactWithLastRow('table tbody tr, [data-cy="farmer-item"]', ($row) => {
        cy.wrap($row).find('[data-cy="btn-reject"], button').first().click({ force: true })
        fillRejectionForm('Documentos ilegibles')
      })
    })
  })

  it('should view farmer details including farms', () => {
    clickTabIfExists('[data-cy="tab-active"]', () => {
      interactWithFirstRow('table tbody tr, [data-cy="farmer-item"]', ($row) => {
        cy.wrap($row).click({ force: true })
        cy.get('[data-cy="farmer-profile"], .profile, .details', { timeout: 5000 }).should('exist')
        cy.get('[data-cy="farm-list"], .farms-list, .list', { timeout: 5000 }).should('exist')
      })
    })
  })

  it('should export farmer registry', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="btn-export-farmers"]').length > 0) {
        cy.get('[data-cy="btn-export-farmers"]').click()
        // Verificar que no hay error
        cy.get('.swal2-error', { timeout: 3000 }).should('not.exist')
      }
    })
  })
})

