import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import UploadImagesView from '../UploadImagesView.vue'

describe('UploadImagesView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should render upload images view', () => {
    const wrapper = mount(UploadImagesView, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })
})

