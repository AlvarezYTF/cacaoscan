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
      <form @submit.prevent="handleSubmit" class="p-6" id="finca-form">
        <!-- Alerta de errores general -->
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
        
        <div class="space-y-8">
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
                    <option v-for="dept in departamentos" :key="typeof dept === 'string' ? dept : dept.nombre" :value="typeof dept === 'string' ? dept : dept.nombre">
                      {{ typeof dept === 'string' ? dept : dept.nombre }}
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
                    <option v-for="mun in municipios" :key="mun.id" :value="mun.id">
                      {{ mun.nombre }}
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
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'
import fincasApi, { getAgricultores } from '@/services/fincasApi'
import catalogosApi from '@/services/catalogosApi'
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
  },
  initialAgricultorId: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['close', 'saved'])

const fincasStore = useFincasStore()
const authStore = useAuthStore()
const { errors, mapServerErrors, scrollToFirstError } = useFormValidation()
const { showSuccess, showError } = useNotifications()
const generalError = ref('')
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
const departamentosList = ref([])
const isInitialized = ref(false)

// Computed
const isAdmin = computed(() => authStore.isAdmin)
const departamentos = computed(() => {
  // Si tenemos la lista de la API, usarla, sino usar la estática
  if (departamentosList.value.length > 0) {
    return departamentosList.value
  }
  return fincasApi.getDepartamentosColombia()
})

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
  // Limpiar errores correctamente
  Object.keys(errors).forEach(key => delete errors[key])
}

// Cargar departamentos desde la API
const loadDepartamentos = async () => {
  try {
    const response = await catalogosApi.getDepartamentos()
    const deptsData = response.data || response
    const depts = Array.isArray(deptsData?.results) 
      ? deptsData.results 
      : Array.isArray(deptsData) 
        ? deptsData 
        : []
    if (depts.length > 0) {
      departamentosList.value = depts
    }
  } catch (error) {
    // Si falla, usar la lista estática
  }
}

const loadFincaData = async () => {
  if (props.finca) {
    // Obtener IDs del municipio y departamento
    const municipioId = props.finca.municipio?.id || props.finca.municipio || null
    const departamentoId = props.finca.departamento?.id || props.finca.departamento || null
    // Obtener nombres si están disponibles (nuevos campos del serializer)
    const municipioNombre = props.finca.municipio_nombre || null
    const departamentoNombre = props.finca.departamento_nombre || null
    
    Object.assign(formData, {
      nombre: props.finca.nombre || '',
      ubicacion: props.finca.ubicacion || '',
      municipio: municipioId ? String(municipioId) : '',
      hectareas: props.finca.hectareas || '',
      descripcion: props.finca.descripcion || '',
      coordenadas_lat: props.finca.coordenadas_lat || '',
      coordenadas_lng: props.finca.coordenadas_lng || '',
      activa: props.finca.activa ?? true
    })
    
    // Cargar departamentos si aún no están cargados
    if (departamentosList.value.length === 0) {
      await loadDepartamentos()
    }
    
    // Si tenemos el nombre del departamento directamente, usarlo
    if (departamentoNombre) {
      formData.departamento = departamentoNombre
      await loadMunicipiosByDepartamento(departamentoNombre, true)
      if (municipioId) {
        formData.municipio = String(municipioId)
      }
    } else if (departamentoId) {
      // Si solo tenemos el ID del departamento, buscar su nombre
      const departamentoObj = departamentosList.value.find(d => {
        if (typeof d === 'object' && d.id) {
          return d.id === Number(departamentoId)
        }
        return false
      })
      
      if (departamentoObj && departamentoObj.nombre) {
        formData.departamento = departamentoObj.nombre
        await loadMunicipiosByDepartamento(departamentoObj.nombre, true)
        if (municipioId) {
          formData.municipio = String(municipioId)
        }
      }
    } else if (municipioId) {
      // Si solo tenemos el ID del municipio, buscar su departamento
      // Buscar en todos los departamentos (fallback)
      let municipioEncontrado = null
      let departamentoEncontrado = null
      
      for (const dept of departamentosList.value) {
        if (typeof dept === 'object' && dept.id) {
          try {
            const response = await catalogosApi.getMunicipiosByDepartamento(dept.id)
            const municipiosData = response.data || response
            const municipiosList = Array.isArray(municipiosData?.results) 
              ? municipiosData.results 
              : Array.isArray(municipiosData) 
                ? municipiosData 
                : []
            
            municipioEncontrado = municipiosList.find(m => m.id === Number(municipioId))
            if (municipioEncontrado) {
              departamentoEncontrado = dept
              break
            }
          } catch (error) {
            // Continuar con el siguiente departamento
            continue
          }
        }
      }
      
      if (departamentoEncontrado && departamentoEncontrado.nombre) {
        formData.departamento = departamentoEncontrado.nombre
        await loadMunicipiosByDepartamento(departamentoEncontrado.nombre, true)
        formData.municipio = String(municipioId)
      }
    }
  }
}

