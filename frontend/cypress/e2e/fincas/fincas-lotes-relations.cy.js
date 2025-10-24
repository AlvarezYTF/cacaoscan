describe('Gestión de Fincas y Lotes - Relaciones', () => {
  beforeEach(() => {
    cy.login('farmer')
  })

  it('debe mostrar lotes asociados a una finca específica', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Verificar sección de lotes
    cy.get('[data-cy="finca-lotes"]').should('be.visible')
    cy.get('[data-cy="lotes-count"]').should('be.visible')
    cy.get('[data-cy="lotes-list"]').should('be.visible')
    
    // Verificar información de cada lote
    cy.get('[data-cy="lote-item"]').each(($item) => {
      cy.wrap($item).within(() => {
        cy.get('[data-cy="lote-name"]').should('be.visible')
        cy.get('[data-cy="lote-area"]').should('be.visible')
        cy.get('[data-cy="lote-variedad"]').should('be.visible')
      })
    })
  })

  it('debe crear lote desde vista de finca', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Crear lote desde la finca
    cy.get('[data-cy="add-lote-button"]').click()
    
    // Verificar que la finca ya está seleccionada
    cy.get('[data-cy="finca-select"]').should('have.value', '1')
    
    // Llenar datos del lote
    cy.fixture('testData').then((data) => {
      const loteData = data.lotes[0]
      cy.fillLoteForm(loteData)
    })
    
    cy.get('[data-cy="save-lote"]').click()
    
    // Verificar éxito
    cy.checkNotification('Lote creado exitosamente', 'success')
    
    // Verificar que aparece en la lista de lotes de la finca
    cy.get('[data-cy="finca-lotes"]').should('contain', 'Lote A - Norte')
  })

  it('debe mostrar estadísticas agregadas de finca con sus lotes', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Verificar estadísticas agregadas
    cy.get('[data-cy="finca-stats"]').should('be.visible')
    cy.get('[data-cy="total-lotes"]').should('be.visible')
    cy.get('[data-cy="total-area-lotes"]').should('be.visible')
    cy.get('[data-cy="variedades-count"]').should('be.visible')
    cy.get('[data-cy="average-age"]').should('be.visible')
  })

  it('debe mostrar análisis agregados de todos los lotes de la finca', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Verificar análisis agregados
    cy.get('[data-cy="finca-analisis"]').should('be.visible')
    cy.get('[data-cy="total-analisis"]').should('be.visible')
    cy.get('[data-cy="average-quality"]').should('be.visible')
    cy.get('[data-cy="last-analysis"]').should('be.visible')
  })

  it('debe mostrar gráficos comparativos entre lotes de la finca', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Verificar gráficos comparativos
    cy.get('[data-cy="lotes-comparison-chart"]').should('be.visible')
    cy.get('[data-cy="quality-comparison"]').should('be.visible')
    cy.get('[data-cy="area-distribution"]').should('be.visible')
  })

  it('debe permitir navegar entre finca y sus lotes', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Navegar a un lote específico
    cy.get('[data-cy="lote-item"]').first().click()
    
    // Verificar que estamos en detalles del lote
    cy.get('[data-cy="lote-details"]').should('be.visible')
    
    // Volver a la finca
    cy.get('[data-cy="back-to-finca"]').click()
    
    // Verificar que estamos de vuelta en la finca
    cy.get('[data-cy="finca-details"]').should('be.visible')
  })

  it('debe mostrar alertas de finca basadas en análisis de lotes', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Verificar alertas
    cy.get('[data-cy="finca-alerts"]').should('be.visible')
    cy.get('[data-cy="alert-item"]').should('be.visible')
    
    // Verificar tipos de alertas
    cy.get('[data-cy="quality-alert"]').should('be.visible')
    cy.get('[data-cy="maintenance-alert"]').should('be.visible')
    cy.get('[data-cy="harvest-alert"]').should('be.visible')
  })

  it('debe permitir exportar reporte completo de finca con lotes', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Exportar reporte completo
    cy.get('[data-cy="export-finca-report"]').click()
    
    // Verificar opciones de exportación
    cy.get('[data-cy="export-pdf"]').should('be.visible')
    cy.get('[data-cy="export-excel"]').should('be.visible')
    
    // Exportar como PDF
    cy.get('[data-cy="export-pdf"]').click()
    cy.verifyDownload('reporte-finca-completo.pdf')
  })

  it('debe mostrar mapa con ubicación de lotes dentro de la finca', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Verificar mapa con lotes
    cy.get('[data-cy="finca-map"]').should('be.visible')
    cy.get('[data-cy="lote-markers"]').should('be.visible')
    
    // Hacer clic en marcador de lote
    cy.get('[data-cy="lote-marker"]').first().click()
    
    // Verificar popup con información del lote
    cy.get('[data-cy="lote-popup"]').should('be.visible')
    cy.get('[data-cy="popup-lote-name"]').should('be.visible')
  })

  it('debe permitir gestionar lotes desde vista de finca', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Editar lote desde vista de finca
    cy.get('[data-cy="lote-item"]').first().within(() => {
      cy.get('[data-cy="edit-lote"]').click()
    })
    
    // Modificar datos
    cy.get('[data-cy="lote-nombre"]').clear().type('Lote Editado desde Finca')
    cy.get('[data-cy="save-lote"]').click()
    
    // Verificar éxito
    cy.checkNotification('Lote actualizado exitosamente', 'success')
    
    // Verificar que se actualizó en la vista de finca
    cy.get('[data-cy="finca-lotes"]').should('contain', 'Lote Editado desde Finca')
  })

  it('debe mostrar resumen de producción por finca', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Verificar resumen de producción
    cy.get('[data-cy="production-summary"]').should('be.visible')
    cy.get('[data-cy="total-production"]').should('be.visible')
    cy.get('[data-cy="production-by-lote"]').should('be.visible')
    cy.get('[data-cy="production-trend"]').should('be.visible')
  })

  it('debe mostrar recomendaciones basadas en análisis de todos los lotes', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Verificar recomendaciones agregadas
    cy.get('[data-cy="finca-recommendations"]').should('be.visible')
    cy.get('[data-cy="recommendation-item"]').should('have.length.greaterThan', 0)
    
    // Verificar tipos de recomendaciones
    cy.get('[data-cy="fertilization-recommendation"]').should('be.visible')
    cy.get('[data-cy="irrigation-recommendation"]').should('be.visible')
    cy.get('[data-cy="harvest-recommendation"]').should('be.visible')
  })

  it('debe permitir programar análisis para múltiples lotes', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Seleccionar múltiples lotes
    cy.get('[data-cy="lote-checkbox"]').first().check()
    cy.get('[data-cy="lote-checkbox"]').eq(1).check()
    
    // Programar análisis en lote
    cy.get('[data-cy="bulk-schedule-analysis"]').click()
    
    // Configurar análisis
    cy.get('[data-cy="analysis-date"]').type('2024-02-15')
    cy.get('[data-cy="analysis-time"]').type('10:00')
    cy.get('[data-cy="analysis-notes"]').type('Análisis programado para múltiples lotes')
    
    cy.get('[data-cy="save-bulk-schedule"]').click()
    
    // Verificar éxito
    cy.checkNotification('Análisis programados exitosamente', 'success')
  })

  it('debe mostrar historial de cambios en finca y lotes', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Verificar historial
    cy.get('[data-cy="finca-history"]').should('be.visible')
    cy.get('[data-cy="history-item"]').should('have.length.greaterThan', 0)
    
    // Verificar información de cada cambio
    cy.get('[data-cy="history-item"]').first().within(() => {
      cy.get('[data-cy="change-date"]').should('be.visible')
      cy.get('[data-cy="change-type"]').should('be.visible')
      cy.get('[data-cy="change-description"]').should('be.visible')
    })
  })

  it('debe validar consistencia de datos entre finca y lotes', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Verificar que el área total de lotes no excede el área de la finca
    cy.get('[data-cy="finca-area"]').then(($fincaArea) => {
      const fincaArea = parseFloat($fincaArea.text())
      
      cy.get('[data-cy="total-area-lotes"]').then(($lotesArea) => {
        const lotesArea = parseFloat($lotesArea.text())
        
        expect(lotesArea).to.be.at.most(fincaArea)
      })
    })
  })

  it('debe mostrar dashboard consolidado de finca con lotes', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Verificar dashboard consolidado
    cy.get('[data-cy="finca-dashboard"]').should('be.visible')
    cy.get('[data-cy="overview-cards"]').should('be.visible')
    cy.get('[data-cy="performance-metrics"]').should('be.visible')
    cy.get('[data-cy="recent-activities"]').should('be.visible')
  })
})
