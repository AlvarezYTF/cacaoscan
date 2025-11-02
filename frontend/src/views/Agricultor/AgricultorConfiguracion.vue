<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar -->
    <Sidebar 
      :brand-name="'CacaoScan'"
      :user-name="userName"
      :user-role="userRole"
      :current-route="$route.path"
      :active-section="activeSection"
      :collapsed="isSidebarCollapsed"
      @menu-click="handleMenuClick"
      @logout="handleLogout"
      @toggle-collapse="toggleSidebarCollapse"
    />

    <!-- Main Content -->
    <div :class="isSidebarCollapsed ? 'lg:pl-20' : 'lg:pl-64'">
      <main class="py-6 px-4 sm:px-6 lg:px-8">
        <div class="max-w-4xl mx-auto">
          <!-- Header mejorado -->
          <div class="mb-8">
            <div class="bg-gradient-to-r from-white to-green-50 rounded-2xl border-2 border-gray-200 p-8 shadow-lg">
              <div class="flex items-center gap-4">
                <div class="p-3 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl shadow-lg">
                  <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <div>
                  <h1 class="text-3xl font-bold text-gray-900 mb-1">Configuración</h1>
                  <p class="text-gray-600 text-base">Gestiona tu perfil, fincas y preferencias</p>
                </div>
              </div>
            </div>
          </div>
        
          <!-- ACORDEÓN DE CONFIGURACIÓN -->
          <!-- Contenedor principal del acordeón -->
          <div class="space-y-4 mb-6">
            
            <!-- ============================================ -->
            <!-- SECCIÓN 1: DATOS PERSONALES -->
            <!-- ============================================ -->
            <div class="bg-white rounded-xl border-2 border-gray-200 shadow-lg overflow-hidden transition-all duration-200 ease-in-out">
              <!-- Cabecera del acordeón -->
              <button
                @click="toggleAccordion('personal')"
                class="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors duration-200"
                :class="{ 'border-b-2 border-gray-100': expandedSections.personal }"
              >
                <div class="flex items-center gap-4">
                  <!-- Ícono de usuario -->
                  <div class="p-2 bg-green-100 rounded-lg">
                    <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <div class="text-left">
                    <h2 class="text-xl font-semibold text-gray-900">Datos Personales</h2>
                    <p class="text-sm text-gray-500">Actualiza tu información personal y de contacto</p>
                  </div>
                </div>
                <!-- Ícono de flecha animado -->
                <svg 
                  class="w-5 h-5 text-gray-500 transition-transform duration-200"
                  :class="{ 'transform rotate-180': expandedSections.personal }"
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              <!-- Contenido del acordeón -->
              <Transition
                enter-active-class="transition-all duration-300 ease-out"
                enter-from-class="opacity-0 max-h-0"
                enter-to-class="opacity-100 max-h-[2000px]"
                leave-active-class="transition-all duration-200 ease-in"
                leave-from-class="opacity-100 max-h-[2000px]"
                leave-to-class="opacity-0 max-h-0"
              >
                <div v-show="expandedSections.personal" class="px-6 py-6 border-t-2 border-gray-100">
                  <!-- Datos personales -->
                  <ProfileSection 
                    ref="profileSectionRef"
                    :persona-data="personaData"
                    :is-loading="isSaving"
                    :is-verified="authStore.isVerified"
                    @save="saveProfile"
                  />
                  
                  <!-- Cambio de contraseña -->
                  <div class="mt-6 pt-6 border-t border-gray-200">
                    <PasswordSection 
                      ref="passwordSectionRef"
                      :is-loading="isChangingPassword"
                      @save="handlePasswordChange"
                    />
                  </div>
                </div>
              </Transition>
            </div>            
        </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { personasApi, authApi } from '@/services'
import Sidebar from '@/components/layout/Common/Sidebar.vue'
import ProfileSection from '@/components/agricultor/configuracion/ProfileSection.vue'
import PasswordSection from '@/components/agricultor/configuracion/PasswordSection.vue'

const router = useRouter()
const authStore = useAuthStore()
const profileSectionRef = ref(null)
const passwordSectionRef = ref(null)

const isSidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true')
const activeSection = ref('settings')

// ============================================
// ESTADO DEL ACORDEÓN
// ============================================
// Controla qué secciones están expandidas/cerradas
const expandedSections = ref({
  personal: true,        // Datos personales: expandido por defecto
  fincas: false,         // Fincas: cerrado por defecto
  escaneo: false,        // Preferencias de escaneo: cerrado por defecto
  notificaciones: false  // Notificaciones: cerrado por defecto
})

// Función para expandir/colapsar secciones del acordeón
const toggleAccordion = (section) => {
  expandedSections.value[section] = !expandedSections.value[section]
}

// Computed properties
const userName = computed(() => {
  return authStore.userFullName || 'Usuario'
})

const userRole = computed(() => {
  const role = authStore.userRole || 'Usuario'
  if (role === 'admin') return 'admin'
  if (role === 'farmer') return 'agricultor'
  return 'agricultor'
})

// Datos de persona
const personaData = ref({})

