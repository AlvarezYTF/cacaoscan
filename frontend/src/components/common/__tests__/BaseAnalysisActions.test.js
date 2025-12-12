/**
 * Unit tests for BaseAnalysisActions component
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseAnalysisActions from '../BaseAnalysisActions.vue'

describe('BaseAnalysisActions', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Props validation', () => {
    it('should accept showDownloadPdf prop', () => {
      wrapper = mount(BaseAnalysisActions, {
        props: {
          showDownloadPdf: true
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should accept showNewAnalysis prop', () => {
      wrapper = mount(BaseAnalysisActions, {
        props: {
          showNewAnalysis: true
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should default showDownloadPdf to true', () => {
      wrapper = mount(BaseAnalysisActions)
      expect(wrapper.props('showDownloadPdf')).toBe(true)
    })

    it('should default showNewAnalysis to true', () => {
      wrapper = mount(BaseAnalysisActions)
      expect(wrapper.props('showNewAnalysis')).toBe(true)
    })
  })

  describe('Rendering', () => {
    it('should render download PDF button when showDownloadPdf is true', () => {
      wrapper = mount(BaseAnalysisActions, {
        props: {
          showDownloadPdf: true
        }
      })

      const buttons = wrapper.findAll('button')
      const downloadButton = buttons.find(btn => btn.text().includes('Descargar PDF'))
      expect(downloadButton).toBeTruthy()
    })

    it('should not render download PDF button when showDownloadPdf is false', () => {
      wrapper = mount(BaseAnalysisActions, {
        props: {
          showDownloadPdf: false
        }
      })

      const buttons = wrapper.findAll('button')
      const downloadButton = buttons.find(btn => btn.text().includes('Descargar PDF'))
      expect(downloadButton).toBeFalsy()
    })

    it('should render new analysis button when showNewAnalysis is true', () => {
      wrapper = mount(BaseAnalysisActions, {
        props: {
          showNewAnalysis: true
        }
      })

      const buttons = wrapper.findAll('button')
      const newAnalysisButton = buttons.find(btn => btn.text().includes('Nuevo Análisis'))
      expect(newAnalysisButton).toBeTruthy()
    })

    it('should not render new analysis button when showNewAnalysis is false', () => {
      wrapper = mount(BaseAnalysisActions, {
        props: {
          showNewAnalysis: false
        }
      })

      const buttons = wrapper.findAll('button')
      const newAnalysisButton = buttons.find(btn => btn.text().includes('Nuevo Análisis'))
      expect(newAnalysisButton).toBeFalsy()
    })

    it('should use custom download label when provided', () => {
      wrapper = mount(BaseAnalysisActions, {
        props: {
          showDownloadPdf: true,
          downloadLabel: 'Custom Download'
        }
      })

      expect(wrapper.text()).toContain('Custom Download')
    })

    it('should use custom new analysis label when provided', () => {
      wrapper = mount(BaseAnalysisActions, {
        props: {
          showNewAnalysis: true,
          newAnalysisLabel: 'Custom New'
        }
      })

      expect(wrapper.text()).toContain('Custom New')
    })

    it('should apply containerClass when provided', () => {
      wrapper = mount(BaseAnalysisActions, {
        props: {
          containerClass: 'custom-class'
        }
      })

      const container = wrapper.find('div')
      expect(container.classes()).toContain('custom-class')
    })
  })

  describe('Events', () => {
    it('should emit download-pdf when download button is clicked', async () => {
      wrapper = mount(BaseAnalysisActions, {
        props: {
          showDownloadPdf: true
        }
      })

      const buttons = wrapper.findAll('button')
      const downloadButton = buttons.find(btn => btn.text().includes('Descargar PDF'))
      await downloadButton.trigger('click')

      expect(wrapper.emitted('download-pdf')).toBeTruthy()
    })

    it('should emit new-analysis when new analysis button is clicked', async () => {
      wrapper = mount(BaseAnalysisActions, {
        props: {
          showNewAnalysis: true
        }
      })

      const buttons = wrapper.findAll('button')
      const newAnalysisButton = buttons.find(btn => btn.text().includes('Nuevo Análisis'))
      await newAnalysisButton.trigger('click')

      expect(wrapper.emitted('new-analysis')).toBeTruthy()
    })
  })

  describe('Slots', () => {
    it('should render default slot content when provided', () => {
      wrapper = mount(BaseAnalysisActions, {
        slots: {
          default: '<button>Custom Action</button>'
        }
      })

      expect(wrapper.text()).toContain('Custom Action')
    })

    it('should not render default buttons when slot is provided', () => {
      wrapper = mount(BaseAnalysisActions, {
        slots: {
          default: '<button>Custom Action</button>'
        }
      })

      const buttons = wrapper.findAll('button')
      const downloadButton = buttons.find(btn => btn.text().includes('Descargar PDF'))
      expect(downloadButton).toBeFalsy()
    })
  })
})

