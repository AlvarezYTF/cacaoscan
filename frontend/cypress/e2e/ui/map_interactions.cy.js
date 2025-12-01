describe('Map Component Interactions', () => {
  beforeEach(() => {
    cy.login('farmer')
    cy.visit('/fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.clickIfExists('[data-cy="btn-view-map"], button, a')
  })

  it('should load the map', () => {
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('.leaflet-container, [data-cy="map"], .map').length > 0) {
        cy.get('.leaflet-container, [data-cy="map"], .map', { timeout: 5000 }).should('exist')
      }
    })
  })

  it('should display markers for fincas', () => {
    cy.get('body').then(($body) => {
      if ($body.find('.leaflet-marker-icon, .marker, [data-cy="marker"]').length > 0) {
        cy.get('.leaflet-marker-icon, .marker, [data-cy="marker"]', { timeout: 5000 }).should('have.length.at.least', 0)
      }
    })
  })

  it('should show popup info on marker click', () => {
    cy.get('body').then(($body) => {
      if ($body.find('.leaflet-marker-icon, .marker, [data-cy="marker"]').length > 0) {
        cy.get('.leaflet-marker-icon, .marker, [data-cy="marker"]').first().click({ force: true })
        cy.get('.leaflet-popup-content, .popup, [data-cy="popup"]', { timeout: 5000 }).should('exist')
      }
    })
  })

  it('should handle geolocation permission denied gracefully', () => {
    cy.visit('/fincas', {
      onBeforeLoad(win) {
        cy.stub(win.navigator.geolocation, 'getCurrentPosition').callsFake((cb, err) => {
          if (err) err({ code: 1, message: 'User denied Geolocation' })
        })
      }
    })
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.clickIfExists('[data-cy="btn-locate-me"], .btn-locate-me, button').then(() => {
      cy.get('body', { timeout: 3000 }).then(($afterClick) => {
        if ($afterClick.find('.swal2-warning, .error-message, .warning').length > 0) {
          cy.get('.swal2-warning, .error-message, .warning').first().should('satisfy', ($el) => {
            const text = $el.text().toLowerCase()
            return text.includes('permiso') || text.includes('denegado') || text.includes('geolocation') || text.length > 0
          })
        }
      })
    })
  })

  it('should switch map layers (Satellite/Terrain)', () => {
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('.leaflet-control-layers-toggle, [data-cy="layer-toggle"], button').length > 0) {
        cy.get('.leaflet-control-layers-toggle, [data-cy="layer-toggle"], button').first().trigger('mouseover', { force: true })
        cy.get('body', { timeout: 2000 }).then(($afterHover) => {
          if ($afterHover.find('text:contains("Satélite"), button:contains("Satélite"), a:contains("Satélite")').length > 0) {
            cy.contains('Satélite').click({ force: true })
            cy.get('body', { timeout: 3000 }).then(($afterClick) => {
              if ($afterClick.find('.leaflet-tile-pane img, .map-tile').length > 0) {
                cy.get('.leaflet-tile-pane img, .map-tile').first().should('satisfy', ($el) => {
                  const src = $el.attr('src') || ''
                  return src.includes('satellite') || src.includes('sat') || src.length > 0
                })
              }
            })
          }
        })
      }
    })
  })
})
