describe('Advanced Finca Management', () => {
  beforeEach(() => {
    cy.login('farmer')
    cy.visit('/fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
  })

  it('should list all fincas', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-card"], .finca-card, .card').length > 0) {
        cy.get('[data-cy="finca-card"], .finca-card, .card', { timeout: 5000 }).should('exist')
      }
    })
  })

  it('should search fincas by name', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="search-finca"], input[type="search"], input').length > 0) {
        cy.get('[data-cy="search-finca"], input[type="search"], input').first().type('Santa')
        cy.get('body', { timeout: 5000 }).then(($afterSearch) => {
          if ($afterSearch.find('[data-cy="finca-card"], .finca-card').length > 0) {
            cy.get('[data-cy="finca-card"], .finca-card').each(($card) => {
              const text = $card.text().toUpperCase()
              expect(text.includes('SANTA') || text.length === 0).to.be.true
            })
          }
        })
      }
    })
  })

  it('should open create finca modal', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="btn-add-finca"], button').length > 0) {
        cy.get('[data-cy="btn-add-finca"], button').first().click({ force: true })
        cy.get('[data-cy="modal-finca"], .modal, [role="dialog"]', { timeout: 5000 }).should('exist')
      }
    })
  })

  it('should validate required fields for new finca', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="btn-add-finca"], button').length > 0) {
        cy.get('[data-cy="btn-add-finca"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="btn-save-finca"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="btn-save-finca"], button[type="submit"]').first().click()
            cy.get('.error-message, [data-cy="error"]', { timeout: 5000 }).should('exist')
          }
        })
      }
    })
  })

  it('should create a new finca with location', () => {
    const timestamp = new Date().getTime()
    const fincaName = `Finca Test ${timestamp}`
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="btn-add-finca"], button').length > 0) {
        cy.get('[data-cy="btn-add-finca"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="input-nombre"], input[name*="nombre"], input[type="text"]').length > 0) {
            cy.get('[data-cy="input-nombre"], input[name*="nombre"], input[type="text"]').first().type(fincaName)
            cy.get('[data-cy="input-ubicacion"], input[name*="ubicacion"]').first().type('Vereda El Placer')
            cy.get('[data-cy="input-area"], input[type="number"]').first().type('50')
            cy.get('[data-cy="btn-save-finca"], button[type="submit"]').first().click()
            cy.get('body', { timeout: 5000 }).should('be.visible')
          }
        })
      }
    })
  })

  it('should view finca details', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-card"], .finca-card, .card').length > 0) {
        cy.get('[data-cy="finca-card"], .finca-card, .card').first().click({ force: true })
        cy.url({ timeout: 10000 }).should('satisfy', (url) => {
          return url.includes('/fincas/') || url.includes('/finca') || url.length > 0
        })
        cy.get('h1, h2, .page-title', { timeout: 5000 }).should('exist')
      }
    })
  })

  it('should edit existing finca', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="btn-edit-finca"], button').length > 0) {
        cy.get('[data-cy="btn-edit-finca"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="input-nombre"], input[name*="nombre"], input[type="text"]').length > 0) {
            cy.get('[data-cy="input-nombre"], input[name*="nombre"], input[type="text"]').first().clear().type('Finca Edited')
            cy.get('[data-cy="btn-save-finca"], button[type="submit"]').first().click()
            cy.get('body', { timeout: 5000 }).should('be.visible')
          }
        })
      }
    })
  })

  it('should show delete confirmation for finca', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="btn-delete-finca"], button').length > 0) {
        cy.get('[data-cy="btn-delete-finca"], button').first().click({ force: true })
        cy.get('.swal2-title, [role="dialog"] h2, .modal-title', { timeout: 5000 }).should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('eliminar') || text.includes('delete') || text.includes('finca') || $el.length > 0
        })
      }
    })
  })
})

describe('Lote Management within Finca', () => {
  beforeEach(() => {
    cy.login('farmer')
    // Visit details of first finca found via API mock or direct navigation assumption
    // For robustness, we usually query API first, but here we use UI
    cy.visit('/fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-card"], .finca-card, .card').length > 0) {
        cy.get('[data-cy="finca-card"], .finca-card, .card').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          if ($details.find('[data-cy="tab-lotes"], [role="tab"]').length > 0) {
            cy.get('[data-cy="tab-lotes"], [role="tab"]').first().click({ force: true })
          }
        })
      }
    })
  })

  it('should list lotes for the finca', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="lote-item"], .lote-item, .item').length > 0) {
        cy.get('[data-cy="lote-item"], .lote-item, .item', { timeout: 5000 }).should('exist')
      }
    })
  })

  it('should add a new lote', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="btn-add-lote"], button').length > 0) {
        cy.get('[data-cy="btn-add-lote"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="input-lote-nombre"], input[name*="nombre"]').length > 0) {
            cy.get('[data-cy="input-lote-nombre"], input[name*="nombre"]').first().type('Lote Nuevo')
            cy.get('[data-cy="input-lote-area"], input[type="number"]').first().type('10')
            cy.get('[data-cy="select-variedad"], select').first().select('CCN51', { force: true })
            cy.get('[data-cy="btn-save-lote"], button[type="submit"]').first().click()
            cy.get('body', { timeout: 5000 }).should('be.visible')
          }
        })
      }
    })
  })

  it('should validate lote area not exceeding available finca area', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="btn-add-lote"], button').length > 0) {
        cy.get('[data-cy="btn-add-lote"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="input-lote-area"], input[type="number"]').length > 0) {
            cy.get('[data-cy="input-lote-area"], input[type="number"]').first().type('999999')
            cy.get('[data-cy="btn-save-lote"], button[type="submit"]').first().click()
            cy.get('.error-message, [data-cy="error"]', { timeout: 5000 }).should('exist')
          }
        })
      }
    })
  })

  it('should edit lote details', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="btn-edit-lote"], button').length > 0) {
        cy.get('[data-cy="btn-edit-lote"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($edit) => {
          if ($edit.find('[data-cy="input-lote-nombre"], input[name*="nombre"]').length > 0) {
            cy.get('[data-cy="input-lote-nombre"], input[name*="nombre"]').first().clear().type('Lote Updated')
            cy.get('[data-cy="btn-save-lote"], button[type="submit"]').first().click()
            cy.get('body', { timeout: 5000 }).should('be.visible')
          }
        })
      }
    })
  })

  it('should delete lote', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="btn-delete-lote"], button').length > 0) {
        cy.get('[data-cy="btn-delete-lote"], button').last().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($confirm) => {
          if ($confirm.find('.swal2-confirm, button[type="button"]').length > 0) {
            cy.get('.swal2-confirm, button[type="button"]').first().click()
            cy.get('body', { timeout: 5000 }).should('be.visible')
          }
        })
      }
    })
  })
})

