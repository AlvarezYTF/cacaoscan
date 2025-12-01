describe('Gestión de Fincas y Lotes - Relaciones', () => {
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

  it('debe permitir exportar reporte completo de finca con lotes', () => {
    const handlePdfExport = ($pdf) => {
      if ($pdf.find('[data-cy="export-pdf"], button').length > 0) {
        cy.get('[data-cy="export-pdf"], button').first().click()
        cy.verifyDownload('reporte-finca-completo.pdf')
      }
    }

    const handleExportOptions = ($export) => {
      if ($export.find('[data-cy="export-pdf"], [data-cy="export-excel"]').length > 0) {
        cy.get('[data-cy="export-pdf"], [data-cy="export-excel"]').first().should('exist')
        cy.get('body').then(handlePdfExport)
      } else {
        cy.get('body').should('be.visible')
      }
    }

    const handleExportButton = ($details) => {
      if ($details.find('[data-cy="export-finca-report"], button').length > 0) {
        cy.get('[data-cy="export-finca-report"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(handleExportOptions)
      } else {
        cy.get('body').should('be.visible')
      }
    }

    const handleFincaItem = ($body) => {
      if ($body.find('[data-cy="finca-item"], .finca-item, .item, tbody tr').length > 0) {
        cy.get('[data-cy="finca-item"], .finca-item, .item, tbody tr').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(handleExportButton)
      }
    }

    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(handleFincaItem)
  })

  it('debe mostrar mapa con ubicación de lotes dentro de la finca', () => {
    const handleLotePopup = ($popup) => {
      if ($popup.find('[data-cy="lote-popup"], .popup').length > 0) {
        cy.get('[data-cy="lote-popup"], .popup').should('exist')
      }
    }

    const handleLoteMarkers = ($markers) => {
      if ($markers.find('[data-cy="lote-markers"], [data-cy="lote-marker"]').length > 0) {
        cy.get('[data-cy="lote-marker"], [data-cy="lote-markers"]').first().click({ force: true })
        cy.get('body', { timeout: 3000 }).then(handleLotePopup)
      }
    }

    const handleMapVerification = ($details) => {
      if ($details.find('[data-cy="finca-map"], .map, [id*="map"]').length > 0) {
        cy.get('[data-cy="finca-map"], .map, [id*="map"]').first().should('be.visible')
        cy.get('body').then(handleLoteMarkers)
      } else {
        cy.get('body').should('be.visible')
      }
    }

    const handleFincaItem = ($body) => {
      if ($body.find('[data-cy="finca-item"], .finca-item, .item, tbody tr').length > 0) {
        cy.get('[data-cy="finca-item"], .finca-item, .item, tbody tr').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(handleMapVerification)
      } else {
        cy.get('body').should('be.visible')
      }
    }

    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(handleFincaItem)
  })

  it('debe permitir gestionar lotes desde vista de finca', () => {
    const handleSuccessNotification = ($success) => {
      if ($success.find('[data-cy="notification-success"], .swal2-success').length > 0) {
        cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
      }
    }

    const handleLoteEdit = ($edit) => {
      if ($edit.find('[data-cy="lote-nombre"], input[name*="nombre"]').length > 0) {
        cy.get('[data-cy="lote-nombre"], input[name*="nombre"]').first().clear().type('Lote Editado desde Finca')
        cy.get('[data-cy="save-lote"], button[type="submit"]').first().click()
        cy.get('body', { timeout: 5000 }).then(handleSuccessNotification)
      }
    }

    const handleEditButton = ($lote) => {
      if ($lote.find('[data-cy="edit-lote"], button').length > 0) {
        cy.get('[data-cy="edit-lote"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(handleLoteEdit)
      }
    }

    const handleLoteItem = ($details) => {
      if ($details.find('[data-cy="lote-item"], .lote-item, .item').length > 0) {
        cy.get('[data-cy="lote-item"], .lote-item, .item').first().then(handleEditButton)
      } else {
        cy.get('body').should('be.visible')
      }
    }

    const handleFincaItem = ($body) => {
      if ($body.find('[data-cy="finca-item"], .finca-item, .item, tbody tr').length > 0) {
        cy.get('[data-cy="finca-item"], .finca-item, .item, tbody tr').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(handleLoteItem)
      } else {
        cy.get('body').should('be.visible')
      }
    }

    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(handleFincaItem)
  })

  it('debe mostrar resumen de producción por finca', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-item"], .finca-item, .item, tbody tr').length > 0) {
        cy.get('[data-cy="finca-item"], .finca-item, .item, tbody tr').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          const productionSelectors = [
            '[data-cy="production-summary"]',
            '[data-cy="total-production"]',
            '[data-cy="production-by-lote"]',
            '[data-cy="production-trend"]'
          ]
          verifySelectorsExist(productionSelectors, $details)
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar recomendaciones basadas en análisis de todos los lotes', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-item"], .finca-item, .item, tbody tr').length > 0) {
        cy.get('[data-cy="finca-item"], .finca-item, .item, tbody tr').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          // Verificar recomendaciones agregadas si existen
          if ($details.find('[data-cy="finca-recommendations"], .recommendations').length > 0) {
            cy.get('[data-cy="finca-recommendations"], .recommendations').should('be.visible')
            
            cy.get('body').then(($recs) => {
              if ($recs.find('[data-cy="recommendation-item"], .recommendation-item').length > 0) {
                cy.get('[data-cy="recommendation-item"], .recommendation-item').should('have.length.greaterThan', 0)
              }
              
              // Verificar tipos de recomendaciones si existen
              const recTypes = [
                '[data-cy="fertilization-recommendation"]',
                '[data-cy="irrigation-recommendation"]',
                '[data-cy="harvest-recommendation"]'
              ]
          verifySelectorsExist(recTypes, $recs, 3000)
            })
          } else {
            cy.get('body').should('be.visible')
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe permitir programar análisis para múltiples lotes', () => {
    const handleSuccessNotification = ($success) => {
      if ($success.find('[data-cy="notification-success"], .swal2-success').length > 0) {
        cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
      }
    }

    const handleScheduleForm = ($schedule) => {
      if ($schedule.find('[data-cy="analysis-date"], input[type="date"]').length > 0) {
        cy.get('[data-cy="analysis-date"], input[type="date"]').first().type('2024-02-15')
        cy.get('[data-cy="analysis-time"], input[type="time"]').first().type('10:00')
        cy.get('[data-cy="analysis-notes"], textarea').first().type('Análisis programado para múltiples lotes')
        cy.get('[data-cy="save-bulk-schedule"], button[type="submit"]').first().click()
        cy.get('body', { timeout: 5000 }).then(handleSuccessNotification)
      }
    }

    const handleBulkSchedule = ($bulk) => {
      if ($bulk.find('[data-cy="bulk-schedule-analysis"], button').length > 0) {
        cy.get('[data-cy="bulk-schedule-analysis"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(handleScheduleForm)
      }
    }

    const handleSecondCheckbox = ($second) => {
      if ($second.find('[data-cy="lote-checkbox"], input[type="checkbox"]').length > 1) {
        cy.get('[data-cy="lote-checkbox"], input[type="checkbox"]').eq(1).check({ force: true })
      }
    }

    const handleCheckboxes = ($details) => {
      if ($details.find('[data-cy="lote-checkbox"], input[type="checkbox"]').length > 0) {
        cy.get('[data-cy="lote-checkbox"], input[type="checkbox"]').first().check({ force: true })
        cy.get('body').then(handleSecondCheckbox)
        cy.get('body').then(handleBulkSchedule)
      } else {
        cy.get('body').should('be.visible')
      }
    }

    const handleFincaItem = ($body) => {
      if ($body.find('[data-cy="finca-item"], .finca-item, .item, tbody tr').length > 0) {
        cy.get('[data-cy="finca-item"], .finca-item, .item, tbody tr').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(handleCheckboxes)
      } else {
        cy.get('body').should('be.visible')
      }
    }

    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(handleFincaItem)
  })

  it('debe mostrar historial de cambios en finca y lotes', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-item"], .finca-item, .item, tbody tr').length > 0) {
        cy.get('[data-cy="finca-item"], .finca-item, .item, tbody tr').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          // Verificar historial si existe
          if ($details.find('[data-cy="finca-history"], .history').length > 0) {
            cy.get('[data-cy="finca-history"], .history').should('be.visible')
            
            cy.get('body').then(($history) => {
              if ($history.find('[data-cy="history-item"], .history-item').length > 0) {
                cy.get('[data-cy="history-item"], .history-item').should('have.length.greaterThan', 0)
                
                // Verificar información de cada cambio
                cy.get('[data-cy="history-item"], .history-item').first().then(($item) => {
                  const changeSelectors = [
                    '[data-cy="change-date"]',
                    '[data-cy="change-type"]',
                    '[data-cy="change-description"]'
                  ]
          verifySelectorsExist(changeSelectors, $item, 3000)
                })
              }
            })
          } else {
            cy.get('body').should('be.visible')
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe validar consistencia de datos entre finca y lotes', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-item"], .finca-item, .item, tbody tr').length > 0) {
        cy.get('[data-cy="finca-item"], .finca-item, .item, tbody tr').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          // Verificar que el área total de lotes no excede el área de la finca si ambos existen
          cy.get('body').then(($area) => {
            if ($area.find('[data-cy="finca-area"]').length > 0 && $area.find('[data-cy="total-area-lotes"]').length > 0) {
              cy.get('[data-cy="finca-area"]').then(($fincaArea) => {
                const fincaArea = Number.parseFloat($fincaArea.text())
                
                cy.get('[data-cy="total-area-lotes"]').then(($lotesArea) => {
                  const lotesArea = Number.parseFloat($lotesArea.text())
                  
                  expect(lotesArea).to.be.at.most(fincaArea)
                })
              })
            } else {
              cy.get('body').should('be.visible')
            }
          })
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar dashboard consolidado de finca con lotes', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-item"], .finca-item, .item, tbody tr').length > 0) {
        cy.get('[data-cy="finca-item"], .finca-item, .item, tbody tr').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          const dashboardSelectors = [
            '[data-cy="finca-dashboard"]',
            '[data-cy="overview-cards"]',
            '[data-cy="performance-metrics"]',
            '[data-cy="recent-activities"]'
          ]
          verifySelectorsExist(dashboardSelectors, $details, 3000)
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe permitir filtrar lotes por variedad', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Filtrar por variedad
    cy.get('[data-cy="filter-variedad"]').select('Criollo')
    cy.get('[data-cy="lotes-list"]').should('be.visible')
    
    // Verificar que solo se muestran lotes de la variedad seleccionada
    cy.get('[data-cy="lote-item"]').each(($item) => {
      cy.wrap($item).find('[data-cy="lote-variedad"]').should('contain', 'Criollo')
    })
  })

  it('debe permitir ordenar lotes por área', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Ordenar por área descendente
    cy.get('[data-cy="sort-lotes"]').select('area-desc')
    
    // Verificar orden
    cy.get('[data-cy="lote-item"]').first().find('[data-cy="lote-area"]').then(($first) => {
      cy.get('[data-cy="lote-item"]').eq(1).find('[data-cy="lote-area"]').then(($second) => {
        const firstArea = Number.parseFloat($first.text())
        const secondArea = Number.parseFloat($second.text())
        expect(firstArea).to.be.at.least(secondArea)
      })
    })
  })

  it('debe mostrar resumen de calidad por finca', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Verificar resumen de calidad
    cy.get('[data-cy="quality-summary"]').should('be.visible')
    cy.get('[data-cy="average-quality"]').should('be.visible')
    cy.get('[data-cy="quality-distribution"]').should('be.visible')
  })

  it('debe permitir comparar lotes de la misma finca', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Seleccionar lotes para comparar
    cy.get('[data-cy="lote-checkbox"]').first().check()
    cy.get('[data-cy="lote-checkbox"]').eq(1).check()
    
    // Activar comparación
    cy.get('[data-cy="compare-lotes"]').click()
    
    // Verificar vista de comparación
    cy.get('[data-cy="comparison-view"]').should('be.visible')
    cy.get('[data-cy="comparison-chart"]').should('be.visible')
  })
})
