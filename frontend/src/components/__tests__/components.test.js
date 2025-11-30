/**
 * Tests unitarios para componentes Vue de CacaoScan.
 */
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import { describe, it, expect, beforeEach, vi } from 'vitest'

// Importar componentes principales
import LoginForm from '../components/auth/LoginForm.vue'
import RegisterForm from '../components/auth/RegisterForm.vue'
import ImageUploader from '../components/analysis/ImageUploader.vue'
import AnalysisSummaryCard from '../components/analysis/AnalysisSummaryCard.vue'
import StatsCard from '../components/analisis/StatsCard.vue'
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
vi.mock('../services/api.js', () => ({
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
    { path: '/register', component: RegisterForm },
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
    
    await emailInput.setValue('test@example.com')
    await passwordInput.setValue('password123')
    
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

describe('RegisterForm', () => {
  let wrapper

  beforeEach(() => {
    wrapper = createWrapper(RegisterForm)
  })

  it('renderiza correctamente', () => {
    expect(wrapper.find('form').exists()).toBe(true)
    expect(wrapper.find('input[name="username"]').exists()).toBe(true)
    expect(wrapper.find('input[name="email"]').exists()).toBe(true)
    expect(wrapper.find('input[name="password"]').exists()).toBe(true)
    expect(wrapper.find('input[name="passwordConfirm"]').exists()).toBe(true)
  })

  it('valida que las contraseñas coincidan', async () => {
    const passwordInput = wrapper.find('input[name="password"]')
    const passwordConfirmInput = wrapper.find('input[name="passwordConfirm"]')
    
    await passwordInput.setValue('password123')
    await passwordConfirmInput.setValue('different123')
    
    const form = wrapper.find('form')
    await form.trigger('submit')
    
    expect(wrapper.text()).toContain('Las contraseñas no coinciden')
  })

  it('valida formato de email', async () => {
    const emailInput = wrapper.find('input[name="email"]')
    
    await emailInput.setValue('invalid-email')
    
    const form = wrapper.find('form')
    await form.trigger('submit')
    
    expect(wrapper.text()).toContain('Email inválido')
  })

  it('envía datos de registro correctamente', async () => {
    const usernameInput = wrapper.find('input[name="username"]')
    const emailInput = wrapper.find('input[name="email"]')
    const passwordInput = wrapper.find('input[name="password"]')
    const passwordConfirmInput = wrapper.find('input[name="passwordConfirm"]')
    
    await usernameInput.setValue('testuser')
    await emailInput.setValue('test@example.com')
    await passwordInput.setValue('password123')
    await passwordConfirmInput.setValue('password123')
    
    const form = wrapper.find('form')
    await form.trigger('submit')
    
    expect(wrapper.emitted('register')).toBeTruthy()
  })
})

describe('ImageUploader', () => {
  let wrapper

  beforeEach(() => {
    wrapper = createWrapper(ImageUploader)
  })

  it('renderiza correctamente', () => {
    expect(wrapper.find('input[type="file"]').exists()).toBe(true)
    expect(wrapper.find('.upload-area').exists()).toBe(true)
  })

  it('maneja selección de archivo', async () => {
    const fileInput = wrapper.find('input[type="file"]')
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    
    await fileInput.setValue(file)
    
    expect(wrapper.emitted('file-selected')).toBeTruthy()
  })

  it('valida tipo de archivo', async () => {
    const fileInput = wrapper.find('input[type="file"]')
    const file = new File(['test'], 'test.txt', { type: 'text/plain' })
    
    await fileInput.setValue(file)
    
    expect(wrapper.text()).toContain('Solo se permiten archivos de imagen')
  })

  it('valida tamaño de archivo', async () => {
    // Mock de archivo grande
    const largeFile = new File(['x'.repeat(10 * 1024 * 1024)], 'large.jpg', { type: 'image/jpeg' })
    
    await wrapper.setData({ maxFileSize: 5 * 1024 * 1024 }) // 5MB
    
    const fileInput = wrapper.find('input[type="file"]')
    await fileInput.setValue(largeFile)
    
    expect(wrapper.text()).toContain('El archivo es demasiado grande')
  })

  it('muestra preview de imagen', async () => {
    const fileInput = wrapper.find('input[type="file"]')
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    
    await fileInput.setValue(file)
    
    expect(wrapper.find('.image-preview').exists()).toBe(true)
  })
})

describe('AnalysisSummaryCard', () => {
  let wrapper

  beforeEach(() => {
    wrapper = createWrapper(AnalysisSummaryCard, {
      props: {
        analysis: {
          id: 1,
          quality_score: 85.5,
          maturity_percentage: 75.0,
          defects_count: 2,
          created_at: '2024-01-01T10:00:00Z'
        }
      }
    })
  })

  it('renderiza correctamente', () => {
    expect(wrapper.find('.analysis-card').exists()).toBe(true)
    expect(wrapper.text()).toContain('85.5')
    expect(wrapper.text()).toContain('75.0')
    expect(wrapper.text()).toContain('2')
  })

  it('muestra estado de calidad correcto', () => {
    expect(wrapper.find('.quality-excellent').exists()).toBe(true)
  })

  it('emite evento al hacer clic', async () => {
    await wrapper.find('.analysis-card').trigger('click')
    
    expect(wrapper.emitted('click')).toBeTruthy()
  })

  it('formatea fecha correctamente', () => {
    expect(wrapper.text()).toContain('01/01/2024')
  })
})

describe('StatsCard', () => {
  let wrapper

  beforeEach(() => {
    wrapper = createWrapper(StatsCard, {
      props: {
        title: 'Total Análisis',
        value: 150,
        icon: 'chart-bar',
        trend: 'up',
        trendValue: 12.5
      }
    })
  })

  it('renderiza correctamente', () => {
    expect(wrapper.text()).toContain('Total Análisis')
    expect(wrapper.text()).toContain('150')
    expect(wrapper.text()).toContain('12.5%')
  })

  it('muestra tendencia positiva', () => {
    expect(wrapper.find('.trend-up').exists()).toBe(true)
  })

  it('muestra tendencia negativa', async () => {
    await wrapper.setProps({ trend: 'down', trendValue: -5.2 })
    
    expect(wrapper.find('.trend-down').exists()).toBe(true)
  })

  it('formatea números grandes', async () => {
    await wrapper.setProps({ value: 1500 })
    
    expect(wrapper.text()).toContain('1.5K')
  })
})

describe('NotificationBell', () => {
  let wrapper

  beforeEach(() => {
    wrapper = createWrapper(NotificationBell, {
      props: {
        unreadCount: 5
      }
    })
  })

  it('renderiza correctamente', () => {
    expect(wrapper.find('.notification-bell').exists()).toBe(true)
    expect(wrapper.find('.badge').exists()).toBe(true)
  })

  it('muestra conteo de no leídas', () => {
    expect(wrapper.find('.badge').text()).toBe('5')
  })

  it('oculta badge cuando no hay notificaciones', async () => {
    await wrapper.setProps({ unreadCount: 0 })
    
    expect(wrapper.find('.badge').exists()).toBe(false)
  })

  it('abre centro de notificaciones', async () => {
    await wrapper.find('.notification-bell').trigger('click')
    
    expect(wrapper.emitted('toggle-center')).toBeTruthy()
  })
})

describe('LoadingSpinner', () => {
  let wrapper

  beforeEach(() => {
    wrapper = createWrapper(LoadingSpinner, {
      props: {
        size: 'large',
        text: 'Cargando...'
      }
    })
  })

  it('renderiza correctamente', () => {
    expect(wrapper.find('.spinner').exists()).toBe(true)
    expect(wrapper.text()).toContain('Cargando...')
  })

  it('aplica tamaño correcto', () => {
    expect(wrapper.find('.spinner-large').exists()).toBe(true)
  })

  it('muestra texto personalizado', () => {
    expect(wrapper.text()).toContain('Cargando...')
  })
})

describe('ErrorAlert', () => {
  let wrapper

  beforeEach(() => {
    wrapper = createWrapper(ErrorAlert, {
      props: {
        message: 'Error de prueba',
        type: 'error'
      }
    })
  })

  it('renderiza correctamente', () => {
    expect(wrapper.find('.alert').exists()).toBe(true)
    expect(wrapper.text()).toContain('Error de prueba')
  })

  it('aplica tipo correcto', () => {
    expect(wrapper.find('.alert-error').exists()).toBe(true)
  })

  it('emite evento al cerrar', async () => {
    await wrapper.find('.close-btn').trigger('click')
    
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('se cierra automáticamente', async () => {
    await wrapper.setProps({ autoClose: true, duration: 100 })
    
    // Esperar que se cierre automáticamente
    await new Promise(resolve => setTimeout(resolve, 150))
    
    expect(wrapper.emitted('close')).toBeTruthy()
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

describe('PageHeader', () => {
  let wrapper

  beforeEach(() => {
    wrapper = createWrapper(PageHeader, {
      props: {
        title: 'Página de Prueba',
        subtitle: 'Subtítulo de prueba',
        showBackButton: true
      }
    })
  })

  it('renderiza correctamente', () => {
    expect(wrapper.text()).toContain('Página de Prueba')
    expect(wrapper.text()).toContain('Subtítulo de prueba')
    expect(wrapper.find('.back-btn').exists()).toBe(true)
  })

  it('emite evento al hacer clic en botón de regreso', async () => {
    await wrapper.find('.back-btn').trigger('click')
    
    expect(wrapper.emitted('back')).toBeTruthy()
  })

  it('muestra breadcrumbs', async () => {
    await wrapper.setProps({
      breadcrumbs: [
        { text: 'Inicio', to: '/' },
        { text: 'Análisis', to: '/analisis' },
        { text: 'Actual', active: true }
      ]
    })
    
    expect(wrapper.find('.breadcrumbs').exists()).toBe(true)
  })
})

describe('QuickActions', () => {
  let wrapper

  beforeEach(() => {
    wrapper = createWrapper(QuickActions)
  })

  it('renderiza correctamente', () => {
    expect(wrapper.find('.quick-actions').exists()).toBe(true)
  })

  it('muestra acciones disponibles', () => {
    expect(wrapper.find('.action-item').exists()).toBe(true)
  })

  it('emite evento al hacer clic en acción', async () => {
    await wrapper.find('.action-item').trigger('click')
    
    expect(wrapper.emitted('action-click')).toBeTruthy()
  })
})

describe('RecentAnalyses', () => {
  let wrapper

  beforeEach(() => {
    wrapper = createWrapper(RecentAnalyses, {
      props: {
        analyses: [
          {
            id: 1,
            filename: 'test1.jpg',
            quality_score: 85.5,
            created_at: '2024-01-01T10:00:00Z'
          },
          {
            id: 2,
            filename: 'test2.jpg',
            quality_score: 92.0,
            created_at: '2024-01-02T10:00:00Z'
          }
        ]
      }
    })
  })

  it('renderiza correctamente', () => {
    expect(wrapper.find('.recent-analyses').exists()).toBe(true)
    expect(wrapper.findAll('.analysis-item')).toHaveLength(2)
  })

  it('muestra análisis recientes', () => {
    expect(wrapper.text()).toContain('test1.jpg')
    expect(wrapper.text()).toContain('test2.jpg')
  })

  it('emite evento al hacer clic en análisis', async () => {
    await wrapper.find('.analysis-item').trigger('click')
    
    expect(wrapper.emitted('analysis-click')).toBeTruthy()
  })
})

describe('StatsOverview', () => {
  let wrapper

  beforeEach(() => {
    wrapper = createWrapper(StatsOverview, {
      props: {
        stats: {
          totalAnalyses: 150,
          averageQuality: 85.5,
          totalImages: 200,
          successRate: 95.2
        }
      }
    })
  })

  it('renderiza correctamente', () => {
    expect(wrapper.find('.stats-overview').exists()).toBe(true)
    expect(wrapper.text()).toContain('150')
    expect(wrapper.text()).toContain('85.5')
    expect(wrapper.text()).toContain('200')
    expect(wrapper.text()).toContain('95.2')
  })

  it('muestra todas las estadísticas', () => {
    expect(wrapper.findAll('.stat-card')).toHaveLength(4)
  })
})

describe('BarChart', () => {
  let wrapper

  beforeEach(() => {
    wrapper = createWrapper(BarChart, {
      props: {
        data: {
          labels: ['Enero', 'Febrero', 'Marzo'],
          datasets: [{
            label: 'Análisis',
            data: [10, 20, 15]
          }]
        },
        options: {
          responsive: true
        }
      }
    })
  })

  it('renderiza correctamente', () => {
    expect(wrapper.find('.chart-container').exists()).toBe(true)
  })

  it('actualiza datos correctamente', async () => {
    await wrapper.setProps({
      data: {
        labels: ['Abril', 'Mayo', 'Junio'],
        datasets: [{
          label: 'Análisis',
          data: [25, 30, 20]
        }]
      }
    })
    
    expect(wrapper.vm.chartData).toEqual(wrapper.props('data'))
  })
})

describe('LineChart', () => {
  let wrapper

  beforeEach(() => {
    wrapper = createWrapper(LineChart, {
      props: {
        data: {
          labels: ['Enero', 'Febrero', 'Marzo'],
          datasets: [{
            label: 'Tendencia',
            data: [10, 20, 15]
          }]
        }
      }
    })
  })

  it('renderiza correctamente', () => {
    expect(wrapper.find('.chart-container').exists()).toBe(true)
  })

  it('muestra línea de tendencia', () => {
    expect(wrapper.vm.chartType).toBe('line')
  })
})

describe('PieChart', () => {
  let wrapper

  beforeEach(() => {
    wrapper = createWrapper(PieChart, {
      props: {
        data: {
          labels: ['Excelente', 'Bueno', 'Regular'],
          datasets: [{
            data: [60, 30, 10]
          }]
        }
      }
    })
  })

  it('renderiza correctamente', () => {
    expect(wrapper.find('.chart-container').exists()).toBe(true)
  })

  it('muestra gráfico de pastel', () => {
    expect(wrapper.vm.chartType).toBe('pie')
  })
})
