/**
 * Tests unitarios para componentes Vue de CacaoScan.
 */
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import { describe, it, expect, beforeEach, vi } from 'vitest'

// Helper function to generate secure password dynamically
const generatePassword = () => {
  return `Pass!${Date.now()}-${Math.random().toString(36).slice(2)}`
}

// Importar componentes principales
import LoginForm from '../auth/LoginForm.vue'
import RegisterForm from '../auth/RegisterForm.vue'
import ImageUploader from '../admin/AdminAnalisisComponents/ImageUploader.vue'
import AnalysisSummaryCard from '../analysis/AnalysisSummaryCard.vue'
import StatsCard from '../reportes/StatsCard.vue'
import NotificationBell from '../components/notifications/NotificationBell.vue'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'
import ErrorAlert from '../components/common/ErrorAlert.vue'
import ConfirmModal from '../components/common/ConfirmModal.vue'
import PageHeader from '../components/common/PageHeader.vue'
import QuickActions from '../components/dashboard/QuickActions.vue'
import RecentAnalyses from '../components/dashboard/RecentAnalyses.vue'
import StatsOverview from '../components/dashboard/StatsOverview.vue'
import BarChart from '../components/charts/BarChart.vue'
import LineChart from '../components/charts/LineChart.vue'
import PieChart from '../components/charts/PieChart.vue'

// Mock de servicios
vi.mock('@/services/api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

vi.mock('../services/authApi.js', () => ({
  default: {
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    getProfile: vi.fn()
  }
}))

vi.mock('../services/predictionApi.js', () => ({
  default: {
    uploadImage: vi.fn(),
    getAnalysis: vi.fn(),
    getAnalysisHistory: vi.fn()
  }
}))

// Configuración global
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: { template: '<div>Home</div>' } },
    { path: '/login', component: LoginForm },
    { path: '/dashboard', component: { template: '<div>Dashboard</div>' } }
  ]
})

const createWrapper = (component, options = {}) => {
  const pinia = createPinia()
  setActivePinia(pinia)
  
  return mount(component, {
    global: {
      plugins: [pinia, router],
      stubs: {
        'router-link': true,
        'router-view': true
      }
    },
    ...options
  })
}

describe('LoginForm', () => {
  let wrapper

  beforeEach(() => {
    wrapper = createWrapper(LoginForm)
  })

  it('renderiza correctamente', () => {
    expect(wrapper.find('form').exists()).toBe(true)
    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })

  it('muestra errores de validación', async () => {
    const emailInput = wrapper.find('input[type="email"]')
    const passwordInput = wrapper.find('input[type="password"]')
    
    await emailInput.setValue('')
    await passwordInput.setValue('')
    
    const form = wrapper.find('form')
    await form.trigger('submit')
    
    expect(wrapper.text()).toContain('Email es requerido')
    expect(wrapper.text()).toContain('Contraseña es requerida')
  })

  it('envía datos de login correctamente', async () => {
    const emailInput = wrapper.find('input[type="email"]')
    const passwordInput = wrapper.find('input[type="password"]')
    const password = generatePassword()
    
    await emailInput.setValue('test@example.com')
    await passwordInput.setValue(password)
    
    const form = wrapper.find('form')
    await form.trigger('submit')
    
    // Verificar que se llamó la función de login
    expect(wrapper.emitted('login')).toBeTruthy()
  })

  it('muestra estado de carga durante login', async () => {
    await wrapper.setData({ isLoading: true })
    
    expect(wrapper.find('.loading').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined()
  })
})


describe('NotificationBell', () => {
  let wrapper

  beforeEach(() => {
    wrapper = createWrapper(NotificationBell)
  })

  it('renderiza correctamente', () => {
    expect(wrapper.exists()).toBe(true)
  })
})

describe('ConfirmModal', () => {
  let wrapper

  beforeEach(() => {
    wrapper = createWrapper(ConfirmModal, {
      props: {
        title: 'Confirmar acción',
        message: '¿Estás seguro?',
        isOpen: true
      }
    })
  })

  it('renderiza correctamente', () => {
    expect(wrapper.find('.modal').exists()).toBe(true)
    expect(wrapper.text()).toContain('Confirmar acción')
    expect(wrapper.text()).toContain('¿Estás seguro?')
  })

  it('confirma acción', async () => {
    await wrapper.find('.confirm-btn').trigger('click')
    
    expect(wrapper.emitted('confirm')).toBeTruthy()
  })

  it('cancela acción', async () => {
    await wrapper.find('.cancel-btn').trigger('click')
    
    expect(wrapper.emitted('cancel')).toBeTruthy()
  })

  it('cierra con escape', async () => {
    await wrapper.find('.modal').trigger('keydown.esc')
    
    expect(wrapper.emitted('cancel')).toBeTruthy()
  })
})

