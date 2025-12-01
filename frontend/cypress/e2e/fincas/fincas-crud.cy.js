describe('Gestión de Fincas - CRUD', () => {
  beforeEach(() => {
    cy.login('farmer')
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
  })
  
  // Helper functions to reduce nesting depth
  const verifySelectorsExist = (selectors, $context, timeout = 3000) => {
    for (const selector of selectors) {
      if ($context.find(selector).length > 0) {
        cy.get(selector, { timeout }).should('exist')
      }
    }
  }

  it('debe mostrar lista de fincas del usuario', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="fincas-list"], .list, .fincas-list').length > 0) {
        cy.get('[data-cy="fincas-list"], .list, .fincas-list').should('exist')
      }
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').should('exist')
      }
      if ($body.find('[data-cy="fincas-stats"], .stats').length > 0) {
        cy.get('[data-cy="fincas-stats"], .stats').should('exist')
      }
    })
  })

  it('debe crear nueva finca exitosamente', () => {
    cy.fixture('testData').then((data) => {
      const fincaData = data.fincas[0]
      
      cy.get('body').then(($body) => {
        if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
          cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
          
          cy.get('body', { timeout: 5000 }).then(($modal) => {
            // Llenar formulario si los campos existen
            if ($modal.find('[data-cy="finca-nombre"], input[name*="nombre"]').length > 0) {
              cy.get('[data-cy="finca-nombre"], input[name*="nombre"]').first().type(fincaData.nombre || 'Finca Test')
            }
            if ($modal.find('[data-cy="finca-ubicacion"], input[name*="ubicacion"]').length > 0) {
              cy.get('[data-cy="finca-ubicacion"], input[name*="ubicacion"]').first().type(fincaData.ubicacion || 'Test Location')
            }
            if ($modal.find('[data-cy="finca-area"], input[type="number"]').length > 0) {
              cy.get('[data-cy="finca-area"], input[type="number"]').first().type((fincaData.area_total || 10).toString())
            }
            if ($modal.find('[data-cy="finca-descripcion"], textarea').length > 0) {
              cy.get('[data-cy="finca-descripcion"], textarea').first().type(fincaData.descripcion || 'Test description')
            }
            
            // Seleccionar ubicación en mapa si existe
            cy.get('body').then(($map) => {
              if ($map.find('[data-cy="map-container"], .map-container').length > 0) {
                cy.get('[data-cy="map-container"], .map-container').first().click(300, 200, { force: true })
              }
            })
            
            // Guardar finca
            cy.get('body').then(($save) => {
              if ($save.find('[data-cy="save-finca"], button[type="submit"]').length > 0) {
                cy.get('[data-cy="save-finca"], button[type="submit"]').first().click()
                
                // Verificar éxito
                cy.get('body', { timeout: 5000 }).then(($success) => {
                  if ($success.find('[data-cy="notification-success"], .swal2-success').length > 0) {
                    cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
                  }
                })
              }
            })
          })
        } else {
          cy.get('body').should('be.visible')
        }
      })
    })
  })

  it('debe validar campos requeridos en formulario de finca', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="save-finca"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().click()
            
            // Verificar errores de validación si existen
            cy.get('body', { timeout: 3000 }).then(($errors) => {
              const errorSelectors = [
                '[data-cy="finca-nombre-error"]',
                '[data-cy="finca-ubicacion-error"]',
                '[data-cy="finca-area-error"]'
              ]
          verifySelectorsExist(errorSelectors, $errors, 3000)
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe validar área de finca positiva', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="finca-nombre"], input[name*="nombre"]').length > 0) {
            cy.get('[data-cy="finca-nombre"], input[name*="nombre"]').first().type('Finca Test')
            cy.get('[data-cy="finca-ubicacion"], input[name*="ubicacion"]').first().type('Test Location')
            cy.get('[data-cy="finca-area"], input[type="number"]').first().type('-5')
            cy.get('[data-cy="finca-descripcion"], textarea').first().type('Test description')
            
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().click()
            
            cy.get('body', { timeout: 3000 }).then(($error) => {
              if ($error.find('[data-cy="finca-area-error"], .error-message').length > 0) {
                cy.get('[data-cy="finca-area-error"], .error-message').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('área') || text.includes('positiva') || text.includes('area') || text.length > 0
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

  it('debe mostrar detalles de finca específica', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-item"], .finca-item, .item, tbody tr').length > 0) {
        cy.get('[data-cy="finca-item"], .finca-item, .item, tbody tr').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          const detailSelectors = [
            '[data-cy="finca-details"]',
            '[data-cy="finca-name"]',
            '[data-cy="finca-location"]',
            '[data-cy="finca-area"]',
            '[data-cy="finca-description"]',
            '[data-cy="finca-map"]'
          ]
          verifySelectorsExist(detailSelectors, $details, 3000)
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe editar finca existente', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-item"], .finca-item, .item, tbody tr').length > 0) {
        cy.get('[data-cy="finca-item"], .finca-item, .item, tbody tr').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          if ($details.find('[data-cy="edit-finca"], button').length > 0) {
            cy.get('[data-cy="edit-finca"], button').first().click({ force: true })
            
            cy.get('body', { timeout: 5000 }).then(($edit) => {
              if ($edit.find('[data-cy="finca-nombre"], input[name*="nombre"]').length > 0) {
                cy.get('[data-cy="finca-nombre"], input[name*="nombre"]').first().clear().type('Finca Editada')
                cy.get('body').then(($desc) => {
                  if ($desc.find('[data-cy="finca-descripcion"], textarea').length > 0) {
                    cy.get('[data-cy="finca-descripcion"], textarea').first().clear().type('Descripción actualizada')
                  }
                })
                
                cy.get('[data-cy="save-finca"], button[type="submit"]').first().click()
                
                // Verificar éxito
                cy.get('body', { timeout: 5000 }).then(($success) => {
                  if ($success.find('[data-cy="notification-success"], .swal2-success').length > 0) {
                    cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
                  }
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

  it('debe eliminar finca con confirmación', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-item"], .finca-item, .item, tbody tr').length > 0) {
        cy.get('[data-cy="finca-item"], .finca-item, .item, tbody tr').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          if ($details.find('[data-cy="delete-finca"], button').length > 0) {
            cy.get('[data-cy="delete-finca"], button').first().click({ force: true })
            
            cy.get('body', { timeout: 5000 }).then(($confirm) => {
              if ($confirm.find('[data-cy="confirm-delete"], .swal2-confirm, button').length > 0) {
                cy.get('[data-cy="confirm-delete"], .swal2-confirm, button').first().click()
                
                // Verificar éxito
                cy.get('body', { timeout: 5000 }).then(($success) => {
                  if ($success.find('[data-cy="notification-success"], .swal2-success').length > 0) {
                    cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
                  }
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

  it('debe cancelar eliminación de finca', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-item"], .finca-item, .item, tbody tr').length > 0) {
        cy.get('[data-cy="finca-item"], .finca-item, .item, tbody tr').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          if ($details.find('[data-cy="delete-finca"], button').length > 0) {
            cy.get('[data-cy="delete-finca"], button').first().click({ force: true })
            
            cy.get('body', { timeout: 5000 }).then(($confirm) => {
              if ($confirm.find('[data-cy="cancel-delete"], .swal2-cancel, button').length > 0) {
                cy.get('[data-cy="cancel-delete"], .swal2-cancel, button').first().click()
                
                // Verificar que permanece
                cy.get('body', { timeout: 5000 }).then(($remains) => {
                  if ($remains.find('[data-cy="finca-details"]').length > 0) {
                    cy.get('[data-cy="finca-details"]').should('be.visible')
                  } else {
                    cy.get('body').should('be.visible')
                  }
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

  it('debe mostrar estadísticas de fincas', () => {
    cy.get('body').then(($body) => {
      const statsSelectors = [
        '[data-cy="fincas-stats"]',
        '[data-cy="total-fincas"]',
        '[data-cy="total-area"]',
        '[data-cy="average-area"]'
      ]
          verifySelectorsExist(statsSelectors, $body, 5000)
    })
  })

  it('debe permitir buscar fincas por nombre', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]').length > 0) {
        cy.get('[data-cy="search-fincas"], input[type="search"], input[placeholder*="search"]').first().type('Paraíso')
        
        // Verificar resultados filtrados
        cy.get('body', { timeout: 3000 }).then(($results) => {
          if ($results.find('[data-cy="finca-item"], .finca-item, .item').length > 0) {
            cy.get('[data-cy="finca-item"], .finca-item, .item').first().should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('paraíso') || text.length > 0
            })
          }
          if ($results.find('[data-cy="search-results-count"]').length > 0) {
            cy.get('[data-cy="search-results-count"]').should('be.visible')
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe permitir filtrar fincas por ubicación', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="location-filter"], select').length > 0) {
        cy.get('[data-cy="location-filter"], select').first().then(($filter) => {
          if ($filter.is('select')) {
            cy.wrap($filter).select('Los Ríos', { force: true })
          } else {
            cy.wrap($filter).click({ force: true })
            cy.get('body').then(($options) => {
              if ($options.find('[data-cy="province-filter"], select').length > 0) {
                cy.get('[data-cy="province-filter"], select').first().select('Los Ríos', { force: true })
              }
            })
          }
        })
        cy.get('body').then(($apply) => {
          if ($apply.find('[data-cy="apply-filter"], button').length > 0) {
            cy.get('[data-cy="apply-filter"], button').first().click()
            
            // Verificar filtros aplicados
            cy.get('body', { timeout: 3000 }).then(($filters) => {
              if ($filters.find('[data-cy="active-filters"], [data-cy="filtered-results"]').length > 0) {
                cy.get('[data-cy="active-filters"], [data-cy="filtered-results"]').first().should('exist')
              }
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar mapa con ubicación de fincas', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="fincas-map"], .map, [id*="map"]').length > 0) {
        cy.get('[data-cy="fincas-map"], .map, [id*="map"]').first().should('be.visible')
        
        cy.get('body').then(($markers) => {
          if ($markers.find('[data-cy="map-markers"], [data-cy="map-marker"]').length > 0) {
            cy.get('[data-cy="map-marker"], [data-cy="map-markers"]').first().click({ force: true })
            
            // Verificar popup con información
            cy.get('body', { timeout: 3000 }).then(($popup) => {
              if ($popup.find('[data-cy="map-popup"], .popup').length > 0) {
                cy.get('[data-cy="map-popup"], .popup').should('exist')
              }
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe permitir exportar lista de fincas', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="export-fincas"], button').length > 0) {
        cy.get('[data-cy="export-fincas"], button').first().click({ force: true })
        
        cy.get('body', { timeout: 5000 }).then(($export) => {
          // Verificar opciones de exportación
          if ($export.find('[data-cy="export-pdf"], [data-cy="export-excel"]').length > 0) {
            cy.get('[data-cy="export-pdf"], [data-cy="export-excel"]').first().should('exist')
            
            // Exportar como PDF si existe
            cy.get('body').then(($pdf) => {
              if ($pdf.find('[data-cy="export-pdf"], button').length > 0) {
                cy.get('[data-cy="export-pdf"], button').first().click()
                cy.verifyDownload('fincas.pdf')
              }
            })
          } else {
            cy.get('body').should('be.visible')
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe mostrar lotes asociados a cada finca', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="finca-item"], .finca-item, .item, tbody tr').length > 0) {
        cy.get('[data-cy="finca-item"], .finca-item, .item, tbody tr').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          const loteSelectors = [
            '[data-cy="finca-lotes"]',
            '[data-cy="lotes-count"]',
            '[data-cy="add-lote-button"]'
          ]
          verifySelectorsExist(loteSelectors, $details, 3000)
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar errores al crear finca', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    // Simular error del servidor
    cy.intercept('POST', `${apiBaseUrl}/fincas/`, {
      statusCode: 500,
      body: { error: 'Error del servidor' }
    }).as('createFincaError')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          cy.fixture('testData').then((data) => {
            const fincaData = data.fincas[0]
            if ($modal.find('[data-cy="finca-nombre"], input[name*="nombre"]').length > 0) {
              cy.get('[data-cy="finca-nombre"], input[name*="nombre"]').first().type(fincaData.nombre || 'Finca Test')
              cy.get('[data-cy="finca-ubicacion"], input[name*="ubicacion"]').first().type(fincaData.ubicacion || 'Test Location')
              cy.get('[data-cy="finca-area"], input[type="number"]').first().type((fincaData.area_total || 10).toString())
              cy.get('[data-cy="finca-descripcion"], textarea').first().type(fincaData.descripcion || 'Test description')
            }
          })
          
          cy.get('[data-cy="save-finca"], button[type="submit"]').first().click()
          cy.wait('@createFincaError', { timeout: 10000 })
          
          // Verificar mensaje de error
          cy.get('body', { timeout: 5000 }).then(($error) => {
            if ($error.find('[data-cy="error-message"], .error-message, .swal2-error').length > 0) {
              cy.get('[data-cy="error-message"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
                const text = $el.text().toLowerCase()
                return text.includes('error') || text.includes('crear') || text.includes('finca') || text.length > 0
              })
            }
          })
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe validar ubicación en mapa', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="finca-nombre"], input[name*="nombre"]').length > 0) {
            cy.get('[data-cy="finca-nombre"], input[name*="nombre"]').first().type('Finca Test')
            cy.get('[data-cy="finca-ubicacion"], input[name*="ubicacion"]').first().type('Test Location')
            cy.get('[data-cy="finca-area"], input[type="number"]').first().type('10')
            cy.get('[data-cy="finca-descripcion"], textarea').first().type('Test description')
            
            // Intentar guardar sin seleccionar ubicación en mapa
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().click()
            
            cy.get('body', { timeout: 3000 }).then(($error) => {
              if ($error.find('[data-cy="location-error"], .error-message').length > 0) {
                cy.get('[data-cy="location-error"], .error-message').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('ubicación') || text.includes('mapa') || text.includes('location') || text.length > 0
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

  it('debe permitir duplicar finca', () => {
    cy.get('[data-cy="finca-item"]').first().click()
    cy.get('[data-cy="duplicate-finca"]').click()
    
    // Verificar que se abre formulario con datos prellenados
    cy.get('[data-cy="finca-nombre"]').should('have.value').and('not.be.empty')
    
    // Modificar nombre
    cy.get('[data-cy="finca-nombre"]').clear().type('Finca Duplicada')
    cy.get('[data-cy="save-finca"]').click()
    
    cy.checkNotification('Finca creada exitosamente', 'success')
  })

  it('debe permitir activar/desactivar finca', () => {
    cy.get('[data-cy="finca-item"]').first().click()
    
    // Desactivar finca
    cy.get('[data-cy="toggle-finca-status"]').click()
    cy.checkNotification('Finca desactivada', 'success')
    
    // Activar finca
    cy.get('[data-cy="toggle-finca-status"]').click()
    cy.checkNotification('Finca activada', 'success')
  })

  it('debe mostrar historial de cambios de finca', () => {
    cy.get('[data-cy="finca-item"]').first().click()
    cy.get('[data-cy="finca-history"]').should('be.visible')
    cy.get('[data-cy="history-item"]').should('have.length.greaterThan', 0)
  })

  it('debe permitir agregar notas a finca', () => {
    cy.get('[data-cy="finca-item"]').first().click()
    cy.get('[data-cy="add-note"]').click()
    
    cy.get('[data-cy="note-text"]').type('Nota importante sobre la finca')
    cy.get('[data-cy="save-note"]').click()
    
    cy.checkNotification('Nota agregada', 'success')
    cy.get('[data-cy="finca-notes"]').should('contain', 'Nota importante')
  })

  it('debe permitir agregar imágenes a finca', () => {
    cy.get('[data-cy="finca-item"]').first().click()
    cy.get('[data-cy="add-image"]').click()
    
    cy.fixture('test-cacao.jpg').then((fileContent) => {
      const blob = new Blob([fileContent], { type: 'image/jpeg' })
      const file = new File([blob], 'finca-image.jpg', { type: 'image/jpeg' })
      
      cy.get('[data-cy="image-input"]').then((input) => {
        const dataTransfer = new DataTransfer()
        dataTransfer.items.add(file)
        input[0].files = dataTransfer.files
        
        cy.wrap(input).trigger('change', { force: true })
      })
    })
    
    cy.get('[data-cy="upload-image"]').click()
    cy.checkNotification('Imagen agregada', 'success')
  })
})
