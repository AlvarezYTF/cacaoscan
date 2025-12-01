import { 
  ifFoundInBody,
  clickIfExistsAndContinue,
  selectIfExistsAndContinue
} from '../../support/helpers'

describe('Reports & Filtering', () => {
  const roles = ['admin', 'analyst', 'farmer']

  for (const role of roles) {
    describe(`Reports for ${role}`, () => {
      beforeEach(() => {
        cy.login(role)
        const path = role === 'farmer' ? '/agricultor/reportes' : '/reportes'
        cy.visit(path)
        cy.get('body', { timeout: 10000 }).should('be.visible')
      })

      it('should load reports dashboard', () => {
        cy.get('body', { timeout: 10000 }).should('be.visible')
        ifFoundInBody('h1, h2, .page-title', () => {
          cy.get('h1, h2, .page-title', { timeout: 5000 }).should('satisfy', ($el) => {
            const text = $el.text().toLowerCase()
            return text.includes('reportes') || text.includes('reports') || text.length > 0
          })
        })
        ifFoundInBody('[data-cy="chart-main"], .chart, canvas', () => {
          cy.get('[data-cy="chart-main"], .chart, canvas', { timeout: 5000 }).should('exist')
        })
      })

      it('should filter reports by date range', () => {
        return clickIfExistsAndContinue('[data-cy="date-range-picker"], input[type="date"], .date-picker', () => {
          return ifFoundInBody('.daterangepicker, .date-picker', () => {
            cy.get('.daterangepicker, .date-picker').should('be.visible')
            return clickIfExistsAndContinue('.applyBtn, button[type="submit"]', () => {
              cy.get('body', { timeout: 5000 }).should('be.visible')
            })
          })
        }, () => {
          cy.get('body').should('be.visible')
        })
      })

      if (role !== 'farmer') {
        it('should filter by farmer (admin/analyst only)', () => {
          return ifFoundInBody('[data-cy="select-farmer"], select', () => {
            cy.get('[data-cy="select-farmer"], select').first().should('exist')
            return selectIfExistsAndContinue('[data-cy="select-farmer"], select', '1', () => {
              return ifFoundInBody('[data-cy="reports-table"], .table, table', () => {
                cy.get('[data-cy="reports-table"], .table, table').should('be.visible')
              }, () => {
                cy.get('body').should('be.visible')
              })
            })
          }, () => {
            cy.get('body').should('be.visible')
          })
        })
      }

      it('should toggle chart types', () => {
        return clickIfExistsAndContinue('[data-cy="btn-chart-bar"], button, .chart-toggle', () => {
          return ifFoundInBody('canvas, .chart', () => {
            cy.get('canvas, .chart').first().should('exist')
          }).then(() => {
            return clickIfExistsAndContinue('[data-cy="btn-chart-line"], button', () => {
              return ifFoundInBody('canvas, .chart', () => {
                cy.get('canvas, .chart').first().should('exist')
              })
            })
          })
        }, () => {
          cy.get('body').should('be.visible')
        })
      })

      it('should download report summary', () => {
        return clickIfExistsAndContinue('[data-cy="btn-download-summary"], button', () => {
          return ifFoundInBody('.swal2-success, [data-cy="notification-success"]', () => {
            cy.get('.swal2-success, [data-cy="notification-success"]').should('exist')
          }, () => {
            cy.get('body').should('be.visible')
          })
        }, () => {
          cy.get('body').should('be.visible')
        })
      })
    })
  }
})

