describe('Carga de Imágenes - Upload', () => {
  beforeEach(() => {
    cy.login('farmer')
    cy.visit('/nuevo-analisis')
  })

  it('debe mostrar el formulario de carga de imagen correctamente', () => {
    cy.get('[data-cy="upload-form"]').should('be.visible')
    cy.get('[data-cy="file-input"]').should('be.visible')
    cy.get('[data-cy="upload-button"]').should('be.visible')
    cy.get('[data-cy="image-preview"]').should('not.exist')
  })

  it('debe cargar imagen exitosamente', () => {
    // Crear imagen de prueba
    cy.fixture('test-cacao.jpg').then((fileContent) => {
      const blob = new Blob([fileContent], { type: 'image/jpeg' })
      const file = new File([blob], 'test-cacao.jpg', { type: 'image/jpeg' })
      
      cy.get('[data-cy="file-input"]').then((input) => {
        const dataTransfer = new DataTransfer()
        dataTransfer.items.add(file)
        input[0].files = dataTransfer.files
        
        cy.wrap(input).trigger('change', { force: true })
      })
      
      // Verificar preview de imagen
      cy.get('[data-cy="image-preview"]').should('be.visible')
      cy.get('[data-cy="image-info"]').should('contain', 'test-cacao.jpg')
      
      // Subir imagen
      cy.get('[data-cy="upload-button"]').click()
      
      // Verificar mensaje de éxito
      cy.get('[data-cy="upload-success"]')
        .should('be.visible')
        .and('contain', 'Imagen cargada exitosamente')
    })
  })

  it('debe validar tipos de archivo permitidos', () => {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png']
    const disallowedTypes = ['text/plain', 'application/pdf', 'video/mp4']
    
    // Test archivos permitidos
    allowedTypes.forEach(type => {
      cy.get('[data-cy="file-input"]').then((input) => {
        const blob = new Blob(['fake image content'], { type })
        const file = new File([blob], `test.${type.split('/')[1]}`, { type })
        
        const dataTransfer = new DataTransfer()
        dataTransfer.items.add(file)
        input[0].files = dataTransfer.files
        
        cy.wrap(input).trigger('change', { force: true })
        
        cy.get('[data-cy="file-validation-success"]').should('be.visible')
      })
    })
  })

  it('debe rechazar tipos de archivo no permitidos', () => {
    cy.get('[data-cy="file-input"]').then((input) => {
      const blob = new Blob(['fake content'], { type: 'text/plain' })
      const file = new File([blob], 'test.txt', { type: 'text/plain' })
      
      const dataTransfer = new DataTransfer()
      dataTransfer.items.add(file)
      input[0].files = dataTransfer.files
      
      cy.wrap(input).trigger('change', { force: true })
      
      cy.get('[data-cy="file-validation-error"]')
        .should('be.visible')
        .and('contain', 'Tipo de archivo no permitido')
    })
  })

  it('debe validar tamaño máximo de archivo', () => {
    // Simular archivo muy grande (más de 10MB)
    cy.get('[data-cy="file-input"]').then((input) => {
      const largeContent = 'x'.repeat(11 * 1024 * 1024) // 11MB
      const blob = new Blob([largeContent], { type: 'image/jpeg' })
      const file = new File([blob], 'large-image.jpg', { type: 'image/jpeg' })
      
      const dataTransfer = new DataTransfer()
      dataTransfer.items.add(file)
      input[0].files = dataTransfer.files
      
      cy.wrap(input).trigger('change', { force: true })
      
      cy.get('[data-cy="file-size-error"]')
        .should('be.visible')
        .and('contain', 'Archivo demasiado grande')
    })
  })

  it('debe mostrar progreso de carga', () => {
    cy.fixture('test-cacao.jpg').then((fileContent) => {
      const blob = new Blob([fileContent], { type: 'image/jpeg' })
      const file = new File([blob], 'test-cacao.jpg', { type: 'image/jpeg' })
      
      cy.get('[data-cy="file-input"]').then((input) => {
        const dataTransfer = new DataTransfer()
        dataTransfer.items.add(file)
        input[0].files = dataTransfer.files
        
        cy.wrap(input).trigger('change', { force: true })
      })
      
      cy.get('[data-cy="upload-button"]').click()
      
      // Verificar barra de progreso
      cy.get('[data-cy="upload-progress"]').should('be.visible')
      cy.get('[data-cy="upload-progress"]').should('contain', '%')
    })
  })

  it('debe permitir cancelar carga en progreso', () => {
    cy.fixture('test-cacao.jpg').then((fileContent) => {
      const blob = new Blob([fileContent], { type: 'image/jpeg' })
      const file = new File([blob], 'test-cacao.jpg', { type: 'image/jpeg' })
      
      cy.get('[data-cy="file-input"]').then((input) => {
        const dataTransfer = new DataTransfer()
        dataTransfer.items.add(file)
        input[0].files = dataTransfer.files
        
        cy.wrap(input).trigger('change', { force: true })
      })
      
      cy.get('[data-cy="upload-button"]').click()
      
      // Cancelar carga
      cy.get('[data-cy="cancel-upload"]').click()
      
      // Verificar que se canceló
      cy.get('[data-cy="upload-cancelled"]')
        .should('be.visible')
        .and('contain', 'Carga cancelada')
    })
  })

  it('debe manejar errores de red durante la carga', () => {
    // Simular error de red
    cy.intercept('POST', '/api/images/', {
      statusCode: 500,
      body: { error: 'Error del servidor' }
    }).as('uploadError')
    
    cy.fixture('test-cacao.jpg').then((fileContent) => {
      const blob = new Blob([fileContent], { type: 'image/jpeg' })
      const file = new File([blob], 'test-cacao.jpg', { type: 'image/jpeg' })
      
      cy.get('[data-cy="file-input"]').then((input) => {
        const dataTransfer = new DataTransfer()
        dataTransfer.items.add(file)
        input[0].files = dataTransfer.files
        
        cy.wrap(input).trigger('change', { force: true })
      })
      
      cy.get('[data-cy="upload-button"]').click()
      
      cy.wait('@uploadError')
      
      cy.get('[data-cy="upload-error"]')
        .should('be.visible')
        .and('contain', 'Error al cargar imagen')
    })
  })

  it('debe permitir arrastrar y soltar archivos', () => {
    cy.fixture('test-cacao.jpg').then((fileContent) => {
      const blob = new Blob([fileContent], { type: 'image/jpeg' })
      const file = new File([blob], 'test-cacao.jpg', { type: 'image/jpeg' })
      
      cy.get('[data-cy="drop-zone"]').then((dropZone) => {
        const dataTransfer = new DataTransfer()
        dataTransfer.items.add(file)
        
        cy.wrap(dropZone).trigger('drop', { dataTransfer })
      })
      
      // Verificar que se cargó la imagen
      cy.get('[data-cy="image-preview"]').should('be.visible')
      cy.get('[data-cy="image-info"]').should('contain', 'test-cacao.jpg')
    })
  })

  it('debe mostrar información de la imagen cargada', () => {
    cy.fixture('test-cacao.jpg').then((fileContent) => {
      const blob = new Blob([fileContent], { type: 'image/jpeg' })
      const file = new File([blob], 'test-cacao.jpg', { type: 'image/jpeg' })
      
      cy.get('[data-cy="file-input"]').then((input) => {
        const dataTransfer = new DataTransfer()
        dataTransfer.items.add(file)
        input[0].files = dataTransfer.files
        
        cy.wrap(input).trigger('change', { force: true })
      })
      
      // Verificar información mostrada
      cy.get('[data-cy="image-info"]').should('contain', 'test-cacao.jpg')
      cy.get('[data-cy="image-size"]').should('be.visible')
      cy.get('[data-cy="image-type"]').should('contain', 'JPEG')
    })
  })

  it('debe permitir eliminar imagen antes de subir', () => {
    cy.fixture('test-cacao.jpg').then((fileContent) => {
      const blob = new Blob([fileContent], { type: 'image/jpeg' })
      const file = new File([blob], 'test-cacao.jpg', { type: 'image/jpeg' })
      
      cy.get('[data-cy="file-input"]').then((input) => {
        const dataTransfer = new DataTransfer()
        dataTransfer.items.add(file)
        input[0].files = dataTransfer.files
        
        cy.wrap(input).trigger('change', { force: true })
      })
      
      cy.get('[data-cy="image-preview"]').should('be.visible')
      
      // Eliminar imagen
      cy.get('[data-cy="remove-image"]').click()
      
      // Verificar que se eliminó
      cy.get('[data-cy="image-preview"]').should('not.exist')
      cy.get('[data-cy="file-input"]').should('have.value', '')
    })
  })
})
