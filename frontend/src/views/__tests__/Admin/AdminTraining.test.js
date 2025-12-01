import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AdminTraining from '../../Admin/AdminTraining.vue'

describe('AdminTraining', () => {
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

  it('should render training view', () => {
    wrapper = mount(AdminTraining, {
      global: {
        stubs: {
          'router-link': true,
          'router-view': true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })
})

