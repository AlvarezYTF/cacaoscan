<template>
  <Transition name="modal">
    <div class="fixed inset-0 z-[9999] flex items-center justify-center p-4 w-screen h-screen overflow-y-auto overflow-x-hidden backdrop-blur-sm" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-lg border border-gray-200 relative w-full max-w-3xl max-h-[90vh] overflow-y-auto">
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
              <p class="text-sm text-gray-600">Bulto de granos para la finca: {{ fincaNombre }}</p>
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
          <div v-if="generalError || Object.keys(errors).length > 0" class="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-r-lg">
            <div class="flex items-start">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="ml-3 flex-1">
                <h3 class="text-sm font-semibold text-red-800">
                  <span v-if="generalError">{{ generalError }}</span>
                  <span v-else-if="Object.keys(errors).length > 0">Por favor corrige los siguientes errores:</span>
                </h3>
                <ul v-if="Object.keys(errors).length > 0" class="mt-2 list-disc list-inside text-sm text-red-700">
                  <li v-for="(error, field) in errors" :key="field">{{ error }}</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Información básica -->
          <div class="bg-gray-50 rounded-lg p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Información del Bulto</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label for="modal-identificador" class="block text-sm font-medium text-gray-700 mb-2">
                  Identificador <span class="text-xs text-gray-500">(opcional, único en la finca)</span>
                </label>
                <input
                  id="modal-identificador"
                  v-model="formData.identificador"
                  type="text"
                  class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                  :class="{ 'border-red-500': errors.identificador }"
                  placeholder="Ej: BULTO-001"
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
                <label for="modal-nombre" class="block text-sm font-medium text-gray-700 mb-2">
                  Nombre/Descripción <span class="text-xs text-gray-500">(opcional, se usa si no hay identificador)</span>
                </label>
                <input
                  id="modal-nombre"
                  v-model="formData.nombre"
                  type="text"
                  class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                  :class="{ 'border-red-500': errors.nombre }"
                  placeholder="Ej: Bulto de cacao premium"
                  maxlength="200"
                />
                <p v-if="errors.nombre" class="text-red-500 text-xs mt-1 flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  {{ errors.nombre }}
                </p>
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
                  <option v-for="variedad in variedades" :key="variedad.id" :value="variedad.id">
                    {{ variedad.nombre }}
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
                <label for="modal-peso" class="block text-sm font-medium text-gray-700 mb-2">
                  Peso (kg) * <span class="text-xs text-gray-500">(peso del bulto en kilogramos)</span>
                </label>
                <input
                  id="modal-peso"
                  v-model="formData.peso_kg"
                  type="number"
                  step="0.01"
                  min="0.01"
                  max="100000"
                  required
                  class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                  :class="{ 'border-red-500': errors.peso_kg }"
                  placeholder="0.00"
                />
                <p v-if="errors.peso_kg" class="text-red-500 text-xs mt-1 flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  {{ errors.peso_kg }}
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
                  <option v-for="estado in estadosLote" :key="estado.id" :value="estado.id">
                    {{ estado.nombre }}
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
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Fechas del Bulto</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label for="modal-fecha-recepcion" class="block text-sm font-medium text-gray-700 mb-2">
                  Fecha de Recepción * <span class="text-xs text-gray-500">(cuándo se recibió el bulto)</span>
                </label>
                <input
                  id="modal-fecha-recepcion"
                  v-model="formData.fecha_recepcion"
                  type="date"
                  required
                  :max="maxDate"
                  class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  :class="{ 'border-red-500': errors.fecha_recepcion }"
                />
                <p v-if="errors.fecha_recepcion" class="text-red-500 text-xs mt-1 flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  {{ errors.fecha_recepcion }}
                </p>
              </div>

              <div>
                <label for="modal-fecha-procesamiento" class="block text-sm font-medium text-gray-700 mb-2">
                  Fecha de Procesamiento <span class="text-xs text-gray-500">(opcional, fermentación/procesamiento)</span>
                </label>
                <input
                  id="modal-fecha-procesamiento"
                  v-model="formData.fecha_procesamiento"
                  type="date"
                  :min="formData.fecha_recepcion"
                  :max="maxDate"
                  class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  :class="{ 'border-red-500': errors.fecha_procesamiento }"
                />
                <p v-if="errors.fecha_procesamiento" class="text-red-500 text-xs mt-1 flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  {{ errors.fecha_procesamiento }}
                </p>
              </div>

              <div>
                <label for="modal-fecha-plantacion" class="block text-sm font-medium text-gray-700 mb-2">
                  Fecha de Plantación <span class="text-xs text-gray-500">(opcional, cuando se sembró)</span>
                </label>
                <input
                  id="modal-fecha-plantacion"
                  v-model="formData.fecha_plantacion"
                  type="date"
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
                  Fecha de Cosecha <span class="text-xs text-gray-500">(opcional, cuando se cosechó)</span>
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

        <!-- Alerta de errores encima de los botones -->
        <div v-if="generalError || Object.keys(errors).length > 0" class="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-r-lg">
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div class="ml-3 flex-1">
              <h3 class="text-sm font-semibold text-red-800">
                <span v-if="generalError">{{ generalError }}</span>
                <span v-else-if="Object.keys(errors).length > 0">Por favor corrige los siguientes errores:</span>
              </h3>
              <ul v-if="Object.keys(errors).length > 0" class="mt-2 list-disc list-inside text-sm text-red-700">
                <li v-for="(error, field) in errors" :key="field">{{ error }}</li>
              </ul>
            </div>
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useLotes } from '@/composables/useLotes'
import { useNotifications } from '@/composables/useNotifications'
import lotesApi from '@/services/lotesApi'
import catalogosApi from '@/services/catalogosApi'

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
const generalError = ref('')

