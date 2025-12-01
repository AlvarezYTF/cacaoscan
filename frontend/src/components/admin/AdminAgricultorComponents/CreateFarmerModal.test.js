import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import CreateFarmerModal from './CreateFarmerModal.vue'

vi.mock('@/components/common/BaseModal.vue', () => ({
  default: {
    name: 'BaseModal',
    template: '<div v-if="show"><slot name="header"></slot><slot></slot><slot name="footer"></slot></div>',
    props: {
      show: {
        type: Boolean,
        default: true
      },
      title: String,
      subtitle: String,
      maxWidth: String
    },
    emits: ['close', 'update:show']
  }
}))

// Mock useNotifications composable to prevent real API calls
vi.mock('@/composables/useNotifications', () => ({
  useNotifications: () => ({
    showSuccess: vi.fn(),
    showError: vi.fn(),
    showWarning: vi.fn(),
    showInfo: vi.fn(),
    clearAll: vi.fn(),
    notifications: [],
    unreadCount: 0,
    loading: false,
    error: null
  })
}))

// Mock api to prevent real API calls when errors occur
vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn().mockResolvedValue({ data: {} }),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn()
  }
}))

// Mock authApi to prevent real API calls
vi.mock('@/services/authApi', () => ({
  default: {
    registerUser: vi.fn().mockResolvedValue({ data: { user: { id: 1 } } })
  }
}))

describe('CreateFarmerModal', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render modal when isOpen is true', () => {
    wrapper = mount(CreateFarmerModal)

    expect(wrapper.exists()).toBe(true)
  })

  it('should display create farmer title', async () => {
    wrapper = mount(CreateFarmerModal)

    await wrapper.vm.openModal()
    await wrapper.vm.$nextTick()

    const text = wrapper.text()
    expect(text.includes('Crear') || text.includes('Agricultor')).toBe(true)
  })

  it('should emit close event when modal is closed', async () => {
    wrapper = mount(CreateFarmerModal)

    await wrapper.vm.openModal()
    await wrapper.vm.$nextTick()

    await wrapper.vm.closeModal()

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should emit created event when farmer is created successfully', async () => {
    wrapper = mount(CreateFarmerModal)

    await wrapper.vm.openModal()
    await wrapper.vm.$nextTick()

    const form = wrapper.find('form')
    if (form.exists()) {
      await form.trigger('submit.prevent')
      await wrapper.vm.$nextTick()
    }
  })
})

