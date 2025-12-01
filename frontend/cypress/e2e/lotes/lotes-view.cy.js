import { visitAndWaitForBody } from '../../support/helpers'

describe('Gestión de Lotes - LotesView y LoteDetailView', () => {
  const createLote = (loteData) => {
    cy.get('[data-cy="create-lote-button"]').click()
    
    if (loteData.nombre) {
      cy.get('[data-cy="lote-nombre"]').type(loteData.nombre)
    }
    if (loteData.finca) {
      cy.get('[data-cy="lote-finca"]').select(loteData.finca)
    }
    if (loteData.area) {
      cy.get('[data-cy="lote-area"]').type(loteData.area)
    }
    if (loteData.descripcion) {
      cy.get('[data-cy="lote-descripcion"]').type(loteData.descripcion)
    }
    
    cy.get('[data-cy="save-lote"]').click()
  }

  const applyFilter = (filterType, value) => {
    cy.get(`[data-cy="filter-${filterType}"]`).select(value)
    cy.get('[data-cy="apply-filters"]').click()
  }

  beforeEach(() => {
    cy.login('farmer')
    visitAndWaitForBody('/lotes')
  })

  it('debe mostrar lista de lotes', () => {
    cy.get('[data-cy="lotes-list"]').should('be.visible')
    cy.get('[data-cy="lotes-header"]').should('be.visible')
    cy.get('[data-cy="create-lote-button"]').should('be.visible')
  })

  it('debe mostrar filtros de lotes', () => {
    cy.get('[data-cy="lotes-filters"]').should('be.visible')
    cy.get('[data-cy="filter-finca"]').should('be.visible')
    cy.get('[data-cy="filter-status"]').should('be.visible')
  })

  it('debe crear nuevo lote', () => {
    createLote({
      nombre: 'Lote Norte',
      finca: '1',
      area: '5.5',
      descripcion: 'Lote de cacao criollo'
    })
    
    cy.checkNotification('Lote creado exitosamente', 'success')
    cy.get('[data-cy="lotes-list"]').should('contain', 'Lote Norte')
  })

  it('debe validar campos requeridos al crear lote', () => {
    cy.get('[data-cy="create-lote-button"]').click()
    cy.get('[data-cy="save-lote"]').click()
    
    cy.get('[data-cy="lote-nombre-error"]').should('be.visible')
    cy.get('[data-cy="lote-finca-error"]').should('be.visible')
    cy.get('[data-cy="lote-area-error"]').should('be.visible')
  })

  it('debe navegar a detalle de lote', () => {
    cy.get('[data-cy="lote-item"]').first().click()
    
    cy.url().should('include', '/lotes/')
    cy.get('[data-cy="lote-detail"]').should('be.visible')
    cy.get('[data-cy="lote-name"]').should('be.visible')
  })

  it('debe mostrar detalles completos del lote', () => {
    cy.get('[data-cy="lote-item"]').first().click()
    
    cy.get('[data-cy="lote-detail"]').within(() => {
      cy.get('[data-cy="lote-name"]').should('be.visible')
      cy.get('[data-cy="lote-finca"]').should('be.visible')
      cy.get('[data-cy="lote-area"]').should('be.visible')
      cy.get('[data-cy="lote-description"]').should('be.visible')
      cy.get('[data-cy="lote-analisis"]').should('be.visible')
    })
  })

  it('debe editar lote existente', () => {
    cy.get('[data-cy="lote-item"]').first().click()
    cy.get('[data-cy="edit-lote"]').click()
    
    cy.get('[data-cy="lote-nombre"]').clear().type('Lote Editado')
    cy.get('[data-cy="lote-descripcion"]').clear().type('Descripción actualizada')
    
    cy.get('[data-cy="save-lote"]').click()
    
    cy.checkNotification('Lote actualizado exitosamente', 'success')
    cy.get('[data-cy="lote-name"]').should('contain', 'Lote Editado')
  })

  it('debe eliminar lote con confirmación', () => {
    cy.get('[data-cy="lote-item"]').first().click()
    cy.get('[data-cy="delete-lote"]').click()
    
    cy.confirmAction()
    
    cy.checkNotification('Lote eliminado exitosamente', 'success')
    cy.url().should('include', '/lotes')
  })

  it('debe navegar a análisis del lote', () => {
    cy.get('[data-cy="lote-item"]').first().click()
    cy.get('[data-cy="view-analisis"]').click()
    
    cy.url().should('include', '/analisis')
    cy.get('[data-cy="analisis-view"]').should('be.visible')
  })

  it('debe filtrar lotes por finca', () => {
    applyFilter('finca', '1')
    
    cy.get('[data-cy="lotes-list"]').should('be.visible')
  })

  it('debe buscar lotes por nombre', () => {
    cy.get('[data-cy="search-lotes"]').type('Norte')
    cy.get('[data-cy="apply-search"]').click()
    
    cy.get('[data-cy="lotes-list"]').should('contain', 'Norte')
  })

  it('debe mostrar estadísticas de lotes', () => {
    cy.get('[data-cy="lotes-stats"]').should('be.visible')
    cy.get('[data-cy="total-lotes"]').should('be.visible')
    cy.get('[data-cy="total-area"]').should('be.visible')
  })

  it('debe mostrar mensaje cuando no hay lotes', () => {
    applyFilter('finca', '999')
    
    cy.get('[data-cy="empty-state"]').should('be.visible')
    cy.get('[data-cy="empty-state"]').should('contain', 'No se encontraron lotes')
  })
})
