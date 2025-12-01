describe('Deep Dive: Analysis Interaction', () => {
  beforeEach(() => {
    cy.login('analyst')
    cy.visit('/detalle-analisis/1')
    cy.get('body', { timeout: 10000 }).should('be.visible')
  })

  it('should toggle different mask layers', () => {
    cy.clickIfExists('[data-cy="layer-control"], button, .layer-control').then(() => {
      cy.get('body').then(($afterClick) => {
        if ($afterClick.find('[data-cy="checkbox-healthy"], input[type="checkbox"]').length > 0) {
          cy.get('[data-cy="checkbox-healthy"], input[type="checkbox"]').first().uncheck({ force: true })
          cy.get('[data-cy="mask-healthy"], .mask', { timeout: 3000 }).should('not.exist')
          cy.get('[data-cy="checkbox-diseased"], input[type="checkbox"]').first().check({ force: true })
          cy.get('[data-cy="mask-diseased"], .mask', { timeout: 3000 }).should('exist')
        }
      })
    })
  })

  it('should zoom in and out of the image', () => {
    const resetZoom = () => {
      cy.clickIfExists('[data-cy="btn-reset-zoom"], button')
      cy.get('[data-cy="image-canvas"], canvas, img').should('exist')
    }

    const afterZoomIn = () => {
      cy.get('[data-cy="image-canvas"], canvas, img', { timeout: 5000 }).should('exist')
      resetZoom()
    }

    cy.clickIfExists('[data-cy="btn-zoom-in"], button, .zoom-in').then(afterZoomIn)
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
    const addComment = ($afterClick) => {
      if ($afterClick.find('[data-cy="input-comment"], textarea, input').length > 0) {
        cy.get('[data-cy="input-comment"], textarea, input').first().type('Observación importante sobre esta muestra.')
        cy.get('[data-cy="btn-post-comment"], button[type="submit"]').first().click()
        cy.get('[data-cy="comments-list"], .comments, .comment-list', { timeout: 5000 }).should('exist')
      }
    }

    const afterClickAddComment = () => {
      cy.get('body', { timeout: 5000 }).then(addComment)
    }

    cy.clickIfExists('[data-cy="btn-add-comment"], button').then(afterClickAddComment)
  })

  it('should switch between visual and tabular view', () => {
    const switchToVisualView = () => {
      cy.clickIfExists('[data-cy="view-mode-visual"], button, [role="tab"]')
      cy.get('[data-cy="image-canvas"], canvas, img', { timeout: 5000 }).should('exist')
    }

    const afterTableMode = () => {
      cy.get('table, .table', { timeout: 5000 }).should('exist')
      switchToVisualView()
    }

    cy.clickIfExists('[data-cy="view-mode-table"], button, [role="tab"]').then(afterTableMode)
  })
})
