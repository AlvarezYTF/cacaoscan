describe('Manejo de Errores - Validación y Formularios', () => {
  beforeEach(() => {
    cy.login('farmer')
  })

  it('debe validar campos requeridos en formulario de finca', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    // Intentar guardar sin llenar campos
    cy.get('[data-cy="save-finca"]').click()
    
    // Verificar errores de validación
    cy.get('[data-cy="finca-nombre-error"]')
      .should('be.visible')
      .and('contain', 'Este campo es requerido')
    
    cy.get('[data-cy="finca-ubicacion-error"]')
      .should('be.visible')
      .and('contain', 'Este campo es requerido')
    
    cy.get('[data-cy="finca-area-error"]')
      .should('be.visible')
      .and('contain', 'Este campo es requerido')
  })

  it('debe validar formato de email en registro', () => {
    cy.visit('/registro')
    
    // Llenar con email inválido
    cy.get('[data-cy="email-input"]').type('email-invalido')
    cy.get('[data-cy="register-button"]').click()
    
    // Verificar error de formato
    cy.get('[data-cy="email-error"]')
      .should('be.visible')
      .and('contain', 'Formato de email inválido')
  })

  it('debe validar fortaleza de contraseña', () => {
    cy.visit('/registro')
    
    const weakPasswords = ['123', 'password', '12345678']
    
    weakPasswords.forEach(password => {
      cy.get('[data-cy="password-input"]').clear().type(password)
      cy.get('[data-cy="password-strength"]')
        .should('be.visible')
        .and('contain', 'Contraseña débil')
    })
    
    // Verificar contraseña fuerte
    cy.get('[data-cy="password-input"]').clear().type('StrongPassword123!')
    cy.get('[data-cy="password-strength"]')
      .should('be.visible')
      .and('contain', 'Contraseña fuerte')
  })

  it('debe validar coincidencia de contraseñas', () => {
    cy.visit('/registro')
    
    cy.get('[data-cy="password-input"]').type('Password123!')
    cy.get('[data-cy="confirm-password-input"]').type('DifferentPassword123!')
    cy.get('[data-cy="register-button"]').click()
    
    // Verificar error de coincidencia
    cy.get('[data-cy="password-match-error"]')
      .should('be.visible')
      .and('contain', 'Las contraseñas no coinciden')
  })

  it('debe validar longitud de campos de texto', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    // Nombre muy corto
    cy.get('[data-cy="finca-nombre"]').type('A')
    cy.get('[data-cy="save-finca"]').click()
    
    cy.get('[data-cy="finca-nombre-error"]')
      .should('be.visible')
      .and('contain', 'El nombre debe tener al menos 3 caracteres')
    
    // Nombre muy largo
    cy.get('[data-cy="finca-nombre"]').clear().type('A'.repeat(100))
    cy.get('[data-cy="save-finca"]').click()
    
    cy.get('[data-cy="finca-nombre-error"]')
      .should('be.visible')
      .and('contain', 'El nombre es demasiado largo')
  })

  it('debe validar rangos numéricos', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    // Área negativa
    cy.get('[data-cy="finca-area"]').type('-10')
    cy.get('[data-cy="save-finca"]').click()
    
    cy.get('[data-cy="finca-area-error"]')
      .should('be.visible')
      .and('contain', 'El área debe ser positiva')
    
    // Área muy grande
    cy.get('[data-cy="finca-area"]').clear().type('999999999')
    cy.get('[data-cy="save-finca"]').click()
    
    cy.get('[data-cy="finca-area-error"]')
      .should('be.visible')
      .and('contain', 'El área es demasiado grande')
  })

  it('debe validar fechas', () => {
    cy.visit('/mis-lotes')
    cy.get('[data-cy="add-lote-button"]').click()
    
    // Fecha futura
    cy.get('[data-cy="lote-fecha-plantacion"]').type('2030-01-01')
    cy.get('[data-cy="save-lote"]').click()
    
    cy.get('[data-cy="lote-fecha-error"]')
      .should('be.visible')
      .and('contain', 'La fecha no puede ser futura')
  })

  it('debe validar archivos', () => {
    cy.visit('/nuevo-analisis')
    
    // Archivo muy grande
    cy.get('[data-cy="file-input"]').then((input) => {
      const largeContent = 'x'.repeat(11 * 1024 * 1024) // 11MB
      const blob = new Blob([largeContent], { type: 'image/jpeg' })
      const file = new File([blob], 'large-image.jpg', { type: 'image/jpeg' })
      
      const dataTransfer = new DataTransfer()
      dataTransfer.items.add(file)
      input[0].files = dataTransfer.files
      
      cy.wrap(input).trigger('change', { force: true })
    })
    
    cy.get('[data-cy="file-size-error"]')
      .should('be.visible')
      .and('contain', 'Archivo demasiado grande')
  })

  it('debe validar selecciones requeridas', () => {
    cy.visit('/mis-lotes')
    cy.get('[data-cy="add-lote-button"]').click()
    
    // No seleccionar finca
    cy.get('[data-cy="save-lote"]').click()
    
    cy.get('[data-cy="finca-select-error"]')
      .should('be.visible')
      .and('contain', 'Debe seleccionar una finca')
  })

  it('debe validar checkboxes requeridos', () => {
    cy.visit('/registro')
    
    // No marcar términos y condiciones
    cy.get('[data-cy="register-button"]').click()
    
    cy.get('[data-cy="terms-error"]')
      .should('be.visible')
      .and('contain', 'Debes aceptar los términos')
  })

  it('debe validar en tiempo real', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    // Verificar validación en tiempo real
    cy.get('[data-cy="finca-nombre"]').type('A')
    cy.get('[data-cy="finca-nombre-error"]')
      .should('be.visible')
      .and('contain', 'El nombre debe tener al menos 3 caracteres')
    
    // Corregir y verificar que desaparece el error
    cy.get('[data-cy="finca-nombre"]').type('bc')
    cy.get('[data-cy="finca-nombre-error"]').should('not.exist')
  })

  it('debe validar formularios complejos', () => {
    cy.visit('/mis-lotes')
    cy.get('[data-cy="add-lote-button"]').click()
    
    // Llenar parcialmente
    cy.get('[data-cy="lote-nombre"]').type('Lote Test')
    cy.get('[data-cy="lote-area"]').type('5')
    
    // Verificar que algunos campos siguen siendo requeridos
    cy.get('[data-cy="save-lote"]').click()
    
    cy.get('[data-cy="lote-variedad-error"]')
      .should('be.visible')
      .and('contain', 'Este campo es requerido')
  })

  it('debe validar dependencias entre campos', () => {
    cy.visit('/mis-lotes')
    cy.get('[data-cy="add-lote-button"]').click()
    
    // Seleccionar finca
    cy.get('[data-cy="finca-select"]').select('1')
    
    // Área del lote mayor que área de la finca
    cy.get('[data-cy="lote-area"]').type('100')
    cy.get('[data-cy="save-lote"]').click()
    
    cy.get('[data-cy="lote-area-error"]')
      .should('be.visible')
      .and('contain', 'El área del lote no puede exceder el área de la finca')
  })

  it('debe validar formatos específicos', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    // Código postal inválido
    cy.get('[data-cy="finca-codigo-postal"]').type('123')
    cy.get('[data-cy="save-finca"]').click()
    
    cy.get('[data-cy="codigo-postal-error"]')
      .should('be.visible')
      .and('contain', 'Formato de código postal inválido')
  })

  it('debe validar unicidad de datos', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    // Nombre duplicado
    cy.get('[data-cy="finca-nombre"]').type('Finca Existente')
    cy.get('[data-cy="save-finca"]').click()
    
    cy.get('[data-cy="finca-nombre-error"]')
      .should('be.visible')
      .and('contain', 'Ya existe una finca con este nombre')
  })

  it('debe validar caracteres especiales', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    // Caracteres no permitidos
    cy.get('[data-cy="finca-nombre"]').type('Finca<script>alert("xss")</script>')
    cy.get('[data-cy="save-finca"]').click()
    
    cy.get('[data-cy="finca-nombre-error"]')
      .should('be.visible')
      .and('contain', 'Caracteres no permitidos')
  })

  it('debe validar límites de caracteres en textarea', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    // Descripción muy larga
    const longDescription = 'A'.repeat(1001)
    cy.get('[data-cy="finca-descripcion"]').type(longDescription)
    cy.get('[data-cy="save-finca"]').click()
    
    cy.get('[data-cy="finca-descripcion-error"]')
      .should('be.visible')
      .and('contain', 'La descripción es demasiado larga')
  })

  it('debe validar múltiples errores simultáneos', () => {
    cy.visit('/mis-fincas')
    cy.get('[data-cy="add-finca-button"]').click()
    
    // Llenar con datos inválidos
    cy.get('[data-cy="finca-nombre"]').type('A')
    cy.get('[data-cy="finca-area"]').type('-5')
    cy.get('[data-cy="save-finca"]').click()
    
    // Verificar múltiples errores
    cy.get('[data-cy="finca-nombre-error"]').should('be.visible')
    cy.get('[data-cy="finca-area-error"]').should('be.visible')
    cy.get('[data-cy="finca-ubicacion-error"]').should('be.visible')
  })

  it('debe validar formularios con campos condicionales', () => {
    cy.visit('/mis-lotes')
    cy.get('[data-cy="add-lote-button"]').click()
    
    // Seleccionar tipo de cultivo que requiere campos adicionales
    cy.get('[data-cy="lote-tipo-cultivo"]').select('organico')
    
    // Verificar que aparecen campos adicionales
    cy.get('[data-cy="certificacion-organica"]').should('be.visible')
    
    // Intentar guardar sin llenar campos condicionales
    cy.get('[data-cy="save-lote"]').click()
    
    cy.get('[data-cy="certificacion-error"]')
      .should('be.visible')
      .and('contain', 'Este campo es requerido para cultivos orgánicos')
  })
})
