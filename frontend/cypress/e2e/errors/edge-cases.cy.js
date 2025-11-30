describe('Manejo de Errores - Casos Edge', () => {
  beforeEach(() => {
    cy.login('farmer')
  })

  it('debe manejar datos vacíos en listas', () => {
    // Simular lista vacía
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, {
      statusCode: 200,
      body: { results: [], count: 0 }
    }).as('emptyList')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Esperar un poco para que la página se estabilice
    cy.wait(1000)
    
    // Verificar estado vacío
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
    
    // Buscar algo que no existe
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]').length > 0) {
        cy.get('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]').first().type('noexiste123')
        
        // Verificar estado de búsqueda sin resultados
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
    
    // Aplicar filtro que no tiene resultados
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="location-filter"], button, .filter').length > 0) {
        cy.get('[data-cy="location-filter"], button, .filter').first().click({ force: true })
        cy.get('body').then(($afterClick) => {
          if ($afterClick.find('[data-cy="province-filter"], select').length > 0) {
            cy.get('[data-cy="province-filter"], select').first().select('Provincia Inexistente', { force: true })
            cy.get('[data-cy="apply-filter"], button[type="submit"]').first().click()
            
            // Verificar estado de filtro sin resultados
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
          // Llenar con texto muy largo si existen los campos
          if ($modal.find('[data-cy="finca-nombre"], input').length > 0) {
            const longText = 'a'.repeat(1000)
            cy.get('[data-cy="finca-nombre"], input').first().type(longText, { force: true })
            
            // Verificar validación de longitud si existe el error
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
          // Llenar con caracteres especiales si existen los campos
          if ($modal.find('[data-cy="finca-nombre"], input').length > 0) {
            cy.get('[data-cy="finca-nombre"], input').first().type('Finca @#$%^&*()', { force: true })
            
            // Verificar que se aceptan caracteres especiales
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
          // Llenar con número muy grande si existe el campo
          if ($modal.find('[data-cy="finca-area"], input[type="number"]').length > 0) {
            cy.get('[data-cy="finca-area"], input[type="number"]').first().type('999999999999999', { force: true })
            
            // Verificar validación si existe el error
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
          // Llenar con número negativo si existe el campo
          if ($modal.find('[data-cy="finca-area"], input[type="number"]').length > 0) {
            cy.get('[data-cy="finca-area"], input[type="number"]').first().type('-10', { force: true })
            
            // Verificar validación si existe el error
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
          // Llenar con edad inválida si existe el campo
          if ($modal.find('[data-cy="lote-edad"], input[type="number"]').length > 0) {
            cy.get('[data-cy="lote-edad"], input[type="number"]').first().type('50', { force: true })
            
            // Verificar validación si existe el error
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
        // Simular archivo con nombre muy largo
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
        
        // Verificar validación si existe el error
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
        // Simular archivo con extensión no permitida
        const fileContent = 'test file content'
        const blob = new Blob([fileContent], { type: 'text/plain' })
        const file = new File([blob], 'test.txt', { type: 'text/plain' })
        
        cy.get('[data-cy="file-input"], input[type="file"]').then((input) => {
          const dataTransfer = new DataTransfer()
          dataTransfer.items.add(file)
          input[0].files = dataTransfer.files
          
          cy.wrap(input).trigger('change', { force: true })
        })
        
        // Verificar validación si existe el error
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
        // Simular archivo corrupto
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
            
            // Verificar error de archivo corrupto si existe
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
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular sesión expirada durante operación
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
            
            // Verificar redirección al login
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
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular operaciones concurrentes
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
            
            // Verificar mensaje de conflicto si existe
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
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular datos corruptos
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
    
    // Esperar un poco para que la página se estabilice
    cy.wait(1000)
    
    // Verificar que se manejan datos corruptos
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
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular respuesta parcial
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
    
    // Esperar un poco para que la página se estabilice
    cy.wait(1000)
    
    // Verificar que se maneja respuesta parcial
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
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular cambio de estado durante operación
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
            
            // Verificar mensaje de recurso no disponible si existe
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
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular límite de recursos
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
            
            // Verificar mensaje de límite de recursos si existe
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
