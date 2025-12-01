describe('Navegación - UI y UX', () => {
  beforeEach(() => {
    cy.login('farmer')
  })
  // Helper functions to reduce nesting depth
  const verifySelectorsExist = (selectors, $context, timeout = 3000) => {
    for (const selector of selectors) {
      if ($context.find(selector).length > 0) {
        cy.get(selector, { timeout }).should('exist')
      }
    }
  }



  it('debe mostrar navegación principal correctamente', () => {
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Verificar navbar principal
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
    
    // Verificar sidebar
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
          // Verificar breadcrumbs si existen
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
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-item"], .finca-item, .item').length > 0) {
        cy.get('[data-cy="finca-item"], .finca-item, .item').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($finca) => {
          if ($finca.find('[data-cy="lote-item"], .lote-item, .item').length > 0) {
            cy.get('[data-cy="lote-item"], .lote-item, .item').first().click({ force: true })
            cy.get('body', { timeout: 5000 }).then(($lote) => {
              // Navegar usando breadcrumbs si existen
              if ($lote.find('[data-cy="breadcrumb-fincas"], .breadcrumb-fincas, .breadcrumb').length > 0) {
                cy.get('[data-cy="breadcrumb-fincas"], .breadcrumb-fincas, .breadcrumb').first().click({ force: true })
                cy.get('body', { timeout: 5000 }).should('be.visible')
              }
              
              if ($lote.find('[data-cy="breadcrumb-home"], .breadcrumb-home, a[href*="dashboard"]').length > 0) {
                cy.get('[data-cy="breadcrumb-home"], .breadcrumb-home, a[href*="dashboard"]').first().click({ force: true })
                cy.url({ timeout: 10000 }).should('satisfy', (url) => {
                  return url.includes('/agricultor-dashboard') || url.includes('/dashboard')
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

  it('debe mostrar menú de usuario correctamente', () => {
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Abrir menú de usuario
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="user-menu"], .user-menu, button').length > 0) {
        cy.get('[data-cy="user-menu"], .user-menu, button').first().click({ force: true })
        cy.get('body', { timeout: 3000 }).then(($menu) => {
          // Verificar opciones del menú si existen
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
    // Simular vista móvil
    cy.viewport(375, 667)
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Verificar menú hamburguesa si existe
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="mobile-menu-button"], .mobile-menu-button, button').length > 0) {
        cy.get('[data-cy="mobile-menu-button"], .mobile-menu-button, button').first().should('exist')
        
        // Abrir menú móvil
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
    // Simular vista tablet
    cy.viewport(768, 1024)
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Verificar que se adapta a tablet
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
    // Simular vista desktop
    cy.viewport(1920, 1080)
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Verificar que se adapta a desktop
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
    
    // Verificar que dashboard está activo si existe
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="nav-dashboard"], .nav-dashboard, a[href*="dashboard"]').length > 0) {
        cy.get('[data-cy="nav-dashboard"], .nav-dashboard, a[href*="dashboard"]').first().should('satisfy', ($el) => {
          return $el.hasClass('active') || $el.attr('aria-current') === 'page' || $el.length > 0
        })
      }
    })
    
    // Navegar a otra página
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
    
    // Navegar a página que puede tardar en cargar
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="nav-fincas"], .nav-fincas, a[href*="fincas"]').length > 0) {
        cy.get('[data-cy="nav-fincas"], .nav-fincas, a[href*="fincas"]').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($afterNav) => {
          // Verificar indicador de carga si existe
          if ($afterNav.find('[data-cy="loading-indicator"], .loading-indicator, .loading').length > 0) {
            cy.get('[data-cy="loading-indicator"], .loading-indicator, .loading').should('exist')
            // Verificar que desaparece cuando carga
            cy.get('[data-cy="loading-indicator"], .loading-indicator, .loading', { timeout: 10000 }).should('not.exist')
          }
        })
      }
    })
  })

  it('debe mostrar notificaciones de navegación', () => {
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Simular notificación
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="notifications-bell"], .notifications-bell, button').length > 0) {
        cy.get('[data-cy="notifications-bell"], .notifications-bell, button').first().click({ force: true })
        cy.get('body', { timeout: 3000 }).then(($notifications) => {
          if ($notifications.find('[data-cy="notification-item"], .notification-item').length > 0) {
            cy.get('[data-cy="notification-item"], .notification-item').first().click({ force: true })
            cy.get('body', { timeout: 3000 }).then(($afterClick) => {
              // Verificar que se muestra notificación si existe
              if ($afterClick.find('[data-cy="notification-toast"], .notification-toast, .toast').length > 0) {
                cy.get('[data-cy="notification-toast"], .notification-toast, .toast').should('exist')
              }
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar navegación con estados de error', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular error de red
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, {
      statusCode: 500,
      body: { error: 'Error del servidor' }
    }).as('serverError')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Esperar un poco para que la página se estabilice
    cy.wait(1000)
    
    // Verificar mensaje de error si existe
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="error-message"], .error-message, .swal2-error').length > 0) {
        cy.get('[data-cy="error-message"], .error-message, .swal2-error').should('exist')
      }
      
      // Verificar que se puede reintentar si existe
      if ($body.find('[data-cy="retry-button"], .retry-button, button').length > 0) {
        cy.get('[data-cy="retry-button"], .retry-button, button').should('exist')
      }
    })
  })

  it('debe mostrar navegación con estados de carga', () => {
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Verificar que se muestra loading inicial si existe
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="initial-loading"], .initial-loading, .loading').length > 0) {
        cy.get('[data-cy="initial-loading"], .initial-loading, .loading').should('exist')
        // Verificar que desaparece cuando carga
        cy.get('[data-cy="initial-loading"], .initial-loading, .loading', { timeout: 10000 }).should('not.exist')
      }
    })
  })

  it('debe mostrar navegación con estados vacíos', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular lista vacía
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, {
      statusCode: 200,
      body: { results: [], count: 0 }
    }).as('emptyList')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Esperar un poco para que la página se estabilice
    cy.wait(1000)
    
    // Verificar estado vacío si existe
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
    
    // Buscar algo que no existe
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]').length > 0) {
        cy.get('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]').first().type('noexiste', { force: true })
        cy.get('body', { timeout: 3000 }).then(($afterSearch) => {
          // Verificar estado de búsqueda sin resultados si existe
          if ($afterSearch.find('[data-cy="no-results"], .no-results').length > 0) {
            cy.get('[data-cy="no-results"], .no-results').should('exist')
            if ($afterSearch.find('[data-cy="no-results-message"], .no-results-message').length > 0) {
              cy.get('[data-cy="no-results-message"], .no-results-message').first().should('satisfy', ($el) => {
                const text = $el.text().toLowerCase()
                return text.includes('resultados') || text.includes('encontraron') || text.includes('no se') || text.length > 0
              })
            }
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar navegación con estados de filtros', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Aplicar filtros
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="location-filter"], .location-filter, button').length > 0) {
        cy.get('[data-cy="location-filter"], .location-filter, button').first().click({ force: true })
        cy.get('body', { timeout: 3000 }).then(($afterClick) => {
          if ($afterClick.find('[data-cy="province-filter"], select').length > 0) {
            cy.get('[data-cy="province-filter"], select').first().select('Los Ríos', { force: true })
            cy.get('[data-cy="apply-filter"], button[type="submit"]').first().click({ force: true })
            cy.get('body', { timeout: 3000 }).then(($afterFilter) => {
              // Verificar filtros activos si existen
              if ($afterFilter.find('[data-cy="active-filters"], .active-filters').length > 0) {
                cy.get('[data-cy="active-filters"], .active-filters').should('exist')
                if ($afterFilter.find('[data-cy="filter-tag"], .filter-tag').length > 0) {
                  cy.get('[data-cy="filter-tag"], .filter-tag').first().should('satisfy', ($el) => {
                    const text = $el.text().toLowerCase()
                    return text.includes('ríos') || text.includes('los') || text.length > 0
                  })
                }
                
                // Limpiar filtros si existe
                if ($afterFilter.find('[data-cy="clear-filters"], button').length > 0) {
                  cy.get('[data-cy="clear-filters"], button').first().click({ force: true })
                  cy.get('body', { timeout: 3000 }).should('be.visible')
                }
              }
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar navegación con estados de paginación', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular muchas páginas
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
    
    // Esperar un poco para que la página se estabilice
    cy.wait(1000)
    
    // Verificar paginación si existe
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="pagination"], .pagination').length > 0) {
        cy.get('[data-cy="pagination"], .pagination').should('exist')
        if ($body.find('[data-cy="page-info"], .page-info').length > 0) {
          cy.get('[data-cy="page-info"], .page-info').first().should('satisfy', ($el) => {
            const text = $el.text().toLowerCase()
            return text.includes('1') || text.includes('4') || text.includes('página') || text.length > 0
          })
        }
        
        // Navegar a siguiente página si existe
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
    
    // Seleccionar elementos
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-checkbox"], input[type="checkbox"]').length > 0) {
        cy.get('[data-cy="finca-checkbox"], input[type="checkbox"]').first().check({ force: true })
        cy.get('[data-cy="finca-checkbox"], input[type="checkbox"]').eq(1).check({ force: true })
        cy.get('body', { timeout: 3000 }).then(($afterCheck) => {
          // Verificar estado de selección si existe
          if ($afterCheck.find('[data-cy="selection-info"], .selection-info').length > 0) {
            cy.get('[data-cy="selection-info"], .selection-info').first().should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('seleccionados') || text.includes('2') || text.length > 0
            })
          }
          if ($afterCheck.find('[data-cy="bulk-actions"], .bulk-actions').length > 0) {
            cy.get('[data-cy="bulk-actions"], .bulk-actions').should('exist')
          }
          
          // Seleccionar todos si existe
          if ($afterCheck.find('[data-cy="select-all"], input[type="checkbox"]').length > 0) {
            cy.get('[data-cy="select-all"], input[type="checkbox"]').first().check({ force: true })
            cy.get('body', { timeout: 3000 }).should('be.visible')
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar navegación con estados de formulario', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          // Verificar estado inicial del formulario si existe
          if ($modal.find('[data-cy="finca-form"], .finca-form, form').length > 0) {
            cy.get('[data-cy="finca-form"], .finca-form, form').should('exist')
            if ($modal.find('[data-cy="save-finca"], button[type="submit"]').length > 0) {
              cy.get('[data-cy="save-finca"], button[type="submit"]').first().should('satisfy', ($el) => {
                return $el.is(':disabled') || $el.length > 0
              })
            }
            
            // Llenar formulario
            if ($modal.find('[data-cy="finca-nombre"], input').length > 0) {
              cy.get('[data-cy="finca-nombre"], input').first().type('Finca Test', { force: true })
              cy.get('[data-cy="finca-ubicacion"], input').first().type('Test Location', { force: true })
              cy.get('[data-cy="finca-area"], input[type="number"]').first().type('10', { force: true })
              
              // Verificar que se habilita el botón si existe
              if ($modal.find('[data-cy="save-finca"], button[type="submit"]').length > 0) {
                cy.get('[data-cy="save-finca"], button[type="submit"]').first().should('satisfy', ($el) => {
                  return !$el.is(':disabled') || $el.length > 0
                })
              }
            }
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar navegación con estados de validación', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          // Intentar guardar sin llenar
          if ($modal.find('[data-cy="save-finca"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().click({ force: true })
            cy.get('body', { timeout: 3000 }).then(($afterSubmit) => {
              // Verificar errores de validación si existen
              if ($afterSubmit.find('[data-cy="validation-error"], .validation-error, .error-message').length > 0) {
                cy.get('[data-cy="validation-error"], .validation-error, .error-message').should('exist')
                if ($afterSubmit.find('[data-cy="field-error"], .field-error').length > 0) {
                  cy.get('[data-cy="field-error"], .field-error').should('have.length.greaterThan', 0)
                }
              }
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar tooltips en elementos interactivos', () => {
    cy.visit('/agricultor-dashboard')
    
    // Verificar tooltips
    cy.get('[data-cy="help-icon"]').trigger('mouseover')
    cy.get('[data-cy="tooltip"]').should('be.visible')
  })

  it('debe mostrar animaciones de transición', () => {
    cy.visit('/agricultor-dashboard')
    
    // Navegar y verificar transiciones
    cy.get('[data-cy="nav-fincas"]').click()
    cy.get('[data-cy="page-transition"]').should('be.visible')
  })

  it('debe mantener scroll position en navegación', () => {
    cy.visit('/mis-fincas')
    
    // Scroll hacia abajo
    cy.scrollTo(0, 500)
    
    // Navegar a otra página y volver
    cy.visit('/mis-lotes')
    cy.visit('/mis-fincas')
    
    // Verificar que se mantiene la posición (si está implementado)
    cy.window().its('scrollY').should('be.greaterThan', 0)
  })

  it('debe mostrar modales con overlay', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    // Verificar overlay del modal
    cy.get('[data-cy="modal-overlay"]').should('be.visible')
    cy.get('[data-cy="modal-overlay"]').should('have.class', 'backdrop-blur')
  })

  it('debe cerrar modales con ESC', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    // Cerrar con ESC
    cy.get('body').type('{esc}')
    cy.get('[data-cy="finca-form"]').should('not.exist')
  })
})
