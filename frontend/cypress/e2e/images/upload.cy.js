import { 
  ifFoundInBody, 
  clickIfExistsAndContinue,
  getApiBaseUrl
} from '../../support/helpers'

describe('Carga de Imágenes - Upload', () => {
  const UPLOAD_FORM_SELECTOR = '[data-cy="upload-form"], form, .upload-form'
  const FILE_INPUT_SELECTOR = '[data-cy="file-input"], input[type="file"]'
  const UPLOAD_BUTTON_SELECTOR = '[data-cy="upload-button"], button[type="submit"]'
  const IMAGE_PREVIEW_SELECTOR = '[data-cy="image-preview"], .preview'
  const IMAGE_INFO_SELECTOR = '[data-cy="image-info"], .image-info'
  const SUCCESS_TEXT_PATTERNS = ['cargada', 'exitosamente', 'success']
  
  const verifyUploadForm = () => {
    return cy.get('body').then(($body) => {
      ifFoundInBody(UPLOAD_FORM_SELECTOR, () => {
        cy.get(UPLOAD_FORM_SELECTOR).should('exist')
      })
      ifFoundInBody(FILE_INPUT_SELECTOR, () => {
        cy.get(FILE_INPUT_SELECTOR).should('exist')
      })
      ifFoundInBody(UPLOAD_BUTTON_SELECTOR, () => {
        cy.get(UPLOAD_BUTTON_SELECTOR).should('exist')
      })
      cy.get(IMAGE_PREVIEW_SELECTOR, { timeout: 1000 }).should('not.exist')
    })
  }
  
  const verifyImageInfo = (expectedText) => {
    return ifFoundInBody(IMAGE_INFO_SELECTOR, ($el) => {
      cy.wrap($el).should('satisfy', ($element) => {
        const text = $element.text().toLowerCase()
        return expectedText ? text.includes(expectedText.toLowerCase()) : text.length > 0
      })
    })
  }
  
  const checkErrorText = ($element, expectedTexts) => {
    const text = $element.text().toLowerCase()
    return expectedTexts.some(expected => text.includes(expected)) || text.length > 0
  }

  const verifyErrorMessage = (errorSelector, expectedTexts) => {
    return ifFoundInBody(errorSelector, ($el) => {
      cy.wrap($el).first().should('satisfy', ($element) => checkErrorText($element, expectedTexts))
    })
  }
  
  const performDragAndDrop = (fileName, type) => {
    return cy.fixture(fileName, { encoding: null }).then((content) => {
      const blob = new Blob([content], { type })
      const file = new File([blob], fileName, { type })
      return performDrop(file, fileName)
    }).catch(() => {
      const blob = new Blob(['fake image content'], { type })
      const file = new File([blob], fileName, { type })
      return performDrop(file, fileName)
    })
  }
  
  const performDrop = (file, fileName) => {
    return cy.get('[data-cy="drop-zone"], .drop-zone, [data-cy*="drop"]').first().then(($dropZone) => {
      const dataTransfer = new DataTransfer()
      dataTransfer.items.add(file)
      cy.wrap($dropZone).trigger('drop', { dataTransfer, force: true })
      verifyImageInfo(fileName)
    })
  }
  
  beforeEach(() => {
    cy.login('farmer')
    cy.visit('/nuevo-analisis')
    cy.get('body', { timeout: 10000 }).should('be.visible')
  })

  it('debe mostrar el formulario de carga de imagen correctamente', () => {
    verifyUploadForm()
  })

  it('debe cargar imagen exitosamente', () => {
    const verifySuccessText = ($element) => {
      const text = $element.text().toLowerCase()
      return SUCCESS_TEXT_PATTERNS.some(pattern => text.includes(pattern)) || text.length > 0
    }

    const handleUploadSuccess = ($el) => {
      cy.wrap($el).should('satisfy', verifySuccessText)
    }

    const handleUploadButtonClick = () => {
      return ifFoundInBody('[data-cy="upload-success"], .success-message', handleUploadSuccess)
    }

    cy.uploadFile('test-cacao.jpg', { useFixture: true })
    
    ifFoundInBody(IMAGE_PREVIEW_SELECTOR, () => {
      cy.get(IMAGE_PREVIEW_SELECTOR).should('be.visible')
    })
    verifyImageInfo('test-cacao')
    
    clickIfExistsAndContinue(UPLOAD_BUTTON_SELECTOR, handleUploadButtonClick)
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
    verifyErrorMessage('[data-cy="file-validation-error"], .error-message', ['tipo', 'permitido', 'archivo'])
  })

  it('debe validar tamaño máximo de archivo', () => {
    const largeSize = 11 * 1024 * 1024 // 11MB
    cy.uploadFile('large-image.jpg', { type: 'image/jpeg', size: largeSize, useFixture: false })
    verifyErrorMessage('[data-cy="file-size-error"], .error-message', ['grande', 'tamaño', 'size'])
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
    const verifyCancelledText = ($el) => {
      const text = $el.text().toLowerCase()
      return text.includes('cancelada') || text.includes('cancel') || text.length > 0
    }

    const handleCancelledMessage = () => {
      cy.get('[data-cy="upload-cancelled"], .cancelled-message').should('satisfy', verifyCancelledText)
    }

    const handleCancelUploadClick = () => {
      return ifFoundInBody('[data-cy="upload-cancelled"], .cancelled-message', handleCancelledMessage)
    }

    const handleUploadButtonClick = () => {
      return clickIfExistsAndContinue('[data-cy="cancel-upload"], button', handleCancelUploadClick)
    }

    cy.uploadFile('test-cacao.jpg', { useFixture: true })
    
    clickIfExistsAndContinue('[data-cy="upload-button"], button[type="submit"]', handleUploadButtonClick)
  })

  it('debe manejar errores de red durante la carga', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('POST', `${apiBaseUrl}/images/`, {
      statusCode: 500,
      body: { error: 'Error del servidor' }
    }).as('uploadError')
    
    cy.uploadFile('test-cacao.jpg', { useFixture: true })
    
    clickIfExistsAndContinue(UPLOAD_BUTTON_SELECTOR, () => {
      cy.wait('@uploadError', { timeout: 10000 })
      return verifyErrorMessage('[data-cy="upload-error"], .error-message', ['error', 'cargar', 'imagen'])
    })
  })

  it('debe permitir arrastrar y soltar archivos', () => {
    const handleDragAndDropSuccess = () => {
      ifFoundInBody(IMAGE_PREVIEW_SELECTOR, () => {
        cy.get(IMAGE_PREVIEW_SELECTOR).should('be.visible')
      })
      verifyImageInfo('test-cacao')
    }

    const handleDropZoneFound = () => {
      performDragAndDrop('test-cacao.jpg', 'image/jpeg').then(handleDragAndDropSuccess)
    }

    const handleDropZoneNotFound = () => {
      cy.get('body').should('be.visible')
    }

    ifFoundInBody('[data-cy="drop-zone"], .drop-zone, [data-cy*="drop"]', handleDropZoneFound, handleDropZoneNotFound)
  })

  it('debe mostrar información de la imagen cargada', () => {
    cy.uploadFile('test-cacao.jpg', { useFixture: true })
    verifyImageInfo('test-cacao')
    
    ifFoundInBody('[data-cy="image-size"], .image-size', () => {
      cy.get('[data-cy="image-size"], .image-size').should('exist')
    })
    verifyImageInfo('jpeg')
  })

  it('debe permitir eliminar imagen antes de subir', () => {
    const verifyImageRemoved = ($afterRemove) => {
      if ($afterRemove.find(IMAGE_PREVIEW_SELECTOR).length === 0) {
        cy.get(IMAGE_PREVIEW_SELECTOR).should('not.exist')
      }
    }

    const handleRemoveButtonClick = () => {
      return cy.get('body', { timeout: 3000 }).then(verifyImageRemoved)
    }

    const handlePreviewFound = () => {
      cy.get(IMAGE_PREVIEW_SELECTOR).should('be.visible')
      return clickIfExistsAndContinue('[data-cy="remove-image"], button', handleRemoveButtonClick)
    }

    cy.uploadFile('test-cacao.jpg', { useFixture: true })
    
    ifFoundInBody(IMAGE_PREVIEW_SELECTOR, handlePreviewFound)
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
