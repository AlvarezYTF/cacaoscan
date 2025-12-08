<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar -->
    <Sidebar
      :brand-name="'CacaoScan'"
      :user-name="userName"
      :user-role="userRole"
      :current-route="route.path"
      :active-section="'fincas'"
      :collapsed="isSidebarCollapsed"
      @menu-click="handleMenuClick"
      @logout="handleLogout"
      @toggle-collapse="toggleSidebarCollapse"
    />

    <!-- Main Content -->
    <div :class="isSidebarCollapsed ? 'lg:pl-20' : 'lg:pl-64'" class="w-full relative">
      <div class="min-h-screen bg-gray-50 py-6 px-4 sm:px-6 lg:px-8">
        <div class="max-w-4xl mx-auto">
          <!-- Header -->
          <div class="mb-8">
            <h1 class="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <div class="p-2 bg-green-100 rounded-lg">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                </svg>
              </div>
              Nuevo Lote
            </h1>
            <p class="mt-2 text-gray-600">Crea un nuevo lote para la finca {{ finca?.nombre || '' }}</p>
          </div>

          <!-- Form Card -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <form @submit.prevent="handleSubmit" class="p-6">
              <div class="space-y-6">
                <!-- Información básica -->
                <div>
                  <h3 class="text-lg font-semibold text-gray-900 mb-4">Información Básica</h3>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label for="identificador" class="block text-sm font-medium text-gray-700 mb-2">
                        Identificador *
                      </label>
                      <input
                        id="identificador"
                        v-model="formData.identificador"
                        type="text"
                        required
                        class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                        :class="{ 'border-red-500': errors.identificador }"
                        placeholder="Ej: LOTE-001"
                      />
                      <p v-if="errors.identificador" class="text-red-500 text-xs mt-1">{{ errors.identificador }}</p>
                    </div>

                    <div>
                      <label for="variedad" class="block text-sm font-medium text-gray-700 mb-2">
                        Variedad *
                      </label>
                      <select
                        id="variedad"
                        v-model="formData.variedad"
                        required
                        class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                        :class="{ 'border-red-500': errors.variedad }"
                      >
                        <option value="">Seleccionar variedad</option>
                        <option v-for="variedad in variedades" :key="variedad" :value="variedad">
                          {{ variedad }}
                        </option>
                      </select>
                      <p v-if="errors.variedad" class="text-red-500 text-xs mt-1">{{ errors.variedad }}</p>
                    </div>
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                    <div>
                      <label for="area_hectareas" class="block text-sm font-medium text-gray-700 mb-2">
                        Área (hectáreas) *
                      </label>
                      <input
                        id="area_hectareas"
                        v-model="formData.area_hectareas"
                        type="number"
                        step="0.01"
                        min="0.01"
                        required
                        class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                        :class="{ 'border-red-500': errors.area_hectareas }"
                        placeholder="0.00"
                      />
                      <p v-if="errors.area_hectareas" class="text-red-500 text-xs mt-1">{{ errors.area_hectareas }}</p>
                    </div>

                    <div>
                      <label for="estado" class="block text-sm font-medium text-gray-700 mb-2">
                        Estado *
                      </label>
                      <select
                        id="estado"
                        v-model="formData.estado"
                        required
                        class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                        :class="{ 'border-red-500': errors.estado }"
                      >
                        <option value="">Seleccionar estado</option>
                        <option value="activo">Activo</option>
                        <option value="inactivo">Inactivo</option>
                        <option value="cosechado">Cosechado</option>
                      </select>
                      <p v-if="errors.estado" class="text-red-500 text-xs mt-1">{{ errors.estado }}</p>
                    </div>
                  </div>
                </div>

                <!-- Fechas -->
                <div>
                  <h3 class="text-lg font-semibold text-gray-900 mb-4">Fechas</h3>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label for="fecha_plantacion" class="block text-sm font-medium text-gray-700 mb-2">
                        Fecha de Plantación *
                      </label>
                      <input
                        id="fecha_plantacion"
                        v-model="formData.fecha_plantacion"
                        type="date"
                        required
                        class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                        :class="{ 'border-red-500': errors.fecha_plantacion }"
                      />
                      <p v-if="errors.fecha_plantacion" class="text-red-500 text-xs mt-1">{{ errors.fecha_plantacion }}</p>
                    </div>

                    <div>
                      <label for="fecha_cosecha" class="block text-sm font-medium text-gray-700 mb-2">
                        Fecha de Cosecha
                      </label>
                      <input
                        id="fecha_cosecha"
                        v-model="formData.fecha_cosecha"
                        type="date"
                        class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                        :class="{ 'border-red-500': errors.fecha_cosecha }"
                      />
                      <p v-if="errors.fecha_cosecha" class="text-red-500 text-xs mt-1">{{ errors.fecha_cosecha }}</p>
                    </div>
                  </div>
                </div>

                <!-- Coordenadas GPS (opcional) -->
                <div>
                  <h3 class="text-lg font-semibold text-gray-900 mb-4">Coordenadas GPS (Opcional)</h3>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label for="coordenadas_lat" class="block text-sm font-medium text-gray-700 mb-2">
                        Latitud
                      </label>
                      <input
                        id="coordenadas_lat"
                        v-model="formData.coordenadas_lat"
                        type="number"
                        step="any"
                        min="-90"
                        max="90"
                        class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                        :class="{ 'border-red-500': errors.coordenadas_lat }"
                        placeholder="Ej: 4.6097"
                      />
                      <p v-if="errors.coordenadas_lat" class="text-red-500 text-xs mt-1">{{ errors.coordenadas_lat }}</p>
                    </div>

                    <div>
                      <label for="coordenadas_lng" class="block text-sm font-medium text-gray-700 mb-2">
                        Longitud
                      </label>
                      <input
                        id="coordenadas_lng"
                        v-model="formData.coordenadas_lng"
                        type="number"
                        step="any"
                        min="-180"
                        max="180"
                        class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                        :class="{ 'border-red-500': errors.coordenadas_lng }"
                        placeholder="Ej: -74.0817"
                      />
                      <p v-if="errors.coordenadas_lng" class="text-red-500 text-xs mt-1">{{ errors.coordenadas_lng }}</p>
                    </div>
                  </div>
                </div>

                <!-- Descripción -->
                <div>
                  <label for="descripcion" class="block text-sm font-medium text-gray-700 mb-2">
                    Descripción (Opcional)
                  </label>
                  <textarea
                    id="descripcion"
                    v-model="formData.descripcion"
                    rows="4"
                    class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                    :class="{ 'border-red-500': errors.descripcion }"
                    placeholder="Descripción adicional del lote..."
                  ></textarea>
                  <p v-if="errors.descripcion" class="text-red-500 text-xs mt-1">{{ errors.descripcion }}</p>
                </div>

                <!-- Errores generales -->
                <div v-if="errors._general && errors._general.length > 0" class="bg-red-50 border-l-4 border-red-400 p-4 rounded">
                  <div class="flex">
                    <div class="flex-shrink-0">
                      <svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>
                    </div>
                    <div class="ml-3">
                      <h3 class="text-sm font-medium text-red-800">Errores de validación</h3>
                      <div class="mt-2 text-sm text-red-700">
                        <ul class="list-disc list-inside space-y-1">
                          <li v-for="(error, index) in errors._general" :key="index">{{ error }}</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Estado activo -->
                <div>
                  <label class="flex items-center">
                    <input
                      v-model="formData.activa"
                      type="checkbox"
                      class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                    />
                    <span class="ml-2 text-sm text-gray-700">Lote activo</span>
                  </label>
                </div>
              </div>

              <!-- Botones -->
              <div class="flex justify-end gap-3 mt-8 pt-6 border-t">
                <button
                  type="button"
                  @click="goBack"
                  class="px-6 py-2.5 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors font-medium"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  :disabled="loading"
                  class="px-6 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-medium"
                >
                  <div v-if="loading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  {{ loading ? 'Creando...' : 'Crear Lote' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSidebarNavigation } from '@/composables/useSidebarNavigation'
