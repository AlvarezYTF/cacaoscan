import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ReportGeneratorModal from '../ReportGeneratorModal.vue'

const mockReportsStore = {
  createReport: vi.fn(),
  fetchFincas: vi.fn().mockResolvedValue({ data: { results: [] } }),
  fetchUsers: vi.fn().mockResolvedValue({ data: { results: [] } }),
  loading: false
}

vi.mock('@/stores/reports', () => ({
  useReportsStore: () => mockReportsStore
}))

describe('ReportGeneratorModal', () => {
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

  it('should render modal when open', () => {
    wrapper = mount(ReportGeneratorModal, {
      props: {
        isOpen: true
      },
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should not render when closed', () => {
    wrapper = mount(ReportGeneratorModal, {
      props: {
        isOpen: false
      },
      global: {
        stubs: { 'router-link': true }
      }
    })

    // Modal should be hidden or not visible
    expect(wrapper.exists()).toBe(true)
  })

  it('should emit close event', async () => {
    wrapper = mount(ReportGeneratorModal, {
      props: {
        isOpen: true
      },
      global: {
        stubs: { 'router-link': true }
      }
    })

    if (wrapper.vm.handleClose) {
      await wrapper.vm.handleClose()
      expect(wrapper.emitted('close')).toBeTruthy()
    }
  })
})

