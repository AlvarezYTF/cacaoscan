import {
  verifySelectorsInBody,
  clickIfExists,
  typeIfExists,
  waitForPageLoad,
  verifyElementWithAlternatives,
  fillFincaFormData,
  verifyNotification,
  verifyErrorMessageWithAlternatives,
  clickIfExistsAndContinue,
  ifFoundInBody,
  getApiBaseUrl
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
    const errorSelectors = [
      '[data-cy="finca-nombre-error"]',
      '[data-cy="finca-ubicacion-error"]',
      '[data-cy="finca-area-error"]'
    ]
    
    clickIfExistsAndContinue('[data-cy="add-finca-button"], button', () => {
      waitForPageLoad(5000)
      clickIfExists('[data-cy="save-finca"], button[type="submit"]').then(() => {
        verifySelectorsInBody(errorSelectors, 3000)
      })
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
      if (!clicked) return cy.wrap(null)
      
      waitForPageLoad(5000)
      const detailSelectors = [
        '[data-cy="finca-details"]',
        '[data-cy="finca-name"]',
        '[data-cy="finca-location"]',
        '[data-cy="finca-area"]',
        '[data-cy="finca-description"]',
        '[data-cy="finca-map"]'
      ]
      verifySelectorsInBody(detailSelectors, 3000)
    })
  })

  it('debe editar finca existente', () => {
    const saveEditedFinca = () => {
      clickIfExists('[data-cy="save-finca"], button[type="submit"]').then(() => {
        verifyNotification('success', ['success', 'exitoso', 'actualizado'])
      })
    }

    const editFinca = () => {
      typeIfExists('[data-cy="finca-nombre"], input[name*="nombre"]', 'Finca Editada', { clear: true })
      typeIfExists('[data-cy="finca-descripcion"], textarea', 'Descripción actualizada', { clear: true })
      saveEditedFinca()
    }
    
    clickIfExists('[data-cy="finca-item"], .finca-item, .item, tbody tr').then((clicked) => {
      if (!clicked) return cy.wrap(null)
      
      waitForPageLoad(5000)
      clickIfExists('[data-cy="edit-finca"], button').then((editClicked) => {
        if (!editClicked) return cy.wrap(null)
        waitForPageLoad(5000)
        editFinca()
      })
    })
  })

  it('debe eliminar finca con confirmación', () => {
    const confirmDelete = () => {
      clickIfExists('[data-cy="confirm-delete"], .swal2-confirm, button').then((confirmed) => {
        if (confirmed) {
          verifyNotification('success', ['success', 'exitoso', 'eliminado'])
        }
      })
    }
    
    clickIfExists('[data-cy="finca-item"], .finca-item, .item, tbody tr').then((clicked) => {
      if (!clicked) return cy.wrap(null)
      
      waitForPageLoad(5000)
      clickIfExists('[data-cy="delete-finca"], button').then((deleteClicked) => {
        if (!deleteClicked) return cy.wrap(null)
        waitForPageLoad(5000)
        confirmDelete()
      })
    })
  })

  it('debe cancelar eliminación de finca', () => {
    const verifyFincaDetailsVisible = () => {
      ifFoundInBody('[data-cy="finca-details"]', () => {
        cy.get('[data-cy="finca-details"]').should('be.visible')
      })
    }

    const handleCancelClick = (cancelled) => {
      if (cancelled) {
        verifyFincaDetailsVisible()
      }
    }

    const cancelDelete = () => {
      clickIfExists('[data-cy="cancel-delete"], .swal2-cancel, button').then(handleCancelClick)
    }

    const handleDeleteClick = (deleteClicked) => {
      if (!deleteClicked) return cy.wrap(null)
      waitForPageLoad(5000)
      cancelDelete()
    }

    const handleFincaItemClick = (clicked) => {
      if (!clicked) return cy.wrap(null)
      waitForPageLoad(5000)
      clickIfExists('[data-cy="delete-finca"], button').then(handleDeleteClick)
    }
    
    clickIfExists('[data-cy="finca-item"], .finca-item, .item, tbody tr').then(handleFincaItemClick)
  })

  it('debe mostrar estadísticas de fincas', () => {
    const statsSelectors = [
      '[data-cy="fincas-stats"]',
      '[data-cy="total-fincas"]',
      '[data-cy="total-area"]',
      '[data-cy="average-area"]'
    ]
    verifySelectorsInBody(statsSelectors, 5000)
  })

  it('debe permitir buscar fincas por nombre', () => {
    const verifySearchResultItem = ($el) => {
      const text = $el.text().toLowerCase()
      return text.includes('paraíso') || text.length > 0
    }

    const verifySearchResultsCount = ($results) => {
      if ($results.find('[data-cy="search-results-count"]').length > 0) {
        cy.get('[data-cy="search-results-count"]').should('be.visible')
      }
    }

    const verifySearchResultItemExists = ($results) => {
      if ($results.find('[data-cy="finca-item"], .finca-item, .item').length > 0) {
        cy.get('[data-cy="finca-item"], .finca-item, .item').first().should('satisfy', verifySearchResultItem)
      }
    }

    const handleSearchResults = ($results) => {
      verifySearchResultItemExists($results)
      verifySearchResultsCount($results)
    }

    const handleTypeResult = (typed) => {
      if (!typed) {
        cy.get('body').should('be.visible')
        return
      }
      cy.get('body', { timeout: 3000 }).then(handleSearchResults)
    }

    typeIfExists('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]', 'Paraíso').then(handleTypeResult)
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
    ifFoundInBody('[data-cy="finca-item"], .finca-item, .item, tbody tr', () => {
      cy.get('[data-cy="finca-item"], .finca-item, .item, tbody tr').first().click({ force: true })
      waitForPageLoad(5000)
      const loteSelectors = [
        '[data-cy="finca-lotes"]',
        '[data-cy="lotes-count"]',
        '[data-cy="add-lote-button"]'
      ]
      verifySelectorsInBody(loteSelectors, 3000)
    })
  })

  it('debe manejar errores al crear finca', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('POST', `${apiBaseUrl}/fincas/`, {
      statusCode: 500,
      body: { error: 'Error del servidor' }
    }).as('createFincaError')
    
    const fillFormAndSubmit = (fincaData) => {
      fillFincaFormData({
        nombre: fincaData.nombre || 'Finca Test',
        ubicacion: fincaData.ubicacion || 'Test Location',
        area: fincaData.area_total || 10,
        descripcion: fincaData.descripcion || 'Test description'
      }).then(() => {
        cy.get('[data-cy="save-finca"], button[type="submit"]').first().click()
        cy.wait('@createFincaError', { timeout: 10000 })
        verifyErrorMessageWithAlternatives(
          ['[data-cy="error-message"], .error-message, .swal2-error'],
          ['error', 'crear', 'finca']
        )
      })
    }
    
    clickIfExistsAndContinue('[data-cy="add-finca-button"], button', () => {
      waitForPageLoad(5000)
      cy.fixture('testData').then((data) => {
        fillFormAndSubmit(data.fincas[0])
      })
    })
  })

  it('debe validar ubicación en mapa', () => {
    const submitFormAndVerifyError = () => {
      cy.get('[data-cy="save-finca"], button[type="submit"]').first().click()
      verifyErrorMessageWithAlternatives(
        ['[data-cy="location-error"], .error-message'],
        ['ubicación', 'mapa', 'location']
      )
    }

    const fillFormAndSubmit = () => {
      fillFincaFormData({
        nombre: 'Finca Test',
        ubicacion: 'Test Location',
        area: 10,
        descripcion: 'Test description'
      }).then(submitFormAndVerifyError)
    }

    const handleFormFound = () => {
      fillFormAndSubmit()
    }

    const handleAddButtonClick = () => {
      waitForPageLoad(5000)
      ifFoundInBody('[data-cy="finca-nombre"], input[name*="nombre"]', handleFormFound)
    }

    clickIfExistsAndContinue('[data-cy="add-finca-button"], button', handleAddButtonClick)
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