import { useLotes } from '@/composables/useLotes'
import { getFincaById } from '@/services/fincasApi'
import { useNotifications } from '@/composables/useNotifications'
import Sidebar from '@/components/layout/Common/Sidebar.vue'
import lotesApi from '@/services/lotesApi'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// Sidebar navigation composable
const {
  isSidebarCollapsed,
  userName,
  userRole,
  handleMenuClick,
  toggleSidebarCollapse,
  handleLogout
} = useSidebarNavigation()

// Composables
const { createLote, loading: isLotesLoading } = useLotes()
const { showSuccess, showError } = useNotifications()

// Reactive data
const finca = ref(null)
const fincaId = computed(() => {
  const id = route.params.id
  return id ? parseInt(id, 10) : null
})
const localLoading = ref(false)
const errors = ref({})

// Datos del formulario
const formData = reactive({
  identificador: '',
  variedad: '',
  fecha_plantacion: '',
  fecha_cosecha: '',
  area_hectareas: '',
  estado: 'activo',
  descripcion: '',
  coordenadas_lat: '',
  coordenadas_lng: '',
  activa: true
})

// Computed
const variedades = computed(() => lotesApi.getVariedadesCacao())
const loading = computed(() => isLotesLoading.value || localLoading.value)

// Methods
const loadFinca = async () => {
  try {
    const data = await getFincaById(fincaId.value)
    finca.value = data
  } catch (err) {
    showError('No se pudo cargar la información de la finca')
  }
}

