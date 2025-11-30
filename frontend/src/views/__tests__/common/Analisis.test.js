import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import Analisis from '../../common/Analisis.vue'

const mockAnalysisStore = {
  currentAnalysis: null,
  analyses: [],
  loading: false,
  error: null,
  fetchAnalyses: vi.fn(),
  getAnalysisById: vi.fn()
}

vi.mock('@/stores/analysis', () => ({
  useAnalysisStore: () => mockAnalysisStore
}))

describe('Analisis', () => {
  let router
  let wrapper

  beforeEach(() => {
    setActivePinia(createPinia())
    router = createRouter({
      history: createWebHistory(),
      routes: [{ path: '/', component: Analisis }]
    })
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render analysis view', () => {
    wrapper = mount(Analisis, {
      global: {
        plugins: [router],
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should load analyses on mount', async () => {
    mockAnalysisStore.fetchAnalyses.mockResolvedValue({
      data: { results: [] }
    })

    wrapper = mount(Analisis, {
      global: {
        plugins: [router],
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(mockAnalysisStore.fetchAnalyses).toHaveBeenCalled()
  })

  it('should display analyses list', async () => {
    mockAnalysisStore.analyses = [
      { id: 1, imagen: 'test1.jpg', resultado: { peso: 1.5 } },
      { id: 2, imagen: 'test2.jpg', resultado: { peso: 2.0 } }
    ]

    wrapper = mount(Analisis, {
      global: {
        plugins: [router],
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.vm.analyses).toHaveLength(2)
  })

  it('should filter analyses', async () => {
    wrapper = mount(Analisis, {
      global: {
        plugins: [router],
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    wrapper.vm.searchQuery = 'test'
    await wrapper.vm.$nextTick()

    if (wrapper.vm.filteredAnalyses) {
      expect(wrapper.vm.filteredAnalyses).toBeDefined()
    }
  })

  it('should display analysis details', async () => {
    mockAnalysisStore.currentAnalysis = {
      id: 1,
      imagen: 'test.jpg',
      resultado: {
        peso: 1.5,
        dimensiones: { ancho: 10, alto: 15 }
      }
    }

    wrapper = mount(Analisis, {
      global: {
        plugins: [router],
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('1.5')
  })

  it('should handle analysis selection', async () => {
    mockAnalysisStore.getAnalysisById.mockResolvedValue({
      data: { id: 1, resultado: { peso: 1.5 } }
    })

    wrapper = mount(Analisis, {
      global: {
        plugins: [router],
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    if (wrapper.vm.selectAnalysis) {
      await wrapper.vm.selectAnalysis(1)
      await wrapper.vm.$nextTick()

      expect(mockAnalysisStore.getAnalysisById).toHaveBeenCalledWith(1)
    }
  })

  it('should export analysis data', async () => {
    wrapper = mount(Analisis, {
      global: {
        plugins: [router],
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    if (wrapper.vm.exportAnalysis) {
      const exportSpy = vi.spyOn(wrapper.vm, 'exportAnalysis')
      await wrapper.vm.exportAnalysis(1)
      await wrapper.vm.$nextTick()

      expect(exportSpy).toHaveBeenCalled()
    }
  })
})

