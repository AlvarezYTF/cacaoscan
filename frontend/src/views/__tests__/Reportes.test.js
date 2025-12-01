import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Reportes from '../Reportes.vue'

const mockReportsStore = {
  reports: [],
  stats: {
    totalReports: 0,
    reportsChange: 0,
    completedReports: 0,
    completedChange: 0,
    inProgressReports: 0,
    inProgressChange: 0,
    errorReports: 0,
    errorChange: 0
  },
  pagination: {
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    itemsPerPage: 20
  },
  loading: false,
  error: null,
  fetchReports: vi.fn().mockResolvedValue({ data: { results: [] } }),
  fetchStats: vi.fn().mockResolvedValue({
    total_reports: 0,
    reports_change: 0,
    completed_reports: 0,
    completed_change: 0,
    in_progress_reports: 0,
    in_progress_change: 0,
    error_reports: 0,
    error_change: 0
  }),
  fetchUsers: vi.fn().mockResolvedValue({ data: { results: [] } }),
  fetchFincas: vi.fn().mockResolvedValue({ data: { results: [] } }),
  fetchLotesByFinca: vi.fn().mockResolvedValue({ data: { results: [] } }),
  createReport: vi.fn(),
  addReport: vi.fn(),
  downloadReport: vi.fn(),
  deleteReport: vi.fn(),
  exportReports: vi.fn(),
  bulkDeleteReports: vi.fn()
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

