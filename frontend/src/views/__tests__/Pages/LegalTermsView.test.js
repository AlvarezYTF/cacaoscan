import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import LegalTermsView from '@/views/Pages/LegalTermsView.vue'

// Mock LegalLayout component
vi.mock('@/components/legal/LegalLayout.vue', () => ({
  default: {
    name: 'LegalLayout',
    template: `
      <div class="legal-layout">
        <slot name="header"></slot>
        <slot name="index"></slot>
        <slot name="content"></slot>
        <slot name="actions"></slot>
      </div>
    `
  }
}))

// Mock router-link
const mockRouterLink = {
  name: 'RouterLink',
  template: '<a><slot /></a>',
  props: ['to']
}

describe('LegalTermsView', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should render LegalLayout component', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      const legalLayout = wrapper.findComponent({ name: 'LegalLayout' })
      expect(legalLayout.exists()).toBe(true)
    })
  })

  describe('Header Section', () => {
    it('should render title in header slot', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Términos y Condiciones')
    })

    it('should render last update date', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Última actualización: Octubre 2025')
    })
  })

  describe('Index Section', () => {
    it('should render index navigation', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Índice de Contenido')
    })

    it('should render all index links', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      const indexLinks = [
        'Introducción',
        'Aceptación de los términos',
        'Descripción del servicio',
        'Registro y cuenta de usuario',
        'Uso permitido y restricciones',
        'Propiedad intelectual',
        'Limitación de responsabilidad',
        'Privacidad y protección de datos',
        'Modificaciones de los términos',
        'Legislación aplicable'
      ]

      for (const link of indexLinks) {
        expect(wrapper.text()).toContain(link)
      }
    })
  })

  describe('Content Sections', () => {
    it('should render introduction section', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('CacaoScan es una plataforma desarrollada por aprendices del SENA')
    })

    it('should render section 1: Acceptation', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Aceptación de los términos')
    })

    it('should render section 2: Service Description', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Descripción del servicio CacaoScan')
    })

    it('should render section 3: Registration', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Registro y cuenta de usuario')
    })

    it('should render section 4: Usage', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Uso permitido y restricciones')
    })

    it('should render section 5: Intellectual Property', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Propiedad intelectual')
    })

    it('should render section 6: Liability', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Limitación de responsabilidad')
    })

    it('should render section 7: Privacy', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Privacidad y protección de datos')
    })

    it('should render section 8: Modifications', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Modificaciones de los términos')
    })

    it('should render section 9: Legislation', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Legislación aplicable y jurisdicción')
    })
  })

  describe('Service Description Details', () => {
    it('should list service features', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Subir y gestionar imágenes')
      expect(wrapper.text()).toContain('Realizar análisis precisos de dimensiones')
      expect(wrapper.text()).toContain('Calcular el peso estimado')
    })
  })

  describe('Actions Section', () => {
    it('should render accept and continue button', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Aceptar y continuar al registro')
    })

    it('should render back to home button', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Volver al inicio')
    })

    it('should have router links in actions', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      const routerLinks = wrapper.findAllComponents(mockRouterLink)
      expect(routerLinks.length).toBeGreaterThan(0)
    })
  })

  describe('Navigation Anchors', () => {
    it('should have anchor IDs for navigation', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      const anchors = [
        'inicio',
        'introduccion',
        'aceptacion',
        'descripcion',
        'registro',
        'uso',
        'propiedad',
        'responsabilidad',
        'privacidad',
        'modificaciones',
        'legislacion'
      ]

      const html = wrapper.html()
      for (const anchor of anchors) {
        expect(html).toContain(`id="${anchor}"`)
      }
    })
  })

  describe('Content Structure', () => {
    it('should have numbered sections', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('1')
      expect(wrapper.text()).toContain('2')
      expect(wrapper.text()).toContain('9')
    })

    it('should have section separators', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      const html = wrapper.html()
      const hrElements = html.match(/<hr/g)
      expect(hrElements?.length).toBeGreaterThan(0)
    })
  })

  describe('Privacy Policy Link', () => {
    it('should contain link to privacy policy', () => {
      wrapper = mount(LegalTermsView, {
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Política de Privacidad')
    })
  })
})