const formData = reactive({
  identificador: '',
  nombre: '',
  variedad: '',
  peso_kg: '',
  fecha_recepcion: '',
  fecha_procesamiento: '',
  fecha_plantacion: '',
  fecha_cosecha: '',
  estado: '',
  descripcion: '',
  activo: true
})

const loading = computed(() => isLotesLoading.value || localLoading.value || loadingParametros.value)
const maxDate = computed(() => new Date().toISOString().split('T')[0])

// Parámetros desde la API
const variedades = ref([])
const estadosLote = ref([])
const loadingParametros = ref(false)

// Cargar parámetros desde la API
const loadParametros = async () => {
  loadingParametros.value = true
  try {
    // Cargar variedades de cacao
    const variedadesData = await catalogosApi.getParametrosPorTema('TEMA_VARIEDAD_CACAO')
    const variedadesList = Array.isArray(variedadesData?.results) 
      ? variedadesData.results 
      : Array.isArray(variedadesData) 
        ? variedadesData 
        : []
    variedades.value = variedadesList.map(p => ({
      id: p.id,
      nombre: p.nombre || p.codigo || String(p.id),
      codigo: p.codigo
    }))
    
    // Cargar estados de lote
    const estadosData = await catalogosApi.getParametrosPorTema('TEMA_ESTADO_LOTE')
    const estadosList = Array.isArray(estadosData?.results) 
      ? estadosData.results 
      : Array.isArray(estadosData) 
        ? estadosData 
        : []
    estadosLote.value = estadosList.map(p => ({
      id: p.id,
      nombre: p.nombre || p.codigo || String(p.id),
      codigo: p.codigo
    }))
  } catch (error) {
    console.error('Error cargando parámetros:', error)
    // Fallback a valores por defecto si falla la carga
    variedades.value = []
    estadosLote.value = []
  } finally {
    loadingParametros.value = false
  }
}

