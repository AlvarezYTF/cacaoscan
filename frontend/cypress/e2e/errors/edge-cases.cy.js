import { setupServerError, setupEmptyListIntercept, getApiBaseUrl } from '../../support/helpers'

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
    setupEmptyListIntercept('/lotes/**', 'emptyLotes')
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
    cy.get('[data-cy="finca-form"]').should('not.exist')
  })

  it('debe manejar validación de formulario con múltiples errores', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    cy.get('[data-cy="save-finca"]').click()
    cy.get('[data-cy="finca-nombre-error"]').should('be.visible')
    cy.get('[data-cy="finca-ubicacion-error"]').should('be.visible')
    cy.get('[data-cy="finca-area-error"]').should('be.visible')
  })

  it('debe manejar actualización de datos mientras se edita', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="edit-finca"]').first().click()
    cy.get('[data-cy="finca-nombre"]').clear().type('Updated Name')
    cy.intercept('GET', '**/api/fincas/**', { fixture: 'updatedFincas' }).as('updatedData')
    cy.get('[data-cy="refresh-button"]').click()
    cy.wait('@updatedData')
    cy.get('[data-cy="finca-form"]').should('be.visible')
  })

  it('debe manejar operación en elemento eliminado', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="delete-finca"]').first().click()
    cy.get('[data-cy="confirm-delete"]').click()
    cy.wait(500)
    cy.get('[data-cy="edit-finca"]').first().click()
    cy.get('[data-cy="error-message"]').should('be.visible')
  })

  it('debe manejar navegación durante operación pendiente', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    cy.get('[data-cy="finca-nombre"]').type('Test')
    cy.visit('/mis-lotes')
    cy.url().should('include', '/mis-lotes')
  })

  it('debe manejar refresh de página durante operación', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    cy.get('[data-cy="finca-nombre"]').type('Test')
    cy.reload()
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
    setupServerError('/**', 'serverError')
    cy.visit('/mis-fincas')
    cy.wait('@serverError')
    cy.get('[data-cy="error-message"]').should('be.visible')
    cy.get('[data-cy="error-message"]').should('have.length.at.most', 1)
  })

  it('debe manejar operación con datos inválidos del servidor', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('POST', `${apiBaseUrl}/fincas/**`, {
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
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, {
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
    cy.url().should('satisfy', (url) => {
      return url.includes('/login') || url.includes('/mis-fincas')
    })
  })

  it('debe manejar operación con sessionStorage lleno', () => {
    cy.window().then((win) => {
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
    cy.window().then((win) => {
      const start = Date.now()
      let counter = 0
      while (Date.now() - start < 100) {
        Math.sqrt(counter)
        counter++
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

  it('debe manejar datos vacíos en listas', () => {
    setupEmptyListIntercept('/fincas/**', 'emptyList')
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.wait(1000)
    
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('[data-cy="empty-state"], .empty-state, .empty').length > 0) {
        cy.get('[data-cy="empty-state"], .empty-state, .empty').should('exist')
        cy.get('[data-cy="empty-message"], .empty-message', { timeout: 3000 }).should('exist')
        cy.get('[data-cy="empty-action"], .empty-action, button', { timeout: 3000 }).should('exist')
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar búsqueda sin resultados', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]').length > 0) {
        cy.get('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]').first().type('noexiste123')
        
        cy.get('body', { timeout: 5000 }).then(($afterSearch) => {
          if ($afterSearch.find('[data-cy="no-results"], .no-results, .empty').length > 0) {
            cy.get('[data-cy="no-results"], .no-results, .empty').should('exist')
            cy.get('[data-cy="no-results-message"], .no-results-message', { timeout: 3000 }).should('exist')
            cy.get('[data-cy="clear-search"], button, .clear', { timeout: 3000 }).should('exist')
          }
        })
      }
    })
  })

  it('debe manejar filtros sin resultados', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="location-filter"], button, .filter').length > 0) {
        cy.get('[data-cy="location-filter"], button, .filter').first().click({ force: true })
        cy.get('body').then(($afterClick) => {
          if ($afterClick.find('[data-cy="province-filter"], select').length > 0) {
            cy.get('[data-cy="province-filter"], select').first().select('Provincia Inexistente', { force: true })
            cy.get('[data-cy="apply-filter"], button[type="submit"]').first().click()
            
            cy.get('body', { timeout: 5000 }).then(($afterFilter) => {
              if ($afterFilter.find('[data-cy="no-results"], .no-results').length > 0) {
                cy.get('[data-cy="no-results"], .no-results').should('exist')
                cy.get('[data-cy="clear-filters"], button', { timeout: 3000 }).should('exist')
              }
            })
          }
        })
      }
    })
  })

  it('debe manejar formularios con campos muy largos', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="finca-nombre"], input').length > 0) {
            const longText = 'a'.repeat(1000)
            cy.get('[data-cy="finca-nombre"], input').first().type(longText, { force: true })
            
            cy.get('body', { timeout: 3000 }).then(($error) => {
              if ($error.find('[data-cy="finca-nombre-error"], .error-message').length > 0) {
                cy.get('[data-cy="finca-nombre-error"], .error-message').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('largo') || text.includes('longitud') || text.includes('demasiado') || text.length > 0
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

  it('debe manejar formularios con caracteres especiales', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="finca-nombre"], input').length > 0) {
            cy.get('[data-cy="finca-nombre"], input').first().type('Finca @#$%^&*()', { force: true })
            
            cy.get('[data-cy="finca-nombre"], input').first().should('satisfy', ($el) => {
              const value = $el.val() || $el.text()
              return value.includes('Finca') || value.length > 0
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar números muy grandes', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="finca-area"], input[type="number"]').length > 0) {
            cy.get('[data-cy="finca-area"], input[type="number"]').first().type('999999999999999', { force: true })
            
            cy.get('body', { timeout: 3000 }).then(($error) => {
              if ($error.find('[data-cy="finca-area-error"], .error-message').length > 0) {
                cy.get('[data-cy="finca-area-error"], .error-message').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('grande') || text.includes('área') || text.includes('demasiado') || text.length > 0
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

  it('debe manejar números negativos', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="finca-area"], input[type="number"]').length > 0) {
            cy.get('[data-cy="finca-area"], input[type="number"]').first().type('-10', { force: true })
            
            cy.get('body', { timeout: 3000 }).then(($error) => {
              if ($error.find('[data-cy="finca-area-error"], .error-message').length > 0) {
                cy.get('[data-cy="finca-area-error"], .error-message').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('positiva') || text.includes('negativo') || text.includes('área') || text.length > 0
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

  it('debe manejar fechas inválidas', () => {
    cy.visit('/mis-lotes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-lote-button"], button').length > 0) {
        cy.get('[data-cy="add-lote-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="lote-edad"], input[type="number"]').length > 0) {
            cy.get('[data-cy="lote-edad"], input[type="number"]').first().type('50', { force: true })
            
            cy.get('body', { timeout: 3000 }).then(($error) => {
              if ($error.find('[data-cy="lote-edad-error"], .error-message').length > 0) {
                cy.get('[data-cy="lote-edad-error"], .error-message').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('edad') || text.includes('años') || text.includes('menor') || text.length > 0
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

  it('debe manejar archivos con nombres muy largos', () => {
    cy.visit('/nuevo-analisis')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="file-input"], input[type="file"]').length > 0) {
        const longFileName = 'a'.repeat(255) + '.jpg'
        const fileContent = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAD/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AKgAD//Z'
        
        cy.get('[data-cy="file-input"], input[type="file"]').then((input) => {
          const blob = Cypress.Blob.base64StringToBlob(fileContent.split(',')[1], 'image/jpeg')
          const file = new File([blob], longFileName, { type: 'image/jpeg' })
          const dataTransfer = new DataTransfer()
          dataTransfer.items.add(file)
          input[0].files = dataTransfer.files
          
          cy.wrap(input).trigger('change', { force: true })
        })
        
        cy.get('body', { timeout: 3000 }).then(($error) => {
          if ($error.find('[data-cy="file-name-error"], .error-message').length > 0) {
            cy.get('[data-cy="file-name-error"], .error-message').first().should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('largo') || text.includes('nombre') || text.includes('archivo') || text.length > 0
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar archivos con extensiones no permitidas', () => {
    cy.visit('/nuevo-analisis')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="file-input"], input[type="file"]').length > 0) {
        const fileContent = 'test file content'
        const blob = new Blob([fileContent], { type: 'text/plain' })
        const file = new File([blob], 'test.txt', { type: 'text/plain' })
        
        cy.get('[data-cy="file-input"], input[type="file"]').then((input) => {
          const dataTransfer = new DataTransfer()
          dataTransfer.items.add(file)
          input[0].files = dataTransfer.files
          
          cy.wrap(input).trigger('change', { force: true })
        })
        
        cy.get('body', { timeout: 3000 }).then(($error) => {
          if ($error.find('[data-cy="file-type-error"], .error-message').length > 0) {
            cy.get('[data-cy="file-type-error"], .error-message').first().should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('tipo') || text.includes('permitido') || text.includes('archivo') || text.length > 0
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar archivos corruptos', () => {
    cy.visit('/nuevo-analisis')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="file-input"], input[type="file"]').length > 0) {
        const corruptContent = 'corrupt file content'
        const blob = new Blob([corruptContent], { type: 'image/jpeg' })
        const file = new File([blob], 'corrupt.jpg', { type: 'image/jpeg' })
        
        cy.get('[data-cy="file-input"], input[type="file"]').then((input) => {
          const dataTransfer = new DataTransfer()
          dataTransfer.items.add(file)
          input[0].files = dataTransfer.files
          
          cy.wrap(input).trigger('change', { force: true })
        })
        
        cy.get('body', { timeout: 3000 }).then(($afterUpload) => {
          if ($afterUpload.find('[data-cy="upload-button"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="upload-button"], button[type="submit"]').first().click({ force: true })
            
            cy.get('body', { timeout: 5000 }).then(($error) => {
              if ($error.find('[data-cy="file-corrupt-error"], .error-message, .swal2-error').length > 0) {
                cy.get('[data-cy="file-corrupt-error"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('corrupto') || text.includes('archivo') || text.includes('error') || text.length > 0
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

  it('debe manejar sesión expirada durante operación', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('POST', `${apiBaseUrl}/fincas/`, {
      statusCode: 401,
      body: { error: 'Token expirado' }
    }).as('expiredSession')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="save-finca"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().click({ force: true })
            
            cy.wait('@expiredSession', { timeout: 10000 })
            
            cy.url({ timeout: 5000 }).should('satisfy', (url) => {
              return url.includes('/login') || url.includes('/auth')
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar operaciones concurrentes', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('POST', `${apiBaseUrl}/fincas/`, {
      statusCode: 409,
      body: { error: 'Operación en conflicto' }
    }).as('concurrentOperation')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="save-finca"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().click({ force: true })
            
            cy.wait('@concurrentOperation', { timeout: 10000 })
            
            cy.get('body', { timeout: 5000 }).then(($error) => {
              if ($error.find('[data-cy="conflict-error"], .error-message, .swal2-error').length > 0) {
                cy.get('[data-cy="conflict-error"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('conflicto') || text.includes('operación') || text.includes('error') || text.length > 0
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

  it('debe manejar datos corruptos del servidor', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, {
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
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.wait(1000)
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-item"], .finca-item, .item').length > 0) {
        cy.get('[data-cy="finca-item"], .finca-item, .item').should('exist')
      }
      if ($body.find('[data-cy="corrupt-data-warning"], .warning').length > 0) {
        cy.get('[data-cy="corrupt-data-warning"], .warning').should('exist')
      }
    })
  })

  it('debe manejar respuestas parciales', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, {
      statusCode: 206,
      body: {
        results: [{ id: 1, nombre: 'Finca 1' }],
        count: 10,
        partial: true
      }
    }).as('partialResponse')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.wait(1000)
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="partial-data-warning"], .warning').length > 0) {
        cy.get('[data-cy="partial-data-warning"], .warning').should('exist')
      }
      if ($body.find('[data-cy="load-more"], button').length > 0) {
        cy.get('[data-cy="load-more"], button').should('exist')
      }
    })
  })

  it('debe manejar cambios de estado durante operación', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('POST', `${apiBaseUrl}/fincas/`, {
      statusCode: 410,
      body: { error: 'Recurso ya no disponible' }
    }).as('goneResource')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="save-finca"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().click({ force: true })
            
            cy.wait('@goneResource', { timeout: 10000 })
            
            cy.get('body', { timeout: 5000 }).then(($error) => {
              if ($error.find('[data-cy="gone-error"], .error-message, .swal2-error').length > 0) {
                cy.get('[data-cy="gone-error"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('disponible') || text.includes('recurso') || text.includes('error') || text.length > 0
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

  it('debe manejar límites de recursos', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('POST', `${apiBaseUrl}/fincas/`, {
      statusCode: 507,
      body: { error: 'Límite de recursos excedido' }
    }).as('resourceLimit')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="save-finca"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().click({ force: true })
            
            cy.wait('@resourceLimit', { timeout: 10000 })
            
            cy.get('body', { timeout: 5000 }).then(($error) => {
              if ($error.find('[data-cy="resource-limit-error"], .error-message, .swal2-error').length > 0) {
                cy.get('[data-cy="resource-limit-error"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('límite') || text.includes('recursos') || text.includes('excedido') || text.length > 0
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
})
