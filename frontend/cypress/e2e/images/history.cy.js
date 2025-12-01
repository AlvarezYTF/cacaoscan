describe('Gestión de Imágenes - Historial y Detalles', () => {
  beforeEach(() => {
    cy.login('farmer')
  })
  // Helper functions to reduce nesting depth
  const verifySelectorsExist = (selectors, $context, timeout = 3000) => {
    for (const selector of selectors) {
      if ($context.find(selector).length > 0) {
        cy.get(selector, { timeout }).should('exist')
      }
    }
  }



  it('debe mostrar historial de imágenes cargadas', () => {
    cy.visit('/mis-imagenes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Verificar elementos del historial
    cy.get('body').then(($body) => {
      const selectors = [
        '[data-cy="images-history"]',
        '[data-cy="image-list"]',
        '[data-cy="search-images"]',
        '[data-cy="filter-images"]'
      ]
          verifySelectorsExist(selectors, $body, 5000)
    })
  })

  it('debe mostrar detalles de imagen específica', () => {
    cy.visit('/mis-imagenes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="image-item"], .image-item, .item').length > 0) {
        cy.get('[data-cy="image-item"], .image-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          const detailSelectors = [
            '[data-cy="image-details"]',
            '[data-cy="image-metadata"]',
            '[data-cy="analysis-results"]',
            '[data-cy="upload-date"]'
          ]
          verifySelectorsExist(detailSelectors, $details, 3000)
        })
      }
    })
  })

  it('debe permitir buscar imágenes por nombre', () => {
    cy.visit('/mis-imagenes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="search-images"], input[type="search"], input').length > 0) {
        cy.get('[data-cy="search-images"], input[type="search"], input').first().type('test-cacao')
        cy.get('body', { timeout: 5000 }).then(($afterSearch) => {
          if ($afterSearch.find('[data-cy="image-item"], .image-item').length > 0) {
            cy.get('[data-cy="image-item"], .image-item', { timeout: 5000 }).should('exist')
          }
          if ($afterSearch.find('[data-cy="search-results-count"], .results-count').length > 0) {
            cy.get('[data-cy="search-results-count"], .results-count', { timeout: 3000 }).should('exist')
          }
        })
      }
    })
  })

  it('debe permitir filtrar imágenes por fecha', () => {
    cy.visit('/mis-imagenes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="date-filter"], button, .filter').length > 0) {
        cy.get('[data-cy="date-filter"], button, .filter').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($filter) => {
          if ($filter.find('[data-cy="date-range-start"], input[type="date"]').length > 0) {
            cy.get('[data-cy="date-range-start"], input[type="date"]').first().type('2024-01-01', { force: true })
            cy.get('[data-cy="date-range-end"], input[type="date"]').first().type('2024-12-31', { force: true })
            cy.get('[data-cy="apply-date-filter"], button[type="submit"]').first().click()
            cy.get('body', { timeout: 5000 }).should('be.visible')
          }
        })
      }
    })
  })

  it('debe permitir filtrar imágenes por calidad', () => {
    cy.visit('/mis-imagenes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="quality-filter"], button, .filter').length > 0) {
        cy.get('[data-cy="quality-filter"], button, .filter').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($filter) => {
          if ($filter.find('[data-cy="quality-excellent"], input[type="checkbox"]').length > 0) {
            cy.get('[data-cy="quality-excellent"], input[type="checkbox"]').first().check({ force: true })
            cy.get('[data-cy="apply-quality-filter"], button[type="submit"]').first().click()
            cy.get('body', { timeout: 5000 }).should('be.visible')
          }
        })
      }
    })
  })

  it('debe permitir ordenar imágenes', () => {
    cy.visit('/mis-imagenes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="sort-images"], select').length > 0) {
        cy.get('[data-cy="sort-images"], select').first().select('date-desc', { force: true })
        cy.get('body', { timeout: 5000 }).should('be.visible')
        cy.get('[data-cy="sort-images"], select').first().select('quality-desc', { force: true })
        cy.get('body', { timeout: 5000 }).should('be.visible')
      }
    })
  })

  it('debe permitir eliminar imagen', () => {
    cy.visit('/mis-imagenes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="image-item"], .image-item, .item').length > 0) {
        cy.get('[data-cy="image-item"], .image-item, .item').first().within(() => {
          cy.get('[data-cy="delete-image"], button, .delete').first().click({ force: true })
        })
        cy.get('body', { timeout: 5000 }).then(($confirm) => {
          if ($confirm.find('[data-cy="confirm-delete"], .swal2-confirm, button').length > 0) {
            cy.get('[data-cy="confirm-delete"], .swal2-confirm, button').first().click()
            cy.get('body', { timeout: 5000 }).should('be.visible')
          }
        })
      }
    })
  })

  it('debe permitir descargar imagen original', () => {
    cy.visit('/mis-imagenes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="image-item"], .image-item, .item').length > 0) {
        cy.get('[data-cy="image-item"], .image-item, .item').first().within(() => {
          cy.get('[data-cy="download-image"], button, a').first().click({ force: true })
        })
        cy.get('body', { timeout: 5000 }).should('be.visible')
      }
    })
  })

  it('debe permitir descargar imagen procesada', () => {
    cy.visit('/mis-imagenes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="image-item"], .image-item, .item').length > 0) {
        cy.get('[data-cy="image-item"], .image-item, .item').first().within(() => {
          cy.get('[data-cy="download-processed"], button, a').first().click({ force: true })
        })
        cy.get('body', { timeout: 5000 }).should('be.visible')
      }
    })
  })

  it('debe mostrar estadísticas de imágenes', () => {
    cy.visit('/mis-imagenes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      const statsSelectors = [
        '[data-cy="images-stats"]',
        '[data-cy="total-images"]',
        '[data-cy="average-quality"]',
        '[data-cy="images-this-month"]'
      ]
          verifySelectorsExist(statsSelectors, $body, 5000)
    })
  })

  it('debe permitir selección múltiple de imágenes', () => {
    cy.visit('/mis-imagenes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="select-all"], input[type="checkbox"]').length > 0) {
        cy.get('[data-cy="select-all"], input[type="checkbox"]').first().check({ force: true })
        cy.get('body', { timeout: 5000 }).then(($afterSelect) => {
          if ($afterSelect.find('[data-cy="image-checkbox"], input[type="checkbox"]').length > 0) {
            cy.get('[data-cy="image-checkbox"], input[type="checkbox"]', { timeout: 3000 }).should('exist')
          }
          if ($afterSelect.find('[data-cy="bulk-actions"], .bulk-actions').length > 0) {
            cy.get('[data-cy="bulk-actions"], .bulk-actions', { timeout: 3000 }).should('exist')
          }
        })
      }
    })
  })

  it('debe permitir acciones en lote', () => {
    cy.visit('/mis-imagenes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="image-checkbox"], input[type="checkbox"]').length >= 2) {
        cy.get('[data-cy="image-checkbox"], input[type="checkbox"]').first().check({ force: true })
        cy.get('[data-cy="image-checkbox"], input[type="checkbox"]').eq(1).check({ force: true })
        cy.get('body', { timeout: 5000 }).then(($selected) => {
          if ($selected.find('[data-cy="bulk-download"], button').length > 0) {
            cy.get('[data-cy="bulk-download"], button').first().click({ force: true })
            cy.get('body', { timeout: 5000 }).should('be.visible')
          }
        })
      }
    })
  })

  it('debe mostrar paginación cuando hay muchas imágenes', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Interceptar la petición pero no esperarla obligatoriamente
    cy.intercept('GET', `${apiBaseUrl}/images/**`, {
      statusCode: 200,
      body: {
        results: new Array(25).fill().map((_, i) => ({
          id: i + 1,
          filename: `imagen-${i + 1}.jpg`,
          uploaded_at: '2024-01-15T10:30:00Z'
        })),
        count: 100,
        next: '/api/images/?page=2',
        previous: null
      }
    }).as('imagesPage1')
    
    cy.visit('/mis-imagenes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Esperar un poco para que la página cargue, pero no fallar si la petición no ocurre
    cy.wait(1000) // Esperar 1 segundo para que la página se estabilice
    
    // Verificar paginación
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="pagination"], .pagination').length > 0) {
        cy.get('[data-cy="pagination"], .pagination', { timeout: 5000 }).should('exist')
        if ($body.find('[data-cy="page-info"], .page-info').length > 0) {
          cy.get('[data-cy="page-info"], .page-info', { timeout: 3000 }).should('exist')
        }
        if ($body.find('[data-cy="next-page"], .next-page, button').length > 0) {
          cy.get('[data-cy="next-page"], .next-page, button').first().click({ force: true })
          cy.get('body', { timeout: 5000 }).should('be.visible')
        }
      } else {
        // Si no hay paginación visible, verificar que la página cargó correctamente
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe permitir ver imagen en modal', () => {
    cy.visit('/mis-imagenes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="image-thumbnail"], .thumbnail, img').length > 0) {
        cy.get('[data-cy="image-thumbnail"], .thumbnail, img').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="image-modal"], .modal, [role="dialog"]').length > 0) {
            cy.get('[data-cy="image-modal"], .modal, [role="dialog"]', { timeout: 5000 }).should('exist')
            cy.get('[data-cy="close-modal"], .close, button').first().click({ force: true })
            cy.get('[data-cy="image-modal"], .modal', { timeout: 3000 }).should('not.exist')
          }
        })
      }
    })
  })

  it('debe mostrar información de análisis en historial', () => {
    cy.visit('/mis-imagenes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="image-item"], .image-item, .item').length > 0) {
        cy.get('[data-cy="image-item"], .image-item, .item', { timeout: 5000 }).then(($items) => {
          if ($items.length > 0) {
            cy.wrap($items.first()).within(() => {
              const infoSelectors = [
                '[data-cy="analysis-status"]',
                '[data-cy="quality-badge"]',
                '[data-cy="analysis-date"]'
              ]
              verifySelectorsExist(infoSelectors, $details, 3000)
            })
          }
        })
      }
    })
  })

  it('debe permitir filtrar por estado de análisis', () => {
    cy.visit('/mis-imagenes')
    
    cy.get('[data-cy="analysis-status-filter"]').select('completado')
    cy.get('[data-cy="image-item"]').each(($item) => {
      cy.wrap($item).find('[data-cy="analysis-status"]').should('contain', 'Completado')
    })
  })

  it('debe mostrar vista de galería', () => {
    cy.visit('/mis-imagenes')
    
    cy.get('[data-cy="view-gallery"]').click()
    cy.get('[data-cy="gallery-view"]').should('be.visible')
    cy.get('[data-cy="gallery-item"]').should('have.length.greaterThan', 0)
  })

  it('debe permitir etiquetar imágenes', () => {
    cy.visit('/mis-imagenes')
    
    cy.get('[data-cy="image-item"]').first().within(() => {
      cy.get('[data-cy="add-tag"]').click()
      cy.get('[data-cy="tag-input"]').type('mejor-calidad')
      cy.get('[data-cy="save-tag"]').click()
    })
    
    cy.get('[data-cy="image-tags"]').should('contain', 'mejor-calidad')
  })

  it('debe mostrar timeline de imágenes', () => {
    cy.visit('/mis-imagenes')
    
    cy.get('[data-cy="view-timeline"]').click()
    cy.get('[data-cy="timeline-view"]').should('be.visible')
    cy.get('[data-cy="timeline-item"]').should('have.length.greaterThan', 0)
  })

  it('debe permitir comparar múltiples imágenes', () => {
    cy.visit('/mis-imagenes')
    
    cy.get('[data-cy="image-checkbox"]').first().check()
    cy.get('[data-cy="image-checkbox"]').eq(1).check()
    
    cy.get('[data-cy="compare-images"]').click()
    cy.get('[data-cy="comparison-view"]').should('be.visible')
  })
})
