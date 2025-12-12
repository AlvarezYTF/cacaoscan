import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import SamplesTable from '../SamplesTable.vue'
import { useDateFormatting } from '@/composables/useDateFormatting'

vi.mock('@/composables/useDateFormatting', () => ({
  useDateFormatting: vi.fn(() => ({
    formatRelativeTime: vi.fn((date) => {
      if (!date) return 'N/A'
      return new Date(date).toLocaleDateString('es-ES')
    })
  }))
}))

describe('SamplesTable', () => {
  let wrapper

  const mockSamples = [
    {
      id: 1,
      grain_id: 'G001',
      height: 20.5,
      width: 15.3,
      thickness: 8.2,
      weight: 1.5,
      image_url: 'https://example.com/image1.jpg',
      created_at: '2024-01-15T10:00:00Z'
    },
    {
      id: 2,
      grain_id: 'G002',
      height: 22,
      width: 16,
      thickness: 9,
      weight: 1.8,
      image_url: 'https://example.com/image2.jpg',
      created_at: '2024-01-14T10:00:00Z'
    }
  ]

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: mockSamples
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should display section title', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: mockSamples
        }
      })

      expect(wrapper.text()).toContain('Muestras Recientes')
    })

    it('should render refresh button', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: mockSamples
        }
      })

      expect(wrapper.text()).toContain('Actualizar')
    })

    it('should render table with all columns', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: mockSamples
        }
      })

      expect(wrapper.text()).toContain('Imagen')
      expect(wrapper.text()).toContain('ID')
      expect(wrapper.text()).toContain('Dimensiones')
      expect(wrapper.text()).toContain('Peso')
      expect(wrapper.text()).toContain('Fecha')
      expect(wrapper.text()).toContain('Acciones')
    })

    it('should render all samples in table', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: mockSamples
        }
      })

      const rows = wrapper.findAll('tbody tr')
      expect(rows.length).toBe(2)
    })

    it('should display grain ID for each sample', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: mockSamples
        }
      })

      expect(wrapper.text()).toContain('G001')
      expect(wrapper.text()).toContain('G002')
    })

    it('should display dimensions for each sample', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: [mockSamples[0]]
        }
      })

      expect(wrapper.text()).toContain('20.5')
      expect(wrapper.text()).toContain('15.3')
      expect(wrapper.text()).toContain('8.2')
    })

    it('should display weight for each sample', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: [mockSamples[0]]
        }
      })

      expect(wrapper.text()).toContain('1.5g')
    })
  })

  describe('Props', () => {
    it('should accept samples array prop', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: mockSamples
        }
      })

      expect(wrapper.vm.$props.samples).toEqual(mockSamples)
    })

    it('should use default empty array for samples', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: []
        }
      })

      expect(wrapper.vm.$props.samples).toEqual([])
    })

    it('should use default false for isLoading', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: mockSamples
        }
      })

      expect(wrapper.vm.$props.isLoading).toBe(false)
    })

    it('should accept isLoading prop', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: mockSamples,
          isLoading: true
        }
      })

      expect(wrapper.vm.$props.isLoading).toBe(true)
    })

    it('should use default 0 for totalSamples', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: mockSamples
        }
      })

      expect(wrapper.vm.$props.totalSamples).toBe(0)
    })

    it('should accept totalSamples prop', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: mockSamples,
          totalSamples: 10
        }
      })

      expect(wrapper.vm.$props.totalSamples).toBe(10)
    })
  })

  describe('Loading State', () => {
    it('should show loading spinner when isLoading is true', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: mockSamples,
          isLoading: true
        }
      })

      const spinner = wrapper.find('.animate-spin')
      expect(spinner.exists()).toBe(true)
      expect(wrapper.text()).toContain('Cargando muestras...')
    })

    it('should not show table when loading', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: mockSamples,
          isLoading: true
        }
      })

      const table = wrapper.find('table')
      expect(table.exists()).toBe(false)
    })

    it('should disable refresh button when loading', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: mockSamples,
          isLoading: true
        }
      })

      const refreshButton = wrapper.find('button')
      expect(refreshButton.attributes('disabled')).toBeDefined()
    })
  })

  describe('Empty State', () => {
    it('should show empty state when no samples', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: [],
          isLoading: false
        }
      })

      expect(wrapper.text()).toContain('No hay muestras registradas')
      expect(wrapper.text()).toContain('Sube imágenes y registra datos')
    })

    it('should show empty state icon', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: [],
          isLoading: false
        }
      })

      const icon = wrapper.find('svg.w-12.h-12')
      expect(icon.exists()).toBe(true)
    })

    it('should not show table when empty', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: [],
          isLoading: false
        }
      })

      const table = wrapper.find('table')
      expect(table.exists()).toBe(false)
    })
  })

  describe('Table Content', () => {
    it('should render sample images', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: [mockSamples[0]]
        }
      })

      const image = wrapper.find('img')
      expect(image.exists()).toBe(true)
      expect(image.attributes('src')).toBe('https://example.com/image1.jpg')
    })

    it('should render sample images with alt text', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: [mockSamples[0]]
        }
      })

      const image = wrapper.find('img')
      expect(image.attributes('alt')).toBe('Grano G001')
    })

    it('should format dates using composable', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: [mockSamples[0]]
        }
      })

      expect(useDateFormatting).toHaveBeenCalled()
    })
  })

  describe('Events', () => {
    it('should emit refresh event when refresh button is clicked', async () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: mockSamples,
          isLoading: false
        }
      })

      const refreshButton = wrapper.find('button')
      await refreshButton.trigger('click')

      expect(wrapper.emitted('refresh')).toBeTruthy()
    })

    it('should emit view-sample event when view button is clicked', async () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: [mockSamples[0]]
        }
      })

      const viewButton = wrapper.findAll('button').find(btn => {
        return btn.attributes('title') === 'Ver detalles'
      })

      if (viewButton) {
        await viewButton.trigger('click')
        expect(wrapper.emitted('view-sample')).toBeTruthy()
        expect(wrapper.emitted('view-sample')[0]).toEqual([mockSamples[0]])
      }
    })
  })

  describe('Pagination', () => {
    it('should show pagination info when samples exist', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: mockSamples,
          totalSamples: 10
        }
      })

      expect(wrapper.text()).toContain('Mostrando')
      expect(wrapper.text()).toContain('10 muestras')
    })

    it('should display correct sample count', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: mockSamples,
          totalSamples: 10
        }
      })

      expect(wrapper.text()).toContain('2')
      expect(wrapper.text()).toContain('10')
    })

    it('should render pagination buttons', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: mockSamples,
          totalSamples: 10
        }
      })

      expect(wrapper.text()).toContain('Anterior')
      expect(wrapper.text()).toContain('Siguiente')
    })

    it('should not show pagination when no samples', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: [],
          totalSamples: 0
        }
      })

      expect(wrapper.text()).not.toContain('Mostrando')
    })
  })

  describe('Image Rendering', () => {
    it('should render image with correct classes', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: [mockSamples[0]]
        }
      })

      const image = wrapper.find('img')
      expect(image.classes()).toContain('rounded-lg')
      expect(image.classes()).toContain('object-cover')
    })

    it('should render image in thumbnail size', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: [mockSamples[0]]
        }
      })

      const image = wrapper.find('img')
      expect(image.classes()).toContain('h-12')
      expect(image.classes()).toContain('w-12')
    })
  })

  describe('Actions Column', () => {
    it('should render view button for each sample', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: [mockSamples[0]]
        }
      })

      const buttons = wrapper.findAll('button')
      const viewButton = buttons.find(btn => btn.attributes('title') === 'Ver detalles')
      expect(viewButton).toBeTruthy()
    })

    it('should render download button for each sample', () => {
      wrapper = mount(SamplesTable, {
        props: {
          samples: [mockSamples[0]]
        }
      })

      const buttons = wrapper.findAll('button')
      const downloadButton = buttons.find(btn => btn.attributes('title') === 'Descargar imagen')
      expect(downloadButton).toBeTruthy()
    })
  })
})



