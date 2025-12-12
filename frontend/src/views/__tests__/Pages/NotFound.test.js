import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import NotFound from '../../Pages/NotFound.vue'

describe('NotFound', () => {
  it('should render 404 page', () => {
    const wrapper = mount(NotFound, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.text().includes('404') || wrapper.text().includes('No encontrado')).toBe(true)
  })
})

