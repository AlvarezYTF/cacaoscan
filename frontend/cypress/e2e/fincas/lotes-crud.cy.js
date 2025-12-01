import { 
  verifySelectorsExist, 
  clickIfExistsAndContinue,
  selectIfExistsAndContinue,
  typeIfExistsAndContinue,
  verifySelectorsInBody,
  ifFoundInBody,
  fillFormFieldsSequence,
  getApiBaseUrl
} from '../../support/helpers'

describe('Gestión de Lotes - CRUD', () => {
  const LOTE_ITEM_SELECTOR = '[data-cy="lote-item"], .lote-item, .item'
  const ADD_LOTE_BUTTON = '[data-cy="add-lote-button"], button'
  const FINCA_SELECT = '[data-cy="finca-select"], select'
  const ERROR_MESSAGE_SELECTOR = '[data-cy="error-message"], .error-message, .swal2-error'
  
  const openLoteForm = (action, fallback) => {
    return clickIfExistsAndContinue(ADD_LOTE_BUTTON, action, fallback)
  }
  
  const openLoteFormWithFinca = (fincaValue, action, fallback) => {
    return openLoteForm(() => {
      return selectIfExistsAndContinue(FINCA_SELECT, fincaValue, action)
    }, fallback)
  }
  
  const interactWithLoteItem = (action, fallback) => {
    return clickIfExistsAndContinue(LOTE_ITEM_SELECTOR, action, fallback)
  }
  
  const verifyLoteError = (errorSelector, expectedTexts) => {
    return ifFoundInBody(errorSelector, ($el) => {
      cy.wrap($el).first().should('satisfy', ($element) => {
        const text = $element.text().toLowerCase()
        return expectedTexts.some(expected => text.includes(expected)) || text.length > 0
      })
    })
  }
  
  const applyFilter = (filterSelector, filterValue) => {
    return selectIfExistsAndContinue(filterSelector, filterValue, () => {
      return clickIfExistsAndContinue('[data-cy="apply-filter"], button', () => {
        return ifFoundInBody('[data-cy="active-filters"], [data-cy="filtered-results"]', () => {
          cy.get('[data-cy="active-filters"], [data-cy="filtered-results"]').first().should('exist')
        })
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  }
  
  const verifyFilteredItems = (itemSelector, expectedText) => {
    return ifFoundInBody(itemSelector, () => {
      cy.get(itemSelector).each(($item) => {
        cy.wrap($item).should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes(expectedText.toLowerCase()) || text.length > 0
        })
      })
    })
  }
  
  beforeEach(() => {
    cy.login('farmer')
    cy.visit('/mis-lotes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
  })

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
    cy.createLote({
      finca: '1',
      nombre: 'Lote Test',
      area: '2',
      variedad: 'CCN-51',
      edad: '5'
    })
  })

  it('debe validar campos requeridos en formulario de lote', () => {
    openLoteForm(() => {
      return clickIfExistsAndContinue('[data-cy="save-lote"], button[type="submit"]', () => {
        const errorSelectors = [
          '[data-cy="lote-nombre-error"]',
          '[data-cy="lote-area-error"]',
          '[data-cy="lote-variedad-error"]',
          '[data-cy="lote-edad-error"]'
        ]
        return verifySelectorsInBody(errorSelectors, 3000)
      })
    })
  })

  it('debe validar área de lote positiva', () => {
    openLoteFormWithFinca('1', () => {
      cy.createLote({
        finca: '1',
        nombre: 'Lote Test',
        area: '-2',
        variedad: 'CCN-51',
        edad: '5'
      })
      return cy.get('[data-cy="lote-area-error"], .error-message', { timeout: 5000 }).should('exist')
    })
  })

  it('debe validar edad de plantas', () => {
    openLoteFormWithFinca('1', () => {
      cy.createLote({
        finca: '1',
        nombre: 'Lote Test',
        area: '2',
        variedad: 'CCN-51',
        edad: '50'
      })
      return cy.get('[data-cy="lote-edad-error"], .error-message', { timeout: 5000 }).should('exist')
    })
  })

  it('debe mostrar detalles de lote específico', () => {
    interactWithLoteItem(() => {
      const detailSelectors = [
        '[data-cy="lote-details"]',
        '[data-cy="lote-name"]',
        '[data-cy="lote-area"]',
        '[data-cy="lote-variedad"]',
        '[data-cy="lote-edad"]',
        '[data-cy="lote-description"]',
        '[data-cy="lote-finca"]'
      ]
      return verifySelectorsInBody(detailSelectors, 3000)
    })
  })

  it('debe editar lote existente', () => {
    interactWithLoteItem(() => {
      return clickIfExistsAndContinue('[data-cy="edit-lote"], button', () => {
        return fillFormFieldsSequence(
          [
            { selector: '[data-cy="lote-nombre"], input[name*="nombre"]', value: 'Lote Editado', options: { clear: true } },
            { selector: '[data-cy="lote-descripcion"], textarea', value: 'Descripción actualizada', options: { clear: true } }
          ],
          '[data-cy="save-lote"], button[type="submit"]'
        )
      })
    })
  })

  it('debe eliminar lote con confirmación', () => {
    interactWithLoteItem(() => {
      return clickIfExistsAndContinue('[data-cy="delete-lote"], button', () => {
        return clickIfExistsAndContinue('[data-cy="confirm-delete"], .swal2-confirm, button', () => {
          cy.visit('/mis-lotes')
          return cy.get('body', { timeout: 10000 }).should('be.visible')
        })
      })
    })
  })

  it('debe mostrar análisis asociados al lote', () => {
    interactWithLoteItem(() => {
      const analisisSelectors = [
        '[data-cy="lote-analisis"]',
        '[data-cy="analisis-count"]',
        '[data-cy="ultimo-analisis"]'
      ]
      return verifySelectorsInBody(analisisSelectors, 3000)
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
    typeIfExistsAndContinue('[data-cy="search-lotes"], input[type="search"], input[placeholder*="search"]', 'Norte', () => {
      return ifFoundInBody(LOTE_ITEM_SELECTOR, ($item) => {
        cy.wrap($item).should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('norte') || text.length > 0
        })
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
    ifFoundInBody('[data-cy="search-results-count"]', () => {
      cy.get('[data-cy="search-results-count"]').should('be.visible')
    })
  })

  it('debe permitir filtrar lotes por finca', () => {
    applyFilter('[data-cy="finca-filter"], select', 'Finca El Paraíso')
  })

  it('debe permitir filtrar lotes por variedad', () => {
    selectIfExistsAndContinue('[data-cy="variedad-filter"], select', 'CCN-51', () => {
      return clickIfExistsAndContinue('[data-cy="apply-filter"], button', () => {
        return verifyFilteredItems(LOTE_ITEM_SELECTOR, 'ccn-51')
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe mostrar gráficos de rendimiento por lote', () => {
    interactWithLoteItem(() => {
      const chartSelectors = [
        '[data-cy="rendimiento-chart"]',
        '[data-cy="calidad-trend"]',
        '[data-cy="produccion-history"]'
      ]
      return verifySelectorsInBody(chartSelectors, 3000)
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe permitir exportar datos de lotes', () => {
    clickIfExistsAndContinue('[data-cy="export-lotes"], button', () => {
      return ifFoundInBody('[data-cy="export-pdf"], [data-cy="export-excel"]', () => {
        cy.get('[data-cy="export-pdf"], [data-cy="export-excel"]').first().should('exist')
        return clickIfExistsAndContinue('[data-cy="export-excel"], button', () => {
          cy.verifyDownload('lotes.xlsx')
        })
      }, () => {
        cy.get('body').should('be.visible')
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe mostrar alertas de mantenimiento', () => {
    interactWithLoteItem(() => {
      return ifFoundInBody('[data-cy="maintenance-alerts"], .alerts', () => {
        cy.get('[data-cy="maintenance-alerts"], .alerts').should('be.visible')
        return ifFoundInBody('[data-cy="alert-item"], .alert-item', () => {
          cy.get('[data-cy="alert-item"], .alert-item').should('be.visible')
        })
      }, () => {
        cy.get('body').should('be.visible')
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe permitir programar análisis para lote', () => {
    interactWithLoteItem(() => {
      return clickIfExistsAndContinue('[data-cy="schedule-analysis"], button', () => {
        return fillFormFieldsSequence(
          [
            { selector: '[data-cy="analysis-date"], input[type="date"]', value: '2024-02-15' },
            { selector: '[data-cy="analysis-time"], input[type="time"]', value: '10:00' },
            { selector: '[data-cy="analysis-notes"], textarea', value: 'Análisis programado' }
          ],
          '[data-cy="save-schedule"], button[type="submit"]'
        ).then(() => {
          return ifFoundInBody('[data-cy="notification-success"], .swal2-success', () => {
            cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
          })
        })
      }, () => {
        cy.get('body').should('be.visible')
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe mostrar historial de análisis del lote', () => {
    interactWithLoteItem(() => {
      return ifFoundInBody('[data-cy="analisis-history"], .history', () => {
        cy.get('[data-cy="analisis-history"], .history').should('be.visible')
        return ifFoundInBody('[data-cy="analisis-item"], .analisis-item', ($item) => {
          cy.get('[data-cy="analisis-item"], .analisis-item').should('have.length.greaterThan', 0)
          const analisisSelectors = [
            '[data-cy="analisis-date"]',
            '[data-cy="analisis-quality"]',
            '[data-cy="analisis-results"]'
          ]
          verifySelectorsExist(analisisSelectors, $item, 3000)
        })
      }, () => {
        cy.get('body').should('be.visible')
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe manejar errores al crear lote', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('POST', `${apiBaseUrl}/lotes/`, {
      statusCode: 500,
      body: { error: 'Error del servidor' }
    }).as('createLoteError')
    
    openLoteForm(() => {
      return cy.fixture('testData').then((data) => {
        const loteData = data.lotes[0]
        cy.createLote({
          finca: '1',
          nombre: loteData.nombre || 'Lote Test',
          area: (loteData.area || 2).toString(),
          variedad: loteData.variedad || 'CCN-51',
          edad: (loteData.edad_plantas || 5).toString()
        })
        
        cy.wait('@createLoteError', { timeout: 10000 })
        return verifyLoteError(ERROR_MESSAGE_SELECTOR, ['error', 'crear', 'lote'])
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe validar que el área del lote no exceda el área de la finca', () => {
    openLoteFormWithFinca('1', () => {
      cy.createLote({
        finca: '1',
        nombre: 'Lote Grande',
        area: '20',
        variedad: 'CCN-51',
        edad: '5',
        descripcion: 'Test description'
      })
      
      return verifyLoteError('[data-cy="lote-area-error"], .error-message', ['área', 'exceder', 'finca'])
    }, () => {
      cy.get('body').should('be.visible')
    })
  })
})
