<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="flex justify-between items-center p-6 border-b">
        <h2 class="text-xl font-semibold text-gray-900">
          {{ isEditing ? 'Editar Finca' : 'Nueva Finca' }}
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
                  Nombre de la Finca *
                </label>
                <input
                  v-model="formData.nombre"
                  type="text"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  :class="{ 'border-red-500': errors.nombre }"
                />
                <p v-if="errors.nombre" class="text-red-500 text-xs mt-1">{{ errors.nombre }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Hectáreas *
                </label>
                <input
                  v-model="formData.hectareas"
                  type="number"
                  step="0.01"
                  min="0.01"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  :class="{ 'border-red-500': errors.hectareas }"
                />
                <p v-if="errors.hectareas" class="text-red-500 text-xs mt-1">{{ errors.hectareas }}</p>
              </div>
            </div>
          </div>

          <!-- Ubicación -->
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4">Ubicación</h3>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Dirección/Ubicación *
                </label>
                <input
                  v-model="formData.ubicacion"
                  type="text"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  :class="{ 'border-red-500': errors.ubicacion }"
                />
                <p v-if="errors.ubicacion" class="text-red-500 text-xs mt-1">{{ errors.ubicacion }}</p>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Departamento *
                  </label>
                  <select
                    v-model="formData.departamento"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    :class="{ 'border-red-500': errors.departamento }"
                    @change="onDepartamentoChange"
                  >
                    <option value="">Seleccionar departamento</option>
                    <option v-for="dept in departamentos" :key="dept" :value="dept">
                      {{ dept }}
                    </option>
                  </select>
                  <p v-if="errors.departamento" class="text-red-500 text-xs mt-1">{{ errors.departamento }}</p>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Municipio *
                  </label>
                  <select
                    v-model="formData.municipio"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    :class="{ 'border-red-500': errors.municipio }"
                  >
                    <option value="">Seleccionar municipio</option>
                    <option v-for="mun in municipios" :key="mun" :value="mun">
                      {{ mun }}
                    </option>
                  </select>
                  <p v-if="errors.municipio" class="text-red-500 text-xs mt-1">{{ errors.municipio }}</p>
                </div>
              </div>
            </div>
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

          <!-- Estado -->
          <div>
            <label class="flex items-center">
              <input
                v-model="formData.activa"
                type="checkbox"
                class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
              />
              <span class="ml-2 text-sm text-gray-700">Finca activa</span>
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
import fincasApi from '@/services/fincasApi'

const props = defineProps({
  finca: {
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
const municipios = ref([])

// Datos del formulario
const formData = reactive({
  nombre: '',
  ubicacion: '',
  municipio: '',
  departamento: '',
  hectareas: '',
  descripcion: '',
  coordenadas_lat: '',
  coordenadas_lng: '',
  activa: true
})

// Computed
const departamentos = computed(() => fincasApi.getDepartamentosColombia())

// Métodos
const resetForm = () => {
  Object.assign(formData, {
    nombre: '',
    ubicacion: '',
    municipio: '',
    departamento: '',
    hectareas: '',
    descripcion: '',
    coordenadas_lat: '',
    coordenadas_lng: '',
    activa: true
  })
  errors.value = {}
}

const loadFincaData = () => {
  if (props.finca) {
    Object.assign(formData, {
      nombre: props.finca.nombre || '',
      ubicacion: props.finca.ubicacion || '',
      municipio: props.finca.municipio || '',
      departamento: props.finca.departamento || '',
      hectareas: props.finca.hectareas || '',
      descripcion: props.finca.descripcion || '',
      coordenadas_lat: props.finca.coordenadas_lat || '',
      coordenadas_lng: props.finca.coordenadas_lng || '',
      activa: props.finca.activa !== undefined ? props.finca.activa : true
    })
    
    // Cargar municipios si hay departamento
    if (props.finca.departamento) {
      municipios.value = fincasApi.getMunicipiosByDepartamento(props.finca.departamento)
    }
  }
}

const onDepartamentoChange = () => {
  formData.municipio = ''
  municipios.value = fincasApi.getMunicipiosByDepartamento(formData.departamento)
}

const validateForm = () => {
  const formattedData = fincasApi.formatFincaData(formData)
  const validation = fincasApi.validateFincaData(formattedData)
  
  if (!validation.isValid) {
    errors.value = {}
    validation.errors.forEach(error => {
      // Mapear errores a campos específicos
      if (error.includes('nombre')) errors.value.nombre = error
      else if (error.includes('ubicación')) errors.value.ubicacion = error
      else if (error.includes('municipio')) errors.value.municipio = error
      else if (error.includes('departamento')) errors.value.departamento = error
      else if (error.includes('hectáreas')) errors.value.hectareas = error
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
    const formattedData = fincasApi.formatFincaData(formData)
    
    if (props.isEditing) {
      await fincasApi.updateFinca(props.finca.id, formattedData)
    } else {
      await fincasApi.createFinca(formattedData)
    }
    
    emit('saved')
  } catch (error) {
    console.error('Error saving finca:', error)
    
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
watch(() => props.finca, () => {
  if (props.finca) {
    loadFincaData()
  } else {
    resetForm()
  }
}, { immediate: true })

// Lifecycle
onMounted(() => {
  if (props.finca) {
    loadFincaData()
  }
})
</script>
