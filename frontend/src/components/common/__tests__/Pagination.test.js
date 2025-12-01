import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Pagination from '../Pagination.vue'

describe('Pagination', () => {
  it('should not render when totalPages is 1', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalPages: 1
      }
    })

    expect(wrapper.find('nav').exists()).toBe(false)
  })

  it('should render when totalPages > 1', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalPages: 5
      }
    })

    expect(wrapper.find('nav').exists()).toBe(true)
  })

  it('should emit page-change when clicking next', async () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalPages: 5
      }
    })

    const nextButton = wrapper.findAll('button').find(btn => btn.text().includes('Siguiente'))
    await nextButton.trigger('click')

    expect(wrapper.emitted('page-change')).toBeTruthy()
    expect(wrapper.emitted('page-change')[0]).toEqual([2])
  })

  it('should emit page-change when clicking previous', async () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 2,
        totalPages: 5
      }
    })

    const prevButton = wrapper.findAll('button').find(btn => btn.text().includes('Anterior'))
    await prevButton.trigger('click')

    expect(wrapper.emitted('page-change')).toBeTruthy()
    expect(wrapper.emitted('page-change')[0]).toEqual([1])
  })

  it('should disable previous button on first page', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalPages: 5
      }
    })

    const prevButton = wrapper.findAll('button').find(btn => btn.text().includes('Anterior'))
    expect(prevButton.attributes('disabled')).toBeDefined()
  })

  it('should disable next button on last page', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 5,
        totalPages: 5
      }
    })

    const nextButton = wrapper.findAll('button').find(btn => btn.text().includes('Siguiente'))
    expect(nextButton.attributes('disabled')).toBeDefined()
  })

  it('should display current page and total pages', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 3,
        totalPages: 10,
        totalItems: 100,
        itemsPerPage: 10
      }
    })

    // Pagination shows "Mostrando X a Y de Z resultados"
    // For page 3 with 10 items per page: startItem = 21, endItem = 30
    expect(wrapper.text()).toContain('Mostrando')
    expect(wrapper.text()).toContain('21')
    expect(wrapper.text()).toContain('30')
    expect(wrapper.text()).toContain('100')
  })

  it('should display total items when provided', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalPages: 5,
        totalItems: 50,
        itemsPerPage: 10
      }
    })

    // Should show "Mostrando 1 a 10 de 50 resultados"
    expect(wrapper.text()).toContain('Mostrando')
    expect(wrapper.text()).toContain('50')
    expect(wrapper.text()).toContain('resultados')
  })

  it('should show ellipsis when many pages', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 5,
        totalPages: 20,
        totalItems: 200,
        itemsPerPage: 10,
        maxVisiblePages: 5
      }
    })

    // Check if separator span with "..." exists
    // If separator should be shown based on currentPage position
    // For currentPage=5 and maxVisiblePages=5, it might show separator
    // Note: ellipsis variable removed as it was unused
    expect(wrapper.html()).toContain('...')
  })
})

