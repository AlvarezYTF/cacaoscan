import { describe, it, expect, vi } from 'vitest'
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
        totalPages: 10
      }
    })

    expect(wrapper.text()).toContain('Página 3 de 10')
  })

  it('should display total items when provided', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalPages: 5,
        totalItems: 50
      }
    })

    expect(wrapper.text()).toContain('50 elementos')
  })

  it('should show ellipsis when many pages', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 5,
        totalPages: 20,
        maxVisiblePages: 5
      }
    })

    const ellipsis = wrapper.findAll('.page-link').filter(link => link.text() === '...')
    expect(ellipsis.length).toBeGreaterThan(0)
  })
})

