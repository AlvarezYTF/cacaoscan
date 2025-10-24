describe('Navegación - UI y UX', () => {
  beforeEach(() => {
    cy.login('farmer')
  })

  it('debe mostrar navegación principal correctamente', () => {
    cy.visit('/agricultor-dashboard')
    
    // Verificar navbar principal
    cy.get('[data-cy="main-navbar"]').should('be.visible')
    cy.get('[data-cy="logo"]').should('be.visible')
    cy.get('[data-cy="user-menu"]').should('be.visible')
    
    // Verificar enlaces de navegación
    cy.get('[data-cy="nav-link"]').should('have.length.greaterThan', 0)
  })

  it('debe mostrar navegación lateral correctamente', () => {
    cy.visit('/agricultor-dashboard')
    
    // Verificar sidebar
    cy.get('[data-cy="sidebar"]').should('be.visible')
    cy.get('[data-cy="sidebar-menu"]').should('be.visible')
    
    // Verificar enlaces del sidebar
    cy.get('[data-cy="sidebar-link"]').should('have.length.greaterThan', 0)
  })

  it('debe mostrar breadcrumbs correctamente', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Verificar breadcrumbs
    cy.get('[data-cy="breadcrumbs"]').should('be.visible')
    cy.get('[data-cy="breadcrumb-home"]').should('be.visible')
    cy.get('[data-cy="breadcrumb-fincas"]').should('be.visible')
    cy.get('[data-cy="breadcrumb-current"]').should('be.visible')
  })

  it('debe navegar usando breadcrumbs', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    cy.get('[data-cy="lote-item"]').first().click()
    
    // Navegar usando breadcrumbs
    cy.get('[data-cy="breadcrumb-fincas"]').click()
    cy.get('[data-cy="finca-details"]').should('be.visible')
    
    cy.get('[data-cy="breadcrumb-home"]').click()
    cy.url().should('include', '/agricultor-dashboard')
  })

  it('debe mostrar menú de usuario correctamente', () => {
    cy.visit('/agricultor-dashboard')
    
    // Abrir menú de usuario
    cy.get('[data-cy="user-menu"]').click()
    
    // Verificar opciones del menú
    cy.get('[data-cy="user-menu-items"]').should('be.visible')
    cy.get('[data-cy="profile-link"]').should('be.visible')
    cy.get('[data-cy="settings-link"]').should('be.visible')
    cy.get('[data-cy="logout-button"]').should('be.visible')
  })

  it('debe mostrar navegación responsive en móvil', () => {
    // Simular vista móvil
    cy.viewport(375, 667)
    cy.visit('/agricultor-dashboard')
    
    // Verificar menú hamburguesa
    cy.get('[data-cy="mobile-menu-button"]').should('be.visible')
    
    // Abrir menú móvil
    cy.get('[data-cy="mobile-menu-button"]').click()
    cy.get('[data-cy="mobile-menu"]').should('be.visible')
    
    // Verificar enlaces del menú móvil
    cy.get('[data-cy="mobile-menu-link"]').should('have.length.greaterThan', 0)
  })

  it('debe mostrar navegación responsive en tablet', () => {
    // Simular vista tablet
    cy.viewport(768, 1024)
    cy.visit('/agricultor-dashboard')
    
    // Verificar que se adapta a tablet
    cy.get('[data-cy="sidebar"]').should('be.visible')
    cy.get('[data-cy="main-content"]').should('be.visible')
  })

  it('debe mostrar navegación responsive en desktop', () => {
    // Simular vista desktop
    cy.viewport(1920, 1080)
    cy.visit('/agricultor-dashboard')
    
    // Verificar que se adapta a desktop
    cy.get('[data-cy="sidebar"]').should('be.visible')
    cy.get('[data-cy="main-content"]').should('be.visible')
    cy.get('[data-cy="navbar"]').should('be.visible')
  })

  it('debe mostrar indicadores de página activa', () => {
    cy.visit('/agricultor-dashboard')
    
    // Verificar que dashboard está activo
    cy.get('[data-cy="nav-dashboard"]').should('have.class', 'active')
    
    // Navegar a otra página
    cy.visit('/mis-fincas')
    cy.get('[data-cy="nav-fincas"]').should('have.class', 'active')
    cy.get('[data-cy="nav-dashboard"]').should('not.have.class', 'active')
  })

  it('debe mostrar indicadores de carga durante navegación', () => {
    cy.visit('/agricultor-dashboard')
    
    // Navegar a página que puede tardar en cargar
    cy.get('[data-cy="nav-fincas"]').click()
    
    // Verificar indicador de carga
    cy.get('[data-cy="loading-indicator"]').should('be.visible')
    
    // Verificar que desaparece cuando carga
    cy.get('[data-cy="loading-indicator"]', { timeout: 10000 }).should('not.exist')
  })

  it('debe mostrar notificaciones de navegación', () => {
    cy.visit('/agricultor-dashboard')
    
    // Simular notificación
    cy.get('[data-cy="notifications-bell"]').click()
    cy.get('[data-cy="notification-item"]').first().click()
    
    // Verificar que se muestra notificación
    cy.get('[data-cy="notification-toast"]').should('be.visible')
  })

  it('debe mostrar navegación con estados de error', () => {
    // Simular error de red
    cy.intercept('GET', '/api/fincas/', {
      statusCode: 500,
      body: { error: 'Error del servidor' }
    }).as('serverError')
    
    cy.visit('/mis-fincas')
    cy.wait('@serverError')
    
    // Verificar mensaje de error
    cy.get('[data-cy="error-message"]').should('be.visible')
    
    // Verificar que se puede reintentar
    cy.get('[data-cy="retry-button"]').should('be.visible')
  })

  it('debe mostrar navegación con estados de carga', () => {
    cy.visit('/agricultor-dashboard')
    
    // Verificar que se muestra loading inicial
    cy.get('[data-cy="initial-loading"]').should('be.visible')
    
    // Verificar que desaparece cuando carga
    cy.get('[data-cy="initial-loading"]', { timeout: 10000 }).should('not.exist')
  })

  it('debe mostrar navegación con estados vacíos', () => {
    // Simular lista vacía
    cy.intercept('GET', '/api/fincas/', {
      statusCode: 200,
      body: { results: [], count: 0 }
    }).as('emptyList')
    
    cy.visit('/mis-fincas')
    cy.wait('@emptyList')
    
    // Verificar estado vacío
    cy.get('[data-cy="empty-state"]').should('be.visible')
    cy.get('[data-cy="empty-message"]').should('contain', 'No hay fincas')
    cy.get('[data-cy="empty-action"]').should('be.visible')
  })

  it('debe mostrar navegación con estados de búsqueda', () => {
    cy.visit('/mis-fincas')
    
    // Buscar algo que no existe
    cy.get('[data-cy="search-fincas"]').type('noexiste')
    
    // Verificar estado de búsqueda sin resultados
    cy.get('[data-cy="no-results"]').should('be.visible')
    cy.get('[data-cy="no-results-message"]').should('contain', 'No se encontraron resultados')
  })

  it('debe mostrar navegación con estados de filtros', () => {
    cy.visit('/mis-fincas')
    
    // Aplicar filtros
    cy.get('[data-cy="location-filter"]').click()
    cy.get('[data-cy="province-filter"]').select('Los Ríos')
    cy.get('[data-cy="apply-filter"]').click()
    
    // Verificar filtros activos
    cy.get('[data-cy="active-filters"]').should('be.visible')
    cy.get('[data-cy="filter-tag"]').should('contain', 'Los Ríos')
    
    // Limpiar filtros
    cy.get('[data-cy="clear-filters"]').click()
    cy.get('[data-cy="active-filters"]').should('not.exist')
  })

  it('debe mostrar navegación con estados de paginación', () => {
    // Simular muchas páginas
    cy.intercept('GET', '/api/fincas/', {
      statusCode: 200,
      body: {
        results: Array(25).fill().map((_, i) => ({
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
    cy.wait('@manyPages')
    
    // Verificar paginación
    cy.get('[data-cy="pagination"]').should('be.visible')
    cy.get('[data-cy="page-info"]').should('contain', '1 de 4')
    
    // Navegar a siguiente página
    cy.get('[data-cy="next-page"]').click()
    cy.get('[data-cy="page-info"]').should('contain', '2 de 4')
  })

  it('debe mostrar navegación con estados de selección', () => {
    cy.visit('/mis-fincas')
    
    // Seleccionar elementos
    cy.get('[data-cy="finca-checkbox"]').first().check()
    cy.get('[data-cy="finca-checkbox"]').eq(1).check()
    
    // Verificar estado de selección
    cy.get('[data-cy="selection-info"]').should('contain', '2 seleccionados')
    cy.get('[data-cy="bulk-actions"]').should('be.visible')
    
    // Seleccionar todos
    cy.get('[data-cy="select-all"]').check()
    cy.get('[data-cy="selection-info"]').should('contain', 'Todos seleccionados')
  })

  it('debe mostrar navegación con estados de formulario', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    // Verificar estado inicial del formulario
    cy.get('[data-cy="finca-form"]').should('be.visible')
    cy.get('[data-cy="save-finca"]').should('be.disabled')
    
    // Llenar formulario
    cy.get('[data-cy="finca-nombre"]').type('Finca Test')
    cy.get('[data-cy="finca-ubicacion"]').type('Test Location')
    cy.get('[data-cy="finca-area"]').type('10')
    
    // Verificar que se habilita el botón
    cy.get('[data-cy="save-finca"]').should('not.be.disabled')
  })

  it('debe mostrar navegación con estados de validación', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    // Intentar guardar sin llenar
    cy.get('[data-cy="save-finca"]').click()
    
    // Verificar errores de validación
    cy.get('[data-cy="validation-error"]').should('be.visible')
    cy.get('[data-cy="field-error"]').should('have.length.greaterThan', 0)
  })
})
