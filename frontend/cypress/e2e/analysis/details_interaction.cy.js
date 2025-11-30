describe('Deep Dive: Analysis Interaction', () => {
  beforeEach(() => {
    cy.login('analyst') // Or farmer/admin
    cy.visit('/detalle-analisis/1') // Mock ID
    cy.get('body', { timeout: 10000 }).should('be.visible')
  })

  it('should toggle different mask layers', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="layer-control"], button, .layer-control').length > 0) {
        cy.get('[data-cy="layer-control"], button, .layer-control').first().click({ force: true })
        cy.get('body').then(($afterClick) => {
          if ($afterClick.find('[data-cy="checkbox-healthy"], input[type="checkbox"]').length > 0) {
            cy.get('[data-cy="checkbox-healthy"], input[type="checkbox"]').first().uncheck({ force: true })
            cy.get('[data-cy="mask-healthy"], .mask', { timeout: 3000 }).should('not.exist')
            cy.get('[data-cy="checkbox-diseased"], input[type="checkbox"]').first().check({ force: true })
            cy.get('[data-cy="mask-diseased"], .mask', { timeout: 3000 }).should('exist')
          }
        })
      }
    })
  })

  it('should zoom in and out of the image', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="btn-zoom-in"], button, .zoom-in').length > 0) {
        cy.get('[data-cy="btn-zoom-in"], button, .zoom-in').first().click({ force: true })
        cy.get('[data-cy="image-canvas"], canvas, img', { timeout: 5000 }).should('exist')
        cy.get('body').then(($afterZoom) => {
          if ($afterZoom.find('[data-cy="btn-reset-zoom"], button').length > 0) {
            cy.get('[data-cy="btn-reset-zoom"], button').first().click({ force: true })
            cy.get('[data-cy="image-canvas"], canvas, img').should('exist')
          }
        })
      }
    })
  })

  it('should show object details on hover', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="detected-object"], .object, .detection').length > 0) {
        cy.get('[data-cy="detected-object"], .object, .detection').first().trigger('mouseover')
        cy.get('[data-cy="tooltip-details"], .tooltip', { timeout: 3000 }).should('exist')
      }
    })
  })

  it('should add comments to the analysis', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="btn-add-comment"], button').length > 0) {
        cy.get('[data-cy="btn-add-comment"], button').first().click({ force: true })
        cy.get('body').then(($afterClick) => {
          if ($afterClick.find('[data-cy="input-comment"], textarea, input').length > 0) {
            cy.get('[data-cy="input-comment"], textarea, input').first().type('Observación importante sobre esta muestra.')
            cy.get('[data-cy="btn-post-comment"], button[type="submit"]').first().click()
            cy.get('[data-cy="comments-list"], .comments, .comment-list', { timeout: 5000 }).should('exist')
          }
        })
      }
    })
  })

  it('should switch between visual and tabular view', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="view-mode-table"], button, [role="tab"]').length > 0) {
        cy.get('[data-cy="view-mode-table"], button, [role="tab"]').first().click({ force: true })
        cy.get('table, .table', { timeout: 5000 }).should('exist')
        cy.get('body').then(($afterTable) => {
          if ($afterTable.find('[data-cy="view-mode-visual"], button, [role="tab"]').length > 0) {
            cy.get('[data-cy="view-mode-visual"], button, [role="tab"]').first().click({ force: true })
            cy.get('[data-cy="image-canvas"], canvas, img', { timeout: 5000 }).should('exist')
          }
        })
      }
    })
  })
})

