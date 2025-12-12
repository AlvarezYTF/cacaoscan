/**
 * Unit tests for BaseBatchInfoCard component
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseBatchInfoCard from '../BaseBatchInfoCard.vue'

vi.mock('../BaseProgressIndicator.vue', () => ({
  default: {
    name: 'BaseProgressIndicator',
    template: '<div class="progress-indicator"></div>',
    props: {
      value: Number,
      max: Number,
      format: String,
      variant: String
    }
  }
}))

describe('BaseBatchInfoCard', () => {
  let wrapper

  const createBatchInfo = () => ({
    total: 100,
    completed: 75,
    failed: 5
  })

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Props validation', () => {
    it('should require batchInfo prop', () => {
      expect(() => {
        wrapper = mount(BaseBatchInfoCard)
      }).toThrow()
    })

    it('should accept batchInfo prop', () => {
      const batchInfo = createBatchInfo()
      wrapper = mount(BaseBatchInfoCard, {
        props: {
          batchInfo
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should accept title prop', () => {
      const batchInfo = createBatchInfo()
      wrapper = mount(BaseBatchInfoCard, {
        props: {
          batchInfo,
          title: 'Test Title'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should accept variant prop', () => {
      const batchInfo = createBatchInfo()
      wrapper = mount(BaseBatchInfoCard, {
        props: {
          batchInfo,
          variant: 'compact'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Rendering', () => {
    it('should render with default title when not provided', () => {
      const batchInfo = createBatchInfo()
      wrapper = mount(BaseBatchInfoCard, {
        props: {
          batchInfo
        }
      })

      expect(wrapper.text()).toContain('Información del Lote')
    })

    it('should render custom title when provided', () => {
      const batchInfo = createBatchInfo()
      wrapper = mount(BaseBatchInfoCard, {
        props: {
          batchInfo,
          title: 'Custom Title'
        }
      })

      expect(wrapper.text()).toContain('Custom Title')
    })

    it('should render subtitle when provided', () => {
      const batchInfo = createBatchInfo()
      wrapper = mount(BaseBatchInfoCard, {
        props: {
          batchInfo,
          subtitle: 'Test Subtitle'
        }
      })

      expect(wrapper.text()).toContain('Test Subtitle')
    })

    it('should display total items', () => {
      const batchInfo = createBatchInfo()
      wrapper = mount(BaseBatchInfoCard, {
        props: {
          batchInfo
        }
      })

      expect(wrapper.text()).toContain('Total de elementos:')
      expect(wrapper.text()).toContain('100')
    })

    it('should display completed items', () => {
      const batchInfo = createBatchInfo()
      wrapper = mount(BaseBatchInfoCard, {
        props: {
          batchInfo
        }
      })

      expect(wrapper.text()).toContain('Completados:')
      expect(wrapper.text()).toContain('75')
    })

    it('should display failed items when greater than 0', () => {
      const batchInfo = createBatchInfo()
      wrapper = mount(BaseBatchInfoCard, {
        props: {
          batchInfo
        }
      })

      expect(wrapper.text()).toContain('Fallidos:')
      expect(wrapper.text()).toContain('5')
    })

    it('should not display failed items when 0', () => {
      const batchInfo = { total: 100, completed: 100, failed: 0 }
      wrapper = mount(BaseBatchInfoCard, {
        props: {
          batchInfo
        }
      })

      expect(wrapper.text()).not.toContain('Fallidos:')
    })

    it('should render progress indicator', () => {
      const batchInfo = createBatchInfo()
      wrapper = mount(BaseBatchInfoCard, {
        props: {
          batchInfo
        }
      })

      expect(wrapper.findComponent({ name: 'BaseProgressIndicator' }).exists()).toBe(true)
    })
  })

  describe('Computed properties', () => {
    it('should apply default container class', () => {
      const batchInfo = createBatchInfo()
      wrapper = mount(BaseBatchInfoCard, {
        props: {
          batchInfo,
          variant: 'default'
        }
      })

      expect(wrapper.vm.containerClass).toBe('')
    })

    it('should apply compact container class', () => {
      const batchInfo = createBatchInfo()
      wrapper = mount(BaseBatchInfoCard, {
        props: {
          batchInfo,
          variant: 'compact'
        }
      })

      expect(wrapper.vm.containerClass).toBe('p-3')
    })

    it('should apply detailed container class', () => {
      const batchInfo = createBatchInfo()
      wrapper = mount(BaseBatchInfoCard, {
        props: {
          batchInfo,
          variant: 'detailed'
        }
      })

      expect(wrapper.vm.containerClass).toBe('p-6')
    })
  })

  describe('Slots', () => {
    it('should render default slot content', () => {
      const batchInfo = createBatchInfo()
      wrapper = mount(BaseBatchInfoCard, {
        props: {
          batchInfo
        },
        slots: {
          default: '<div>Custom Content</div>'
        }
      })

      expect(wrapper.text()).toContain('Custom Content')
    })

    it('should render header-actions slot', () => {
      const batchInfo = createBatchInfo()
      wrapper = mount(BaseBatchInfoCard, {
        props: {
          batchInfo
        },
        slots: {
          'header-actions': '<button>Action</button>'
        }
      })

      expect(wrapper.text()).toContain('Action')
    })

    it('should render footer slot', () => {
      const batchInfo = createBatchInfo()
      wrapper = mount(BaseBatchInfoCard, {
        props: {
          batchInfo
        },
        slots: {
          footer: '<div>Footer Content</div>'
        }
      })

      expect(wrapper.text()).toContain('Footer Content')
    })
  })

  describe('Edge cases', () => {
    it('should handle missing total', () => {
      const batchInfo = { completed: 50 }
      wrapper = mount(BaseBatchInfoCard, {
        props: {
          batchInfo
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should handle missing completed', () => {
      const batchInfo = { total: 100 }
      wrapper = mount(BaseBatchInfoCard, {
        props: {
          batchInfo
        }
      })

      expect(wrapper.exists()).toBe(true)
    })
  })
})

