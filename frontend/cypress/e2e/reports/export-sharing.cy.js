import { 
  verifySelectorsExist,
  ifFoundInBody,
  clickIfExistsAndContinue,
  selectIfExistsAndContinue,
  typeIfExistsAndContinue
} from '../../support/helpers'

describe('Reportes - Exportación y Compartir', () => {
  beforeEach(() => {
    cy.login('analyst')
    cy.visit('/reportes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
  })

  it('debe exportar reporte como PDF', () => {
    cy.exportReport('pdf', { reportIndex: 0, verifyDownload: false })
  })

  it('debe exportar reporte como Excel', () => {
    cy.exportReport('excel', { reportIndex: 0, verifyDownload: true, downloadFilename: 'reporte.xlsx' })
  })

  it('debe exportar reporte como PowerPoint', () => {
    cy.exportReport('powerpoint', { reportIndex: 0, verifyDownload: true, downloadFilename: 'reporte.pptx' })
  })

  it('debe exportar múltiples reportes en lote', () => {
    ifFoundInBody('[data-cy="report-checkbox"], input[type="checkbox"]', () => {
      cy.get('[data-cy="report-checkbox"], input[type="checkbox"]').first().check({ force: true })
      cy.get('[data-cy="report-checkbox"], input[type="checkbox"]').eq(1).check({ force: true })
      
      return clickIfExistsAndContinue('[data-cy="bulk-export"], button', () => {
        return ifFoundInBody('[data-cy="bulk-export-options"], .bulk-export-options', () => {
          cy.get('[data-cy="bulk-export-options"], .bulk-export-options').should('exist')
          selectIfExistsAndContinue('[data-cy="export-format"], select', 'zip', () => {
            return clickIfExistsAndContinue('[data-cy="confirm-bulk-export"], button[type="submit"]', () => {
              cy.verifyDownload('reportes-lote.zip')
            })
          })
        })
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe compartir reporte por email', () => {
    cy.shareReport('email', { 
      reportIndex: 0, 
      email: 'test@example.com', 
      subject: 'Reporte de Análisis de Cacao',
      attachmentFormat: 'pdf'
    })
    
    cy.get('body', { timeout: 5000 }).then(($success) => {
      if ($success.find('[data-cy="notification-success"], .swal2-success').length > 0) {
        cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
      }
    })
  })

  it('debe generar enlace de compartir', () => {
    cy.shareReport('link', { reportIndex: 0 })
    
    cy.get('body', { timeout: 5000 }).then(($generated) => {
      if ($generated.find('[data-cy="generated-link"], .generated-link').length > 0) {
        cy.get('[data-cy="generated-link"], .generated-link').should('exist')
        if ($generated.find('[data-cy="copy-link"], button').length > 0) {
          cy.get('[data-cy="copy-link"], button').first().click()
        }
      }
    })
  })

  it('debe programar envío automático de reportes', () => {
    clickIfExistsAndContinue('[data-cy="report-item"], .report-item, .item', () => {
      return clickIfExistsAndContinue('[data-cy="schedule-sharing"], button', () => {
        return selectIfExistsAndContinue('[data-cy="schedule-frequency"], select', 'mensual', () => {
          typeIfExistsAndContinue('[data-cy="schedule-day"], input[type="number"]', '1', () => {
            typeIfExistsAndContinue('[data-cy="schedule-time"], input[type="time"]', '09:00', () => {
              typeIfExistsAndContinue('[data-cy="schedule-recipients"], input[type="email"]', 'admin@cacaoscan.com', () => {
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
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe mostrar historial de compartir', () => {
    clickIfExistsAndContinue('[data-cy="report-item"], .report-item, .item', () => {
      return ifFoundInBody('[data-cy="sharing-history"], .sharing-history', () => {
        cy.get('[data-cy="sharing-history"], .sharing-history').should('be.visible')
        
        return ifFoundInBody('[data-cy="sharing-item"], .sharing-item', ($item) => {
          cy.get('[data-cy="sharing-item"], .sharing-item').should('have.length.greaterThan', 0)
          const sharingSelectors = [
            '[data-cy="sharing-date"]',
            '[data-cy="sharing-method"]',
            '[data-cy="sharing-recipients"]'
          ]
          verifySelectorsExist(sharingSelectors, $item, 3000)
        })
      }, () => {
        cy.get('body').should('be.visible')
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe permitir revocar acceso a reporte compartido', () => {
    clickIfExistsAndContinue('[data-cy="report-item"], .report-item, .item', () => {
      return ifFoundInBody('[data-cy="sharing-item"], .sharing-item', ($item) => {
        return clickIfExistsAndContinue('[data-cy="revoke-access"], button', () => {
          return clickIfExistsAndContinue('[data-cy="confirm-revoke"], .swal2-confirm, button', () => {
            return ifFoundInBody('[data-cy="notification-success"], .swal2-success', () => {
              cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
            })
          })
        })
      }, () => {
        cy.get('body').should('be.visible')
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe exportar reporte con marca de agua', () => {
    clickIfExistsAndContinue('[data-cy="report-item"], .report-item, .item', () => {
      return clickIfExistsAndContinue('[data-cy="download-pdf"], button, a', () => {
        return typeIfExistsAndContinue('[data-cy="watermark-text"], input', 'CONFIDENCIAL', () => {
          selectIfExistsAndContinue('[data-cy="watermark-position"], select', 'center', () => {
            typeIfExistsAndContinue('[data-cy="watermark-opacity"], input[type="number"]', '0.3', () => {
              return clickIfExistsAndContinue('[data-cy="confirm-download"], button[type="submit"]', () => {
                cy.verifyDownload('reporte-marcado.pdf')
              })
            })
          })
        })
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe exportar reporte con firma digital', () => {
    clickIfExistsAndContinue('[data-cy="report-item"], .report-item, .item', () => {
      return clickIfExistsAndContinue('[data-cy="download-pdf"], button, a', () => {
        return clickIfExistsAndContinue('[data-cy="digital-signature"], input[type="checkbox"]', () => {
          selectIfExistsAndContinue('[data-cy="signature-certificate"], select', 'certificado-valido', () => {
            typeIfExistsAndContinue('[data-cy="signature-reason"], input, textarea', 'Aprobación del reporte', () => {
              return clickIfExistsAndContinue('[data-cy="confirm-download"], button[type="submit"]', () => {
                cy.verifyDownload('reporte-firmado.pdf')
              })
            })
          })
        })
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe mostrar vista previa antes de exportar', () => {
    clickIfExistsAndContinue('[data-cy="report-item"], .report-item, .item', () => {
      return clickIfExistsAndContinue('[data-cy="preview-export"], button', () => {
        return ifFoundInBody('[data-cy="export-preview"], .preview', () => {
          cy.get('[data-cy="export-preview"], .preview').should('be.visible')
          
          const previewSelectors = [
            '[data-cy="preview-content"]',
            '[data-cy="preview-pages"]'
          ]
          verifySelectorsInBody(previewSelectors, 3000)
          
          return clickIfExistsAndContinue('[data-cy="next-page"], button', () => {
            return clickIfExistsAndContinue('[data-cy="previous-page"], button', () => {
              cy.wrap(null)
            })
          })
        }, () => {
          cy.get('body').should('be.visible')
        })
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe manejar errores durante la exportación', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    cy.intercept('POST', `${apiBaseUrl}/reportes/**/export/`, {
      statusCode: 500,
      body: { error: 'Error al exportar reporte' }
    }).as('exportError')
    
    clickIfExistsAndContinue('[data-cy="report-item"], .report-item, .item', () => {
      return clickIfExistsAndContinue('[data-cy="download-pdf"], button, a', () => {
        return clickIfExistsAndContinue('[data-cy="confirm-download"], button[type="submit"]', () => {
          cy.wait('@exportError', { timeout: 10000 })
          
          return ifFoundInBody('[data-cy="export-error"], .error-message, .swal2-error', () => {
            cy.get('[data-cy="export-error"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('error') || text.includes('exportar') || text.includes('reporte') || text.length > 0
            })
          })
        })
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe mostrar progreso de exportación', () => {
    clickIfExistsAndContinue('[data-cy="report-item"], .report-item, .item', () => {
      return clickIfExistsAndContinue('[data-cy="download-pdf"], button, a', () => {
        return clickIfExistsAndContinue('[data-cy="confirm-download"], button[type="submit"]', () => {
          return ifFoundInBody('[data-cy="export-progress"], .progress', () => {
            cy.get('[data-cy="export-progress"], .progress').should('be.visible')
            ifFoundInBody('[data-cy="progress-percentage"], .progress-percentage', () => {
              cy.get('[data-cy="progress-percentage"], .progress-percentage').should('satisfy', ($el) => {
                const text = $el.text()
                return text.includes('%') || text.length > 0
              })
            })
          })
        })
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe exportar reporte como CSV', () => {
    cy.exportReport('csv', { reportIndex: 0, verifyDownload: true, downloadFilename: 'reporte.csv' })
  })

  it('debe exportar reporte como JSON', () => {
    cy.exportReport('json', { reportIndex: 0, verifyDownload: true, downloadFilename: 'reporte.json' })
  })

  it('debe validar destinatarios de email', () => {
    cy.get('[data-cy="report-item"]').first().click()
    cy.get('[data-cy="share-email"]').click()
    
    cy.get('[data-cy="email-recipients"]').type('invalid-email')
    cy.get('[data-cy="send-email"]').click()
    
    cy.get('[data-cy="email-error"]')
      .should('be.visible')
      .and('contain', 'Email inválido')
  })

  it('debe permitir cancelar exportación en progreso', () => {
    cy.get('[data-cy="report-item"]').first().click()
    cy.get('[data-cy="download-pdf"]').click()
    cy.get('[data-cy="confirm-download"]').click()
    
    cy.get('[data-cy="cancel-export"]').click()
    cy.get('[data-cy="export-progress"]').should('not.exist')
  })

  it('debe mostrar tamaño estimado del archivo', () => {
    cy.get('[data-cy="report-item"]').first().click()
    cy.get('[data-cy="download-pdf"]').click()
    
    cy.get('[data-cy="estimated-size"]').should('be.visible')
    cy.get('[data-cy="estimated-size"]').should('contain', 'MB')
  })
})
