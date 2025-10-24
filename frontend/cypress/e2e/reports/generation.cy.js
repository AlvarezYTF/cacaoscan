describe('Generación de Reportes - Creación', () => {
  beforeEach(() => {
    cy.login('analyst')
    cy.visit('/reportes')
  })

  it('debe mostrar interfaz de generación de reportes', () => {
    cy.get('[data-cy="reports-interface"]').should('be.visible')
    cy.get('[data-cy="create-report-button"]').should('be.visible')
    cy.get('[data-cy="reports-list"]').should('be.visible')
    cy.get('[data-cy="report-filters"]').should('be.visible')
  })

  it('debe crear reporte de análisis por período', () => {
    cy.get('[data-cy="create-report-button"]').click()
    
    // Seleccionar tipo de reporte
    cy.get('[data-cy="report-type"]').select('analisis-periodo')
    
    // Configurar período
    cy.get('[data-cy="start-date"]').type('2024-01-01')
    cy.get('[data-cy="end-date"]').type('2024-01-31')
    
    // Seleccionar fincas
    cy.get('[data-cy="fincas-select"]').check()
    
    // Configurar opciones
    cy.get('[data-cy="include-charts"]').check()
    cy.get('[data-cy="include-recommendations"]').check()
    
    // Generar reporte
    cy.get('[data-cy="generate-report"]').click()
    
    // Verificar progreso
    cy.get('[data-cy="report-progress"]').should('be.visible')
    
    // Esperar completación
    cy.get('[data-cy="report-completed"]', { timeout: 30000 }).should('be.visible')
    
    // Verificar éxito
    cy.checkNotification('Reporte generado exitosamente', 'success')
  })

  it('debe crear reporte de calidad por finca', () => {
    cy.get('[data-cy="create-report-button"]').click()
    
    // Seleccionar tipo de reporte
    cy.get('[data-cy="report-type"]').select('calidad-finca')
    
    // Seleccionar finca específica
    cy.get('[data-cy="finca-select"]').select('Finca El Paraíso')
    
    // Configurar opciones
    cy.get('[data-cy="include-trends"]').check()
    cy.get('[data-cy="include-comparisons"]').check()
    
    // Generar reporte
    cy.get('[data-cy="generate-report"]').click()
    
    // Esperar completación
    cy.get('[data-cy="report-completed"]', { timeout: 30000 }).should('be.visible')
    
    cy.checkNotification('Reporte generado exitosamente', 'success')
  })

  it('debe crear reporte comparativo entre lotes', () => {
    cy.get('[data-cy="create-report-button"]').click()
    
    // Seleccionar tipo de reporte
    cy.get('[data-cy="report-type"]').select('comparativo-lotes')
    
    // Seleccionar lotes
    cy.get('[data-cy="lotes-select"]').check()
    
    // Configurar comparación
    cy.get('[data-cy="compare-quality"]').check()
    cy.get('[data-cy="compare-production"]').check()
    cy.get('[data-cy="compare-trends"]').check()
    
    // Generar reporte
    cy.get('[data-cy="generate-report"]').click()
    
    // Esperar completación
    cy.get('[data-cy="report-completed"]', { timeout: 30000 }).should('be.visible')
    
    cy.checkNotification('Reporte generado exitosamente', 'success')
  })

  it('debe crear reporte de recomendaciones', () => {
    cy.get('[data-cy="create-report-button"]').click()
    
    // Seleccionar tipo de reporte
    cy.get('[data-cy="report-type"]').select('recomendaciones')
    
    // Configurar alcance
    cy.get('[data-cy="scope-all-fincas"]').check()
    
    // Seleccionar tipos de recomendaciones
    cy.get('[data-cy="fertilization-rec"]').check()
    cy.get('[data-cy="irrigation-rec"]').check()
    cy.get('[data-cy="harvest-rec"]').check()
    
    // Generar reporte
    cy.get('[data-cy="generate-report"]').click()
    
    // Esperar completación
    cy.get('[data-cy="report-completed"]', { timeout: 30000 }).should('be.visible')
    
    cy.checkNotification('Reporte generado exitosamente', 'success')
  })

  it('debe validar campos requeridos para generar reporte', () => {
    cy.get('[data-cy="create-report-button"]').click()
    cy.get('[data-cy="generate-report"]').click()
    
    // Verificar errores de validación
    cy.get('[data-cy="report-type-error"]').should('be.visible')
    cy.get('[data-cy="date-range-error"]').should('be.visible')
  })

  it('debe validar rango de fechas', () => {
    cy.get('[data-cy="create-report-button"]').click()
    
    // Fecha de inicio mayor que fecha de fin
    cy.get('[data-cy="start-date"]').type('2024-01-31')
    cy.get('[data-cy="end-date"]').type('2024-01-01')
    cy.get('[data-cy="generate-report"]').click()
    
    cy.get('[data-cy="date-range-error"]')
      .should('be.visible')
      .and('contain', 'La fecha de inicio debe ser anterior a la fecha de fin')
  })

  it('debe permitir cancelar generación de reporte', () => {
    cy.get('[data-cy="create-report-button"]').click()
    
    cy.get('[data-cy="report-type"]').select('analisis-periodo')
    cy.get('[data-cy="start-date"]').type('2024-01-01')
    cy.get('[data-cy="end-date"]').type('2024-01-31')
    cy.get('[data-cy="generate-report"]').click()
    
    // Cancelar generación
    cy.get('[data-cy="cancel-generation"]').click()
    
    // Confirmar cancelación
    cy.get('[data-cy="confirm-cancel"]').click()
    
    // Verificar que se canceló
    cy.get('[data-cy="generation-cancelled"]')
      .should('be.visible')
      .and('contain', 'Generación cancelada')
  })

  it('debe mostrar progreso detallado de generación', () => {
    cy.get('[data-cy="create-report-button"]').click()
    
    cy.get('[data-cy="report-type"]').select('analisis-periodo')
    cy.get('[data-cy="start-date"]').type('2024-01-01')
    cy.get('[data-cy="end-date"]').type('2024-01-31')
    cy.get('[data-cy="generate-report"]').click()
    
    // Verificar etapas del progreso
    cy.get('[data-cy="progress-stage"]').should('contain', 'Recopilando datos')
    cy.get('[data-cy="progress-stage"]').should('contain', 'Procesando análisis')
    cy.get('[data-cy="progress-stage"]').should('contain', 'Generando gráficos')
    cy.get('[data-cy="progress-stage"]').should('contain', 'Finalizando reporte')
  })

  it('debe manejar errores durante la generación', () => {
    // Simular error del servidor
    cy.intercept('POST', '/api/reportes/', {
      statusCode: 500,
      body: { error: 'Error del servidor' }
    }).as('reportError')
    
    cy.get('[data-cy="create-report-button"]').click()
    
    cy.get('[data-cy="report-type"]').select('analisis-periodo')
    cy.get('[data-cy="start-date"]').type('2024-01-01')
    cy.get('[data-cy="end-date"]').type('2024-01-31')
    cy.get('[data-cy="generate-report"]').click()
    
    cy.wait('@reportError')
    
    // Verificar mensaje de error
    cy.get('[data-cy="generation-error"]')
      .should('be.visible')
      .and('contain', 'Error al generar reporte')
  })

  it('debe permitir programar generación de reportes', () => {
    cy.get('[data-cy="create-report-button"]').click()
    
    // Configurar reporte programado
    cy.get('[data-cy="report-type"]').select('analisis-periodo')
    cy.get('[data-cy="schedule-report"]').check()
    
    // Configurar programación
    cy.get('[data-cy="schedule-frequency"]').select('mensual')
    cy.get('[data-cy="schedule-day"]').type('1')
    cy.get('[data-cy="schedule-time"]').type('09:00')
    
    // Guardar programación
    cy.get('[data-cy="save-schedule"]').click()
    
    // Verificar éxito
    cy.checkNotification('Reporte programado exitosamente', 'success')
  })

  it('debe permitir personalizar formato de reporte', () => {
    cy.get('[data-cy="create-report-button"]').click()
    
    // Configurar formato
    cy.get('[data-cy="report-format"]').select('pdf')
    cy.get('[data-cy="include-cover"]').check()
    cy.get('[data-cy="include-summary"]').check()
    cy.get('[data-cy="include-appendix"]').check()
    
    // Configurar estilo
    cy.get('[data-cy="color-scheme"]').select('corporate')
    cy.get('[data-cy="font-size"]').select('medium')
    
    // Verificar preview
    cy.get('[data-cy="format-preview"]').should('be.visible')
  })
})