// Función para cargar datos del perfil desde el backend
const loadUserProfile = async () => {
  try {
    const perfilData = await personasApi.getPerfil()
    personaData.value = perfilData
  } catch (error) {
    console.error('Error cargando perfil:', error)
    // Si no hay datos de persona, mostrar mensaje
    if (error.response?.status === 404) {
      console.warn('Este usuario no tiene un perfil de persona asociado')
      // Inicializar con datos básicos del usuario para compatibilidad
      personaData.value = {
        email: authStore.user?.email || '',
        primer_nombre: authStore.user?.first_name || '',
        primer_apellido: authStore.user?.last_name || '',
        telefono: '',
        tipo_documento: '',
        numero_documento: '',
        genero: '',
        fecha_nacimiento: '',
        direccion: '',
        departamento: null,
        municipio: null
      }
    }
  }
}

// Estado de carga
const isSaving = ref(false)
const isChangingPassword = ref(false)
const isSavingScanPrefs = ref(false)
const isSavingNotifs = ref(false)
const isSyncing = ref(false)

// Fincas
const fincas = ref([
  {
    id: 1,
    nombre: 'Finca Los Cacaos',
    ubicacion: 'Tumaco, Nariño',
    hectareas: 2.5,
    isPrimary: true,
    isActive: true
  },
  {
    id: 2,
    nombre: 'Finca La Esperanza',
    ubicacion: 'Pasto, Nariño',
    hectareas: 1.8,
    isPrimary: false,
    isActive: true
  }
])

const showAddFincaModal = ref(false)

// Preferencias de escaneo
const scanPreferences = ref({
  grainType: 'Criollo',
  minWeight: 5,
  guidedMode: false,
  advancedResults: true
})

// Notificaciones
const notifications = ref({
  email: true,
  whatsapp: false,
  quality: true,
  environment: false
})

// Conectividad y respaldo
const lastSync = ref('Hace 2 horas')

// Sidebar methods
const handleMenuClick = (item) => {
  if (item.route && item.route !== null) {
    const currentPath = router.currentRoute.value.path
    if (currentPath !== item.route) {
      router.push(item.route)
    }
  } else {
    const role = authStore.userRole
    if (role === 'farmer' || role === 'Agricultor') {
      router.push({ 
        name: 'AgricultorDashboard',
        query: { section: item.id }
      })
    } else {
      router.push({ 
        name: 'AdminDashboard',
        query: { section: item.id }
      })
    }
  }
}

const toggleSidebarCollapse = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  localStorage.setItem('sidebarCollapsed', isSidebarCollapsed.value)
}

const handleLogout = async () => {
  try {
    await authStore.logout()
  } catch (error) {
    console.error('Error during logout:', error)
  }
}

// Métodos para gestionar el perfil
const saveProfile = async (formData) => {
  isSaving.value = true
  try {
    // Preparar datos para envío (solo los campos que pueden modificarse)
    const dataToUpdate = {
      primer_nombre: formData.primer_nombre,
      segundo_nombre: formData.segundo_nombre || '',
      primer_apellido: formData.primer_apellido,
      segundo_apellido: formData.segundo_apellido || '',
      tipo_documento: formData.tipo_documento,
      numero_documento: formData.numero_documento,
      genero: formData.genero,
      fecha_nacimiento: formData.fecha_nacimiento || null,
      telefono: formData.telefono,
      direccion: formData.direccion || '',
      departamento: formData.departamento || null,
      municipio: formData.municipio || null
    }

    let result
    
    // Intentar actualizar, si falla con 404, intentar crear
    try {
      result = await personasApi.actualizarPerfil(dataToUpdate)
    } catch (updateError) {
      if (updateError.response?.status === 404) {
        // Si no existe, crear el perfil
        console.log('📝 Perfil no existe, creando...')
        result = await personasApi.crearPerfil(dataToUpdate)
      } else {
        throw updateError
      }
    }
    
    if (result.message) {
      // Actualizar los datos locales
      personaData.value = result.data
      
      // Mostrar mensaje de éxito en el componente
      if (profileSectionRef.value) {
        profileSectionRef.value.setStatusMessage(result.message, 'success')
      }
    }
  } catch (error) {
    console.error('Error al guardar perfil:', error)
    
    // Extraer mensaje de error
    let errorMessage = 'Error al actualizar el perfil'
    if (error.response?.data) {
      const responseData = error.response.data
      if (typeof responseData === 'string') {
        errorMessage = responseData
      } else if (responseData.error) {
        errorMessage = responseData.error
      } else {
        // Si hay errores de campo específicos, tomar el primero
        const firstError = Object.values(responseData)[0]
        if (Array.isArray(firstError)) {
          errorMessage = firstError[0]
        } else if (typeof firstError === 'string') {
          errorMessage = firstError
        }
      }
    }
    
    // Mostrar mensaje de error en el componente
    if (profileSectionRef.value) {
      profileSectionRef.value.setStatusMessage(errorMessage, 'error')
    }
  } finally {
    isSaving.value = false
  }
}