const validateForm = () => {
  errors.value = {}
  generalError.value = ''
  let isValid = true

  // Validar identificador (opcional, pero si se proporciona debe ser válido)
  if (formData.identificador && formData.identificador.trim().length > 0) {
    if (formData.identificador.trim().length < 2) {
      errors.value.identificador = 'El identificador debe tener al menos 2 caracteres'
      isValid = false
    } else if (formData.identificador.trim().length > 50) {
      errors.value.identificador = 'El identificador no puede exceder 50 caracteres'
      isValid = false
    }
  }

  // Validar variedad (debe ser un ID numérico)
  if (!formData.variedad) {
    errors.value.variedad = 'Debes seleccionar una variedad'
    isValid = false
  } else {
    const variedadId = Number(formData.variedad)
    if (isNaN(variedadId) || variedadId <= 0) {
      errors.value.variedad = 'Debes seleccionar una variedad válida'
      isValid = false
    }
  }

  // Validar nombre (si no hay identificador, el nombre es requerido)
  if (!formData.nombre || formData.nombre.trim().length === 0) {
    if (!formData.identificador || formData.identificador.trim().length === 0) {
      errors.value.nombre = 'El nombre o identificador es requerido'
      isValid = false
    }
  }

  // Validar peso
  const pesoNum = parseFloat(formData.peso_kg)
  if (!formData.peso_kg || formData.peso_kg.toString().trim().length === 0) {
    errors.value.peso_kg = 'El peso es requerido'
    isValid = false
  } else if (isNaN(pesoNum)) {
    errors.value.peso_kg = 'El peso debe ser un número válido'
    isValid = false
  } else if (pesoNum <= 0) {
    errors.value.peso_kg = 'El peso debe ser mayor a 0'
    isValid = false
  } else if (pesoNum > 100000) {
    errors.value.peso_kg = 'El peso no puede exceder 100,000 kg'
    isValid = false
  }

  // Validar fecha de recepción (requerida)
  if (!formData.fecha_recepcion) {
    errors.value.fecha_recepcion = 'Debes seleccionar una fecha de recepción'
    isValid = false
  } else {
    const fechaRecepcion = new Date(formData.fecha_recepcion)
    const hoy = new Date()
    hoy.setHours(23, 59, 59, 999)
    if (fechaRecepcion > hoy) {
      errors.value.fecha_recepcion = 'La fecha de recepción no puede ser futura'
      isValid = false
    }
  }

  // Validar fecha de procesamiento (si se proporciona)
  if (formData.fecha_procesamiento) {
    if (formData.fecha_recepcion) {
      const fechaRecepcion = new Date(formData.fecha_recepcion)
      const fechaProcesamiento = new Date(formData.fecha_procesamiento)
      if (fechaProcesamiento < fechaRecepcion) {
        errors.value.fecha_procesamiento = 'La fecha de procesamiento no puede ser anterior a la fecha de recepción'
        isValid = false
      }
    }
    const fechaProcesamiento = new Date(formData.fecha_procesamiento)
    const hoy = new Date()
    hoy.setHours(23, 59, 59, 999)
    if (fechaProcesamiento > hoy) {
      errors.value.fecha_procesamiento = 'La fecha de procesamiento no puede ser futura'
      isValid = false
    }
  }

  // Validar fecha de plantación (opcional, pero si se proporciona debe ser válida)
  if (formData.fecha_plantacion) {
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

  // Validar estado (debe ser un ID numérico, requerido)
  if (!formData.estado) {
    errors.value.estado = 'Debes seleccionar un estado'
    isValid = false
  } else {
    const estadoId = Number(formData.estado)
    if (isNaN(estadoId) || estadoId <= 0) {
      errors.value.estado = 'Debes seleccionar un estado válido'
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
  generalError.value = ''

  try {
    const loteData = {
      finca: Number(props.fincaId),
      identificador: formData.identificador.trim() || null,
      nombre: formData.nombre.trim() || formData.identificador.trim() || 'Bulto de cacao',
      variedad: Number(formData.variedad), // Asegurar que es un número
      peso_kg: parseFloat(formData.peso_kg),
      fecha_recepcion: formData.fecha_recepcion,
      fecha_procesamiento: formData.fecha_procesamiento || null,
      fecha_plantacion: formData.fecha_plantacion || null,
      fecha_cosecha: formData.fecha_cosecha || null,
      estado: Number(formData.estado),
      descripcion: formData.descripcion.trim() || null,
      activo: formData.activo
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
    console.error('Error al crear lote:', error)
    console.error('Error response:', error.response)
    console.error('Error data:', error.response?.data)
    
    // Limpiar errores previos
    errors.value = {}
    generalError.value = ''
    
    // Manejar errores del servidor
    if (error.response?.data) {
      const responseData = error.response.data
      
      // Extraer mensaje de error general (autenticación, permisos, etc.)
      const generalErrorMessage = responseData.error || responseData.detail || responseData.message
      if (generalErrorMessage) {
        generalError.value = String(generalErrorMessage)
        showError(generalErrorMessage)
      }
      
      // Mapear errores de campos específicos
      const serverErrors = responseData.details || responseData
      if (typeof serverErrors === 'object' && serverErrors !== null) {
        Object.keys(serverErrors).forEach(key => {
          // Ignorar campos que son mensajes generales
          if (key !== 'error' && key !== 'status' && key !== 'detail' && key !== 'message') {
            const errorValue = serverErrors[key]
            if (errorValue) {
              errors.value[key] = Array.isArray(errorValue) ? errorValue[0] : String(errorValue)
            }
          }
        })
      }
      
      // Si no hay mensaje general pero hay errores de campos, mostrar mensaje genérico
      if (!generalError.value && Object.keys(errors.value).length > 0) {
        generalError.value = 'Por favor, corrige los errores en el formulario'
      } else if (!generalError.value) {
        generalError.value = 'No se pudo crear el lote. Por favor, intenta nuevamente.'
        showError(generalError.value)
      }
    } else {
      // Error de red u otro error sin respuesta del servidor
      const errorMessage = error.message || 'No se pudo crear el lote. Verifica tu conexión e intenta nuevamente.'
      generalError.value = errorMessage
      showError(errorMessage)
    }
  } finally {
    localLoading.value = false
  }
}

// Cargar parámetros al montar el componente
onMounted(() => {
  loadParametros()
})
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

