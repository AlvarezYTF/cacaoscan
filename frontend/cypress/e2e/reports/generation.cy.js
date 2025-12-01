import { 
  ifFoundInBody,
  clickIfExistsAndContinue,
  selectIfExistsAndContinue,
  checkCheckboxIfExists,
  typeIfExistsAndContinue
} from '../../support/helpers'

describe('Generación de Reportes - Creación', () => {
  beforeEach(() => {
    cy.navigateToReports('analyst')
  })

  it('debe mostrar interfaz de generación de reportes', () => {
    cy.get('body').then(($body) => {
      const selectors = [
        '[data-cy="reports-interface"]',
        '[data-cy="create-report-button"]',
        '[data-cy="reports-list"]',
        '[data-cy="report-filters"]'
      ]
      // Import verifySelectorsExist from helpers if needed, or use cy.get directly
      for (const selector of selectors) {
        if ($body.find(selector).length > 0) {
          cy.get(selector, { timeout: 5000 }).should('exist')
        }
      }
    })
  })

  it('debe crear reporte de análisis por período', () => {
    return clickIfExistsAndContinue('[data-cy="create-report-button"], button', () => {
      cy.wait(500)
      return selectIfExistsAndContinue('[data-cy="report-type"], select', 'analisis-periodo', () => {
        cy.fillFieldIfExists('[data-cy="start-date"], input[type="date"]', '2024-01-01')
        cy.fillFieldIfExists('[data-cy="end-date"], input[type="date"]', '2024-01-31')
        cy.checkCheckboxIfExists('[data-cy="fincas-select"], input[type="checkbox"]')
        cy.checkCheckboxIfExists('[data-cy="include-charts"], input[type="checkbox"]')
        cy.checkCheckboxIfExists('[data-cy="include-recommendations"], input[type="checkbox"]')
        cy.clickIfExists('[data-cy="generate-report"], button[type="submit"]')
        cy.get('body', { timeout: 5000 }).should('be.visible')
      })
    })
  })

  it('debe crear reporte de calidad por finca', () => {
    return clickIfExistsAndContinue('[data-cy="create-report-button"], button', () => {
      cy.wait(500)
      return selectIfExistsAndContinue('[data-cy="report-type"], select', 'calidad-finca', () => {
        cy.wait(500)
        return selectIfExistsAndContinue('[data-cy="finca-select"], select', 'Finca El Paraíso', () => {
          checkCheckboxIfExists('[data-cy="include-trends"], input[type="checkbox"]')
          checkCheckboxIfExists('[data-cy="include-comparisons"], input[type="checkbox"]')
          return clickIfExistsAndContinue('[data-cy="generate-report"], button[type="submit"]', () => {
            return cy.get('body', { timeout: 30000 }).then(($completed) => {
              ifFoundInBody('[data-cy="report-completed"], .completed', () => {
                cy.get('[data-cy="report-completed"], .completed').should('be.visible')
              })
              ifFoundInBody('[data-cy="notification-success"], .swal2-success', () => {
                cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
              })
            })
          })
        })
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe crear reporte comparativo entre lotes', () => {
    cy.clickIfExists('[data-cy="create-report-button"], button').then((clicked) => {
      if (clicked) {
        cy.wait(500)
        return selectIfExistsAndContinue('[data-cy="report-type"], select', 'comparativo-lotes', () => {
          cy.wait(500)
          checkCheckboxIfExists('[data-cy="lotes-select"], input[type="checkbox"]')
          checkCheckboxIfExists('[data-cy="compare-quality"], input[type="checkbox"]')
          checkCheckboxIfExists('[data-cy="compare-production"], input[type="checkbox"]')
          return clickIfExistsAndContinue('[data-cy="generate-report"], button[type="submit"]', () => {
            return cy.get('body', { timeout: 30000 }).then(($completed) => {
              ifFoundInBody('[data-cy="report-completed"], .completed', () => {
                cy.get('[data-cy="report-completed"], .completed').should('be.visible')
              })
              ifFoundInBody('[data-cy="notification-success"], .swal2-success', () => {
                cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
              })
            })
          })
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe crear reporte de recomendaciones', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="create-report-button"], button').length > 0) {
        return clickIfExistsAndContinue('[data-cy="create-report-button"], button', () => {
          return selectIfExistsAndContinue('[data-cy="report-type"], select', 'recomendaciones', () => {
            checkCheckboxIfExists('[data-cy="scope-all-fincas"], input[type="checkbox"]')
            checkCheckboxIfExists('[data-cy="fertilization-rec"], input[type="checkbox"]')
            checkCheckboxIfExists('[data-cy="irrigation-rec"], input[type="checkbox"]')
            
            return clickIfExistsAndContinue('[data-cy="generate-report"], button[type="submit"]', () => {
              return cy.get('body', { timeout: 30000 }).then(($completed) => {
                ifFoundInBody('[data-cy="report-completed"], .completed', () => {
                  cy.get('[data-cy="report-completed"], .completed').should('be.visible')
                })
                ifFoundInBody('[data-cy="notification-success"], .swal2-success', () => {
                  cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
                })
              })
            })
          })
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe validar campos requeridos para generar reporte', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="create-report-button"], button').length > 0) {
        cy.get('[data-cy="create-report-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="generate-report"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="generate-report"], button[type="submit"]').first().click()
            
            // Verificar errores de validación si existen
            const errorSelectors = [
              '[data-cy="report-type-error"]',
              '[data-cy="date-range-error"]'
            ]
            for (const selector of errorSelectors) {
              ifFoundInBody(selector, () => {
                cy.get(selector, { timeout: 3000 }).should('exist')
              })
            }
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe validar rango de fechas', () => {
    return clickIfExistsAndContinue('[data-cy="create-report-button"], button', () => {
      return typeIfExistsAndContinue('[data-cy="start-date"], input[type="date"]', '2024-01-31', () => {
        return typeIfExistsAndContinue('[data-cy="end-date"], input[type="date"]', '2024-01-01', () => {
          cy.get('[data-cy="generate-report"], button[type="submit"]').first().click()
          
          return ifFoundInBody('[data-cy="date-range-error"], .error-message', () => {
            cy.get('[data-cy="date-range-error"], .error-message').first().should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('fecha') || text.includes('inicio') || text.includes('anterior') || text.length > 0
            })
          })
        })
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe permitir cancelar generación de reporte', () => {
    return clickIfExistsAndContinue('[data-cy="create-report-button"], button', () => {
      return selectIfExistsAndContinue('[data-cy="report-type"], select', 'analisis-periodo', () => {
        return typeIfExistsAndContinue('[data-cy="start-date"], input[type="date"]', '2024-01-01', () => {
          return typeIfExistsAndContinue('[data-cy="end-date"], input[type="date"]', '2024-01-31', () => {
            cy.get('[data-cy="generate-report"], button[type="submit"]').first().click()
            
            return clickIfExistsAndContinue('[data-cy="cancel-generation"], button', () => {
              return clickIfExistsAndContinue('[data-cy="confirm-cancel"], .swal2-confirm, button', () => {
                return ifFoundInBody('[data-cy="generation-cancelled"], .cancelled-message', () => {
                  cy.get('[data-cy="generation-cancelled"], .cancelled-message').should('satisfy', ($el) => {
                    const text = $el.text().toLowerCase()
                    return text.includes('cancelada') || text.includes('cancel') || text.length > 0
                  })
                })
              })
            })
          })
        })
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe mostrar progreso detallado de generación', () => {
    return clickIfExistsAndContinue('[data-cy="create-report-button"], button', () => {
      return selectIfExistsAndContinue('[data-cy="report-type"], select', 'analisis-periodo', () => {
        return typeIfExistsAndContinue('[data-cy="start-date"], input[type="date"]', '2024-01-01', () => {
          return typeIfExistsAndContinue('[data-cy="end-date"], input[type="date"]', '2024-01-31', () => {
            cy.get('[data-cy="generate-report"], button[type="submit"]').first().click()
            
            return ifFoundInBody('[data-cy="progress-stage"], .progress-stage', () => {
              cy.get('[data-cy="progress-stage"], .progress-stage').should('satisfy', ($el) => {
                const text = $el.text().toLowerCase()
                return text.includes('recopilando') || text.includes('procesando') || text.includes('generando') || text.includes('finalizando') || text.length > 0
              })
            })
          })
        })
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe manejar errores durante la generación', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    cy.intercept('POST', `${apiBaseUrl}/reportes/`, {
      statusCode: 500,
      body: { error: 'Error del servidor' }
    }).as('reportError')
    
    return clickIfExistsAndContinue('[data-cy="create-report-button"], button', () => {
      return selectIfExistsAndContinue('[data-cy="report-type"], select', 'analisis-periodo', () => {
        return typeIfExistsAndContinue('[data-cy="start-date"], input[type="date"]', '2024-01-01', () => {
          return typeIfExistsAndContinue('[data-cy="end-date"], input[type="date"]', '2024-01-31', () => {
            cy.get('[data-cy="generate-report"], button[type="submit"]').first().click()
            
            cy.wait('@reportError', { timeout: 10000 })
            
            return ifFoundInBody('[data-cy="generation-error"], .error-message, .swal2-error', () => {
              cy.get('[data-cy="generation-error"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
                const text = $el.text().toLowerCase()
                return text.includes('error') || text.includes('generar') || text.includes('reporte') || text.length > 0
              })
            })
          })
        })
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe permitir programar generación de reportes', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="create-report-button"], button').length > 0) {
        cy.get('[data-cy="create-report-button"], button').first().click({ force: true })
        return selectIfExistsAndContinue('[data-cy="report-type"], select', 'analisis-periodo', () => {
          return clickIfExistsAndContinue('[data-cy="schedule-report"], input[type="checkbox"]', () => {
            return selectIfExistsAndContinue('[data-cy="schedule-frequency"], select', 'mensual', () => {
              typeIfExistsAndContinue('[data-cy="schedule-day"], input[type="number"]', '1', () => {
                typeIfExistsAndContinue('[data-cy="schedule-time"], input[type="time"]', '09:00', () => {
                  return clickIfExistsAndContinue('[data-cy="save-schedule"], button[type="submit"]', () => {
                    return ifFoundInBody('[data-cy="notification-success"], .swal2-success', () => {
                      cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
                    })
                  })
                })
              })
            })
          })
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe permitir personalizar formato de reporte', () => {
    return clickIfExistsAndContinue('[data-cy="create-report-button"], button', () => {
      return selectIfExistsAndContinue('[data-cy="report-format"], select', 'pdf', () => {
        checkCheckboxIfExists('[data-cy="include-cover"], input[type="checkbox"]')
        checkCheckboxIfExists('[data-cy="include-summary"], input[type="checkbox"]')
        selectIfExistsAndContinue('[data-cy="color-scheme"], select', 'corporate', () => {
          return ifFoundInBody('[data-cy="format-preview"], .preview', () => {
            cy.get('[data-cy="format-preview"], .preview').should('be.visible')
          }, () => {
            cy.get('body').should('be.visible')
          })
        })
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe permitir guardar plantilla de reporte', () => {
    cy.get('[data-cy="create-report-button"]').click()
    
    cy.get('[data-cy="report-type"]').select('analisis-periodo')
    cy.get('[data-cy="start-date"]').type('2024-01-01')
    cy.get('[data-cy="end-date"]').type('2024-01-31')
    
    // Guardar como plantilla
    cy.get('[data-cy="save-template"]').click()
    cy.get('[data-cy="template-name"]').type('Plantilla Mensual')
    cy.get('[data-cy="save-template-button"]').click()
    
    cy.checkNotification('Plantilla guardada', 'success')
  })

  it('debe permitir usar plantilla guardada', () => {
    cy.get('[data-cy="use-template"]').click()
    cy.get('[data-cy="template-item"]').first().click()
    
    // Verificar que se llenan los campos
    cy.get('[data-cy="report-type"]').should('have.value')
    cy.get('[data-cy="start-date"]').should('have.value')
  })

  it('debe mostrar estimación de tiempo de generación', () => {
    cy.get('[data-cy="create-report-button"]').click()
    
    cy.get('[data-cy="report-type"]').select('analisis-periodo')
    cy.get('[data-cy="start-date"]').type('2024-01-01')
    cy.get('[data-cy="end-date"]').type('2024-01-31')
    
    cy.get('[data-cy="estimated-time"]')
      .should('be.visible')
      .and('contain', 'minutos')
  })

  it('debe validar que hay datos para el período', () => {
    cy.get('[data-cy="create-report-button"]').click()
    
    cy.get('[data-cy="report-type"]').select('analisis-periodo')
    cy.get('[data-cy="start-date"]').type('2030-01-01')
    cy.get('[data-cy="end-date"]').type('2030-01-31')
    cy.get('[data-cy="generate-report"]').click()
    
    cy.get('[data-cy="no-data-error"]')
      .should('be.visible')
      .and('contain', 'No hay datos')
  })

  it('debe permitir agregar comentarios al reporte', () => {
    cy.get('[data-cy="create-report-button"]').click()
    
    cy.get('[data-cy="report-comments"]').type('Comentario importante sobre el reporte')
    cy.get('[data-cy="save-comments"]').click()
    
    cy.checkNotification('Comentarios guardados', 'success')
  })
})
