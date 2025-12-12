import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import AnalysisActions from '../AnalysisActions.vue'

// Mock BaseAnalysisActions component
vi.mock('@/components/common/BaseAnalysisActions.vue', () => ({
  default: {
    name: 'BaseAnalysisActions',
    template: `
      <div>
        <button @click="$emit('download-pdf')" data-testid="download-pdf-btn">Download PDF</button>
        <button @click="$emit('new-analysis')" data-testid="new-analysis-btn">New Analysis</button>
      </div>
    `,
    emits: ['download-pdf', 'new-analysis']
  }
}))

describe('AnalysisActions', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render BaseAnalysisActions component', () => {
    wrapper = mount(AnalysisActions)

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.findComponent({ name: 'BaseAnalysisActions' }).exists()).toBe(true)
  })

  it('should emit download-pdf event when BaseAnalysisActions emits it', async () => {
    wrapper = mount(AnalysisActions)

    wrapper.findComponent({ name: 'BaseAnalysisActions' })
    const downloadButton = wrapper.find('[data-testid="download-pdf-btn"]')

    await downloadButton.trigger('click')

    expect(wrapper.emitted('download-pdf')).toBeTruthy()
    expect(wrapper.emitted('download-pdf')).toHaveLength(1)
  })

  it('should emit new-analysis event when BaseAnalysisActions emits it', async () => {
    wrapper = mount(AnalysisActions)

    wrapper.findComponent({ name: 'BaseAnalysisActions' })
    const newAnalysisButton = wrapper.find('[data-testid="new-analysis-btn"]')

    await newAnalysisButton.trigger('click')

    expect(wrapper.emitted('new-analysis')).toBeTruthy()
    expect(wrapper.emitted('new-analysis')).toHaveLength(1)
  })

  it('should emit both events independently', async () => {
    wrapper = mount(AnalysisActions)

    const downloadButton = wrapper.find('[data-testid="download-pdf-btn"]')
    const newAnalysisButton = wrapper.find('[data-testid="new-analysis-btn"]')

    await downloadButton.trigger('click')
    await newAnalysisButton.trigger('click')

    expect(wrapper.emitted('download-pdf')).toHaveLength(1)
    expect(wrapper.emitted('new-analysis')).toHaveLength(1)
  })

  it('should emit multiple download-pdf events', async () => {
    wrapper = mount(AnalysisActions)

    const downloadButton = wrapper.find('[data-testid="download-pdf-btn"]')

    await downloadButton.trigger('click')
    await downloadButton.trigger('click')

    expect(wrapper.emitted('download-pdf')).toHaveLength(2)
  })

  it('should emit multiple new-analysis events', async () => {
    wrapper = mount(AnalysisActions)

    const newAnalysisButton = wrapper.find('[data-testid="new-analysis-btn"]')

    await newAnalysisButton.trigger('click')
    await newAnalysisButton.trigger('click')

    expect(wrapper.emitted('new-analysis')).toHaveLength(2)
  })
})

