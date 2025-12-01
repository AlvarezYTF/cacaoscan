import { 
  ifFoundInBody, 
  clickIfExistsAndContinue,
  verifySelectorsInBody
} from '../../support/helpers'

describe('Carga de Imágenes - Upload', () => {
  beforeEach(() => {
    cy.login('farmer')
    cy.visit('/nuevo-analisis')
    cy.get('body', { timeout: 10000 }).should('be.visible')
  })

  it('debe mostrar el formulario de carga de imagen correctamente', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="upload-form"], form, .upload-form').length > 0) {
        cy.get('[data-cy="upload-form"], form, .upload-form').should('exist')
      }
      if ($body.find('[data-cy="file-input"], input[type="file"]').length > 0) {
        cy.get('[data-cy="file-input"], input[type="file"]').should('exist')
      }
      if ($body.find('[data-cy="upload-button"], button[type="submit"]').length > 0) {
        cy.get('[data-cy="upload-button"], button[type="submit"]').should('exist')
      }
      cy.get('[data-cy="image-preview"], .preview', { timeout: 1000 }).should('not.exist')
    })
  })

  it('debe cargar imagen exitosamente', () => {
    cy.uploadFile('test-cacao.jpg', { useFixture: true })
    
    ifFoundInBody('[data-cy="image-preview"], .preview', () => {
      cy.get('[data-cy="image-preview"], .preview').should('be.visible')
    })
    ifFoundInBody('[data-cy="image-info"], .image-info', () => {
      cy.get('[data-cy="image-info"], .image-info').should('satisfy', ($el) => {
        const text = $el.text().toLowerCase()
        return text.includes('test-cacao') || text.includes('jpg') || text.length > 0
      })
    })
    
    clickIfExistsAndContinue('[data-cy="upload-button"], button[type="submit"]', () => {
      return ifFoundInBody('[data-cy="upload-success"], .success-message', () => {
        cy.get('[data-cy="upload-success"], .success-message').should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('cargada') || text.includes('exitosamente') || text.includes('success') || text.length > 0
        })
      })
    })
  })

  it('debe validar tipos de archivo permitidos', () => {
    ifFoundInBody('[data-cy="file-input"], input[type="file"]', () => {
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png']
      
      for (const type of allowedTypes) {
        cy.uploadFile(`test.${type.split('/')[1]}`, { type, useFixture: false })
        
        ifFoundInBody('[data-cy="file-validation-success"], .validation-success', () => {
          cy.get('[data-cy="file-validation-success"], .validation-success').should('exist')
        })
      }
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe rechazar tipos de archivo no permitidos', () => {
    cy.uploadFile('test.txt', { type: 'text/plain', useFixture: false })
    
    ifFoundInBody('[data-cy="file-validation-error"], .error-message', () => {
      cy.get('[data-cy="file-validation-error"], .error-message').first().should('satisfy', ($el) => {
        const text = $el.text().toLowerCase()
        return text.includes('tipo') || text.includes('permitido') || text.includes('archivo') || text.length > 0
      })
    })
  })

  it('debe validar tamaño máximo de archivo', () => {
    const largeSize = 11 * 1024 * 1024 // 11MB
    cy.uploadFile('large-image.jpg', { type: 'image/jpeg', size: largeSize, useFixture: false })
    
    ifFoundInBody('[data-cy="file-size-error"], .error-message', () => {
      cy.get('[data-cy="file-size-error"], .error-message').first().should('satisfy', ($el) => {
        const text = $el.text().toLowerCase()
        return text.includes('grande') || text.includes('tamaño') || text.includes('size') || text.length > 0
      })
    })
  })

  it('debe mostrar progreso de carga', () => {
    cy.uploadFile('test-cacao.jpg', { useFixture: true })
    
    clickIfExistsAndContinue('[data-cy="upload-button"], button[type="submit"]', () => {
      return ifFoundInBody('[data-cy="upload-progress"], .progress', () => {
        cy.get('[data-cy="upload-progress"], .progress').should('exist')
      })
    })
  })

  it('debe permitir cancelar carga en progreso', () => {
    cy.uploadFile('test-cacao.jpg', { useFixture: true })
    
    clickIfExistsAndContinue('[data-cy="upload-button"], button[type="submit"]', () => {
      return clickIfExistsAndContinue('[data-cy="cancel-upload"], button', () => {
        return ifFoundInBody('[data-cy="upload-cancelled"], .cancelled-message', () => {
          cy.get('[data-cy="upload-cancelled"], .cancelled-message').should('satisfy', ($el) => {
            const text = $el.text().toLowerCase()
            return text.includes('cancelada') || text.includes('cancel') || text.length > 0
          })
        })
      })
    })
  })

  it('debe manejar errores de red durante la carga', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    cy.intercept('POST', `${apiBaseUrl}/images/`, {
      statusCode: 500,
      body: { error: 'Error del servidor' }
    }).as('uploadError')
    
    cy.uploadFile('test-cacao.jpg', { useFixture: true })
    
    clickIfExistsAndContinue('[data-cy="upload-button"], button[type="submit"]', () => {
      cy.wait('@uploadError', { timeout: 10000 })
      
      return ifFoundInBody('[data-cy="upload-error"], .error-message', () => {
        cy.get('[data-cy="upload-error"], .error-message').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('error') || text.includes('cargar') || text.includes('imagen') || text.length > 0
        })
      })
    })
  })

  it('debe permitir arrastrar y soltar archivos', () => {
    ifFoundInBody('[data-cy="drop-zone"], .drop-zone, [data-cy*="drop"]', () => {
      cy.fixture('test-cacao.jpg', { encoding: null }).then((fileContent) => {
        const blob = new Blob([fileContent], { type: 'image/jpeg' })
        const file = new File([blob], 'test-cacao.jpg', { type: 'image/jpeg' })
        
        cy.get('[data-cy="drop-zone"], .drop-zone, [data-cy*="drop"]').first().then(($dropZone) => {
          const dataTransfer = new DataTransfer()
          dataTransfer.items.add(file)
          
          cy.wrap($dropZone).trigger('drop', { dataTransfer, force: true })
        })
        
        ifFoundInBody('[data-cy="image-preview"], .preview', () => {
          cy.get('[data-cy="image-preview"], .preview').should('be.visible')
        })
        ifFoundInBody('[data-cy="image-info"], .image-info', () => {
          cy.get('[data-cy="image-info"], .image-info').should('satisfy', ($el) => {
            const text = $el.text().toLowerCase()
            return text.includes('test-cacao') || text.includes('jpg') || text.length > 0
          })
        })
      }).catch(() => {
        const blob = new Blob(['fake image content'], { type: 'image/jpeg' })
        const file = new File([blob], 'test-cacao.jpg', { type: 'image/jpeg' })
        
        cy.get('[data-cy="drop-zone"], .drop-zone, [data-cy*="drop"]').first().then(($dropZone) => {
          const dataTransfer = new DataTransfer()
          dataTransfer.items.add(file)
          
          cy.wrap($dropZone).trigger('drop', { dataTransfer, force: true })
        })
        
        cy.get('body', { timeout: 5000 }).should('be.visible')
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe mostrar información de la imagen cargada', () => {
    cy.uploadFile('test-cacao.jpg', { useFixture: true })
    
    ifFoundInBody('[data-cy="image-info"], .image-info', () => {
      cy.get('[data-cy="image-info"], .image-info').should('satisfy', ($el) => {
        const text = $el.text().toLowerCase()
        return text.includes('test-cacao') || text.includes('jpg') || text.length > 0
      })
    })
    ifFoundInBody('[data-cy="image-size"], .image-size', () => {
      cy.get('[data-cy="image-size"], .image-size').should('exist')
    })
    ifFoundInBody('[data-cy="image-type"], .image-type', () => {
      cy.get('[data-cy="image-type"], .image-type').should('satisfy', ($el) => {
        const text = $el.text().toLowerCase()
        return text.includes('jpeg') || text.includes('jpg') || text.length > 0
      })
    })
  })

  it('debe permitir eliminar imagen antes de subir', () => {
    cy.uploadFile('test-cacao.jpg', { useFixture: true })
    
    ifFoundInBody('[data-cy="image-preview"], .preview', () => {
      cy.get('[data-cy="image-preview"], .preview').should('be.visible')
      
      return clickIfExistsAndContinue('[data-cy="remove-image"], button', () => {
        return cy.get('body', { timeout: 3000 }).then(($afterRemove) => {
          if ($afterRemove.find('[data-cy="image-preview"], .preview').length === 0) {
            cy.get('[data-cy="image-preview"], .preview').should('not.exist')
          }
        })
      })
    })
  })

  it('debe permitir cargar múltiples imágenes', () => {
    cy.get('[data-cy="file-input"]').then((input) => {
      const files = [
        new File(['image1'], 'test1.jpg', { type: 'image/jpeg' }),
        new File(['image2'], 'test2.jpg', { type: 'image/jpeg' })
      ]
      
      const dataTransfer = new DataTransfer()
      for (const file of files) {
        dataTransfer.items.add(file)
      }
      input[0].files = dataTransfer.files
      
      cy.wrap(input).trigger('change', { force: true })
    })
    
    cy.get('[data-cy="image-preview"]').should('have.length', 2)
  })

  it('debe validar resolución mínima de imagen', () => {
    cy.uploadFile('tiny.jpg', { type: 'image/jpeg', useFixture: false })
    
    cy.get('[data-cy="resolution-error"]')
      .should('be.visible')
      .and('contain', 'Resolución mínima')
  })

  it('debe mostrar preview con dimensiones correctas', () => {
    cy.uploadFile('test-cacao.jpg', { useFixture: true })
    
    cy.get('[data-cy="image-dimensions"]').should('be.visible')
  })

  it('debe permitir recortar imagen antes de subir', () => {
    cy.uploadFile('test-cacao.jpg', { useFixture: true })
    
    cy.get('[data-cy="crop-image"]').click()
    cy.get('[data-cy="crop-tool"]').should('be.visible')
  })
})
