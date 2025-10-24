describe('Reportes - Exportación y Compartir', () => {
  beforeEach(() => {
    cy.login('analyst')
    cy.visit('/reportes')
  })

  it('debe exportar reporte como PDF', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Exportar como PDF
    cy.get('[data-cy="download-pdf"]').click()
    
    // Verificar opciones de PDF
    cy.get('[data-cy="pdf-options"]').should('be.visible')
    cy.get('[data-cy="include-charts"]').should('be.checked')
    cy.get('[data-cy="include-tables"]').should('be.checked')
    
    // Configurar PDF
    cy.get('[data-cy="pdf-quality"]').select('high')
    cy.get('[data-cy="pdf-orientation"]').select('portrait')
    
    // Confirmar descarga
    cy.get('[data-cy="confirm-download"]').click()
    
    // Verificar descarga
    cy.verifyDownload('reporte.pdf')
  })

  it('debe exportar reporte como Excel', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Exportar como Excel
    cy.get('[data-cy="download-excel"]').click()
    
    // Verificar opciones de Excel
    cy.get('[data-cy="excel-options"]').should('be.visible')
    cy.get('[data-cy="include-raw-data"]').check()
    cy.get('[data-cy="include-calculations"]').check()
    
    // Configurar Excel
    cy.get('[data-cy="excel-format"]').select('xlsx')
    cy.get('[data-cy="include-macros"]').check()
    
    // Confirmar descarga
    cy.get('[data-cy="confirm-download"]').click()
    
    // Verificar descarga
    cy.verifyDownload('reporte.xlsx')
  })

  it('debe exportar reporte como PowerPoint', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Exportar como PowerPoint
    cy.get('[data-cy="download-powerpoint"]').click()
    
    // Verificar opciones de PowerPoint
    cy.get('[data-cy="powerpoint-options"]').should('be.visible')
    cy.get('[data-cy="include-slides"]').should('be.checked')
    cy.get('[data-cy="include-speaker-notes"]').check()
    
    // Configurar PowerPoint
    cy.get('[data-cy="slide-template"]').select('corporate')
    cy.get('[data-cy="include-animations"]').check()
    
    // Confirmar descarga
    cy.get('[data-cy="confirm-download"]').click()
    
    // Verificar descarga
    cy.verifyDownload('reporte.pptx')
  })

  it('debe exportar múltiples reportes en lote', () => {
    // Seleccionar múltiples reportes
    cy.get('[data-cy="report-checkbox"]').first().check()
    cy.get('[data-cy="report-checkbox"]').eq(1).check()
    cy.get('[data-cy="report-checkbox"]').eq(2).check()
    
    // Exportar en lote
    cy.get('[data-cy="bulk-export"]').click()
    
    // Verificar opciones de exportación en lote
    cy.get('[data-cy="bulk-export-options"]').should('be.visible')
    cy.get('[data-cy="export-format"]').select('zip')
    cy.get('[data-cy="include-index"]').check()
    
    // Confirmar exportación
    cy.get('[data-cy="confirm-bulk-export"]').click()
    
    // Verificar descarga
    cy.verifyDownload('reportes-lote.zip')
  })

  it('debe compartir reporte por email', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Compartir por email
    cy.get('[data-cy="share-email"]').click()
    
    // Configurar email
    cy.get('[data-cy="email-recipients"]').type('test@example.com, admin@cacaoscan.com')
    cy.get('[data-cy="email-subject"]').type('Reporte de Análisis de Cacao')
    cy.get('[data-cy="email-message"]').type('Adjunto encontrará el reporte solicitado.')
    
    // Configurar formato de adjunto
    cy.get('[data-cy="attachment-format"]').select('pdf')
    cy.get('[data-cy="include-summary"]').check()
    
    // Enviar email
    cy.get('[data-cy="send-email"]').click()
    
    // Verificar éxito
    cy.checkNotification('Reporte enviado por email exitosamente', 'success')
  })

  it('debe generar enlace de compartir', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Generar enlace
    cy.get('[data-cy="share-link"]').click()
    
    // Configurar enlace
    cy.get('[data-cy="link-expiration"]').select('7-days')
    cy.get('[data-cy="require-password"]').check()
    cy.get('[data-cy="link-password"]').type('secure123')
    
    // Generar enlace
    cy.get('[data-cy="generate-link"]').click()
    
    // Verificar enlace generado
    cy.get('[data-cy="generated-link"]').should('be.visible')
    cy.get('[data-cy="copy-link"]').should('be.visible')
    
    // Copiar enlace
    cy.get('[data-cy="copy-link"]').click()
    cy.checkNotification('Enlace copiado al portapapeles', 'success')
  })

  it('debe programar envío automático de reportes', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Programar envío automático
    cy.get('[data-cy="schedule-sharing"]').click()
    
    // Configurar programación
    cy.get('[data-cy="schedule-frequency"]').select('mensual')
    cy.get('[data-cy="schedule-day"]').type('1')
    cy.get('[data-cy="schedule-time"]').type('09:00')
    
    // Configurar destinatarios
    cy.get('[data-cy="schedule-recipients"]').type('admin@cacaoscan.com')
    cy.get('[data-cy="schedule-subject"]').type('Reporte Mensual Automático')
    
    // Guardar programación
    cy.get('[data-cy="save-schedule"]').click()
    
    // Verificar éxito
    cy.checkNotification('Envío automático programado exitosamente', 'success')
  })

  it('debe mostrar historial de compartir', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Verificar historial de compartir
    cy.get('[data-cy="sharing-history"]').should('be.visible')
    cy.get('[data-cy="sharing-item"]').should('have.length.greaterThan', 0)
    
    // Verificar información de cada compartir
    cy.get('[data-cy="sharing-item"]').first().within(() => {
      cy.get('[data-cy="sharing-date"]').should('be.visible')
      cy.get('[data-cy="sharing-method"]').should('be.visible')
      cy.get('[data-cy="sharing-recipients"]').should('be.visible')
    })
  })

  it('debe permitir revocar acceso a reporte compartido', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Revocar acceso
    cy.get('[data-cy="sharing-item"]').first().within(() => {
      cy.get('[data-cy="revoke-access"]').click()
    })
    
    // Confirmar revocación
    cy.get('[data-cy="confirm-revoke"]').click()
    
    // Verificar éxito
    cy.checkNotification('Acceso revocado exitosamente', 'success')
  })

  it('debe exportar reporte con marca de agua', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Exportar con marca de agua
    cy.get('[data-cy="download-pdf"]').click()
    
    // Configurar marca de agua
    cy.get('[data-cy="watermark-text"]').type('CONFIDENCIAL')
    cy.get('[data-cy="watermark-position"]').select('center')
    cy.get('[data-cy="watermark-opacity"]').type('0.3')
    
    // Confirmar descarga
    cy.get('[data-cy="confirm-download"]').click()
    
    // Verificar descarga
    cy.verifyDownload('reporte-marcado.pdf')
  })

  it('debe exportar reporte con firma digital', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Exportar con firma digital
    cy.get('[data-cy="download-pdf"]').click()
    
    // Configurar firma digital
    cy.get('[data-cy="digital-signature"]').check()
    cy.get('[data-cy="signature-certificate"]').select('certificado-valido')
    cy.get('[data-cy="signature-reason"]').type('Aprobación del reporte')
    
    // Confirmar descarga
    cy.get('[data-cy="confirm-download"]').click()
    
    // Verificar descarga
    cy.verifyDownload('reporte-firmado.pdf')
  })

  it('debe mostrar vista previa antes de exportar', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Ver vista previa
    cy.get('[data-cy="preview-export"]').click()
    
    // Verificar vista previa
    cy.get('[data-cy="export-preview"]').should('be.visible')
    cy.get('[data-cy="preview-content"]').should('be.visible')
    cy.get('[data-cy="preview-pages"]').should('be.visible')
    
    // Navegar por páginas
    cy.get('[data-cy="next-page"]').click()
    cy.get('[data-cy="previous-page"]').click()
  })

  it('debe manejar errores durante la exportación', () => {
    // Simular error de exportación
    cy.intercept('POST', '/api/reportes/*/export/', {
      statusCode: 500,
      body: { error: 'Error al exportar reporte' }
    }).as('exportError')
    
    cy.get('[data-cy="report-item"]').first().click()
    cy.get('[data-cy="download-pdf"]').click()
    cy.get('[data-cy="confirm-download"]').click()
    
    cy.wait('@exportError')
    
    // Verificar mensaje de error
    cy.get('[data-cy="export-error"]')
      .should('be.visible')
      .and('contain', 'Error al exportar reporte')
  })

  it('debe mostrar progreso de exportación', () => {
    cy.get('[data-cy="report-item"]').first().click()
    cy.get('[data-cy="download-pdf"]').click()
    cy.get('[data-cy="confirm-download"]').click()
    
    // Verificar progreso
    cy.get('[data-cy="export-progress"]').should('be.visible')
    cy.get('[data-cy="progress-percentage"]').should('contain', '%')
  })
})
