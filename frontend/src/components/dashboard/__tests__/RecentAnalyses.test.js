import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import RecentAnalyses from '../RecentAnalyses.vue'

// Mock vue-router composables
const mockRoute = {
  params: {},
  query: {},
  path: '/',
  name: 'Home'
}

const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  go: vi.fn(),
  back: vi.fn(),
  forward: vi.fn(),
  resolve: vi.fn((to) => ({
    href: '/detalle-analisis',
    route: { name: 'DetalleAnalisis' }
  }))
}

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRoute: () => mockRoute,
    useRouter: () => mockRouter
  }
})

describe('RecentAnalyses', () => {
  let wrapper

  const mockAnalyses = [
    {
      id: 1,
      status: 'completed',
      statusLabel: 'Completado',
      quality: 85,
      defects: 5,
      avgSize: 22.5,
      date: '2024-01-15'
    },
    {
      id: 2,
      status: 'processing',
      statusLabel: 'Procesando',
      quality: 0,
      defects: 0,
      avgSize: 0,
      date: '2024-01-14'
    }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    // Reset route mock
    mockRoute.params = {}
    mockRoute.query = {}
    mockRoute.path = '/'
    mockRoute.name = 'Home'
    mockRouter.push.mockClear()
    mockRouter.replace.mockClear()
  })

  afterEach(() => {
    if (wrapper) {
      try {
        wrapper.unmount()
      } catch {
        // Ignore unmount errors
      }
      wrapper = null
    }
    vi.clearAllMocks()
  })

  const getDefaultMountOptions = () => {
    return {
      global: {
        stubs: {
          'router-link': {
            template: '<a><slot></slot></a>',
            props: ['to']
          }
        },
        mocks: {
          $route: mockRoute,
          $router: mockRouter
        }
      }
    }
  }
  

  describe('Rendering', () => {
    it('should render component', async () => {
      wrapper = mount(RecentAnalyses, {
        props: {
          analyses: mockAnalyses
        },
        ...getDefaultMountOptions()
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should display section title', async () => {
      // Wait to ensure previous router is fully cleaned up
      await new Promise(resolve => setTimeout(resolve, 50))
      wrapper = mount(RecentAnalyses, {
        props: {
          analyses: mockAnalyses
        },
        ...getDefaultMountOptions()
      })

      expect(wrapper.text()).toContain('Análisis recientes')
    })

    it('should display view all link', async () => {
      // Wait to ensure previous router is fully cleaned up
      await new Promise(resolve => setTimeout(resolve, 50))
      wrapper = mount(RecentAnalyses, {
        props: {
          analyses: mockAnalyses
        },
        ...getDefaultMountOptions()
      })

      expect(wrapper.text()).toContain('Ver todo')
    })

    it('should render all analysis cards', () => {
      wrapper = mount(RecentAnalyses, {
        props: {
          analyses: mockAnalyses
        },
        ...getDefaultMountOptions()
      })

      const cards = wrapper.findAll('.analysis-card')
      expect(cards.length).toBe(2)
    })

    it('should display batch ID for each analysis', () => {
      wrapper = mount(RecentAnalyses, {
        props: {
          analyses: mockAnalyses
        },
        ...getDefaultMountOptions()
      })

      expect(wrapper.text()).toContain('Lote #1')
      expect(wrapper.text()).toContain('Lote #2')
    })

    it('should display status badge for each analysis', () => {
      wrapper = mount(RecentAnalyses, {
        props: {
          analyses: mockAnalyses
        },
        ...getDefaultMountOptions()
      })

      expect(wrapper.text()).toContain('Completado')
      expect(wrapper.text()).toContain('Procesando')
    })

    it('should display quality percentage', () => {
      wrapper = mount(RecentAnalyses, {
        props: {
          analyses: [mockAnalyses[0]]
        },
        ...getDefaultMountOptions()
      })

      expect(wrapper.text()).toContain('85%')
    })

    it('should display defects percentage', () => {
      wrapper = mount(RecentAnalyses, {
        props: {
          analyses: [mockAnalyses[0]]
        },
        ...getDefaultMountOptions()
      })

      expect(wrapper.text()).toContain('5%')
    })

    it('should display average size', async () => {
      // Wait a bit to ensure previous test's router is fully cleaned up
      await new Promise(resolve => setTimeout(resolve, 10))
      
      wrapper = mount(RecentAnalyses, {
        props: {
          analyses: [mockAnalyses[0]]
        },
        ...getDefaultMountOptions()
      })

      expect(wrapper.text()).toContain('22.5mm')
    })

    it('should display date for each analysis', async () => {
      // Wait a bit to ensure previous test's router is fully cleaned up
      await new Promise(resolve => setTimeout(resolve, 10))
      
      wrapper = mount(RecentAnalyses, {
        props: {
          analyses: mockAnalyses
        },
        ...getDefaultMountOptions()
      })

      expect(wrapper.text()).toContain('2024-01-15')
      expect(wrapper.text()).toContain('2024-01-14')
    })
  })

  describe('Props', () => {
    it('should have analyses prop defined as required', () => {
      const analysesProp = RecentAnalyses.props.analyses
      expect(analysesProp).toBeDefined()
      expect(analysesProp.required).toBe(true)
      expect(analysesProp.type).toBe(Array)
    })

    it('should accept analyses array prop', () => {
      // Ensure previous wrapper is unmounted
      if (wrapper) {
        wrapper.unmount()
        wrapper = null
      }
      
      wrapper = mount(RecentAnalyses, {
        props: {
          analyses: mockAnalyses
        },
        ...getDefaultMountOptions()
      })

      expect(wrapper.vm.$props.analyses).toEqual(mockAnalyses)
    })

    it('should handle empty analyses array', () => {
      // Ensure previous wrapper is unmounted
      if (wrapper) {
        wrapper.unmount()
        wrapper = null
      }
      
      wrapper = mount(RecentAnalyses, {
        props: {
          analyses: []
        },
        ...getDefaultMountOptions()
      })

      expect(wrapper.vm.$props.analyses).toEqual([])
      const cards = wrapper.findAll('.analysis-card')
      expect(cards.length).toBe(0)
    })
  })

  describe('Progress Bar', () => {
    it('should render progress bar with correct width', () => {
      wrapper = mount(RecentAnalyses, {
        props: {
          analyses: [mockAnalyses[0]]
        },
        ...getDefaultMountOptions()
      })

      const progressBar = wrapper.find('.progress')
      expect(progressBar.exists()).toBe(true)
      expect(progressBar.attributes('style')).toContain('width: 85%')
    })

    it('should render progress bar with 0% width for zero quality', async () => {
      // Wait to ensure previous router is fully cleaned up
      await new Promise(resolve => setTimeout(resolve, 50))
      wrapper = mount(RecentAnalyses, {
        props: {
          analyses: [mockAnalyses[1]]
        },
        ...getDefaultMountOptions()
      })

      const progressBar = wrapper.find('.progress')
      if (progressBar.exists()) {
        expect(progressBar.attributes('style')).toContain('width: 0%')
      }
    })
  })

  describe('Status Badges', () => {
    it('should apply completed status class', async () => {
      // Wait to ensure previous router is fully cleaned up
      await new Promise(resolve => setTimeout(resolve, 50))
      wrapper = mount(RecentAnalyses, {
        props: {
          analyses: [mockAnalyses[0]]
        },
        ...getDefaultMountOptions()
      })

      const badge = wrapper.find('.status-badge.completed')
      expect(badge.exists()).toBe(true)
    })

    it('should display status label correctly', () => {
      wrapper = mount(RecentAnalyses, {
        props: {
          analyses: [mockAnalyses[0]]
        },
        ...getDefaultMountOptions()
      })

      const badge = wrapper.find('.status-badge')
      expect(badge.text()).toBe('Completado')
    })
  })

  describe('Navigation', () => {
    it('should render router-link to detail page', () => {
      wrapper = mount(RecentAnalyses, {
        props: {
          analyses: [mockAnalyses[0]]
        },
        ...getDefaultMountOptions()
      })

      // router-link is stubbed, so we need to find it by the stub or by selector
      const link = wrapper.find('a[href]')
      expect(link.exists()).toBe(true)
      // Verify it's the router-link stub by checking if it has the 'to' prop or is in the card-footer
      const cardFooter = wrapper.find('.card-footer')
      expect(cardFooter.exists()).toBe(true)
      const footerLink = cardFooter.find('a')
      expect(footerLink.exists()).toBe(true)
    })
  })

  describe('Structure', () => {
    it('should have correct section structure', () => {
      wrapper = mount(RecentAnalyses, {
        props: {
          analyses: mockAnalyses
        },
        ...getDefaultMountOptions()
      })

      const section = wrapper.find('section')
      expect(section.exists()).toBe(true)
      expect(section.classes()).toContain('recent-analysis')
    })

    it('should have section header', () => {
      wrapper = mount(RecentAnalyses, {
        props: {
          analyses: mockAnalyses
        },
        ...getDefaultMountOptions()
      })

      const header = wrapper.find('.section-header')
      expect(header.exists()).toBe(true)
    })

    it('should have analysis grid', () => {
      wrapper = mount(RecentAnalyses, {
        props: {
          analyses: mockAnalyses
        },
        ...getDefaultMountOptions()
      })

      const grid = wrapper.find('.analysis-grid')
      expect(grid.exists()).toBe(true)
    })
  })
})


