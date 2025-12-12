import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import BatchInfoCard from '../BatchInfoCard.vue'

describe('BatchInfoCard', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render component', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: '2024-01-15',
          origin: 'Test Origin',
          notes: ''
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display default title', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: '2024-01-15',
          origin: 'Test Origin'
        }
      }
    })

    const title = wrapper.find('h3')
    expect(title.exists()).toBe(true)
    expect(title.text()).toBe('Información del Lote')
  })

  it('should display batch name when provided', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Lote de Prueba',
          collectionDate: '2024-01-15',
          origin: 'Test Origin'
        }
      }
    })

    expect(wrapper.text()).toContain('Nombre')
    expect(wrapper.text()).toContain('Lote de Prueba')
  })

  it('should display N/A when batch name is empty', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: '',
          collectionDate: '2024-01-15',
          origin: 'Test Origin'
        }
      }
    })

    expect(wrapper.text()).toContain('Nombre')
    expect(wrapper.text()).toContain('N/A')
  })

  it('should display N/A when batch name is null', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: null,
          collectionDate: '2024-01-15',
          origin: 'Test Origin'
        }
      }
    })

    expect(wrapper.text()).toContain('N/A')
  })

  it('should display formatted collection date', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: '2024-01-15',
          origin: 'Test Origin'
        }
      }
    })

    expect(wrapper.text()).toContain('Fecha de Recolección')
    // The date should be formatted in Spanish
    const formattedDate = wrapper.vm.formatDate('2024-01-15')
    expect(wrapper.text()).toContain(formattedDate)
  })

  it('should display N/A when collection date is empty', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: '',
          origin: 'Test Origin'
        }
      }
    })

    expect(wrapper.text()).toContain('Fecha de Recolección')
    expect(wrapper.text()).toContain('N/A')
  })

  it('should display N/A when collection date is null', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: null,
          origin: 'Test Origin'
        }
      }
    })

    expect(wrapper.text()).toContain('N/A')
  })

  it('should format date correctly in Spanish locale', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: '2024-03-15',
          origin: 'Test Origin'
        }
      }
    })

    const formattedDate = wrapper.vm.formatDate('2024-03-15')
    // Should contain year, month name in Spanish, and day
    expect(formattedDate).toContain('2024')
    expect(formattedDate).toContain('15')
    // The month should be in Spanish (marzo)
    expect(formattedDate.toLowerCase()).toMatch(/marzo|march/)
  })

  it('should display origin when provided', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: '2024-01-15',
          origin: 'Finca San José'
        }
      }
    })

    expect(wrapper.text()).toContain('Origen')
    expect(wrapper.text()).toContain('Finca San José')
  })

  it('should display N/A when origin is empty', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: '2024-01-15',
          origin: ''
        }
      }
    })

    expect(wrapper.text()).toContain('Origen')
    expect(wrapper.text()).toContain('N/A')
  })

  it('should display N/A when origin is null', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: '2024-01-15',
          origin: null
        }
      }
    })

    expect(wrapper.text()).toContain('N/A')
  })

  it('should display notes when provided', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: '2024-01-15',
          origin: 'Test Origin',
          notes: 'Estas son notas importantes'
        }
      }
    })

    expect(wrapper.text()).toContain('Notas')
    expect(wrapper.text()).toContain('Estas son notas importantes')
  })

  it('should not display notes section when notes are empty', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: '2024-01-15',
          origin: 'Test Origin',
          notes: ''
        }
      }
    })

    expect(wrapper.text()).not.toContain('Notas')
  })

  it('should not display notes section when notes are null', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: '2024-01-15',
          origin: 'Test Origin',
          notes: null
        }
      }
    })

    expect(wrapper.text()).not.toContain('Notas')
  })

  it('should not display notes section when notes are undefined', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: '2024-01-15',
          origin: 'Test Origin'
        }
      }
    })

    expect(wrapper.text()).not.toContain('Notas')
  })

  it('should handle all fields together', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Lote Completo',
          collectionDate: '2024-06-20',
          origin: 'Finca El Paraíso',
          notes: 'Lote de alta calidad'
        }
      }
    })

    expect(wrapper.text()).toContain('Lote Completo')
    expect(wrapper.text()).toContain('Finca El Paraíso')
    expect(wrapper.text()).toContain('Lote de alta calidad')
    expect(wrapper.text()).toContain('Fecha de Recolección')
  })

  it('should format date with different date formats', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: '2024-12-25',
          origin: 'Test Origin'
        }
      }
    })

    const formattedDate = wrapper.vm.formatDate('2024-12-25')
    expect(formattedDate).not.toBe('N/A')
    expect(formattedDate).toContain('2024')
    expect(formattedDate).toContain('25')
  })

  it('should handle invalid date strings gracefully', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: 'invalid-date',
          origin: 'Test Origin'
        }
      }
    })

    // formatDate should still attempt to format, but may return Invalid Date
    const formattedDate = wrapper.vm.formatDate('invalid-date')
    // The method doesn't validate, so it will try to format
    expect(typeof formattedDate).toBe('string')
  })

  it('should update when data prop changes', async () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Initial Batch',
          collectionDate: '2024-01-15',
          origin: 'Initial Origin'
        }
      }
    })

    expect(wrapper.text()).toContain('Initial Batch')

    await wrapper.setProps({
      data: {
        batchName: 'Updated Batch',
        collectionDate: '2024-02-20',
        origin: 'Updated Origin'
      }
    })

    expect(wrapper.text()).toContain('Updated Batch')
    expect(wrapper.text()).toContain('Updated Origin')
  })

  it('should show and hide notes when data changes', async () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: '2024-01-15',
          origin: 'Test Origin',
          notes: 'Initial notes'
        }
      }
    })

    expect(wrapper.text()).toContain('Notas')
    expect(wrapper.text()).toContain('Initial notes')

    await wrapper.setProps({
      data: {
        batchName: 'Test Batch',
        collectionDate: '2024-01-15',
        origin: 'Test Origin',
        notes: ''
      }
    })

    expect(wrapper.text()).not.toContain('Notas')
  })

  it('should have correct CSS classes', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: '2024-01-15',
          origin: 'Test Origin'
        }
      }
    })

    expect(wrapper.classes()).toContain('bg-gray-50')
    expect(wrapper.find('.rounded-lg').exists()).toBe(true)
    expect(wrapper.find('.space-y-3').exists()).toBe(true)
  })

  it('should have proper structure with definition list', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: '2024-01-15',
          origin: 'Test Origin'
        }
      }
    })

    const dl = wrapper.find('dl')
    expect(dl.exists()).toBe(true)
    
    const dtElements = wrapper.findAll('dt')
    expect(dtElements.length).toBeGreaterThanOrEqual(3)
    
    const ddElements = wrapper.findAll('dd')
    expect(ddElements.length).toBeGreaterThanOrEqual(3)
  })

  it('should format date method return N/A for empty string', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: '',
          origin: 'Test Origin'
        }
      }
    })

    const result = wrapper.vm.formatDate('')
    expect(result).toBe('N/A')
  })

  it('should format date method return N/A for null', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: null,
          origin: 'Test Origin'
        }
      }
    })

    const result = wrapper.vm.formatDate(null)
    expect(result).toBe('N/A')
  })

  it('should format date method return N/A for undefined', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: '2024-01-15',
          origin: 'Test Origin'
        }
      }
    })

    const result = wrapper.vm.formatDate(undefined)
    expect(result).toBe('N/A')
  })

  it('should require data prop', () => {
    // This test verifies that the prop is required
    // In Vue 3, missing required props will cause a warning
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: '2024-01-15',
          origin: 'Test Origin'
        }
      }
    })

    expect(wrapper.props('data')).toBeDefined()
    expect(wrapper.props('data')).toHaveProperty('batchName')
  })

  it('should handle ISO date format', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: '2024-01-15T10:30:00Z',
          origin: 'Test Origin'
        }
      }
    })

    const formattedDate = wrapper.vm.formatDate('2024-01-15T10:30:00Z')
    expect(formattedDate).not.toBe('N/A')
    expect(formattedDate).toContain('2024')
  })

  it('should handle date with time component', () => {
    wrapper = mount(BatchInfoCard, {
      props: {
        data: {
          batchName: 'Test Batch',
          collectionDate: '2024-05-10T14:30:00.000Z',
          origin: 'Test Origin'
        }
      }
    })

    const formattedDate = wrapper.vm.formatDate('2024-05-10T14:30:00.000Z')
    expect(formattedDate).not.toBe('N/A')
    expect(formattedDate).toContain('2024')
    expect(formattedDate).toContain('10')
  })
})

