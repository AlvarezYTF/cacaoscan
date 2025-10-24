<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="flex justify-between items-center p-6 border-b">
        <h2 class="text-xl font-semibold text-gray-900">
          {{ isEditing ? 'Editar Lote' : 'Nuevo Lote' }}
        </h2>
        <button
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="p-6">
        <div class="space-y-6">
          <!-- Información básica -->
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4">Información Básica</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Finca *
                </label>
                <select
                  v-model="formData.finca"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  :class="{ 'border-red-500': errors.finca }"
                >
                  <option value="">Seleccionar finca</option>
                  <option v-for="finca in fincas" :key="finca.id" :value="finca.id">
                    {{ finca.nombre }}
                  </option>
                </select>
                <p v-if="errors.finca" class="text-red-500 text-xs mt-1">{{ errors.finca }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Identificador *
                </label>
                <input
                  v-model="formData.identificador"
                  type="text"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  :class="{ 'border-red-500': errors.identificador }"
                />
                <p v-if="errors.identificador" class="text-red-500 text-xs mt-1">{{ errors.identificador }}</p>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Variedad *
                </label>
                <select
                  v-model="formData.variedad"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  :class="{ 'border-red-500': errors.variedad }"
                >
                  <option value="">Seleccionar variedad</option>
                  <option v-for="variedad in variedades" :key="variedad" :value="variedad">
                    {{ variedad }}
                  </option>
                </select>
                <p v-if="errors.variedad" class="text-red-500 text-xs mt-1">{{ errors.variedad }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Área (hectáreas) *
                </label>
                <input
                  v-model="formData.area_hectareas"
                  type="number"
                  step="0.01"
                  min="0.01"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  :class="{ 'border-red-500': errors.area_hectareas }"
                />
                <p v-if="errors.area_hectareas" class="text-red-500 text-xs mt-1">{{ errors.area_hectareas }}</p>
              </div>
            </div>
          </div>

          <!-- Fechas -->
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4">Fechas</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Fecha de Plantación *
                </label>
                <input
                  v-model="formData.fecha_plantacion"
                  type="date"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  :class="{ 'border-red-500': errors.fecha_plantacion }"
                />
                <p v-if="errors.fecha_plantacion" class="text-red-500 text-xs mt-1">{{ errors.fecha_plantacion }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Fecha de Cosecha
                </label>
                <input
                  v-model="formData.fecha_cosecha"
                  type="date"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  :class="{ 'border-red-500': errors.fecha_cosecha }"
                />
                <p v-if="errors.fecha_cosecha" class="text-red-500 text-xs mt-1">{{ errors.fecha_cosecha }}</p>
              </div>
            </div>
          </div>

          <!-- Estado -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Estado del Lote *
            </label>
            <select
              v-model="formData.estado"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              :class="{ 'border-red-500': errors.estado }"
            >
              <option value="">Seleccionar estado</option>
              <option v-for="estado in estadosLote" :key="estado.value" :value="estado.value">
                {{ estado.label }}
              </option>
            </select>
            <p v-if="errors.estado" class="text-red-500 text-xs mt-1">{{ errors.estado }}</p>
          </div>

          <!-- Coordenadas GPS (opcional) -->
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4">Coordenadas GPS (Opcional)</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Latitud
                </label>
                <input
                  v-model="formData.coordenadas_lat"
                  type="number"
                  step="any"
                  min="-90"
                  max="90"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  :class="{ 'border-red-500': errors.coordenadas_lat }"
                />
                <p v-if="errors.coordenadas_lat" class="text-red-500 text-xs mt-1">{{ errors.coordenadas_lat }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Longitud
                </label>
                <input
                  v-model="formData.coordenadas_lng"
                  type="number"
                  step="any"
                  min="-180"
                  max="180"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  :class="{ 'border-red-500': errors.coordenadas_lng }"
                />
                <p v-if="errors.coordenadas_lng" class="text-red-500 text-xs mt-1">{{ errors.coordenadas_lng }}</p>
              </div>
            </div>
          </div>

          <!-- Descripción -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Descripción (Opcional)
            </label>
            <textarea
              v-model="formData.descripcion"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              :class="{ 'border-red-500': errors.descripcion }"
            ></textarea>
            <p v-if="errors.descripcion" class="text-red-500 text-xs mt-1">{{ errors.descripcion }}</p>
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
            @click="$emit('close')"
            class="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md transition-colors"
          >
            Cancelar
          </button>
          <button
            type="submit"
            :disabled="loading"
            class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <div v-if="loading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            {{ loading ? 'Guardando...' : (isEditing ? 'Actualizar' : 'Crear') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import lotesApi from '@/services/lotesApi'
import fincasApi from '@/services/fincasApi'

const props = defineProps({
  lote: {
    type: Object,
    default: null
  },
  isEditing: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'saved'])

// Estado reactivo
const loading = ref(false)
const errors = ref({})
const fincas = ref([])

// Datos del formulario
const formData = reactive({
  finca: '',
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
const estadosLote = computed(() => lotesApi.getEstadosLote())

// Métodos
const resetForm = () => {
  Object.assign(formData, {
    finca: '',
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
  errors.value = {}
}

const loadLoteData = () => {
  if (props.lote) {
    Object.assign(formData, {
      finca: props.lote.finca?.id || '',
      identificador: props.lote.identificador || '',
      variedad: props.lote.variedad || '',
      fecha_plantacion: props.lote.fecha_plantacion || '',
      fecha_cosecha: props.lote.fecha_cosecha || '',
      area_hectareas: props.lote.area_hectareas || '',
      estado: props.lote.estado || 'activo',
      descripcion: props.lote.descripcion || '',
      coordenadas_lat: props.lote.coordenadas_lat || '',
      coordenadas_lng: props.lote.coordenadas_lng || '',
      activa: props.lote.activa !== undefined ? props.lote.activa : true
    })
  }
}

const loadFincas = async () => {
  try {
    const response = await fincasApi.getFincas()
    fincas.value = response.results || response
  } catch (error) {
    console.error('Error loading fincas:', error)
  }
}

const validateForm = () => {
  const formattedData = lotesApi.formatLoteData(formData)
  const validation = lotesApi.validateLoteData(formattedData)
  
  if (!validation.isValid) {
    errors.value = {}
    validation.errors.forEach(error => {
      // Mapear errores a campos específicos
      if (error.includes('finca')) errors.value.finca = error
      else if (error.includes('identificador')) errors.value.identificador = error
      else if (error.includes('variedad')) errors.value.variedad = error
      else if (error.includes('plantación')) errors.value.fecha_plantacion = error
      else if (error.includes('cosecha')) errors.value.fecha_cosecha = error
      else if (error.includes('área')) errors.value.area_hectareas = error
      else if (error.includes('latitud')) errors.value.coordenadas_lat = error
      else if (error.includes('longitud')) errors.value.coordenadas_lng = error
      else if (error.includes('descripción')) errors.value.descripcion = error
    })
    return false
  }
  
  errors.value = {}
  return true
}

const handleSubmit = async () => {
  if (!validateForm()) return
  
  loading.value = true
  
  try {
    const formattedData = lotesApi.formatLoteData(formData)
    
    if (props.isEditing) {
      await lotesApi.updateLote(props.lote.id, formattedData)
    } else {
      await lotesApi.createLote(formattedData)
    }
    
    emit('saved')
  } catch (error) {
    console.error('Error saving lote:', error)
    
    // Manejar errores de validación del servidor
    if (error.response?.data) {
      const serverErrors = error.response.data
      errors.value = {}
      
      Object.keys(serverErrors).forEach(field => {
        if (Array.isArray(serverErrors[field])) {
          errors.value[field] = serverErrors[field][0]
        } else {
          errors.value[field] = serverErrors[field]
        }
      })
    }
  } finally {
    loading.value = false
  }
}

// Watchers
watch(() => props.lote, () => {
  if (props.lote) {
    loadLoteData()
  } else {
    resetForm()
  }
}, { immediate: true })

// Lifecycle
onMounted(() => {
  loadFincas()
  if (props.lote) {
    loadLoteData()
  }
})
</script>
