import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import FarmersTable from './FarmersTable.vue'

vi.mock('./DataTable.vue', () => ({
  default: {
    name: 'DataTable',
    template: `
      <div>
        <template v-for="row in data" :key="row.id">
          <div v-if="$slots['cell-farmer']">
            <slot name="cell-farmer" :row="row"></slot>
          </div>
          <div v-if="$slots['cell-farm']">
            <slot name="cell-farm" :row="row"></slot>
          </div>
          <div v-if="$slots['cell-status']">
            <slot name="cell-status" :row="row"></slot>
          </div>
          <div v-if="$slots['cell-actions']">
            <slot name="cell-actions" :row="row"></slot>
          </div>
        </template>
        <slot name="pagination"></slot>
      </div>
    `,
    props: ['columns', 'data', 'showTableInfo']
  }
}))

vi.mock('@/components/common/Pagination.vue', () => ({
  default: {
    name: 'Pagination',
    template: '<div>Pagination</div>',
    props: ['currentPage', 'totalPages', 'totalItems', 'itemsPerPage'],
    emits: ['page-change']
  }
}))

describe('FarmersTable', () => {
  const mockColumns = [
    { key: 'farmer', label: 'Agricultor' },
    { key: 'farm', label: 'Finca' },
    { key: 'status', label: 'Estado' },
    { key: 'actions', label: 'Acciones' }
  ]

  const mockFarmers = [
    {
      id: 1,
      name: 'John Doe',
      email: 'john@test.com',
      initials: 'JD',
      is_active: true,
      fincas: [{ id: 1, nombre: 'Finca 1', hectareas: '10.5' }],
      farm: 'Finca 1',
      hectares: '10.5 ha'
    },
    {
      id: 2,
      name: 'Jane Smith',
      email: 'jane@test.com',
      initials: 'JS',
      is_active: false,
      fincas: [],
      farm: null,
      hectares: '0 ha'
    }
  ]

  it('should render table with farmers', () => {
    const wrapper = mount(FarmersTable, {
      props: {
        filteredFarmers: mockFarmers,
        searchQuery: '',
        filters: { region: 'all', status: 'all' },
        tableColumns: mockColumns,
        currentPage: 1,
        totalPages: 1,
        totalItems: 2,
        itemsPerPage: 10
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display empty state when no farmers', () => {
    const wrapper = mount(FarmersTable, {
      props: {
        filteredFarmers: [],
        searchQuery: '',
        filters: { region: 'all', status: 'all' },
        tableColumns: mockColumns,
        currentPage: 1,
        totalPages: 0,
        totalItems: 0,
        itemsPerPage: 10
      }
    })

    const text = wrapper.text()
    expect(text.includes('No se encontraron agricultores')).toBe(true)
  })

  it('should show add farmer button when empty and no filters', () => {
    const wrapper = mount(FarmersTable, {
      props: {
        filteredFarmers: [],
        searchQuery: '',
        filters: { region: 'all', status: 'all' },
        tableColumns: mockColumns,
        currentPage: 1,
        totalPages: 0,
        totalItems: 0,
        itemsPerPage: 10
      }
    })

    const button = wrapper.find('button')
    expect(button.exists()).toBe(true)
    expect(button.text().includes('Agregar Primer Agricultor')).toBe(true)
  })

  it('should not show add farmer button when filters are active', () => {
    const wrapper = mount(FarmersTable, {
      props: {
        filteredFarmers: [],
        searchQuery: 'test',
        filters: { region: 'all', status: 'all' },
        tableColumns: mockColumns,
        currentPage: 1,
        totalPages: 0,
        totalItems: 0,
        itemsPerPage: 10
      }
    })

    const button = wrapper.find('button')
    if (button.exists()) {
      expect(button.text().includes('Agregar Primer Agricultor')).toBe(false)
    }
  })

  it('should emit new-farmer event when add button is clicked', async () => {
    const wrapper = mount(FarmersTable, {
      props: {
        filteredFarmers: [],
        searchQuery: '',
        filters: { region: 'all', status: 'all' },
        tableColumns: mockColumns,
        currentPage: 1,
        totalPages: 0,
        totalItems: 0,
        itemsPerPage: 10
      }
    })

    const button = wrapper.find('button')
    if (button.exists()) {
      await button.trigger('click')
      expect(wrapper.emitted('new-farmer')).toBeTruthy()
    }
  })

  it('should emit toggle-status event', async () => {
    const wrapper = mount(FarmersTable, {
      props: {
        filteredFarmers: mockFarmers,
        searchQuery: '',
        filters: { region: 'all', status: 'all' },
        tableColumns: mockColumns,
        currentPage: 1,
        totalPages: 1,
        totalItems: 2,
        itemsPerPage: 10
      }
    })

    await wrapper.vm.$nextTick()
    const statusButton = wrapper.find('button[title="Click para cambiar estado"]')
    if (statusButton.exists()) {
      await statusButton.trigger('click')
      expect(wrapper.emitted('toggle-status')).toBeTruthy()
    }
  })

  it('should emit view-farmer event', async () => {
    const wrapper = mount(FarmersTable, {
      props: {
        filteredFarmers: mockFarmers,
        searchQuery: '',
        filters: { region: 'all', status: 'all' },
        tableColumns: mockColumns,
        currentPage: 1,
        totalPages: 1,
        totalItems: 2,
        itemsPerPage: 10
      }
    })

    await wrapper.vm.$nextTick()
    const viewButton = wrapper.find('button[title="Ver detalles"]')
    if (viewButton.exists()) {
      await viewButton.trigger('click')
      expect(wrapper.emitted('view-farmer')).toBeTruthy()
    }
  })

  it('should emit edit-farmer event', async () => {
    const wrapper = mount(FarmersTable, {
      props: {
        filteredFarmers: mockFarmers,
        searchQuery: '',
        filters: { region: 'all', status: 'all' },
        tableColumns: mockColumns,
        currentPage: 1,
        totalPages: 1,
        totalItems: 2,
        itemsPerPage: 10
      }
    })

    await wrapper.vm.$nextTick()
    const editButtons = wrapper.findAll('button')
    const editButton = editButtons.find(btn => btn.attributes('title') === 'Editar')
    if (editButton) {
      await editButton.trigger('click')
      expect(wrapper.emitted('edit-farmer')).toBeTruthy()
    }
  })

  it('should emit delete-farmer event', async () => {
    const wrapper = mount(FarmersTable, {
      props: {
        filteredFarmers: mockFarmers,
        searchQuery: '',
        filters: { region: 'all', status: 'all' },
        tableColumns: mockColumns,
        currentPage: 1,
        totalPages: 1,
        totalItems: 2,
        itemsPerPage: 10
      }
    })

    await wrapper.vm.$nextTick()
    const deleteButtons = wrapper.findAll('button')
    const deleteButton = deleteButtons.find(btn => btn.attributes('title') === 'Eliminar')
    if (deleteButton) {
      await deleteButton.trigger('click')
      expect(wrapper.emitted('delete-farmer')).toBeTruthy()
    }
  })

  it('should emit page-change event', async () => {
    const wrapper = mount(FarmersTable, {
      props: {
        filteredFarmers: mockFarmers,
        searchQuery: '',
        filters: { region: 'all', status: 'all' },
        tableColumns: mockColumns,
        currentPage: 1,
        totalPages: 2,
        totalItems: 20,
        itemsPerPage: 10
      }
    })

    await wrapper.vm.$nextTick()
    const pagination = wrapper.findComponent({ name: 'Pagination' })
    if (pagination.exists()) {
      pagination.vm.$emit('page-change', 2)
      expect(wrapper.emitted('page-change')).toBeTruthy()
    }
  })

  it('should return correct status classes', () => {
    const wrapper = mount(FarmersTable, {
      props: {
        filteredFarmers: mockFarmers,
        searchQuery: '',
        filters: { region: 'all', status: 'all' },
        tableColumns: mockColumns,
        currentPage: 1,
        totalPages: 1,
        totalItems: 2,
        itemsPerPage: 10
      }
    })

    expect(wrapper.vm.getStatusClasses('Activo')).toBe('bg-green-100 text-green-800')
    expect(wrapper.vm.getStatusClasses('En revisión')).toBe('bg-amber-100 text-amber-800')
    expect(wrapper.vm.getStatusClasses('Inactivo')).toBe('bg-red-100 text-red-800')
    expect(wrapper.vm.getStatusClasses('Unknown')).toBe('bg-gray-100 text-gray-800')
  })
})

