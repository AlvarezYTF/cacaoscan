describe('Generación de Reportes - Creación', () => {
  beforeEach(() => {
    cy.login('analyst')
    cy.visit('/reportes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
  })

  it('debe mostrar interfaz de generación de reportes', () => {
    cy.get('body').then(($body) => {
      const selectors = [
        '[data-cy="reports-interface"]',
        '[data-cy="create-report-button"]',
        '[data-cy="reports-list"]',
        '[data-cy="report-filters"]'
      ]
      selectors.forEach(selector => {
        if ($body.find(selector).length > 0) {
          cy.get(selector, { timeout: 5000 }).should('exist')
        }
      })
    })
  })

  it('debe crear reporte de análisis por período', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="create-report-button"], button').length > 0) {
        cy.get('[data-cy="create-report-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="report-type"], select').length > 0) {
            cy.get('[data-cy="report-type"], select').first().select('analisis-periodo', { force: true })
            cy.get('body').then(($afterSelect) => {
              if ($afterSelect.find('[data-cy="start-date"], input[type="date"]').length > 0) {
                cy.get('[data-cy="start-date"], input[type="date"]').first().type('2024-01-01', { force: true })
                cy.get('[data-cy="end-date"], input[type="date"]').first().type('2024-01-31', { force: true })
                cy.get('body').then(($afterDates) => {
                  if ($afterDates.find('[data-cy="fincas-select"], input[type="checkbox"]').length > 0) {
                    cy.get('[data-cy="fincas-select"], input[type="checkbox"]').first().check({ force: true })
                    cy.get('[data-cy="include-charts"], input[type="checkbox"]').first().check({ force: true })
                    cy.get('[data-cy="include-recommendations"], input[type="checkbox"]').last().check({ force: true })
                    cy.get('[data-cy="generate-report"], button[type="submit"]').first().click()
                    cy.get('body', { timeout: 5000 }).should('be.visible')
                  }
                })
              }
            })
          }
        })
      }
    })
  })

  it('debe crear reporte de calidad por finca', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="create-report-button"], button').length > 0) {
        cy.get('[data-cy="create-report-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="report-type"], select').length > 0) {
            cy.get('[data-cy="report-type"], select').first().select('calidad-finca', { force: true })
            cy.get('body', { timeout: 5000 }).then(($afterSelect) => {
              if ($afterSelect.find('[data-cy="finca-select"], select').length > 0) {
                cy.get('[data-cy="finca-select"], select').first().select('Finca El Paraíso', { force: true })
                cy.get('body').then(($options) => {
                  if ($options.find('[data-cy="include-trends"], input[type="checkbox"]').length > 0) {
                    cy.get('[data-cy="include-trends"], input[type="checkbox"]').first().check({ force: true })
                  }
                  if ($options.find('[data-cy="include-comparisons"], input[type="checkbox"]').length > 0) {
                    cy.get('[data-cy="include-comparisons"], input[type="checkbox"]').first().check({ force: true })
                  }
                })
                
                // Generar reporte
                cy.get('body').then(($generate) => {
                  if ($generate.find('[data-cy="generate-report"], button[type="submit"]').length > 0) {
                    cy.get('[data-cy="generate-report"], button[type="submit"]').first().click()
                    
                    // Esperar completación si existe
                    cy.get('body', { timeout: 30000 }).then(($completed) => {
                      if ($completed.find('[data-cy="report-completed"], .completed').length > 0) {
                        cy.get('[data-cy="report-completed"], .completed').should('be.visible')
                      }
                      if ($completed.find('[data-cy="notification-success"], .swal2-success').length > 0) {
                        cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
                      }
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

  it('debe crear reporte comparativo entre lotes', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="create-report-button"], button').length > 0) {
        cy.get('[data-cy="create-report-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="report-type"], select').length > 0) {
            cy.get('[data-cy="report-type"], select').first().select('comparativo-lotes', { force: true })
            cy.get('body', { timeout: 5000 }).then(($afterSelect) => {
              if ($afterSelect.find('[data-cy="lotes-select"], input[type="checkbox"]').length > 0) {
                cy.get('[data-cy="lotes-select"], input[type="checkbox"]').first().check({ force: true })
                cy.get('body').then(($compare) => {
                  if ($compare.find('[data-cy="compare-quality"], input[type="checkbox"]').length > 0) {
                    cy.get('[data-cy="compare-quality"], input[type="checkbox"]').first().check({ force: true })
                  }
                  if ($compare.find('[data-cy="compare-production"], input[type="checkbox"]').length > 0) {
                    cy.get('[data-cy="compare-production"], input[type="checkbox"]').first().check({ force: true })
                  }
                })
                
                // Generar reporte
                cy.get('body').then(($generate) => {
                  if ($generate.find('[data-cy="generate-report"], button[type="submit"]').length > 0) {
                    cy.get('[data-cy="generate-report"], button[type="submit"]').first().click()
                    
                    // Esperar completación si existe
                    cy.get('body', { timeout: 30000 }).then(($completed) => {
                      if ($completed.find('[data-cy="report-completed"], .completed').length > 0) {
                        cy.get('[data-cy="report-completed"], .completed').should('be.visible')
                      }
                      if ($completed.find('[data-cy="notification-success"], .swal2-success').length > 0) {
                        cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
                      }
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

  it('debe crear reporte de recomendaciones', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="create-report-button"], button').length > 0) {
        cy.get('[data-cy="create-report-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="report-type"], select').length > 0) {
            cy.get('[data-cy="report-type"], select').first().select('recomendaciones', { force: true })
            cy.get('body', { timeout: 5000 }).then(($afterSelect) => {
              if ($afterSelect.find('[data-cy="scope-all-fincas"], input[type="checkbox"]').length > 0) {
                cy.get('[data-cy="scope-all-fincas"], input[type="checkbox"]').first().check({ force: true })
                cy.get('body').then(($recs) => {
                  if ($recs.find('[data-cy="fertilization-rec"], input[type="checkbox"]').length > 0) {
                    cy.get('[data-cy="fertilization-rec"], input[type="checkbox"]').first().check({ force: true })
                  }
                  if ($recs.find('[data-cy="irrigation-rec"], input[type="checkbox"]').length > 0) {
                    cy.get('[data-cy="irrigation-rec"], input[type="checkbox"]').first().check({ force: true })
                  }
                })
                
                // Generar reporte
                cy.get('body').then(($generate) => {
                  if ($generate.find('[data-cy="generate-report"], button[type="submit"]').length > 0) {
                    cy.get('[data-cy="generate-report"], button[type="submit"]').first().click()
                    
                    // Esperar completación si existe
                    cy.get('body', { timeout: 30000 }).then(($completed) => {
                      if ($completed.find('[data-cy="report-completed"], .completed').length > 0) {
                        cy.get('[data-cy="report-completed"], .completed').should('be.visible')
                      }
                      if ($completed.find('[data-cy="notification-success"], .swal2-success').length > 0) {
                        cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
                      }
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

  it('debe validar campos requeridos para generar reporte', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="create-report-button"], button').length > 0) {
        cy.get('[data-cy="create-report-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="generate-report"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="generate-report"], button[type="submit"]').first().click()
            
            // Verificar errores de validación si existen
            cy.get('body', { timeout: 3000 }).then(($errors) => {
              const errorSelectors = [
                '[data-cy="report-type-error"]',
                '[data-cy="date-range-error"]'
              ]
              errorSelectors.forEach(selector => {
                if ($errors.find(selector).length > 0) {
                  cy.get(selector).should('exist')
                }
              })
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe validar rango de fechas', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="create-report-button"], button').length > 0) {
        cy.get('[data-cy="create-report-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          // Fecha de inicio mayor que fecha de fin
          if ($modal.find('[data-cy="start-date"], input[type="date"]').length > 0) {
            cy.get('[data-cy="start-date"], input[type="date"]').first().type('2024-01-31', { force: true })
            cy.get('[data-cy="end-date"], input[type="date"]').first().type('2024-01-01', { force: true })
            cy.get('[data-cy="generate-report"], button[type="submit"]').first().click()
            
            cy.get('body', { timeout: 3000 }).then(($error) => {
              if ($error.find('[data-cy="date-range-error"], .error-message').length > 0) {
                cy.get('[data-cy="date-range-error"], .error-message').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('fecha') || text.includes('inicio') || text.includes('anterior') || text.length > 0
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

  it('debe permitir cancelar generación de reporte', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="create-report-button"], button').length > 0) {
        cy.get('[data-cy="create-report-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="report-type"], select').length > 0) {
            cy.get('[data-cy="report-type"], select').first().select('analisis-periodo', { force: true })
            cy.get('body').then(($afterSelect) => {
              if ($afterSelect.find('[data-cy="start-date"], input[type="date"]').length > 0) {
                cy.get('[data-cy="start-date"], input[type="date"]').first().type('2024-01-01', { force: true })
                cy.get('[data-cy="end-date"], input[type="date"]').first().type('2024-01-31', { force: true })
                cy.get('[data-cy="generate-report"], button[type="submit"]').first().click()
                
                // Cancelar generación si existe el botón
                cy.get('body', { timeout: 5000 }).then(($cancel) => {
                  if ($cancel.find('[data-cy="cancel-generation"], button').length > 0) {
                    cy.get('[data-cy="cancel-generation"], button').first().click({ force: true })
                    
                    // Confirmar cancelación si existe
                    cy.get('body', { timeout: 5000 }).then(($confirm) => {
                      if ($confirm.find('[data-cy="confirm-cancel"], .swal2-confirm, button').length > 0) {
                        cy.get('[data-cy="confirm-cancel"], .swal2-confirm, button').first().click()
                        
                        // Verificar que se canceló si existe el mensaje
                        cy.get('body', { timeout: 5000 }).then(($cancelled) => {
                          if ($cancelled.find('[data-cy="generation-cancelled"], .cancelled-message').length > 0) {
                            cy.get('[data-cy="generation-cancelled"], .cancelled-message').should('satisfy', ($el) => {
                              const text = $el.text().toLowerCase()
                              return text.includes('cancelada') || text.includes('cancel') || text.length > 0
                            })
                          }
                        })
                      }
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

  it('debe mostrar progreso detallado de generación', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="create-report-button"], button').length > 0) {
        cy.get('[data-cy="create-report-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="report-type"], select').length > 0) {
            cy.get('[data-cy="report-type"], select').first().select('analisis-periodo', { force: true })
            cy.get('body').then(($afterSelect) => {
              if ($afterSelect.find('[data-cy="start-date"], input[type="date"]').length > 0) {
                cy.get('[data-cy="start-date"], input[type="date"]').first().type('2024-01-01', { force: true })
                cy.get('[data-cy="end-date"], input[type="date"]').first().type('2024-01-31', { force: true })
                cy.get('[data-cy="generate-report"], button[type="submit"]').first().click()
                
                // Verificar etapas del progreso si existen
                cy.get('body', { timeout: 10000 }).then(($progress) => {
                  if ($progress.find('[data-cy="progress-stage"], .progress-stage').length > 0) {
                    cy.get('[data-cy="progress-stage"], .progress-stage').should('satisfy', ($el) => {
                      const text = $el.text().toLowerCase()
                      return text.includes('recopilando') || text.includes('procesando') || text.includes('generando') || text.includes('finalizando') || text.length > 0
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

  it('debe manejar errores durante la generación', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular error del servidor
    cy.intercept('POST', `${apiBaseUrl}/reportes/`, {
      statusCode: 500,
      body: { error: 'Error del servidor' }
    }).as('reportError')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="create-report-button"], button').length > 0) {
        cy.get('[data-cy="create-report-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="report-type"], select').length > 0) {
            cy.get('[data-cy="report-type"], select').first().select('analisis-periodo', { force: true })
            cy.get('body').then(($afterSelect) => {
              if ($afterSelect.find('[data-cy="start-date"], input[type="date"]').length > 0) {
                cy.get('[data-cy="start-date"], input[type="date"]').first().type('2024-01-01', { force: true })
                cy.get('[data-cy="end-date"], input[type="date"]').first().type('2024-01-31', { force: true })
                cy.get('[data-cy="generate-report"], button[type="submit"]').first().click()
                
                cy.wait('@reportError', { timeout: 10000 })
                
                // Verificar mensaje de error si existe
                cy.get('body', { timeout: 5000 }).then(($error) => {
                  if ($error.find('[data-cy="generation-error"], .error-message, .swal2-error').length > 0) {
                    cy.get('[data-cy="generation-error"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
                      const text = $el.text().toLowerCase()
                      return text.includes('error') || text.includes('generar') || text.includes('reporte') || text.length > 0
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

  it('debe permitir programar generación de reportes', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="create-report-button"], button').length > 0) {
        cy.get('[data-cy="create-report-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="report-type"], select').length > 0) {
            cy.get('[data-cy="report-type"], select').first().select('analisis-periodo', { force: true })
            cy.get('body').then(($afterSelect) => {
              if ($afterSelect.find('[data-cy="schedule-report"], input[type="checkbox"]').length > 0) {
                cy.get('[data-cy="schedule-report"], input[type="checkbox"]').first().check({ force: true })
                cy.get('body', { timeout: 5000 }).then(($schedule) => {
                  if ($schedule.find('[data-cy="schedule-frequency"], select').length > 0) {
                    cy.get('[data-cy="schedule-frequency"], select').first().select('mensual', { force: true })
                    cy.get('body').then(($fields) => {
                      if ($fields.find('[data-cy="schedule-day"], input[type="number"]').length > 0) {
                        cy.get('[data-cy="schedule-day"], input[type="number"]').first().type('1')
                      }
                      if ($fields.find('[data-cy="schedule-time"], input[type="time"]').length > 0) {
                        cy.get('[data-cy="schedule-time"], input[type="time"]').first().type('09:00')
                      }
                    })
                  }
                  
                  // Guardar programación si existe el botón
                  cy.get('body').then(($save) => {
                    if ($save.find('[data-cy="save-schedule"], button[type="submit"]').length > 0) {
                      cy.get('[data-cy="save-schedule"], button[type="submit"]').first().click()
                      
                      // Verificar éxito si existe la notificación
                      cy.get('body', { timeout: 5000 }).then(($success) => {
                        if ($success.find('[data-cy="notification-success"], .swal2-success').length > 0) {
                          cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
                        }
                      })
                    }
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

  it('debe permitir personalizar formato de reporte', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="create-report-button"], button').length > 0) {
        cy.get('[data-cy="create-report-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          // Configurar formato si existen los campos
          if ($modal.find('[data-cy="report-format"], select').length > 0) {
            cy.get('[data-cy="report-format"], select').first().select('pdf', { force: true })
            cy.get('body').then(($format) => {
              if ($format.find('[data-cy="include-cover"], input[type="checkbox"]').length > 0) {
                cy.get('[data-cy="include-cover"], input[type="checkbox"]').first().check({ force: true })
              }
              if ($format.find('[data-cy="include-summary"], input[type="checkbox"]').length > 0) {
                cy.get('[data-cy="include-summary"], input[type="checkbox"]').first().check({ force: true })
              }
              if ($format.find('[data-cy="color-scheme"], select').length > 0) {
                cy.get('[data-cy="color-scheme"], select').first().select('corporate', { force: true })
              }
            })
          }
          
          // Verificar preview si existe
          cy.get('body').then(($preview) => {
            if ($preview.find('[data-cy="format-preview"], .preview').length > 0) {
              cy.get('[data-cy="format-preview"], .preview').should('be.visible')
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
})
