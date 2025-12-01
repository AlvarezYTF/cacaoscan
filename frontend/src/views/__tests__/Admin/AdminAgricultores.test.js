import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AdminAgricultores from '../../Admin/AdminAgricultores.vue'

describe('AdminAgricultores', () => {
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

  it('should render agricultores view', () => {
    wrapper = mount(AdminAgricultores, {
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

