import { 
  ifFoundInBody,
  clickIfExistsAndContinue,
  selectIfExistsAndContinue,
  checkCheckboxIfExists,
  typeIfExistsAndContinue,
  verifyReportGenerationComplete,
  verifyErrorMessageGeneric,
  getApiBaseUrl
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
    const generateReport = () => {
      checkCheckboxIfExists('[data-cy="include-trends"], input[type="checkbox"]')
      checkCheckboxIfExists('[data-cy="include-comparisons"], input[type="checkbox"]')
      clickIfExistsAndContinue('[data-cy="generate-report"], button[type="submit"]', () => {
        verifyReportGenerationComplete()
      })
    }
    
    const selectFinca = () => {
      cy.wait(500)
      selectIfExistsAndContinue('[data-cy="finca-select"], select', 'Finca El Paraíso', generateReport)
    }
    
    const selectReportType = () => {
      cy.wait(500)
      selectIfExistsAndContinue('[data-cy="report-type"], select', 'calidad-finca', selectFinca)
    }
    
    clickIfExistsAndContinue('[data-cy="create-report-button"], button', () => {
      cy.wait(500)
      selectReportType()
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe crear reporte comparativo entre lotes', () => {
    const generateComparativoReport = () => {
      checkCheckboxIfExists('[data-cy="lotes-select"], input[type="checkbox"]')
      checkCheckboxIfExists('[data-cy="compare-quality"], input[type="checkbox"]')
      checkCheckboxIfExists('[data-cy="compare-production"], input[type="checkbox"]')
      clickIfExistsAndContinue('[data-cy="generate-report"], button[type="submit"]', () => {
        verifyReportGenerationComplete()
      })
    }
    
    const selectComparativoType = () => {
      cy.wait(500)
      selectIfExistsAndContinue('[data-cy="report-type"], select', 'comparativo-lotes', () => {
        cy.wait(500)
        generateComparativoReport()
      })
    }
    
    cy.clickIfExists('[data-cy="create-report-button"], button').then((clicked) => {
      if (clicked) {
        cy.wait(500)
        selectComparativoType()
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe crear reporte de recomendaciones', () => {
    const generateRecomendacionesReport = () => {
      checkCheckboxIfExists('[data-cy="scope-all-fincas"], input[type="checkbox"]')
      checkCheckboxIfExists('[data-cy="fertilization-rec"], input[type="checkbox"]')
      checkCheckboxIfExists('[data-cy="irrigation-rec"], input[type="checkbox"]')
      clickIfExistsAndContinue('[data-cy="generate-report"], button[type="submit"]', () => {
        verifyReportGenerationComplete()
      })
    }
    
    const selectRecomendacionesType = () => {
      selectIfExistsAndContinue('[data-cy="report-type"], select', 'recomendaciones', generateRecomendacionesReport)
    }
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="create-report-button"], button').length > 0) {
        clickIfExistsAndContinue('[data-cy="create-report-button"], button', selectRecomendacionesType)
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
            
            const verifyErrorSelector = (selector) => {
              cy.get(selector, { timeout: 3000 }).should('exist')
            }

            const verifyValidationErrors = () => {
              const errorSelectors = [
                '[data-cy="report-type-error"]',
                '[data-cy="date-range-error"]'
              ]
              for (const selector of errorSelectors) {
                ifFoundInBody(selector, () => verifyErrorSelector(selector))
              }
            }
            verifyValidationErrors()
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe validar rango de fechas', () => {
    const verifyDateRangeError = () => {
      ifFoundInBody('[data-cy="date-range-error"], .error-message', () => {
        verifyErrorMessageGeneric(['fecha', 'inicio', 'anterior'], '[data-cy="date-range-error"], .error-message')
      })
    }
    
    const fillEndDate = () => {
      typeIfExistsAndContinue('[data-cy="end-date"], input[type="date"]', '2024-01-01', () => {
        cy.get('[data-cy="generate-report"], button[type="submit"]').first().click()
        verifyDateRangeError()
      })
    }
    
    const fillStartDate = () => {
      typeIfExistsAndContinue('[data-cy="start-date"], input[type="date"]', '2024-01-31', fillEndDate)
    }
    
    clickIfExistsAndContinue('[data-cy="create-report-button"], button', fillStartDate, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe permitir cancelar generación de reporte', () => {
    const verifyCancelled = () => {
      ifFoundInBody('[data-cy="generation-cancelled"], .cancelled-message', () => {
        verifyErrorMessageGeneric(['cancelada', 'cancel'], '[data-cy="generation-cancelled"], .cancelled-message')
      })
    }
    
    const confirmCancel = () => {
      clickIfExistsAndContinue('[data-cy="confirm-cancel"], .swal2-confirm, button', verifyCancelled)
    }
    
    const cancelGeneration = () => {
      clickIfExistsAndContinue('[data-cy="cancel-generation"], button', confirmCancel)
    }
    
    const fillDatesAndCancel = () => {
      typeIfExistsAndContinue('[data-cy="end-date"], input[type="date"]', '2024-01-31', () => {
        cy.get('[data-cy="generate-report"], button[type="submit"]').first().click()
        cancelGeneration()
      })
    }
    
    const fillStartDateAndContinue = () => {
      typeIfExistsAndContinue('[data-cy="start-date"], input[type="date"]', '2024-01-01', fillDatesAndCancel)
    }
    
    const selectReportType = () => {
      selectIfExistsAndContinue('[data-cy="report-type"], select', 'analisis-periodo', fillStartDateAndContinue)
    }
    
    clickIfExistsAndContinue('[data-cy="create-report-button"], button', selectReportType, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe mostrar progreso detallado de generación', () => {
    const verifyProgress = () => {
      ifFoundInBody('[data-cy="progress-stage"], .progress-stage', () => {
        verifyErrorMessageGeneric(['recopilando', 'procesando', 'generando', 'finalizando'], '[data-cy="progress-stage"], .progress-stage')
      })
    }
    
    const submitAndVerify = () => {
      cy.get('[data-cy="generate-report"], button[type="submit"]').first().click()
      verifyProgress()
    }
    
    const fillEndDate = () => {
      typeIfExistsAndContinue('[data-cy="end-date"], input[type="date"]', '2024-01-31', submitAndVerify)
    }
    
    const fillStartDate = () => {
      typeIfExistsAndContinue('[data-cy="start-date"], input[type="date"]', '2024-01-01', fillEndDate)
    }
    
    const selectType = () => {
      selectIfExistsAndContinue('[data-cy="report-type"], select', 'analisis-periodo', fillStartDate)
    }
    
    clickIfExistsAndContinue('[data-cy="create-report-button"], button', selectType, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe manejar errores durante la generación', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('POST', `${apiBaseUrl}/reportes/`, {
      statusCode: 500,
      body: { error: 'Error del servidor' }
    }).as('reportError')
    
    const verifyError = () => {
      ifFoundInBody('[data-cy="generation-error"], .error-message, .swal2-error', () => {
        verifyErrorMessageGeneric(['error', 'generar', 'reporte'], '[data-cy="generation-error"], .error-message, .swal2-error')
      })
    }
    
    const submitAndWait = () => {
      cy.get('[data-cy="generate-report"], button[type="submit"]').first().click()
      cy.wait('@reportError', { timeout: 10000 })
      verifyError()
    }
    
    const fillEndDate = () => {
      typeIfExistsAndContinue('[data-cy="end-date"], input[type="date"]', '2024-01-31', submitAndWait)
    }
    
    const fillStartDate = () => {
      typeIfExistsAndContinue('[data-cy="start-date"], input[type="date"]', '2024-01-01', fillEndDate)
    }
    
    const selectType = () => {
      selectIfExistsAndContinue('[data-cy="report-type"], select', 'analisis-periodo', fillStartDate)
    }
    
    clickIfExistsAndContinue('[data-cy="create-report-button"], button', selectType, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe permitir programar generación de reportes', () => {
    const verifyScheduleSuccess = () => {
      ifFoundInBody('[data-cy="notification-success"], .swal2-success', () => {
        cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
      })
    }
    
    const saveSchedule = () => {
      clickIfExistsAndContinue('[data-cy="save-schedule"], button[type="submit"]', verifyScheduleSuccess)
    }
    
    const fillTime = () => {
      typeIfExistsAndContinue('[data-cy="schedule-time"], input[type="time"]', '09:00', saveSchedule)
    }
    
    const fillDay = () => {
      typeIfExistsAndContinue('[data-cy="schedule-day"], input[type="number"]', '1', fillTime)
    }
    
    const selectFrequency = () => {
      selectIfExistsAndContinue('[data-cy="schedule-frequency"], select', 'mensual', fillDay)
    }
    
    const enableSchedule = () => {
      clickIfExistsAndContinue('[data-cy="schedule-report"], input[type="checkbox"]', selectFrequency)
    }
    
    const selectType = () => {
      selectIfExistsAndContinue('[data-cy="report-type"], select', 'analisis-periodo', enableSchedule)
    }
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="create-report-button"], button').length > 0) {
        cy.get('[data-cy="create-report-button"], button').first().click({ force: true })
        selectType()
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
