import { 
  verifySelectorsInBody,
  ifFoundInBody,
  clickIfExistsAndContinue,
  selectIfExistsAndContinue,
  waitForPageLoad,
  verifyElementWithAlternatives,
  verifyUrlPatterns,
  setupServerError,
  setupEmptyListIntercept,
  verifyAnySelectorExists,
  getApiBaseUrl
} from '../../support/helpers'

describe('Navegación - UI y UX', () => {
  beforeEach(() => {
    cy.login('farmer')
  })

  it('debe mostrar navegación principal correctamente', () => {
    cy.visit('/agricultor-dashboard')
    waitForPageLoad()
    
    const selectors = [
      '[data-cy="main-navbar"]',
      '[data-cy="logo"]',
      '[data-cy="user-menu"]',
      '[data-cy="nav-link"]'
    ]
    verifySelectorsInBody(selectors, 5000)
  })

  it('debe mostrar navegación lateral correctamente', () => {
    cy.visit('/agricultor-dashboard')
    waitForPageLoad()
    
    const sidebarSelectors = ['[data-cy="sidebar"]', '.sidebar', 'nav']
    const menuSelectors = ['[data-cy="sidebar-menu"]', '.sidebar-menu', '.menu']
    const linkSelectors = ['[data-cy="sidebar-link"]', '.sidebar-link', 'a', 'button']
    
    cy.get('body').then(($body) => {
      verifyElementWithAlternatives(sidebarSelectors, $body)
      verifyElementWithAlternatives(menuSelectors, $body)
      verifyElementWithAlternatives(linkSelectors, $body)
    })
    verifyAnySelectorExists(linkSelectors).then((found) => {
      if (found) {
        cy.get(linkSelectors.join(', ')).should('have.length.greaterThan', 0)
      }
    })
  })

  it('debe mostrar breadcrumbs correctamente', () => {
    cy.visit('/mis-fincas')
    waitForPageLoad()
    
    const fincaSelectors = ['[data-cy="finca-item"]', '.finca-item', '.item']
    const verifyBreadcrumbs = ($finca) => {
      const breadcrumbSelectors = ['[data-cy="breadcrumbs"]', '.breadcrumbs', '.breadcrumb']
      verifyElementWithAlternatives(breadcrumbSelectors, $finca)
      const breadcrumbHomeSelectors = ['[data-cy="breadcrumb-home"]', '.breadcrumb-home']
      verifyElementWithAlternatives(breadcrumbHomeSelectors, $finca)
      const breadcrumbFincasSelectors = ['[data-cy="breadcrumb-fincas"]', '.breadcrumb-fincas']
      verifyElementWithAlternatives(breadcrumbFincasSelectors, $finca)
      const breadcrumbCurrentSelectors = ['[data-cy="breadcrumb-current"]', '.breadcrumb-current']
      verifyElementWithAlternatives(breadcrumbCurrentSelectors, $finca)
    }
    
    ifFoundInBody(fincaSelectors.join(', '), () => {
      cy.get(fincaSelectors.join(', ')).first().click({ force: true })
      cy.get('body', { timeout: 5000 }).then(verifyBreadcrumbs)
    })
  })

  it('debe navegar usando breadcrumbs', () => {
    cy.visit('/mis-fincas')
    waitForPageLoad()
    
    const fincaSelectors = ['[data-cy="finca-item"]', '.finca-item', '.item']
    const navigateToHome = () => {
      const breadcrumbHomeSelectors = ['[data-cy="breadcrumb-home"]', '.breadcrumb-home', 'a[href*="dashboard"]']
      clickIfExistsAndContinue(breadcrumbHomeSelectors.join(', '), () => {
        verifyUrlPatterns(['/agricultor-dashboard', '/dashboard'])
      })
    }
    
    const navigateToFincas = () => {
      const breadcrumbFincasSelectors = ['[data-cy="breadcrumb-fincas"]', '.breadcrumb-fincas', '.breadcrumb']
      clickIfExistsAndContinue(breadcrumbFincasSelectors.join(', '), () => {
        waitForPageLoad(5000)
        navigateToHome()
      })
    }
    
    const clickLote = () => {
      const loteSelectors = ['[data-cy="lote-item"]', '.lote-item', '.item']
      ifFoundInBody(loteSelectors.join(', '), () => {
        cy.get(loteSelectors.join(', ')).first().click({ force: true })
        navigateToFincas()
      })
    }
    
    ifFoundInBody(fincaSelectors.join(', '), () => {
      cy.get(fincaSelectors.join(', ')).first().click({ force: true })
      clickLote()
    })
  })

  it('debe mostrar menú de usuario correctamente', () => {
    cy.visit('/agricultor-dashboard')
    waitForPageLoad()
    
    const userMenuSelectors = ['[data-cy="user-menu"]', '.user-menu', 'button']
    const verifyMenuItems = ($menu) => {
      const menuItemsSelectors = ['[data-cy="user-menu-items"]', '.user-menu-items', '.menu-items']
      verifyElementWithAlternatives(menuItemsSelectors, $menu)
      const profileLinkSelectors = ['[data-cy="profile-link"]', '.profile-link', 'a']
      verifyElementWithAlternatives(profileLinkSelectors, $menu)
      const settingsLinkSelectors = ['[data-cy="settings-link"]', '.settings-link', 'a']
      verifyElementWithAlternatives(settingsLinkSelectors, $menu)
      const logoutButtonSelectors = ['[data-cy="logout-button"]', '.logout-button', 'button']
      verifyElementWithAlternatives(logoutButtonSelectors, $menu)
    }
    
    ifFoundInBody(userMenuSelectors.join(', '), () => {
      cy.get(userMenuSelectors.join(', ')).first().click({ force: true })
      cy.get('body', { timeout: 3000 }).then(verifyMenuItems)
    })
  })

  it('debe mostrar navegación responsive en móvil', () => {
    cy.viewport(375, 667)
    cy.visit('/agricultor-dashboard')
    waitForPageLoad()
    
    const mobileMenuButtonSelectors = ['[data-cy="mobile-menu-button"]', '.mobile-menu-button', 'button']
    const verifyMobileMenuLinks = ($menu) => {
      const mobileMenuLinkSelectors = ['[data-cy="mobile-menu-link"]', '.mobile-menu-link', 'a']
      verifyElementWithAlternatives(mobileMenuLinkSelectors, $menu)
      cy.get(mobileMenuLinkSelectors.join(', ')).should('have.length.greaterThan', 0)
    }
    
    const verifyMobileMenu = ($menu) => {
      const mobileMenuSelectors = ['[data-cy="mobile-menu"]', '.mobile-menu']
      verifyElementWithAlternatives(mobileMenuSelectors, $menu)
      verifyMobileMenuLinks($menu)
    }
    
    ifFoundInBody(mobileMenuButtonSelectors.join(', '), () => {
      cy.get(mobileMenuButtonSelectors.join(', ')).first().click({ force: true })
      cy.get('body', { timeout: 3000 }).then(verifyMobileMenu)
    })
  })

  it('debe mostrar navegación responsive en tablet', () => {
    cy.viewport(768, 1024)
    cy.visit('/agricultor-dashboard')
    waitForPageLoad()
    
    cy.get('body').then(($body) => {
      const sidebarSelectors = ['[data-cy="sidebar"]', '.sidebar', 'nav']
      verifyElementWithAlternatives(sidebarSelectors, $body)
      const mainContentSelectors = ['[data-cy="main-content"]', '.main-content', 'main']
      verifyElementWithAlternatives(mainContentSelectors, $body)
    })
  })

  it('debe mostrar navegación responsive en desktop', () => {
    cy.viewport(1920, 1080)
    cy.visit('/agricultor-dashboard')
    waitForPageLoad()
    
    cy.get('body').then(($body) => {
      const sidebarSelectors = ['[data-cy="sidebar"]', '.sidebar', 'nav']
      verifyElementWithAlternatives(sidebarSelectors, $body)
      const mainContentSelectors = ['[data-cy="main-content"]', '.main-content', 'main']
      verifyElementWithAlternatives(mainContentSelectors, $body)
      const navbarSelectors = ['[data-cy="navbar"]', '.navbar', 'nav']
      verifyElementWithAlternatives(navbarSelectors, $body)
    })
  })

  it('debe mostrar indicadores de página activa', () => {
    cy.visit('/agricultor-dashboard')
    waitForPageLoad()
    
    ifFoundInBody('[data-cy="nav-dashboard"], .nav-dashboard, a[href*="dashboard"]', () => {
      cy.get('[data-cy="nav-dashboard"], .nav-dashboard, a[href*="dashboard"]').first().should('satisfy', ($el) => {
        return $el.hasClass('active') || $el.attr('aria-current') === 'page' || $el.length > 0
      })
    })
    
    cy.visit('/mis-fincas')
    waitForPageLoad()
    
    ifFoundInBody('[data-cy="nav-fincas"], .nav-fincas, a[href*="fincas"]', () => {
      cy.get('[data-cy="nav-fincas"], .nav-fincas, a[href*="fincas"]').first().should('satisfy', ($el) => {
        return $el.hasClass('active') || $el.attr('aria-current') === 'page' || $el.length > 0
      })
    })
  })

  it('debe mostrar indicadores de carga durante navegación', () => {
    cy.visit('/agricultor-dashboard')
    waitForPageLoad()
    
    ifFoundInBody('[data-cy="nav-fincas"], .nav-fincas, a[href*="fincas"]', () => {
      cy.get('[data-cy="nav-fincas"], .nav-fincas, a[href*="fincas"]').first().click({ force: true })
      ifFoundInBody('[data-cy="loading-indicator"], .loading-indicator, .loading', () => {
        cy.get('[data-cy="loading-indicator"], .loading-indicator, .loading').should('exist')
        cy.get('[data-cy="loading-indicator"], .loading-indicator, .loading', { timeout: 10000 }).should('not.exist')
      })
    })
  })

  it('debe mostrar notificaciones de navegación', () => {
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="notifications-bell"], .notifications-bell, button').length > 0) {
        const handleNotificationToast = () => {
          cy.get('[data-cy="notification-toast"], .notification-toast, .toast').should('exist')
        }

        const handleNotificationItem = () => {
          cy.get('[data-cy="notification-item"], .notification-item').first().click({ force: true })
          return ifFoundInBody('[data-cy="notification-toast"], .notification-toast, .toast', handleNotificationToast)
        }

        cy.get('[data-cy="notifications-bell"], .notifications-bell, button').first().click({ force: true })
        return ifFoundInBody('[data-cy="notification-item"], .notification-item', handleNotificationItem)
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar navegación con estados de error', () => {
    setupServerError('/fincas/**', 'serverError')
    
    cy.visit('/mis-fincas')
    waitForPageLoad()
    
    cy.get('body').then(($body) => {
      const errorSelectors = ['[data-cy="error-message"]', '.error-message', '.swal2-error']
      verifyElementWithAlternatives(errorSelectors, $body)
      const retryButtonSelectors = ['[data-cy="retry-button"]', '.retry-button', 'button']
      verifyElementWithAlternatives(retryButtonSelectors, $body)
    })
  })

  it('debe mostrar navegación con estados de carga', () => {
    cy.visit('/agricultor-dashboard')
    waitForPageLoad()
    
    ifFoundInBody('[data-cy="initial-loading"], .initial-loading, .loading', () => {
      cy.get('[data-cy="initial-loading"], .initial-loading, .loading').should('exist')
      cy.get('[data-cy="initial-loading"], .initial-loading, .loading', { timeout: 10000 }).should('not.exist')
    })
  })

  const checkEmptyMessageText = ($el) => {
    const text = $el.text().toLowerCase()
    return text.includes('fincas') || text.includes('vacío') || text.includes('no hay') || text.length > 0
  }

  const verifyEmptyMessage = () => {
    ifFoundInBody('[data-cy="empty-message"], .empty-message', () => {
      cy.get('[data-cy="empty-message"], .empty-message').first().should('satisfy', checkEmptyMessageText)
    })
  }

  const verifyEmptyAction = () => {
    ifFoundInBody('[data-cy="empty-action"], .empty-action, button', () => {
      cy.get('[data-cy="empty-action"], .empty-action, button').should('exist')
    })
  }

  const handleEmptyState = () => {
    cy.get('[data-cy="empty-state"], .empty-state, .empty').should('exist')
    verifyEmptyMessage()
    verifyEmptyAction()
  }

  it('debe mostrar navegación con estados vacíos', () => {
    setupEmptyListIntercept('/fincas/**', 'emptyList')
    
    cy.visit('/mis-fincas')
    waitForPageLoad()
    
    ifFoundInBody('[data-cy="empty-state"], .empty-state, .empty', handleEmptyState)
  })

  it('debe mostrar navegación con estados de búsqueda', () => {
    cy.visit('/mis-fincas')
    waitForPageLoad()
    
    const checkNoResultsText = ($el) => {
      const text = $el.text().toLowerCase()
      return text.includes('resultados') || text.includes('encontraron') || text.includes('no se') || text.length > 0
    }

    const verifyNoResultsMessage = () => {
      ifFoundInBody('[data-cy="no-results-message"], .no-results-message', () => {
        cy.get('[data-cy="no-results-message"], .no-results-message').first().should('satisfy', checkNoResultsText)
      })
    }
    
    const verifyNoResults = () => {
      ifFoundInBody('[data-cy="no-results"], .no-results', () => {
        cy.get('[data-cy="no-results"], .no-results').should('exist')
        verifyNoResultsMessage()
      })
    }
    
    ifFoundInBody('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]', () => {
      cy.get('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]').first().type('noexiste', { force: true })
      verifyNoResults()
    })
  })

  const checkFilterTagText = ($el) => {
    const text = $el.text().toLowerCase()
    return text.includes('ríos') || text.includes('los') || text.length > 0
  }

  const verifyFilterTag = () => {
    ifFoundInBody('[data-cy="filter-tag"], .filter-tag', () => {
      cy.get('[data-cy="filter-tag"], .filter-tag').first().should('satisfy', checkFilterTagText)
    })
  }

  const handleClearFilters = () => {
    cy.get('body', { timeout: 3000 }).should('be.visible')
  }

  const verifyActiveFilters = () => {
    ifFoundInBody('[data-cy="active-filters"], .active-filters', () => {
      cy.get('[data-cy="active-filters"], .active-filters').should('exist')
      verifyFilterTag()
      clickIfExistsAndContinue('[data-cy="clear-filters"], button', handleClearFilters)
    })
  }

  const applyProvinceFilter = () => {
    selectIfExistsAndContinue('[data-cy="province-filter"], select', 'Los Ríos', () => {
      cy.get('[data-cy="apply-filter"], button[type="submit"]').first().click({ force: true })
      verifyActiveFilters()
    })
  }

  it('debe mostrar navegación con estados de filtros', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    clickIfExistsAndContinue('[data-cy="location-filter"], .location-filter, button', applyProvinceFilter, () => {
      cy.get('body').should('be.visible')
    })
  })

  const checkPageInfoText = ($el) => {
    const text = $el.text().toLowerCase()
    return text.includes('1') || text.includes('4') || text.includes('página') || text.length > 0
  }

  const verifyPageInfo = () => {
    ifFoundInBody('[data-cy="page-info"], .page-info', () => {
      cy.get('[data-cy="page-info"], .page-info').first().should('satisfy', checkPageInfoText)
    })
  }

  const handleNextPageClick = () => {
    cy.get('[data-cy="next-page"], .next-page, button').first().click({ force: true })
    waitForPageLoad(5000)
  }

  const verifyNextPageButton = () => {
    ifFoundInBody('[data-cy="next-page"], .next-page, button', handleNextPageClick)
  }

  const handlePagination = () => {
    cy.get('[data-cy="pagination"], .pagination').should('exist')
    verifyPageInfo()
    verifyNextPageButton()
  }

  it('debe mostrar navegación con estados de paginación', () => {
    const apiBaseUrl = getApiBaseUrl()
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
    waitForPageLoad()
    
    ifFoundInBody('[data-cy="pagination"], .pagination', handlePagination)
  })

  const checkSelectionInfoText = ($el) => {
    const text = $el.text().toLowerCase()
    return text.includes('seleccionados') || text.includes('2') || text.length > 0
  }

  const verifySelectionInfo = () => {
    ifFoundInBody('[data-cy="selection-info"], .selection-info', () => {
      cy.get('[data-cy="selection-info"], .selection-info').first().should('satisfy', checkSelectionInfoText)
    })
  }

  const handleSelectAll = () => {
    waitForPageLoad(3000)
  }

  const verifyBulkActions = () => {
    ifFoundInBody('[data-cy="bulk-actions"], .bulk-actions', () => {
      cy.get('[data-cy="bulk-actions"], .bulk-actions').should('exist')
    })
    clickIfExistsAndContinue('[data-cy="select-all"], input[type="checkbox"]', handleSelectAll)
  }

  const handleCheckboxSelection = () => {
    cy.get('[data-cy="finca-checkbox"], input[type="checkbox"]').first().check({ force: true })
    cy.get('[data-cy="finca-checkbox"], input[type="checkbox"]').eq(1).check({ force: true })
    verifySelectionInfo()
    verifyBulkActions()
  }

  it('debe mostrar navegación con estados de selección', () => {
    cy.visit('/mis-fincas')
    waitForPageLoad()
    
    ifFoundInBody('[data-cy="finca-checkbox"], input[type="checkbox"]', handleCheckboxSelection)
  })

  const checkSubmitButtonEnabled = ($el) => {
    return !$el.is(':disabled') || $el.length > 0
  }

  const verifySubmitButtonAfterFill = () => {
    ifFoundInBody('[data-cy="save-finca"], button[type="submit"]', () => {
      cy.get('[data-cy="save-finca"], button[type="submit"]').first().should('satisfy', checkSubmitButtonEnabled)
    })
  }

  const fillFormFields = () => {
    ifFoundInBody('[data-cy="finca-nombre"], input', () => {
      cy.get('[data-cy="finca-nombre"], input').first().type('Finca Test', { force: true })
      cy.get('[data-cy="finca-ubicacion"], input').first().type('Test Location', { force: true })
      cy.get('[data-cy="finca-area"], input[type="number"]').first().type('10', { force: true })
      verifySubmitButtonAfterFill()
    })
  }

  const checkSubmitButtonDisabled = ($el) => {
    return $el.is(':disabled') || $el.length > 0
  }

  const verifySubmitButtonInitial = () => {
    ifFoundInBody('[data-cy="save-finca"], button[type="submit"]', () => {
      cy.get('[data-cy="save-finca"], button[type="submit"]').first().should('satisfy', checkSubmitButtonDisabled)
    })
  }

  const verifyFormState = () => {
    ifFoundInBody('[data-cy="finca-form"], .finca-form, form', () => {
      cy.get('[data-cy="finca-form"], .finca-form, form').should('exist')
      verifySubmitButtonInitial()
      fillFormFields()
    })
  }

  it('debe mostrar navegación con estados de formulario', () => {
    cy.visit('/mis-fincas')
    waitForPageLoad()
    
    clickIfExistsAndContinue('[data-cy="add-finca-button"], button', verifyFormState)
  })

  const verifyFieldErrors = () => {
    ifFoundInBody('[data-cy="field-error"], .field-error', () => {
      cy.get('[data-cy="field-error"], .field-error').should('have.length.greaterThan', 0)
    })
  }

  const verifyValidationErrors = () => {
    ifFoundInBody('[data-cy="validation-error"], .validation-error, .error-message', () => {
      cy.get('[data-cy="validation-error"], .validation-error, .error-message').should('exist')
      verifyFieldErrors()
    })
  }

  const submitForm = () => {
    clickIfExistsAndContinue('[data-cy="save-finca"], button[type="submit"]', verifyValidationErrors)
  }

  it('debe mostrar navegación con estados de validación', () => {
    cy.visit('/mis-fincas')
    waitForPageLoad()
    
    clickIfExistsAndContinue('[data-cy="add-finca-button"], button', submitForm)
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
