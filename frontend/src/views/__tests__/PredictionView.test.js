import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PredictionView from '../PredictionView.vue'

describe('PredictionView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should render prediction view', () => {
    const wrapper = mount(PredictionView, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })
})

