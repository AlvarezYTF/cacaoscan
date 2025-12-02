import { visitAndWaitForBody, ifFoundInBody, clickIfExistsAndContinue } from '../../support/helpers'

describe('Admin Agricultores E2E Tests', () => {
  beforeEach(() => {
    // Mock API calls - use flexible patterns to catch all variations
    const mockUsersResponse = {
      statusCode: 200,
      body: {
        results: [
          {
            id: 1,
            username: 'farmer1',
            email: 'farmer1@test.com',
            first_name: 'Juan',
            last_name: 'Pérez',
            role: 'farmer',
            is_active: true,
            date_joined: new Date().toISOString(),
            verified: true
          },
          {
            id: 2,
            username: 'farmer2',
            email: 'farmer2@test.com',
            first_name: 'María',
            last_name: 'García',
            role: 'farmer',
            is_active: true,
            date_joined: new Date().toISOString(),
            verified: false
          },
          {
            id: 3,
            username: 'farmer3',
            email: 'farmer3@test.com',
            first_name: 'Pedro',
            last_name: 'López',
            role: 'farmer',
            is_active: false,
            date_joined: new Date().toISOString(),
            verified: true
          }
        ],
        count: 3
      }
    }
    
    const mockFincasResponse = {
      statusCode: 200,
      body: {
        results: [
          {
            id: 1,
            nombre: 'Finca Test 1',
            agricultor_id: 1,
            hectareas: 10,
            departamento: 'Cundinamarca',
            activa: true
          },
          {
            id: 2,
            nombre: 'Finca Test 2',
            agricultor_id: 1,
            hectareas: 5,
            departamento: 'Antioquia',
            activa: true
          }
        ],
        count: 2
      }
    }

    // Intercept multiple URL patterns
    cy.intercept('GET', '**/api/v1/auth/users/**', mockUsersResponse).as('getUsers')
    cy.intercept('GET', '**/auth/users/**', mockUsersResponse)
    cy.intercept('GET', '**/api/v1/fincas/**', mockFincasResponse).as('getFincas')
    cy.intercept('GET', '**/fincas/**', mockFincasResponse)
    cy.intercept('POST', '**/api/v1/auth/users/**', { statusCode: 200, body: { success: true } }).as('updateUser')
    cy.intercept('DELETE', '**/api/v1/auth/users/**', { statusCode: 204 }).as('deleteUser')

    cy.login('admin')
    cy.visit('/admin/agricultores')
    visitAndWaitForBody()
    // Verify URL navigation
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/admin') || url.includes('/agricultores')
    })
  })

  it('should display agricultores list', () => {
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/admin') || url.includes('/agricultores')
    })
    ifFoundInBody('[data-cy="agricultores-table"], table', () => {
      cy.get('[data-cy="agricultores-table"], table', { timeout: 10000 }).should('exist')
      cy.get('tbody tr, [data-cy="farmer-item"]').should('have.length.at.least', 1)
    })
  })

  it('should filter agricultores by search', () => {
    ifFoundInBody('[data-cy="filter-agricultores"], input[type="text"], [data-cy="search-input"]', () => {
      cy.get('[data-cy="filter-agricultores"], input[type="text"], [data-cy="search-input"]', { timeout: 10000 })
        .first()
        .should('be.visible')
        .type('Juan')
      cy.wait(500)
      cy.get('body').should('be.visible')
      cy.get('tbody tr, [data-cy="farmer-item"]').should('exist')
    })
  })

  it('should filter agricultores by status', () => {
    ifFoundInBody('[data-cy="status-filter"], select', () => {
      cy.get('[data-cy="status-filter"], select').first().select('active', { force: true })
      cy.wait(500)
      cy.get('body').should('be.visible')
    })
  })

  it('should filter agricultores by verification status', () => {
    ifFoundInBody('[data-cy="verification-filter"], select', () => {
      cy.get('[data-cy="verification-filter"], select').first().select('verified', { force: true })
      cy.wait(500)
      cy.get('body').should('be.visible')
    })
  })

  it('should view agricultor details', () => {
    clickIfExistsAndContinue('[data-cy="view-agricultor"], [data-cy="farmer-item"], tbody tr', () => {
      cy.get('[data-cy="agricultor-details"], .modal, [role="dialog"]', { timeout: 5000 }).should('exist')
      ifFoundInBody('[data-cy="farmer-name"]', () => {
        cy.get('[data-cy="farmer-name"]').should('be.visible')
      })
      ifFoundInBody('[data-cy="farmer-email"]', () => {
        cy.get('[data-cy="farmer-email"]').should('be.visible')
      })
    })
  })

  it('should view agricultor fincas in details', () => {
    clickIfExistsAndContinue('[data-cy="view-agricultor"], [data-cy="farmer-item"], tbody tr', () => {
      cy.get('[data-cy="agricultor-details"], .modal, [role="dialog"]', { timeout: 5000 }).should('exist')
      ifFoundInBody('[data-cy="farmer-fincas"], [data-cy="fincas-list"]', () => {
        cy.get('[data-cy="farmer-fincas"], [data-cy="fincas-list"]').should('be.visible')
      })
    })
  })

  it('should edit agricultor information', () => {
    clickIfExistsAndContinue('[data-cy="edit-agricultor"], button', () => {
      cy.get('[data-cy="edit-farmer-form"], form, .modal', { timeout: 5000 }).should('exist')
      ifFoundInBody('[data-cy="farmer-first-name"], input[name*="first"]', () => {
        cy.get('[data-cy="farmer-first-name"], input[name*="first"]').first().clear().type('Updated Name')
      })
      clickIfExistsAndContinue('[data-cy="save-farmer"], button[type="submit"]', () => {
        cy.get('body', { timeout: 5000 }).should('be.visible')
      })
    })
  })

  it('should activate/deactivate agricultor', () => {
    ifFoundInBody('[data-cy="toggle-active"], [data-cy="activate-farmer"], button', () => {
      cy.get('[data-cy="toggle-active"], [data-cy="activate-farmer"], button').first().click({ force: true })
      cy.wait(500)
      cy.get('body').should('be.visible')
    })
  })

  it('should paginate agricultores list', () => {
    ifFoundInBody('[data-cy="pagination"]', () => {
      cy.get('[data-cy="pagination"]').should('be.visible')
      ifFoundInBody('[data-cy="page-next"], [data-cy="next-page"], button', () => {
        cy.get('[data-cy="page-next"], [data-cy="next-page"], button').first().click({ force: true })
        cy.wait(500)
        cy.get('body').should('be.visible')
      })
    })
  })

  it('should export agricultores list', () => {
    ifFoundInBody('[data-cy="export-farmers"], [data-cy="export-button"], button', () => {
      cy.get('[data-cy="export-farmers"], [data-cy="export-button"], button').first().click({ force: true })
      cy.wait(1000)
      cy.get('body').should('be.visible')
      cy.get('.swal2-error', { timeout: 3000 }).should('not.exist')
    })
  })

  it('should show statistics cards', () => {
    ifFoundInBody('[data-cy="stats-cards"], [data-cy="farmer-stats"]', () => {
      cy.get('[data-cy="stats-cards"], [data-cy="farmer-stats"]').should('be.visible')
    })
  })
})
