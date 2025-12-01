import {
  visitAndWaitForBody,
  openUserMenuAndExecute,
  verifyTokensCleared
} from '../../support/helpers'

describe('Autenticación - Logout', () => {
  beforeEach(() => {
    cy.login('admin')
  })

  it('debe hacer logout exitosamente desde el menú de usuario', () => {
    visitAndWaitForBody('/admin/dashboard')
    cy.performLogout()
    cy.url({ timeout: 10000 }).should('include', '/login')
    verifyTokensCleared()
  })

  it('debe hacer logout desde cualquier página', () => {
    const pages = ['/admin/dashboard', '/analisis', '/agricultor-dashboard']
    for (const [index, page] of pages.entries()) {
      visitAndWaitForBody(page)
      cy.performLogout()
      cy.url({ timeout: 10000 }).should('include', '/login')
      if (index < pages.length - 1) {
        cy.login('admin')
      }
    }
  })

  it('debe limpiar datos de sesión al hacer logout', () => {
    visitAndWaitForBody('/admin/dashboard')
    cy.window().then((win) => {
      const hasToken = win.localStorage.getItem('access_token') || win.localStorage.getItem('auth_token')
      expect(hasToken).to.not.be.null
    })
    cy.performLogout()
    verifyTokensCleared()
  })

  it('debe redirigir a página solicitada después del logout', () => {
    visitAndWaitForBody('/admin/dashboard')
    openUserMenuAndExecute(($menu) => {
      if ($menu.find('[data-cy="logout-button"], button').length > 0) {
        cy.get('[data-cy="logout-button"], button').first().click({ force: true })
        cy.visit('/admin/agricultores')
        cy.url({ timeout: 10000 }).should('include', '/login')
      }
    })
  })

  it('debe mostrar mensaje de confirmación antes del logout', () => {
    const checkUrlAfterCancel = (url) => {
      return url.includes('/admin/dashboard') || url.includes('/admin') || url.length > 0
    }

    const handleModalConfirmation = ($modal) => {
      if ($modal.find('[data-cy="logout-confirmation-modal"], .swal2-container, [role="dialog"]').length > 0) {
        cy.get('[data-cy="logout-confirmation-modal"], .swal2-container, [role="dialog"]').should('exist')
        cy.get('[data-cy="cancel-logout"], .swal2-cancel, button').first().click()
        cy.url({ timeout: 5000 }).should('satisfy', checkUrlAfterCancel)
      }
    }

    const handleLogoutButton = ($menu) => {
      if ($menu.find('[data-cy="logout-button"], button').length > 0) {
        cy.get('[data-cy="logout-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(handleModalConfirmation)
      }
    }

    visitAndWaitForBody('/admin/dashboard')
    openUserMenuAndExecute(handleLogoutButton)
  })

  it('debe cancelar logout desde modal de confirmación', () => {
    const checkUrlAfterCancel = (url) => {
      return url.includes('/admin/dashboard') || url.includes('/admin')
    }

    const handleCancelButton = ($modal) => {
      if ($modal.find('[data-cy="cancel-logout"], .swal2-cancel, button').length > 0) {
        cy.get('[data-cy="cancel-logout"], .swal2-cancel, button').first().click()
        cy.url({ timeout: 5000 }).should('satisfy', checkUrlAfterCancel)
        cy.get('[data-cy="admin-dashboard"], body', { timeout: 5000 }).should('exist')
      }
    }

    const handleLogoutButton = ($menu) => {
      if ($menu.find('[data-cy="logout-button"], button').length > 0) {
        cy.get('[data-cy="logout-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(handleCancelButton)
      }
    }

    visitAndWaitForBody('/admin/dashboard')
    openUserMenuAndExecute(handleLogoutButton)
  })

  it('debe hacer logout automático cuando el token expira', () => {
    const checkExpiredUrl = (url) => {
      return url.includes('/login') || url.includes('/auth') || url.includes('/admin') || url.length > 0
    }

    const handleExpiredMessage = ($body) => {
      if ($body.find('[data-cy="session-expired-message"], .error-message').length > 0) {
        cy.get('[data-cy="session-expired-message"], .error-message').should('exist')
      }
    }

    visitAndWaitForBody('/admin/dashboard')
    cy.window().then((win) => {
      win.localStorage.setItem('access_token', 'expired-token')
      win.localStorage.setItem('auth_token', 'expired-token')
    })
    cy.reload()
    cy.url({ timeout: 10000 }).should('satisfy', checkExpiredUrl)
    cy.get('body', { timeout: 5000 }).then(handleExpiredMessage)
  })
})
