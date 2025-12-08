<template>
  <Transition name="modal">
    <div class="fixed inset-0 z-[9999] flex items-center justify-center p-4 w-screen h-screen overflow-y-auto overflow-x-hidden backdrop-blur-sm bg-black bg-opacity-50" @click.self="$emit('close')">
    <div class="bg-white rounded-xl shadow-2xl border border-gray-200 relative w-full max-w-3xl max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="bg-gradient-to-r from-green-50 to-green-50 px-6 py-4 border-b border-gray-200 sticky top-0 z-10">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="bg-green-100 p-2 rounded-lg">
              <svg class="text-xl text-green-600 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
              </svg>
            </div>
            <div>
              <h2 class="text-xl font-bold text-gray-900">Crear Nuevo Lote</h2>
              <p class="text-sm text-gray-600">Para la finca: {{ fincaNombre }}</p>
            </div>
          </div>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 transition-all duration-200 p-2 rounded-lg hover:bg-gray-100"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="p-6">
        <div class="space-y-6">
          <!-- Alerta de errores generales -->
          <div v-if="Object.keys(errors).length > 0" class="bg-red-50 border-l-4 border-red-400 p-4 rounded-lg">
            <div class="flex items-start">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="ml-3 flex-1">
                <h3 class="text-sm font-medium text-red-800">Por favor, corrige los siguientes errores:</h3>
                <ul class="mt-2 text-sm text-red-700 list-disc list-inside space-y-1">
                  <li v-for="(error, field) in errors" :key="field">{{ error }}</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Información básica -->
          <div class="bg-gray-50 rounded-lg p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Información Básica</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label for="modal-identificador" class="block text-sm font-medium text-gray-700 mb-2">
                  Identificador * <span class="text-xs text-gray-500">(único en la finca)</span>
                </label>
                <input
                  id="modal-identificador"
                  v-model="formData.identificador"
                  type="text"
                  required
                  class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                  :class="{ 'border-red-500': errors.identificador }"
                  placeholder="Ej: LOTE-001"
                  maxlength="50"
                />
                <p v-if="errors.identificador" class="text-red-500 text-xs mt-1 flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  {{ errors.identificador }}
                </p>
                <p class="text-xs text-gray-500 mt-1">{{ formData.identificador.length }}/50 caracteres</p>
              </div>

              <div>
                <label for="modal-variedad" class="block text-sm font-medium text-gray-700 mb-2">
                  Variedad * <span class="text-xs text-gray-500">(genética del cacao)</span>
                </label>
                <select
                  id="modal-variedad"
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
                <p v-if="errors.variedad" class="text-red-500 text-xs mt-1 flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  {{ errors.variedad }}
                </p>
              </div>

              <div>
                <label for="modal-area" class="block text-sm font-medium text-gray-700 mb-2">
                  Área (hectáreas) * <span class="text-xs text-gray-500">(superficie del lote)</span>
                </label>
                <input
                  id="modal-area"
                  v-model="formData.area_hectareas"
                  type="number"
                  step="0.01"
                  min="0.01"
                  max="1000"
                  required
                  class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                  :class="{ 'border-red-500': errors.area_hectareas }"
                  placeholder="0.00"
                />
                <p v-if="errors.area_hectareas" class="text-red-500 text-xs mt-1 flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  {{ errors.area_hectareas }}
                </p>
              </div>

              <div>
                <label for="modal-estado" class="block text-sm font-medium text-gray-700 mb-2">
                  Estado * <span class="text-xs text-gray-500">(estado actual del lote)</span>
                </label>
                <select
                  id="modal-estado"
                  v-model="formData.estado"
                  required
                  class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                  :class="{ 'border-red-500': errors.estado }"
                >
                  <option value="">Seleccionar estado</option>
                  <option v-for="estado in estadosLote" :key="estado.value" :value="estado.value">
                    {{ estado.label }}
                  </option>
                </select>
                <p v-if="errors.estado" class="text-red-500 text-xs mt-1 flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  {{ errors.estado }}
                </p>
              </div>
            </div>
          </div>

          <!-- Fechas -->
          <div class="bg-blue-50 rounded-lg p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Fechas</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label for="modal-fecha-plantacion" class="block text-sm font-medium text-gray-700 mb-2">
                  Fecha de Plantación * <span class="text-xs text-gray-500">(cuando se sembró)</span>
                </label>
                <input
                  id="modal-fecha-plantacion"
                  v-model="formData.fecha_plantacion"
                  type="date"
                  required
                  :max="maxDate"
                  class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  :class="{ 'border-red-500': errors.fecha_plantacion }"
                />
                <p v-if="errors.fecha_plantacion" class="text-red-500 text-xs mt-1 flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  {{ errors.fecha_plantacion }}
                </p>
              </div>

              <div>
                <label for="modal-fecha-cosecha" class="block text-sm font-medium text-gray-700 mb-2">
                  Fecha de Cosecha <span class="text-xs text-gray-500">(opcional, si ya se cosechó)</span>
                </label>
                <input
                  id="modal-fecha-cosecha"
                  v-model="formData.fecha_cosecha"
                  type="date"
                  :min="formData.fecha_plantacion"
                  :max="maxDate"
                  class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  :class="{ 'border-red-500': errors.fecha_cosecha }"
                />
                <p v-if="errors.fecha_cosecha" class="text-red-500 text-xs mt-1 flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  {{ errors.fecha_cosecha }}
                </p>
              </div>
            </div>
          </div>

          <!-- Coordenadas GPS (opcional) -->
          <div class="bg-purple-50 rounded-lg p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Coordenadas GPS (Opcional)</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label for="modal-latitud" class="block text-sm font-medium text-gray-700 mb-2">
                  Latitud <span class="text-xs text-gray-500">(-90 a 90)</span>
                </label>
                <input
                  id="modal-latitud"
                  v-model="formData.coordenadas_lat"
                  type="number"
                  step="any"
                  min="-90"
                  max="90"
                  class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors"
                  :class="{ 'border-red-500': errors.coordenadas_lat }"
                  placeholder="Ej: 4.6097"
                />
                <p v-if="errors.coordenadas_lat" class="text-red-500 text-xs mt-1 flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  {{ errors.coordenadas_lat }}
                </p>
              </div>

              <div>
                <label for="modal-longitud" class="block text-sm font-medium text-gray-700 mb-2">
                  Longitud <span class="text-xs text-gray-500">(-180 a 180)</span>
                </label>
                <input
                  id="modal-longitud"
                  v-model="formData.coordenadas_lng"
                  type="number"
                  step="any"
                  min="-180"
                  max="180"
                  class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors"
                  :class="{ 'border-red-500': errors.coordenadas_lng }"
                  placeholder="Ej: -74.0817"
                />
                <p v-if="errors.coordenadas_lng" class="text-red-500 text-xs mt-1 flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  {{ errors.coordenadas_lng }}
                </p>
              </div>
            </div>
          </div>

          <!-- Descripción -->
          <div class="bg-gray-50 rounded-lg p-6">
            <label for="modal-descripcion" class="block text-sm font-medium text-gray-700 mb-2">
              Descripción (Opcional) <span class="text-xs text-gray-500">(información adicional)</span>
            </label>
            <textarea
              id="modal-descripcion"
              v-model="formData.descripcion"
              rows="3"
              maxlength="500"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-gray-500 transition-colors resize-none"
              :class="{ 'border-red-500': errors.descripcion }"
              placeholder="Descripción adicional del lote..."
            ></textarea>
            <p v-if="errors.descripcion" class="text-red-500 text-xs mt-1 flex items-center gap-1">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              {{ errors.descripcion }}
            </p>
            <p class="text-xs text-gray-500 mt-1">{{ formData.descripcion.length }}/500 caracteres</p>
          </div>
        </div>

        <!-- Botones -->
        <div class="flex justify-end gap-4 mt-8 pt-6 border-t border-gray-200 bg-gray-50 -mx-6 -mb-6 px-6 py-4 rounded-b-xl">
          <button
            type="button"
            @click="$emit('close')"
            class="px-6 py-3 text-gray-700 bg-white hover:bg-gray-50 border border-gray-300 rounded-lg transition-all duration-200 font-medium shadow-sm hover:shadow-md"
          >
            Cancelar
          </button>
          <button
            type="submit"
            :disabled="loading"
            class="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-medium shadow-sm hover:shadow-md"
          >
            <div v-if="loading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            <svg v-if="!loading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            {{ loading ? 'Creando...' : 'Crear Lote' }}
          </button>
        </div>
      </form>
    </div>
  </div>
  </Transition>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useLotes } from '@/composables/useLotes'
