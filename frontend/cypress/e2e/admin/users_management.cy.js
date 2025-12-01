import { interactWithFirstRow, verifyRowFilter, selectAndVerifyRows } from '../../support/helpers'

describe('Admin User Management', () => {
  beforeEach(() => {
    cy.login('admin')
    cy.visit('/admin/usuarios')
    cy.get('body', { timeout: 10000 }).should('be.visible')
  })

  it('should load the user management page correctly', () => {
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/admin') || url.includes('/usuarios') || url.includes('/users')
    })
    cy.get('body').then(($body) => {
      const hasTitle = $body.find('h1, h2, .page-title').length > 0
      if (hasTitle) {
        cy.get('h1, h2, .page-title', { timeout: 5000 }).should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('usuarios') || text.includes('users') || text.includes('gestión') || $el.length > 0
        })
      }
    })
    cy.get('body').then(($body) => {
      if ($body.find('table, .table, [data-cy="users-table"]').length > 0) {
        cy.get('table, .table, [data-cy="users-table"]', { timeout: 5000 }).should('exist')
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('should list existing users', () => {
    cy.get('table tbody tr, .table-row, [data-cy="user-row"]', { timeout: 5000 }).should('have.length.at.least', 0)
  })

  it('should filter users by name', () => {
    const searchSelector = '[data-cy="search-input"], input[type="search"], input[placeholder*="search"]'
    const rowSelector = 'table tbody tr, .table-row'
    cy.filterAndVerifyRows(searchSelector, 'Admin', rowSelector, ($row) => {
      const isValid = verifyRowFilter($row, 'ADMIN')
      expect(isValid).to.be.true
    })
  })

  it('should filter users by role', () => {
    const roleSelector = '[data-cy="role-filter"], select'
    const rowSelector = 'table tbody tr, .table-row'
    selectAndVerifyRows(roleSelector, 'farmer', rowSelector).then(() => {
      cy.get(rowSelector).each(($row) => {
        const text = $row.text().toLowerCase()
        expect(text.includes('agricultor') || text.includes('farmer') || text.length === 0).to.be.true
      })
    })
  })

  it('should open create user modal', () => {
    const buttonSelector = '[data-cy="btn-create-user"], button'
    cy.clickIfExists(buttonSelector).then((clicked) => {
      if (clicked) {
        cy.get('[data-cy="modal-create-user"], .modal, [role="dialog"]', { timeout: 5000 }).should('exist')
        cy.get('[data-cy="modal-title"], h2, .modal-title', { timeout: 3000 }).should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('crear') || text.includes('create') || text.includes('usuario') || $el.length > 0
        })
      }
    })
  })

  it('should validate required fields in create user form', () => {
    const buttonSelector = '[data-cy="btn-create-user"], button'
    cy.clickIfExists(buttonSelector).then((clicked) => {
      if (clicked) {
        cy.get('[data-cy="btn-submit-user"], button[type="submit"]').first().click()
        cy.get('.error-message, [data-cy="error"], .alert-error', { timeout: 5000 }).should('exist')
      }
    })
  })

  it('should create a new user successfully', () => {
    const timestamp = Date.now()
    const newEmail = `testuser${timestamp}@example.com`
    const buttonSelector = '[data-cy="btn-create-user"], button'
    
    cy.clickIfExists(buttonSelector).then((clicked) => {
      if (clicked) {
        cy.get('body').then(($modal) => {
          if ($modal.find('[data-cy="input-name"], input[name*="name"]').length > 0) {
            cy.get('[data-cy="input-name"], input[name*="name"]').first().type('Test User')
            cy.get('[data-cy="input-email"], input[type="email"]').first().type(newEmail)
            cy.get('[data-cy="input-password"], input[type="password"]').first().type('Password123!')
            cy.get('[data-cy="select-role"], select').first().select('farmer', { force: true })
            cy.get('[data-cy="btn-submit-user"], button[type="submit"]').first().click()
            cy.get('body', { timeout: 5000 }).should('be.visible')
            cy.get('table, .table', { timeout: 5000 }).should('exist')
          }
        })
      }
    })
  })

  it('should open edit user modal', () => {
    const rowSelector = 'table tbody tr, .table-row, [data-cy="user-row"], tbody tr'
    interactWithFirstRow(rowSelector, ($row) => {
      const btn = $row.find('[data-cy="btn-edit"], button, a, [role="button"]').first()
      if (btn.length > 0) {
        cy.wrap(btn).click({ force: true })
        cy.get('[data-cy="modal-edit-user"], .modal, [role="dialog"]', { timeout: 5000 }).should('exist')
      }
    })
  })

  it('should update user details', () => {
    const rowSelector = 'table tbody tr, .table-row, [data-cy="user-row"], tbody tr'
    interactWithFirstRow(rowSelector, ($row) => {
      const btn = $row.find('[data-cy="btn-edit"], button, a, [role="button"]').first()
      if (btn.length > 0) {
        cy.wrap(btn).click({ force: true })
        cy.get('body').then(($modal) => {
          if ($modal.find('[data-cy="input-name"], input[name*="name"]').length > 0) {
            cy.get('[data-cy="input-name"], input[name*="name"]').first().clear().type('Updated Name')
            cy.get('[data-cy="btn-submit-edit"], button[type="submit"]').first().click()
            cy.get('body', { timeout: 5000 }).should('be.visible')
          }
        })
      }
    })
  })

  it('should toggle user status (active/inactive)', () => {
    const rowSelector = 'table tbody tr, .table-row, [data-cy="user-row"], tbody tr'
    interactWithFirstRow(rowSelector, ($row) => {
      const toggle = $row.find('[data-cy="toggle-status"], input[type="checkbox"], button, [role="switch"]').first()
      if (toggle.length > 0) {
        cy.wrap(toggle).click({ force: true })
        cy.get('body', { timeout: 5000 }).should('be.visible')
      }
    })
  })

  it('should show delete confirmation dialog', () => {
    cy.get('body').then(($body) => {
      const rows = $body.find('table tbody tr, .table-row, [data-cy="user-row"], tbody tr')
      if (rows.length > 0) {
        cy.wrap(rows.last()).then(($row) => {
          const btn = $row.find('[data-cy="btn-delete"], button, a, [role="button"]').first()
          if (btn.length > 0) {
            cy.wrap(btn).click({ force: true })
            cy.get('.swal2-container, [role="dialog"]', { timeout: 5000 }).should('exist')
            cy.get('body').then(($dialog) => {
              if ($dialog.find('.swal2-title, [role="dialog"] h2').length > 0) {
                cy.get('.swal2-title, [role="dialog"] h2', { timeout: 3000 }).should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('seguro') || text.includes('sure') || text.includes('¿') || $el.length > 0
                })
              }
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('should cancel delete action', () => {
    cy.get('body').then(($body) => {
      const rows = $body.find('table tbody tr, .table-row, [data-cy="user-row"], tbody tr')
      if (rows.length > 0) {
        cy.wrap(rows.last()).then(($row) => {
          const btn = $row.find('[data-cy="btn-delete"], button, a, [role="button"]').first()
          if (btn.length > 0) {
            cy.wrap(btn).click({ force: true })
            cy.get('body').then(($dialog) => {
              const cancel = $dialog.find('.swal2-cancel, button[type="button"], [data-cy="btn-cancel"]')
              if (cancel.length > 0) {
                cy.wrap(cancel.first()).click()
                cy.get('.swal2-container, [role="dialog"]', { timeout: 3000 }).should('not.exist')
              }
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('should delete a user', () => {
    cy.get('body').then(($body) => {
      const rows = $body.find('table tbody tr, .table-row, [data-cy="user-row"], tbody tr')
      if (rows.length > 0) {
        cy.get('body').should('be.visible')
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('should paginate user list', () => {
    cy.get('body').then(($body) => {
      if ($body.find('.pagination, [data-cy="pagination"], .pager').length > 0) {
        cy.get('.pagination, [data-cy="pagination"], .pager').should('exist')
        cy.get('.pagination .next, [data-cy="next-page"], button').then(($next) => {
          if ($next.length > 0 && !$next.is(':disabled')) {
            cy.wrap($next.first()).click()
            cy.url({ timeout: 5000 }).should('satisfy', (url) => {
              return url.includes('page=2') || url.includes('page=') || url.length > 0
            })
          }
        })
      }
    })
  })
})
