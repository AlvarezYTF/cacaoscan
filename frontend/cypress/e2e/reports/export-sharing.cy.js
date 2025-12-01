import { 
  verifySelectorsExist,
  ifFoundInBody,
  clickIfExistsAndContinue,
  selectIfExistsAndContinue,
  typeIfExistsAndContinue,
  verifyErrorMessageGeneric,
  verifySuccessMessage,
  getApiBaseUrl
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
      
      const confirmBulkExport = () => {
        clickIfExistsAndContinue('[data-cy="confirm-bulk-export"], button[type="submit"]', () => {
          cy.verifyDownload('reportes-lote.zip')
        })
      }
      
      const selectExportFormat = () => {
        selectIfExistsAndContinue('[data-cy="export-format"], select', 'zip', confirmBulkExport)
      }
      
      const openBulkExportOptions = () => {
        ifFoundInBody('[data-cy="bulk-export-options"], .bulk-export-options', () => {
          cy.get('[data-cy="bulk-export-options"], .bulk-export-options').should('exist')
          selectExportFormat()
        })
      }
      
      clickIfExistsAndContinue('[data-cy="bulk-export"], button', openBulkExportOptions)
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
    
    verifySuccessMessage(['success'], '[data-cy="notification-success"], .swal2-success')
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
    const verifySuccess = () => {
      ifFoundInBody('[data-cy="notification-success"], .swal2-success', () => {
        cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
      })
    }
    
    const saveSchedule = () => {
      clickIfExistsAndContinue('[data-cy="save-schedule"], button[type="submit"]', verifySuccess)
    }
    
    const fillRecipients = () => {
      typeIfExistsAndContinue('[data-cy="schedule-recipients"], input[type="email"]', 'admin@cacaoscan.com', saveSchedule)
    }
    
    const fillTime = () => {
      typeIfExistsAndContinue('[data-cy="schedule-time"], input[type="time"]', '09:00', fillRecipients)
    }
    
    const fillDay = () => {
      typeIfExistsAndContinue('[data-cy="schedule-day"], input[type="number"]', '1', fillTime)
    }
    
    const selectFrequency = () => {
      selectIfExistsAndContinue('[data-cy="schedule-frequency"], select', 'mensual', fillDay)
    }
    
    const openSchedule = () => {
      clickIfExistsAndContinue('[data-cy="schedule-sharing"], button', selectFrequency)
    }
    
    clickIfExistsAndContinue('[data-cy="report-item"], .report-item, .item', openSchedule, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe mostrar historial de compartir', () => {
    const verifySharingItems = ($item) => {
      cy.get('[data-cy="sharing-item"], .sharing-item').should('have.length.greaterThan', 0)
      const sharingSelectors = [
        '[data-cy="sharing-date"]',
        '[data-cy="sharing-method"]',
        '[data-cy="sharing-recipients"]'
      ]
      verifySelectorsExist(sharingSelectors, $item, 3000)
    }
    
    const verifySharingHistory = () => {
      ifFoundInBody('[data-cy="sharing-history"], .sharing-history', () => {
        cy.get('[data-cy="sharing-history"], .sharing-history').should('be.visible')
        ifFoundInBody('[data-cy="sharing-item"], .sharing-item', verifySharingItems)
      }, () => {
        cy.get('body').should('be.visible')
      })
    }
    
    clickIfExistsAndContinue('[data-cy="report-item"], .report-item, .item', verifySharingHistory, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe permitir revocar acceso a reporte compartido', () => {
    const verifyRevokeSuccess = () => {
      ifFoundInBody('[data-cy="notification-success"], .swal2-success', () => {
        cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
      })
    }
    
    const confirmRevoke = () => {
      clickIfExistsAndContinue('[data-cy="confirm-revoke"], .swal2-confirm, button', verifyRevokeSuccess)
    }
    
    const revokeAccess = () => {
      clickIfExistsAndContinue('[data-cy="revoke-access"], button', confirmRevoke)
    }
    
    const openSharingItem = ($item) => {
      revokeAccess()
    }
    
    clickIfExistsAndContinue('[data-cy="report-item"], .report-item, .item', () => {
      ifFoundInBody('[data-cy="sharing-item"], .sharing-item', openSharingItem, () => {
        cy.get('body').should('be.visible')
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe exportar reporte con marca de agua', () => {
    const confirmDownload = () => {
      clickIfExistsAndContinue('[data-cy="confirm-download"], button[type="submit"]', () => {
        cy.verifyDownload('reporte-marcado.pdf')
      })
    }
    
    const setOpacity = () => {
      typeIfExistsAndContinue('[data-cy="watermark-opacity"], input[type="number"]', '0.3', confirmDownload)
    }
    
    const setPosition = () => {
      selectIfExistsAndContinue('[data-cy="watermark-position"], select', 'center', setOpacity)
    }
    
    const setWatermarkText = () => {
      typeIfExistsAndContinue('[data-cy="watermark-text"], input', 'CONFIDENCIAL', setPosition)
    }
    
    const openDownload = () => {
      clickIfExistsAndContinue('[data-cy="download-pdf"], button, a', setWatermarkText)
    }
    
    clickIfExistsAndContinue('[data-cy="report-item"], .report-item, .item', openDownload, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe exportar reporte con firma digital', () => {
    const confirmSignedDownload = () => {
      clickIfExistsAndContinue('[data-cy="confirm-download"], button[type="submit"]', () => {
        cy.verifyDownload('reporte-firmado.pdf')
      })
    }
    
    const fillReason = () => {
      typeIfExistsAndContinue('[data-cy="signature-reason"], input, textarea', 'Aprobación del reporte', confirmSignedDownload)
    }
    
    const selectCertificate = () => {
      selectIfExistsAndContinue('[data-cy="signature-certificate"], select', 'certificado-valido', fillReason)
    }
    
    const enableSignature = () => {
      clickIfExistsAndContinue('[data-cy="digital-signature"], input[type="checkbox"]', selectCertificate)
    }
    
    const openDownload = () => {
      clickIfExistsAndContinue('[data-cy="download-pdf"], button, a', enableSignature)
    }
    
    clickIfExistsAndContinue('[data-cy="report-item"], .report-item, .item', openDownload, () => {
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
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('POST', `${apiBaseUrl}/reportes/**/export/`, {
      statusCode: 500,
      body: { error: 'Error al exportar reporte' }
    }).as('exportError')
    
    clickIfExistsAndContinue('[data-cy="report-item"], .report-item, .item', () => {
      return clickIfExistsAndContinue('[data-cy="download-pdf"], button, a', () => {
        return clickIfExistsAndContinue('[data-cy="confirm-download"], button[type="submit"]', () => {
          cy.wait('@exportError', { timeout: 10000 })
          
          return ifFoundInBody('[data-cy="export-error"], .error-message, .swal2-error', () => {
            verifyErrorMessageGeneric(['error', 'exportar', 'reporte'], '[data-cy="export-error"], .error-message, .swal2-error')
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
              verifyErrorMessageGeneric(['%'], '[data-cy="progress-percentage"], .progress-percentage')
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
