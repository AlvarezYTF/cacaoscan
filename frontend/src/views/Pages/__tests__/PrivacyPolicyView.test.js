import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import PrivacyPolicyView from '../PrivacyPolicyView.vue'

vi.mock('@/components/legal/LegalLayout.vue', () => ({
  default: {
    name: 'LegalLayout',
    template: '<div><slot name="header"></slot><slot name="index"></slot><slot name="content"></slot><slot name="actions"></slot></div>'
  }
}))

describe('PrivacyPolicyView', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should render LegalLayout component', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      const legalLayout = wrapper.findComponent({ name: 'LegalLayout' })
      expect(legalLayout.exists()).toBe(true)
    })

    it('should display policy title in header', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      expect(wrapper.text()).toContain('Política de Privacidad')
    })

    it('should display last update date', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      expect(wrapper.text()).toContain('Octubre 2025')
    })

    it('should display information banner', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      expect(wrapper.text()).toContain('Protección de Datos Personales')
    })

    it('should display content index', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      expect(wrapper.text()).toContain('Índice de Contenido')
    })

    it('should display all section links in index', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      expect(wrapper.text()).toContain('Introducción')
      expect(wrapper.text()).toContain('Información que recopilamos')
      expect(wrapper.text()).toContain('Uso de la información')
      expect(wrapper.text()).toContain('Protección y seguridad')
      expect(wrapper.text()).toContain('Derechos del usuario')
      expect(wrapper.text()).toContain('Cookies y tecnologías')
      expect(wrapper.text()).toContain('Compartición con terceros')
      expect(wrapper.text()).toContain('Modificaciones')
      expect(wrapper.text()).toContain('Contacto')
    })
  })

  describe('Content Sections', () => {
    it('should display introduction section', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      expect(wrapper.text()).toContain('Ley 1581 de 2012')
      expect(wrapper.text()).toContain('Decreto 1377 de 2013')
    })

    it('should display information collection section', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      expect(wrapper.text()).toContain('Información que recopilamos')
    })

    it('should display usage section', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      expect(wrapper.text()).toContain('Cómo utilizamos su información')
    })

    it('should display protection section', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      expect(wrapper.text()).toContain('Protección y seguridad de los datos')
    })

    it('should display user rights section', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      expect(wrapper.text()).toContain('Derechos del usuario')
    })

    it('should display cookies section', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      expect(wrapper.text()).toContain('Cookies y tecnologías similares')
    })

    it('should display third parties section', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      expect(wrapper.text()).toContain('Compartición de datos con terceros')
    })

    it('should display modifications section', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      expect(wrapper.text()).toContain('Modificaciones de la política')
    })

    it('should display contact section', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      expect(wrapper.text()).toContain('Contacto')
    })
  })

  describe('Navigation Links', () => {
    it('should have anchor links for all sections', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      const links = wrapper.findAll('a[href^="#"]')
      expect(links.length).toBeGreaterThan(0)
    })

    it('should have link to introduccion section', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      const link = wrapper.find('a[href="#introduccion"]')
      expect(link.exists()).toBe(true)
    })

    it('should have link to contacto section', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      const link = wrapper.find('a[href="#contacto"]')
      expect(link.exists()).toBe(true)
    })
  })

  describe('Action Buttons', () => {
    it('should render router-link to registration', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { 
              template: '<a><slot></slot></a>',
              props: ['to']
            }
          }
        }
      })

      // Verify the text exists first
      expect(wrapper.text()).toContain('Ir al registro')
      
      // Find all links (router-link stubs render as <a> tags)
      const allLinks = wrapper.findAll('a')
      expect(allLinks.length).toBeGreaterThan(0)
      
      // Find the link that contains "Ir al registro" text
      const registrationLink = allLinks.find(link => 
        link.text().includes('Ir al registro') || link.text().includes('registro')
      )
      expect(registrationLink).toBeTruthy()
      expect(registrationLink.exists()).toBe(true)
    })

    it('should render router-link to home', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { 
              template: '<a><slot></slot></a>',
              props: ['to']
            }
          }
        }
      })

      // Verify the text exists first
      expect(wrapper.text()).toContain('Volver al inicio')
      
      // Since the stub renders as <a> tags, find all links
      const allLinks = wrapper.findAll('a')
      expect(allLinks.length).toBeGreaterThanOrEqual(2)
      
      // Find the link that contains "Volver al inicio" text
      const homeLink = allLinks.find(link => link.text().includes('Volver al inicio'))
      expect(homeLink).toBeTruthy()
      expect(homeLink.exists()).toBe(true)
      
      // Also try to find router-link components if they're available
      const routerLinks = wrapper.findAllComponents({ name: 'router-link' })
      if (routerLinks.length > 0) {
        expect(routerLinks.length).toBeGreaterThanOrEqual(2)
        
        // Find the link with to="/"
        const homeRouterLink = routerLinks.find(link => {
          try {
            const toProp = link.props('to')
            if (typeof toProp === 'string') {
              return toProp === '/'
            }
            if (typeof toProp === 'object' && toProp !== null) {
              return toProp.path === '/' || toProp.name === 'Home'
            }
            return false
          } catch (e) {
            // Log error for debugging but continue
            return false
          }
        })
        
        if (homeRouterLink?.exists()) {
          const toProp = homeRouterLink.props('to')
          const isHomeRoute = typeof toProp === 'string' 
            ? toProp === '/' 
            : (toProp?.path === '/' || toProp?.name === 'Home')
          expect(isHomeRoute).toBe(true)
        }
      }
    })

    it('should display registration button text', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      expect(wrapper.text()).toContain('Ir al registro')
    })

    it('should display home button text', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      expect(wrapper.text()).toContain('Volver al inicio')
    })
  })

  describe('Legal Compliance', () => {
    it('should mention Colombian law 1581', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      expect(wrapper.text()).toContain('Ley 1581 de 2012')
    })

    it('should mention Colombian decree 1377', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      expect(wrapper.text()).toContain('Decreto 1377 de 2013')
    })

    it('should mention SENA Guaviare in contact section', () => {
      wrapper = mount(PrivacyPolicyView, {
        global: {
          stubs: {
            'router-link': { template: '<a><slot></slot></a>', props: ['to'] }
          }
        }
      })

      expect(wrapper.text()).toContain('SENA Guaviare')
    })
  })
})

