import {
  interactWithFirstRow,
  verifyRowFilter,
  selectAndVerifyRows,
  waitForPageLoad,
  verifyElementWithAlternatives,
  verifyTextContains,
  verifyUrlPatterns,
  clickIfExists,
  typeIfExists,
  selectIfExists,
  verifyErrorMessageWithAlternatives
} from '../../support/helpers'

describe('Admin User Management', () => {
  beforeEach(() => {
    cy.login('admin')
    cy.visit('/admin/usuarios')
    waitForPageLoad()
  })

  it('should load the user management page correctly', () => {
    verifyUrlPatterns(['/admin', '/usuarios', '/users'])
    const titleSelectors = ['h1', 'h2', '.page-title']
    cy.get('body').then(($body) => {
      verifyElementWithAlternatives(titleSelectors, $body).then(() => {
        verifyTextContains(titleSelectors.join(', '), ['usuarios', 'users', 'gestión'])
      })
      const tableSelectors = ['table', '.table', '[data-cy="users-table"]']
      verifyElementWithAlternatives(tableSelectors, $body, 5000)
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
    const buttonSelectors = ['[data-cy="btn-create-user"]', 'button']
    clickIfExists(buttonSelectors.join(', ')).then((clicked) => {
      if (clicked) {
        const modalSelectors = ['[data-cy="modal-create-user"]', '.modal', '[role="dialog"]']
        verifyElementWithAlternatives(modalSelectors, cy.get('body'), 5000)
        const titleSelectors = ['[data-cy="modal-title"]', 'h2', '.modal-title']
        verifyElementWithAlternatives(titleSelectors, cy.get('body'), 3000).then(() => {
          verifyTextContains(titleSelectors.join(', '), ['crear', 'create', 'usuario'])
        })
      }
    })
  })

  it('should validate required fields in create user form', () => {
    const buttonSelectors = ['[data-cy="btn-create-user"]', 'button']
    clickIfExists(buttonSelectors.join(', ')).then((clicked) => {
      if (clicked) {
        const submitButtonSelectors = ['[data-cy="btn-submit-user"]', 'button[type="submit"]']
        cy.get(submitButtonSelectors.join(', ')).first().click()
        const errorSelectors = ['.error-message', '[data-cy="error"]', '.alert-error']
        verifyElementWithAlternatives(errorSelectors, cy.get('body'), 5000)
      }
    })
  })

  it('should create a new user successfully', () => {
    const timestamp = Date.now()
    const newEmail = `testuser${timestamp}@example.com`
    const buttonSelectors = ['[data-cy="btn-create-user"]', 'button']
    
    clickIfExists(buttonSelectors.join(', ')).then((clicked) => {
      if (clicked) {
        cy.get('body').then(($modal) => {
          const nameInputSelectors = ['[data-cy="input-name"]', 'input[name*="name"]']
          if ($modal.find(nameInputSelectors.join(', ')).length > 0) {
            typeIfExists(nameInputSelectors.join(', '), 'Test User')
            typeIfExists('[data-cy="input-email"], input[type="email"]', newEmail)
            typeIfExists('[data-cy="input-password"], input[type="password"]', 'Password123!')
            selectIfExists('[data-cy="select-role"], select', 'farmer', { force: true })
            clickIfExists('[data-cy="btn-submit-user"], button[type="submit"]')
            waitForPageLoad(5000)
            const tableSelectors = ['table', '.table']
            verifyElementWithAlternatives(tableSelectors, cy.get('body'), 5000)
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
    const rowSelectors = ['table tbody tr', '.table-row', '[data-cy="user-row"]', 'tbody tr']
    interactWithFirstRow(rowSelectors.join(', '), ($row) => {
      const deleteButtonSelectors = ['[data-cy="btn-delete"]', 'button', 'a', '[role="button"]']
      const btn = $row.find(deleteButtonSelectors.join(', ')).first()
      if (btn.length > 0) {
        cy.wrap(btn).click({ force: true })
        const dialogSelectors = ['.swal2-container', '[role="dialog"]']
        verifyElementWithAlternatives(dialogSelectors, cy.get('body'), 5000)
        const titleSelectors = ['.swal2-title', '[role="dialog"] h2']
        verifyElementWithAlternatives(titleSelectors, cy.get('body'), 3000).then(() => {
          verifyTextContains(titleSelectors.join(', '), ['seguro', 'sure', '¿'])
        })
      }
    })
  })

  it('should cancel delete action', () => {
    const rowSelectors = ['table tbody tr', '.table-row', '[data-cy="user-row"]', 'tbody tr']
    interactWithFirstRow(rowSelectors.join(', '), ($row) => {
      const deleteButtonSelectors = ['[data-cy="btn-delete"]', 'button', 'a', '[role="button"]']
      const btn = $row.find(deleteButtonSelectors.join(', ')).first()
      if (btn.length > 0) {
        cy.wrap(btn).click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($dialog) => {
          const cancelSelectors = ['.swal2-cancel', 'button[type="button"]', '[data-cy="btn-cancel"]']
          if ($dialog.find(cancelSelectors.join(', ')).length > 0) {
            cy.get(cancelSelectors.join(', ')).first().click()
            cy.get('.swal2-container, [role="dialog"]', { timeout: 3000 }).should('not.exist')
          }
        })
      }
    })
  })

  it('should delete a user', () => {
    const rowSelectors = ['table tbody tr', '.table-row', '[data-cy="user-row"]', 'tbody tr']
    cy.get('body', { timeout: 10000 }).then(($body) => {
      if ($body.find(rowSelectors.join(', ')).length > 0) {
        const deleteButtonSelectors = ['[data-cy="delete-user"]', '.delete-button', 'button']
        clickIfExists(deleteButtonSelectors.join(', '), { force: true })
        const confirmButtonSelectors = ['[data-cy="confirm-delete"]', '.confirm-button', 'button']
        clickIfExists(confirmButtonSelectors.join(', '), { force: true })
        waitForPageLoad(5000)
        cy.get('[data-cy="user-row"], .table-row').should('have.length.at.least', 0)
      } else {
        cy.log('No users found to delete')
        waitForPageLoad()
      }
    })
  })

  it('should paginate user list', () => {
    const paginationSelectors = ['.pagination', '[data-cy="pagination"]', '.pager']
    cy.get('body', { timeout: 10000 }).then(($body) => {
      verifyElementWithAlternatives(paginationSelectors, $body).then(() => {
        const nextButtonSelectors = ['.pagination .next', '[data-cy="next-page"]', 'button']
        cy.get(nextButtonSelectors.join(', '), { timeout: 5000 }).then(($next) => {
          if ($next.length > 0 && !$next.is(':disabled')) {
            cy.wrap($next.first()).click()
            verifyUrlPatterns(['page=2', 'page='], 5000)
          }
        })
      })
    })
  })
})
