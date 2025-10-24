describe('Gestión de Lotes - CRUD', () => {
  beforeEach(() => {
    cy.login('farmer')
    cy.visit('/mis-lotes')
  })

  it('debe mostrar lista de lotes del usuario', () => {
    cy.get('[data-cy="lotes-list"]').should('be.visible')
    cy.get('[data-cy="add-lote-button"]').should('be.visible')
    cy.get('[data-cy="lotes-stats"]').should('be.visible')
  })

  it('debe crear nuevo lote exitosamente', () => {
    cy.fixture('testData').then((data) => {
      const loteData = data.lotes[0]
      
      cy.get('[data-cy="add-lote-button"]').click()
      
      // Seleccionar finca
      cy.get('[data-cy="finca-select"]').select('1')
      
      // Llenar formulario
      cy.fillLoteForm(loteData)
      
      // Guardar lote
      cy.get('[data-cy="save-lote"]').click()
      
      // Verificar éxito
      cy.checkNotification('Lote creado exitosamente', 'success')
      
      // Verificar que aparece en la lista
      cy.get('[data-cy="lotes-list"]').should('contain', loteData.nombre)
    })
  })

  it('debe validar campos requeridos en formulario de lote', () => {
    cy.get('[data-cy="add-lote-button"]').click()
    cy.get('[data-cy="save-lote"]').click()
    
    // Verificar errores de validación
    cy.get('[data-cy="lote-nombre-error"]').should('be.visible')
    cy.get('[data-cy="lote-area-error"]').should('be.visible')
    cy.get('[data-cy="lote-variedad-error"]').should('be.visible')
    cy.get('[data-cy="lote-edad-error"]').should('be.visible')
  })

  it('debe validar área de lote positiva', () => {
    cy.get('[data-cy="add-lote-button"]').click()
    
    cy.get('[data-cy="finca-select"]').select('1')
    cy.get('[data-cy="lote-nombre"]').type('Lote Test')
    cy.get('[data-cy="lote-area"]').type('-2')
    cy.get('[data-cy="lote-variedad"]').select('CCN-51')
    cy.get('[data-cy="lote-edad"]').type('5')
    cy.get('[data-cy="lote-descripcion"]').type('Test description')
    
    cy.get('[data-cy="save-lote"]').click()
    
    cy.get('[data-cy="lote-area-error"]')
      .should('be.visible')
      .and('contain', 'El área debe ser positiva')
  })

  it('debe validar edad de plantas', () => {
    cy.get('[data-cy="add-lote-button"]').click()
    
    cy.get('[data-cy="finca-select"]').select('1')
    cy.get('[data-cy="lote-nombre"]').type('Lote Test')
    cy.get('[data-cy="lote-area"]').type('2')
    cy.get('[data-cy="lote-variedad"]').select('CCN-51')
    cy.get('[data-cy="lote-edad"]').type('50') // Edad muy alta
    cy.get('[data-cy="lote-descripcion"]').type('Test description')
    
    cy.get('[data-cy="save-lote"]').click()
    
    cy.get('[data-cy="lote-edad-error"]')
      .should('be.visible')
      .and('contain', 'La edad debe ser menor a 30 años')
  })

  it('debe mostrar detalles de lote específico', () => {
    cy.get('[data-cy="lote-item"]').first().click()
    
    // Verificar detalles
    cy.get('[data-cy="lote-details"]').should('be.visible')
    cy.get('[data-cy="lote-name"]').should('be.visible')
    cy.get('[data-cy="lote-area"]').should('be.visible')
    cy.get('[data-cy="lote-variedad"]').should('be.visible')
    cy.get('[data-cy="lote-edad"]').should('be.visible')
    cy.get('[data-cy="lote-description"]').should('be.visible')
    cy.get('[data-cy="lote-finca"]').should('be.visible')
  })

  it('debe editar lote existente', () => {
    cy.get('[data-cy="lote-item"]').first().click()
    cy.get('[data-cy="edit-lote"]').click()
    
    // Modificar datos
    cy.get('[data-cy="lote-nombre"]').clear().type('Lote Editado')
    cy.get('[data-cy="lote-descripcion"]').clear().type('Descripción actualizada')
    
    cy.get('[data-cy="save-lote"]').click()
    
    // Verificar éxito
    cy.checkNotification('Lote actualizado exitosamente', 'success')
    
    // Verificar cambios
    cy.get('[data-cy="lote-name"]').should('contain', 'Lote Editado')
  })

  it('debe eliminar lote con confirmación', () => {
    cy.get('[data-cy="lote-item"]').first().click()
    cy.get('[data-cy="delete-lote"]').click()
    
    // Confirmar eliminación
    cy.get('[data-cy="confirm-delete"]').click()
    
    // Verificar éxito
    cy.checkNotification('Lote eliminado exitosamente', 'success')
    
    // Verificar que se eliminó de la lista
    cy.visit('/mis-lotes')
    cy.get('[data-cy="lotes-list"]').should('not.contain', 'Lote eliminado')
  })

  it('debe mostrar análisis asociados al lote', () => {
    cy.get('[data-cy="lote-item"]').first().click()
    
    // Verificar sección de análisis
    cy.get('[data-cy="lote-analisis"]').should('be.visible')
    cy.get('[data-cy="analisis-count"]').should('be.visible')
    cy.get('[data-cy="ultimo-analisis"]').should('be.visible')
  })

  it('debe mostrar estadísticas de lotes', () => {
    cy.get('[data-cy="lotes-stats"]').should('be.visible')
    cy.get('[data-cy="total-lotes"]').should('be.visible')
    cy.get('[data-cy="total-area-lotes"]').should('be.visible')
    cy.get('[data-cy="variedades-count"]').should('be.visible')
  })

  it('debe permitir buscar lotes por nombre', () => {
    cy.get('[data-cy="search-lotes"]').type('Norte')
    
    // Verificar resultados filtrados
    cy.get('[data-cy="lote-item"]').should('contain', 'Norte')
    cy.get('[data-cy="search-results-count"]').should('be.visible')
  })

  it('debe permitir filtrar lotes por finca', () => {
    cy.get('[data-cy="finca-filter"]').select('Finca El Paraíso')
    cy.get('[data-cy="apply-filter"]').click()
    
    // Verificar filtros aplicados
    cy.get('[data-cy="active-filters"]').should('be.visible')
    cy.get('[data-cy="filtered-results"]').should('be.visible')
  })

  it('debe permitir filtrar lotes por variedad', () => {
    cy.get('[data-cy="variedad-filter"]').select('CCN-51')
    cy.get('[data-cy="apply-filter"]').click()
    
    // Verificar que solo se muestran lotes de CCN-51
    cy.get('[data-cy="lote-item"]').each(($item) => {
      cy.wrap($item).should('contain', 'CCN-51')
    })
  })

  it('debe mostrar gráficos de rendimiento por lote', () => {
    cy.get('[data-cy="lote-item"]').first().click()
    
    // Verificar gráficos
    cy.get('[data-cy="rendimiento-chart"]').should('be.visible')
    cy.get('[data-cy="calidad-trend"]').should('be.visible')
    cy.get('[data-cy="produccion-history"]').should('be.visible')
  })

  it('debe permitir exportar datos de lotes', () => {
    cy.get('[data-cy="export-lotes"]').click()
    
    // Verificar opciones de exportación
    cy.get('[data-cy="export-pdf"]').should('be.visible')
    cy.get('[data-cy="export-excel"]').should('be.visible')
    
    // Exportar como Excel
    cy.get('[data-cy="export-excel"]').click()
    cy.verifyDownload('lotes.xlsx')
  })

  it('debe mostrar alertas de mantenimiento', () => {
    cy.get('[data-cy="lote-item"]').first().click()
    
    // Verificar alertas
    cy.get('[data-cy="maintenance-alerts"]').should('be.visible')
    cy.get('[data-cy="alert-item"]').should('be.visible')
  })

  it('debe permitir programar análisis para lote', () => {
    cy.get('[data-cy="lote-item"]').first().click()
    cy.get('[data-cy="schedule-analysis"]').click()
    
    // Programar análisis
    cy.get('[data-cy="analysis-date"]').type('2024-02-15')
    cy.get('[data-cy="analysis-time"]').type('10:00')
    cy.get('[data-cy="analysis-notes"]').type('Análisis programado')
    
    cy.get('[data-cy="save-schedule"]').click()
    
    // Verificar éxito
    cy.checkNotification('Análisis programado exitosamente', 'success')
  })

  it('debe mostrar historial de análisis del lote', () => {
    cy.get('[data-cy="lote-item"]').first().click()
    
    // Verificar historial
    cy.get('[data-cy="analisis-history"]').should('be.visible')
    cy.get('[data-cy="analisis-item"]').should('have.length.greaterThan', 0)
    
    // Verificar información de cada análisis
    cy.get('[data-cy="analisis-item"]').first().within(() => {
      cy.get('[data-cy="analisis-date"]').should('be.visible')
      cy.get('[data-cy="analisis-quality"]').should('be.visible')
      cy.get('[data-cy="analisis-results"]').should('be.visible')
    })
  })

  it('debe manejar errores al crear lote', () => {
    // Simular error del servidor
    cy.intercept('POST', '/api/lotes/', {
      statusCode: 500,
      body: { error: 'Error del servidor' }
    }).as('createLoteError')
    
    cy.get('[data-cy="add-lote-button"]').click()
    
    cy.fixture('testData').then((data) => {
      const loteData = data.lotes[0]
      cy.get('[data-cy="finca-select"]').select('1')
      cy.fillLoteForm(loteData)
    })
    
    cy.get('[data-cy="save-lote"]').click()
    cy.wait('@createLoteError')
    
    // Verificar mensaje de error
    cy.get('[data-cy="error-message"]')
      .should('be.visible')
      .and('contain', 'Error al crear lote')
  })

  it('debe validar que el área del lote no exceda el área de la finca', () => {
    cy.get('[data-cy="add-lote-button"]').click()
    
    cy.get('[data-cy="finca-select"]').select('1') // Finca con área 15.5
    cy.get('[data-cy="lote-nombre"]').type('Lote Grande')
    cy.get('[data-cy="lote-area"]').type('20') // Área mayor que la finca
    cy.get('[data-cy="lote-variedad"]').select('CCN-51')
    cy.get('[data-cy="lote-edad"]').type('5')
    cy.get('[data-cy="lote-descripcion"]').type('Test description')
    
    cy.get('[data-cy="save-lote"]').click()
    
    cy.get('[data-cy="lote-area-error"]')
      .should('be.visible')
      .and('contain', 'El área del lote no puede exceder el área de la finca')
  })
})