import { useNotifications } from '@/composables/useNotifications'
import lotesApi from '@/services/lotesApi'

const props = defineProps({
  fincaId: {
    type: Number,
    required: true,
    validator: (value) => {
      return value > 0
    }
  },
  fincaNombre: {
    type: String,
    default: 'Finca'
  }
})

const emit = defineEmits(['close', 'lote-created'])

const { createLote, loading: isLotesLoading } = useLotes()
const { showSuccess, showError } = useNotifications()

const localLoading = ref(false)
const errors = ref({})

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

const loading = computed(() => isLotesLoading.value || localLoading.value)
const variedades = computed(() => lotesApi.getVariedadesCacao())
const estadosLote = computed(() => {
  const estados = lotesApi.getEstadosLote()
  return estados || [
    { value: 'activo', label: 'Activo' },
    { value: 'inactivo', label: 'Inactivo' },
    { value: 'cosechado', label: 'Cosechado' }
  ]
})
const maxDate = computed(() => new Date().toISOString().split('T')[0])

const validateForm = () => {
  errors.value = {}
  let isValid = true

  // Validar identificador
  if (!formData.identificador || formData.identificador.trim().length < 2) {
    errors.value.identificador = 'El identificador debe tener al menos 2 caracteres'
    isValid = false
  } else if (formData.identificador.trim().length > 50) {
    errors.value.identificador = 'El identificador no puede exceder 50 caracteres'
    isValid = false
  }

  // Validar variedad
  if (!formData.variedad || formData.variedad.trim().length === 0) {
    errors.value.variedad = 'Debes seleccionar una variedad'
    isValid = false
  }

  // Validar área
  const areaNum = parseFloat(formData.area_hectareas)
  if (!formData.area_hectareas || formData.area_hectareas.toString().trim().length === 0) {
    errors.value.area_hectareas = 'El área es requerida'
    isValid = false
  } else if (isNaN(areaNum)) {
    errors.value.area_hectareas = 'El área debe ser un número válido'
    isValid = false
  } else if (areaNum <= 0) {
    errors.value.area_hectareas = 'El área debe ser mayor a 0'
    isValid = false
  } else if (areaNum > 1000) {
    errors.value.area_hectareas = 'El área no puede exceder 1,000 hectáreas'
    isValid = false
  }

  // Validar fecha de plantación
  if (!formData.fecha_plantacion) {
    errors.value.fecha_plantacion = 'Debes seleccionar una fecha de plantación'
    isValid = false
  } else {
    const fechaPlantacion = new Date(formData.fecha_plantacion)
    const hoy = new Date()
    hoy.setHours(23, 59, 59, 999)
    if (fechaPlantacion > hoy) {
      errors.value.fecha_plantacion = 'La fecha de plantación no puede ser futura'
      isValid = false
    }
  }

  // Validar fecha de cosecha (si se proporciona)
  if (formData.fecha_cosecha) {
    if (formData.fecha_plantacion) {
      const fechaPlantacion = new Date(formData.fecha_plantacion)
      const fechaCosecha = new Date(formData.fecha_cosecha)
      if (fechaCosecha < fechaPlantacion) {
        errors.value.fecha_cosecha = 'La fecha de cosecha no puede ser anterior a la fecha de plantación'
        isValid = false
      }
    }
    const fechaCosecha = new Date(formData.fecha_cosecha)
    const hoy = new Date()
    hoy.setHours(23, 59, 59, 999)
    if (fechaCosecha > hoy) {
      errors.value.fecha_cosecha = 'La fecha de cosecha no puede ser futura'
      isValid = false
    }
  }

  // Validar estado
  if (!formData.estado || formData.estado.trim().length === 0) {
    errors.value.estado = 'Debes seleccionar un estado'
    isValid = false
  }

  // Validar coordenadas (si se proporcionan)
  if (formData.coordenadas_lat && formData.coordenadas_lat.toString().trim().length > 0) {
    const lat = parseFloat(formData.coordenadas_lat)
    if (isNaN(lat)) {
      errors.value.coordenadas_lat = 'La latitud debe ser un número válido'
      isValid = false
    } else if (lat < -90 || lat > 90) {
      errors.value.coordenadas_lat = 'La latitud debe estar entre -90 y 90'
      isValid = false
    }
  }

  if (formData.coordenadas_lng && formData.coordenadas_lng.toString().trim().length > 0) {
    const lng = parseFloat(formData.coordenadas_lng)
    if (isNaN(lng)) {
      errors.value.coordenadas_lng = 'La longitud debe ser un número válido'
      isValid = false
    } else if (lng < -180 || lng > 180) {
      errors.value.coordenadas_lng = 'La longitud debe estar entre -180 y 180'
      isValid = false
    }
  }

  // Validar descripción (si se proporciona)
  if (formData.descripcion && formData.descripcion.length > 500) {
    errors.value.descripcion = 'La descripción no puede exceder 500 caracteres'
    isValid = false
  }

  return isValid
}

