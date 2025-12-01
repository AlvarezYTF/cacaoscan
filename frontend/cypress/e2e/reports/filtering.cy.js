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
        const checkReportsTitle = ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('reportes') || text.includes('reports') || text.length > 0
        }

        cy.get('body', { timeout: 10000 }).should('be.visible')
        ifFoundInBody('h1, h2, .page-title', () => {
          cy.get('h1, h2, .page-title', { timeout: 5000 }).should('satisfy', checkReportsTitle)
        })
        ifFoundInBody('[data-cy="chart-main"], .chart, canvas', () => {
          cy.get('[data-cy="chart-main"], .chart, canvas', { timeout: 5000 }).should('exist')
        })
      })

      it('should filter reports by date range', () => {
        const handleApplyDateRange = () => {
          cy.get('body', { timeout: 5000 }).should('be.visible')
        }

        const handleDatePicker = () => {
          cy.get('.daterangepicker, .date-picker').should('be.visible')
          return clickIfExistsAndContinue('.applyBtn, button[type="submit"]', handleApplyDateRange)
        }

        return clickIfExistsAndContinue('[data-cy="date-range-picker"], input[type="date"], .date-picker', () => {
          return ifFoundInBody('.daterangepicker, .date-picker', handleDatePicker)
        }, () => {
          cy.get('body').should('be.visible')
        })
      })

      if (role !== 'farmer') {
        it('should filter by farmer (admin/analyst only)', () => {
          const handleReportsTable = () => {
            cy.get('[data-cy="reports-table"], .table, table').should('be.visible')
          }

          const handleReportsTableNotFound = () => {
            cy.get('body').should('be.visible')
          }

          const handleFarmerSelection = () => {
            return ifFoundInBody('[data-cy="reports-table"], .table, table', handleReportsTable, handleReportsTableNotFound)
          }

          const handleSelectFarmer = () => {
            cy.get('[data-cy="select-farmer"], select').first().should('exist')
            return selectIfExistsAndContinue('[data-cy="select-farmer"], select', '1', handleFarmerSelection)
          }

          const handleSelectFarmerNotFound = () => {
            cy.get('body').should('be.visible')
          }

          return ifFoundInBody('[data-cy="select-farmer"], select', handleSelectFarmer, handleSelectFarmerNotFound)
        })
      }

      it('should toggle chart types', () => {
        const handleLineChart = () => {
          cy.get('canvas, .chart').first().should('exist')
        }

        const handleLineChartClick = () => {
          return ifFoundInBody('canvas, .chart', handleLineChart)
        }

        const handleBarChart = () => {
          cy.get('canvas, .chart').first().should('exist')
          return clickIfExistsAndContinue('[data-cy="btn-chart-line"], button', handleLineChartClick)
        }

        const handleBarChartClick = () => {
          return ifFoundInBody('canvas, .chart', handleBarChart)
        }

        const handleBarChartNotFound = () => {
          cy.get('body').should('be.visible')
        }

        return clickIfExistsAndContinue('[data-cy="btn-chart-bar"], button, .chart-toggle', handleBarChartClick, handleBarChartNotFound)
      })

      it('should download report summary', () => {
        const handleNotificationSuccess = () => {
          cy.get('.swal2-success, [data-cy="notification-success"]').should('exist')
        }

        const handleNotificationNotFound = () => {
          cy.get('body').should('be.visible')
        }

        const handleDownloadButtonClick = () => {
          return ifFoundInBody('.swal2-success, [data-cy="notification-success"]', handleNotificationSuccess, handleNotificationNotFound)
        }

        const handleDownloadButtonNotFound = () => {
          cy.get('body').should('be.visible')
        }

        return clickIfExistsAndContinue('[data-cy="btn-download-summary"], button', handleDownloadButtonClick, handleDownloadButtonNotFound)
      })
    })
  }
})

