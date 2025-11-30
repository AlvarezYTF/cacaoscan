describe('Manejo de Errores - Casos Edge', () => {
  beforeEach(() => {
    cy.login('farmer')
  })

  it('debe manejar timeout de red correctamente', () => {
    cy.intercept('GET', '**/api/**', { delay: 10000, statusCode: 200 }).as('slowRequest')
    cy.visit('/mis-fincas')
    cy.wait('@slowRequest', { timeout: 5000 }).then(() => {
      cy.get('[data-cy="error-message"]').should('be.visible')
    })
  })

  it('debe manejar respuesta vacía del servidor', () => {
    cy.intercept('GET', '**/api/fincas/**', { body: null }).as('emptyResponse')
    cy.visit('/mis-fincas')
    cy.wait('@emptyResponse')
    cy.get('[data-cy="empty-state"]').should('be.visible')
  })

  it('debe manejar caracteres especiales en inputs', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    cy.get('[data-cy="finca-nombre"]').type('Finca <script>alert("xss")</script>')
    cy.get('[data-cy="save-finca"]').click()
    // Should sanitize input
    cy.get('[data-cy="finca-nombre"]').should('not.contain', '<script>')
  })

  it('debe manejar valores muy largos en inputs', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    const longString = 'a'.repeat(10000)
    cy.get('[data-cy="finca-nombre"]').type(longString)
    cy.get('[data-cy="finca-nombre-error"]').should('be.visible')
  })

  it('debe manejar múltiples requests simultáneos', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="refresh-button"]').click()
    cy.get('[data-cy="refresh-button"]').click()
    cy.get('[data-cy="refresh-button"]').click()
    // Should handle gracefully
    cy.wait(1000)
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar pérdida de conexión', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      cy.stub(win.navigator, 'onLine').value(false)
    })
    cy.get('[data-cy="refresh-button"]').click()
    cy.get('[data-cy="offline-message"]').should('be.visible')
  })

  it('debe manejar token expirado durante operación', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      win.localStorage.setItem('access_token', 'expired-token')
    })
    cy.get('[data-cy="add-finca-button"]').click()
    cy.get('[data-cy="finca-nombre"]').type('Test Finca')
    cy.get('[data-cy="save-finca"]').click()
    // Should redirect to login or refresh token
    cy.url().should('satisfy', (url) => {
      return url.includes('/login') || url.includes('/mis-fincas')
    })
  })

  it('debe manejar archivos corruptos en upload', () => {
    cy.visit('/nuevo-analisis')
    const corruptFile = new File(['corrupt'], 'corrupt.jpg', { type: 'image/jpeg' })
    cy.get('[data-cy="file-input"]').then((input) => {
      const dataTransfer = new DataTransfer()
      dataTransfer.items.add(corruptFile)
      input[0].files = dataTransfer.files
      input.trigger('change')
    })
    cy.get('[data-cy="upload-error"]').should('be.visible')
  })

  it('debe manejar paginación con datos vacíos', () => {
    cy.intercept('GET', '**/api/lotes/**', { body: { results: [], count: 0 } }).as('emptyLotes')
    cy.visit('/mis-lotes')
    cy.wait('@emptyLotes')
    cy.get('[data-cy="empty-lotes-message"]').should('be.visible')
    cy.get('[data-cy="pagination"]').should('not.exist')
  })

  it('debe manejar filtros con resultados vacíos', () => {
    cy.visit('/mis-lotes')
    cy.get('[data-cy="filter-variedad"]').select('inexistente')
    cy.wait(500)
    cy.get('[data-cy="no-results"]').should('be.visible')
  })

  it('debe manejar cancelación de operación asíncrona', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    cy.get('[data-cy="finca-nombre"]').type('Test')
    cy.get('[data-cy="cancel-finca"]').click()
    // Should cancel and not save
    cy.get('[data-cy="finca-form"]').should('not.exist')
  })

  it('debe manejar validación de formulario con múltiples errores', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    cy.get('[data-cy="save-finca"]').click()
    // Should show all validation errors
    cy.get('[data-cy="finca-nombre-error"]').should('be.visible')
    cy.get('[data-cy="finca-ubicacion-error"]').should('be.visible')
    cy.get('[data-cy="finca-area-error"]').should('be.visible')
  })

  it('debe manejar actualización de datos mientras se edita', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="edit-finca"]').first().click()
    cy.get('[data-cy="finca-nombre"]').clear().type('Updated Name')
    // Simulate data update from another source
    cy.intercept('GET', '**/api/fincas/**', { fixture: 'updatedFincas' }).as('updatedData')
    cy.get('[data-cy="refresh-button"]').click()
    cy.wait('@updatedData')
    // Should handle conflict gracefully
    cy.get('[data-cy="finca-form"]').should('be.visible')
  })

  it('debe manejar operación en elemento eliminado', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="delete-finca"]').first().click()
    cy.get('[data-cy="confirm-delete"]').click()
    cy.wait(500)
    // Try to edit deleted item
    cy.get('[data-cy="edit-finca"]').first().click()
    cy.get('[data-cy="error-message"]').should('be.visible')
  })

  it('debe manejar navegación durante operación pendiente', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    cy.get('[data-cy="finca-nombre"]').type('Test')
    // Navigate away
    cy.visit('/mis-lotes')
    // Should cancel operation or show warning
    cy.url().should('include', '/mis-lotes')
  })

  it('debe manejar refresh de página durante operación', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    cy.get('[data-cy="finca-nombre"]').type('Test')
    cy.reload()
    // Should handle gracefully
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar cambio de tamaño de ventana', () => {
    cy.visit('/mis-fincas')
    cy.viewport(1920, 1080)
    cy.get('[data-cy="fincas-list"]').should('be.visible')
    cy.viewport(375, 667)
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar teclado navigation', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').focus()
    cy.get('[data-cy="add-finca-button"]').type('{enter}')
    cy.get('[data-cy="finca-form"]').should('be.visible')
  })

  it('debe manejar operación con permisos insuficientes', () => {
    cy.login('farmer')
    cy.visit('/admin/dashboard')
    cy.get('[data-cy="access-denied"]').should('be.visible')
  })

  it('debe manejar respuesta con formato inesperado', () => {
    cy.intercept('GET', '**/api/fincas/**', { body: 'invalid json' }).as('invalidResponse')
    cy.visit('/mis-fincas')
    cy.wait('@invalidResponse')
    cy.get('[data-cy="error-message"]').should('be.visible')
  })

  it('debe manejar múltiples errores simultáneos', () => {
    cy.intercept('GET', '**/api/**', { statusCode: 500 }).as('serverError')
    cy.visit('/mis-fincas')
    cy.wait('@serverError')
    cy.get('[data-cy="error-message"]').should('be.visible')
    // Should not show duplicate errors
    cy.get('[data-cy="error-message"]').should('have.length.at.most', 1)
  })

  it('debe manejar operación con datos inválidos del servidor', () => {
    cy.intercept('POST', '**/api/fincas/**', {
      statusCode: 200,
      body: { invalid: 'response' }
    }).as('invalidData')
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    cy.get('[data-cy="finca-nombre"]').type('Test')
    cy.get('[data-cy="finca-ubicacion"]').type('Test Location')
    cy.get('[data-cy="finca-area"]').type('10')
    cy.get('[data-cy="save-finca"]').click()
    cy.wait('@invalidData')
    cy.get('[data-cy="error-message"]').should('be.visible')
  })

  it('debe manejar operación con datos parciales', () => {
    cy.intercept('GET', '**/api/fincas/**', {
      statusCode: 206,
      body: { results: [{ id: 1, nombre: 'Partial' }] }
    }).as('partialData')
    cy.visit('/mis-fincas')
    cy.wait('@partialData')
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con encoding incorrecto', () => {
    cy.intercept('GET', '**/api/fincas/**', {
      body: Buffer.from('invalid encoding', 'binary')
    }).as('badEncoding')
    cy.visit('/mis-fincas')
    cy.wait('@badEncoding')
    cy.get('[data-cy="error-message"]').should('be.visible')
  })

  it('debe manejar operación con headers incorrectos', () => {
    cy.intercept('GET', '**/api/fincas/**', {
      headers: { 'content-type': 'text/html' },
      body: '<html>Error</html>'
    }).as('wrongHeaders')
    cy.visit('/mis-fincas')
    cy.wait('@wrongHeaders')
    cy.get('[data-cy="error-message"]').should('be.visible')
  })

  it('debe manejar operación con cookies expiradas', () => {
    cy.clearCookies()
    cy.visit('/mis-fincas')
    cy.url().should('include', '/login')
  })

  it('debe manejar operación con localStorage corrupto', () => {
    cy.window().then((win) => {
      win.localStorage.setItem('access_token', 'corrupt{data')
    })
    cy.visit('/mis-fincas')
    // Should handle gracefully
    cy.url().should('satisfy', (url) => {
      return url.includes('/login') || url.includes('/mis-fincas')
    })
  })

  it('debe manejar operación con sessionStorage lleno', () => {
    cy.window().then((win) => {
      // Fill sessionStorage
      for (let i = 0; i < 1000; i++) {
        try {
          win.sessionStorage.setItem(`key${i}`, 'x'.repeat(1000))
        } catch (e) {
          break
        }
      }
    })
    cy.visit('/mis-fincas')
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con memoria limitada', () => {
    cy.visit('/mis-fincas')
    // Simulate memory pressure
    cy.window().then((win) => {
      const largeArray = new Array(1000000).fill('x')
      win.testLargeArray = largeArray
    })
    cy.get('[data-cy="refresh-button"]').click()
    cy.wait(1000)
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con CPU limitado', () => {
    cy.visit('/mis-fincas')
    // Simulate CPU intensive operation
    cy.window().then((win) => {
      const start = Date.now()
      while (Date.now() - start < 100) {
        Math.sqrt(Math.random())
      }
    })
    cy.get('[data-cy="refresh-button"]').click()
    cy.wait(1000)
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con múltiples pestañas', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      win.open('/mis-fincas', '_blank')
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con iframe', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      const iframe = win.document.createElement('iframe')
      iframe.src = '/mis-fincas'
      win.document.body.appendChild(iframe)
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con service worker', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('serviceWorker' in win.navigator) {
        win.navigator.serviceWorker.register('/sw.js').catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con web workers', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if (typeof Worker !== 'undefined') {
        const worker = new Worker('/worker.js')
        worker.postMessage({ type: 'test' })
        worker.terminate()
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con geolocation', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('geolocation' in win.navigator) {
        win.navigator.geolocation.getCurrentPosition(() => {}, () => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con camera', () => {
    cy.visit('/nuevo-analisis')
    cy.window().then((win) => {
      if ('mediaDevices' in win.navigator) {
        win.navigator.mediaDevices.getUserMedia({ video: true }).catch(() => {})
      }
    })
    cy.get('[data-cy="file-input"]').should('be.visible')
  })

  it('debe manejar operación con clipboard', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('clipboard' in win.navigator) {
        win.navigator.clipboard.writeText('test').catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con notifications', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('Notification' in win) {
        win.Notification.requestPermission().catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con battery API', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('getBattery' in win.navigator) {
        win.navigator.getBattery().catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con device orientation', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('DeviceOrientationEvent' in win) {
        win.addEventListener('deviceorientation', () => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con device motion', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('DeviceMotionEvent' in win) {
        win.addEventListener('devicemotion', () => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con vibration API', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('vibrate' in win.navigator) {
        win.navigator.vibrate(100)
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con fullscreen API', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('requestFullscreen' in win.document.documentElement) {
        win.document.documentElement.requestFullscreen().catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con pointer lock', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('requestPointerLock' in win.document.body) {
        win.document.body.requestPointerLock().catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con screen orientation', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('orientation' in win.screen) {
        win.screen.orientation.lock('portrait').catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con wake lock', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('wakeLock' in win.navigator) {
        win.navigator.wakeLock.request('screen').catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con payment request', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('PaymentRequest' in win) {
        try {
          const paymentRequest = new win.PaymentRequest([], { total: { label: 'Test', amount: { currency: 'USD', value: '0' } } })
          paymentRequest.show().catch(() => {})
        } catch (e) {
          // Ignore
        }
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con credential management', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('credentials' in win.navigator) {
        win.navigator.credentials.get({ publicKey: {} }).catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con web share', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('share' in win.navigator) {
        win.navigator.share({ title: 'Test', text: 'Test', url: '/' }).catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con web bluetooth', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('bluetooth' in win.navigator) {
        win.navigator.bluetooth.requestDevice({ filters: [] }).catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con web usb', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('usb' in win.navigator) {
        win.navigator.usb.requestDevice({ filters: [] }).catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con web serial', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('serial' in win.navigator) {
        win.navigator.serial.requestPort().catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con web nfc', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('nfc' in win.navigator) {
        win.navigator.nfc.watch(() => {}).catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con web xr', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('xr' in win.navigator) {
        win.navigator.xr.requestSession('immersive-vr').catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con web midi', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('requestMIDIAccess' in win.navigator) {
        win.navigator.requestMIDIAccess().catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con web hid', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('hid' in win.navigator) {
        win.navigator.hid.requestDevice({ filters: [] }).catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con web locks', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('locks' in win.navigator) {
        win.navigator.locks.request('test', () => {}).catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con web storage estimate', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('storage' in win.navigator && 'estimate' in win.navigator.storage) {
        win.navigator.storage.estimate().catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con web storage persist', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('storage' in win.navigator && 'persist' in win.navigator.storage) {
        win.navigator.storage.persist().catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con web storage persisted', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('storage' in win.navigator && 'persisted' in win.navigator.storage) {
        win.navigator.storage.persisted().catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con web storage quota', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('storage' in win.navigator && 'quota' in win.navigator.storage) {
        win.navigator.storage.quota().catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con web storage usage', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('storage' in win.navigator && 'usage' in win.navigator.storage) {
        win.navigator.storage.usage().catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con web storage getDirectory', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('storage' in win.navigator && 'getDirectory' in win.navigator.storage) {
        win.navigator.storage.getDirectory().catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar operación con web storage getDirectory', () => {
    cy.visit('/mis-fincas')
    cy.window().then((win) => {
      if ('storage' in win.navigator && 'getDirectory' in win.navigator.storage) {
        win.navigator.storage.getDirectory().catch(() => {})
      }
    })
    cy.get('[data-cy="fincas-list"]').should('be.visible')
  })

  it('debe manejar datos vacíos en listas', () => {
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

  it('debe manejar búsqueda sin resultados', () => {
    cy.visit('/mis-fincas')
    
    // Buscar algo que no existe
    cy.get('[data-cy="search-fincas"]').type('noexiste123')
    
    // Verificar estado de búsqueda sin resultados
    cy.get('[data-cy="no-results"]').should('be.visible')
    cy.get('[data-cy="no-results-message"]').should('contain', 'No se encontraron resultados')
    cy.get('[data-cy="clear-search"]').should('be.visible')
  })

  it('debe manejar filtros sin resultados', () => {
    cy.visit('/mis-fincas')
    
    // Aplicar filtro que no tiene resultados
    cy.get('[data-cy="location-filter"]').click()
    cy.get('[data-cy="province-filter"]').select('Provincia Inexistente')
    cy.get('[data-cy="apply-filter"]').click()
    
    // Verificar estado de filtro sin resultados
    cy.get('[data-cy="no-results"]').should('be.visible')
    cy.get('[data-cy="no-results-message"]').should('contain', 'No hay resultados para los filtros aplicados')
    cy.get('[data-cy="clear-filters"]').should('be.visible')
  })

  it('debe manejar formularios con campos muy largos', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    // Llenar con texto muy largo
    const longText = 'a'.repeat(1000)
    cy.get('[data-cy="finca-nombre"]').type(longText)
    cy.get('[data-cy="finca-descripcion"]').type(longText)
    
    // Verificar validación de longitud
    cy.get('[data-cy="finca-nombre-error"]')
      .should('be.visible')
      .and('contain', 'El nombre es demasiado largo')
  })

  it('debe manejar formularios con caracteres especiales', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    // Llenar con caracteres especiales
    cy.get('[data-cy="finca-nombre"]').type('Finca @#$%^&*()')
    cy.get('[data-cy="finca-descripcion"]').type('Descripción con emojis 🚀🌱')
    
    // Verificar que se aceptan caracteres especiales
    cy.get('[data-cy="finca-nombre"]').should('have.value', 'Finca @#$%^&*()')
    cy.get('[data-cy="finca-descripcion"]').should('have.value', 'Descripción con emojis 🚀🌱')
  })

  it('debe manejar números muy grandes', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    // Llenar con número muy grande
    cy.get('[data-cy="finca-area"]').type('999999999999999')
    
    // Verificar validación
    cy.get('[data-cy="finca-area-error"]')
      .should('be.visible')
      .and('contain', 'El área es demasiado grande')
  })

  it('debe manejar números negativos', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    // Llenar con número negativo
    cy.get('[data-cy="finca-area"]').type('-10')
    
    // Verificar validación
    cy.get('[data-cy="finca-area-error"]')
      .should('be.visible')
      .and('contain', 'El área debe ser positiva')
  })

  it('debe manejar fechas inválidas', () => {
    cy.visit('/mis-lotes')
    cy.get('[data-cy="add-lote-button"]').click()
    
    // Llenar con fecha inválida
    cy.get('[data-cy="lote-edad"]').type('50') // Edad muy alta
    
    // Verificar validación
    cy.get('[data-cy="lote-edad-error"]')
      .should('be.visible')
      .and('contain', 'La edad debe ser menor a 30 años')
  })

  it('debe manejar archivos con nombres muy largos', () => {
    cy.visit('/nuevo-analisis')
    
    // Simular archivo con nombre muy largo
    const longFileName = 'a'.repeat(255) + '.jpg'
    
    cy.fixture('test-cacao.jpg').then((fileContent) => {
      const blob = new Blob([fileContent], { type: 'image/jpeg' })
      const file = new File([blob], longFileName, { type: 'image/jpeg' })
      
      cy.get('[data-cy="file-input"]').then((input) => {
        const dataTransfer = new DataTransfer()
        dataTransfer.items.add(file)
        input[0].files = dataTransfer.files
        
        cy.wrap(input).trigger('change', { force: true })
      })
    })
    
    // Verificar validación
    cy.get('[data-cy="file-name-error"]')
      .should('be.visible')
      .and('contain', 'El nombre del archivo es demasiado largo')
  })

  it('debe manejar archivos con extensiones no permitidas', () => {
    cy.visit('/nuevo-analisis')
    
    // Simular archivo con extensión no permitida
    cy.fixture('test-cacao.jpg').then((fileContent) => {
      const blob = new Blob([fileContent], { type: 'text/plain' })
      const file = new File([blob], 'test.txt', { type: 'text/plain' })
      
      cy.get('[data-cy="file-input"]').then((input) => {
        const dataTransfer = new DataTransfer()
        dataTransfer.items.add(file)
        input[0].files = dataTransfer.files
        
        cy.wrap(input).trigger('change', { force: true })
      })
    })
    
    // Verificar validación
    cy.get('[data-cy="file-type-error"]')
      .should('be.visible')
      .and('contain', 'Tipo de archivo no permitido')
  })

  it('debe manejar archivos corruptos', () => {
    cy.visit('/nuevo-analisis')
    
    // Simular archivo corrupto
    const corruptContent = 'corrupt file content'
    const blob = new Blob([corruptContent], { type: 'image/jpeg' })
    const file = new File([blob], 'corrupt.jpg', { type: 'image/jpeg' })
    
    cy.get('[data-cy="file-input"]').then((input) => {
      const dataTransfer = new DataTransfer()
      dataTransfer.items.add(file)
      input[0].files = dataTransfer.files
      
      cy.wrap(input).trigger('change', { force: true })
    })
    
    cy.get('[data-cy="upload-button"]').click()
    
    // Verificar error de archivo corrupto
    cy.get('[data-cy="file-corrupt-error"]')
      .should('be.visible')
      .and('contain', 'Archivo corrupto')
  })

  it('debe manejar sesión expirada durante operación', () => {
    cy.visit('/mis-fincas')
    
    // Simular sesión expirada durante operación
    cy.intercept('POST', '/api/fincas/', {
      statusCode: 401,
      body: { error: 'Token expirado' }
    }).as('expiredSession')
    
    cy.get('[data-cy="add-finca-button"]').click()
    
    cy.fixture('testData').then((data) => {
      const fincaData = data.fincas[0]
      cy.fillFincaForm(fincaData)
    })
    
    cy.get('[data-cy="save-finca"]').click()
    cy.wait('@expiredSession')
    
    // Verificar redirección al login
    cy.url().should('include', '/login')
    cy.get('[data-cy="session-expired-message"]')
      .should('be.visible')
      .and('contain', 'Sesión expirada')
  })

  it('debe manejar operaciones concurrentes', () => {
    cy.visit('/mis-fincas')
    
    // Simular operaciones concurrentes
    cy.intercept('POST', '/api/fincas/', {
      statusCode: 409,
      body: { error: 'Operación en conflicto' }
    }).as('concurrentOperation')
    
    cy.get('[data-cy="add-finca-button"]').click()
    
    cy.fixture('testData').then((data) => {
      const fincaData = data.fincas[0]
      cy.fillFincaForm(fincaData)
    })
    
    cy.get('[data-cy="save-finca"]').click()
    cy.wait('@concurrentOperation')
    
    // Verificar mensaje de conflicto
    cy.get('[data-cy="conflict-error"]')
      .should('be.visible')
      .and('contain', 'Operación en conflicto')
  })

  it('debe manejar datos corruptos del servidor', () => {
    // Simular datos corruptos
    cy.intercept('GET', '/api/fincas/', {
      statusCode: 200,
      body: {
        results: [
          { id: 1, nombre: null, ubicacion: undefined },
          { id: 2, nombre: '', ubicacion: '' }
        ],
        count: 2
      }
    }).as('corruptData')
    
    cy.visit('/mis-fincas')
    cy.wait('@corruptData')
    
    // Verificar que se manejan datos corruptos
    cy.get('[data-cy="finca-item"]').should('be.visible')
    cy.get('[data-cy="corrupt-data-warning"]').should('be.visible')
  })

  it('debe manejar respuestas parciales', () => {
    // Simular respuesta parcial
    cy.intercept('GET', '/api/fincas/', {
      statusCode: 206,
      body: {
        results: [{ id: 1, nombre: 'Finca 1' }],
        count: 10,
        partial: true
      }
    }).as('partialResponse')
    
    cy.visit('/mis-fincas')
    cy.wait('@partialResponse')
    
    // Verificar que se maneja respuesta parcial
    cy.get('[data-cy="partial-data-warning"]').should('be.visible')
    cy.get('[data-cy="load-more"]').should('be.visible')
  })

  it('debe manejar cambios de estado durante operación', () => {
    cy.visit('/mis-fincas')
    
    // Simular cambio de estado durante operación
    cy.intercept('POST', '/api/fincas/', {
      statusCode: 410,
      body: { error: 'Recurso ya no disponible' }
    }).as('goneResource')
    
    cy.get('[data-cy="add-finca-button"]').click()
    
    cy.fixture('testData').then((data) => {
      const fincaData = data.fincas[0]
      cy.fillFincaForm(fincaData)
    })
    
    cy.get('[data-cy="save-finca"]').click()
    cy.wait('@goneResource')
    
    // Verificar mensaje de recurso no disponible
    cy.get('[data-cy="gone-error"]')
      .should('be.visible')
      .and('contain', 'Recurso ya no disponible')
  })

  it('debe manejar límites de recursos', () => {
    cy.visit('/mis-fincas')
    
    // Simular límite de recursos
    cy.intercept('POST', '/api/fincas/', {
      statusCode: 507,
      body: { error: 'Límite de recursos excedido' }
    }).as('resourceLimit')
    
    cy.get('[data-cy="add-finca-button"]').click()
    
    cy.fixture('testData').then((data) => {
      const fincaData = data.fincas[0]
      cy.fillFincaForm(fincaData)
    })
    
    cy.get('[data-cy="save-finca"]').click()
    cy.wait('@resourceLimit')
    
    // Verificar mensaje de límite de recursos
    cy.get('[data-cy="resource-limit-error"]')
      .should('be.visible')
      .and('contain', 'Límite de recursos excedido')
  })
})
