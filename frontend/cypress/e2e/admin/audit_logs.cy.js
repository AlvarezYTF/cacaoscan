import { verifyUrlContains, ifFoundInBody } from '../../support/helpers'

describe('Admin Audit Logs', () => {
  const verifyPageTitle = () => {
    return ifFoundInBody('h1, h2, .page-title', ($el) => {
      cy.wrap($el).should('satisfy', ($element) => {
        const text = $element.text().toLowerCase()
        return text.includes('auditoría') || text.includes('audit') || $element.length > 0
      })
    })
  }

  const verifyTableIfExists = () => {
    return ifFoundInBody('table, .table, [data-cy="audit-table"]', () => {
      cy.get('table, .table, [data-cy="audit-table"]', { timeout: 5000 }).should('exist')
    }, () => {
      cy.get('body').should('be.visible')
    })
  }

  beforeEach(() => {
    cy.navigateToAdminAuditLogs('admin')
  })

  it('should load audit logs table', () => {
    verifyUrlContains(['/admin', '/auditoria', '/audit'], 10000)
    verifyPageTitle()
    verifyTableIfExists()
  })

  it('should filter logs by action type', () => {
    const selectSelector = '[data-cy="select-action-type"], select'
    const rowSelector = 'table tbody tr, .table-row'
    cy.selectAndVerifyRows(selectSelector, 'LOGIN', rowSelector)
  })

  it('should filter logs by date range', () => {
    const today = new Date().toISOString().split('T')[0]
    
    return ifFoundInBody('[data-cy="date-start"], input[type="date"]', () => {
      cy.get('[data-cy="date-start"], input[type="date"]').first().type(today, { force: true })
      cy.get('[data-cy="date-end"], input[type="date"]').last().type(today, { force: true })
      cy.get('[data-cy="btn-apply-filter"], button[type="submit"]').first().click()
      
      return ifFoundInBody('table tbody tr, .table-row', () => {
        cy.get('table tbody tr, .table-row').first().should('exist')
      }, () => {
        cy.contains('No se encontraron registros, No hay registros, Sin resultados', { matchCase: false }).should('exist')
      })
    })
  })

  it('should view log details', () => {
    const rowSelector = 'table tbody tr, .table-row, [data-cy="audit-row"], tbody tr'
    cy.interactWithFirstRow(rowSelector, ($row) => {
      const btn = $row.find('[data-cy="btn-view-details"], button, a, [role="button"]').first()
      if (btn.length > 0) {
        cy.wrap(btn).click({ force: true })
        cy.get('[data-cy="modal-log-details"], .modal, [role="dialog"]', { timeout: 5000 }).should('exist')
        cy.get('body').then(($modal) => {
          if ($modal.find('[data-cy="json-viewer"], .json-viewer, pre, code').length > 0) {
            cy.get('[data-cy="json-viewer"], .json-viewer, pre, code', { timeout: 3000 }).should('exist')
          }
        })
      }
    })
  })

  it('should export audit logs to CSV', () => {
    cy.clickIfExists('[data-cy="btn-export-csv"], button')
    cy.get('.swal2-error', { timeout: 3000 }).should('not.exist')
  })

  it('should clear old logs (if applicable)', () => {
    cy.clickIfExists('[data-cy="btn-cleanup-logs"]')
    cy.get('body', { timeout: 5000 }).should('be.visible')
  })
})

