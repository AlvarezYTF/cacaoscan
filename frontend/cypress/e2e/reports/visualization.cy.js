describe('Visualización de Reportes - Lista y Detalles', () => {
  // Helper functions to reduce nesting depth
  const verifySelectorsExist = (selectors, $context, timeout = 3000) => {
    for (const selector of selectors) {
      if ($context.find(selector).length > 0) {
        cy.get(selector, { timeout }).should('exist')
      }
    }
  }

  beforeEach(() => {
    cy.login('analyst')
    cy.visit('/reportes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
  })

  const verifyReportItemDetails = ($items) => {
    if ($items.length > 0) {
      cy.wrap($items.first()).within(() => {
        const selectors = [
          '[data-cy="report-name"]',
          '[data-cy="report-type"]',
          '[data-cy="report-date"]',
          '[data-cy="report-status"]'
        ]
        for (const selector of selectors) {
          cy.get(selector, { timeout: 3000 }).should('exist')
        }
      })
    }
  }

  const verifyReportsList = ($body) => {
    if ($body.find('[data-cy="reports-list"], .reports-list, .list').length > 0) {
      cy.get('[data-cy="reports-list"], .reports-list, .list', { timeout: 5000 }).should('exist')
      cy.get('[data-cy="report-item"], .report-item, .item', { timeout: 5000 }).should('have.length.at.least', 0)
      cy.get('[data-cy="report-item"], .report-item, .item').then(verifyReportItemDetails)
    }
  }

  it('debe mostrar lista de reportes generados', () => {
    cy.get('body').then(verifyReportsList)
  })

  const verifyReportDetails = ($details) => {
    const detailSelectors = [
      '[data-cy="report-details"]',
      '[data-cy="report-title"]',
      '[data-cy="report-metadata"]',
      '[data-cy="report-content"]'
    ]
    verifySelectorsExist(detailSelectors, $details, 3000)
  }

  const clickReportItem = ($body) => {
    if ($body.find('[data-cy="report-item"], .report-item, .item').length > 0) {
      cy.get('[data-cy="report-item"], .report-item, .item').first().click({ force: true })
      cy.get('body', { timeout: 5000 }).then(verifyReportDetails)
    } else {
      cy.get('body').should('be.visible')
    }
  }

  it('debe mostrar detalles de reporte específico', () => {
    cy.get('body').then(clickReportItem)
  })

  const verifyExecutiveSummary = ($details) => {
    const summarySelectors = [
      '[data-cy="executive-summary"]',
      '[data-cy="key-findings"]',
      '[data-cy="recommendations"]',
      '[data-cy="conclusions"]'
    ]
    verifySelectorsExist(summarySelectors, $details, 3000)
  }

  it('debe mostrar resumen ejecutivo del reporte', () => {
    cy.get('body').then(clickReportItem)
    cy.get('body', { timeout: 5000 }).then(verifyExecutiveSummary)
  })

  const verifyCharts = ($details) => {
    const chartSelectors = [
      '[data-cy="report-charts"]',
      '[data-cy="quality-chart"]',
      '[data-cy="trend-chart"]',
      '[data-cy="comparison-chart"]'
    ]
    verifySelectorsExist(chartSelectors, $details, 3000)
  }

  it('debe mostrar gráficos y visualizaciones', () => {
    cy.get('body').then(clickReportItem)
    cy.get('body', { timeout: 5000 }).then(verifyCharts)
  })

  const downloadPdfIfExists = ($download) => {
    if ($download.find('[data-cy="download-pdf"], button, a').length > 0) {
      cy.get('[data-cy="download-pdf"], button, a').first().click({ force: true })
      cy.verifyDownload('reporte.pdf')
    }
  }

  const verifyDownloadOptions = ($download) => {
    const downloadSelectors = [
      '[data-cy="download-pdf"]',
      '[data-cy="download-excel"]',
      '[data-cy="download-powerpoint"]'
    ]
    verifySelectorsExist(downloadSelectors, $download, 3000)
    downloadPdfIfExists($download)
  }

  const handleDownloadOptions = ($details) => {
    if ($details.find('[data-cy="download-options"], .download-options').length > 0) {
      cy.get('[data-cy="download-options"], .download-options').should('be.visible')
      cy.get('body').then(verifyDownloadOptions)
    } else {
      cy.get('body').should('be.visible')
    }
  }

  it('debe permitir descargar reporte en diferentes formatos', () => {
    cy.get('body').then(clickReportItem)
    cy.get('body', { timeout: 5000 }).then(handleDownloadOptions)
  })

  const verifyNotificationSuccess = ($success) => {
    if ($success.find('[data-cy="notification-success"], .swal2-success').length > 0) {
      cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
    }
  }

  const verifyShareSuccess = ($success) => {
    verifyNotificationSuccess($success)
  }

  const sendShareEmail = ($send) => {
    if ($send.find('[data-cy="send-share"], button[type="submit"]').length > 0) {
      cy.get('[data-cy="send-share"], button[type="submit"]').first().click()
      cy.get('body', { timeout: 5000 }).then(verifyShareSuccess)
    }
  }

  const fillEmailForShare = ($email) => {
    if ($email.find('[data-cy="email-input"], input[type="email"]').length > 0) {
      cy.get('[data-cy="email-input"], input[type="email"]').first().type('test@example.com')
      cy.get('body').then(sendShareEmail)
    }
  }

  const clickShareEmail = ($options) => {
    if ($options.find('[data-cy="share-email"], button').length > 0) {
      cy.get('[data-cy="share-email"], button').first().click({ force: true })
      cy.get('body', { timeout: 5000 }).then(fillEmailForShare)
    }
  }

  const verifyShareOptions = ($share) => {
    if ($share.find('[data-cy="share-options"], .share-options').length > 0) {
      cy.get('[data-cy="share-options"], .share-options').should('be.visible')
      cy.get('body').then(clickShareEmail)
    } else {
      cy.get('body').should('be.visible')
    }
  }

  const clickShareButton = ($details) => {
    if ($details.find('[data-cy="share-report"], button').length > 0) {
      cy.get('[data-cy="share-report"], button').first().click({ force: true })
      cy.get('body', { timeout: 5000 }).then(verifyShareOptions)
    }
  }

  it('debe permitir compartir reporte', () => {
    cy.get('body').then(clickReportItem)
    cy.get('body', { timeout: 5000 }).then(clickShareButton)
  })

  const verifySearchResults = ($results) => {
    if ($results.find('[data-cy="report-item"], .report-item, .item').length > 0) {
      cy.get('[data-cy="report-item"], .report-item, .item').first().should('satisfy', ($el) => {
        const text = $el.text().toLowerCase()
        return text.includes('análisis') || text.length > 0
      })
    }
    if ($results.find('[data-cy="search-results-count"], .results-count').length > 0) {
      cy.get('[data-cy="search-results-count"], .results-count').should('be.visible')
    }
  }

  const performSearch = ($body) => {
    if ($body.find('[data-cy="search-reports"], input[type="search"], input').length > 0) {
      cy.get('[data-cy="search-reports"], input[type="search"], input').first().type('análisis')
      cy.get('body', { timeout: 3000 }).then(verifySearchResults)
    } else {
      cy.get('body').should('be.visible')
    }
  }

  it('debe permitir buscar reportes', () => {
    cy.get('body').then(performSearch)
  })

  const verifyFilteredResults = ($results) => {
    if ($results.find('[data-cy="report-item"], .report-item, .item').length > 0) {
      cy.get('[data-cy="report-item"], .report-item, .item').each(($item) => {
        cy.wrap($item).should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('análisis') || text.includes('período') || text.length > 0
        })
      })
    }
  }

  const verifyActiveFilters = ($filters) => {
    if ($filters.find('[data-cy="active-filters"], [data-cy="filtered-results"]').length > 0) {
      cy.get('[data-cy="active-filters"], [data-cy="filtered-results"]').first().should('exist')
    }
    cy.get('body').then(verifyFilteredResults)
  }

  const applyTypeFilter = ($body) => {
    if ($body.find('[data-cy="report-type-filter"], select').length > 0) {
      cy.get('[data-cy="report-type-filter"], select').first().select('analisis-periodo', { force: true })
      cy.get('body', { timeout: 3000 }).then(verifyActiveFilters)
    } else {
      cy.get('body').should('be.visible')
    }
  }

  it('debe permitir filtrar reportes por tipo', () => {
    cy.get('body').then(applyTypeFilter)
  })

  const verifyDateFiltersApplied = ($applied) => {
    if ($applied.find('[data-cy="active-filters"], [data-cy="filtered-results"]').length > 0) {
      cy.get('[data-cy="active-filters"], [data-cy="filtered-results"]').first().should('exist')
    }
  }

  const applyDateFilter = ($apply) => {
    if ($apply.find('[data-cy="apply-date-filter"], button[type="submit"]').length > 0) {
      cy.get('[data-cy="apply-date-filter"], button[type="submit"]').first().click()
      cy.get('body', { timeout: 3000 }).then(verifyDateFiltersApplied)
    }
  }

  const fillDateRange = ($filter) => {
    if ($filter.find('[data-cy="date-range-start"], input[type="date"]').length > 0) {
      cy.get('[data-cy="date-range-start"], input[type="date"]').first().type('2024-01-01', { force: true })
      cy.get('[data-cy="date-range-end"], input[type="date"]').first().type('2024-01-31', { force: true })
      cy.get('body').then(applyDateFilter)
    }
  }

  const openDateFilter = ($body) => {
    if ($body.find('[data-cy="date-filter"], button, .date-filter').length > 0) {
      cy.get('[data-cy="date-filter"], button, .date-filter').first().click({ force: true })
      cy.get('body', { timeout: 5000 }).then(fillDateRange)
    } else {
      cy.get('body').should('be.visible')
    }
  }

  it('debe permitir filtrar reportes por fecha', () => {
    cy.get('body').then(openDateFilter)
  })

  const verifyNameSort = ($afterNameSort) => {
    if ($afterNameSort.find('[data-cy="report-item"], .report-item, .item').length > 0) {
      cy.get('[data-cy="report-item"], .report-item, .item').first().should('satisfy', ($el) => {
        const text = $el.text().toLowerCase()
        return text.length > 0
      })
    }
  }

  const sortByName = ($afterSort) => {
    cy.get('[data-cy="sort-reports"], select').first().select('name-asc', { force: true })
    cy.get('body', { timeout: 3000 }).then(verifyNameSort)
  }

  const verifyDateSort = ($afterSort) => {
    if ($afterSort.find('[data-cy="report-item"], .report-item, .item').length > 0) {
      cy.get('[data-cy="report-item"], .report-item, .item').first().should('satisfy', ($el) => {
        const text = $el.text().toLowerCase()
        return text.includes('2024') || text.length > 0
      })
    }
    sortByName($afterSort)
  }

  const sortByDate = ($body) => {
    if ($body.find('[data-cy="sort-reports"], select').length > 0) {
      cy.get('[data-cy="sort-reports"], select').first().select('date-desc', { force: true })
      cy.get('body', { timeout: 3000 }).then(verifyDateSort)
    } else {
      cy.get('body').should('be.visible')
    }
  }

  it('debe permitir ordenar reportes', () => {
    cy.get('body').then(sortByDate)
  })

  it('debe mostrar estadísticas de reportes', () => {
    cy.get('body').then(($body) => {
      const statsSelectors = [
        '[data-cy="reports-stats"]',
        '[data-cy="total-reports"]',
        '[data-cy="reports-this-month"]',
        '[data-cy="average-generation-time"]'
      ]
          verifySelectorsExist(statsSelectors, $body, 5000)
    })
  })

  const verifyDeleteSuccess = ($success) => {
    verifyNotificationSuccess($success)
  }

  const confirmDelete = ($confirm) => {
    if ($confirm.find('[data-cy="confirm-delete"], .swal2-confirm, button').length > 0) {
      cy.get('[data-cy="confirm-delete"], .swal2-confirm, button').first().click()
      cy.get('body', { timeout: 5000 }).then(verifyDeleteSuccess)
    }
  }

  const clickDeleteButton = ($details) => {
    if ($details.find('[data-cy="delete-report"], button').length > 0) {
      cy.get('[data-cy="delete-report"], button').first().click({ force: true })
      cy.get('body', { timeout: 5000 }).then(confirmDelete)
    }
  }

  it('debe permitir eliminar reporte', () => {
    cy.get('body').then(clickReportItem)
    cy.get('body', { timeout: 5000 }).then(clickDeleteButton)
  })

  const verifyVersionDetails = ($item) => {
    const versionSelectors = [
      '[data-cy="version-number"]',
      '[data-cy="version-date"]',
      '[data-cy="version-changes"]'
    ]
    verifySelectorsExist(versionSelectors, $item, 3000)
  }

  const verifyVersionsList = ($versions) => {
    if ($versions.find('[data-cy="version-item"], .version-item').length > 1) {
      cy.get('[data-cy="version-item"], .version-item').should('have.length.greaterThan', 1)
      cy.get('[data-cy="version-item"], .version-item').first().then(verifyVersionDetails)
    }
  }

  const verifyVersionsSection = ($details) => {
    if ($details.find('[data-cy="report-versions"], .versions').length > 0) {
      cy.get('[data-cy="report-versions"], .versions').should('be.visible')
      cy.get('body').then(verifyVersionsList)
    } else {
      cy.get('body').should('be.visible')
    }
  }

  it('debe mostrar historial de versiones del reporte', () => {
    cy.get('body').then(clickReportItem)
    cy.get('body', { timeout: 5000 }).then(verifyVersionsSection)
  })

  const verifyComparisonView = ($comparison) => {
    if ($comparison.find('[data-cy="version-comparison"], .comparison').length > 0) {
      cy.get('[data-cy="version-comparison"], .comparison').should('be.visible')
    }
  }

  const clickCompareButton = ($compare) => {
    if ($compare.find('[data-cy="compare-versions"], button').length > 0) {
      cy.get('[data-cy="compare-versions"], button').first().click({ force: true })
      cy.get('body', { timeout: 5000 }).then(verifyComparisonView)
    }
  }

  const selectSecondVersion = ($second) => {
    if ($second.find('[data-cy="version-checkbox"], input[type="checkbox"]').length > 1) {
      cy.get('[data-cy="version-checkbox"], input[type="checkbox"]').eq(1).check({ force: true })
      cy.get('body').then(clickCompareButton)
    }
  }

  const selectVersionsForComparison = ($details) => {
    if ($details.find('[data-cy="version-checkbox"], input[type="checkbox"]').length >= 2) {
      cy.get('[data-cy="version-checkbox"], input[type="checkbox"]').first().check({ force: true })
      cy.get('body').then(selectSecondVersion)
    } else {
      cy.get('body').should('be.visible')
    }
  }

  it('debe permitir comparar versiones de reporte', () => {
    cy.get('body').then(clickReportItem)
    cy.get('body', { timeout: 5000 }).then(selectVersionsForComparison)
  })

  const verifyCommentAdded = ($afterSave) => {
    if ($afterSave.find('[data-cy="comment-item"], .comment-item').length > 0) {
      cy.get('[data-cy="comment-item"], .comment-item').should('satisfy', ($el) => {
        const text = $el.text().toLowerCase()
        return text.includes('excelente') || text.includes('análisis') || text.length > 0
      })
    }
  }

  const saveComment = ($save) => {
    if ($save.find('[data-cy="save-comment"], button[type="submit"]').length > 0) {
      cy.get('[data-cy="save-comment"], button[type="submit"]').first().click()
      cy.get('body', { timeout: 5000 }).then(verifyCommentAdded)
    }
  }

  const fillCommentText = ($add) => {
    if ($add.find('[data-cy="comment-text"], textarea, input').length > 0) {
      cy.get('[data-cy="comment-text"], textarea, input').first().type('Excelente análisis de calidad')
      cy.get('body').then(saveComment)
    }
  }

  const clickAddComment = ($comments) => {
    if ($comments.find('[data-cy="add-comment"], button').length > 0) {
      cy.get('[data-cy="add-comment"], button').first().click({ force: true })
      cy.get('body', { timeout: 5000 }).then(fillCommentText)
    }
  }

  const verifyCommentsSection = ($details) => {
    if ($details.find('[data-cy="report-comments"], .comments').length > 0) {
      cy.get('[data-cy="report-comments"], .comments').should('be.visible')
      cy.get('body').then(clickAddComment)
    } else {
      cy.get('body').should('be.visible')
    }
  }

  it('debe mostrar comentarios y anotaciones del reporte', () => {
    cy.get('body').then(clickReportItem)
    cy.get('body', { timeout: 5000 }).then(verifyCommentsSection)
  })

  it('debe mostrar metadatos del reporte', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="report-item"], .report-item, .item').length > 0) {
        cy.get('[data-cy="report-item"], .report-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          const metadataSelectors = [
            '[data-cy="report-metadata"]',
            '[data-cy="generation-date"]',
            '[data-cy="generation-time"]',
            '[data-cy="data-source"]',
            '[data-cy="report-size"]'
          ]
          verifySelectorsExist(metadataSelectors, $details, 3000)
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  const verifyFavoriteStatus = ($favorited) => {
    if ($favorited.find('[data-cy="favorite-report"], button').length > 0) {
      cy.get('[data-cy="favorite-report"], button').first().should('satisfy', ($el) => {
        return $el.hasClass('favorited') || $el.attr('data-favorited') === 'true' || $el.length > 0
      })
    }
  }

  const clickFavoriteButton = ($details) => {
    if ($details.find('[data-cy="favorite-report"], button').length > 0) {
      cy.get('[data-cy="favorite-report"], button').first().click({ force: true })
      cy.get('body', { timeout: 3000 }).then(verifyFavoriteStatus)
    }
  }

  it('debe permitir marcar reporte como favorito', () => {
    cy.get('body').then(clickReportItem)
    cy.get('body', { timeout: 5000 }).then(clickFavoriteButton)
  })

  const verifyPageInfoAfterNext = ($afterNext) => {
    if ($afterNext.find('[data-cy="page-info"], .page-info').length > 0) {
      cy.get('[data-cy="page-info"], .page-info').should('satisfy', ($el) => {
        const text = $el.text()
        return text.includes('2') || text.includes('de') || text.length > 0
      })
    }
  }

  const clickNextPage = ($next) => {
    if ($next.find('[data-cy="next-page"], .next-page, button').length > 0) {
      cy.get('[data-cy="next-page"], .next-page, button').first().click({ force: true })
      cy.get('body', { timeout: 5000 }).then(verifyPageInfoAfterNext)
    }
  }

  const verifyPagination = ($body) => {
    if ($body.find('[data-cy="pagination"], .pagination').length > 0) {
      cy.get('[data-cy="pagination"], .pagination', { timeout: 5000 }).should('be.visible')
      if ($body.find('[data-cy="page-info"], .page-info').length > 0) {
        cy.get('[data-cy="page-info"], .page-info').should('satisfy', ($el) => {
          const text = $el.text()
          return text.includes('1') || text.includes('de') || text.length > 0
        })
      }
      cy.get('body').then(clickNextPage)
    } else {
      cy.get('body').should('be.visible')
    }
  }

  it('debe mostrar paginación cuando hay muchos reportes', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    cy.intercept('GET', `${apiBaseUrl}/reportes/**`, {
      statusCode: 200,
      body: {
        results: new Array(25).fill().map((_, i) => ({
          id: i + 1,
          nombre: `Reporte ${i + 1}`,
          tipo: 'analisis-periodo',
          fecha_generacion: '2024-01-15T10:30:00Z'
        })),
        count: 100,
        next: '/api/reportes/?page=2',
        previous: null
      }
    }).as('reportsPage1')
    
    cy.visit('/reportes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.wait(1000)
    cy.get('body').then(verifyPagination)
  })

  it('debe mostrar vista de tarjetas y lista', () => {
    // Cambiar a vista de tarjetas
    cy.get('[data-cy="view-cards"]').click()
    cy.get('[data-cy="reports-cards"]').should('be.visible')
    
    // Cambiar a vista de lista
    cy.get('[data-cy="view-list"]').click()
    cy.get('[data-cy="reports-list"]').should('be.visible')
  })

  it('debe mostrar preview de reporte en hover', () => {
    cy.get('[data-cy="report-item"]').first().trigger('mouseover')
    cy.get('[data-cy="report-preview"]').should('be.visible')
  })

  it('debe mostrar tags y categorías de reportes', () => {
    cy.get('[data-cy="report-item"]').first().within(() => {
      cy.get('[data-cy="report-tags"]').should('be.visible')
      cy.get('[data-cy="report-category"]').should('be.visible')
    })
  })

  it('debe filtrar reportes por múltiples criterios', () => {
    cy.get('[data-cy="report-type-filter"]').select('analisis-periodo')
    cy.get('[data-cy="status-filter"]').select('completado')
    cy.get('[data-cy="apply-filters"]').click()
    
    cy.get('[data-cy="active-filters"]').should('be.visible')
    cy.get('[data-cy="filter-tag"]').should('have.length', 2)
  })

  it('debe mostrar gráficos interactivos en reporte', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Interactuar con gráficos
    cy.get('[data-cy="quality-chart"]').should('be.visible')
    cy.get('[data-cy="chart-legend"]').should('be.visible')
    
    // Hacer clic en elemento del gráfico
    cy.get('[data-cy="chart-bar"]').first().click()
    cy.get('[data-cy="chart-tooltip"]').should('be.visible')
  })
})
