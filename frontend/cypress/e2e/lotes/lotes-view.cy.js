import { 
  visitAndWaitForBody, 
  verifyElementsVisible 
} from '../../support/helpers'

describe('Gestión de Lotes - LotesView y LoteDetailView', () => {

  beforeEach(() => {
    cy.login('farmer')
    visitAndWaitForBody('/lotes')
  })

  it('debe mostrar lista de lotes', () => {
    verifyElementsVisible([
      '[data-cy="lotes-list"]',
      '[data-cy="lotes-header"]',
      '[data-cy="create-lote-button"]'
    ])
  })

  it('debe mostrar filtros de lotes', () => {
    verifyElementsVisible([
      '[data-cy="lotes-filters"]',
      '[data-cy="filter-finca"]',
      '[data-cy="filter-status"]'
    ])
  })

  it('debe crear nuevo lote', () => {
    cy.createLote({
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
      verifyElementsVisible([
        '[data-cy="lote-name"]',
        '[data-cy="lote-finca"]',
        '[data-cy="lote-area"]',
        '[data-cy="lote-description"]',
        '[data-cy="lote-analisis"]'
      ])
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
    cy.applyFilter('finca', '1')
    
    cy.get('[data-cy="lotes-list"]').should('be.visible')
  })

  it('debe buscar lotes por nombre', () => {
    cy.get('[data-cy="search-lotes"]').type('Norte')
    cy.get('[data-cy="apply-search"]').click()
    
    cy.get('[data-cy="lotes-list"]').should('contain', 'Norte')
  })

  it('debe mostrar estadísticas de lotes', () => {
    verifyElementsVisible([
      '[data-cy="lotes-stats"]',
      '[data-cy="total-lotes"]',
      '[data-cy="total-area"]'
    ])
  })

  it('debe mostrar mensaje cuando no hay lotes', () => {
    cy.applyFilter('finca', '999')
    
    cy.verifyEmptyStateMessage('[data-cy="empty-state"]', 'No se encontraron lotes')
  })
})
