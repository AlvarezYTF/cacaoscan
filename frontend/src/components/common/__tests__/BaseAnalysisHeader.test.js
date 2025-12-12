/**
 * Unit tests for BaseAnalysisHeader component
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseAnalysisHeader from '../BaseAnalysisHeader.vue'

describe('BaseAnalysisHeader', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Props validation', () => {
    it('should accept title prop', () => {
      wrapper = mount(BaseAnalysisHeader, {
        props: {
          title: 'Test Title'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should accept analysisId prop', () => {
      wrapper = mount(BaseAnalysisHeader, {
        props: {
          analysisId: 123
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should accept subtitle prop', () => {
      wrapper = mount(BaseAnalysisHeader, {
        props: {
          subtitle: 'Test Subtitle'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Rendering', () => {
    it('should render title when provided', () => {
      wrapper = mount(BaseAnalysisHeader, {
        props: {
          title: 'Test Title'
        }
      })

      expect(wrapper.text()).toContain('Test Title')
    })

    it('should render analysisId when title is not provided', () => {
      wrapper = mount(BaseAnalysisHeader, {
        props: {
          analysisId: 123
        }
      })

      expect(wrapper.text()).toContain('Detalles del Análisis #123')
    })

    it('should prioritize title over analysisId', () => {
      wrapper = mount(BaseAnalysisHeader, {
        props: {
          title: 'Custom Title',
          analysisId: 123
        }
      })

      expect(wrapper.text()).toContain('Custom Title')
      expect(wrapper.text()).not.toContain('Detalles del Análisis #123')
    })

    it('should render subtitle when provided', () => {
      wrapper = mount(BaseAnalysisHeader, {
        props: {
          title: 'Test Title',
          subtitle: 'Test Subtitle'
        }
      })

      expect(wrapper.text()).toContain('Test Subtitle')
    })

    it('should use default subtitle when not provided', () => {
      wrapper = mount(BaseAnalysisHeader, {
        props: {
          title: 'Test Title'
        }
      })

      expect(wrapper.text()).toContain('Resultados del análisis de calidad del lote')
    })

    it('should apply containerClass when provided', () => {
      wrapper = mount(BaseAnalysisHeader, {
        props: {
          title: 'Test Title',
          containerClass: 'custom-class'
        }
      })

      const container = wrapper.find('div')
      expect(container.classes()).toContain('custom-class')
    })
  })

  describe('Slots', () => {
    it('should render title slot when provided', () => {
      wrapper = mount(BaseAnalysisHeader, {
        slots: {
          title: '<h2>Custom Title</h2>'
        }
      })

      expect(wrapper.text()).toContain('Custom Title')
    })

    it('should render subtitle slot when provided', () => {
      wrapper = mount(BaseAnalysisHeader, {
        slots: {
          subtitle: '<p>Custom Subtitle</p>'
        }
      })

      expect(wrapper.text()).toContain('Custom Subtitle')
    })

    it('should render actions slot when provided', () => {
      wrapper = mount(BaseAnalysisHeader, {
        slots: {
          actions: '<button>Action</button>'
        }
      })

      expect(wrapper.text()).toContain('Action')
    })
  })
})

