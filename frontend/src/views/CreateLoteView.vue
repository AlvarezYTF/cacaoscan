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
              Crear Nuevo Lote
            </h1>
            <p class="mt-2 text-gray-600">Bulto de granos para la finca: {{ finca?.nombre || '' }}</p>
          </div>

          <!-- Form Card -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
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

                <!-- Información del Bulto -->
                <div class="bg-gray-50 rounded-lg p-6">
                  <h3 class="text-lg font-semibold text-gray-900 mb-4">Información del Bulto</h3>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label for="identificador" class="block text-sm font-medium text-gray-700 mb-2">
                        Identificador <span class="text-xs text-gray-500">(opcional, único en la finca)</span>
                      </label>
                      <input
                        id="identificador"
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
                      <label for="nombre" class="block text-sm font-medium text-gray-700 mb-2">
                        Nombre/Descripción <span class="text-xs text-gray-500">(opcional, se usa si no hay identificador)</span>
                      </label>
                      <input
                        id="nombre"
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
                      <label for="variedad" class="block text-sm font-medium text-gray-700 mb-2">
                        Variedad * <span class="text-xs text-gray-500">(genética del cacao)</span>
                      </label>
                      <select
                        id="variedad"
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
                      <label for="peso_kg" class="block text-sm font-medium text-gray-700 mb-2">
                        Peso (kg) * <span class="text-xs text-gray-500">(peso del bulto en kilogramos)</span>
                      </label>
                      <input
                        id="peso_kg"
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
                      <label for="estado" class="block text-sm font-medium text-gray-700 mb-2">
                        Estado <span class="text-xs text-gray-500">(estado actual del lote)</span>
                      </label>
                      <select
                        id="estado"
                        v-model="formData.estado"
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

                <!-- Fechas del Bulto -->
                <div class="bg-blue-50 rounded-lg p-6">
                  <h3 class="text-lg font-semibold text-gray-900 mb-4">Fechas del Bulto</h3>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label for="fecha_recepcion" class="block text-sm font-medium text-gray-700 mb-2">
                        Fecha de Recepción * <span class="text-xs text-gray-500">(cuándo se recibió el bulto)</span>
                      </label>
                      <input
                        id="fecha_recepcion"
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
                      <label for="fecha_procesamiento" class="block text-sm font-medium text-gray-700 mb-2">
                        Fecha de Procesamiento <span class="text-xs text-gray-500">(opcional, fermentación/procesamiento)</span>
                      </label>
                      <input
                        id="fecha_procesamiento"
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
                      <label for="fecha_plantacion" class="block text-sm font-medium text-gray-700 mb-2">
                        Fecha de Plantación <span class="text-xs text-gray-500">(opcional, cuando se sembró)</span>
                      </label>
                      <input
                        id="fecha_plantacion"
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
                      <label for="fecha_cosecha" class="block text-sm font-medium text-gray-700 mb-2">
                        Fecha de Cosecha <span class="text-xs text-gray-500">(opcional, cuando se cosechó)</span>
                      </label>
                      <input
                        id="fecha_cosecha"
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
                  <label for="descripcion" class="block text-sm font-medium text-gray-700 mb-2">
                    Descripción (Opcional) <span class="text-xs text-gray-500">(información adicional)</span>
                  </label>
                  <textarea
                    id="descripcion"
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
                  <svg v-if="!loading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                  </svg>
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
import catalogosApi from '@/services/catalogosApi'

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
const generalError = ref('')

// Datos del formulario
const formData = reactive({
  identificador: '',
  nombre: '',
  variedad: '',
  peso_kg: '',
  fecha_recepcion: '',
  fecha_procesamiento: '',
  fecha_plantacion: '',
  fecha_cosecha: '',
  estado: null,
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

  // Validar estado (opcional, pero si se proporciona debe ser válido)
  if (formData.estado) {
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
  // Validar que tenemos fincaId
  if (!fincaId.value || isNaN(fincaId.value)) {
    showError('No se pudo identificar la finca. Por favor, regresa e intenta nuevamente.')
    return
  }

  if (!validateForm()) {
    showError('Por favor, corrige los errores en el formulario antes de continuar')
    return
  }

  localLoading.value = true
  errors.value = {}
  generalError.value = ''

  try {
    const loteData = {
      finca: Number(fincaId.value),
      identificador: formData.identificador.trim() || null,
      nombre: formData.nombre.trim() || formData.identificador.trim() || 'Bulto de cacao',
      variedad: Number(formData.variedad), // Asegurar que es un número
      peso_kg: parseFloat(formData.peso_kg),
      fecha_recepcion: formData.fecha_recepcion,
      fecha_procesamiento: formData.fecha_procesamiento || null,
      fecha_plantacion: formData.fecha_plantacion || null,
      fecha_cosecha: formData.fecha_cosecha || null,
      estado: formData.estado ? Number(formData.estado) : null, // Asegurar que es un número o null
      descripcion: formData.descripcion.trim() || null,
      activo: formData.activo
    }

    const result = await createLote(loteData)
    
    showSuccess('El lote ha sido creado exitosamente')
    router.push(`/fincas/${fincaId.value}/lotes`)
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

const goBack = () => {
  router.push(`/fincas/${fincaId.value}/lotes`)
}

// Lifecycle
onMounted(() => {
  loadFinca()
  loadParametros()
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
