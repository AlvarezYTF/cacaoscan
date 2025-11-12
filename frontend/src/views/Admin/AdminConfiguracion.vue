<template>
  <div class="bg-gray-50 min-h-screen">
    <!-- Sidebar -->
    <AdminSidebar 
      :brand-name="brandName"
      :user-name="userName"
      :user-role="userRole"
      :current-route="$route.path"
      :collapsed="isSidebarCollapsed"
      @menu-click="handleMenuClick"
      @logout="handleLogout"
      @toggle-collapse="toggleSidebarCollapse"
    />
    
    <!-- Contenido principal -->
    <div class="p-6 transition-all duration-300" :class="isSidebarCollapsed ? 'sm:ml-20' : 'sm:ml-64'">
      <div class="max-w-7xl mx-auto">
        <!-- Encabezado -->
        <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-8 mb-6">
          <div class="flex items-center">
            <div class="bg-green-100 p-3 rounded-lg mr-4">
              <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
            </div>
            <div>
              <h1 class="text-3xl font-bold text-gray-900">Configuración del Sistema</h1>
              <p class="text-gray-600 mt-1">Administra los parámetros generales, seguridad y modelos ML del sistema CacaoScan</p>
            </div>
          </div>
        </div>

        <!-- Tabs de navegación -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div class="border-b border-gray-200">
            <nav class="-mb-px flex space-x-8 px-6 overflow-x-auto" aria-label="Tabs">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                @click="activeTab = tab.id"
                :class="[
                  activeTab === tab.id
                    ? 'border-green-500 text-green-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                  'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors'
                ]"
              >
                <component :is="tab.icon" v-if="tab.icon" class="w-4 h-4 mr-2 inline" />
                {{ tab.name }}
              </button>
            </nav>
          </div>
          
          <!-- Contenido de las pestañas -->
          <div class="p-6">
            <!-- 1. General -->
            <div v-if="activeTab === 'general'">
              <SectionCard 
                title="Configuración General"
                description="Información básica del sistema y branding institucional"
              >
                <LoadingSkeleton v-if="loading && !generalConfig" :lines="4" />
                
                <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <InputField 
                    v-model="generalConfig.nombre_sistema"
                    label="Nombre del sistema"
                    placeholder="CacaoScan"
                  />
                  <InputField 
                    v-model="generalConfig.email_contacto"
                    label="Correo de contacto"
                    type="email"
                    placeholder="contacto@cacaoscan.com"
                  />
                  <div class="md:col-span-2">
                    <InputField 
                      v-model="generalConfig.lema"
                      label="Lema"
                      placeholder="La mejor plataforma para el control de calidad del cacao"
                    />
                  </div>
                  
                  <div class="md:col-span-2">
                    <label for="logo-upload" class="block text-sm font-medium text-gray-700 mb-2">Logo actual</label>
                    <div class="flex items-center space-x-4">
                      <img v-if="generalConfig.logo_url" :src="generalConfig.logo_url" alt="Logo" class="h-20 w-20 object-contain border border-gray-200 rounded-lg p-2">
                      <input
                        id="logo-upload"
                        type="file"
                        accept="image/*"
                        @change="handleLogoUpload"
                        class="block w-full text-sm text-gray-500
                          file:mr-4 file:py-2 file:px-4
                          file:rounded-lg file:border-0
                          file:text-sm file:font-semibold
                          file:bg-green-50 file:text-green-700
                          hover:file:bg-green-100"
                      />
                    </div>
                  </div>
                </div>

                <div class="flex justify-end mt-6">
                  <button
                    @click="saveGeneralConfig"
                    :disabled="saving"
                    class="inline-flex items-center px-6 py-3 text-sm font-semibold text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
                  >
                    <svg v-if="saving" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <svg v-else class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    {{ saving ? 'Guardando...' : 'Guardar cambios' }}
                  </button>
                </div>
              </SectionCard>
            </div>

            <!-- 2. Usuarios y Roles -->
            <div v-if="activeTab === 'users'">
              <SectionCard 
                title="Usuarios y Roles"
                description="Gestiona los roles y permisos del sistema"
              >
                <div class="space-y-6">
                  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div
                      v-for="role in roles"
                      :key="role.id"
                      class="bg-gray-50 rounded-lg p-4 border border-gray-200"
                    >
                      <div class="flex items-center justify-between mb-2">
                        <h4 class="text-sm font-medium text-gray-900">{{ role.name }}</h4>
                        <span :class="getRoleBadgeClass(role.id)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                          {{ role.active ? 'Activo' : 'Inactivo' }}
                        </span>
                      </div>
                      <p class="text-sm text-gray-600 mb-3">{{ role.description }}</p>
                      <div class="space-y-2">
                        <div v-for="permission in role.permissions" :key="permission">
                          <ToggleSwitch 
                            :model-value="true"
                            :label="permission"
                            :description="`Permiso ${permission}`"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </SectionCard>
            </div>

            <!-- 3. Seguridad -->
            <div v-if="activeTab === 'security'">
              <SectionCard 
                title="Configuración de Seguridad"
                description="Gestión de seguridad, sesiones y autenticación"
              >
                <LoadingSkeleton v-if="loading && !securityConfig" :lines="4" />
                
                <div v-else class="space-y-6">
                  <ToggleSwitch 
                    v-model="securityConfig.recaptcha_enabled"
                    label="Activar reCAPTCHA"
                    description="Protege el sistema contra bots"
                  />
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label for="session-timeout" class="block text-sm font-medium text-gray-700 mb-2">Tiempo máximo de sesión (minutos)</label>
                      <div class="flex items-center space-x-4">
                        <input
                          id="session-timeout"
                          type="range"
                          v-model.number="securityConfig.session_timeout"
                          min="5"
                          max="480"
                          step="5"
                          class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                          style="background: linear-gradient(to right, #10b981 0%, #10b981 var(--value, 50%), #e5e7eb var(--value, 50%), #e5e7eb 100%)"
                          @input="(e) => updateSliderStyle(e.target)"
                        />
                        <span class="text-sm font-medium text-gray-900 w-16">{{ securityConfig.session_timeout }} min</span>
                      </div>
                    </div>
                    
                    <div>
                      <label for="login-attempts" class="block text-sm font-medium text-gray-700 mb-2">Límite de intentos de login</label>
                      <input
                        id="login-attempts"
                        type="number"
                        v-model.number="securityConfig.login_attempts"
                        min="3"
                        max="10"
                        class="block w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-green-500 focus:border-green-500"
                      />
                    </div>
                  </div>

                  <ToggleSwitch 
                    v-model="securityConfig.two_factor_auth"
                    label="Autenticación de dos factores (2FA)"
                    description="Requiere código de verificación para acceder al sistema"
                  />

                  <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <h4 class="text-sm font-medium text-gray-900 mb-2">Último acceso</h4>
                    <p class="text-sm text-gray-600">{{ lastLogin || 'No disponible' }}</p>
                  </div>
                </div>

                <div class="flex justify-end mt-6">
                  <button
                    @click="saveSecurityConfig"
                    :disabled="saving"
                    class="inline-flex items-center px-6 py-3 text-sm font-semibold text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
                  >
                    Actualizar Seguridad
                  </button>
                </div>
              </SectionCard>
            </div>

            <!-- 4. Modelos ML -->
            <div v-if="activeTab === 'ml'">
              <SectionCard 
                title="Modelos de Machine Learning"
                description="Gestión y configuración de modelos de IA"
              >
                <LoadingSkeleton v-if="loading && !mlConfig" :lines="3" />
                
                <div v-else class="space-y-6">
                  <SelectField
                    v-model="mlConfig.active_model"
                    label="Modelo Activo"
                    :options="modelOptions"
                    helper-text="Selecciona el modelo que se usará para las predicciones"
                  />

                  <div v-if="mlConfig.metrics" class="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <h4 class="text-sm font-medium text-gray-900 mb-3">Métricas del Modelo</h4>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <p class="text-xs text-gray-500 mb-1">MAE</p>
                        <p class="text-2xl font-bold text-gray-900">{{ mlConfig.metrics.mae }}</p>
                      </div>
                      <div>
                        <p class="text-xs text-gray-500 mb-1">RMSE</p>
                        <p class="text-2xl font-bold text-gray-900">{{ mlConfig.metrics.rmse }}</p>
                      </div>
                      <div>
                        <p class="text-xs text-gray-500 mb-1">R²</p>
                        <p class="text-2xl font-bold text-gray-900">{{ mlConfig.metrics.r2 }}</p>
                      </div>
                    </div>
                  </div>

                  <div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
                    <div class="flex items-start">
                      <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
                      </svg>
                      <div class="flex-1">
                        <p class="text-sm font-medium text-blue-900">Última actualización</p>
                        <p class="text-sm text-blue-700">{{ mlConfig.last_training || 'No disponible' }}</p>
                      </div>
                    </div>
                  </div>

                  <div class="flex justify-between">
                    <button
                      @click="retrainModel"
                      :disabled="saving"
                      class="inline-flex items-center px-6 py-3 text-sm font-semibold text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
                    >
                      Reentrenar Modelo
                    </button>
                    
                    <button
                      @click="saveMLConfig"
                      :disabled="saving"
                      class="inline-flex items-center px-6 py-3 text-sm font-semibold text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
                    >
                      Guardar Configuración ML
                    </button>
                  </div>
                </div>
              </SectionCard>
            </div>

            <!-- 5. Sistema -->
            <div v-if="activeTab === 'system'">
              <SectionCard 
                title="Información del Sistema"
                description="Estado y configuración del servidor"
              >
                <LoadingSkeleton v-if="loading && !systemConfig" :lines="5" />
                
                <div v-else class="space-y-6">
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <div class="flex items-center justify-between mb-2">
                        <h4 class="text-sm font-medium text-gray-900">Versión del Sistema</h4>
                        <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">{{ systemConfig.version }}</span>
                      </div>
                      <p class="text-sm text-gray-600">CacaoScan v{{ systemConfig.version }}</p>
                    </div>

                    <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <div class="flex items-center justify-between mb-2">
                        <h4 class="text-sm font-medium text-gray-900">Estado del Servidor</h4>
                        <span :class="systemConfig.server_status === 'online' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                          {{ systemConfig.server_status === 'online' ? 'Online' : 'Offline' }}
                        </span>
                      </div>
                      <p class="text-sm text-gray-600">{{ systemConfig.server_status === 'online' ? 'El servidor está funcionando correctamente' : 'Servidor no disponible' }}</p>
                    </div>
                  </div>

                  <div class="bg-white rounded-lg border border-gray-200 p-4">
                    <h4 class="text-sm font-medium text-gray-900 mb-3">Stack Tecnológico</h4>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <p class="text-xs text-gray-500">Backend</p>
                        <p class="text-sm font-medium text-gray-900">Django {{ systemConfig.backend_version }}</p>
                      </div>
                      <div>
                        <p class="text-xs text-gray-500">Frontend</p>
                        <p class="text-sm font-medium text-gray-900">Vue {{ systemConfig.frontend_version }}</p>
                      </div>
                      <div>
                        <p class="text-xs text-gray-500">Base de Datos</p>
                        <p class="text-sm font-medium text-gray-900">{{ systemConfig.database }}</p>
                      </div>
                    </div>
                  </div>

                  <div class="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                    <h4 class="text-sm font-medium text-yellow-900 mb-2">Rutas Activas de la API</h4>
                    <div class="space-y-1">
                      <div v-for="route in systemConfig.active_routes" :key="route" class="flex items-center text-sm">
                        <svg class="w-4 h-4 text-yellow-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                        </svg>
                        <span class="text-yellow-800 font-mono">{{ route }}</span>
                      </div>
                    </div>
                  </div>

                  <div class="flex flex-wrap gap-4">
                    <button
                      @click="clearCache"
                      :disabled="saving"
                      class="inline-flex items-center px-6 py-3 text-sm font-semibold text-white bg-amber-600 border border-transparent rounded-lg hover:bg-amber-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
                    >
                      Limpiar Caché
                    </button>
                    
                    <button
                      @click="checkBackendStatus"
                      :disabled="saving"
                      class="inline-flex items-center px-6 py-3 text-sm font-semibold text-white bg-purple-600 border border-transparent rounded-lg hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
                    >
                      Ver Estado del Backend
                    </button>
                  </div>
                </div>
              </SectionCard>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Swal from 'sweetalert2'
