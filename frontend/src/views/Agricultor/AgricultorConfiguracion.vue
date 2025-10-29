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
        <div class="max-w-7xl mx-auto">
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
        
          <!-- Settings Content mejorado -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <!-- Componente: Datos Personales -->
            <ProfileSection 
              :user-profile="userProfile"
              :is-loading="isSaving"
              :is-verified="authStore.isVerified"
              @update:userProfile="userProfile = $event"
              @save="saveProfile"
            />

            <!-- Componente: Cambio de Contraseña -->
            <PasswordSection 
              :is-loading="isChangingPassword"
              @save="handlePasswordChange"
            />
          </div>

          <!-- Segunda fila: Configuración de Fincas y Preferencias de Escaneo -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <!-- Componente: Fincas -->
            <FincasSection 
              :fincas="fincas"
              @toggle-status="toggleFincaStatus"
              @set-primary="setPrimaryFinca"
              @add-new="showAddFincaModal = true"
            />

            <!-- Componente: Preferencias de Escaneo -->
            <ScanPreferencesSection 
              :preferences="scanPreferences"
              :is-loading="isSavingScanPrefs"
              @update:preferences="scanPreferences = $event"
              @save="saveScanPreferences"
            />
          </div>

          <!-- Tercera fila: Notificaciones y Ajustes -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <!-- Componente: Notificaciones -->
            <NotificationsSection
              :notifications="notifications"
              :is-loading="isSavingNotifs"
              @update:notifications="notifications = $event"
              @save="saveNotifications"
            />

            <!-- Componente: Ajustes Visuales -->
            <VisualSettingsSection
              :settings="visualSettings"
              :is-loading="isSavingVisual"
              @update:settings="visualSettings = $event"
              @save="saveVisualSettings"
            />
          </div>

          <!-- Cuarta fila: Conectividad y respaldo -->
          <BackupSyncSection
            :last-sync="lastSync"
            :is-loading="isSyncing"
            @sync="syncData"
            @export-csv="exportToCSV"
            @export-pdf="exportToPDF"
          />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Sidebar from '@/components/layout/Common/Sidebar.vue'
import ProfileSection from '@/components/agricultor/configuracion/ProfileSection.vue'
import PasswordSection from '@/components/agricultor/configuracion/PasswordSection.vue'
import FincasSection from '@/components/agricultor/configuracion/FincasSection.vue'
import ScanPreferencesSection from '@/components/agricultor/configuracion/ScanPreferencesSection.vue'
import NotificationsSection from '@/components/agricultor/configuracion/NotificationsSection.vue'
import VisualSettingsSection from '@/components/agricultor/configuracion/VisualSettingsSection.vue'
import BackupSyncSection from '@/components/agricultor/configuracion/BackupSyncSection.vue'

const router = useRouter()
const authStore = useAuthStore()

const isSidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true')
const activeSection = ref('settings')

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

// Variables para configuración - inicializar con datos del usuario
const userProfile = ref({
  fullName: authStore.user?.full_name || `${authStore.user?.first_name || ''} ${authStore.user?.last_name || ''}`.trim() || '',
  email: authStore.user?.email || '',
  phone: authStore.user?.phone_number || ''
})

// Función para cargar datos del perfil desde el backend
const loadUserProfile = async () => {
  try {
    // Primero actualizar los datos del usuario en el store
    await authStore.getCurrentUser()
    
    // Luego obtener los datos actualizados
    const currentUser = authStore.user
    
    if (currentUser) {
      userProfile.value = {
        fullName: currentUser.full_name || `${currentUser.first_name || ''} ${currentUser.last_name || ''}`.trim() || '',
        email: currentUser.email || '',
        phone: currentUser.phone_number || ''
      }
    }
  } catch (error) {
    console.error('Error cargando perfil:', error)
  }
}

// Cargar perfil al montar el componente
loadUserProfile()

// Estado de carga
const isSaving = ref(false)
const isChangingPassword = ref(false)
const isSavingScanPrefs = ref(false)
const isSavingNotifs = ref(false)
const isSavingVisual = ref(false)
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

// Ajustes visuales
const visualSettings = ref({
  darkMode: false,
  fontSize: 'medium',
  compactMode: false
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
const saveProfile = async () => {
  isSaving.value = true
  try {
    // Llamar al API para actualizar el perfil
    const result = await authStore.updateProfile({
      fullName: userProfile.value.fullName,
      phone: userProfile.value.phone
    })
    
    if (result.success) {
      // Mostrar notificación de éxito
      alert('Perfil actualizado exitosamente')
    } else {
      alert(result.error || 'Error al guardar el perfil')
    }
  } catch (error) {
    console.error('Error al guardar perfil:', error)
    alert('Error al guardar el perfil')
  } finally {
    isSaving.value = false
  }
}

// Método para cambio de contraseña
const handlePasswordChange = async (passwordData) => {
  isChangingPassword.value = true
  try {
    // Llamar al API para cambiar la contraseña
    const result = await authStore.changePassword({
      oldPassword: passwordData.currentPassword,
      newPassword: passwordData.newPassword,
      confirmPassword: passwordData.confirmPassword
    })
    
    if (result.success) {
      alert('Contraseña cambiada exitosamente')
    } else {
      alert(result.error || 'Error al cambiar la contraseña')
    }
  } catch (error) {
    console.error('Error al cambiar contraseña:', error)
    alert('Error al cambiar la contraseña')
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

// Métodos para ajustes visuales
const saveVisualSettings = async () => {
  isSavingVisual.value = true
  try {
    localStorage.setItem('darkMode', visualSettings.value.darkMode)
    localStorage.setItem('fontSize', visualSettings.value.fontSize)
    localStorage.setItem('compactMode', visualSettings.value.compactMode)
    console.log('Guardando ajustes visuales:', visualSettings.value)
    await new Promise(resolve => setTimeout(resolve, 800))
    alert('Ajustes visuales guardados')
  } catch (error) {
    console.error('Error al guardar ajustes:', error)
    alert('Error al guardar los ajustes')
  } finally {
    isSavingVisual.value = false
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
</script>

<style scoped>
.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.settings-card {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
