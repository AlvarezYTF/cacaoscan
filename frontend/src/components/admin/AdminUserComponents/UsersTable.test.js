import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import UsersTable from './UsersTable.vue'

vi.mock('@/components/common/BaseSpinner.vue', () => ({
  default: {
    name: 'BaseSpinner',
    template: '<div>Loading...</div>',
    props: ['size', 'color']
  }
}))

describe('UsersTable', () => {
  const mockUsers = [
    {
      id: 1,
      username: 'user1',
      email: 'user1@test.com',
      first_name: 'John',
      last_name: 'Doe',
      role: 'Administrador',
      is_active: true,
      last_login: '2024-01-01T12:00:00',
      date_joined: '2024-01-01T10:00:00',
      is_superuser: false
    },
    {
      id: 2,
      username: 'user2',
      email: 'user2@test.com',
      first_name: 'Jane',
      last_name: 'Smith',
      role: 'Agricultor',
      is_active: false,
      last_login: null,
      date_joined: '2024-01-02T10:00:00',
      is_superuser: false
    }
  ]

  it('should render users table', () => {
    const wrapper = mount(UsersTable, {
      props: {
        users: mockUsers,
        selectedUsers: [],
        loading: false
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display loading state', () => {
    const wrapper = mount(UsersTable, {
      props: {
        users: [],
        selectedUsers: [],
        loading: true
      }
    })

    expect(wrapper.text().includes('Cargando usuarios')).toBe(true)
  })

  it('should display empty state when no users', () => {
    const wrapper = mount(UsersTable, {
      props: {
        users: [],
        selectedUsers: [],
        loading: false
      }
    })

    expect(wrapper.text().includes('No se encontraron usuarios')).toBe(true)
  })

  it('should display all users', () => {
    const wrapper = mount(UsersTable, {
      props: {
        users: mockUsers,
        selectedUsers: [],
        loading: false
      }
    })

    expect(wrapper.text().includes('John Doe')).toBe(true)
    expect(wrapper.text().includes('Jane Smith')).toBe(true)
  })

  it('should emit toggle-select-all event', async () => {
    const wrapper = mount(UsersTable, {
      props: {
        users: mockUsers,
        selectedUsers: [],
        loading: false
      }
    })

    await wrapper.vm.handleToggleSelectAll()

    expect(wrapper.emitted('toggle-select-all')).toBeTruthy()
  })

  it('should emit toggle-user-select event', async () => {
    const wrapper = mount(UsersTable, {
      props: {
        users: mockUsers,
        selectedUsers: [],
        loading: false
      }
    })

    await wrapper.vm.handleToggleUserSelect(1)

    expect(wrapper.emitted('toggle-user-select')).toBeTruthy()
    expect(wrapper.emitted('toggle-user-select')[0]).toEqual([1])
  })

  it('should emit toggle-status event', async () => {
    const wrapper = mount(UsersTable, {
      props: {
        users: mockUsers,
        selectedUsers: [],
        loading: false
      }
    })

    await wrapper.vm.handleToggleStatus(mockUsers[0])

    expect(wrapper.emitted('toggle-status')).toBeTruthy()
  })

  it('should emit view-user event', async () => {
    const wrapper = mount(UsersTable, {
      props: {
        users: mockUsers,
        selectedUsers: [],
        loading: false
      }
    })

    await wrapper.vm.handleViewUser(mockUsers[0])

    expect(wrapper.emitted('view-user')).toBeTruthy()
  })

  it('should emit edit-user event', async () => {
    const wrapper = mount(UsersTable, {
      props: {
        users: mockUsers,
        selectedUsers: [],
        loading: false
      }
    })

    await wrapper.vm.handleEditUser(mockUsers[0])

    expect(wrapper.emitted('edit-user')).toBeTruthy()
  })

  it('should emit view-activity event', async () => {
    const wrapper = mount(UsersTable, {
      props: {
        users: mockUsers,
        selectedUsers: [],
        loading: false
      }
    })

    await wrapper.vm.handleViewActivity(mockUsers[0])

    expect(wrapper.emitted('view-activity')).toBeTruthy()
  })

  it('should emit delete-user event', async () => {
    const wrapper = mount(UsersTable, {
      props: {
        users: mockUsers,
        selectedUsers: [],
        loading: false
      }
    })

    await wrapper.vm.handleDeleteUser(mockUsers[0])

    expect(wrapper.emitted('delete-user')).toBeTruthy()
  })

  it('should emit export event', async () => {
    const wrapper = mount(UsersTable, {
      props: {
        users: mockUsers,
        selectedUsers: [],
        loading: false
      }
    })

    await wrapper.vm.handleExport()

    expect(wrapper.emitted('export')).toBeTruthy()
  })

  it('should format date correctly', () => {
    const wrapper = mount(UsersTable, {
      props: {
        users: mockUsers,
        selectedUsers: [],
        loading: false
      }
    })

    const date = new Date('2024-01-01T12:00:00')
    const formatted = wrapper.vm.formatDate(date)

    expect(formatted).toBeTruthy()
  })

  it('should format date time correctly', () => {
    const wrapper = mount(UsersTable, {
      props: {
        users: mockUsers,
        selectedUsers: [],
        loading: false
      }
    })

    const date = new Date('2024-01-01T12:00:00')
    const formatted = wrapper.vm.formatDateTime(date)

    expect(formatted).toBeTruthy()
  })

  it('should return correct role badge class', () => {
    const wrapper = mount(UsersTable, {
      props: {
        users: mockUsers,
        selectedUsers: [],
        loading: false
      }
    })

    expect(wrapper.vm.getRoleBadgeClass('Administrador')).toBe('bg-purple-100 text-purple-800')
    expect(wrapper.vm.getRoleBadgeClass('Agricultor')).toBe('bg-green-100 text-green-800')
    expect(wrapper.vm.getRoleBadgeClass('Técnico')).toBe('bg-blue-100 text-blue-800')
    expect(wrapper.vm.getRoleBadgeClass('Unknown')).toBe('bg-gray-100 text-gray-800')
  })

  it('should compute selectAll correctly when all selected', () => {
    const wrapper = mount(UsersTable, {
      props: {
        users: mockUsers,
        selectedUsers: [1, 2],
        loading: false
      }
    })

    expect(wrapper.vm.selectAll).toBe(true)
  })

  it('should compute selectAll correctly when not all selected', () => {
    const wrapper = mount(UsersTable, {
      props: {
        users: mockUsers,
        selectedUsers: [1],
        loading: false
      }
    })

    expect(wrapper.vm.selectAll).toBe(false)
  })

  it('should compute selectAll correctly when no users', () => {
    const wrapper = mount(UsersTable, {
      props: {
        users: [],
        selectedUsers: [],
        loading: false
      }
    })

    expect(wrapper.vm.selectAll).toBe(false)
  })

  it('should display "Nunca" when user has no last_login', () => {
    const wrapper = mount(UsersTable, {
      props: {
        users: [mockUsers[1]],
        selectedUsers: [],
        loading: false
      }
    })

    expect(wrapper.text().includes('Nunca')).toBe(true)
  })

  it('should disable delete button for superuser', () => {
    const superuser = { ...mockUsers[0], is_superuser: true }
    const wrapper = mount(UsersTable, {
      props: {
        users: [superuser],
        selectedUsers: [],
        loading: false
      }
    })

    const deleteButtons = wrapper.findAll('button[title="Eliminar"]')
    if (deleteButtons.length > 0) {
      expect(deleteButtons[0].attributes('disabled')).toBeDefined()
    }
  })
})

