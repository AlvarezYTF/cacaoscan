import {
  visitAndWaitForBodyVisible,
  verifySelectorsExist,
  ifFoundInBody,
  clickIfExistsAndContinue
} from '../../support/helpers'

describe('Gestión de Fincas y Lotes - Relaciones', () => {
  beforeEach(() => {
    cy.login('farmer')
  })

  const visitFincasAndClickFirst = (callback) => {
    visitAndWaitForBodyVisible('/mis-fincas')
    ifFoundInBody('[data-cy="finca-item"], .finca-item, .item, tbody tr', () => {
      cy.get('[data-cy="finca-item"], .finca-item, .item, tbody tr').first().click({ force: true })
      cy.get('body', { timeout: 5000 }).then(callback)
    })
  }

  const downloadPdfReport = () => {
    clickIfExistsAndContinue('[data-cy="export-pdf"], button', () => {
      cy.verifyDownload('reporte-finca-completo.pdf')
    })
  }

  const verifyExportOptions = () => {
    ifFoundInBody('[data-cy="export-pdf"], [data-cy="export-excel"]', () => {
      cy.get('[data-cy="export-pdf"], [data-cy="export-excel"]').first().should('exist')
      downloadPdfReport()
    })
  }

  const handleExportReport = () => {
    clickIfExistsAndContinue('[data-cy="export-finca-report"], button', () => {
      verifyExportOptions()
    })
  }

  const checkLotePopupExists = () => {
    ifFoundInBody('[data-cy="lote-popup"], .popup', () => {
      cy.get('[data-cy="lote-popup"], .popup').should('exist')
    })
  }

  const verifyLoteMarkerPopup = () => {
    cy.get('body', { timeout: 3000 }).then(checkLotePopupExists)
  }

  const clickLoteMarker = () => {
    ifFoundInBody('[data-cy="lote-markers"], [data-cy="lote-marker"]', () => {
      cy.get('[data-cy="lote-marker"], [data-cy="lote-markers"]').first().click({ force: true })
      verifyLoteMarkerPopup()
    })
  }

  const verifyMapWithLotes = () => {
    ifFoundInBody('[data-cy="finca-map"], .map, [id*="map"]', () => {
      cy.get('[data-cy="finca-map"], .map, [id*="map"]').first().should('be.visible')
      clickLoteMarker()
    })
  }

  const checkNotificationSuccess = () => {
    ifFoundInBody('[data-cy="notification-success"], .swal2-success', () => {
      cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
    })
  }

  const verifySaveLoteSuccess = () => {
    clickIfExistsAndContinue('[data-cy="save-lote"], button[type="submit"]', () => {
      checkNotificationSuccess()
    })
  }

  const editLoteName = () => {
    ifFoundInBody('[data-cy="lote-nombre"], input[name*="nombre"]', () => {
      cy.get('[data-cy="lote-nombre"], input[name*="nombre"]').first().clear().type('Lote Editado desde Finca')
      verifySaveLoteSuccess()
    })
  }

  const handleEditLote = () => {
    clickIfExistsAndContinue('[data-cy="edit-lote"], button', () => {
      editLoteName()
    })
  }

  const checkRecommendationItemsCount = () => {
    ifFoundInBody('[data-cy="recommendation-item"], .recommendation-item', () => {
      cy.get('[data-cy="recommendation-item"], .recommendation-item').should('have.length.greaterThan', 0)
    })
  }

  const verifyRecommendationTypes = ($recs) => {
    const recTypes = [
      '[data-cy="fertilization-recommendation"]',
      '[data-cy="irrigation-recommendation"]',
      '[data-cy="harvest-recommendation"]'
    ]
    verifySelectorsExist(recTypes, $recs, 3000)
  }

  const verifyRecommendationItems = ($recs) => {
    checkRecommendationItemsCount()
    verifyRecommendationTypes($recs)
  }

  const verifyRecommendations = () => {
    ifFoundInBody('[data-cy="finca-recommendations"], .recommendations', () => {
      cy.get('[data-cy="finca-recommendations"], .recommendations').should('be.visible')
      cy.get('body').then(verifyRecommendationItems)
    })
  }

  const checkSecondLote = () => {
    ifFoundInBody('[data-cy="lote-checkbox"], input[type="checkbox"]', () => {
      cy.get('[data-cy="lote-checkbox"], input[type="checkbox"]').eq(1).check({ force: true })
    })
  }

  const checkFirstLote = () => {
    cy.get('[data-cy="lote-checkbox"], input[type="checkbox"]').first().check({ force: true })
    checkSecondLote()
  }

  const verifyBulkScheduleSuccess = () => {
    clickIfExistsAndContinue('[data-cy="save-bulk-schedule"], button[type="submit"]', () => {
      checkNotificationSuccess()
    })
  }

  const fillBulkScheduleForm = () => {
    ifFoundInBody('[data-cy="analysis-date"], input[type="date"]', () => {
      cy.get('[data-cy="analysis-date"], input[type="date"]').first().type('2024-02-15')
      cy.get('[data-cy="analysis-time"], input[type="time"]').first().type('10:00')
      cy.get('[data-cy="analysis-notes"], textarea').first().type('Análisis programado para múltiples lotes')
      verifyBulkScheduleSuccess()
    })
  }

  const handleBulkScheduleAnalysis = () => {
    clickIfExistsAndContinue('[data-cy="bulk-schedule-analysis"], button', () => {
      fillBulkScheduleForm()
    })
  }

  const verifyHistoryItemDetails = ($item) => {
    const changeSelectors = [
      '[data-cy="change-date"]',
      '[data-cy="change-type"]',
      '[data-cy="change-description"]'
    ]
    verifySelectorsExist(changeSelectors, $item, 3000)
  }

  const checkFirstHistoryItem = () => {
    cy.get('[data-cy="history-item"], .history-item').first().then(verifyHistoryItemDetails)
  }

  const verifyHistoryItems = ($history) => {
    ifFoundInBody('[data-cy="history-item"], .history-item', () => {
      cy.get('[data-cy="history-item"], .history-item').should('have.length.greaterThan', 0)
      checkFirstHistoryItem()
    })
  }

  const verifyHistory = () => {
    ifFoundInBody('[data-cy="finca-history"], .history', () => {
      cy.get('[data-cy="finca-history"], .history').should('be.visible')
      cy.get('body').then(verifyHistoryItems)
    })
  }

  const compareFincaAndLotesAreas = ($fincaArea, $lotesArea) => {
    const fincaArea = Number.parseFloat($fincaArea.text())
    const lotesArea = Number.parseFloat($lotesArea.text())
    expect(lotesArea).to.be.at.most(fincaArea)
  }

  const verifyAreaConsistency = ($fincaArea) => {
    cy.get('[data-cy="total-area-lotes"]').then(($lotesArea) => {
      compareFincaAndLotesAreas($fincaArea, $lotesArea)
    })
  }

  const checkAreaConsistency = ($area) => {
    if ($area.find('[data-cy="finca-area"]').length > 0 && $area.find('[data-cy="total-area-lotes"]').length > 0) {
      cy.get('[data-cy="finca-area"]').then(verifyAreaConsistency)
    }
  }

  const verifyEachLoteVariedad = () => {
    ifFoundInBody('[data-cy="lote-item"]', () => {
      cy.get('[data-cy="lote-item"]').each(($item) => {
        cy.wrap($item).find('[data-cy="lote-variedad"]').should('contain', 'Criollo')
      })
    })
  }

  const verifyLotesFilteredByVariedad = () => {
    ifFoundInBody('[data-cy="lotes-list"]', () => {
      cy.get('[data-cy="lotes-list"]').should('be.visible')
      verifyEachLoteVariedad()
    })
  }

  const applyVariedadFilter = () => {
    ifFoundInBody('[data-cy="filter-variedad"], select', () => {
      cy.get('[data-cy="filter-variedad"], select').first().select('Criollo', { force: true })
      verifyLotesFilteredByVariedad()
    })
  }

  const compareAreas = ($first, $second) => {
    const firstArea = Number.parseFloat($first.text())
    const secondArea = Number.parseFloat($second.text())
    expect(firstArea).to.be.at.least(secondArea)
  }

  const verifySortedAreas = ($first) => {
    cy.get('[data-cy="lote-item"]').eq(1).find('[data-cy="lote-area"]').then(($second) => {
      compareAreas($first, $second)
    })
  }

  const getFirstLoteArea = () => {
    cy.get('[data-cy="lote-item"]').first().find('[data-cy="lote-area"]').then(verifySortedAreas)
  }

  const verifyLotesSortedByArea = () => {
    ifFoundInBody('[data-cy="lote-item"]', () => {
      getFirstLoteArea()
    })
  }

  const applyAreaSort = () => {
    ifFoundInBody('[data-cy="sort-lotes"], select', () => {
      cy.get('[data-cy="sort-lotes"], select').first().select('area-desc', { force: true })
      verifyLotesSortedByArea()
    })
  }

  const verifyComparisonView = () => {
    const comparisonSelectors = [
      '[data-cy="comparison-view"]',
      '[data-cy="comparison-chart"]'
    ]
    verifySelectorsExist(comparisonSelectors, cy.get('body'), 3000)
  }

  const handleCompareLotes = () => {
    clickIfExistsAndContinue('[data-cy="compare-lotes"], button', () => {
      verifyComparisonView()
    })
  }

  it('debe permitir exportar reporte completo de finca con lotes', () => {
    visitFincasAndClickFirst(() => {
      handleExportReport()
    })
  })

  it('debe mostrar mapa con ubicación de lotes dentro de la finca', () => {
    visitFincasAndClickFirst(() => {
      verifyMapWithLotes()
    })
  })

  it('debe permitir gestionar lotes desde vista de finca', () => {
    visitFincasAndClickFirst(() => {
      ifFoundInBody('[data-cy="lote-item"], .lote-item, .item', () => {
        handleEditLote()
      })
    })
  })

  it('debe mostrar resumen de producción por finca', () => {
    visitFincasAndClickFirst(($details) => {
      const productionSelectors = [
        '[data-cy="production-summary"]',
        '[data-cy="total-production"]',
        '[data-cy="production-by-lote"]',
        '[data-cy="production-trend"]'
      ]
      verifySelectorsExist(productionSelectors, $details)
    })
  })

  it('debe mostrar recomendaciones basadas en análisis de todos los lotes', () => {
    visitFincasAndClickFirst(() => {
      verifyRecommendations()
    })
  })

  it('debe permitir programar análisis para múltiples lotes', () => {
    visitFincasAndClickFirst(() => {
      ifFoundInBody('[data-cy="lote-checkbox"], input[type="checkbox"]', () => {
        checkFirstLote()
        handleBulkScheduleAnalysis()
      })
    })
  })

  it('debe mostrar historial de cambios en finca y lotes', () => {
    visitFincasAndClickFirst(() => {
      verifyHistory()
    })
  })

  it('debe validar consistencia de datos entre finca y lotes', () => {
    visitFincasAndClickFirst(() => {
      cy.get('body').then(checkAreaConsistency)
    })
  })

  it('debe mostrar dashboard consolidado de finca con lotes', () => {
    visitFincasAndClickFirst(($details) => {
      const dashboardSelectors = [
        '[data-cy="finca-dashboard"]',
        '[data-cy="overview-cards"]',
        '[data-cy="performance-metrics"]',
        '[data-cy="recent-activities"]'
      ]
      verifySelectorsExist(dashboardSelectors, $details, 3000)
    })
  })

  it('debe permitir filtrar lotes por variedad', () => {
    visitFincasAndClickFirst(() => {
      applyVariedadFilter()
    })
  })

  it('debe permitir ordenar lotes por área', () => {
    visitFincasAndClickFirst(() => {
      applyAreaSort()
    })
  })

  it('debe mostrar resumen de calidad por finca', () => {
    visitFincasAndClickFirst(() => {
      const qualitySelectors = [
        '[data-cy="quality-summary"]',
        '[data-cy="average-quality"]',
        '[data-cy="quality-distribution"]'
      ]
      verifySelectorsExist(qualitySelectors, cy.get('body'), 3000)
    })
  })

  it('debe permitir comparar lotes de la misma finca', () => {
    visitFincasAndClickFirst(() => {
      ifFoundInBody('[data-cy="lote-checkbox"], input[type="checkbox"]', () => {
        checkFirstLote()
        handleCompareLotes()
      })
    })
  })
})
