describe('Navegación - Flujos Completos', () => {
  beforeEach(() => {
    cy.login('farmer')
  })

  it('debe completar flujo completo de análisis de imagen', () => {
    // 1. Ir a nuevo análisis
    cy.visit('/nuevo-analisis')
    
    // 2. Cargar imagen
    cy.uploadTestImage('test-cacao.jpg')
    cy.get('[data-cy="upload-button"]').click()
    cy.checkNotification('Imagen cargada exitosamente', 'success')
    
    // 3. Esperar análisis
    cy.waitForAnalysis()
    
    // 4. Ver resultados
    cy.get('[data-cy="analysis-results"]').should('be.visible')
    cy.get('[data-cy="quality-score"]').should('be.visible')
    
    // 5. Guardar análisis
    cy.get('[data-cy="save-analysis"]').click()
    cy.checkNotification('Análisis guardado exitosamente', 'success')
    
    // 6. Verificar que aparece en historial
    cy.visit('/mis-analisis')
    cy.get('[data-cy="analysis-history"]').should('contain', 'test-cacao.jpg')
  })

  it('debe completar flujo de gestión de finca y lotes', () => {
    // 1. Crear finca
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    cy.fixture('testData').then((data) => {
      const fincaData = data.fincas[0]
      cy.fillFincaForm(fincaData)
    })
    
    cy.get('[data-cy="map-container"]').click(300, 200)
    cy.get('[data-cy="save-finca"]').click()
    cy.checkNotification('Finca creada exitosamente', 'success')
    
    // 2. Crear lote en la finca
    cy.get('[data-cy="finca-item"]').first().click()
    cy.get('[data-cy="add-lote-button"]').click()
    
    cy.fixture('testData').then((data) => {
      const loteData = data.lotes[0]
      cy.fillLoteForm(loteData)
    })
    
    cy.get('[data-cy="save-lote"]').click()
    cy.checkNotification('Lote creado exitosamente', 'success')
    
    // 3. Verificar relación finca-lote
    cy.get('[data-cy="finca-lotes"]').should('contain', 'Lote A - Norte')
    
    // 4. Programar análisis para el lote
    cy.get('[data-cy="lote-item"]').first().click()
    cy.get('[data-cy="schedule-analysis"]').click()
    
    cy.get('[data-cy="analysis-date"]').type('2024-02-15')
    cy.get('[data-cy="analysis-time"]').type('10:00')
    cy.get('[data-cy="save-schedule"]').click()
    cy.checkNotification('Análisis programado exitosamente', 'success')
  })

  it('debe completar flujo de generación de reporte', () => {
    cy.login('analyst')
    
    // 1. Ir a reportes
    cy.visit('/reportes')
    
    // 2. Crear reporte
    cy.get('[data-cy="create-report-button"]').click()
    cy.get('[data-cy="report-type"]').select('analisis-periodo')
    cy.get('[data-cy="start-date"]').type('2024-01-01')
    cy.get('[data-cy="end-date"]').type('2024-01-31')
    cy.get('[data-cy="include-charts"]').check()
    cy.get('[data-cy="generate-report"]').click()
    
    // 3. Esperar generación
    cy.get('[data-cy="report-completed"]', { timeout: 30000 }).should('be.visible')
    cy.checkNotification('Reporte generado exitosamente', 'success')
    
    // 4. Ver reporte generado
    cy.get('[data-cy="report-item"]').first().click()
    cy.get('[data-cy="report-details"]').should('be.visible')
    
    // 5. Exportar reporte
    cy.get('[data-cy="download-pdf"]').click()
    cy.get('[data-cy="confirm-download"]').click()
    cy.verifyDownload('reporte.pdf')
    
    // 6. Compartir reporte
    cy.get('[data-cy="share-email"]').click()
    cy.get('[data-cy="email-recipients"]').type('test@example.com')
    cy.get('[data-cy="send-email"]').click()
    cy.checkNotification('Reporte enviado por email exitosamente', 'success')
  })

  it('debe completar flujo de administración de usuarios', () => {
    cy.login('admin')
    
    // 1. Ir a gestión de agricultores
    cy.visit('/admin/agricultores')
    
    // 2. Ver lista de usuarios
    cy.get('[data-cy="users-list"]').should('be.visible')
    
    // 3. Ver detalles de usuario
    cy.get('[data-cy="user-item"]').first().click()
    cy.get('[data-cy="user-details"]').should('be.visible')
    
    // 4. Editar usuario
    cy.get('[data-cy="edit-user"]').click()
    cy.get('[data-cy="user-first-name"]').clear().type('Usuario Editado')
    cy.get('[data-cy="save-user"]').click()
    cy.checkNotification('Usuario actualizado exitosamente', 'success')
    
    // 5. Verificar estadísticas
    cy.visit('/admin/dashboard')
    cy.get('[data-cy="admin-stats"]').should('be.visible')
    cy.get('[data-cy="total-users"]').should('be.visible')
  })

  it('debe completar flujo de verificación de email', () => {
    // 1. Registrarse
    cy.visit('/registro')
    
    const newUser = {
      firstName: 'Nuevo',
      lastName: 'Usuario',
      email: 'nuevo.usuario@test.com',
      password: 'Password123!',
      confirmPassword: 'Password123!',
      role: 'farmer'
    }
    
    cy.get('[data-cy="first-name-input"]').type(newUser.firstName)
    cy.get('[data-cy="last-name-input"]').type(newUser.lastName)
    cy.get('[data-cy="email-input"]').type(newUser.email)
    cy.get('[data-cy="password-input"]').type(newUser.password)
    cy.get('[data-cy="confirm-password-input"]').type(newUser.confirmPassword)
    cy.get('[data-cy="role-select"]').select(newUser.role)
    cy.get('[data-cy="terms-checkbox"]').check()
    cy.get('[data-cy="register-button"]').click()
    
    cy.checkNotification('Usuario registrado exitosamente', 'success')
    
    // 2. Intentar hacer login (debería requerir verificación)
    cy.visit('/login')
    cy.get('[data-cy="email-input"]').type(newUser.email)
    cy.get('[data-cy="password-input"]').type(newUser.password)
    cy.get('[data-cy="login-button"]').click()
    
    // 3. Ver mensaje de verificación
    cy.get('[data-cy="verification-message"]')
      .should('be.visible')
      .and('contain', 'Verifica tu email')
    
    // 4. Reenviar email de verificación
    cy.get('[data-cy="resend-verification-button"]').click()
    cy.checkNotification('Email de verificación reenviado', 'success')
  })

  it('debe completar flujo de recuperación de contraseña', () => {
    // 1. Ir a login
    cy.visit('/login')
    
    // 2. Ir a recuperación de contraseña
    cy.get('[data-cy="forgot-password-link"]').click()
    
    // 3. Solicitar recuperación
    cy.fixture('users').then((users) => {
      const user = users.farmer
      cy.get('[data-cy="email-input"]').type(user.email)
      cy.get('[data-cy="send-reset-button"]').click()
      
      cy.checkNotification('Email de recuperación enviado', 'success')
    })
    
    // 4. Simular reset de contraseña
    cy.visit('/reset-password?token=valid-token-123')
    cy.get('[data-cy="new-password-input"]').type('NewPassword123!')
    cy.get('[data-cy="confirm-password-input"]').type('NewPassword123!')
    cy.get('[data-cy="reset-button"]').click()
    
    cy.checkNotification('Contraseña actualizada exitosamente', 'success')
    
    // 5. Hacer login con nueva contraseña
    cy.visit('/login')
    cy.fixture('users').then((users) => {
      const user = users.farmer
      cy.get('[data-cy="email-input"]').type(user.email)
      cy.get('[data-cy="password-input"]').type('NewPassword123!')
      cy.get('[data-cy="login-button"]').click()
      
      cy.url().should('include', '/agricultor-dashboard')
    })
  })

  it('debe completar flujo de navegación entre roles', () => {
    // Test como agricultor
    cy.login('farmer')
    cy.visit('/agricultor-dashboard')
    cy.get('[data-cy="farmer-dashboard"]').should('be.visible')
    
    // Test como analista
    cy.login('analyst')
    cy.visit('/analisis')
    cy.get('[data-cy="analyst-dashboard"]').should('be.visible')
    
    // Test como admin
    cy.login('admin')
    cy.visit('/admin/dashboard')
    cy.get('[data-cy="admin-dashboard"]').should('be.visible')
  })

  it('debe completar flujo de logout y acceso denegado', () => {
    cy.login('farmer')
    cy.visit('/agricultor-dashboard')
    
    // Hacer logout
    cy.get('[data-cy="user-menu"]').click()
    cy.get('[data-cy="logout-button"]').click()
    cy.get('[data-cy="confirm-logout"]').click()
    
    // Verificar redirección al login
    cy.url().should('include', '/login')
    
    // Intentar acceder a página protegida
    cy.visit('/agricultor-dashboard')
    cy.url().should('include', '/login')
  })

  it('debe completar flujo de navegación con breadcrumbs', () => {
    cy.login('farmer')
    
    // Navegar con breadcrumbs
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-item"]').first().click()
    cy.get('[data-cy="breadcrumb-fincas"]').should('be.visible')
    
    cy.get('[data-cy="lote-item"]').first().click()
    cy.get('[data-cy="breadcrumb-lotes"]').should('be.visible')
    
    // Usar breadcrumbs para navegar
    cy.get('[data-cy="breadcrumb-fincas"]').click()
    cy.get('[data-cy="finca-details"]').should('be.visible')
    
    cy.get('[data-cy="breadcrumb-home"]').click()
    cy.url().should('include', '/agricultor-dashboard')
  })

  it('debe completar flujo de búsqueda y filtros', () => {
    cy.login('farmer')
    
    // Buscar en fincas
    cy.visit('/mis-fincas')
    cy.get('[data-cy="search-fincas"]').type('Paraíso')
    cy.get('[data-cy="finca-item"]').should('contain', 'Paraíso')
    
    // Buscar en lotes
    cy.visit('/mis-lotes')
    cy.get('[data-cy="search-lotes"]').type('Norte')
    cy.get('[data-cy="lote-item"]').should('contain', 'Norte')
    
    // Buscar en análisis
    cy.visit('/mis-analisis')
    cy.get('[data-cy="search-analisis"]').type('test-cacao')
    cy.get('[data-cy="analisis-item"]').should('contain', 'test-cacao')
  })

  it('debe completar flujo de exportación múltiple', () => {
    cy.login('farmer')
    
    // Exportar múltiples fincas
    cy.visit('/mis-fincas')
    cy.get('[data-cy="finca-checkbox"]').first().check()
    cy.get('[data-cy="finca-checkbox"]').eq(1).check()
    cy.get('[data-cy="bulk-export"]').click()
    cy.verifyDownload('fincas-seleccionadas.pdf')
    
    // Exportar múltiples lotes
    cy.visit('/mis-lotes')
    cy.get('[data-cy="lote-checkbox"]').first().check()
    cy.get('[data-cy="lote-checkbox"]').eq(1).check()
    cy.get('[data-cy="bulk-export"]').click()
    cy.verifyDownload('lotes-seleccionados.xlsx')
  })

  it('debe completar flujo de notificaciones', () => {
    cy.login('farmer')
    
    // Ver notificaciones
    cy.get('[data-cy="notifications-bell"]').click()
    cy.get('[data-cy="notifications-list"]').should('be.visible')
    
    // Marcar como leída
    cy.get('[data-cy="notification-item"]').first().click()
    cy.get('[data-cy="mark-read"]').click()
    
    // Marcar todas como leídas
    cy.get('[data-cy="mark-all-read"]').click()
    cy.checkNotification('Todas las notificaciones marcadas como leídas', 'success')
  })
})
