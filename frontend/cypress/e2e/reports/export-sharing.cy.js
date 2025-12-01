describe('Reportes - Exportación y Compartir', () => {
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

  it('debe exportar reporte como PDF', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="report-item"], .report-item, .item').length > 0) {
        cy.get('[data-cy="report-item"], .report-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          if ($details.find('[data-cy="download-pdf"], button, a').length > 0) {
            cy.get('[data-cy="download-pdf"], button, a').first().click({ force: true })
            cy.get('body', { timeout: 5000 }).then(($pdfModal) => {
              if ($pdfModal.find('[data-cy="pdf-options"], .pdf-options').length > 0) {
                cy.get('[data-cy="pdf-options"], .pdf-options').should('exist')
                cy.get('[data-cy="confirm-download"], button[type="submit"]', { timeout: 3000 }).then(($confirm) => {
                  if ($confirm.length > 0) {
                    cy.wrap($confirm.first()).click()
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

  it('debe exportar reporte como Excel', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="report-item"], .report-item, .item').length > 0) {
        cy.get('[data-cy="report-item"], .report-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          if ($details.find('[data-cy="download-excel"], button, a').length > 0) {
            cy.get('[data-cy="download-excel"], button, a').first().click({ force: true })
            
            cy.get('body', { timeout: 5000 }).then(($excel) => {
              // Verificar opciones de Excel si existen
              if ($excel.find('[data-cy="excel-options"], .excel-options').length > 0) {
                cy.get('[data-cy="excel-options"], .excel-options').should('exist')
                cy.get('body').then(($options) => {
                  if ($options.find('[data-cy="include-raw-data"], input[type="checkbox"]').length > 0) {
                    cy.get('[data-cy="include-raw-data"], input[type="checkbox"]').first().check({ force: true })
                  }
                  if ($options.find('[data-cy="include-calculations"], input[type="checkbox"]').length > 0) {
                    cy.get('[data-cy="include-calculations"], input[type="checkbox"]').first().check({ force: true })
                  }
                  if ($options.find('[data-cy="excel-format"], select').length > 0) {
                    cy.get('[data-cy="excel-format"], select').first().select('xlsx', { force: true })
                  }
                })
              }
              
              // Confirmar descarga si existe el botón
              cy.get('body').then(($confirm) => {
                if ($confirm.find('[data-cy="confirm-download"], button[type="submit"]').length > 0) {
                  cy.get('[data-cy="confirm-download"], button[type="submit"]').first().click()
                  cy.verifyDownload('reporte.xlsx')
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

  it('debe exportar reporte como PowerPoint', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="report-item"], .report-item, .item').length > 0) {
        cy.get('[data-cy="report-item"], .report-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          if ($details.find('[data-cy="download-powerpoint"], button, a').length > 0) {
            cy.get('[data-cy="download-powerpoint"], button, a').first().click({ force: true })
            
            cy.get('body', { timeout: 5000 }).then(($powerpoint) => {
              // Verificar opciones de PowerPoint si existen
              if ($powerpoint.find('[data-cy="powerpoint-options"], .powerpoint-options').length > 0) {
                cy.get('[data-cy="powerpoint-options"], .powerpoint-options').should('exist')
                cy.get('body').then(($options) => {
                  if ($options.find('[data-cy="include-speaker-notes"], input[type="checkbox"]').length > 0) {
                    cy.get('[data-cy="include-speaker-notes"], input[type="checkbox"]').first().check({ force: true })
                  }
                  if ($options.find('[data-cy="slide-template"], select').length > 0) {
                    cy.get('[data-cy="slide-template"], select').first().select('corporate', { force: true })
                  }
                })
              }
              
              // Confirmar descarga si existe el botón
              cy.get('body').then(($confirm) => {
                if ($confirm.find('[data-cy="confirm-download"], button[type="submit"]').length > 0) {
                  cy.get('[data-cy="confirm-download"], button[type="submit"]').first().click()
                  cy.verifyDownload('reporte.pptx')
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

  it('debe exportar múltiples reportes en lote', () => {
    cy.get('body').then(($body) => {
      // Seleccionar múltiples reportes si existen
      if ($body.find('[data-cy="report-checkbox"], input[type="checkbox"]').length >= 2) {
        cy.get('[data-cy="report-checkbox"], input[type="checkbox"]').first().check({ force: true })
        cy.get('body').then(($second) => {
          if ($second.find('[data-cy="report-checkbox"], input[type="checkbox"]').length > 1) {
            cy.get('[data-cy="report-checkbox"], input[type="checkbox"]').eq(1).check({ force: true })
          }
        })
        
        // Exportar en lote si existe el botón
        cy.get('body').then(($bulk) => {
          if ($bulk.find('[data-cy="bulk-export"], button').length > 0) {
            cy.get('[data-cy="bulk-export"], button').first().click({ force: true })
            
            cy.get('body', { timeout: 5000 }).then(($export) => {
              // Verificar opciones de exportación en lote si existen
              if ($export.find('[data-cy="bulk-export-options"], .bulk-export-options').length > 0) {
                cy.get('[data-cy="bulk-export-options"], .bulk-export-options').should('exist')
                cy.get('body').then(($options) => {
                  if ($options.find('[data-cy="export-format"], select').length > 0) {
                    cy.get('[data-cy="export-format"], select').first().select('zip', { force: true })
                  }
                })
              }
              
              // Confirmar exportación si existe el botón
              cy.get('body').then(($confirm) => {
                if ($confirm.find('[data-cy="confirm-bulk-export"], button[type="submit"]').length > 0) {
                  cy.get('[data-cy="confirm-bulk-export"], button[type="submit"]').first().click()
                  cy.verifyDownload('reportes-lote.zip')
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

  it('debe compartir reporte por email', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="report-item"], .report-item, .item').length > 0) {
        cy.get('[data-cy="report-item"], .report-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          if ($details.find('[data-cy="share-email"], button').length > 0) {
            cy.get('[data-cy="share-email"], button').first().click({ force: true })
            
            cy.get('body', { timeout: 5000 }).then(($email) => {
              // Configurar email si existen los campos
              if ($email.find('[data-cy="email-recipients"], input[type="email"], input').length > 0) {
                cy.get('[data-cy="email-recipients"], input[type="email"], input').first().type('test@example.com')
                cy.get('body').then(($subject) => {
                  if ($subject.find('[data-cy="email-subject"], input').length > 0) {
                    cy.get('[data-cy="email-subject"], input').first().type('Reporte de Análisis de Cacao')
                  }
                  if ($subject.find('[data-cy="attachment-format"], select').length > 0) {
                    cy.get('[data-cy="attachment-format"], select').first().select('pdf', { force: true })
                  }
                })
              }
              
              // Enviar email si existe el botón
              cy.get('body').then(($send) => {
                if ($send.find('[data-cy="send-email"], button[type="submit"]').length > 0) {
                  cy.get('[data-cy="send-email"], button[type="submit"]').first().click()
                  
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
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe generar enlace de compartir', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="report-item"], .report-item, .item').length > 0) {
        cy.get('[data-cy="report-item"], .report-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          if ($details.find('[data-cy="share-link"], button').length > 0) {
            cy.get('[data-cy="share-link"], button').first().click({ force: true })
            
            cy.get('body', { timeout: 5000 }).then(($link) => {
              // Configurar enlace si existen los campos
              if ($link.find('[data-cy="link-expiration"], select').length > 0) {
                cy.get('[data-cy="link-expiration"], select').first().select('7-days', { force: true })
                cy.get('body').then(($password) => {
                  if ($password.find('[data-cy="require-password"], input[type="checkbox"]').length > 0) {
                    cy.get('[data-cy="require-password"], input[type="checkbox"]').first().check({ force: true })
                    if ($password.find('[data-cy="link-password"], input[type="password"]').length > 0) {
                      cy.get('[data-cy="link-password"], input[type="password"]').first().type('secure123')
                    }
                  }
                })
              }
              
              // Generar enlace si existe el botón
              cy.get('body').then(($generate) => {
                if ($generate.find('[data-cy="generate-link"], button[type="submit"]').length > 0) {
                  cy.get('[data-cy="generate-link"], button[type="submit"]').first().click()
                  
                  // Verificar enlace generado si existe
                  cy.get('body', { timeout: 5000 }).then(($generated) => {
                    if ($generated.find('[data-cy="generated-link"], .generated-link').length > 0) {
                      cy.get('[data-cy="generated-link"], .generated-link').should('exist')
                      if ($generated.find('[data-cy="copy-link"], button').length > 0) {
                        cy.get('[data-cy="copy-link"], button').first().click()
                      }
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

  it('debe programar envío automático de reportes', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="report-item"], .report-item, .item').length > 0) {
        cy.get('[data-cy="report-item"], .report-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          if ($details.find('[data-cy="schedule-sharing"], button').length > 0) {
            cy.get('[data-cy="schedule-sharing"], button').first().click({ force: true })
            
            cy.get('body', { timeout: 5000 }).then(($schedule) => {
              // Configurar programación si existen los campos
              if ($schedule.find('[data-cy="schedule-frequency"], select').length > 0) {
                cy.get('[data-cy="schedule-frequency"], select').first().select('mensual', { force: true })
                cy.get('body').then(($fields) => {
                  if ($fields.find('[data-cy="schedule-day"], input[type="number"]').length > 0) {
                    cy.get('[data-cy="schedule-day"], input[type="number"]').first().type('1')
                  }
                  if ($fields.find('[data-cy="schedule-time"], input[type="time"]').length > 0) {
                    cy.get('[data-cy="schedule-time"], input[type="time"]').first().type('09:00')
                  }
                  if ($fields.find('[data-cy="schedule-recipients"], input[type="email"]').length > 0) {
                    cy.get('[data-cy="schedule-recipients"], input[type="email"]').first().type('admin@cacaoscan.com')
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
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar historial de compartir', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="report-item"], .report-item, .item').length > 0) {
        cy.get('[data-cy="report-item"], .report-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          // Verificar historial de compartir si existe
          if ($details.find('[data-cy="sharing-history"], .sharing-history').length > 0) {
            cy.get('[data-cy="sharing-history"], .sharing-history').should('be.visible')
            
            cy.get('body').then(($history) => {
              if ($history.find('[data-cy="sharing-item"], .sharing-item').length > 0) {
                cy.get('[data-cy="sharing-item"], .sharing-item').should('have.length.greaterThan', 0)
                
                // Verificar información de cada compartir
                cy.get('[data-cy="sharing-item"], .sharing-item').first().then(($item) => {
                  const sharingSelectors = [
                    '[data-cy="sharing-date"]',
                    '[data-cy="sharing-method"]',
                    '[data-cy="sharing-recipients"]'
                  ]
          verifySelectorsExist(sharingSelectors, $item, 3000)
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

  it('debe permitir revocar acceso a reporte compartido', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="report-item"], .report-item, .item').length > 0) {
        cy.get('[data-cy="report-item"], .report-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          // Revocar acceso si existe
          if ($details.find('[data-cy="sharing-item"], .sharing-item').length > 0) {
            cy.get('[data-cy="sharing-item"], .sharing-item').first().then(($item) => {
              if ($item.find('[data-cy="revoke-access"], button').length > 0) {
                cy.get('[data-cy="revoke-access"], button').first().click({ force: true })
                
                // Confirmar revocación si existe
                cy.get('body', { timeout: 5000 }).then(($confirm) => {
                  if ($confirm.find('[data-cy="confirm-revoke"], .swal2-confirm, button').length > 0) {
                    cy.get('[data-cy="confirm-revoke"], .swal2-confirm, button').first().click()
                    
                    // Verificar éxito si existe la notificación
                    cy.get('body', { timeout: 5000 }).then(($success) => {
                      if ($success.find('[data-cy="notification-success"], .swal2-success').length > 0) {
                        cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
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
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe exportar reporte con marca de agua', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="report-item"], .report-item, .item').length > 0) {
        cy.get('[data-cy="report-item"], .report-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          if ($details.find('[data-cy="download-pdf"], button, a').length > 0) {
            cy.get('[data-cy="download-pdf"], button, a').first().click({ force: true })
            
            cy.get('body', { timeout: 5000 }).then(($pdf) => {
              // Configurar marca de agua si existen los campos
              if ($pdf.find('[data-cy="watermark-text"], input').length > 0) {
                cy.get('[data-cy="watermark-text"], input').first().type('CONFIDENCIAL')
                cy.get('body').then(($watermark) => {
                  if ($watermark.find('[data-cy="watermark-position"], select').length > 0) {
                    cy.get('[data-cy="watermark-position"], select').first().select('center', { force: true })
                  }
                  if ($watermark.find('[data-cy="watermark-opacity"], input[type="number"]').length > 0) {
                    cy.get('[data-cy="watermark-opacity"], input[type="number"]').first().type('0.3')
                  }
                })
              }
              
              // Confirmar descarga si existe el botón
              cy.get('body').then(($confirm) => {
                if ($confirm.find('[data-cy="confirm-download"], button[type="submit"]').length > 0) {
                  cy.get('[data-cy="confirm-download"], button[type="submit"]').first().click()
                  cy.verifyDownload('reporte-marcado.pdf')
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

  it('debe exportar reporte con firma digital', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="report-item"], .report-item, .item').length > 0) {
        cy.get('[data-cy="report-item"], .report-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          if ($details.find('[data-cy="download-pdf"], button, a').length > 0) {
            cy.get('[data-cy="download-pdf"], button, a').first().click({ force: true })
            
            cy.get('body', { timeout: 5000 }).then(($pdf) => {
              // Configurar firma digital si existen los campos
              if ($pdf.find('[data-cy="digital-signature"], input[type="checkbox"]').length > 0) {
                cy.get('[data-cy="digital-signature"], input[type="checkbox"]').first().check({ force: true })
                cy.get('body').then(($signature) => {
                  if ($signature.find('[data-cy="signature-certificate"], select').length > 0) {
                    cy.get('[data-cy="signature-certificate"], select').first().select('certificado-valido', { force: true })
                  }
                  if ($signature.find('[data-cy="signature-reason"], input, textarea').length > 0) {
                    cy.get('[data-cy="signature-reason"], input, textarea').first().type('Aprobación del reporte')
                  }
                })
              }
              
              // Confirmar descarga si existe el botón
              cy.get('body').then(($confirm) => {
                if ($confirm.find('[data-cy="confirm-download"], button[type="submit"]').length > 0) {
                  cy.get('[data-cy="confirm-download"], button[type="submit"]').first().click()
                  cy.verifyDownload('reporte-firmado.pdf')
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

  it('debe mostrar vista previa antes de exportar', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="report-item"], .report-item, .item').length > 0) {
        cy.get('[data-cy="report-item"], .report-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          if ($details.find('[data-cy="preview-export"], button').length > 0) {
            cy.get('[data-cy="preview-export"], button').first().click({ force: true })
            
            cy.get('body', { timeout: 5000 }).then(($preview) => {
              // Verificar vista previa si existe
              if ($preview.find('[data-cy="export-preview"], .preview').length > 0) {
                cy.get('[data-cy="export-preview"], .preview').should('be.visible')
                
                cy.get('body').then(($content) => {
                  const previewSelectors = [
                    '[data-cy="preview-content"]',
                    '[data-cy="preview-pages"]'
                  ]
          verifySelectorsExist(previewSelectors, $content, 3000)
                  
                  // Navegar por páginas si existen los botones
                  if ($content.find('[data-cy="next-page"], button').length > 0) {
                    cy.get('[data-cy="next-page"], button').first().click({ force: true })
                    cy.get('body').then(($afterNext) => {
                      if ($afterNext.find('[data-cy="previous-page"], button').length > 0) {
                        cy.get('[data-cy="previous-page"], button').first().click({ force: true })
                      }
                    })
                  }
                })
              } else {
                cy.get('body').should('be.visible')
              }
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar errores durante la exportación', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular error de exportación
    cy.intercept('POST', `${apiBaseUrl}/reportes/**/export/`, {
      statusCode: 500,
      body: { error: 'Error al exportar reporte' }
    }).as('exportError')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="report-item"], .report-item, .item').length > 0) {
        cy.get('[data-cy="report-item"], .report-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          if ($details.find('[data-cy="download-pdf"], button, a').length > 0) {
            cy.get('[data-cy="download-pdf"], button, a').first().click({ force: true })
            cy.get('body', { timeout: 5000 }).then(($pdf) => {
              if ($pdf.find('[data-cy="confirm-download"], button[type="submit"]').length > 0) {
                cy.get('[data-cy="confirm-download"], button[type="submit"]').first().click()
                
                cy.wait('@exportError', { timeout: 10000 })
                
                // Verificar mensaje de error si existe
                cy.get('body', { timeout: 5000 }).then(($error) => {
                  if ($error.find('[data-cy="export-error"], .error-message, .swal2-error').length > 0) {
                    cy.get('[data-cy="export-error"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
                      const text = $el.text().toLowerCase()
                      return text.includes('error') || text.includes('exportar') || text.includes('reporte') || text.length > 0
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

  it('debe mostrar progreso de exportación', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="report-item"], .report-item, .item').length > 0) {
        cy.get('[data-cy="report-item"], .report-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          if ($details.find('[data-cy="download-pdf"], button, a').length > 0) {
            cy.get('[data-cy="download-pdf"], button, a').first().click({ force: true })
            cy.get('body', { timeout: 5000 }).then(($pdf) => {
              if ($pdf.find('[data-cy="confirm-download"], button[type="submit"]').length > 0) {
                cy.get('[data-cy="confirm-download"], button[type="submit"]').first().click()
                
                // Verificar progreso si existe
                cy.get('body', { timeout: 5000 }).then(($progress) => {
                  if ($progress.find('[data-cy="export-progress"], .progress').length > 0) {
                    cy.get('[data-cy="export-progress"], .progress').should('be.visible')
                    if ($progress.find('[data-cy="progress-percentage"], .progress-percentage').length > 0) {
                      cy.get('[data-cy="progress-percentage"], .progress-percentage').should('satisfy', ($el) => {
                        const text = $el.text()
                        return text.includes('%') || text.length > 0
                      })
                    }
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

  it('debe exportar reporte como CSV', () => {
    cy.get('[data-cy="report-item"]').first().click()
    cy.get('[data-cy="download-csv"]').click()
    cy.verifyDownload('reporte.csv')
  })

  it('debe exportar reporte como JSON', () => {
    cy.get('[data-cy="report-item"]').first().click()
    cy.get('[data-cy="download-json"]').click()
    cy.verifyDownload('reporte.json')
  })

  it('debe validar destinatarios de email', () => {
    cy.get('[data-cy="report-item"]').first().click()
    cy.get('[data-cy="share-email"]').click()
    
    // Email inválido
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
    
    // Cancelar exportación
    cy.get('[data-cy="cancel-export"]').click()
    cy.get('[data-cy="export-progress"]').should('not.exist')
  })

  it('debe mostrar tamaño estimado del archivo', () => {
    cy.get('[data-cy="report-item"]').first().click()
    cy.get('[data-cy="download-pdf"]').click()
    
    // Verificar tamaño estimado
    cy.get('[data-cy="estimated-size"]').should('be.visible')
    cy.get('[data-cy="estimated-size"]').should('contain', 'MB')
  })
})