// Método para cambio de contraseña
const handlePasswordChange = async (passwordData) => {
  isChangingPassword.value = true
  
  // Limpiar mensajes previos
  if (passwordSectionRef.value) {
    passwordSectionRef.value.setError('')
  }
  
  try {
    // Llamar directamente a la API
    const result = await authApi.changePassword({
      oldPassword: passwordData.currentPassword,
      newPassword: passwordData.newPassword,
      confirmPassword: passwordData.confirmPassword
    })
    
    // Verificar si el resultado es exitoso
    if (result.success || result.message) {
      // Mostrar mensaje de éxito en el componente
      if (passwordSectionRef.value) {
        passwordSectionRef.value.setSuccess(result.message || 'Contraseña cambiada exitosamente')
      }
    } else {
      throw new Error(result.error || 'Error al cambiar la contraseña')
    }
  } catch (error) {
    console.error('Error al cambiar contraseña:', error)
    
    // Extraer mensaje de error del backend
    let errorMessage = 'Error al cambiar la contraseña'
    
    if (error.response?.data) {
      const responseData = error.response.data
      
      // Si hay un mensaje general
      if (responseData.message) {
        errorMessage = responseData.message
      } else if (typeof responseData === 'string') {
        errorMessage = responseData
      } else if (responseData.error) {
        errorMessage = responseData.error
      } else if (responseData.details) {
        // Si hay detalles, extraer el primer error
        const firstKey = Object.keys(responseData.details)[0]
        if (firstKey) {
          const fieldError = responseData.details[firstKey]
          errorMessage = Array.isArray(fieldError) ? fieldError[0] : fieldError
        }
      } else {
        // Si hay errores de campo específicos, tomar el primero
        const errorKeys = Object.keys(responseData)
        if (errorKeys.length > 0) {
          const firstKey = errorKeys[0]
          const fieldError = responseData[firstKey]
          errorMessage = Array.isArray(fieldError) ? fieldError[0] : fieldError
        }
      }
    } else if (error.message) {
      errorMessage = error.message
    }
    
    // Mostrar error en el componente
    if (passwordSectionRef.value) {
      passwordSectionRef.value.setError(errorMessage)
    }
  } finally {
    isChangingPassword.value = false
  }
}

// Métodos para gestionar fincas
const toggleFincaStatus = (id) => {
  const finca = fincas.value.find(f => f.id === id)
  if (finca) {
    finca.isActive = !finca.isActive
  }
}

const setPrimaryFinca = (id) => {
  fincas.value.forEach(f => {
    f.isPrimary = f.id === id
  })
}

// Métodos para preferencias de escaneo
const saveScanPreferences = async () => {
  isSavingScanPrefs.value = true
  try {
    // TODO: Llamar al API PATCH /api/v1/agricultores/configuracion/
    console.log('Guardando preferencias de escaneo:', scanPreferences.value)
    await new Promise(resolve => setTimeout(resolve, 1000))
    alert('Preferencias de escaneo guardadas')
  } catch (error) {
    console.error('Error al guardar preferencias:', error)
    alert('Error al guardar las preferencias')
  } finally {
    isSavingScanPrefs.value = false
  }
}

// Métodos para notificaciones
const saveNotifications = async () => {
  isSavingNotifs.value = true
  try {
    // TODO: Llamar al API PATCH /api/v1/agricultores/notificaciones/
    console.log('Guardando notificaciones:', notifications.value)
    await new Promise(resolve => setTimeout(resolve, 1000))
    alert('Preferencias de notificaciones guardadas')
  } catch (error) {
    console.error('Error al guardar notificaciones:', error)
    alert('Error al guardar las notificaciones')
  } finally {
    isSavingNotifs.value = false
  }
}

// Métodos para conectividad y respaldo
const syncData = async () => {
  isSyncing.value = true
  try {
    console.log('Sincronizando datos...')
    await new Promise(resolve => setTimeout(resolve, 2000))
    lastSync.value = 'Hace un momento'
    alert('Datos sincronizados exitosamente')
  } catch (error) {
    console.error('Error al sincronizar:', error)
    alert('Error al sincronizar los datos')
  } finally {
    isSyncing.value = false
  }
}

const exportToCSV = async () => {
  try {
    console.log('Exportando a CSV...')
    alert('Archivo CSV descargado')
  } catch (error) {
    console.error('Error al exportar CSV:', error)
    alert('Error al exportar el archivo CSV')
  }
}

const exportToPDF = async () => {
  try {
    console.log('Exportando a PDF...')
    alert('Archivo PDF descargado')
  } catch (error) {
    console.error('Error al exportar PDF:', error)
    alert('Error al exportar el archivo PDF')
  }
}

// Cargar datos al montar el componente
onMounted(() => {
  loadUserProfile()
})
</script>

<style scoped>
/* Estilos para el acordeón - Animaciones suaves de expansión/colapso */
.accordion-content {
  overflow: hidden;
  transition: max-height 0.3s ease-out, opacity 0.2s ease-out;
}

/* Responsive: Asegurar que el acordeón se adapte bien en móviles */
@media (max-width: 640px) {
  .max-w-4xl {
    max-width: 100%;
    padding-left: 1rem;
    padding-right: 1rem;
  }
}
</style>
