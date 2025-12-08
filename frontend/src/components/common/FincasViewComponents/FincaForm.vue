<template>
  <div class="fixed inset-0 z-[9999] flex items-center justify-center p-4 w-screen h-screen overflow-y-auto overflow-x-hidden backdrop-blur-sm">
    <div class="bg-white rounded-lg shadow-lg border border-gray-200 relative w-full max-w-2xl max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="bg-gradient-to-r from-green-50 to-green-50 px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <div class="bg-green-100 p-2 rounded-lg mr-3">
              <svg v-if="isEditing" class="text-xl text-green-600 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
              </svg>
              <svg v-else class="text-xl text-green-600 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
              </svg>
            </div>
            <div>
              <h2 class="text-xl font-bold text-gray-900">
                {{ isEditing ? 'Editar Finca' : 'Nueva Finca' }}
              </h2>
              <p class="text-sm text-gray-600">{{ isEditing ? 'Modifica los datos de la finca' : 'Registra una nueva finca en el sistema' }}</p>
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
        <div class="space-y-8">
          <!-- Alerta de errores generales -->
          <div v-if="Object.keys(errors).length > 0" class="bg-red-50 border-l-4 border-red-400 p-4 rounded-lg mb-6">
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
            <div class="flex items-center mb-4">
              <div class="bg-green-100 p-2 rounded-lg mr-3">
                <svg class="text-lg text-green-600 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
              </div>
              <h3 class="text-lg font-bold text-gray-900">Información Básica</h3>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label for="finca-form-nombre" class="block text-sm font-semibold text-gray-700 mb-2">
                  Nombre de la Finca *
                </label>
                <input
                  id="finca-form-nombre"
                  v-model="formData.nombre"
                  name="nombre"
                  type="text"
                  required
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors"
                  :class="{ 'border-red-500 focus:ring-red-500': errors.nombre }"
                  placeholder="Ingresa el nombre de la finca"
                />
                <p v-if="errors.nombre" class="text-red-500 text-xs mt-2 flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  {{ errors.nombre }}
                </p>
              </div>

              <div>
                <label for="finca-form-hectareas" class="block text-sm font-semibold text-gray-700 mb-2">
                  Hectáreas *
                </label>
                <input
                  id="finca-form-hectareas"
                  v-model="formData.hectareas"
                  name="hectareas"
                  type="number"
                  step="0.01"
                  min="0.01"
                  required
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors"
                  :class="{ 'border-red-500 focus:ring-red-500': errors.hectareas }"
                  placeholder="0.00"
                />
                <p v-if="errors.hectareas" class="text-red-500 text-xs mt-2 flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  {{ errors.hectareas }}
                </p>
              </div>

              <!-- Select de agricultor (solo para admin en modo creación) -->
              <div v-if="isAdmin && !isEditing" class="md:col-span-2">
                <label for="finca-form-agricultor" class="block text-sm font-semibold text-gray-700 mb-2">
                  Agricultor asignado *
                </label>
                <select
                  id="finca-form-agricultor"
                  v-model="formData.agricultor"
                  name="agricultor"
                  required
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors bg-white"
                  :class="{ 'border-red-500 focus:ring-red-500': errors.agricultor }"
                >
                  <option value="">Selecciona un agricultor</option>
                  <option v-for="a in agricultores" :key="a.id" :value="a.id">
                    {{ a.username }}
                  </option>
                </select>
                <p v-if="errors.agricultor" class="text-red-500 text-xs mt-2 flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  {{ errors.agricultor }}
                </p>
              </div>
            </div>
          </div>

          <!-- Ubicación -->
          <div class="bg-blue-50 rounded-lg p-6">
            <div class="flex items-center mb-4">
              <div class="bg-blue-100 p-2 rounded-lg mr-3">
                <svg class="text-lg text-blue-600 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
              </div>
              <h3 class="text-lg font-bold text-gray-900">Ubicación</h3>
            </div>
            <div class="space-y-6">
              <div>
                <label for="finca-form-ubicacion" class="block text-sm font-semibold text-gray-700 mb-2">
                  Dirección/Ubicación *
                </label>
                <input
                  id="finca-form-ubicacion"
                  v-model="formData.ubicacion"
                  name="ubicacion"
                  type="text"
                  required
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  :class="{ 'border-red-500 focus:ring-red-500': errors.ubicacion }"
                  placeholder="Ingresa la dirección completa de la finca"
                />
                <p v-if="errors.ubicacion" class="text-red-500 text-xs mt-2 flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  {{ errors.ubicacion }}
                </p>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label for="finca-form-departamento" class="block text-sm font-semibold text-gray-700 mb-2">
                    Departamento *
                  </label>
                  <select
                    id="finca-form-departamento"
                    v-model="formData.departamento"
                    name="departamento"
                    required
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors bg-white"
                    :class="{ 'border-red-500 focus:ring-red-500': errors.departamento }"
                    @change="onDepartamentoChange"
                  >
                    <option value="">Seleccionar departamento</option>
                    <option v-for="dept in departamentos" :key="dept" :value="dept">
                      {{ dept }}
                    </option>
                  </select>
                  <p v-if="errors.departamento" class="text-red-500 text-xs mt-2 flex items-center gap-1">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                    {{ errors.departamento }}
                  </p>
                </div>

                <div>
                  <label for="finca-form-municipio" class="block text-sm font-semibold text-gray-700 mb-2">
                    Municipio *
                  </label>
                  <select
                    id="finca-form-municipio"
                    v-model="formData.municipio"
                    name="municipio"
                    required
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors bg-white"
                    :class="{ 'border-red-500 focus:ring-red-500': errors.municipio }"
                  >
                    <option value="">Seleccionar municipio</option>
                    <option v-for="mun in municipios" :key="mun" :value="mun">
                      {{ mun }}
                    </option>
                  </select>
                  <p v-if="errors.municipio" class="text-red-500 text-xs mt-2 flex items-center gap-1">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                    {{ errors.municipio }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Coordenadas GPS (opcional) -->
          <div class="bg-purple-50 rounded-lg p-6">
            <div class="flex items-center mb-4">
              <div class="bg-purple-100 p-2 rounded-lg mr-3">
                <svg class="text-lg text-purple-600 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path>
                </svg>
              </div>
              <h3 class="text-lg font-bold text-gray-900">Coordenadas GPS (Opcional)</h3>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label for="finca-form-latitud" class="block text-sm font-semibold text-gray-700 mb-2">
                  Latitud
                </label>
                <input
                  id="finca-form-latitud"
                  v-model="formData.coordenadas_lat"
                  name="coordenadas_lat"
                  type="number"
                  step="any"
                  min="-90"
                  max="90"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-colors"
                  :class="{ 'border-red-500 focus:ring-red-500': errors.coordenadas_lat }"
                  placeholder="-90.000000 a 90.000000"
                />
                <p v-if="errors.coordenadas_lat" class="text-red-500 text-xs mt-2 flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  {{ errors.coordenadas_lat }}
                </p>
              </div>

              <div>
                <label for="finca-form-longitud" class="block text-sm font-semibold text-gray-700 mb-2">
                  Longitud
                </label>
                <input
                  id="finca-form-longitud"
                  v-model="formData.coordenadas_lng"
                  name="coordenadas_lng"
                  type="number"
                  step="any"
                  min="-180"
                  max="180"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-colors"
                  :class="{ 'border-red-500 focus:ring-red-500': errors.coordenadas_lng }"
                  placeholder="-180.000000 a 180.000000"
                />
                <p v-if="errors.coordenadas_lng" class="text-red-500 text-xs mt-2 flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                  </svg>
                  {{ errors.coordenadas_lng }}
                </p>
              </div>
            </div>
          </div>

          <!-- Información adicional -->
          <div class="bg-gray-50 rounded-lg p-6">
            <div class="flex items-center mb-4">
              <div class="bg-gray-100 p-2 rounded-lg mr-3">
                <svg class="text-lg text-gray-600 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <h3 class="text-lg font-bold text-gray-900">Información Adicional</h3>
            </div>

            <!-- Descripción -->
            <div class="mb-6">
              <label for="finca-form-descripcion" class="block text-sm font-semibold text-gray-700 mb-2">
                Descripción (Opcional)
              </label>
              <textarea
                id="finca-form-descripcion"
                v-model="formData.descripcion"
              name="descripcion"
                rows="3"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-500 focus:border-transparent transition-colors resize-none"
                :class="{ 'border-red-500 focus:ring-red-500': errors.descripcion }"
                placeholder="Agrega una descripción detallada de la finca..."
              ></textarea>
              <p v-if="errors.descripcion" class="text-red-500 text-xs mt-2 flex items-center gap-1">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                {{ errors.descripcion }}
              </p>
            </div>

            <!-- Estado -->
            <div class="bg-white rounded-lg p-4 border border-gray-200">
              <label class="flex items-center cursor-pointer">
                <input
                  v-model="formData.activa"
                  type="checkbox"
                  class="h-5 w-5 text-green-600 focus:ring-green-500 border-gray-300 rounded transition-colors"
                />
                <span class="ml-3 text-sm font-medium text-gray-700">Finca activa</span>
              </label>
              <p class="text-xs text-gray-500 mt-2 ml-8">Las fincas activas pueden recibir análisis y gestionar lotes</p>
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
              <path v-if="isEditing" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            {{ loading ? 'Guardando...' : (isEditing ? 'Actualizar Finca' : 'Crear Finca') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import fincasApi, { getAgricultores } from '@/services/fincasApi'
import { useFincasStore } from '@/stores/fincas'
import { useAuthStore } from '@/stores/auth'
import { useFormValidation } from '@/composables/useFormValidation'
import { useNotifications } from '@/composables/useNotifications'
import { useFincas } from '@/composables/useFincas'

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

const fincasStore = useFincasStore()
const authStore = useAuthStore()
const { errors, mapServerErrors, scrollToFirstError } = useFormValidation()
const { showSuccess, showError } = useNotifications()
const { create: createFincaComposable, update: updateFincaComposable, isLoading: isFincasLoading } = useFincas({
  onFincaCreate: () => {
    showSuccess('La finca se creó correctamente.')
  },
  onFincaUpdate: () => {
    showSuccess('La finca se actualizó correctamente.')
  }
})

// Estado reactivo - combinar loading del composable con estado local del formulario
const localLoading = ref(false)
const loading = computed(() => localLoading.value || isFincasLoading.value)
const municipios = ref([])
const agricultores = ref([])

// Computed
const isAdmin = computed(() => authStore.isAdmin)

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
  activa: true,
  agricultor: ''
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
    activa: true,
    agricultor: ''
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
      activa: props.finca.activa ?? true
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

const mapValidationErrorToField = (error) => {
  const errorMapping = {
    'nombre': 'nombre',
    'ubicación': 'ubicacion',
    'municipio': 'municipio',
    'departamento': 'departamento',
    'hectáreas': 'hectareas',
    'latitud': 'coordenadas_lat',
    'longitud': 'coordenadas_lng',
    'descripción': 'descripcion'
  }
  
  for (const [key, field] of Object.entries(errorMapping)) {
    if (error.includes(key)) {
      return field
    }
  }
  return null
}

const validateForm = () => {
  // Limpiar errores previos
  errors.value = {}
  let isValid = true
  
  // Validar nombre
  if (!formData.nombre || formData.nombre.trim().length === 0) {
    errors.value.nombre = 'El nombre de la finca es requerido'
    isValid = false
  } else if (formData.nombre.trim().length < 3) {
    errors.value.nombre = 'El nombre debe tener al menos 3 caracteres'
    isValid = false
  } else if (formData.nombre.trim().length > 200) {
    errors.value.nombre = 'El nombre no puede exceder 200 caracteres'
    isValid = false
  }
  
  // Validar ubicación
  if (!formData.ubicacion || formData.ubicacion.trim().length === 0) {
    errors.value.ubicacion = 'La ubicación es requerida'
    isValid = false
  } else if (formData.ubicacion.trim().length < 5) {
    errors.value.ubicacion = 'La ubicación debe tener al menos 5 caracteres'
    isValid = false
  } else if (formData.ubicacion.trim().length > 300) {
    errors.value.ubicacion = 'La ubicación no puede exceder 300 caracteres'
    isValid = false
  }
  
  // Validar departamento
  if (!formData.departamento || formData.departamento.trim().length === 0) {
    errors.value.departamento = 'El departamento es requerido'
    isValid = false
  }
  
  // Validar municipio
  if (!formData.municipio || formData.municipio.trim().length === 0) {
    errors.value.municipio = 'El municipio es requerido'
    isValid = false
  }
  
  // Validar hectáreas
  const hectareasNum = parseFloat(formData.hectareas)
  if (!formData.hectareas || formData.hectareas.toString().trim().length === 0) {
    errors.value.hectareas = 'Las hectáreas son requeridas'
    isValid = false
  } else if (isNaN(hectareasNum)) {
    errors.value.hectareas = 'Las hectáreas deben ser un número válido'
    isValid = false
  } else if (hectareasNum <= 0) {
    errors.value.hectareas = 'Las hectáreas deben ser mayor a 0'
    isValid = false
  } else if (hectareasNum > 999999.99) {
    errors.value.hectareas = 'Las hectáreas no pueden exceder 999,999.99'
    isValid = false
  }
  
  // Validar agricultor (solo para admin en creación)
  if (isAdmin.value && !props.isEditing) {
    if (!formData.agricultor || formData.agricultor.toString().trim().length === 0) {
      errors.value.agricultor = 'Debes seleccionar un agricultor'
      isValid = false
    }
  }
  
  // Validar coordenadas GPS (opcional, pero si se proporcionan deben ser válidas)
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
  
  // Validar descripción (opcional, pero si se proporciona tiene límite)
  if (formData.descripcion && formData.descripcion.length > 1000) {
    errors.value.descripcion = 'La descripción no puede exceder 1000 caracteres'
    isValid = false
  }
  
  // Si hay errores, mostrar alerta y hacer scroll al primer error
  if (!isValid) {
    showError('Por favor, corrige los errores en el formulario antes de continuar')
    scrollToFirstError('finca-form')
  }
  
  return isValid
}

// Helper functions to reduce complexity
const getFieldMapping = () => ({
  'nombre': 'nombre',
  'ubicacion': 'ubicacion',
  'municipio': 'municipio',
  'departamento': 'departamento',
  'hectareas': 'hectareas',
  'coordenadas_lat': 'coordenadas_lat',
  'coordenadas_lng': 'coordenadas_lng',
  'descripcion': 'descripcion'
})

const saveFinca = async (formattedData) => {
  if (props.isEditing) {
    await fincasStore.update(props.finca.id, formattedData)
    return 'Finca actualizada'
  }
  await fincasStore.create(formattedData)
  return 'Finca creada'
}

// showSuccessNotification ya no es necesario - se maneja en los callbacks del composable

const extractErrorMessageFromServerErrors = (serverErrors) => {
  const nonFieldKeys = new Set(['error', 'status', 'error_detail'])
  for (const [key, value] of Object.entries(serverErrors)) {
    if (nonFieldKeys.has(key) && typeof value === 'string') {
      return value
    }
  }
  return null
}

const processServerErrors = (serverErrors) => {
  const fieldMapping = getFieldMapping()
  mapServerErrors(serverErrors, fieldMapping)
  return extractErrorMessageFromServerErrors(serverErrors)
}

const showValidationErrorNotification = (errorMessage = 'Por favor revisa los campos marcados en rojo.') => {
  showError(errorMessage)
}

const showGeneralErrorNotification = (errorMsg) => {
  showError(errorMsg)
}

const handleServerError = (error) => {
  if (error.response?.data) {
    const serverErrors = error.response.data.details || error.response.data
    const errorMessage = processServerErrors(serverErrors)
    scrollToFirstError('finca-form')
    showValidationErrorNotification(errorMessage)
  } else {
    const errorMsg = error.message || 'No se pudo guardar la finca. Intenta nuevamente.'
    showGeneralErrorNotification(errorMsg)
  }
}

const handleSubmit = async () => {
  if (!validateForm()) return
  
  localLoading.value = true
  
  try {
    const formattedData = fincasApi.formatFincaData(formData)
    
    
    await saveFinca(formattedData)
    // showSuccessNotification ya se llama desde los callbacks del composable
    emit('saved')
  } catch (error) {
    
    handleServerError(error)
  } finally {
    localLoading.value = false
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

// Cargar agricultores si es admin
const loadAgricultores = async () => {
  if (isAdmin.value && !props.isEditing) {
    try {
      const res = await getAgricultores()
      const data = res.data
      if (Array.isArray(data?.results)) {
        agricultores.value = data.results
      } else if (Array.isArray(data)) {
        agricultores.value = data
      } else {
        agricultores.value = data?.results || []
      }
    } catch (e) {
    }
  }
}

// Lifecycle
onMounted(() => {
  if (props.finca) {
    loadFincaData()
  }
  loadAgricultores()
})
</script>
