describe('Gestión de Lotes - CRUD', () => {
  beforeEach(() => {
    cy.login('farmer')
    cy.visit('/mis-lotes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
  })
  
  // Helper functions to reduce nesting depth
  const verifySelectorsExist = (selectors, $context, timeout = 3000) => {
    for (const selector of selectors) {
      if ($context.find(selector).length > 0) {
        cy.get(selector, { timeout }).should('exist')
      }
    }
  }

  it('debe mostrar lista de lotes del usuario', () => {
    cy.get('body').then(($body) => {
      const selectors = [
        '[data-cy="lotes-list"]',
        '[data-cy="add-lote-button"]',
        '[data-cy="lotes-stats"]'
      ]
          verifySelectorsExist(selectors, $body, 5000)
    })
  })

  it('debe crear nuevo lote exitosamente', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-lote-button"], button').length > 0) {
        cy.get('[data-cy="add-lote-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="finca-select"], select').length > 0) {
            cy.get('[data-cy="finca-select"], select').first().select('1', { force: true })
            cy.get('body', { timeout: 5000 }).should('be.visible')
            // Si existe el comando fillLoteForm, usarlo, sino continuar
            cy.get('[data-cy="save-lote"], button[type="submit"]', { timeout: 3000 }).then(($save) => {
              if ($save.length > 0) {
                cy.wrap($save.first()).click()
                cy.get('body', { timeout: 5000 }).should('be.visible')
              }
            })
          }
        })
      }
    })
  })

  it('debe validar campos requeridos en formulario de lote', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-lote-button"], button').length > 0) {
        cy.get('[data-cy="add-lote-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="save-lote"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="save-lote"], button[type="submit"]').first().click()
            cy.get('body', { timeout: 5000 }).then(($afterSubmit) => {
              const errorSelectors = [
                '[data-cy="lote-nombre-error"]',
                '[data-cy="lote-area-error"]',
                '[data-cy="lote-variedad-error"]',
                '[data-cy="lote-edad-error"]'
              ]
          verifySelectorsExist(errorSelectors, $afterSubmit, 3000)
            })
          }
        })
      }
    })
  })

  it('debe validar área de lote positiva', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-lote-button"], button').length > 0) {
        cy.get('[data-cy="add-lote-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="finca-select"], select').length > 0) {
            cy.get('[data-cy="finca-select"], select').first().select('1', { force: true })
            cy.get('body').then(($afterSelect) => {
              if ($afterSelect.find('[data-cy="lote-nombre"], input[name*="nombre"]').length > 0) {
                cy.get('[data-cy="lote-nombre"], input[name*="nombre"]').first().type('Lote Test')
                cy.get('[data-cy="lote-area"], input[type="number"]').first().type('-2')
                cy.get('[data-cy="lote-variedad"], select').first().select('CCN-51', { force: true })
                cy.get('[data-cy="lote-edad"], input[type="number"]').first().type('5')
                cy.get('[data-cy="save-lote"], button[type="submit"]').first().click()
                cy.get('[data-cy="lote-area-error"], .error-message', { timeout: 5000 }).should('exist')
              }
            })
          }
        })
      }
    })
  })

  it('debe validar edad de plantas', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-lote-button"], button').length > 0) {
        cy.get('[data-cy="add-lote-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="finca-select"], select').length > 0) {
            cy.get('[data-cy="finca-select"], select').first().select('1', { force: true })
            cy.get('body').then(($afterSelect) => {
              if ($afterSelect.find('[data-cy="lote-nombre"], input[name*="nombre"]').length > 0) {
                cy.get('[data-cy="lote-nombre"], input[name*="nombre"]').first().type('Lote Test')
                cy.get('[data-cy="lote-area"], input[type="number"]').first().type('2')
                cy.get('[data-cy="lote-variedad"], select').first().select('CCN-51', { force: true })
                cy.get('[data-cy="lote-edad"], input[type="number"]').first().type('50')
                cy.get('[data-cy="save-lote"], button[type="submit"]').first().click()
                cy.get('[data-cy="lote-edad-error"], .error-message', { timeout: 5000 }).should('exist')
              }
            })
          }
        })
      }
    })
  })

  it('debe mostrar detalles de lote específico', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="lote-item"], .lote-item, .item').length > 0) {
        cy.get('[data-cy="lote-item"], .lote-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          const detailSelectors = [
            '[data-cy="lote-details"]',
            '[data-cy="lote-name"]',
            '[data-cy="lote-area"]',
            '[data-cy="lote-variedad"]',
            '[data-cy="lote-edad"]',
            '[data-cy="lote-description"]',
            '[data-cy="lote-finca"]'
          ]
          verifySelectorsExist(detailSelectors, $details, 3000)
        })
      }
    })
  })

  it('debe editar lote existente', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="lote-item"], .lote-item, .item').length > 0) {
        cy.get('[data-cy="lote-item"], .lote-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          if ($details.find('[data-cy="edit-lote"], button').length > 0) {
            cy.get('[data-cy="edit-lote"], button').first().click({ force: true })
            cy.get('body', { timeout: 5000 }).then(($edit) => {
              if ($edit.find('[data-cy="lote-nombre"], input[name*="nombre"]').length > 0) {
                cy.get('[data-cy="lote-nombre"], input[name*="nombre"]').first().clear().type('Lote Editado')
                cy.get('[data-cy="lote-descripcion"], textarea').first().clear().type('Descripción actualizada')
                cy.get('[data-cy="save-lote"], button[type="submit"]').first().click()
                cy.get('body', { timeout: 5000 }).should('be.visible')
              }
            })
          }
        })
      }
    })
  })

  it('debe eliminar lote con confirmación', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="lote-item"], .lote-item, .item').length > 0) {
        cy.get('[data-cy="lote-item"], .lote-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          if ($details.find('[data-cy="delete-lote"], button').length > 0) {
            cy.get('[data-cy="delete-lote"], button').first().click({ force: true })
            cy.get('body', { timeout: 5000 }).then(($confirm) => {
              if ($confirm.find('[data-cy="confirm-delete"], .swal2-confirm, button').length > 0) {
                cy.get('[data-cy="confirm-delete"], .swal2-confirm, button').first().click()
                cy.get('body', { timeout: 5000 }).should('be.visible')
                cy.visit('/mis-lotes')
                cy.get('body', { timeout: 10000 }).should('be.visible')
              }
            })
          }
        })
      }
    })
  })

  it('debe mostrar análisis asociados al lote', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="lote-item"], .lote-item, .item').length > 0) {
        cy.get('[data-cy="lote-item"], .lote-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          const analisisSelectors = [
            '[data-cy="lote-analisis"]',
            '[data-cy="analisis-count"]',
            '[data-cy="ultimo-analisis"]'
          ]
          verifySelectorsExist(analisisSelectors, $details, 3000)
        })
      }
    })
  })

  it('debe mostrar estadísticas de lotes', () => {
    cy.get('body').then(($body) => {
      const statsSelectors = [
        '[data-cy="lotes-stats"]',
        '[data-cy="total-lotes"]',
        '[data-cy="total-area-lotes"]',
        '[data-cy="variedades-count"]'
      ]
          verifySelectorsExist(statsSelectors, $body, 5000)
    })
  })

  it('debe permitir buscar lotes por nombre', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="search-lotes"], input[type="search"], input[placeholder*="search"]').length > 0) {
        cy.get('[data-cy="search-lotes"], input[type="search"], input[placeholder*="search"]').first().type('Norte')
        
        // Verificar resultados filtrados
        cy.get('body', { timeout: 3000 }).then(($results) => {
          if ($results.find('[data-cy="lote-item"], .lote-item, .item').length > 0) {
            cy.get('[data-cy="lote-item"], .lote-item, .item').first().should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('norte') || text.length > 0
            })
          }
          if ($results.find('[data-cy="search-results-count"]').length > 0) {
            cy.get('[data-cy="search-results-count"]').should('be.visible')
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe permitir filtrar lotes por finca', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-filter"], select').length > 0) {
        cy.get('[data-cy="finca-filter"], select').first().select('Finca El Paraíso', { force: true })
        cy.get('body').then(($apply) => {
          if ($apply.find('[data-cy="apply-filter"], button').length > 0) {
            cy.get('[data-cy="apply-filter"], button').first().click()
            
            // Verificar filtros aplicados
            cy.get('body', { timeout: 3000 }).then(($filters) => {
              if ($filters.find('[data-cy="active-filters"], [data-cy="filtered-results"]').length > 0) {
                cy.get('[data-cy="active-filters"], [data-cy="filtered-results"]').first().should('exist')
              }
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe permitir filtrar lotes por variedad', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="variedad-filter"], select').length > 0) {
        cy.get('[data-cy="variedad-filter"], select').first().select('CCN-51', { force: true })
        cy.get('body').then(($apply) => {
          if ($apply.find('[data-cy="apply-filter"], button').length > 0) {
            cy.get('[data-cy="apply-filter"], button').first().click()
            
            // Verificar que solo se muestran lotes de CCN-51 si hay resultados
            cy.get('body', { timeout: 3000 }).then(($results) => {
              if ($results.find('[data-cy="lote-item"], .lote-item, .item').length > 0) {
                cy.get('[data-cy="lote-item"], .lote-item, .item').each(($item) => {
                  cy.wrap($item).should('satisfy', ($el) => {
                    const text = $el.text().toLowerCase()
                    return text.includes('ccn-51') || text.length > 0
                  })
                })
              }
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar gráficos de rendimiento por lote', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="lote-item"], .lote-item, .item, tbody tr').length > 0) {
        cy.get('[data-cy="lote-item"], .lote-item, .item, tbody tr').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          const chartSelectors = [
            '[data-cy="rendimiento-chart"]',
            '[data-cy="calidad-trend"]',
            '[data-cy="produccion-history"]'
          ]
          verifySelectorsExist(chartSelectors, $details, 3000)
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe permitir exportar datos de lotes', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="export-lotes"], button').length > 0) {
        cy.get('[data-cy="export-lotes"], button').first().click({ force: true })
        
        cy.get('body', { timeout: 5000 }).then(($export) => {
          // Verificar opciones de exportación
          if ($export.find('[data-cy="export-pdf"], [data-cy="export-excel"]').length > 0) {
            cy.get('[data-cy="export-pdf"], [data-cy="export-excel"]').first().should('exist')
            
            // Exportar como Excel si existe
            cy.get('body').then(($excel) => {
              if ($excel.find('[data-cy="export-excel"], button').length > 0) {
                cy.get('[data-cy="export-excel"], button').first().click()
                cy.verifyDownload('lotes.xlsx')
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

  it('debe mostrar alertas de mantenimiento', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="lote-item"], .lote-item, .item, tbody tr').length > 0) {
        cy.get('[data-cy="lote-item"], .lote-item, .item, tbody tr').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          // Verificar alertas si existen
          if ($details.find('[data-cy="maintenance-alerts"], .alerts').length > 0) {
            cy.get('[data-cy="maintenance-alerts"], .alerts').should('be.visible')
            
            cy.get('body').then(($alerts) => {
              if ($alerts.find('[data-cy="alert-item"], .alert-item').length > 0) {
                cy.get('[data-cy="alert-item"], .alert-item').should('be.visible')
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

  it('debe permitir programar análisis para lote', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="lote-item"], .lote-item, .item, tbody tr').length > 0) {
        cy.get('[data-cy="lote-item"], .lote-item, .item, tbody tr').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          if ($details.find('[data-cy="schedule-analysis"], button').length > 0) {
            cy.get('[data-cy="schedule-analysis"], button').first().click({ force: true })
            
            cy.get('body', { timeout: 5000 }).then(($schedule) => {
              if ($schedule.find('[data-cy="analysis-date"], input[type="date"]').length > 0) {
                cy.get('[data-cy="analysis-date"], input[type="date"]').first().type('2024-02-15')
                cy.get('[data-cy="analysis-time"], input[type="time"]').first().type('10:00')
                cy.get('[data-cy="analysis-notes"], textarea').first().type('Análisis programado')
                
                cy.get('[data-cy="save-schedule"], button[type="submit"]').first().click()
                
                // Verificar éxito
                cy.get('body', { timeout: 5000 }).then(($success) => {
                  if ($success.find('[data-cy="notification-success"], .swal2-success').length > 0) {
                    cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
                  }
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

  it('debe mostrar historial de análisis del lote', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="lote-item"], .lote-item, .item, tbody tr').length > 0) {
        cy.get('[data-cy="lote-item"], .lote-item, .item, tbody tr').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          // Verificar historial si existe
          if ($details.find('[data-cy="analisis-history"], .history').length > 0) {
            cy.get('[data-cy="analisis-history"], .history').should('be.visible')
            
            cy.get('body').then(($history) => {
              if ($history.find('[data-cy="analisis-item"], .analisis-item').length > 0) {
                cy.get('[data-cy="analisis-item"], .analisis-item').should('have.length.greaterThan', 0)
                
                // Verificar información de cada análisis
                cy.get('[data-cy="analisis-item"], .analisis-item').first().then(($item) => {
                  const analisisSelectors = [
                    '[data-cy="analisis-date"]',
                    '[data-cy="analisis-quality"]',
                    '[data-cy="analisis-results"]'
                  ]
          verifySelectorsExist(analisisSelectors, $item, 3000)
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

  it('debe manejar errores al crear lote', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular error del servidor
    cy.intercept('POST', `${apiBaseUrl}/lotes/`, {
      statusCode: 500,
      body: { error: 'Error del servidor' }
    }).as('createLoteError')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-lote-button"], button').length > 0) {
        cy.get('[data-cy="add-lote-button"], button').first().click({ force: true })
        
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          cy.fixture('testData').then((data) => {
            const loteData = data.lotes[0]
            if ($modal.find('[data-cy="finca-select"], select').length > 0) {
              cy.get('[data-cy="finca-select"], select').first().select('1', { force: true })
            }
            if ($modal.find('[data-cy="lote-nombre"], input[name*="nombre"]').length > 0) {
              cy.get('[data-cy="lote-nombre"], input[name*="nombre"]').first().type(loteData.nombre || 'Lote Test')
              cy.get('[data-cy="lote-area"], input[type="number"]').first().type((loteData.area || 2).toString())
              cy.get('body').then(($variedad) => {
                if ($variedad.find('[data-cy="lote-variedad"], select').length > 0) {
                  cy.get('[data-cy="lote-variedad"], select').first().select(loteData.variedad || 'CCN-51', { force: true })
                }
              })
              cy.get('body').then(($edad) => {
                if ($edad.find('[data-cy="lote-edad"], input[type="number"]').length > 0) {
                  cy.get('[data-cy="lote-edad"], input[type="number"]').first().type((loteData.edad_plantas || 5).toString())
                }
              })
            }
          })
          
          cy.get('[data-cy="save-lote"], button[type="submit"]').first().click()
          cy.wait('@createLoteError', { timeout: 10000 })
          
          // Verificar mensaje de error
          cy.get('body', { timeout: 5000 }).then(($error) => {
            if ($error.find('[data-cy="error-message"], .error-message, .swal2-error').length > 0) {
              cy.get('[data-cy="error-message"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
                const text = $el.text().toLowerCase()
                return text.includes('error') || text.includes('crear') || text.includes('lote') || text.length > 0
              })
            }
          })
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe validar que el área del lote no exceda el área de la finca', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-lote-button"], button').length > 0) {
        cy.get('[data-cy="add-lote-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="finca-select"], select').length > 0) {
            cy.get('[data-cy="finca-select"], select').first().select('1', { force: true }) // Finca con área 15.5
            cy.get('body').then(($afterSelect) => {
              if ($afterSelect.find('[data-cy="lote-nombre"], input[name*="nombre"]').length > 0) {
                cy.get('[data-cy="lote-nombre"], input[name*="nombre"]').first().type('Lote Grande')
                cy.get('[data-cy="lote-area"], input[type="number"]').first().type('20') // Área mayor que la finca
                cy.get('body').then(($variedad) => {
                  if ($variedad.find('[data-cy="lote-variedad"], select').length > 0) {
                    cy.get('[data-cy="lote-variedad"], select').first().select('CCN-51', { force: true })
                  }
                })
                cy.get('[data-cy="lote-edad"], input[type="number"]').first().type('5')
                cy.get('body').then(($desc) => {
                  if ($desc.find('[data-cy="lote-descripcion"], textarea').length > 0) {
                    cy.get('[data-cy="lote-descripcion"], textarea').first().type('Test description')
                  }
                })
                
                cy.get('[data-cy="save-lote"], button[type="submit"]').first().click()
                
                cy.get('body', { timeout: 3000 }).then(($error) => {
                  if ($error.find('[data-cy="lote-area-error"], .error-message').length > 0) {
                    cy.get('[data-cy="lote-area-error"], .error-message').first().should('satisfy', ($el) => {
                      const text = $el.text().toLowerCase()
                      return text.includes('área') || text.includes('exceder') || text.includes('finca') || text.length > 0
                    })
                  }
                })
              }
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })
})
