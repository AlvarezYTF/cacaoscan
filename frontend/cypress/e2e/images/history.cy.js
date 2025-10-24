describe('Gestión de Imágenes - Historial y Detalles', () => {
  beforeEach(() => {
    cy.login('farmer')
  })

  it('debe mostrar historial de imágenes cargadas', () => {
    cy.visit('/mis-imagenes')
    
    // Verificar elementos del historial
    cy.get('[data-cy="images-history"]').should('be.visible')
    cy.get('[data-cy="image-list"]').should('be.visible')
    cy.get('[data-cy="search-images"]').should('be.visible')
    cy.get('[data-cy="filter-images"]').should('be.visible')
  })

  it('debe mostrar detalles de imagen específica', () => {
    cy.visit('/mis-imagenes')
    
    // Hacer clic en primera imagen
    cy.get('[data-cy="image-item"]').first().click()
    
    // Verificar detalles
    cy.get('[data-cy="image-details"]').should('be.visible')
    cy.get('[data-cy="image-metadata"]').should('be.visible')
    cy.get('[data-cy="analysis-results"]').should('be.visible')
    cy.get('[data-cy="upload-date"]').should('be.visible')
  })

  it('debe permitir buscar imágenes por nombre', () => {
    cy.visit('/mis-imagenes')
    
    // Buscar imagen específica
    cy.get('[data-cy="search-images"]').type('test-cacao')
    
    // Verificar resultados filtrados
    cy.get('[data-cy="image-item"]').should('contain', 'test-cacao')
    cy.get('[data-cy="search-results-count"]').should('be.visible')
  })

  it('debe permitir filtrar imágenes por fecha', () => {
    cy.visit('/mis-imagenes')
    
    // Aplicar filtro de fecha
    cy.get('[data-cy="date-filter"]').click()
    cy.get('[data-cy="date-range-start"]').type('2024-01-01')
    cy.get('[data-cy="date-range-end"]').type('2024-12-31')
    cy.get('[data-cy="apply-date-filter"]').click()
    
    // Verificar filtros aplicados
    cy.get('[data-cy="active-filters"]').should('be.visible')
    cy.get('[data-cy="filtered-results"]').should('be.visible')
  })

  it('debe permitir filtrar imágenes por calidad', () => {
    cy.visit('/mis-imagenes')
    
    // Aplicar filtro de calidad
    cy.get('[data-cy="quality-filter"]').click()
    cy.get('[data-cy="quality-excellent"]').check()
    cy.get('[data-cy="apply-quality-filter"]').click()
    
    // Verificar que solo se muestran imágenes de calidad excelente
    cy.get('[data-cy="image-item"]').each(($item) => {
      cy.wrap($item).should('contain', 'Excelente')
    })
  })

  it('debe permitir ordenar imágenes', () => {
    cy.visit('/mis-imagenes')
    
    // Ordenar por fecha (más recientes primero)
    cy.get('[data-cy="sort-images"]').select('date-desc')
    
    // Verificar orden
    cy.get('[data-cy="image-item"]').first().should('contain', '2024-01-15')
    
    // Ordenar por calidad
    cy.get('[data-cy="sort-images"]').select('quality-desc')
    
    // Verificar orden por calidad
    cy.get('[data-cy="image-item"]').first().should('contain', 'Excelente')
  })

  it('debe permitir eliminar imagen', () => {
    cy.visit('/mis-imagenes')
    
    // Seleccionar imagen para eliminar
    cy.get('[data-cy="image-item"]').first().within(() => {
      cy.get('[data-cy="delete-image"]').click()
    })
    
    // Confirmar eliminación
    cy.get('[data-cy="confirm-delete"]').click()
    
    // Verificar mensaje de éxito
    cy.get('[data-cy="delete-success"]')
      .should('be.visible')
      .and('contain', 'Imagen eliminada')
  })

  it('debe permitir descargar imagen original', () => {
    cy.visit('/mis-imagenes')
    
    // Descargar imagen
    cy.get('[data-cy="image-item"]').first().within(() => {
      cy.get('[data-cy="download-image"]').click()
    })
    
    // Verificar descarga
    cy.verifyDownload('imagen-cacao.jpg')
  })

  it('debe permitir descargar imagen procesada', () => {
    cy.visit('/mis-imagenes')
    
    // Descargar imagen procesada
    cy.get('[data-cy="image-item"]').first().within(() => {
      cy.get('[data-cy="download-processed"]').click()
    })
    
    // Verificar descarga
    cy.verifyDownload('imagen-procesada.jpg')
  })

  it('debe mostrar estadísticas de imágenes', () => {
    cy.visit('/mis-imagenes')
    
    // Verificar estadísticas
    cy.get('[data-cy="images-stats"]').should('be.visible')
    cy.get('[data-cy="total-images"]').should('be.visible')
    cy.get('[data-cy="average-quality"]').should('be.visible')
    cy.get('[data-cy="images-this-month"]').should('be.visible')
  })

  it('debe permitir selección múltiple de imágenes', () => {
    cy.visit('/mis-imagenes')
    
    // Seleccionar múltiples imágenes
    cy.get('[data-cy="select-all"]').check()
    
    // Verificar que todas están seleccionadas
    cy.get('[data-cy="image-checkbox"]').should('be.checked')
    
    // Verificar acciones en lote
    cy.get('[data-cy="bulk-actions"]').should('be.visible')
    cy.get('[data-cy="bulk-download"]').should('be.visible')
    cy.get('[data-cy="bulk-delete"]').should('be.visible')
  })

  it('debe permitir acciones en lote', () => {
    cy.visit('/mis-imagenes')
    
    // Seleccionar imágenes
    cy.get('[data-cy="image-checkbox"]').first().check()
    cy.get('[data-cy="image-checkbox"]').eq(1).check()
    
    // Descargar seleccionadas
    cy.get('[data-cy="bulk-download"]').click()
    
    // Verificar descarga múltiple
    cy.verifyDownload('imagenes-seleccionadas.zip')
  })

  it('debe mostrar paginación cuando hay muchas imágenes', () => {
    // Simular muchas imágenes
    cy.intercept('GET', '/api/images/', {
      statusCode: 200,
      body: {
        results: Array(25).fill().map((_, i) => ({
          id: i + 1,
          filename: `imagen-${i + 1}.jpg`,
          uploaded_at: '2024-01-15T10:30:00Z'
        })),
        count: 100,
        next: '/api/images/?page=2',
        previous: null
      }
    }).as('imagesPage1')
    
    cy.visit('/mis-imagenes')
    cy.wait('@imagesPage1')
    
    // Verificar paginación
    cy.get('[data-cy="pagination"]').should('be.visible')
    cy.get('[data-cy="page-info"]').should('contain', '1 de 4')
    
    // Navegar a siguiente página
    cy.get('[data-cy="next-page"]').click()
    cy.get('[data-cy="page-info"]').should('contain', '2 de 4')
  })

  it('debe permitir ver imagen en modal', () => {
    cy.visit('/mis-imagenes')
    
    // Hacer clic en imagen para ver en modal
    cy.get('[data-cy="image-thumbnail"]').first().click()
    
    // Verificar modal
    cy.get('[data-cy="image-modal"]').should('be.visible')
    cy.get('[data-cy="modal-image"]').should('be.visible')
    cy.get('[data-cy="close-modal"]').should('be.visible')
    
    // Cerrar modal
    cy.get('[data-cy="close-modal"]').click()
    cy.get('[data-cy="image-modal"]').should('not.exist')
  })

  it('debe mostrar información de análisis en historial', () => {
    cy.visit('/mis-imagenes')
    
    // Verificar información de análisis en cada imagen
    cy.get('[data-cy="image-item"]').each(($item) => {
      cy.wrap($item).within(() => {
        cy.get('[data-cy="analysis-status"]').should('be.visible')
        cy.get('[data-cy="quality-badge"]').should('be.visible')
        cy.get('[data-cy="analysis-date"]').should('be.visible')
      })
    })
  })
})
