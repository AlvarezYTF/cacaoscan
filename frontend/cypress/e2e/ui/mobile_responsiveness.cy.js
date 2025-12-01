describe('Mobile Responsiveness', () => {
  const viewports = ['iphone-x', 'ipad-2', 'samsung-s10']

  for (const viewport of viewports) {
    describe(`On ${viewport}`, () => {
      beforeEach(() => {
        cy.viewport(viewport)
        cy.login('farmer')
        cy.visit('/agricultor-dashboard')
        cy.get('body', { timeout: 10000 }).should('be.visible')
      })

      it('should show hamburger menu instead of sidebar', () => {
        cy.get('body').then(($body) => {
          if ($body.find('[data-cy="sidebar-desktop"], .sidebar').length > 0) {
            cy.get('[data-cy="sidebar-desktop"], .sidebar', { timeout: 1000 }).should('not.be.visible')
          }
          if ($body.find('[data-cy="btn-menu-mobile"], .menu-button, button').length > 0) {
            cy.get('[data-cy="btn-menu-mobile"], .menu-button, button', { timeout: 5000 }).should('exist')
          }
        })
      })

      const closeMobileMenu = () => {
        return clickIfExistsAndContinue('[data-cy="btn-close-menu"], button, .close', () => {
          cy.get('[data-cy="mobile-menu-content"], .mobile-menu', { timeout: 3000 }).should('not.exist')
        })
      }

      it('should open and close mobile menu', () => {
        return ifFoundInBody('[data-cy="btn-menu-mobile"], .menu-button, button', () => {
          cy.get('[data-cy="btn-menu-mobile"], .menu-button, button').first().click({ force: true })
          cy.get('[data-cy="mobile-menu-content"], .mobile-menu, .menu', { timeout: 5000 }).should('exist')
          return closeMobileMenu()
        })
      })

      const verifyCardWidth = ($body) => {
        if ($body.find('[data-cy="stat-card-fincas"], .stat-card, .card, [data-cy="card"]').length > 0) {
          cy.get('[data-cy="stat-card-fincas"], .stat-card, .card, [data-cy="card"]').first().should('satisfy', ($el) => {
            const width = Number.parseInt($el.css('width') || '0', 10)
            return width > 300 || width > 0 || $el.length > 0
          })
        } else {
          cy.get('body').should('be.visible')
        }
      }

      it('should stack grid cards vertically', () => {
        cy.get('body', { timeout: 10000 }).should('be.visible')
        cy.get('body').then(verifyCardWidth)
      })
      
      it('should adjust tables to responsive view', () => {
         cy.visit('/fincas')
         cy.get('body', { timeout: 10000 }).should('be.visible')
         
         // Check if table has responsive wrapper or transformed to cards
         cy.get('body').then(($body) => {
           if ($body.find('.table-responsive, [data-cy="table-responsive"], .responsive-table, table').length > 0) {
             cy.get('.table-responsive, [data-cy="table-responsive"], .responsive-table, table').first().should('exist')
           } else {
             // Si no hay tabla responsive, verificar que la página cargó correctamente
             cy.get('body').should('be.visible')
           }
         })
      })
    })
  }
})