const loadMunicipiosByDepartamento = async (departamentoNombre, preserveMunicipio = false) => {
  if (!departamentoNombre) {
    if (!preserveMunicipio) {
      formData.municipio = ''
    }
    municipios.value = []
    return
  }
  
  try {
    // Usar la lista de departamentos ya cargada, o cargarla si no está disponible
    let deptsList = departamentosList.value
    if (deptsList.length === 0) {
      const deptsResponse = await catalogosApi.getDepartamentos()
      const deptsData = deptsResponse.data || deptsResponse
      deptsList = Array.isArray(deptsData?.results) 
        ? deptsData.results 
        : Array.isArray(deptsData) 
          ? deptsData 
          : []
      departamentosList.value = deptsList
    }
    
    // Buscar departamento por nombre (puede variar el formato)
    const departamentoObj = deptsList.find(d => {
      if (typeof d === 'string') {
        return d.toLowerCase().trim() === departamentoNombre.toLowerCase().trim()
      }
      const nombreMatch = d.nombre && d.nombre.toLowerCase().trim() === departamentoNombre.toLowerCase().trim()
      const codigoMatch = d.codigo && d.codigo.toString() === departamentoNombre.toString()
      return nombreMatch || codigoMatch
    })
    
    if (departamentoObj) {
      const deptId = typeof departamentoObj === 'object' ? departamentoObj.id : null
      
      if (deptId) {
        const response = await catalogosApi.getMunicipiosByDepartamento(deptId)
        const municipiosData = response.data || response
        municipios.value = Array.isArray(municipiosData?.results) 
          ? municipiosData.results 
          : Array.isArray(municipiosData) 
            ? municipiosData 
            : []
      } else {
        municipios.value = []
      }
    } else {
      municipios.value = []
    }
  } catch (error) {
    municipios.value = []
  }
}

