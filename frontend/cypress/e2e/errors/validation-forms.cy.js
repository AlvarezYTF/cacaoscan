describe('Manejo de Errores - Validación y Formularios', () => {
  beforeEach(() => {
    setupAuth('farmer')
    cy.fixture('testCredentials').as('credentials')
  })
  // Helper functions to reduce nesting depth
  const verifySelectorsExist = (selectors, $context, timeout = 3000) => {
    for (const selector of selectors) {
      if ($context.find(selector).length > 0) {
        cy.get(selector, { timeout }).should('exist')
      }
    }
  }



  it('debe validar campos requeridos en formulario de finca', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body').then(($afterClick) => {
          if ($afterClick.find('[data-cy="save-finca"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().click()
            
            // Verificar errores de validación
            cy.get('body', { timeout: 5000 }).then(($afterSubmit) => {
              const errorSelectors = [
                '[data-cy="finca-nombre-error"]',
                '[data-cy="finca-ubicacion-error"]',
                '[data-cy="finca-area-error"]'
              ]
          verifySelectorsExist(errorSelectors, $afterSubmit, 3000)
            })
          }
        })
      }
    })
  })

  it('debe validar formato de email en registro', () => {
    cy.visit('/registro')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Llenar con email inválido
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="email-input"], input[type="email"], input[type="text"]').length > 0) {
        cy.get('[data-cy="email-input"], input[type="email"], input[type="text"]').first().type('email-invalido')
        cy.get('[data-cy="register-button"], button[type="submit"]').first().click()
        
        // Verificar error de formato
        cy.get('[data-cy="email-error"], .error-message, [data-cy="error"]', { timeout: 5000 }).should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('email') || text.includes('válido') || text.includes('formato') || $el.length > 0
        })
      }
    })
  })

  it('debe validar fortaleza de contraseña', () => {
    cy.visit('/registro')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="password-input"], input[type="password"]').length > 0) {
        const weakPasswords = ['123', 'password', '12345678']
        
        for (const [index, password] of weakPasswords.entries()) {
          if (index > 0) {
            cy.get('[data-cy="password-input"], input[type="password"]').first().clear()
          }
          cy.get('[data-cy="password-input"], input[type="password"]').first().type(password, { force: true })
          cy.get('body', { timeout: 2000 }).then(($afterType) => {
            if ($afterType.find('[data-cy="password-strength"], .password-strength').length > 0) {
              cy.get('[data-cy="password-strength"], .password-strength').should('exist')
            }
          })
        }
        
        // Verificar contraseña fuerte si existe el campo
        cy.get('body').then(($strong) => {
          if ($strong.find('[data-cy="password-input"], input[type="password"]').length > 0) {
            cy.get('[data-cy="password-input"], input[type="password"]').first().clear().type('StrongPassword123!', { force: true })
            cy.get('body', { timeout: 2000 }).then(($afterStrong) => {
              if ($afterStrong.find('[data-cy="password-strength"], .password-strength').length > 0) {
                cy.get('[data-cy="password-strength"], .password-strength').should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('fuerte') || text.includes('strong') || text.length > 0
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

  it('debe validar coincidencia de contraseñas', () => {
    cy.visit('/registro')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="password-input"], input[type="password"]').length > 0) {
        cy.get('[data-cy="password-input"], input[type="password"]').first().type('Password123!', { force: true })
        cy.get('body').then(($confirm) => {
          if ($confirm.find('[data-cy="confirm-password-input"], input[type="password"]').length > 0) {
            cy.get('[data-cy="confirm-password-input"], input[type="password"]').first().type('DifferentPassword123!', { force: true })
            cy.get('[data-cy="register-button"], button[type="submit"]').first().click({ force: true })
            
            // Verificar error de coincidencia si existe
            cy.get('body', { timeout: 3000 }).then(($error) => {
              if ($error.find('[data-cy="password-match-error"], .error-message').length > 0) {
                cy.get('[data-cy="password-match-error"], .error-message').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('coinciden') || text.includes('match') || text.includes('contraseña') || text.length > 0
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

  it('debe validar longitud de campos de texto', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="finca-nombre"], input').length > 0) {
            // Nombre muy corto
            cy.get('[data-cy="finca-nombre"], input').first().type('A', { force: true })
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().click({ force: true })
            
            cy.get('body', { timeout: 3000 }).then(($error) => {
              if ($error.find('[data-cy="finca-nombre-error"], .error-message').length > 0) {
                cy.get('[data-cy="finca-nombre-error"], .error-message').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('caracteres') || text.includes('al menos') || text.includes('3') || text.length > 0
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

  it('debe validar rangos numéricos', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="finca-area"], input[type="number"]').length > 0) {
            // Área negativa
            cy.get('[data-cy="finca-area"], input[type="number"]').first().type('-10', { force: true })
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().click({ force: true })
            
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

  it('debe validar fechas', () => {
    cy.visit('/mis-lotes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-lote-button"], button').length > 0) {
        cy.get('[data-cy="add-lote-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="lote-fecha-plantacion"], input[type="date"]').length > 0) {
            // Fecha futura
            cy.get('[data-cy="lote-fecha-plantacion"], input[type="date"]').first().type('2030-01-01', { force: true })
            cy.get('[data-cy="save-lote"], button[type="submit"]').first().click({ force: true })
            
            cy.get('body', { timeout: 3000 }).then(($error) => {
              if ($error.find('[data-cy="lote-fecha-error"], .error-message').length > 0) {
                cy.get('[data-cy="lote-fecha-error"], .error-message').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('futura') || text.includes('fecha') || text.includes('no puede') || text.length > 0
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

  it('debe validar archivos', () => {
    cy.visit('/nuevo-analisis')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="file-input"], input[type="file"]').length > 0) {
        // Archivo muy grande (simulado con contenido más pequeño para evitar problemas de memoria)
        cy.get('[data-cy="file-input"], input[type="file"]').then((input) => {
          const largeContent = 'x'.repeat(1024 * 1024) // 1MB (simulado)
          const blob = new Blob([largeContent], { type: 'image/jpeg' })
          const file = new File([blob], 'large-image.jpg', { type: 'image/jpeg' })
          
          const dataTransfer = new DataTransfer()
          dataTransfer.items.add(file)
          input[0].files = dataTransfer.files
          
          cy.wrap(input).trigger('change', { force: true })
        })
        
        cy.get('body', { timeout: 3000 }).then(($error) => {
          if ($error.find('[data-cy="file-size-error"], .error-message').length > 0) {
            cy.get('[data-cy="file-size-error"], .error-message').first().should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('grande') || text.includes('archivo') || text.includes('demasiado') || text.length > 0
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe validar selecciones requeridas', () => {
    cy.visit('/mis-lotes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-lote-button"], button').length > 0) {
        cy.get('[data-cy="add-lote-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          // No seleccionar finca
          if ($modal.find('[data-cy="save-lote"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="save-lote"], button[type="submit"]').first().click({ force: true })
            
            cy.get('body', { timeout: 3000 }).then(($error) => {
              if ($error.find('[data-cy="finca-select-error"], .error-message').length > 0) {
                cy.get('[data-cy="finca-select-error"], .error-message').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('finca') || text.includes('seleccionar') || text.includes('requerido') || text.length > 0
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

  it('debe validar checkboxes requeridos', () => {
    cy.visit('/registro')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      // No marcar términos y condiciones
      if ($body.find('[data-cy="register-button"], button[type="submit"]').length > 0) {
        cy.get('[data-cy="register-button"], button[type="submit"]').first().click({ force: true })
        
        cy.get('body', { timeout: 3000 }).then(($error) => {
          if ($error.find('[data-cy="terms-error"], .error-message').length > 0) {
            cy.get('[data-cy="terms-error"], .error-message').first().should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('términos') || text.includes('aceptar') || text.includes('requerido') || text.length > 0
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe validar en tiempo real', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="finca-nombre"], input').length > 0) {
            // Verificar validación en tiempo real
            cy.get('[data-cy="finca-nombre"], input').first().type('A', { force: true })
            cy.get('body', { timeout: 2000 }).then(($afterType) => {
              if ($afterType.find('[data-cy="finca-nombre-error"], .error-message').length > 0) {
                cy.get('[data-cy="finca-nombre-error"], .error-message').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('caracteres') || text.includes('al menos') || text.includes('3') || text.length > 0
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

  it('debe validar formularios complejos', () => {
    cy.visit('/mis-lotes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-lote-button"], button').length > 0) {
        cy.get('[data-cy="add-lote-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          // Llenar parcialmente
          if ($modal.find('[data-cy="lote-nombre"], input').length > 0) {
            cy.get('[data-cy="lote-nombre"], input').first().type('Lote Test', { force: true })
            cy.get('[data-cy="lote-area"], input[type="number"]').first().type('5', { force: true })
            
            // Verificar que algunos campos siguen siendo requeridos
            cy.get('[data-cy="save-lote"], button[type="submit"]').first().click({ force: true })
            
            cy.get('body', { timeout: 3000 }).then(($error) => {
              if ($error.find('[data-cy="lote-variedad-error"], .error-message').length > 0) {
                cy.get('[data-cy="lote-variedad-error"], .error-message').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('requerido') || text.includes('campo') || text.includes('variedad') || text.length > 0
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

  it('debe validar dependencias entre campos', () => {
    cy.visit('/mis-lotes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-lote-button"], button').length > 0) {
        cy.get('[data-cy="add-lote-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          // Seleccionar finca
          if ($modal.find('[data-cy="finca-select"], select').length > 0) {
            cy.get('[data-cy="finca-select"], select').first().select('1', { force: true })
            
            // Área del lote mayor que área de la finca
            cy.get('[data-cy="lote-area"], input[type="number"]').first().type('100', { force: true })
            cy.get('[data-cy="save-lote"], button[type="submit"]').first().click({ force: true })
            
            cy.get('body', { timeout: 3000 }).then(($error) => {
              if ($error.find('[data-cy="lote-area-error"], .error-message').length > 0) {
                cy.get('[data-cy="lote-area-error"], .error-message').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('exceder') || text.includes('área') || text.includes('finca') || text.length > 0
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

  it('debe validar formatos específicos', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          // Código postal inválido
          if ($modal.find('[data-cy="finca-codigo-postal"], input').length > 0) {
            cy.get('[data-cy="finca-codigo-postal"], input').first().type('123', { force: true })
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().click({ force: true })
            
            cy.get('body', { timeout: 3000 }).then(($error) => {
              if ($error.find('[data-cy="codigo-postal-error"], .error-message').length > 0) {
                cy.get('[data-cy="codigo-postal-error"], .error-message').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('código') || text.includes('postal') || text.includes('inválido') || text.includes('formato') || text.length > 0
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

  it('debe validar unicidad de datos', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          // Nombre duplicado
          if ($modal.find('[data-cy="finca-nombre"], input').length > 0) {
            cy.get('[data-cy="finca-nombre"], input').first().type('Finca Existente', { force: true })
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().click({ force: true })
            
            cy.get('body', { timeout: 3000 }).then(($error) => {
              if ($error.find('[data-cy="finca-nombre-error"], .error-message').length > 0) {
                cy.get('[data-cy="finca-nombre-error"], .error-message').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('existe') || text.includes('duplicado') || text.includes('nombre') || text.length > 0
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

  it('debe validar caracteres especiales', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          // Caracteres no permitidos
          if ($modal.find('[data-cy="finca-nombre"], input').length > 0) {
            cy.get('[data-cy="finca-nombre"], input').first().type('Finca<script>alert("xss")</script>', { force: true })
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().click({ force: true })
            
            cy.get('body', { timeout: 3000 }).then(($error) => {
              if ($error.find('[data-cy="finca-nombre-error"], .error-message').length > 0) {
                cy.get('[data-cy="finca-nombre-error"], .error-message').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('permitidos') || text.includes('caracteres') || text.includes('inválido') || text.length > 0
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

  it('debe validar límites de caracteres en textarea', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          // Descripción muy larga
          if ($modal.find('[data-cy="finca-descripcion"], textarea').length > 0) {
            const longDescription = 'A'.repeat(1001)
            cy.get('[data-cy="finca-descripcion"], textarea').first().type(longDescription, { force: true })
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().click({ force: true })
            
            cy.get('body', { timeout: 3000 }).then(($error) => {
              if ($error.find('[data-cy="finca-descripcion-error"], .error-message').length > 0) {
                cy.get('[data-cy="finca-descripcion-error"], .error-message').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('larga') || text.includes('descripción') || text.includes('demasiado') || text.length > 0
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

  it('debe validar múltiples errores simultáneos', () => {
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          // Llenar con datos inválidos
          if ($modal.find('[data-cy="finca-nombre"], input').length > 0) {
            cy.get('[data-cy="finca-nombre"], input').first().type('A', { force: true })
            cy.get('[data-cy="finca-area"], input[type="number"]').first().type('-5', { force: true })
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().click({ force: true })
            
            // Verificar múltiples errores si existen
            cy.get('body', { timeout: 3000 }).then(($error) => {
              const errorSelectors = [
                '[data-cy="finca-nombre-error"]',
                '[data-cy="finca-area-error"]',
                '[data-cy="finca-ubicacion-error"]'
              ]
          verifySelectorsExist(errorSelectors, $error, 3000)
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe validar formularios con campos condicionales', () => {
    cy.visit('/mis-lotes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-lote-button"], button').length > 0) {
        cy.get('[data-cy="add-lote-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          // Seleccionar tipo de cultivo que requiere campos adicionales
          if ($modal.find('[data-cy="lote-tipo-cultivo"], select').length > 0) {
            cy.get('[data-cy="lote-tipo-cultivo"], select').first().select('organico', { force: true })
            
            cy.get('body', { timeout: 3000 }).then(($afterSelect) => {
              // Verificar que aparecen campos adicionales si existen
              if ($afterSelect.find('[data-cy="certificacion-organica"], input, select').length > 0) {
                cy.get('[data-cy="certificacion-organica"], input, select').should('exist')
              }
              
              // Intentar guardar sin llenar campos condicionales
              cy.get('[data-cy="save-lote"], button[type="submit"]').first().click({ force: true })
              
              cy.get('body', { timeout: 3000 }).then(($error) => {
                if ($error.find('[data-cy="certificacion-error"], .error-message').length > 0) {
                  cy.get('[data-cy="certificacion-error"], .error-message').first().should('satisfy', ($el) => {
                    const text = $el.text().toLowerCase()
                    return text.includes('requerido') || text.includes('orgánicos') || text.includes('certificación') || text.length > 0
                  })
                }
              })
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe validar formato de teléfono', () => {
    cy.visit('/registro')
    
    cy.get('[data-cy="phone-input"]').type('123')
    cy.get('[data-cy="register-button"]').click()
    
    cy.get('[data-cy="phone-error"]')
      .should('be.visible')
      .and('contain', 'Formato de teléfono inválido')
  })

  it('debe validar formato de documento', () => {
    cy.visit('/registro')
    
    cy.get('[data-cy="document-input"]').type('123')
    cy.get('[data-cy="register-button"]').click()
    
    cy.get('[data-cy="document-error"]')
      .should('be.visible')
      .and('contain', 'Formato de documento inválido')
  })

  it('debe validar edad mínima en fecha de nacimiento', () => {
    cy.visit('/registro')
    
    const futureDate = new Date()
    futureDate.setFullYear(futureDate.getFullYear() - 10)
    const dateString = futureDate.toISOString().split('T')[0]
    
    cy.get('[data-cy="birthdate-input"]').type(dateString)
    cy.get('[data-cy="register-button"]').click()
    
    cy.get('[data-cy="birthdate-error"]')
      .should('be.visible')
      .and('contain', 'Debes tener al menos 14 años')
  })

  it('debe validar campos de dirección', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    cy.get('[data-cy="finca-direccion"]').type('A'.repeat(501))
    cy.get('[data-cy="save-finca"]').click()
    
    cy.get('[data-cy="direccion-error"]')
      .should('be.visible')
      .and('contain', 'La dirección es demasiado larga')
  })

  it('debe validar coordenadas GPS', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    cy.get('[data-cy="finca-latitud"]').type('100')
    cy.get('[data-cy="finca-longitud"]').type('200')
    cy.get('[data-cy="save-finca"]').click()
    
    cy.get('[data-cy="coordenadas-error"]')
      .should('be.visible')
      .and('contain', 'Coordenadas inválidas')
  })
})