import { useAuthStore } from '@/stores/auth'
import { useConfigStore } from '@/stores/config'
import AdminSidebar from '@/components/layout/Common/Sidebar.vue'
import InputField from '@/components/admin/AdminConfigComponents/InputField.vue'
import SelectField from '@/components/admin/AdminConfigComponents/SelectField.vue'
import ToggleSwitch from '@/components/admin/AdminConfigComponents/ToggleSwitch.vue'
import SectionCard from '@/components/admin/AdminConfigComponents/SectionCard.vue'
import LoadingSkeleton from '@/components/admin/AdminConfigComponents/LoadingSkeleton.vue'

export default {
  name: 'AdminConfiguracion',
  components: {
    AdminSidebar,
    InputField,
    SelectField,
    ToggleSwitch,
    SectionCard,
    LoadingSkeleton
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const configStore = useConfigStore()

    // Estado reactivo
    const loading = ref(false)
    const saving = ref(false)
    
    // Usar el store para obtener el nombre del sistema
    const brandName = computed(() => configStore.brandName)
    
    const userName = computed(() => {
      const user = authStore.user
      if (user?.first_name && user?.last_name) {
        return `${user.first_name} ${user.last_name}`
      }
      return user?.username || 'Administrador'
    })

    const userRole = computed(() => {
      const role = authStore.userRole || 'Usuario'
      if (role === 'admin') return 'admin'
      if (role === 'farmer') return 'agricultor'
      return 'admin'
    })

    // Sidebar collapse state
    const isSidebarCollapsed = ref(false)
    
    // Intentar cargar el estado del sidebar desde localStorage
    const savedState = localStorage.getItem('sidebarCollapsed')
    if (savedState) {
      isSidebarCollapsed.value = savedState === 'true'
    }

    const toggleSidebarCollapse = () => {
      isSidebarCollapsed.value = !isSidebarCollapsed.value
      localStorage.setItem('sidebarCollapsed', isSidebarCollapsed.value)
    }
    
    // Tabs
    const tabs = [
      { id: 'general', name: 'General' },
      { id: 'users', name: 'Usuarios y Roles' },
      { id: 'security', name: 'Seguridad' },
      { id: 'ml', name: 'Modelos ML' },
      { id: 'system', name: 'Sistema' }
    ]
    const activeTab = ref('general')
    
    // Usar los datos del store
    const generalConfig = computed({
      get: () => configStore.general,
      set: (val) => configStore.updateGeneral(val)
    })

    const roles = ref([
      {
        id: 'admin',
        name: 'Administrador',
        description: 'Acceso completo al sistema',
        active: true,
        permissions: ['Crear usuarios', 'Eliminar usuarios', 'Modificar configuración']
      },
      {
        id: 'farmer',
        name: 'Agricultor',
        description: 'Gestiona fincas y analiza cacao',
        active: true,
        permissions: ['Crear fincas', 'Ver reportes', 'Subir imágenes']
      },
      {
        id: 'analyst',
        name: 'Técnico',
        description: 'Realiza análisis de calidad',
        active: true,
        permissions: ['Analizar imágenes', 'Generar reportes', 'Ver métricas']
      }
    ])

    const securityConfig = computed({
      get: () => configStore.security,
      set: (val) => configStore.updateSecurity(val)
    })

    
    // Referencia reactiva para uso en el template
    const mlConfig = ref({
      active_model: 'yolov8',
      metrics: {
        mae: '0.045',
        rmse: '0.068',
        r2: '0.92'
      },
      last_training: '15 de Noviembre, 2024'
    })

    const systemConfig = computed(() => ({
      ...configStore.system,
      active_routes: [
        '/api/auth/',
        '/api/fincas/',
        '/api/analisis/',
        '/api/config/'
      ]
    }))

    const modelOptions = [
      { value: 'yolov8', label: 'YOLOv8 (Recomendado)' },
      { value: 'resnet', label: 'ResNet Fine-tuned' },
      { value: 'baseline', label: 'Modelo Baseline' }
    ]

    const lastLogin = ref(null)
    
    // Métodos
    const handleMenuClick = (menuItem) => {
      if (menuItem.route) {
        router.push(menuItem.route)
      }
    }

    const handleLogout = async () => {
      try {
        await authStore.logout()
        router.push('/login')
      } catch (error) {
        console.error('Error al cerrar sesión:', error)
      }
    }

    const loadConfigurations = async () => {
      loading.value = true
      try {
        // Cargar desde el store
        await configStore.loadAll()
        
        // Sincronizar mlConfig para el template
        mlConfig.value = {
          active_model: configStore.ml.active_model,
          metrics: {
            mae: '0.045',
            rmse: '0.068',
            r2: '0.92'
          },
          last_training: configStore.ml.last_training 
            ? new Date(configStore.ml.last_training).toLocaleDateString('es-ES', { year: 'numeric', month: 'long', day: 'numeric' })
            : '15 de Noviembre, 2024'
        }
        
        console.log('✅ Configuraciones cargadas exitosamente')
      } catch (error) {
        console.error('Error cargando configuraciones:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudieron cargar las configuraciones'
        })
      } finally {
        loading.value = false
      }
    }

    const saveGeneralConfig = async () => {
      saving.value = true
      try {
        await configStore.saveGeneral(generalConfig.value)
        
        Swal.fire({
          toast: true,
          position: 'top-end',
          icon: 'success',
          title: 'Configuración guardada exitosamente',
          showConfirmButton: false,
          timer: 2000
        })
      } catch (error) {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: error.response?.data?.error || 'No se pudo guardar la configuración'
        })
      } finally {
        saving.value = false
      }
    }

    const saveSecurityConfig = async () => {
      saving.value = true
      try {
        await configStore.saveSecurity(securityConfig.value)
        Swal.fire({
          toast: true,
          position: 'top-end',
          icon: 'success',
          title: 'Configuración de seguridad actualizada',
          showConfirmButton: false,
          timer: 2000
        })
      } catch (error) {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: error.response?.data?.error || 'No se pudo actualizar la configuración de seguridad'
        })
      } finally {
        saving.value = false
      }
    }

    const saveMLConfig = async () => {
      saving.value = true
      try {
        const mlData = { active_model: mlConfig.value.active_model }
        await configStore.saveML(mlData)
        Swal.fire({
          toast: true,
          position: 'top-end',
          icon: 'success',
          title: 'Configuración ML guardada',
          showConfirmButton: false,
          timer: 2000
        })
      } catch (error) {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: error.response?.data?.error || 'No se pudo guardar la configuración ML'
        })
      } finally {
        saving.value = false
      }
    }

    const retrainModel = async () => {
      Swal.fire({
        icon: 'info',
        title: 'Función en desarrollo',
        text: 'La funcionalidad de reentrenamiento de modelos estará disponible próximamente'
      })
    }

    const clearCache = async () => {
      const result = await Swal.fire({
        title: '¿Limpiar caché?',
        text: 'Esta acción limpiará todo el caché del sistema',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sí, limpiar',
        cancelButtonText: 'Cancelar'
      })

      if (result.isConfirmed) {
        Swal.fire({
          icon: 'info',
          title: 'Función en desarrollo',
          text: 'La funcionalidad de limpieza de caché estará disponible próximamente'
        })
      }
    }

    const checkBackendStatus = async () => {
      saving.value = true
      try {
        const status = configStore.system
        Swal.fire({
          icon: 'success',
          title: 'Estado del Sistema',
          html: `
            <div class="text-left">
              <p><strong>Versión:</strong> ${status.version || 'N/A'}</p>
              <p><strong>Estado:</strong> <span style="color: ${status.server_status === 'online' ? 'green' : 'red'}">${status.server_status || 'N/A'}</span></p>
              <p><strong>Backend:</strong> Django ${status.backend_version || 'N/A'}</p>
              <p><strong>Frontend:</strong> Vue ${status.frontend_version || 'N/A'}</p>
              <p><strong>Base de datos:</strong> ${status.database || 'N/A'}</p>
            </div>
          `
        })
      } catch (error) {
        console.error('Error verificando estado del sistema:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo verificar el estado del sistema'
        })
      } finally {
        saving.value = false
      }
    }

    const handleLogoUpload = (event) => {
      const file = event.target.files[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
          generalConfig.value.logo_url = e.target.result
        }
        reader.readAsDataURL(file)
      }
    }

    const updateSliderStyle = (element) => {
      const value = ((element.value - element.min) / (element.max - element.min)) * 100
      element.style.setProperty('--value', value + '%')
    }

    const getRoleBadgeClass = (roleId) => {
      const classes = {
        admin: 'bg-red-100 text-red-800',
        farmer: 'bg-green-100 text-green-800',
        analyst: 'bg-blue-100 text-blue-800'
      }
      return classes[roleId] || 'bg-gray-100 text-gray-800'
    }

    // Lifecycle
    onMounted(() => {
      loadConfigurations()
    })

    return {
      // Estado
      loading,
      saving,
      isSidebarCollapsed,
      toggleSidebarCollapse,
      
      // Props
      brandName,
      userName,
      userRole,
      
      // Tabs
      tabs,
      activeTab,
      
      // Configuraciones
      generalConfig,
      roles,
      securityConfig,
      mlConfig,
      systemConfig,
      modelOptions,
      lastLogin,
      
      // Métodos
      handleMenuClick,
      handleLogout,
      saveGeneralConfig,
      saveSecurityConfig,
      saveMLConfig,
      retrainModel,
      clearCache,
      checkBackendStatus,
      handleLogoUpload,
      updateSliderStyle,
      getRoleBadgeClass
    }
  }
}
</script>

<style scoped>
/* Slider personalizado */
input[type="range"] {
  -webkit-appearance: none;
  appearance: none;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #10b981;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

input[type="range"]::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #10b981;
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Transiciones suaves */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

/* Responsive */
@media (max-width: 768px) {
  [class*="md:grid-cols-2"] {
    grid-template-columns: 1fr;
  }
  
  [class*="md:grid-cols-3"] {
    grid-template-columns: 1fr;
  }
}
</style>
