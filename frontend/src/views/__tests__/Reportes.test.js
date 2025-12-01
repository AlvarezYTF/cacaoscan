import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Reportes from '../Reportes.vue'

const mockReportsStore = {
  reports: [],
  loading: false,
  error: null,
  fetchReports: vi.fn(),
  createReport: vi.fn()
}

vi.mock('@/stores/reports', () => ({
  useReportsStore: () => mockReportsStore
}))

describe('Reportes', () => {
  let wrapper

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render reportes view', () => {
    wrapper = mount(Reportes, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('should load reports on mount', async () => {
    mockReportsStore.fetchReports.mockResolvedValue({ data: { results: [] } })
    wrapper = mount(Reportes, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })
    await wrapper.vm.$nextTick()
    expect(mockReportsStore.fetchReports).toHaveBeenCalled()
  })
})