const onDepartamentoChange = async () => {
  const currentMunicipio = formData.municipio
  formData.municipio = ''
  await loadMunicipiosByDepartamento(formData.departamento, false)
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

const validateForm = async () => {
  // Limpiar errores previos
  Object.keys(errors).forEach(key => delete errors[key])
  generalError.value = ''
  // Forzar reactividad asegurando que el objeto reactive se actualice
  let isValid = true
  
  console.log('Validando formulario:', formData)
  
  // Validar nombre
  if (!formData.nombre || formData.nombre.trim().length === 0) {
    errors.nombre = 'El nombre de la finca es requerido'
    isValid = false
  } else if (formData.nombre.trim().length < 3) {
    errors.nombre = 'El nombre debe tener al menos 3 caracteres'
    isValid = false
  } else if (formData.nombre.trim().length > 200) {
    errors.nombre = 'El nombre no puede exceder 200 caracteres'
    isValid = false
  }
  
  // Validar ubicación
  if (!formData.ubicacion || formData.ubicacion.trim().length === 0) {
    errors.ubicacion = 'La ubicación es requerida'
    isValid = false
  } else if (formData.ubicacion.trim().length < 5) {
    errors.ubicacion = 'La ubicación debe tener al menos 5 caracteres'
    isValid = false
  } else if (formData.ubicacion.trim().length > 300) {
    errors.ubicacion = 'La ubicación no puede exceder 300 caracteres'
    isValid = false
  }
  
  // Validar departamento
  if (!formData.departamento || formData.departamento.trim().length === 0) {
    errors.departamento = 'El departamento es requerido'
    isValid = false
  }
  
  // Validar municipio
  if (!formData.municipio || (typeof formData.municipio === 'string' && formData.municipio.trim().length === 0)) {
    errors.municipio = 'El municipio es requerido'
    isValid = false
  }
  
  // Validar hectáreas
  const hectareasNum = parseFloat(formData.hectareas)
  if (!formData.hectareas || formData.hectareas.toString().trim().length === 0) {
    errors.hectareas = 'Las hectáreas son requeridas'
    isValid = false
  } else if (isNaN(hectareasNum)) {
    errors.hectareas = 'Las hectáreas deben ser un número válido'
    isValid = false
  } else if (hectareasNum <= 0) {
    errors.hectareas = 'Las hectáreas deben ser mayor a 0'
    isValid = false
  } else if (hectareasNum > 999999.99) {
    errors.hectareas = 'Las hectáreas no pueden exceder 999,999.99'
    isValid = false
  }
  
  // Validar agricultor (solo para admin en creación)
  if (isAdmin.value && !props.isEditing) {
    if (!formData.agricultor || formData.agricultor.toString().trim().length === 0) {
      errors.agricultor = 'Debes seleccionar un agricultor'
      isValid = false
    }
  }
  
  // Validar coordenadas GPS (opcional, pero si se proporcionan deben ser válidas)
  if (formData.coordenadas_lat && formData.coordenadas_lat.toString().trim().length > 0) {
    const lat = parseFloat(formData.coordenadas_lat)
    if (isNaN(lat)) {
      errors.coordenadas_lat = 'La latitud debe ser un número válido'
      isValid = false
    } else if (lat < -90 || lat > 90) {
      errors.coordenadas_lat = 'La latitud debe estar entre -90 y 90'
      isValid = false
    }
  }
  
  if (formData.coordenadas_lng && formData.coordenadas_lng.toString().trim().length > 0) {
    const lng = parseFloat(formData.coordenadas_lng)
    if (isNaN(lng)) {
      errors.coordenadas_lng = 'La longitud debe ser un número válido'
      isValid = false
    } else if (lng < -180 || lng > 180) {
      errors.coordenadas_lng = 'La longitud debe estar entre -180 y 180'
      isValid = false
      }
    }
  
  // Validar descripción (opcional, pero si se proporciona tiene límite)
  if (formData.descripcion && formData.descripcion.length > 1000) {
    errors.descripcion = 'La descripción no puede exceder 1000 caracteres'
    isValid = false
  }
  
  // Si hay errores, mostrar alerta y hacer scroll al primer error
  if (!isValid) {
    console.log('Formulario inválido. Errores:', errors)
    console.log('Errores en formato JSON:', JSON.stringify(errors, null, 2))
    console.log('Claves de errores:', Object.keys(errors))
    
    // Forzar reactividad asegurando que Vue detecte los cambios
    await nextTick()
    
    // Mostrar notificación si está disponible
    try {
      showError('Por favor, corrige los errores en el formulario antes de continuar')
    } catch (e) {
      console.warn('No se pudo mostrar notificación:', e)
    }
    
    // Esperar un tick adicional para asegurar que el DOM se actualice con los errores
    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // Hacer scroll al primer error
    scrollToFirstError('finca-form')
  } else {
    console.log('Formulario válido')
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
  // Limpiar errores previos
  generalError.value = ''
  
  if (error.response?.data) {
    const responseData = error.response.data
    const serverErrors = responseData.errors || responseData.details || responseData
    
    // Primero intentar procesar errors como diccionario (formato estructurado)
    if (responseData.errors && typeof responseData.errors === 'object' && !Array.isArray(responseData.errors)) {
      // Procesar errores de campos desde el diccionario
      let hasFieldErrors = false
      for (const [fieldName, errorMessages] of Object.entries(responseData.errors)) {
        if (Array.isArray(errorMessages) && errorMessages.length > 0) {
          errors[fieldName] = errorMessages[0] // Tomar el primer mensaje de error
          hasFieldErrors = true
        } else if (typeof errorMessages === 'string') {
          errors[fieldName] = errorMessages
          hasFieldErrors = true
        }
      }
      
      if (hasFieldErrors) {
        // Mostrar el primer error encontrado
        const firstErrorField = Object.keys(errors)[0]
        const firstErrorMessage = errors[firstErrorField]
        const fieldLabel = firstErrorField === 'nombre' ? 'el nombre de la finca' : 
                          firstErrorField === 'municipio' ? 'el municipio' :
                          firstErrorField === 'departamento' ? 'el departamento' : firstErrorField
        generalError.value = `Error en ${fieldLabel}: ${firstErrorMessage}`
        showError(generalError.value)
        scrollToFirstError('finca-form')
        return
      }
    }
    
    // Si details es un string con formato "campo: mensaje", extraerlo (fallback para compatibilidad)
    if (responseData.details && typeof responseData.details === 'string') {
      const detailsStr = responseData.details.trim()
      // Formato: "nombre: Ya tienes una finca con este nombre."
      const fieldErrorMatch = detailsStr.match(/^(\w+):\s*(.+)$/)
      if (fieldErrorMatch) {
        const [, fieldName, errorMessage] = fieldErrorMatch
        errors[fieldName] = errorMessage.trim()
        // Mensaje más claro para el usuario
        const fieldLabel = fieldName === 'nombre' ? 'el nombre de la finca' : 
                          fieldName === 'municipio' ? 'el municipio' :
                          fieldName === 'departamento' ? 'el departamento' : fieldName
        generalError.value = `Error en ${fieldLabel}: ${errorMessage.trim()}`
        showError(generalError.value)
        scrollToFirstError('finca-form')
        return
      }
    }
    
    // Extraer mensaje de error general (autenticación, permisos, etc.)
    const generalErrorMessage = responseData.error || responseData.detail || responseData.message
    if (generalErrorMessage && typeof generalErrorMessage === 'string') {
      // Si el mensaje general contiene información de un campo específico, extraerlo
      const fieldErrorMatch = generalErrorMessage.match(/^(\w+):\s*(.+)$/)
      if (fieldErrorMatch) {
        const [, fieldName, errorMessage] = fieldErrorMatch
        errors[fieldName] = errorMessage.trim()
        const fieldLabel = fieldName === 'nombre' ? 'el nombre de la finca' : 
                          fieldName === 'municipio' ? 'el municipio' :
                          fieldName === 'departamento' ? 'el departamento' : fieldName
        generalError.value = `Error en ${fieldLabel}: ${errorMessage.trim()}`
        showError(generalError.value)
        scrollToFirstError('finca-form')
        return
      } else {
        generalError.value = String(generalErrorMessage)
        showError(generalErrorMessage)
      }
    }
    
    // Procesar errores de campos específicos
    const errorMessage = processServerErrors(serverErrors)
    if (errorMessage && !generalError.value) {
      generalError.value = errorMessage
      showValidationErrorNotification(errorMessage)
    } else if (!generalError.value && Object.keys(errors).length > 0) {
      // Si hay errores de campos pero no mensaje general, crear uno
      const firstErrorField = Object.keys(errors)[0]
      const firstErrorMessage = errors[firstErrorField]
      const fieldLabel = firstErrorField === 'nombre' ? 'el nombre de la finca' : 
                        firstErrorField === 'municipio' ? 'el municipio' :
                        firstErrorField === 'departamento' ? 'el departamento' : firstErrorField
      generalError.value = `Error en ${fieldLabel}: ${firstErrorMessage}`
      showError(generalError.value)
    } else if (!generalError.value) {
      generalError.value = 'No se pudo guardar la finca. Por favor, intenta nuevamente.'
      showError(generalError.value)
    }
    
    scrollToFirstError('finca-form')
  } else {
    // Error de red u otro error sin respuesta del servidor
    const errorMsg = error.message || 'No se pudo guardar la finca. Verifica tu conexión e intenta nuevamente.'
    generalError.value = errorMsg
    showGeneralErrorNotification(errorMsg)
  }
}

const handleSubmit = async (event) => {
  if (event) {
    event.preventDefault()
  }
  
  console.log('handleSubmit llamado')
  console.log('Datos del formulario:', formData)
  
  const isValid = await validateForm()
  if (!isValid) {
    console.log('Validación falló, no se puede enviar')
    console.log('Estado actual de errores:', errors)
    return
  }
  
  console.log('Validación exitosa, procediendo a guardar...')
  localLoading.value = true
  
  try {
    const formattedData = fincasApi.formatFincaData(formData)
    console.log('Datos formateados para enviar:', formattedData)
    console.log('Usuario autenticado:', authStore.user)
    console.log('Es admin:', isAdmin.value)
    
    await saveFinca(formattedData)
    console.log('Finca guardada exitosamente')
    // showSuccessNotification ya se llama desde los callbacks del composable
    emit('saved')
  } catch (error) {
    console.error('Error al guardar finca:', error)
    console.error('Error completo:', error)
    console.error('Response del error:', error.response)
    console.error('Detalles del error:', error.response?.data)
    handleServerError(error)
  } finally {
    localLoading.value = false
  }
}

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
      
      // Si hay un agricultor inicial y no estamos editando, inicializarlo después de cargar
      if (props.initialAgricultorId && !props.isEditing) {
        const agricultorId = Number(props.initialAgricultorId)
        if (!isNaN(agricultorId) && agricultorId > 0) {
          const agricultor = agricultores.value.find(a => a.id === agricultorId)
          if (agricultor) {
            formData.agricultor = agricultor.id
          }
        }
      }
    } catch (e) {
    }
  }
}

// Lifecycle
onMounted(async () => {
  await loadDepartamentos()
  if (props.finca) {
    await loadFincaData()
  }
  await loadAgricultores()
  isInitialized.value = true
})

// Watchers - Definido después de todas las funciones para evitar problemas de inicialización
watch(() => props.finca, async () => {
  if (!isInitialized.value) {
    return
  }
  if (props.finca) {
    await loadFincaData()
  } else {
    resetForm()
  }
}, { immediate: false })
</script>
