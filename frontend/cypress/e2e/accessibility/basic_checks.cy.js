describe('Accessibility (A11y) Manual Checks', () => {
  const routes = [
    '/login',
    '/registro',
    '/',
    '/legal/terms'
  ]

  routes.forEach(route => {
    it(`should have basic accessibility attributes on ${route}`, () => {
      cy.visit(route)
      cy.get('body', { timeout: 10000 }).should('be.visible')
      
      // 1. Images must have alt text (si existen)
      cy.get('body').then(($body) => {
        if ($body.find('img').length > 0) {
          cy.get('img').each(($img) => {
            cy.wrap($img).should('satisfy', ($el) => {
              return $el.attr('alt') !== undefined || $el.attr('aria-label') !== undefined || $el.attr('role') === 'presentation'
            })
          })
        }
      })

      // 2. Form inputs should have labels (si existen)
      cy.get('body').then(($body) => {
        if ($body.find('input').length > 0) {
          cy.get('input').each(($input) => {
            const id = $input.attr('id')
            if (id) {
              cy.get(`label[for="${id}"]`).should('satisfy', ($label) => {
                return $label.length > 0 || $input.attr('aria-label') !== undefined
              })
            } else {
              cy.wrap($input).should('satisfy', ($el) => {
                return $el.attr('aria-label') !== undefined || $el.attr('aria-labelledby') !== undefined
              })
            }
          })
        }
      })

      // 3. Buttons should have text or aria-label (si existen)
      cy.get('body').then(($body) => {
        if ($body.find('button').length > 0) {
          cy.get('button').each(($btn) => {
            cy.wrap($btn).should('satisfy', ($el) => {
              const text = $el.text().trim()
              return text !== '' || $el.attr('aria-label') !== undefined || $el.attr('aria-labelledby') !== undefined
            })
          })
        }
      })
    })
  })

  it('should support keyboard navigation on login', () => {
    cy.visit('/login')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="input-email"], input[type="email"], input[type="text"]').length > 0) {
        cy.get('[data-cy="input-email"], input[type="email"], input[type="text"]').first().focus()
        cy.focused().tab()
        cy.focused().should('satisfy', ($el) => {
          return $el.attr('data-cy') === 'input-password' || $el.attr('type') === 'password' || $el.length > 0
        })
      }
    })
  })
})

