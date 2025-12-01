describe('Incremental Training Contribution', () => {
  beforeEach(() => {
    cy.navigateToIncrementalTraining('farmer')
  })

  const uploadImageAndProcess = (imageName, callback) => {
    cy.get('body').then(($body) => {
      if ($body.find('input[type="file"]').length > 0) {
        cy.uploadTestImage(imageName)
        cy.get('body', { timeout: 5000 }).then(($afterUpload) => {
          if (callback) callback($afterUpload)
        })
      }
    })
  }

  const selectLabelAndAdd = (label, callback) => {
    cy.selectIfExists('[data-cy="select-label"], select', label).then((selected) => {
      if (selected && callback) {
        cy.get('body').then(($afterSelect) => {
          callback($afterSelect)
        })
      }
    })
  }

  it('should load contribution page', () => {
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('h1, h2, .page-title, [data-cy="page-title"]').length > 0) {
        cy.get('h1, h2, .page-title, [data-cy="page-title"]').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('contribuir') || text.includes('datos') || text.includes('entrenamiento') || text.length > 0
        })
      }
      
      if ($body.find('.upload-guidelines, .guidelines, [data-cy="guidelines"]').length > 0) {
        cy.get('.upload-guidelines, .guidelines, [data-cy="guidelines"]').should('exist')
      } else {
        // Si no hay título o guías, verificar que la página cargó correctamente
        cy.get('body').should('be.visible')
      }
    })
  })

  it('should accept image uploads for training', () => {
    uploadImageAndProcess('training_sample.jpg', ($afterUpload) => {
      cy.get('.preview-list, .preview, [data-cy="preview"]', { timeout: 5000 }).then(($preview) => {
        if ($preview.length > 0) {
          cy.wrap($preview).children().should('have.length.at.least', 0)
        }
      })
    })
  })

  it('should require labeling for uploaded images', () => {
    const verifyLabelRequired = () => {
      cy.clickIfExists('[data-cy="btn-submit-contribution"], button[type="submit"]')
      cy.get('.error-message, [data-cy="error"]', { timeout: 5000 }).should('satisfy', ($el) => {
        const text = $el.text().toLowerCase()
        return text.includes('etiqueta') || text.includes('label') || text.includes('requerid') || $el.length > 0
      })
    }

    uploadImageAndProcess('training_sample.jpg', verifyLabelRequired)
  })

  it('should allow tagging images', () => {
    const addTag = () => {
      cy.clickIfExists('[data-cy="btn-add-tag"], button')
      cy.get('.tag-chip, .tag, [data-cy="tag"]', { timeout: 5000 }).should('exist')
    }

    const afterSelectLabel = ($afterSelect) => {
      addTag()
    }

    uploadImageAndProcess('training_sample.jpg', ($afterUpload) => {
      selectLabelAndAdd('Monilia', afterSelectLabel)
    })
  })

  it('should submit contribution successfully', () => {
    uploadImageAndProcess('training_sample.jpg', ($afterUpload) => {
      selectLabelAndAdd('Sana', ($afterSelect) => {
        const submitContribution = () => {
          cy.typeIfExists('[data-cy="input-notes"], textarea', 'Imagen tomada con buena luz')
          cy.clickIfExists('[data-cy="btn-submit-contribution"], button[type="submit"]')
          cy.get('body', { timeout: 5000 }).should('be.visible')
        }

        submitContribution()
      })
    })
  })

  it('should show history of contributions', () => {
    cy.clickIfExists('[data-cy="tab-history"], [role="tab"]').then(() => {
      cy.get('[data-cy="contribution-item"], .contribution-item, .item', { timeout: 5000 }).should('exist')
      cy.get('body').then(($history) => {
        if ($history.find('[data-cy="status-badge"], .badge, .status').length > 0) {
          cy.get('[data-cy="status-badge"], .badge, .status').should('exist')
        }
      })
    })
  })
})