const handleSubmit = async () => {
  if (!validateForm()) {
    showError('Por favor, corrige los errores en el formulario antes de continuar')
    return
  }

  localLoading.value = true
  errors.value = {}

  try {
    const loteData = {
      finca: Number(props.fincaId),
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

    const result = await createLote(loteData)
    // El resultado puede venir en diferentes formatos
    let newLote = null
    if (result) {
      if (result.lote) {
        newLote = result.lote
      } else if (result.id) {
        newLote = result
      } else if (typeof result === 'object') {
        newLote = result
      }
    }
    
    // Si no tenemos el lote completo, intentar obtenerlo por ID
    if (newLote && newLote.id) {
      try {
        const { getLoteById } = await import('@/services/lotesApi')
        newLote = await getLoteById(newLote.id)
      } catch (err) {
      }
    }
    
    showSuccess('El lote ha sido creado exitosamente')
    emit('lote-created', newLote)
  } catch (error) {
    
    // Manejar errores del servidor
    if (error.response?.data) {
      const responseData = error.response.data
      const serverErrors = responseData.details || responseData
      
      // Mapear errores del servidor
      Object.keys(serverErrors).forEach(key => {
        if (key !== 'error' && key !== 'status') {
          const errorValue = serverErrors[key]
          errors.value[key] = Array.isArray(errorValue) ? errorValue[0] : String(errorValue)
        }
      })
      
      const errorMessage = responseData.error || responseData.detail || 'No se pudo crear el lote'
      showError(errorMessage)
    } else {
      showError(error.message || 'No se pudo crear el lote. Intenta nuevamente.')
    }
  } finally {
    localLoading.value = false
  }
}
</script>

<style scoped>
/* Transiciones del modal */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .bg-white,
.modal-leave-active .bg-white {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.modal-enter-from .bg-white,
.modal-leave-to .bg-white {
  transform: scale(0.9);
  opacity: 0;
}
</style>