const validateForm = () => {
  errors.value = {}
  let isValid = true

  if (!formData.identificador || formData.identificador.trim().length < 2) {
    errors.value.identificador = 'El identificador debe tener al menos 2 caracteres'
    isValid = false
  }

  if (!formData.variedad) {
    errors.value.variedad = 'Debes seleccionar una variedad'
    isValid = false
  }

  if (!formData.area_hectareas || parseFloat(formData.area_hectareas) <= 0) {
    errors.value.area_hectareas = 'El área debe ser mayor a 0'
    isValid = false
  }

  if (!formData.fecha_plantacion) {
    errors.value.fecha_plantacion = 'Debes seleccionar una fecha de plantación'
    isValid = false
  }

  if (!formData.estado) {
    errors.value.estado = 'Debes seleccionar un estado'
    isValid = false
  }

  return isValid
}

const handleSubmit = async () => {
  // Validar que tenemos fincaId
  if (!fincaId.value || isNaN(fincaId.value)) {
    showError('No se pudo identificar la finca. Por favor, regresa e intenta nuevamente.')
    return
  }

  if (!validateForm()) {
    return
  }

  localLoading.value = true
  errors.value = {} // Limpiar errores previos

  try {
    const loteData = {
      finca: Number(fincaId.value),
      identificador: formData.identificador.trim(),
      variedad: formData.variedad,
      fecha_plantacion: formData.fecha_plantacion,
      fecha_cosecha: formData.fecha_cosecha || null,
      area_hectareas: parseFloat(formData.area_hectareas),
      estado: formData.estado,
      descripcion: formData.descripcion || null,
      coordenadas_lat: formData.coordenadas_lat ? parseFloat(formData.coordenadas_lat) : null,
      coordenadas_lng: formData.coordenadas_lng ? parseFloat(formData.coordenadas_lng) : null,
      activa: formData.activa
    }

    await createLote(loteData)
    showSuccess('El lote ha sido creado exitosamente')
    router.push(`/fincas/${fincaId.value}/lotes`)
  } catch (error) {
    
    // Limpiar errores previos
    errors.value = {}
    
    // Manejar errores de validación del composable (errores lanzados con throw new Error)
    if (error.message && !error.response) {
      const errorMessage = error.message
      showError(errorMessage)
      
      // Mapear errores a campos específicos si es posible
      if (errorMessage.includes('finca') || errorMessage.includes('Finca')) {
        errors.value.finca = 'La finca es requerida'
      }
      if (errorMessage.includes('identificador') || errorMessage.includes('Identificador')) {
        errors.value.identificador = 'El identificador es requerido'
      }
      if (errorMessage.includes('variedad') || errorMessage.includes('Variedad')) {
        errors.value.variedad = 'La variedad es requerida'
      }
      if (errorMessage.includes('plantación') || errorMessage.includes('Plantación')) {
        errors.value.fecha_plantacion = 'La fecha de plantación es requerida'
      }
      if (errorMessage.includes('área') || errorMessage.includes('Área') || errorMessage.includes('hectáreas')) {
        errors.value.area_hectareas = 'El área es requerida'
      }
      return
    }
    
    // Manejar errores del servidor (400, 403, etc.)
    if (error.response?.data) {
      const responseData = error.response.data
      
      // El backend puede devolver errores en 'details' o directamente en el objeto
      const serverErrors = responseData.details || responseData
      
      // Mapear errores del servidor a campos específicos
      const errorFields = [
        'finca', 'identificador', 'variedad', 'area_hectareas', 
        'fecha_plantacion', 'fecha_cosecha', 'estado', 
        'coordenadas_lat', 'coordenadas_lng', 'descripcion'
      ]
      
      errorFields.forEach(field => {
        if (serverErrors[field]) {
          errors.value[field] = Array.isArray(serverErrors[field]) 
            ? serverErrors[field][0] 
            : String(serverErrors[field])
        }
      })
      
      // Manejar errores no asociados a campos específicos
      if (serverErrors.non_field_errors) {
        const nonFieldErrors = Array.isArray(serverErrors.non_field_errors) 
          ? serverErrors.non_field_errors 
          : [serverErrors.non_field_errors]
        errors.value._general = nonFieldErrors
      }
      
      // Construir mensaje de error para mostrar en la notificación
      let errorMessage = 'No se pudo crear el lote'
      const errorMessages = []
      
      // Priorizar mensajes específicos
      if (responseData.error && typeof responseData.error === 'string') {
        errorMessages.push(responseData.error)
      } else if (responseData.detail && typeof responseData.detail === 'string') {
        errorMessages.push(responseData.detail)
      }
      
      // Agregar errores de campos
      const fieldErrorMessages = Object.entries(serverErrors)
        .filter(([key]) => !['error', 'detail', 'status'].includes(key))
        .map(([key, value]) => {
          const fieldName = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
          const errorText = Array.isArray(value) ? value[0] : String(value)
          return `${fieldName}: ${errorText}`
        })
      
      if (fieldErrorMessages.length > 0) {
        errorMessages.push(...fieldErrorMessages)
      }
      
      // Si hay errores no asociados a campos
      if (serverErrors.non_field_errors) {
        const nonFieldErrors = Array.isArray(serverErrors.non_field_errors) 
          ? serverErrors.non_field_errors 
          : [serverErrors.non_field_errors]
        errorMessages.push(...nonFieldErrors)
      }
      
      // Mostrar el mensaje de error
      if (errorMessages.length > 0) {
        errorMessage = errorMessages.join('. ')
      }
      
      showError(errorMessage)
    } else if (error.message) {
      // Mostrar el mensaje de error del error lanzado
      showError(error.message)
    } else {
      showError('No se pudo crear el lote. Intenta nuevamente.')
    }
  } finally {
    localLoading.value = false
  }
}

const goBack = () => {
  router.push(`/fincas/${fincaId.value}/lotes`)
}

// Lifecycle
onMounted(() => {
  loadFinca()
})
</script>

<style scoped>
/* Transiciones suaves */
.transition-colors {
  transition-property: color, background-color, border-color;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

/* Animación de carga */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>

