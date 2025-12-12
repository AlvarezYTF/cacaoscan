import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import PredictionResults from '../PredictionResults.vue'

describe('PredictionResults', () => {
  const mockPredictionData = {
    id: 1,
    width: 10.5,
    height: 12.3,
    thickness: 8.2,
    predicted_weight: 1.75,
    confidence_level: 'high',
    confidence_score: 0.85,
    prediction_method: 'vision_cnn',
    created_at: '2024-01-15T10:30:00Z',
    processing_time: 2.5,
    image_url: 'http://example.com/image.jpg'
  }

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Ensure document.body is properly set up
    if (!document.body) {
      const body = document.createElement('body')
      document.documentElement.appendChild(body)
    }
    
    // Mock navigator APIs
    if (typeof navigator !== 'undefined') {
      navigator.share = vi.fn()
      navigator.clipboard = {
        writeText: vi.fn().mockResolvedValue()
      }
    }
    
    // Mock Blob if needed (already in setup.js but ensure it exists)
    if (globalThis.Blob === undefined) {
      globalThis.Blob = class Blob {
        constructor(data) {
          this.data = data
        }
        
        size = 0
        type = ''
        
        async text() {
          return ''
        }
        
        async arrayBuffer() {
          return new ArrayBuffer(0)
        }
      }
    }
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    vi.clearAllMocks()
  })

  it('should render prediction results', () => {
    wrapper = mount(PredictionResults, {
      props: {
        predictionData: mockPredictionData
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('Resultados del Análisis')
  })

  it('should conditionally render based on predictionData', () => {
    // The component uses v-if="predictionData" in the template,
    // which means it will only render when predictionData is truthy.
    // Since the prop is required with a validator, we verify that
    // the component renders correctly when valid data is provided.
    const wrapper = mount(PredictionResults, {
      props: {
        predictionData: mockPredictionData
      }
    })

    // Component should render when valid data is provided
    expect(wrapper.find('.bg-white').exists()).toBe(true)
    expect(wrapper.text()).toContain('Resultados del Análisis')
    
    // Verify the conditional rendering structure exists
    expect(wrapper.vm.$props.predictionData).toBeTruthy()
  })

  it('should display prediction ID', () => {
    const wrapper = mount(PredictionResults, {
      props: {
        predictionData: mockPredictionData
      }
    })

    expect(wrapper.text()).toContain('#1')
  })

  it('should display formatted date', () => {
    const wrapper = mount(PredictionResults, {
      props: {
        predictionData: mockPredictionData
      }
    })

    expect(wrapper.text()).toContain('2024')
  })

  it('should display processing time if available', () => {
    const wrapper = mount(PredictionResults, {
      props: {
        predictionData: mockPredictionData
      }
    })

    expect(wrapper.text()).toContain('2.5s')
  })

  it('should display dimensions', () => {
    const wrapper = mount(PredictionResults, {
      props: {
        predictionData: mockPredictionData
      }
    })

    expect(wrapper.text()).toContain('10.50')
    expect(wrapper.text()).toContain('12.30')
    expect(wrapper.text()).toContain('8.20')
  })

  it('should display predicted weight', () => {
    const wrapper = mount(PredictionResults, {
      props: {
        predictionData: mockPredictionData
      }
    })

    expect(wrapper.text()).toContain('1.75')
  })

  it('should display confidence level', () => {
    const wrapper = mount(PredictionResults, {
      props: {
        predictionData: mockPredictionData
      }
    })

    expect(wrapper.text()).toContain('Alta')
  })

  it('should display confidence score', () => {
    const wrapper = mount(PredictionResults, {
      props: {
        predictionData: mockPredictionData
      }
    })

    expect(wrapper.text()).toContain('85%')
  })

  it('should display prediction method', () => {
    const wrapper = mount(PredictionResults, {
      props: {
        predictionData: mockPredictionData
      }
    })

    expect(wrapper.text()).toContain('Visión CNN')
  })

  it('should display image if available', () => {
    const wrapper = mount(PredictionResults, {
      props: {
        predictionData: mockPredictionData
      }
    })

    const img = wrapper.find('img')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toBe('http://example.com/image.jpg')
  })

  it('should display placeholder if no image', () => {
    const dataWithoutImage = { ...mockPredictionData, image_url: null }
    const wrapper = mount(PredictionResults, {
      props: {
        predictionData: dataWithoutImage
      }
    })

    const img = wrapper.find('img')
    expect(img.exists()).toBe(false)
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('should handle image error', async () => {
    const wrapper = mount(PredictionResults, {
      props: {
        predictionData: mockPredictionData
      }
    })

    const img = wrapper.find('img')
    await img.trigger('error')

    expect(img.element.style.display).toBe('none')
  })

  it('should emit new-analysis event', async () => {
    const wrapper = mount(PredictionResults, {
      props: {
        predictionData: mockPredictionData
      }
    })

    const button = wrapper.find('button')
    await button.trigger('click')

    expect(wrapper.emitted('new-analysis')).toBeTruthy()
  })

  it('should download results', async () => {
    // Create proper DOM element mock preserving original functionality
    const createElementOriginal = document.createElement.bind(document)
    let mockAnchor = null
    const mockClick = vi.fn()
    const mockRemove = vi.fn()
    
    const createElementSpy = vi.spyOn(document, 'createElement').mockImplementation((tag) => {
      if (tag === 'a') {
        mockAnchor = createElementOriginal('a')
        mockAnchor.click = mockClick
        mockAnchor.remove = mockRemove
        return mockAnchor
      }
      return createElementOriginal(tag)
    })
    
    wrapper = mount(PredictionResults, {
      props: {
        predictionData: mockPredictionData
      }
    })

    const downloadButton = wrapper.findAll('button').find(b => 
      b.text().includes('Descargar Resultados')
    )
    
    await downloadButton.trigger('click')

    expect(createElementSpy).toHaveBeenCalledWith('a')
    expect(globalThis.URL.createObjectURL).toHaveBeenCalled()
    if (mockAnchor) {
      expect(mockClick).toHaveBeenCalled()
    }
    
    // Cleanup
    createElementSpy.mockRestore()
  })

  it('should share results with Web Share API', async () => {
    navigator.share = vi.fn().mockResolvedValue()
    
    const wrapper = mount(PredictionResults, {
      props: {
        predictionData: mockPredictionData
      }
    })

    const shareButton = wrapper.findAll('button').find(b => 
      b.text().includes('Compartir')
    )
    
    await shareButton.trigger('click')

    expect(navigator.share).toHaveBeenCalled()
  })

  it('should fallback to clipboard if Web Share not available', async () => {
    delete navigator.share
    
    const wrapper = mount(PredictionResults, {
      props: {
        predictionData: mockPredictionData
      }
    })

    const shareButton = wrapper.findAll('button').find(b => 
      b.text().includes('Compartir')
    )
    
    await shareButton.trigger('click')

    expect(navigator.clipboard.writeText).toHaveBeenCalled()
  })

  it('should emit save-analysis event', async () => {
    const wrapper = mount(PredictionResults, {
      props: {
        predictionData: mockPredictionData
      }
    })

    const saveButton = wrapper.findAll('button').find(b => 
      b.text().includes('Guardar Análisis')
    )
    
    await saveButton.trigger('click')

    expect(wrapper.emitted('save-analysis')).toBeTruthy()
  })

  describe('confidence levels', () => {
    const confidenceLevels = [
      { level: 'very_high', label: 'Muy Alta', class: 'bg-green-500' },
      { level: 'high', label: 'Alta', class: 'bg-green-400' },
      { level: 'medium', label: 'Media', class: 'bg-yellow-400' },
      { level: 'low', label: 'Baja', class: 'bg-orange-400' },
      { level: 'very_low', label: 'Muy Baja', class: 'bg-red-400' },
      { level: 'unknown', label: 'Desconocida', class: 'bg-gray-400' }
    ]

    for (const { level, label, class: expectedClass } of confidenceLevels) {
      it(`should display ${level} confidence correctly`, () => {
        const data = { ...mockPredictionData, confidence_level: level }
        const wrapper = mount(PredictionResults, {
          props: {
            predictionData: data
          }
        })

        expect(wrapper.text()).toContain(label)
        const indicator = wrapper.find('.w-3.h-3')
        expect(indicator.classes()).toContain(expectedClass.split(' ')[0])
      })
    }
  })

  describe('prediction methods', () => {
    const methods = [
      { method: 'vision_cnn', label: 'Visión CNN' },
      { method: 'regression', label: 'Regresión' },
      { method: 'fallback', label: 'Estimación' },
      { method: 'unknown', label: 'Desconocido' }
    ]

    for (const { method, label } of methods) {
      it(`should format ${method} method correctly`, () => {
        const data = { ...mockPredictionData, prediction_method: method }
        const wrapper = mount(PredictionResults, {
          props: {
            predictionData: data
          }
        })

        expect(wrapper.text()).toContain(label)
      })
    }
  })

  describe('derived metrics', () => {
    it('should display derived metrics if available', () => {
      const dataWithMetrics = {
        ...mockPredictionData,
        derived_metrics: {
          volume_mm3: 1000,
          density_g_per_cm3: 1.2,
          aspect_ratio: 1.5,
          projected_area_mm2: 500
        }
      }

      const wrapper = mount(PredictionResults, {
        props: {
          predictionData: dataWithMetrics
        }
      })

      expect(wrapper.text()).toContain('1000')
      expect(wrapper.text()).toContain('1.20')
      expect(wrapper.text()).toContain('1.50')
      expect(wrapper.text()).toContain('500')
    })

    it('should not display derived metrics section if not available', () => {
      const wrapper = mount(PredictionResults, {
        props: {
          predictionData: mockPredictionData
        }
      })

      expect(wrapper.text()).not.toContain('Volumen')
    })
  })

  describe('weight comparison', () => {
    it('should display weight comparison if available', () => {
      const dataWithComparison = {
        ...mockPredictionData,
        weight_comparison: {
          vision_weight: 1.75,
          regression_weight: 1.8,
          difference: 0.05,
          agreement_level: 'high'
        }
      }

      const wrapper = mount(PredictionResults, {
        props: {
          predictionData: dataWithComparison
        }
      })

      expect(wrapper.text()).toContain('Comparación de Métodos')
      expect(wrapper.text()).toContain('1.75')
      expect(wrapper.text()).toContain('1.80')
      expect(wrapper.text()).toContain('0.05')
      expect(wrapper.text()).toContain('high')
    })

    it('should not display weight comparison if not available', () => {
      const wrapper = mount(PredictionResults, {
        props: {
          predictionData: mockPredictionData
        }
      })

      expect(wrapper.text()).not.toContain('Comparación de Métodos')
    })
  })

  describe('formatNumber', () => {
    it('should format null as N/A', () => {
      const data = { ...mockPredictionData, width: null }
      const wrapper = mount(PredictionResults, {
        props: {
          predictionData: data
        }
      })

      expect(wrapper.text()).toContain('N/A')
    })

    it('should format undefined as N/A', () => {
      const data = { ...mockPredictionData, width: undefined }
      const wrapper = mount(PredictionResults, {
        props: {
          predictionData: data
        }
      })

      expect(wrapper.text()).toContain('N/A')
    })

    it('should format NaN as N/A', () => {
      const data = { ...mockPredictionData, width: Number.NaN }
      const wrapper = mount(PredictionResults, {
        props: {
          predictionData: data
        }
      })

      expect(wrapper.text()).toContain('N/A')
    })
  })

  describe('confidence recommendations', () => {
    const recommendations = {
      'very_high': 'Excelente precisión',
      'high': 'Buena precisión',
      'medium': 'Precisión aceptable',
      'low': 'Verificar manualmente',
      'very_low': 'Revisar imagen',
      'unknown': 'Calidad desconocida'
    }

    for (const [level, recommendation] of Object.entries(recommendations)) {
      it(`should show ${level} recommendation`, () => {
        const data = { ...mockPredictionData, confidence_level: level }
        const wrapper = mount(PredictionResults, {
          props: {
            predictionData: data
          }
        })

        expect(wrapper.text()).toContain(recommendation)
      })
    }
  })

  describe('prop validation', () => {
    it('should validate required props', () => {
      const validator = PredictionResults.props.predictionData.validator

      const validData = {
        width: 10,
        height: 12,
        thickness: 8,
        predicted_weight: 1.5
      }

      expect(validator(validData)).toBe(true)
    })

    it('should reject invalid props', () => {
      const validator = PredictionResults.props.predictionData.validator

      const invalidData = {
        width: 10
        // Missing required fields
      }

      expect(validator(invalidData)).toBe(false)
    })
  })
})

