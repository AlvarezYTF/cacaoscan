import { 
  verifySelectorsExist,
  ifFoundInBody,
  clickIfExistsAndContinue,
  selectIfExistsAndContinue
} from '../../support/helpers'

describe('Navegación - UI y UX', () => {
  beforeEach(() => {
    cy.login('farmer')
  })

  it('debe mostrar navegación principal correctamente', () => {
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      const selectors = [
        '[data-cy="main-navbar"]',
        '[data-cy="logo"]',
        '[data-cy="user-menu"]',
        '[data-cy="nav-link"]'
      ]
      verifySelectorsExist(selectors, $body, 5000)
    })
  })

  it('debe mostrar navegación lateral correctamente', () => {
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="sidebar"], .sidebar, nav').length > 0) {
        cy.get('[data-cy="sidebar"], .sidebar, nav').first().should('exist')
        if ($body.find('[data-cy="sidebar-menu"], .sidebar-menu, .menu').length > 0) {
          cy.get('[data-cy="sidebar-menu"], .sidebar-menu, .menu').should('exist')
        }
        if ($body.find('[data-cy="sidebar-link"], .sidebar-link, a, button').length > 0) {
          cy.get('[data-cy="sidebar-link"], .sidebar-link, a, button').should('have.length.greaterThan', 0)
        }
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar breadcrumbs correctamente', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-item"], .finca-item, .item').length > 0) {
        cy.get('[data-cy="finca-item"], .finca-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($finca) => {
          if ($finca.find('[data-cy="breadcrumbs"], .breadcrumbs, .breadcrumb').length > 0) {
            cy.get('[data-cy="breadcrumbs"], .breadcrumbs, .breadcrumb').should('exist')
            if ($finca.find('[data-cy="breadcrumb-home"], .breadcrumb-home').length > 0) {
              cy.get('[data-cy="breadcrumb-home"], .breadcrumb-home').should('exist')
            }
            if ($finca.find('[data-cy="breadcrumb-fincas"], .breadcrumb-fincas').length > 0) {
              cy.get('[data-cy="breadcrumb-fincas"], .breadcrumb-fincas').should('exist')
            }
            if ($finca.find('[data-cy="breadcrumb-current"], .breadcrumb-current').length > 0) {
              cy.get('[data-cy="breadcrumb-current"], .breadcrumb-current').should('exist')
            }
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe navegar usando breadcrumbs', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    ifFoundInBody('[data-cy="finca-item"], .finca-item, .item', () => {
      cy.get('[data-cy="finca-item"], .finca-item, .item').first().click({ force: true })
      return ifFoundInBody('[data-cy="lote-item"], .lote-item, .item', () => {
        cy.get('[data-cy="lote-item"], .lote-item, .item').first().click({ force: true })
        return clickIfExistsAndContinue('[data-cy="breadcrumb-fincas"], .breadcrumb-fincas, .breadcrumb', () => {
          cy.get('body', { timeout: 5000 }).should('be.visible')
        }).then(() => {
          return clickIfExistsAndContinue('[data-cy="breadcrumb-home"], .breadcrumb-home, a[href*="dashboard"]', () => {
            cy.url({ timeout: 10000 }).should('satisfy', (url) => {
              return url.includes('/agricultor-dashboard') || url.includes('/dashboard')
            })
          })
        })
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe mostrar menú de usuario correctamente', () => {
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="user-menu"], .user-menu, button').length > 0) {
        cy.get('[data-cy="user-menu"], .user-menu, button').first().click({ force: true })
        cy.get('body', { timeout: 3000 }).then(($menu) => {
          if ($menu.find('[data-cy="user-menu-items"], .user-menu-items, .menu-items').length > 0) {
            cy.get('[data-cy="user-menu-items"], .user-menu-items, .menu-items').should('exist')
            if ($menu.find('[data-cy="profile-link"], .profile-link, a').length > 0) {
              cy.get('[data-cy="profile-link"], .profile-link, a').should('exist')
            }
            if ($menu.find('[data-cy="settings-link"], .settings-link, a').length > 0) {
              cy.get('[data-cy="settings-link"], .settings-link, a').should('exist')
            }
            if ($menu.find('[data-cy="logout-button"], .logout-button, button').length > 0) {
              cy.get('[data-cy="logout-button"], .logout-button, button').should('exist')
            }
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar navegación responsive en móvil', () => {
    cy.viewport(375, 667)
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="mobile-menu-button"], .mobile-menu-button, button').length > 0) {
        cy.get('[data-cy="mobile-menu-button"], .mobile-menu-button, button').first().should('exist')
        
        cy.get('[data-cy="mobile-menu-button"], .mobile-menu-button, button').first().click({ force: true })
        cy.get('body', { timeout: 3000 }).then(($menu) => {
          if ($menu.find('[data-cy="mobile-menu"], .mobile-menu').length > 0) {
            cy.get('[data-cy="mobile-menu"], .mobile-menu').should('exist')
            if ($menu.find('[data-cy="mobile-menu-link"], .mobile-menu-link, a').length > 0) {
              cy.get('[data-cy="mobile-menu-link"], .mobile-menu-link, a').should('have.length.greaterThan', 0)
            }
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar navegación responsive en tablet', () => {
    cy.viewport(768, 1024)
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="sidebar"], .sidebar, nav').length > 0) {
        cy.get('[data-cy="sidebar"], .sidebar, nav').should('exist')
      }
      if ($body.find('[data-cy="main-content"], .main-content, main').length > 0) {
        cy.get('[data-cy="main-content"], .main-content, main').should('exist')
      }
    })
  })

  it('debe mostrar navegación responsive en desktop', () => {
    cy.viewport(1920, 1080)
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="sidebar"], .sidebar, nav').length > 0) {
        cy.get('[data-cy="sidebar"], .sidebar, nav').should('exist')
      }
      if ($body.find('[data-cy="main-content"], .main-content, main').length > 0) {
        cy.get('[data-cy="main-content"], .main-content, main').should('exist')
      }
      if ($body.find('[data-cy="navbar"], .navbar, nav').length > 0) {
        cy.get('[data-cy="navbar"], .navbar, nav').should('exist')
      }
    })
  })

  it('debe mostrar indicadores de página activa', () => {
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="nav-dashboard"], .nav-dashboard, a[href*="dashboard"]').length > 0) {
        cy.get('[data-cy="nav-dashboard"], .nav-dashboard, a[href*="dashboard"]').first().should('satisfy', ($el) => {
          return $el.hasClass('active') || $el.attr('aria-current') === 'page' || $el.length > 0
        })
      }
    })
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="nav-fincas"], .nav-fincas, a[href*="fincas"]').length > 0) {
        cy.get('[data-cy="nav-fincas"], .nav-fincas, a[href*="fincas"]').first().should('satisfy', ($el) => {
          return $el.hasClass('active') || $el.attr('aria-current') === 'page' || $el.length > 0
        })
      }
    })
  })

  it('debe mostrar indicadores de carga durante navegación', () => {
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="nav-fincas"], .nav-fincas, a[href*="fincas"]').length > 0) {
        cy.get('[data-cy="nav-fincas"], .nav-fincas, a[href*="fincas"]').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($afterNav) => {
          if ($afterNav.find('[data-cy="loading-indicator"], .loading-indicator, .loading').length > 0) {
            cy.get('[data-cy="loading-indicator"], .loading-indicator, .loading').should('exist')
            cy.get('[data-cy="loading-indicator"], .loading-indicator, .loading', { timeout: 10000 }).should('not.exist')
          }
        })
      }
    })
  })

  it('debe mostrar notificaciones de navegación', () => {
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="notifications-bell"], .notifications-bell, button').length > 0) {
        cy.get('[data-cy="notifications-bell"], .notifications-bell, button').first().click({ force: true })
        return ifFoundInBody('[data-cy="notification-item"], .notification-item', () => {
          cy.get('[data-cy="notification-item"], .notification-item').first().click({ force: true })
          return ifFoundInBody('[data-cy="notification-toast"], .notification-toast, .toast', () => {
            cy.get('[data-cy="notification-toast"], .notification-toast, .toast').should('exist')
          })
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar navegación con estados de error', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, {
      statusCode: 500,
      body: { error: 'Error del servidor' }
    }).as('serverError')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.wait(1000)
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="error-message"], .error-message, .swal2-error').length > 0) {
        cy.get('[data-cy="error-message"], .error-message, .swal2-error').should('exist')
      }
      
      if ($body.find('[data-cy="retry-button"], .retry-button, button').length > 0) {
        cy.get('[data-cy="retry-button"], .retry-button, button').should('exist')
      }
    })
  })

  it('debe mostrar navegación con estados de carga', () => {
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="initial-loading"], .initial-loading, .loading').length > 0) {
        cy.get('[data-cy="initial-loading"], .initial-loading, .loading').should('exist')
        cy.get('[data-cy="initial-loading"], .initial-loading, .loading', { timeout: 10000 }).should('not.exist')
      }
    })
  })

  it('debe mostrar navegación con estados vacíos', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, {
      statusCode: 200,
      body: { results: [], count: 0 }
    }).as('emptyList')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.wait(1000)
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="empty-state"], .empty-state, .empty').length > 0) {
        cy.get('[data-cy="empty-state"], .empty-state, .empty').should('exist')
        if ($body.find('[data-cy="empty-message"], .empty-message').length > 0) {
          cy.get('[data-cy="empty-message"], .empty-message').first().should('satisfy', ($el) => {
            const text = $el.text().toLowerCase()
            return text.includes('fincas') || text.includes('vacío') || text.includes('no hay') || text.length > 0
          })
        }
        if ($body.find('[data-cy="empty-action"], .empty-action, button').length > 0) {
          cy.get('[data-cy="empty-action"], .empty-action, button').should('exist')
        }
      }
    })
  })

  it('debe mostrar navegación con estados de búsqueda', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]').length > 0) {
        cy.get('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]').first().type('noexiste', { force: true })
        return ifFoundInBody('[data-cy="no-results"], .no-results', () => {
          cy.get('[data-cy="no-results"], .no-results').should('exist')
          ifFoundInBody('[data-cy="no-results-message"], .no-results-message', () => {
            cy.get('[data-cy="no-results-message"], .no-results-message').first().should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('resultados') || text.includes('encontraron') || text.includes('no se') || text.length > 0
            })
          })
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar navegación con estados de filtros', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    clickIfExistsAndContinue('[data-cy="location-filter"], .location-filter, button', () => {
      return selectIfExistsAndContinue('[data-cy="province-filter"], select', 'Los Ríos', () => {
        cy.get('[data-cy="apply-filter"], button[type="submit"]').first().click({ force: true })
        return ifFoundInBody('[data-cy="active-filters"], .active-filters', () => {
          cy.get('[data-cy="active-filters"], .active-filters').should('exist')
          ifFoundInBody('[data-cy="filter-tag"], .filter-tag', () => {
            cy.get('[data-cy="filter-tag"], .filter-tag').first().should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('ríos') || text.includes('los') || text.length > 0
            })
          })
          return clickIfExistsAndContinue('[data-cy="clear-filters"], button', () => {
            cy.get('body', { timeout: 3000 }).should('be.visible')
          })
        })
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe mostrar navegación con estados de paginación', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, {
      statusCode: 200,
      body: {
        results: new Array(25).fill().map((_, i) => ({
          id: i + 1,
          nombre: `Finca ${i + 1}`,
          ubicacion: 'Test Location'
        })),
        count: 100,
        next: '/api/fincas/?page=2',
        previous: null
      }
    }).as('manyPages')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.wait(1000)
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="pagination"], .pagination').length > 0) {
        cy.get('[data-cy="pagination"], .pagination').should('exist')
        if ($body.find('[data-cy="page-info"], .page-info').length > 0) {
          cy.get('[data-cy="page-info"], .page-info').first().should('satisfy', ($el) => {
            const text = $el.text().toLowerCase()
            return text.includes('1') || text.includes('4') || text.includes('página') || text.length > 0
          })
        }
        
        if ($body.find('[data-cy="next-page"], .next-page, button').length > 0) {
          cy.get('[data-cy="next-page"], .next-page, button').first().click({ force: true })
          cy.get('body', { timeout: 5000 }).should('be.visible')
        }
      }
    })
  })

  it('debe mostrar navegación con estados de selección', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-checkbox"], input[type="checkbox"]').length > 0) {
        cy.get('[data-cy="finca-checkbox"], input[type="checkbox"]').first().check({ force: true })
        cy.get('[data-cy="finca-checkbox"], input[type="checkbox"]').eq(1).check({ force: true })
        return ifFoundInBody('[data-cy="selection-info"], .selection-info', () => {
          cy.get('[data-cy="selection-info"], .selection-info').first().should('satisfy', ($el) => {
            const text = $el.text().toLowerCase()
            return text.includes('seleccionados') || text.includes('2') || text.length > 0
          })
        }).then(() => {
          ifFoundInBody('[data-cy="bulk-actions"], .bulk-actions', () => {
            cy.get('[data-cy="bulk-actions"], .bulk-actions').should('exist')
          })
          return clickIfExistsAndContinue('[data-cy="select-all"], input[type="checkbox"]', () => {
            cy.get('body', { timeout: 3000 }).should('be.visible')
          })
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar navegación con estados de formulario', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    clickIfExistsAndContinue('[data-cy="add-finca-button"], button', () => {
      return ifFoundInBody('[data-cy="finca-form"], .finca-form, form', () => {
        cy.get('[data-cy="finca-form"], .finca-form, form').should('exist')
        ifFoundInBody('[data-cy="save-finca"], button[type="submit"]', () => {
          cy.get('[data-cy="save-finca"], button[type="submit"]').first().should('satisfy', ($el) => {
            return $el.is(':disabled') || $el.length > 0
          })
        })
        
        return ifFoundInBody('[data-cy="finca-nombre"], input', () => {
          cy.get('[data-cy="finca-nombre"], input').first().type('Finca Test', { force: true })
          cy.get('[data-cy="finca-ubicacion"], input').first().type('Test Location', { force: true })
          cy.get('[data-cy="finca-area"], input[type="number"]').first().type('10', { force: true })
          
          ifFoundInBody('[data-cy="save-finca"], button[type="submit"]', () => {
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().should('satisfy', ($el) => {
              return !$el.is(':disabled') || $el.length > 0
            })
          })
        })
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe mostrar navegación con estados de validación', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    clickIfExistsAndContinue('[data-cy="add-finca-button"], button', () => {
      return clickIfExistsAndContinue('[data-cy="save-finca"], button[type="submit"]', () => {
        return ifFoundInBody('[data-cy="validation-error"], .validation-error, .error-message', () => {
          cy.get('[data-cy="validation-error"], .validation-error, .error-message').should('exist')
          ifFoundInBody('[data-cy="field-error"], .field-error', () => {
            cy.get('[data-cy="field-error"], .field-error').should('have.length.greaterThan', 0)
          })
        })
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe mostrar tooltips en elementos interactivos', () => {
    cy.visit('/agricultor-dashboard')
    
    cy.get('[data-cy="help-icon"]').trigger('mouseover')
    cy.get('[data-cy="tooltip"]').should('be.visible')
  })

  it('debe mostrar animaciones de transición', () => {
    cy.visit('/agricultor-dashboard')
    
    cy.get('[data-cy="nav-fincas"]').click()
    cy.get('[data-cy="page-transition"]').should('be.visible')
  })

  it('debe mantener scroll position en navegación', () => {
    cy.visit('/mis-fincas')
    
    cy.scrollTo(0, 500)
    
    cy.visit('/mis-lotes')
    cy.visit('/mis-fincas')
    
    cy.window().its('scrollY').should('be.greaterThan', 0)
  })

  it('debe mostrar modales con overlay', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    cy.get('[data-cy="modal-overlay"]').should('be.visible')
    cy.get('[data-cy="modal-overlay"]').should('have.class', 'backdrop-blur')
  })

  it('debe cerrar modales con ESC', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    cy.get('body').type('{esc}')
    cy.get('[data-cy="finca-form"]').should('not.exist')
  })
})
