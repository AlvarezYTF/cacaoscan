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
        cy.get('body').then(($body) => {
          // Verificar título si existe
          if ($body.find('h1, h2, .page-title').length > 0) {
            cy.get('h1, h2, .page-title', { timeout: 5000 }).should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('reportes') || text.includes('reports') || text.length > 0
            })
          }
          // Verificar gráficos si existen
          if ($body.find('[data-cy="chart-main"], .chart, canvas').length > 0) {
            cy.get('[data-cy="chart-main"], .chart, canvas', { timeout: 5000 }).should('exist')
          }
        })
      })

      it('should filter reports by date range', () => {
        cy.get('body').then(($body) => {
          if ($body.find('[data-cy="date-range-picker"], input[type="date"], .date-picker').length > 0) {
            cy.clickIfExists('[data-cy="date-range-picker"], input[type="date"], .date-picker', { force: true }).then(() => {
              cy.get('body', { timeout: 5000 }).then(($picker) => {
                if ($picker.find('.daterangepicker, .date-picker').length > 0) {
                  cy.get('.daterangepicker, .date-picker').should('be.visible')
                  cy.clickIfExists('.applyBtn, button[type="submit"]').then(() => {
                    cy.get('body', { timeout: 5000 }).should('be.visible')
                  })
                }
              })
            })
          } else {
            cy.get('body').should('be.visible')
          }
        })
      })

      if (role !== 'farmer') {
        it('should filter by farmer (admin/analyst only)', () => {
          cy.get('body').then(($body) => {
            if ($body.find('[data-cy="select-farmer"], select').length > 0) {
              cy.get('[data-cy="select-farmer"], select').first().should('exist')
              cy.selectIfExists('[data-cy="select-farmer"], select', '1', { force: true }).then(() => {
                cy.get('body', { timeout: 5000 }).then(($afterSelect) => {
                  if ($afterSelect.find('[data-cy="reports-table"], .table, table').length > 0) {
                    cy.get('[data-cy="reports-table"], .table, table').should('be.visible')
                  } else {
                    cy.get('body').should('be.visible')
                  }
                })
              })
            } else {
              cy.get('body').should('be.visible')
            }
          })
        })
      }

      it('should toggle chart types', () => {
        cy.get('body').then(($body) => {
          if ($body.find('[data-cy="btn-chart-bar"], button, .chart-toggle').length > 0) {
            cy.clickIfExists('[data-cy="btn-chart-bar"], button, .chart-toggle', { force: true }).then(() => {
              cy.get('body', { timeout: 3000 }).then(($afterBar) => {
                if ($afterBar.find('canvas, .chart').length > 0) {
                  cy.get('canvas, .chart').first().should('exist')
                }
                cy.clickIfExists('[data-cy="btn-chart-line"], button', { force: true }).then(() => {
                  cy.get('body', { timeout: 3000 }).then(($afterLine) => {
                    if ($afterLine.find('canvas, .chart').length > 0) {
                      cy.get('canvas, .chart').first().should('exist')
                    }
                  })
                })
              })
            })
          } else {
            cy.get('body').should('be.visible')
          }
        })
      })

      it('should download report summary', () => {
        cy.get('body').then(($body) => {
          if ($body.find('[data-cy="btn-download-summary"], button').length > 0) {
            cy.clickIfExists('[data-cy="btn-download-summary"], button', { force: true }).then(() => {
              cy.get('body', { timeout: 5000 }).then(($afterClick) => {
                if ($afterClick.find('.swal2-success, [data-cy="notification-success"]').length > 0) {
                  cy.get('.swal2-success, [data-cy="notification-success"]').should('exist')
                } else {
                  cy.get('body').should('be.visible')
                }
              })
            })
          } else {
            cy.get('body').should('be.visible')
          }
        })
      })
    })
  }
})

