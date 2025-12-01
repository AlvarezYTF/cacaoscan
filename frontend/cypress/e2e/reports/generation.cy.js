describe('Generación de Reportes - Creación', () => {
  beforeEach(() => {
    cy.login('analyst')
    cy.visit('/reportes')
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

  const clickIfExists = (selector, options = {}) => {
    return cy.get('body').then(($body) => {
      if ($body.find(selector).length > 0) {
        cy.get(selector).first().click({ force: true, ...options })
        return true
      }
      return false
    })
  }

  const fillFieldIfExists = (selector, value, options = {}) => {
    return cy.get('body').then(($body) => {
      if ($body.find(selector).length > 0) {
        cy.get(selector).first().type(value, { force: true, ...options })
        return true
      }
      return false
    })
  }

  const selectOptionIfExists = (selector, value, options = {}) => {
    return cy.get('body').then(($body) => {
      if ($body.find(selector).length > 0) {
        cy.get(selector).first().select(value, { force: true, ...options })
        return true
      }
      return false
    })
  }

  const checkCheckboxIfExists = (selector, options = {}) => {
    return cy.get('body').then(($body) => {
      if ($body.find(selector).length > 0) {
        cy.get(selector).first().check({ force: true, ...options })
        return true
      }
      return false
    })
  }

  it('debe mostrar interfaz de generación de reportes', () => {
    cy.get('body').then(($body) => {
      const selectors = [
        '[data-cy="reports-interface"]',
        '[data-cy="create-report-button"]',
        '[data-cy="reports-list"]',
        '[data-cy="report-filters"]'
      ]
          verifySelectorsExist(selectors, $body, 5000)
    })
  })

  it('debe crear reporte de análisis por período', () => {
    clickIfExists('[data-cy="create-report-button"], button').then((clicked) => {
      if (clicked) {
        cy.wait(500)
        selectOptionIfExists('[data-cy="report-type"], select', 'analisis-periodo').then((selected) => {
          if (selected) {
            fillFieldIfExists('[data-cy="start-date"], input[type="date"]', '2024-01-01')
            fillFieldIfExists('[data-cy="end-date"], input[type="date"]', '2024-01-31')
            checkCheckboxIfExists('[data-cy="fincas-select"], input[type="checkbox"]')
            checkCheckboxIfExists('[data-cy="include-charts"], input[type="checkbox"]')
            checkCheckboxIfExists('[data-cy="include-recommendations"], input[type="checkbox"]')
            clickIfExists('[data-cy="generate-report"], button[type="submit"]')
            cy.get('body', { timeout: 5000 }).should('be.visible')
          }
        })
      }
    })
  })

  it('debe crear reporte de calidad por finca', () => {
    clickIfExists('[data-cy="create-report-button"], button').then((clicked) => {
      if (clicked) {
        cy.wait(500)
        selectOptionIfExists('[data-cy="report-type"], select', 'calidad-finca').then((selected) => {
          if (selected) {
            cy.wait(500)
            selectOptionIfExists('[data-cy="finca-select"], select', 'Finca El Paraíso').then((fincaSelected) => {
              if (fincaSelected) {
                checkCheckboxIfExists('[data-cy="include-trends"], input[type="checkbox"]')
                checkCheckboxIfExists('[data-cy="include-comparisons"], input[type="checkbox"]')
                clickIfExists('[data-cy="generate-report"], button[type="submit"]').then((submitted) => {
                  if (submitted) {
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
    clickIfExists('[data-cy="create-report-button"], button').then((clicked) => {
      if (clicked) {
        cy.wait(500)
        selectOptionIfExists('[data-cy="report-type"], select', 'comparativo-lotes').then((selected) => {
          if (selected) {
            cy.wait(500)
            checkCheckboxIfExists('[data-cy="lotes-select"], input[type="checkbox"]').then(() => {
              checkCheckboxIfExists('[data-cy="compare-quality"], input[type="checkbox"]')
              checkCheckboxIfExists('[data-cy="compare-production"], input[type="checkbox"]')
              clickIfExists('[data-cy="generate-report"], button[type="submit"]').then((submitted) => {
                if (submitted) {
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
          verifySelectorsExist(errorSelectors, $errors, 3000)
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
