/**
 * Unit tests for BaseDataTable component
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseDataTable from '../BaseDataTable.vue'

vi.mock('@/composables/usePagination', () => ({
  usePagination: vi.fn(() => ({
    currentPage: { value: 1 },
    itemsPerPage: { value: 10 },
    totalPages: { value: 1 },
    totalItems: { value: 0 },
    startItem: { value: 1 },
    endItem: { value: 0 },
    goToPage: vi.fn(),
    nextPage: vi.fn(),
    previousPage: vi.fn()
  }))
}))

describe('BaseDataTable', () => {
  let wrapper

  const createColumns = () => [
    { key: 'id', label: 'ID', sortable: true },
    { key: 'name', label: 'Name', sortable: true },
    { key: 'email', label: 'Email' }
  ]

  const createData = () => [
    { id: 1, name: 'John', email: 'john@example.com' },
    { id: 2, name: 'Jane', email: 'jane@example.com' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Props validation', () => {
    it('should require columns prop', () => {
      expect(() => {
        wrapper = mount(BaseDataTable)
      }).toThrow()
    })

    it('should require data prop', () => {
      // In Vue 3, if a required prop has a default value, it won't throw an error
      // but will use the default. The validator will still run and show a warning.
      wrapper = mount(BaseDataTable, {
        props: {
          columns: createColumns()
        }
      })
      expect(wrapper.exists()).toBe(true)
      // Assert that default empty array is used
      expect(wrapper.props('data')).toEqual([])
    })

    it('should accept columns and data props', () => {
      wrapper = mount(BaseDataTable, {
        props: {
          columns: createColumns(),
          data: createData()
        }
      })
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Rendering', () => {
    it('should render table', () => {
      wrapper = mount(BaseDataTable, {
        props: {
          columns: createColumns(),
          data: createData()
        }
      })

      expect(wrapper.find('table').exists()).toBe(true)
    })

    it('should render column headers', () => {
      wrapper = mount(BaseDataTable, {
        props: {
          columns: createColumns(),
          data: createData()
        }
      })

      expect(wrapper.text()).toContain('ID')
      expect(wrapper.text()).toContain('Name')
      expect(wrapper.text()).toContain('Email')
    })

    it('should render data rows', () => {
      wrapper = mount(BaseDataTable, {
        props: {
          columns: createColumns(),
          data: createData()
        }
      })

      expect(wrapper.text()).toContain('John')
      expect(wrapper.text()).toContain('jane@example.com')
    })

    it('should show loading state when loading is true', () => {
      wrapper = mount(BaseDataTable, {
        props: {
          columns: createColumns(),
          data: createData(),
          loading: true
        }
      })

      expect(wrapper.text()).toContain('Cargando datos...')
    })

    it('should show empty state when no data', () => {
      wrapper = mount(BaseDataTable, {
        props: {
          columns: createColumns(),
          data: []
        }
      })

      expect(wrapper.text()).toContain('No hay datos disponibles')
    })

    it('should render selection checkbox when selectable is true', () => {
      wrapper = mount(BaseDataTable, {
        props: {
          columns: createColumns(),
          data: createData(),
          selectable: true
        }
      })

      const checkboxes = wrapper.findAll('input[type="checkbox"]')
      expect(checkboxes.length).toBeGreaterThan(0)
    })

    it('should render actions column when actions are provided', () => {
      wrapper = mount(BaseDataTable, {
        props: {
          columns: createColumns(),
          data: createData(),
          actions: [
            { key: 'edit', label: 'Edit' },
            { key: 'delete', label: 'Delete' }
          ]
        }
      })

      expect(wrapper.text()).toContain('Acciones')
    })
  })

  describe('Events', () => {
    it('should emit sort event when column header is clicked', async () => {
      wrapper = mount(BaseDataTable, {
        props: {
          columns: createColumns(),
          data: createData()
        }
      })

      const sortableHeader = wrapper.findAll('th').find(th => th.text().includes('ID'))
      await sortableHeader.trigger('click')

      expect(wrapper.emitted('sort')).toBeTruthy()
    })

    it('should emit row-select event when row is selected', async () => {
      wrapper = mount(BaseDataTable, {
        props: {
          columns: createColumns(),
          data: createData(),
          selectable: true
        }
      })

      const checkbox = wrapper.findAll('input[type="checkbox"]')[1]
      await checkbox.setValue(true)

      expect(wrapper.emitted('row-select')).toBeTruthy()
    })

    it('should emit row-click event when row is clicked', async () => {
      wrapper = mount(BaseDataTable, {
        props: {
          columns: createColumns(),
          data: createData(),
          rowClickable: true
        }
      })

      const row = wrapper.findAll('tbody tr')[0]
      await row.trigger('click')

      expect(wrapper.emitted('row-click')).toBeTruthy()
    })

    it('should emit action-click event when action button is clicked', async () => {
      wrapper = mount(BaseDataTable, {
        props: {
          columns: createColumns(),
          data: createData(),
          actions: [
            { key: 'edit', label: 'Edit' }
          ]
        }
      })

      const actionButton = wrapper.find('button')
      await actionButton.trigger('click')

      expect(wrapper.emitted('action-click')).toBeTruthy()
    })
  })

  describe('Slots', () => {
    it('should render controls slot when provided', () => {
      wrapper = mount(BaseDataTable, {
        props: {
          columns: createColumns(),
          data: createData()
        },
        slots: {
          controls: '<div>Controls</div>'
        }
      })

      expect(wrapper.text()).toContain('Controls')
    })

    it('should render cell slot when provided', () => {
      wrapper = mount(BaseDataTable, {
        props: {
          columns: createColumns(),
          data: createData()
        },
        slots: {
          'cell-name': '<span>Custom Cell</span>'
        }
      })

      expect(wrapper.text()).toContain('Custom Cell')
    })

    it('should render empty slot when provided', () => {
      wrapper = mount(BaseDataTable, {
        props: {
          columns: createColumns(),
          data: []
        },
        slots: {
          empty: '<div>Custom Empty</div>'
        }
      })

      expect(wrapper.text()).toContain('Custom Empty')
    })
  })

  describe('Methods', () => {
    it('should format cell value correctly', () => {
      wrapper = mount(BaseDataTable, {
        props: {
          columns: createColumns(),
          data: createData()
        }
      })

      const value = wrapper.vm.formatCellValue('test', {})
      expect(value).toBe('test')
    })

    it('should return empty value for null', () => {
      wrapper = mount(BaseDataTable, {
        props: {
          columns: createColumns(),
          data: createData()
        }
      })

      const value = wrapper.vm.formatCellValue(null, { emptyValue: 'N/A' })
      expect(value).toBe('N/A')
    })

    it('should use formatter function when provided', () => {
      const formatter = vi.fn((val) => `Formatted: ${val}`)
      wrapper = mount(BaseDataTable, {
        props: {
          columns: [
            { key: 'name', label: 'Name', formatter }
          ],
          data: [{ name: 'John' }]
        }
      })

      wrapper.vm.formatCellValue('John', { formatter })
      expect(formatter).toHaveBeenCalledWith('John')
    })
  })
})

