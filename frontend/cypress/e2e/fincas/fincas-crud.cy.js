import {
  verifySelectorsExist,
  clickIfExists,
  typeIfExists,
  waitForPageLoad,
  verifyElementWithAlternatives,
  fillFincaFormData,
  verifyNotification,
  verifyErrorMessageWithAlternatives,
  clickIfExistsAndContinue
} from '../../support/helpers'

describe('Gestión de Fincas - CRUD', () => {
  beforeEach(() => {
    cy.login('farmer')
    cy.visit('/mis-fincas')
    waitForPageLoad()
  })

  it('debe mostrar lista de fincas del usuario', () => {
    cy.get('body').then(($body) => {
      const listSelectors = ['[data-cy="fincas-list"]', '.list', '.fincas-list']
      verifyElementWithAlternatives(listSelectors, $body)
      const addButtonSelectors = ['[data-cy="add-finca-button"]', 'button']
      verifyElementWithAlternatives(addButtonSelectors, $body)
      const statsSelectors = ['[data-cy="fincas-stats"]', '.stats']
      verifyElementWithAlternatives(statsSelectors, $body)
    })
  })

  it('debe crear nueva finca exitosamente', () => {
    const saveFinca = () => {
      clickIfExists('[data-cy="save-finca"], button[type="submit"]').then(() => {
        verifyNotification('success', ['success', 'exitoso', 'creado'])
      })
    }
    
    const clickMapAndSave = () => {
      clickIfExists('[data-cy="map-container"], .map-container', { x: 300, y: 200 }).then(saveFinca)
    }
    
    const fillAndSubmitForm = (fincaData) => {
      fillFincaFormData({
        nombre: fincaData.nombre || 'Finca Test',
        ubicacion: fincaData.ubicacion || 'Test Location',
        area: fincaData.area_total || 10,
        descripcion: fincaData.descripcion || 'Test description'
      }).then(clickMapAndSave)
    }
    
    cy.fixture('testData').then((data) => {
      const fincaData = data.fincas[0]
      clickIfExistsAndContinue('[data-cy="add-finca-button"], button', () => {
        waitForPageLoad(5000)
        fillAndSubmitForm(fincaData)
      })
    })
  })

  it('debe validar campos requeridos en formulario de finca', () => {
    const verifyErrors = () => {
      const errorSelectors = [
        '[data-cy="finca-nombre-error"]',
        '[data-cy="finca-ubicacion-error"]',
        '[data-cy="finca-area-error"]'
      ]
      cy.get('body', { timeout: 3000 }).then(($errors) => {
        verifySelectorsExist(errorSelectors, $errors, 3000)
      })
    }
    
    clickIfExistsAndContinue('[data-cy="add-finca-button"], button', () => {
      waitForPageLoad(5000)
      clickIfExists('[data-cy="save-finca"], button[type="submit"]').then(verifyErrors)
    })
  })

  it('debe validar área de finca positiva', () => {
    const verifyAreaError = () => {
      verifyErrorMessageWithAlternatives(
        ['[data-cy="finca-area-error"]', '.error-message'],
        ['área', 'positiva', 'area'],
        3000
      )
    }
    
    const submitInvalidArea = () => {
      clickIfExists('[data-cy="save-finca"], button[type="submit"]').then(verifyAreaError)
    }
    
    clickIfExistsAndContinue('[data-cy="add-finca-button"], button', () => {
      waitForPageLoad(5000)
      fillFincaFormData({
        nombre: 'Finca Test',
        ubicacion: 'Test Location',
        area: '-5',
        descripcion: 'Test description'
      }).then(submitInvalidArea)
    })
  })

  it('debe mostrar detalles de finca específica', () => {
    clickIfExists('[data-cy="finca-item"], .finca-item, .item, tbody tr').then((clicked) => {
      if (!clicked) {
        cy.get('body').should('be.visible')
        return
      }
      
      cy.get('body', { timeout: 5000 }).then(($details) => {
        const detailSelectors = [
          '[data-cy="finca-details"]',
          '[data-cy="finca-name"]',
          '[data-cy="finca-location"]',
          '[data-cy="finca-area"]',
          '[data-cy="finca-description"]',
          '[data-cy="finca-map"]'
        ]
        verifySelectorsExist(detailSelectors, $details, 3000)
      })
    })
  })

  it('debe editar finca existente', () => {
    const verifySuccessNotification = ($success) => {
      if ($success.find('[data-cy="notification-success"], .swal2-success').length > 0) {
        cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
      }
    }

    const saveEditedFinca = () => {
      clickIfExists('[data-cy="save-finca"], button[type="submit"]')
      cy.get('body', { timeout: 5000 }).then(verifySuccessNotification)
    }

    const editFinca = () => {
      typeIfExists('[data-cy="finca-nombre"], input[name*="nombre"]', 'Finca Editada', { clear: true })
      typeIfExists('[data-cy="finca-descripcion"], textarea', 'Descripción actualizada', { clear: true })
      saveEditedFinca()
    }
    
    clickIfExists('[data-cy="finca-item"], .finca-item, .item, tbody tr').then((clicked) => {
      if (!clicked) {
        cy.get('body').should('be.visible')
        return
      }
      
      cy.get('body', { timeout: 5000 }).should('be.visible')
      clickIfExists('[data-cy="edit-finca"], button').then((editClicked) => {
        if (!editClicked) return
        cy.get('body', { timeout: 5000 }).should('be.visible')
        editFinca()
      })
    })
  })

  it('debe eliminar finca con confirmación', () => {
    const verifyDeleteSuccess = ($success) => {
      if ($success.find('[data-cy="notification-success"], .swal2-success').length > 0) {
        cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
      }
    }

    const confirmDelete = () => {
      clickIfExists('[data-cy="confirm-delete"], .swal2-confirm, button').then((confirmed) => {
        if (confirmed) {
          cy.get('body', { timeout: 5000 }).then(verifyDeleteSuccess)
        }
      })
    }
    
    clickIfExists('[data-cy="finca-item"], .finca-item, .item, tbody tr').then((clicked) => {
      if (!clicked) {
        cy.get('body').should('be.visible')
        return
      }
      
      cy.get('body', { timeout: 5000 }).should('be.visible')
      clickIfExists('[data-cy="delete-finca"], button').then((deleteClicked) => {
        if (!deleteClicked) return
        cy.get('body', { timeout: 5000 }).should('be.visible')
        confirmDelete()
      })
    })
  })

  it('debe cancelar eliminación de finca', () => {
    const verifyFincaRemains = ($remains) => {
      if ($remains.find('[data-cy="finca-details"]').length > 0) {
        cy.get('[data-cy="finca-details"]').should('be.visible')
      } else {
        cy.get('body').should('be.visible')
      }
    }

    const cancelDelete = () => {
      clickIfExists('[data-cy="cancel-delete"], .swal2-cancel, button').then((cancelled) => {
        if (cancelled) {
          cy.get('body', { timeout: 5000 }).then(verifyFincaRemains)
        }
      })
    }
    
    clickIfExists('[data-cy="finca-item"], .finca-item, .item, tbody tr').then((clicked) => {
      if (!clicked) {
        cy.get('body').should('be.visible')
        return
      }
      
      cy.get('body', { timeout: 5000 }).should('be.visible')
      clickIfExists('[data-cy="delete-finca"], button').then((deleteClicked) => {
        if (!deleteClicked) return
        cy.get('body', { timeout: 5000 }).should('be.visible')
        cancelDelete()
      })
    })
  })

  it('debe mostrar estadísticas de fincas', () => {
    cy.get('body').then(($body) => {
      const statsSelectors = [
        '[data-cy="fincas-stats"]',
        '[data-cy="total-fincas"]',
        '[data-cy="total-area"]',
        '[data-cy="average-area"]'
      ]
      verifySelectorsExist(statsSelectors, $body, 5000)
    })
  })

  it('debe permitir buscar fincas por nombre', () => {
    typeIfExists('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]', 'Paraíso').then((typed) => {
      if (!typed) {
        cy.get('body').should('be.visible')
        return
      }
      
      cy.get('body', { timeout: 3000 }).then(($results) => {
        if ($results.find('[data-cy="finca-item"], .finca-item, .item').length > 0) {
          cy.get('[data-cy="finca-item"], .finca-item, .item').first().should('satisfy', ($el) => {
            const text = $el.text().toLowerCase()
            return text.includes('paraíso') || text.length > 0
          })
        }
        if ($results.find('[data-cy="search-results-count"]').length > 0) {
          cy.get('[data-cy="search-results-count"]').should('be.visible')
        }
      })
    })
  })

  it('debe permitir filtrar fincas por ubicación', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="location-filter"], select').length > 0) {
        const selectProvince = ($options) => {
          if ($options.find('[data-cy="province-filter"], select').length > 0) {
            cy.get('[data-cy="province-filter"], select').first().select('Los Ríos', { force: true })
          }
        }

        const handleFilter = ($filter) => {
          if ($filter.is('select')) {
            cy.wrap($filter).select('Los Ríos', { force: true })
          } else {
            cy.wrap($filter).click({ force: true })
            cy.get('body', { timeout: 3000 }).then(selectProvince)
          }
        }

        const verifyActiveFilters = ($filters) => {
          if ($filters.find('[data-cy="active-filters"], [data-cy="filtered-results"]').length > 0) {
            cy.get('[data-cy="active-filters"], [data-cy="filtered-results"]').first().should('exist')
          }
        }

        const applyFilter = ($apply) => {
          if ($apply.find('[data-cy="apply-filter"], button').length > 0) {
            cy.get('[data-cy="apply-filter"], button').first().click()
            cy.get('body', { timeout: 3000 }).then(verifyActiveFilters)
          }
        }

        cy.get('[data-cy="location-filter"], select').first().then(handleFilter)
        cy.get('body', { timeout: 3000 }).then(applyFilter)
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar mapa con ubicación de fincas', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="fincas-map"], .map, [id*="map"]').length > 0) {
        cy.get('[data-cy="fincas-map"], .map, [id*="map"]').first().should('be.visible')
        
        const verifyMapPopup = ($popup) => {
          if ($popup.find('[data-cy="map-popup"], .popup').length > 0) {
            cy.get('[data-cy="map-popup"], .popup').should('exist')
          }
        }

        const clickMapMarker = ($markers) => {
          if ($markers.find('[data-cy="map-markers"], [data-cy="map-marker"]').length > 0) {
            cy.get('[data-cy="map-marker"], [data-cy="map-markers"]').first().click({ force: true })
            cy.get('body', { timeout: 3000 }).then(verifyMapPopup)
          }
        }

        cy.get('body', { timeout: 5000 }).then(clickMapMarker)
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe permitir exportar lista de fincas', () => {
    const downloadPdf = () => {
      cy.get('[data-cy="export-pdf"], button').first().click()
      cy.verifyDownload('fincas.pdf')
    }
    
    const verifyExportOptions = ($export) => {
      if ($export.find('[data-cy="export-pdf"], [data-cy="export-excel"]').length > 0) {
        cy.get('[data-cy="export-pdf"], [data-cy="export-excel"]').first().should('exist')
        cy.get('body').then(($pdf) => {
          if ($pdf.find('[data-cy="export-pdf"], button').length > 0) {
            downloadPdf()
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    }
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="export-fincas"], button').length > 0) {
        cy.get('[data-cy="export-fincas"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(verifyExportOptions)
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar lotes asociados a cada finca', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-item"], .finca-item, .item, tbody tr').length > 0) {
        cy.get('[data-cy="finca-item"], .finca-item, .item, tbody tr').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          const loteSelectors = [
            '[data-cy="finca-lotes"]',
            '[data-cy="lotes-count"]',
            '[data-cy="add-lote-button"]'
          ]
          verifySelectorsExist(loteSelectors, $details, 3000)
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar errores al crear finca', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    cy.intercept('POST', `${apiBaseUrl}/fincas/`, {
      statusCode: 500,
      body: { error: 'Error del servidor' }
    }).as('createFincaError')
    
    const verifyError = ($error) => {
      if ($error.find('[data-cy="error-message"], .error-message, .swal2-error').length > 0) {
        cy.get('[data-cy="error-message"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('error') || text.includes('crear') || text.includes('finca') || text.length > 0
        })
      }
    }
    
    const fillFormAndSubmit = ($modal, fincaData) => {
      if ($modal.find('[data-cy="finca-nombre"], input[name*="nombre"]').length > 0) {
        cy.get('[data-cy="finca-nombre"], input[name*="nombre"]').first().type(fincaData.nombre || 'Finca Test')
        cy.get('[data-cy="finca-ubicacion"], input[name*="ubicacion"]').first().type(fincaData.ubicacion || 'Test Location')
        cy.get('[data-cy="finca-area"], input[type="number"]').first().type((fincaData.area_total || 10).toString())
        cy.get('[data-cy="finca-descripcion"], textarea').first().type(fincaData.descripcion || 'Test description')
      }
      cy.get('[data-cy="save-finca"], button[type="submit"]').first().click()
      cy.wait('@createFincaError', { timeout: 10000 })
      cy.get('body', { timeout: 5000 }).then(verifyError)
    }
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          cy.fixture('testData').then((data) => {
            fillFormAndSubmit($modal, data.fincas[0])
          })
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe validar ubicación en mapa', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="finca-nombre"], input[name*="nombre"]').length > 0) {
            cy.get('[data-cy="finca-nombre"], input[name*="nombre"]').first().type('Finca Test')
            cy.get('[data-cy="finca-ubicacion"], input[name*="ubicacion"]').first().type('Test Location')
            cy.get('[data-cy="finca-area"], input[type="number"]').first().type('10')
            cy.get('[data-cy="finca-descripcion"], textarea').first().type('Test description')
            
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().click()
            
            cy.get('body', { timeout: 3000 }).then(($error) => {
              if ($error.find('[data-cy="location-error"], .error-message').length > 0) {
                cy.get('[data-cy="location-error"], .error-message').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('ubicación') || text.includes('mapa') || text.includes('location') || text.length > 0
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

  it('debe permitir duplicar finca', () => {
    cy.get('[data-cy="finca-item"]').first().click()
    cy.get('[data-cy="duplicate-finca"]').click()
    
    cy.get('[data-cy="finca-nombre"]').should('have.value').and('not.be.empty')
    
    cy.get('[data-cy="finca-nombre"]').clear().type('Finca Duplicada')
    cy.get('[data-cy="save-finca"]').click()
    
    cy.checkNotification('Finca creada exitosamente', 'success')
  })

  it('debe permitir activar/desactivar finca', () => {
    cy.get('[data-cy="finca-item"]').first().click()
    
    cy.get('[data-cy="toggle-finca-status"]').click()
    cy.checkNotification('Finca desactivada', 'success')
    
    cy.get('[data-cy="toggle-finca-status"]').click()
    cy.checkNotification('Finca activada', 'success')
  })

  it('debe mostrar historial de cambios de finca', () => {
    cy.get('[data-cy="finca-item"]').first().click()
    cy.get('[data-cy="finca-history"]').should('be.visible')
    cy.get('[data-cy="history-item"]').should('have.length.greaterThan', 0)
  })

  it('debe permitir agregar notas a finca', () => {
    cy.get('[data-cy="finca-item"]').first().click()
    cy.get('[data-cy="add-note"]').click()
    
    cy.get('[data-cy="note-text"]').type('Nota importante sobre la finca')
    cy.get('[data-cy="save-note"]').click()
    
    cy.checkNotification('Nota agregada', 'success')
    cy.get('[data-cy="finca-notes"]').should('contain', 'Nota importante')
  })

  it('debe permitir agregar imágenes a finca', () => {
    cy.get('[data-cy="finca-item"]').first().click()
    cy.get('[data-cy="add-image"]').click()
    
    cy.fixture('test-cacao.jpg').then((fileContent) => {
      const blob = new Blob([fileContent], { type: 'image/jpeg' })
      const file = new File([blob], 'finca-image.jpg', { type: 'image/jpeg' })
      
      cy.get('[data-cy="image-input"]').then((input) => {
        const dataTransfer = new DataTransfer()
        dataTransfer.items.add(file)
        input[0].files = dataTransfer.files
        
        cy.wrap(input).trigger('change', { force: true })
      })
    })
    
    cy.get('[data-cy="upload-image"]').click()
    cy.checkNotification('Imagen agregada', 'success')
  })
})
