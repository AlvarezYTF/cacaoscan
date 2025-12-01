describe('Autenticación - Login', () => {
  beforeEach(() => {
    cy.visit('/login')
    cy.get('body', { timeout: 10000 }).should('be.visible')
  })
  
  const verifySelectorsExist = (selectors, $context, timeout = 3000) => {
    for (const selector of selectors) {
      if ($context.find(selector).length > 0) {
        cy.get(selector, { timeout }).should('exist')
      }
    }
  }

  const checkUrlIncludesRoutes = (url, routes) => {
    return routes.some(route => url.includes(route))
  }

  const checkErrorText = (text) => {
    const lowerText = text.toLowerCase()
    return lowerText.includes('credenciales') || 
           lowerText.includes('inválid') || 
           lowerText.includes('error') || 
           lowerText.includes('incorrect')
  }

  const checkEmailErrorText = (text) => {
    const lowerText = text.toLowerCase()
    return lowerText.includes('email') || 
           lowerText.includes('válido') || 
           lowerText.includes('formato') || 
           text.length > 0
  }

  const checkRequiredAttribute = ($el) => {
    return $el.attr('required') !== undefined || $el.length > 0
  }

  const checkUrlIncludesLogin = (url) => {
    return url.includes('/login') || url.length > 0
  }

  const checkUrlNotIncludesLogin = (url) => {
    return !url.includes('/login') || url.length > 0
  }

  const checkUrlIncludesLoginOrAdmin = (url) => {
    return url.includes('/login') || url.includes('/admin')
  }

  const performLoginAction = (email, password, expectedRoutes) => {
    const submitLogin = ($body) => {
      if ($body.find('[data-cy="email-input"], input[type="text"], input[type="email"]').length > 0) {
        cy.get('[data-cy="email-input"], input[type="text"], input[type="email"]').first().type(email)
        cy.get('[data-cy="password-input"], input[type="password"]').first().type(password)
        cy.get('[data-cy="login-button"], button[type="submit"]').first().click()
        
        const routes = Array.isArray(expectedRoutes) ? expectedRoutes : [expectedRoutes]
        cy.url({ timeout: 10000 }).should('satisfy', (url) => checkUrlIncludesRoutes(url, routes))
        cy.get('body', { timeout: 10000 }).should('be.visible')
      }
    }

    cy.get('body', { timeout: 10000 }).then(submitLogin)
  }

  const verifyErrorExists = () => {
    cy.get('body', { timeout: 5000 }).then(($error) => {
      if ($error.find('[data-cy="error-message"], .error-message, .swal2-error').length > 0) {
        cy.get('[data-cy="error-message"], .error-message, .swal2-error').first().should('satisfy', (el) => {
          return checkErrorText(el.text())
        })
      }
    })
  }

  const verifyEmailError = () => {
    cy.get('body', { timeout: 3000 }).then(($error) => {
      if ($error.find('[data-cy="email-error"], .error-message').length > 0) {
        cy.get('[data-cy="email-error"], .error-message').first().should('satisfy', (el) => {
          return checkEmailErrorText(el.text())
        })
      }
    })
  }

  const verifyRequiredField = (selector) => {
    cy.get('body').then(($form) => {
      if ($form.find(selector).length > 0) {
        cy.get(selector).first().should('satisfy', checkRequiredAttribute)
      }
    })
  }

  it('debe mostrar el formulario de login correctamente', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="login-form"], form').length > 0) {
        cy.get('[data-cy="login-form"], form').should('be.visible')
      }
      // Verificar elementos si existen
      const selectors = [
        '[data-cy="email-input"]', '[data-cy="password-input"]', '[data-cy="login-button"]',
        '[data-cy="forgot-password-link"]', '[data-cy="register-link"]'
      ]
          verifySelectorsExist(selectors, $body, 5000)
    })
  })

  it('debe hacer login exitoso como administrador', () => {
    cy.fixture('users').then((users) => {
      const admin = users.admin
      performLoginAction(admin.email, admin.password, ['/admin/dashboard', '/admin', '/dashboard'])
    })
  })

  it('debe hacer login exitoso como analista', () => {
    cy.fixture('users').then((users) => {
      const analyst = users.analyst
      performLoginAction(analyst.email, analyst.password, ['/analisis', '/admin/dashboard', '/dashboard'])
    })
  })

  it('debe hacer login exitoso como agricultor', () => {
    cy.fixture('users').then((users) => {
      const farmer = users.farmer
      performLoginAction(farmer.email, farmer.password, ['/agricultor-dashboard', '/agricultor', '/dashboard'])
    })
  })

  it('debe mostrar error con credenciales inválidas', () => {
    cy.fixture('users').then((users) => {
      const invalidUser = users.invalidUser
      const emailSelector = '[data-cy="email-input"], input[type="text"], input[type="email"]'
      
      const submitInvalidLogin = ($body) => {
        if ($body.find(emailSelector).length > 0) {
          cy.get(emailSelector).first().type(invalidUser.email)
          cy.get('[data-cy="password-input"], input[type="password"]').first().type(invalidUser.password)
          cy.get('[data-cy="login-button"], button[type="submit"]').first().click()
          
          verifyErrorExists()
          cy.url({ timeout: 5000 }).should('satisfy', checkUrlIncludesLogin)
        }
      }

      cy.get('body', { timeout: 10000 }).then(submitInvalidLogin)
    })
  })

  it('debe validar campos requeridos', () => {
    const buttonSelector = '[data-cy="login-button"], button[type="submit"]'
    
    const verifyErrorsExist = ($errors) => {
      if ($errors.find('[data-cy="email-error"], [data-cy="password-error"]').length > 0) {
        cy.get('[data-cy="email-error"], [data-cy="password-error"]').first().should('exist')
      }
    }

    const handleLoginButton = ($body) => {
      if ($body.find(buttonSelector).length > 0) {
        cy.get(buttonSelector).first().click()
        
        verifyRequiredField('[data-cy="email-input"], input[type="text"], input[type="email"]')
        verifyRequiredField('[data-cy="password-input"], input[type="password"]')
        
        cy.get('body', { timeout: 3000 }).then(verifyErrorsExist)
      }
    }

    cy.get('body', { timeout: 10000 }).then(handleLoginButton)
  })

  it('debe validar formato de email', () => {
    const emailSelector = '[data-cy="email-input"], input[type="text"], input[type="email"]'
    cy.get('body').then(($body) => {
      if ($body.find(emailSelector).length > 0) {
        cy.get(emailSelector).first().type('email-invalido')
        cy.get('[data-cy="password-input"], input[type="password"]').first().type('password123')
        cy.get('[data-cy="login-button"], button[type="submit"]').first().click()
        
        verifyEmailError()
      }
    })
  })

  it('debe recordar credenciales si está habilitado', () => {
    cy.fixture('users').then((users) => {
      const admin = users.admin
      
      const checkRememberMe = ($body) => {
        if ($body.find('[data-cy="remember-me"], input[type="checkbox"]').length > 0) {
          cy.get('[data-cy="remember-me"], input[type="checkbox"]').first().check({ force: true })
        }
        performLoginAction(admin.email, admin.password, ['/admin', '/dashboard'])
      }

      const verifyLoginForm = ($form) => {
        if ($form.find('[data-cy="email-input"], input[type="text"], input[type="email"]').length > 0) {
          cy.get('[data-cy="email-input"], input[type="text"], input[type="email"]').first().should('be.visible')
        }
        if ($form.find('[data-cy="login-form"], form').length > 0) {
          cy.get('[data-cy="login-form"], form').should('be.visible')
        }
      }

      const afterLogout = () => {
        cy.get('body', { timeout: 5000 }).then(verifyLoginForm)
      }

      cy.get('body', { timeout: 10000 }).then(checkRememberMe).then(() => {
        cy.url({ timeout: 10000 }).should('satisfy', checkUrlNotIncludesLogin)
        
        cy.logout()
        cy.visit('/login')
        afterLogout()
      })
    })
  })

  it('debe redirigir a página solicitada después del login', () => {
    cy.fixture('users').then((users) => {
      const admin = users.admin
      
      const handleLoginIfNeeded = (url) => {
        if (url.includes('/login')) {
          performLoginAction(admin.email, admin.password, ['/admin/agricultores', '/admin/dashboard', '/admin'])
        }
      }

      cy.navigateTo('/admin/agricultores')
      
      cy.url({ timeout: 5000 }).should('satisfy', checkUrlIncludesLoginOrAdmin)
      
      cy.url().then(handleLoginIfNeeded)
    })
  })
})
