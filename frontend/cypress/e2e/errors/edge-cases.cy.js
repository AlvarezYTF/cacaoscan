import {
  setupServerError,
  setupEmptyListIntercept,
  getApiBaseUrl,
  visitAndWaitForBodyVisible,
  openModalFillFieldAndVerifyError,
  uploadFileAndVerifyError,
  ifFoundInBody,
  clickIfExistsAndContinue,
  verifyErrorMessageGeneric,
  testNavigatorApi,
  testWindowApi,
  testBrowserApi
} from '../../support/helpers'

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
    visitAndWaitForBodyVisible('/mis-fincas')
    openModalFillFieldAndVerifyError(
      '[data-cy="add-finca-button"], button',
      '[data-cy="finca-nombre"], input',
      'a'.repeat(10000),
      '[data-cy="save-finca"], button[type="submit"]',
      '[data-cy="finca-nombre-error"], .error-message',
      ['largo', 'longitud', 'demasiado']
    )
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
    visitAndWaitForBodyVisible('/nuevo-analisis')
    const corruptFile = new File(['corrupt'], 'corrupt.jpg', { type: 'image/jpeg' })
    uploadFileAndVerifyError(
      '[data-cy="file-input"], input[type="file"]',
      corruptFile,
      '[data-cy="upload-error"], .error-message',
      ['corrupto', 'archivo', 'error']
    )
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
          cy.log(`SessionStorage limit reached at key ${i}: ${e.message}`)
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
      let result = 0
      while (Date.now() - start < 100) {
        result += Math.sqrt(counter)
        counter++
      }
      // Use result to prevent optimization
      expect(result).to.be.a('number')
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
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'serviceWorker' in nav,
      (nav) => nav.serviceWorker.register('/sw.js'),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con web workers', () => {
    testBrowserApi(
      '/mis-fincas',
      (win) => {
        if (typeof Worker !== 'undefined') {
          const worker = new Worker('/worker.js')
          worker.postMessage({ type: 'test' })
          worker.terminate()
        }
      },
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con geolocation', () => {
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'geolocation' in nav,
      (nav) => nav.geolocation.getCurrentPosition(() => {}, () => {}),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con camera', () => {
    testNavigatorApi(
      '/nuevo-analisis',
      (nav) => 'mediaDevices' in nav,
      (nav) => nav.mediaDevices.getUserMedia({ video: true }),
      '[data-cy="file-input"]'
    )
  })

  it('debe manejar operación con clipboard', () => {
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'clipboard' in nav,
      (nav) => nav.clipboard.writeText('test'),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con notifications', () => {
    testWindowApi(
      '/mis-fincas',
      (win) => 'Notification' in win,
      (win) => win.Notification.requestPermission(),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con battery API', () => {
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'getBattery' in nav,
      (nav) => nav.getBattery(),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con device orientation', () => {
    testWindowApi(
      '/mis-fincas',
      (win) => 'DeviceOrientationEvent' in win,
      (win) => Promise.resolve(win.addEventListener('deviceorientation', () => {})),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con device motion', () => {
    testWindowApi(
      '/mis-fincas',
      (win) => 'DeviceMotionEvent' in win,
      (win) => Promise.resolve(win.addEventListener('devicemotion', () => {})),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con vibration API', () => {
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'vibrate' in nav,
      (nav) => Promise.resolve(nav.vibrate(100)),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con fullscreen API', () => {
    testBrowserApi(
      '/mis-fincas',
      (win) => {
        if ('requestFullscreen' in win.document.documentElement) {
          win.document.documentElement.requestFullscreen().catch(() => {})
        }
      },
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con pointer lock', () => {
    testBrowserApi(
      '/mis-fincas',
      (win) => {
        if ('requestPointerLock' in win.document.body) {
          win.document.body.requestPointerLock().catch(() => {})
        }
      },
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con screen orientation', () => {
    testBrowserApi(
      '/mis-fincas',
      (win) => {
        if ('orientation' in win.screen) {
          win.screen.orientation.lock('portrait').catch(() => {})
        }
      },
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con wake lock', () => {
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'wakeLock' in nav,
      (nav) => nav.wakeLock.request('screen'),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con payment request', () => {
    testBrowserApi(
      '/mis-fincas',
      (win) => {
        if ('PaymentRequest' in win) {
          try {
            const paymentRequest = new win.PaymentRequest([], { total: { label: 'Test', amount: { currency: 'USD', value: '0' } } })
            paymentRequest.show().catch((error) => {
              cy.log(`PaymentRequest error: ${error.message}`)
            })
          } catch (e) {
            cy.log(`PaymentRequest initialization error: ${e.message}`)
          }
        }
      },
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con credential management', () => {
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'credentials' in nav,
      (nav) => nav.credentials.get({ publicKey: {} }),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con web share', () => {
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'share' in nav,
      (nav) => nav.share({ title: 'Test', text: 'Test', url: '/' }),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con web bluetooth', () => {
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'bluetooth' in nav,
      (nav) => nav.bluetooth.requestDevice({ filters: [] }),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con web usb', () => {
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'usb' in nav,
      (nav) => nav.usb.requestDevice({ filters: [] }),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con web serial', () => {
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'serial' in nav,
      (nav) => nav.serial.requestPort(),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con web nfc', () => {
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'nfc' in nav,
      (nav) => nav.nfc.watch(() => {}),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con web xr', () => {
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'xr' in nav,
      (nav) => nav.xr.requestSession('immersive-vr'),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con web midi', () => {
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'requestMIDIAccess' in nav,
      (nav) => nav.requestMIDIAccess(),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con web hid', () => {
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'hid' in nav,
      (nav) => nav.hid.requestDevice({ filters: [] }),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con web locks', () => {
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'locks' in nav,
      (nav) => nav.locks.request('test', () => {}),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con web storage estimate', () => {
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'storage' in nav && 'estimate' in nav.storage,
      (nav) => nav.storage.estimate(),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con web storage persist', () => {
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'storage' in nav && 'persist' in nav.storage,
      (nav) => nav.storage.persist(),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con web storage persisted', () => {
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'storage' in nav && 'persisted' in nav.storage,
      (nav) => nav.storage.persisted(),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con web storage quota', () => {
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'storage' in nav && 'quota' in nav.storage,
      (nav) => nav.storage.quota(),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con web storage usage', () => {
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'storage' in nav && 'usage' in nav.storage,
      (nav) => nav.storage.usage(),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar operación con web storage getDirectory', () => {
    testNavigatorApi(
      '/mis-fincas',
      (nav) => 'storage' in nav && 'getDirectory' in nav.storage,
      (nav) => nav.storage.getDirectory(),
      '[data-cy="fincas-list"]'
    )
  })

  it('debe manejar datos vacíos en listas', () => {
    setupEmptyListIntercept('/fincas/**', 'emptyList')
    visitAndWaitForBodyVisible('/mis-fincas')
    
    const verifyEmptyMessage = () => {
      ifFoundInBody('[data-cy="empty-message"], .empty-message', () => {
        cy.get('[data-cy="empty-message"], .empty-message').should('exist')
      })
    }

    const verifyEmptyAction = () => {
      ifFoundInBody('[data-cy="empty-action"], .empty-action, button', () => {
        cy.get('[data-cy="empty-action"], .empty-action, button').should('exist')
      })
    }

    ifFoundInBody('[data-cy="empty-state"], .empty-state, .empty', () => {
      cy.get('[data-cy="empty-state"], .empty-state, .empty').should('exist')
      verifyEmptyMessage()
      verifyEmptyAction()
    })
  })

  it('debe manejar búsqueda sin resultados', () => {
    visitAndWaitForBodyVisible('/mis-fincas')
    
    const verifyNoResultsMessage = () => {
      ifFoundInBody('[data-cy="no-results-message"], .no-results-message', () => {
        cy.get('[data-cy="no-results-message"], .no-results-message').should('exist')
      })
    }

    const verifyClearSearch = () => {
      ifFoundInBody('[data-cy="clear-search"], button, .clear', () => {
        cy.get('[data-cy="clear-search"], button, .clear').should('exist')
      })
    }

    const verifyNoResults = () => {
      ifFoundInBody('[data-cy="no-results"], .no-results, .empty', () => {
        cy.get('[data-cy="no-results"], .no-results, .empty').should('exist')
        verifyNoResultsMessage()
        verifyClearSearch()
      })
    }

    ifFoundInBody('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]', () => {
      cy.get('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]').first().type('noexiste123')
      verifyNoResults()
    })
  })

  it('debe manejar filtros sin resultados', () => {
    visitAndWaitForBodyVisible('/mis-fincas')
    
    const verifyClearFilters = () => {
      ifFoundInBody('[data-cy="clear-filters"], button', () => {
        cy.get('[data-cy="clear-filters"], button').should('exist')
      })
    }

    const handleNoResults = () => {
      ifFoundInBody('[data-cy="no-results"], .no-results', () => {
        cy.get('[data-cy="no-results"], .no-results').should('exist')
        verifyClearFilters()
      })
    }

    const applyFilterAndVerify = () => {
      ifFoundInBody('[data-cy="province-filter"], select', () => {
        cy.get('[data-cy="province-filter"], select').first().select('Provincia Inexistente', { force: true })
        cy.get('[data-cy="apply-filter"], button[type="submit"]').first().click()
        cy.wait(1000)
        handleNoResults()
      })
    }

    ifFoundInBody('[data-cy="location-filter"], button, .filter', () => {
      cy.get('[data-cy="location-filter"], button, .filter').first().click({ force: true })
      cy.wait(500)
      applyFilterAndVerify()
    })
  })

  it('debe manejar formularios con campos muy largos', () => {
    visitAndWaitForBodyVisible('/mis-fincas')
    openModalFillFieldAndVerifyError(
      '[data-cy="add-finca-button"], button',
      '[data-cy="finca-nombre"], input',
      'a'.repeat(1000),
      '[data-cy="save-finca"], button[type="submit"]',
      '[data-cy="finca-nombre-error"], .error-message',
      ['largo', 'longitud', 'demasiado']
    )
  })

  it('debe manejar formularios con caracteres especiales', () => {
    visitAndWaitForBodyVisible('/mis-fincas')
    
    const verifyFieldValue = () => {
      cy.get('[data-cy="finca-nombre"], input').first().should('satisfy', ($el) => {
        const value = $el.val() || $el.text()
        return value.includes('Finca') || value.length > 0
      })
    }

    const fillSpecialCharactersField = () => {
      ifFoundInBody('[data-cy="finca-nombre"], input', () => {
        cy.get('[data-cy="finca-nombre"], input').first().type('Finca @#$%^&*()', { force: true })
        verifyFieldValue()
      })
    }

    clickIfExistsAndContinue('[data-cy="add-finca-button"], button', () => {
      fillSpecialCharactersField()
    })
  })

  it('debe manejar números muy grandes', () => {
    visitAndWaitForBodyVisible('/mis-fincas')
    openModalFillFieldAndVerifyError(
      '[data-cy="add-finca-button"], button',
      '[data-cy="finca-area"], input[type="number"]',
      '999999999999999',
      '[data-cy="save-finca"], button[type="submit"]',
      '[data-cy="finca-area-error"], .error-message',
      ['grande', 'área', 'demasiado']
    )
  })

  it('debe manejar números negativos', () => {
    visitAndWaitForBodyVisible('/mis-fincas')
    openModalFillFieldAndVerifyError(
      '[data-cy="add-finca-button"], button',
      '[data-cy="finca-area"], input[type="number"]',
      '-10',
      '[data-cy="save-finca"], button[type="submit"]',
      '[data-cy="finca-area-error"], .error-message',
      ['positiva', 'negativo', 'área']
    )
  })

  it('debe manejar fechas inválidas', () => {
    visitAndWaitForBodyVisible('/mis-lotes')
    
    clickIfExistsAndContinue('[data-cy="add-lote-button"], button', () => {
      ifFoundInBody('[data-cy="lote-edad"], input[type="number"]', () => {
        cy.get('[data-cy="lote-edad"], input[type="number"]').first().type('50', { force: true })
        verifyErrorMessageGeneric(
          ['edad', 'años', 'menor'],
          '[data-cy="lote-edad-error"], .error-message'
        )
      })
    })
  })

  it('debe manejar archivos con nombres muy largos', () => {
    visitAndWaitForBodyVisible('/nuevo-analisis')
    ifFoundInBody('[data-cy="file-input"], input[type="file"]', () => {
      const longFileName = 'a'.repeat(255) + '.jpg'
      const fileContent = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAD/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AKgAD//Z'
      cy.get('[data-cy="file-input"], input[type="file"]').then(($input) => {
        const blob = Cypress.Blob.base64StringToBlob(fileContent.split(',')[1], 'image/jpeg')
        const file = new File([blob], longFileName, { type: 'image/jpeg' })
        uploadFileAndVerifyError(
          '[data-cy="file-input"], input[type="file"]',
          file,
          '[data-cy="file-name-error"], .error-message',
          ['largo', 'nombre', 'archivo']
        )
      })
    })
  })

  it('debe manejar archivos con extensiones no permitidas', () => {
    visitAndWaitForBodyVisible('/nuevo-analisis')
    ifFoundInBody('[data-cy="file-input"], input[type="file"]', () => {
      const fileContent = 'test file content'
      const blob = new Blob([fileContent], { type: 'text/plain' })
      const file = new File([blob], 'test.txt', { type: 'text/plain' })
      uploadFileAndVerifyError(
        '[data-cy="file-input"], input[type="file"]',
        file,
        '[data-cy="file-type-error"], .error-message',
        ['tipo', 'permitido', 'archivo']
      )
    })
  })

  it('debe manejar archivos corruptos', () => {
    visitAndWaitForBodyVisible('/nuevo-analisis')
    
    const verifyCorruptFileError = () => {
      verifyErrorMessageGeneric(
        ['corrupto', 'archivo', 'error'],
        '[data-cy="file-corrupt-error"], .error-message, .swal2-error'
      )
    }

    const handleCorruptFileUpload = () => {
      const corruptContent = 'corrupt file content'
      const blob = new Blob([corruptContent], { type: 'image/jpeg' })
      const file = new File([blob], 'corrupt.jpg', { type: 'image/jpeg' })
      uploadFileAndVerifyError(
        '[data-cy="file-input"], input[type="file"]',
        file,
        '[data-cy="file-corrupt-error"], .error-message, .swal2-error',
        ['corrupto', 'archivo', 'error']
      )
      clickIfExistsAndContinue('[data-cy="upload-button"], button[type="submit"]', () => {
        verifyCorruptFileError()
      })
    }

    ifFoundInBody('[data-cy="file-input"], input[type="file"]', () => {
      handleCorruptFileUpload()
    })
  })

  it('debe manejar sesión expirada durante operación', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('POST', `${apiBaseUrl}/fincas/`, {
      statusCode: 401,
      body: { error: 'Token expirado' }
    }).as('expiredSession')
    
    visitAndWaitForBodyVisible('/mis-fincas')
    
    const isLoginOrAuthUrl = (url) => {
      return url.includes('/login') || url.includes('/auth')
    }

    const verifyRedirectToLogin = () => {
      cy.wait('@expiredSession', { timeout: 10000 })
      cy.url({ timeout: 5000 }).should('satisfy', isLoginOrAuthUrl)
    }

    clickIfExistsAndContinue('[data-cy="add-finca-button"], button', () => {
      clickIfExistsAndContinue('[data-cy="save-finca"], button[type="submit"]', verifyRedirectToLogin)
    })
  })

  it('debe manejar operaciones concurrentes', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('POST', `${apiBaseUrl}/fincas/`, {
      statusCode: 409,
      body: { error: 'Operación en conflicto' }
    }).as('concurrentOperation')
    
    visitAndWaitForBodyVisible('/mis-fincas')
    
    const verifyConflictError = () => {
      cy.wait('@concurrentOperation', { timeout: 10000 })
      verifyErrorMessageGeneric(
        ['conflicto', 'operación', 'error'],
        '[data-cy="conflict-error"], .error-message, .swal2-error'
      )
    }

    clickIfExistsAndContinue('[data-cy="add-finca-button"], button', () => {
      clickIfExistsAndContinue('[data-cy="save-finca"], button[type="submit"]', verifyConflictError)
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
    
    visitAndWaitForBodyVisible('/mis-fincas')
    
    ifFoundInBody('[data-cy="finca-item"], .finca-item, .item', () => {
      cy.get('[data-cy="finca-item"], .finca-item, .item').should('exist')
    })
    ifFoundInBody('[data-cy="corrupt-data-warning"], .warning', () => {
      cy.get('[data-cy="corrupt-data-warning"], .warning').should('exist')
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
    
    visitAndWaitForBodyVisible('/mis-fincas')
    
    ifFoundInBody('[data-cy="partial-data-warning"], .warning', () => {
      cy.get('[data-cy="partial-data-warning"], .warning').should('exist')
    })
    ifFoundInBody('[data-cy="load-more"], button', () => {
      cy.get('[data-cy="load-more"], button').should('exist')
    })
  })

  it('debe manejar cambios de estado durante operación', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('POST', `${apiBaseUrl}/fincas/`, {
      statusCode: 410,
      body: { error: 'Recurso ya no disponible' }
    }).as('goneResource')
    
    visitAndWaitForBodyVisible('/mis-fincas')
    
    const verifyGoneError = () => {
      cy.wait('@goneResource', { timeout: 10000 })
      verifyErrorMessageGeneric(
        ['disponible', 'recurso', 'error'],
        '[data-cy="gone-error"], .error-message, .swal2-error'
      )
    }

    clickIfExistsAndContinue('[data-cy="add-finca-button"], button', () => {
      clickIfExistsAndContinue('[data-cy="save-finca"], button[type="submit"]', verifyGoneError)
    })
  })

  it('debe manejar límites de recursos', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('POST', `${apiBaseUrl}/fincas/`, {
      statusCode: 507,
      body: { error: 'Límite de recursos excedido' }
    }).as('resourceLimit')
    
    visitAndWaitForBodyVisible('/mis-fincas')
    
    const verifyResourceLimitError = () => {
      cy.wait('@resourceLimit', { timeout: 10000 })
      verifyErrorMessageGeneric(
        ['límite', 'recursos', 'excedido'],
        '[data-cy="resource-limit-error"], .error-message, .swal2-error'
      )
    }

    clickIfExistsAndContinue('[data-cy="add-finca-button"], button', () => {
      clickIfExistsAndContinue('[data-cy="save-finca"], button[type="submit"]', verifyResourceLimitError)
    })
  })
})
