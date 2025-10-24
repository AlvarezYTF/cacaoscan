describe('Gestión de Fincas - CRUD', () => {
  beforeEach(() => {
    cy.login('farmer')
    cy.visit('/mis-fincas')
  })

  it('debe mostrar lista de fincas del usuario', () => {
    cy.get('[data-cy="fincas-list"]').should('be.visible')
    cy.get('[data-cy="add-finca-button"]').should('be.visible')
    cy.get('[data-cy="fincas-stats"]').should('be.visible')
  })

  it('debe crear nueva finca exitosamente', () => {
    cy.fixture('testData').then((data) => {
      const fincaData = data.fincas[0]
      
      cy.get('[data-cy="add-finca-button"]').click()
      
      // Llenar formulario
      cy.fillFincaForm(fincaData)
      
      // Seleccionar ubicación en mapa
      cy.get('[data-cy="map-container"]').should('be.visible')
      cy.get('[data-cy="map-container"]').click(300, 200)
      
      // Guardar finca
      cy.get('[data-cy="save-finca"]').click()
      
      // Verificar éxito
      cy.checkNotification('Finca creada exitosamente', 'success')
      
      // Verificar que aparece en la lista
      cy.get('[data-cy="fincas-list"]').should('contain', fincaData.nombre)
    })
  })

  it('debe validar campos requeridos en formulario de finca', () => {
    cy.get('[data-cy="add-finca-button"]').click()
    cy.get('[data-cy="save-finca"]').click()
    
    // Verificar errores de validación
    cy.get('[data-cy="finca-nombre-error"]').should('be.visible')
    cy.get('[data-cy="finca-ubicacion-error"]').should('be.visible')
    cy.get('[data-cy="finca-area-error"]').should('be.visible')
  })

  it('debe validar área de finca positiva', () => {
    cy.get('[data-cy="add-finca-button"]').click()
    
    cy.get('[data-cy="finca-nombre"]').type('Finca Test')
    cy.get('[data-cy="finca-ubicacion"]').type('Test Location')
    cy.get('[data-cy="finca-area"]').type('-5')
    cy.get('[data-cy="finca-descripcion"]').type('Test description')
    
    cy.get('[data-cy="save-finca"]').click()
    
    cy.get('[data-cy="finca-area-error"]')
      .should('be.visible')
      .and('contain', 'El área debe ser positiva')
  })

  it('debe mostrar detalles de finca específica', () => {
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Verificar detalles
    cy.get('[data-cy="finca-details"]').should('be.visible')
    cy.get('[data-cy="finca-name"]').should('be.visible')
    cy.get('[data-cy="finca-location"]').should('be.visible')
    cy.get('[data-cy="finca-area"]').should('be.visible')
    cy.get('[data-cy="finca-description"]').should('be.visible')
    cy.get('[data-cy="finca-map"]').should('be.visible')
  })

  it('debe editar finca existente', () => {
    cy.get('[data-cy="finca-item"]').first().click()
    cy.get('[data-cy="edit-finca"]').click()
    
    // Modificar datos
    cy.get('[data-cy="finca-nombre"]').clear().type('Finca Editada')
    cy.get('[data-cy="finca-descripcion"]').clear().type('Descripción actualizada')
    
    cy.get('[data-cy="save-finca"]').click()
    
    // Verificar éxito
    cy.checkNotification('Finca actualizada exitosamente', 'success')
    
    // Verificar cambios
    cy.get('[data-cy="finca-name"]').should('contain', 'Finca Editada')
  })

  it('debe eliminar finca con confirmación', () => {
    cy.get('[data-cy="finca-item"]').first().click()
    cy.get('[data-cy="delete-finca"]').click()
    
    // Confirmar eliminación
    cy.get('[data-cy="confirm-delete"]').click()
    
    // Verificar éxito
    cy.checkNotification('Finca eliminada exitosamente', 'success')
    
    // Verificar que se eliminó de la lista
    cy.visit('/mis-fincas')
    cy.get('[data-cy="fincas-list"]').should('not.contain', 'Finca eliminada')
  })

  it('debe cancelar eliminación de finca', () => {
    cy.get('[data-cy="finca-item"]').first().click()
    cy.get('[data-cy="delete-finca"]').click()
    
    // Cancelar eliminación
    cy.get('[data-cy="cancel-delete"]').click()
    
    // Verificar que permanece
    cy.get('[data-cy="finca-details"]').should('be.visible')
  })

  it('debe mostrar estadísticas de fincas', () => {
    cy.get('[data-cy="fincas-stats"]').should('be.visible')
    cy.get('[data-cy="total-fincas"]').should('be.visible')
    cy.get('[data-cy="total-area"]').should('be.visible')
    cy.get('[data-cy="average-area"]').should('be.visible')
  })

  it('debe permitir buscar fincas por nombre', () => {
    cy.get('[data-cy="search-fincas"]').type('Paraíso')
    
    // Verificar resultados filtrados
    cy.get('[data-cy="finca-item"]').should('contain', 'Paraíso')
    cy.get('[data-cy="search-results-count"]').should('be.visible')
  })

  it('debe permitir filtrar fincas por ubicación', () => {
    cy.get('[data-cy="location-filter"]').click()
    cy.get('[data-cy="province-filter"]').select('Los Ríos')
    cy.get('[data-cy="apply-filter"]').click()
    
    // Verificar filtros aplicados
    cy.get('[data-cy="active-filters"]').should('be.visible')
    cy.get('[data-cy="filtered-results"]').should('be.visible')
  })

  it('debe mostrar mapa con ubicación de fincas', () => {
    cy.get('[data-cy="fincas-map"]').should('be.visible')
    cy.get('[data-cy="map-markers"]').should('be.visible')
    
    // Hacer clic en marcador
    cy.get('[data-cy="map-marker"]').first().click()
    
    // Verificar popup con información
    cy.get('[data-cy="map-popup"]').should('be.visible')
    cy.get('[data-cy="popup-finca-name"]').should('be.visible')
  })

  it('debe permitir exportar lista de fincas', () => {
    cy.get('[data-cy="export-fincas"]').click()
    
    // Verificar opciones de exportación
    cy.get('[data-cy="export-pdf"]').should('be.visible')
    cy.get('[data-cy="export-excel"]').should('be.visible')
    
    // Exportar como PDF
    cy.get('[data-cy="export-pdf"]').click()
    cy.verifyDownload('fincas.pdf')
  })

  it('debe mostrar lotes asociados a cada finca', () => {
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Verificar sección de lotes
    cy.get('[data-cy="finca-lotes"]').should('be.visible')
    cy.get('[data-cy="lotes-count"]').should('be.visible')
    cy.get('[data-cy="add-lote-button"]').should('be.visible')
  })

  it('debe manejar errores al crear finca', () => {
    // Simular error del servidor
    cy.intercept('POST', '/api/fincas/', {
      statusCode: 500,
      body: { error: 'Error del servidor' }
    }).as('createFincaError')
    
    cy.get('[data-cy="add-finca-button"]').click()
    
    cy.fixture('testData').then((data) => {
      const fincaData = data.fincas[0]
      cy.fillFincaForm(fincaData)
    })
    
    cy.get('[data-cy="save-finca"]').click()
    cy.wait('@createFincaError')
    
    // Verificar mensaje de error
    cy.get('[data-cy="error-message"]')
      .should('be.visible')
      .and('contain', 'Error al crear finca')
  })

  it('debe validar ubicación en mapa', () => {
    cy.get('[data-cy="add-finca-button"]').click()
    
    cy.get('[data-cy="finca-nombre"]').type('Finca Test')
    cy.get('[data-cy="finca-ubicacion"]').type('Test Location')
    cy.get('[data-cy="finca-area"]').type('10')
    cy.get('[data-cy="finca-descripcion"]').type('Test description')
    
    // Intentar guardar sin seleccionar ubicación en mapa
    cy.get('[data-cy="save-finca"]').click()
    
    cy.get('[data-cy="location-error"]')
      .should('be.visible')
      .and('contain', 'Debe seleccionar ubicación en el mapa')
  })
})
