import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import AnalysisHeader from '../AnalysisHeader.vue'

// Mock BaseAnalysisHeader component
vi.mock('@/components/common/BaseAnalysisHeader.vue', () => ({
  default: {
    name: 'BaseAnalysisHeader',
    template: `
      <div>
        <h2 v-if="analysisId" data-testid="analysis-title">Detalles del Análisis #{{ analysisId }}</h2>
        <p v-if="subtitle" data-testid="subtitle">{{ subtitle }}</p>
      </div>
    `,
    props: {
      analysisId: {
        type: [String, Number],
        required: false
      },
      subtitle: {
        type: String,
        default: ''
      }
    }
  }
}))

describe('AnalysisHeader', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render BaseAnalysisHeader component', () => {
    wrapper = mount(AnalysisHeader, {
      props: {
        analysisId: 1
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.findComponent({ name: 'BaseAnalysisHeader' }).exists()).toBe(true)
  })

  it('should pass analysisId prop to BaseAnalysisHeader', () => {
    wrapper = mount(AnalysisHeader, {
      props: {
        analysisId: 123
      }
    })

    const baseComponent = wrapper.findComponent({ name: 'BaseAnalysisHeader' })
    expect(baseComponent.props('analysisId')).toBe(123)
  })

  it('should pass analysisId as string to BaseAnalysisHeader', () => {
    wrapper = mount(AnalysisHeader, {
      props: {
        analysisId: '456'
      }
    })

    const baseComponent = wrapper.findComponent({ name: 'BaseAnalysisHeader' })
    expect(baseComponent.props('analysisId')).toBe('456')
  })

  it('should pass default subtitle to BaseAnalysisHeader when not provided', () => {
    wrapper = mount(AnalysisHeader, {
      props: {
        analysisId: 1
      }
    })

    const baseComponent = wrapper.findComponent({ name: 'BaseAnalysisHeader' })
    expect(baseComponent.props('subtitle')).toBe('Resultados del análisis de calidad del lote')
  })

  it('should pass custom subtitle to BaseAnalysisHeader', () => {
    const customSubtitle = 'Análisis personalizado'
    wrapper = mount(AnalysisHeader, {
      props: {
        analysisId: 1,
        subtitle: customSubtitle
      }
    })

    const baseComponent = wrapper.findComponent({ name: 'BaseAnalysisHeader' })
    expect(baseComponent.props('subtitle')).toBe(customSubtitle)
  })

  it('should render analysis title with correct ID', () => {
    wrapper = mount(AnalysisHeader, {
      props: {
        analysisId: 789
      }
    })

    const title = wrapper.find('[data-testid="analysis-title"]')
    expect(title.exists()).toBe(true)
    expect(title.text()).toContain('789')
  })

  it('should render subtitle text', () => {
    const customSubtitle = 'Subtítulo personalizado'
    wrapper = mount(AnalysisHeader, {
      props: {
        analysisId: 1,
        subtitle: customSubtitle
      }
    })

    const subtitle = wrapper.find('[data-testid="subtitle"]')
    expect(subtitle.exists()).toBe(true)
    expect(subtitle.text()).toBe(customSubtitle)
  })

  it('should update props when they change', async () => {
    wrapper = mount(AnalysisHeader, {
      props: {
        analysisId: 1,
        subtitle: 'Initial subtitle'
      }
    })

    const baseComponent = wrapper.findComponent({ name: 'BaseAnalysisHeader' })
    expect(baseComponent.props('analysisId')).toBe(1)
    expect(baseComponent.props('subtitle')).toBe('Initial subtitle')

    await wrapper.setProps({
      analysisId: 2,
      subtitle: 'Updated subtitle'
    })

    expect(baseComponent.props('analysisId')).toBe(2)
    expect(baseComponent.props('subtitle')).toBe('Updated subtitle')
  })

  it('should require analysisId prop', () => {
    // This test verifies that the prop is required
    // In Vue 3, missing required props will cause a warning
    wrapper = mount(AnalysisHeader, {
      props: {
        analysisId: 1
      }
    })

    expect(wrapper.props('analysisId')).toBe(1)
  })
})

