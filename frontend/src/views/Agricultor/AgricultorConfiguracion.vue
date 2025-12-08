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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { personasApi, authApi } from '@/services'
import { useSidebarNavigation } from '@/composables/useSidebarNavigation'
import Sidebar from '@/components/layout/Common/Sidebar.vue'
import ProfileSection from '@/components/agricultor/configuracion/ProfileSection.vue'
import PasswordSection from '@/components/agricultor/configuracion/PasswordSection.vue'

const router = useRouter()
const authStore = useAuthStore()
const profileSectionRef = ref(null)
const passwordSectionRef = ref(null)

// Sidebar navigation composable
const {
  isSidebarCollapsed,
  userName,
  userRole: computedUserRole,
  handleMenuClick,
  toggleSidebarCollapse,
  handleLogout
} = useSidebarNavigation()

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
const userRole = computedUserRole

// Datos de persona
const personaData = ref({})

// Función para cargar datos del perfil desde el backend
const loadUserProfile = async () => {
  try {
    const perfilData = await personasApi.getPerfil()
    personaData.value = perfilData
  } catch (error) {
    // Si no hay datos de persona, mostrar mensaje
    if (error.response?.status === 404) {
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

// Sidebar and navbar methods are now provided by useSidebarNavigation composable

// Helper functions for profile management
const prepareProfileData = (formData) => {
  return {
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
}

const isNotFoundError = (error) => {
  return error.response?.status === 404
}

const updateOrCreateProfile = async (dataToUpdate) => {
  try {
    return await personasApi.actualizarPerfil(dataToUpdate)
  } catch (updateError) {
    if (isNotFoundError(updateError)) {
      return await personasApi.crearPerfil(dataToUpdate)
    }
    throw updateError
  }
}

const getFirstErrorValue = (responseData) => {
  const firstError = Object.values(responseData)[0]
  if (Array.isArray(firstError)) {
    return firstError[0]
  }
  if (typeof firstError === 'string') {
    return firstError
  }
  return null
}

const extractStringError = (responseData) => {
  return typeof responseData === 'string' ? responseData : null
}

const extractErrorField = (responseData) => {
  return responseData.error || null
}

const extractProfileErrorMessage = (error) => {
  const defaultMessage = 'Error al actualizar el perfil'
  
  if (!error.response?.data) {
    return defaultMessage
  }
  
  const responseData = error.response.data
  const stringError = extractStringError(responseData)
  if (stringError) return stringError
  
  const errorField = extractErrorField(responseData)
  if (errorField) return errorField
  
  const firstError = getFirstErrorValue(responseData)
  return firstError || defaultMessage
}

const handleProfileSuccess = (result) => {
  if (result.message) {
    personaData.value = result.data
    if (profileSectionRef.value) {
      profileSectionRef.value.setStatusMessage(result.message, 'success')
    }
  }
}

const handleProfileError = (error) => {
  const errorMessage = extractProfileErrorMessage(error)
  if (profileSectionRef.value) {
    profileSectionRef.value.setStatusMessage(errorMessage, 'error')
  }
}

// Métodos para gestionar el perfil
const saveProfile = async (formData) => {
  isSaving.value = true
  try {
    const dataToUpdate = prepareProfileData(formData)
    const result = await updateOrCreateProfile(dataToUpdate)
    handleProfileSuccess(result)
  } catch (error) {
    handleProfileError(error)
  } finally {
    isSaving.value = false
  }
}

/**
 * Extract error message from field error (array or string)
 * @param {string|Array<string>} fieldError - Field error value
 * @returns {string} - Error message
 */
function extractFieldErrorMessage(fieldError) {
  return Array.isArray(fieldError) ? fieldError[0] : fieldError
}

/**
 * Extract first error from object with field errors
 * @param {Object} errorObject - Object with field errors
 * @returns {string|null} - First error message or null
 */
function extractFirstFieldError(errorObject) {
  const errorKeys = Object.keys(errorObject)
  if (errorKeys.length === 0) {
    return null
  }
  const firstKey = errorKeys[0]
  const fieldError = errorObject[firstKey]
  return extractFieldErrorMessage(fieldError)
}

/**
 * Extract error message from API error response
 * @param {Object} error - Error object from API call
 * @returns {string} - Error message
 */
function extractErrorMessage(error) {
  const defaultMessage = 'Error al cambiar la contraseña'
  
  if (error.message) {
    return error.message
  }
  
  if (!error.response?.data) {
    return defaultMessage
  }
  
  const responseData = error.response.data
  
  if (responseData.message) {
    return responseData.message
  }
  
  if (typeof responseData === 'string') {
    return responseData
  }
  
  if (responseData.error) {
    return responseData.error
  }
  
  if (responseData.details) {
    const detailsError = extractFirstFieldError(responseData.details)
    if (detailsError) {
      return detailsError
    }
  }
  
  const fieldError = extractFirstFieldError(responseData)
  if (fieldError) {
    return fieldError
  }
  
  return defaultMessage
}

/**
 * Show success message in password section component
 * @param {string} message - Success message
 */
function showPasswordSuccess(message) {
  if (passwordSectionRef.value) {
    passwordSectionRef.value.setSuccess(message)
  }
}

/**
 * Show error message in password section component
 * @param {string} message - Error message
 */
function showPasswordError(message) {
  if (passwordSectionRef.value) {
    passwordSectionRef.value.setError(message)
  }
}

/**
 * Clear error messages in password section component
 */
function clearPasswordErrors() {
  if (passwordSectionRef.value) {
    passwordSectionRef.value.setError('')
  }
}

// Método para cambio de contraseña
const handlePasswordChange = async (passwordData) => {
  isChangingPassword.value = true
  clearPasswordErrors()
  
  try {
    const result = await authApi.changePassword({
      oldPassword: passwordData.currentPassword,
      newPassword: passwordData.newPassword,
      confirmPassword: passwordData.confirmPassword
    })
    
    if (result.success || result.message) {
      showPasswordSuccess(result.message || 'Contraseña cambiada exitosamente')
    } else {
      throw new Error(result.error || 'Error al cambiar la contraseña')
    }
  } catch (error) {
    const errorMessage = extractErrorMessage(error)
    showPasswordError(errorMessage)
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
  for (const f of fincas.value) {
    f.isPrimary = f.id === id
  }
}

// Métodos para preferencias de escaneo
const saveScanPreferences = async () => {
  isSavingScanPrefs.value = true
  try {
    // Pendiente: Implementar endpoint PATCH /api/v1/agricultores/configuracion/
    // Cuando esté disponible, usar:
    // await api.patch('/agricultores/configuracion/', scanPreferences.value)
    await new Promise(resolve => setTimeout(resolve, 1000))
    alert('Preferencias de escaneo guardadas')
  } catch (error) {
    alert('Error al guardar las preferencias')
  } finally {
    isSavingScanPrefs.value = false
  }
}

// Métodos para notificaciones
const saveNotifications = async () => {
  isSavingNotifs.value = true
  try {
    // Pendiente: Implementar endpoint PATCH /api/v1/agricultores/notificaciones/
    // Cuando esté disponible, usar:
    // await api.patch('/agricultores/notificaciones/', notifications.value)
    await new Promise(resolve => setTimeout(resolve, 1000))
    alert('Preferencias de notificaciones guardadas')
  } catch (error) {
    alert('Error al guardar las notificaciones')
  } finally {
    isSavingNotifs.value = false
  }
}

// Métodos para conectividad y respaldo
const syncData = async () => {
  isSyncing.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    lastSync.value = 'Hace un momento'
    alert('Datos sincronizados exitosamente')
  } catch (error) {
    alert('Error al sincronizar los datos')
  } finally {
    isSyncing.value = false
  }
}

const exportToCSV = async () => {
  try {
    alert('Archivo CSV descargado')
  } catch (error) {
    alert('Error al exportar el archivo CSV')
  }
}

const exportToPDF = async () => {
  try {
    alert('Archivo PDF descargado')
  } catch (error) {
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
