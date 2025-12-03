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

  it('should sync currentPage with composable', async () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalPages: 5
      }
    })

    await wrapper.setProps({ currentPage: 2 })
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.pagination.currentPage.value).toBe(2)
  })

  it('should sync totalItems with composable', async () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalPages: 5,
        totalItems: 50
      }
    })

    await wrapper.setProps({ totalItems: 100 })
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.pagination.totalItems.value).toBe(100)
  })

  it('should sync itemsPerPage with composable', async () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalPages: 5,
        itemsPerPage: 10
      }
    })

    await wrapper.setProps({ itemsPerPage: 20 })
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.pagination.itemsPerPage.value).toBe(20)
  })

  it('should calculate startItem correctly', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 3,
        totalPages: 10,
        totalItems: 100,
        itemsPerPage: 10
      }
    })

    expect(wrapper.vm.startItem).toBe(21)
  })

  it('should calculate endItem correctly', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 3,
        totalPages: 10,
        totalItems: 100,
        itemsPerPage: 10
      }
    })

    expect(wrapper.vm.endItem).toBe(30)
  })

  it('should calculate endItem correctly on last page', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 10,
        totalPages: 10,
        totalItems: 95,
        itemsPerPage: 10
      }
    })

    expect(wrapper.vm.endItem).toBe(95)
  })

  it('should show all pages when totalPages <= maxVisiblePages', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalPages: 5,
        maxVisiblePages: 5
      }
    })

    expect(wrapper.vm.visiblePages.length).toBe(5)
  })

  it('should show first pages when currentPage <= 3', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 2,
        totalPages: 20,
        maxVisiblePages: 5
      }
    })

    expect(wrapper.vm.visiblePages).toEqual([1, 2, 3])
  })

  it('should show last pages when currentPage >= totalPages - 2', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 19,
        totalPages: 20,
        maxVisiblePages: 5
      }
    })

    expect(wrapper.vm.visiblePages).toEqual([18, 19, 20])
  })

  it('should show middle pages when currentPage is in middle', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 10,
        totalPages: 20,
        maxVisiblePages: 5
      }
    })

    expect(wrapper.vm.visiblePages).toEqual([9, 10, 11])
  })

  it('should show page separator when conditions are met', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 10,
        totalPages: 20,
        maxVisiblePages: 5
      }
    })

    expect(wrapper.vm.showPageSeparator).toBe(true)
  })

  it('should not show page separator when conditions are not met', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 2,
        totalPages: 20,
        maxVisiblePages: 5
      }
    })

    expect(wrapper.vm.showPageSeparator).toBe(false)
  })

  it('should emit page-change when goToPage is called with valid page', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalPages: 5
      }
    })

    wrapper.vm.goToPage(3)

    expect(wrapper.emitted('page-change')).toBeTruthy()
    expect(wrapper.emitted('page-change')[0]).toEqual([3])
  })

  it('should not emit page-change when goToPage is called with invalid page', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalPages: 5
      }
    })

    wrapper.vm.goToPage(0)
    wrapper.vm.goToPage(6)
    wrapper.vm.goToPage(1)

    expect(wrapper.emitted('page-change')).toBeFalsy()
  })

  it('should emit items-per-page-change when handleItemsPerPageChange is called', () => {
    const wrapper = mount(Pagination, {
      props: {
        currentPage: 1,
        totalPages: 5
      }
    })

    wrapper.vm.handleItemsPerPageChange(20)

    expect(wrapper.emitted('items-per-page-change')).toBeTruthy()
    expect(wrapper.emitted('items-per-page-change')[0]).toEqual([20])
  })
})

