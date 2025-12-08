<template>
  <div class="space-y-6">
    <!-- Alerta informativa de campos requeridos -->
    <div v-if="Object.keys(errors).length > 0" class="bg-amber-50 border-l-4 border-amber-400 p-4 rounded-lg">
      <div class="flex items-start">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <div class="ml-3 flex-1">
          <h3 class="text-sm font-medium text-amber-800">Información requerida:</h3>
          <ul class="mt-2 text-sm text-amber-700 list-disc list-inside space-y-1">
            <li v-for="(error, field) in errors" :key="field">{{ error }}</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
      <!-- Agricultor (solo para admin) -->
      <div v-if="userRole === 'admin'">
        <label for="farmer" class="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-2">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
          </svg>
          Agricultor <span class="text-red-500">*</span>
        </label>
        <div class="relative">
          <select
            id="farmer"
            v-model="formData.farmer"
            :disabled="loadingAgricultores"
            @change="handleFarmerChange"
            required
            class="mt-1 block w-full rounded-xl border-2 border-gray-200 px-4 py-3 pr-10 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
            :class="{ 
              'border-amber-500 focus:border-amber-500 focus:ring-amber-500/30': errors.farmer, 
              'bg-gray-100 cursor-wait': loadingAgricultores
            }"
          >
            <option value="">{{ loadingAgricultores ? 'Cargando agricultores...' : 'Selecciona un agricultor' }}</option>
            <option v-for="agricultor in agricultores" :key="agricultor.id" :value="agricultor.username">
              {{ agricultor.first_name }} {{ agricultor.last_name }} ({{ agricultor.email }})
            </option>
          </select>
          <!-- Botón para deseleccionar agricultor -->
          <button
            v-if="formData.farmer && !loadingAgricultores"
            @click="clearFarmerSelection"
            type="button"
            class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-red-600 transition-colors duration-200 p-1 rounded-lg hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500"
            title="Deseleccionar agricultor"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
          <p v-if="errors.farmer" class="mt-1 text-sm text-amber-600 flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            {{ errors.farmer }}
          </p>
        <p v-if="agricultores.length === 0 && !loadingAgricultores" class="mt-1 text-xs text-amber-600 flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
          </svg>
          No hay agricultores registrados
        </p>
        <p v-if="selectedLoteData" class="mt-1 text-xs text-gray-500 flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
          </svg>
          Este campo está bloqueado porque se autocompletó desde el lote seleccionado
        </p>
      </div>

      <!-- Finca (se muestra solo si hay agricultor seleccionado para admin, o siempre para agricultor) -->
      <div v-if="userRole !== 'admin' || formData.farmer">
        <label for="farm" class="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-2">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
          </svg>
          Finca <span class="text-red-500">*</span>
        </label>
        <div class="relative">
          <select
            id="farm"
            v-model="formData.farm"
            :disabled="loadingFincas || (userRole === 'admin' && !formData.farmer)"
            @change="handleFincaChange"
            required
            class="mt-1 block w-full rounded-xl border-2 border-gray-200 px-4 py-3 pr-10 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
            :class="{ 
              'border-amber-500 focus:border-amber-500 focus:ring-amber-500/30': errors.farm, 
              'bg-gray-100 cursor-wait': loadingFincas,
              'bg-gray-100 cursor-not-allowed': (userRole === 'admin' && !formData.farmer)
            }"
          >
            <option value="">{{ loadingFincas ? 'Cargando fincas...' : (userRole === 'admin' && !formData.farmer ? 'Primero selecciona un agricultor' : 'Selecciona una finca') }}</option>
            <option v-for="finca in fincas" :key="finca.id" :value="finca.nombre">
              {{ finca.nombre }} - {{ finca.ubicacion || 'Sin ubicación' }}
            </option>
          </select>
          <!-- Botón para deseleccionar finca -->
          <button
            v-if="formData.farm && !loadingFincas && !(userRole === 'admin' && !formData.farmer)"
            @click="clearFincaSelection"
            type="button"
            class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-red-600 transition-colors duration-200 p-1 rounded-lg hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500"
            title="Deseleccionar finca"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <p v-if="errors.farm" class="mt-1 text-sm text-amber-600 flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          {{ errors.farm }}
        </p>
        <!-- Mensaje y botón para crear finca cuando no hay fincas -->
        <div v-if="fincas.length === 0 && !loadingFincas && (userRole !== 'admin' || formData.farmer)" class="mt-3">
          <div class="bg-amber-50 border-2 border-amber-200 rounded-xl p-4">
            <div class="flex items-start gap-3">
              <div class="flex-shrink-0">
                <svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                </svg>
              </div>
              <div class="flex-1">
                <h3 class="text-sm font-semibold text-amber-800 mb-1">
                  {{ userRole === 'agricultor' ? 'No tienes fincas registradas' : 'Este agricultor no tiene fincas registradas' }}
                </h3>
                <p class="text-xs text-amber-700 mb-3">
                  Necesitas registrar una finca para poder realizar análisis.
                </p>
                <button
                  type="button"
                  @click="openCreateFincaModal"
                  class="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white text-sm font-semibold rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-all duration-200"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                  </svg>
                  Crear Nueva Finca
                </button>
              </div>
            </div>
          </div>
        </div>
        <p v-if="selectedLoteData" class="mt-1 text-xs text-gray-500 flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
          </svg>
          Este campo está bloqueado porque se autocompletó desde el lote seleccionado
        </p>
      </div>

      <!-- Lote (se muestra solo si hay una finca seleccionada) -->
      <div v-if="formData.farm" class="sm:col-span-2">
        <label for="lote" class="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-2">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
          </svg>
          Lote <span class="text-red-500">*</span>
        </label>
        
        <!-- Si hay lotes, mostrar selector -->
        <div v-if="lotes.length > 0 || loadingLotes" class="relative">
          <select
            id="lote"
            v-model="formData.lote"
            :disabled="loadingLotes || selectedLoteData !== null"
            @change="handleLoteChange"
            required
            class="mt-1 block w-full rounded-xl border-2 border-gray-200 px-4 py-3 pr-10 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
            :class="{ 
              'border-amber-500 focus:border-amber-500 focus:ring-amber-500/30': errors.lote, 
              'bg-gray-100 cursor-wait': loadingLotes,
              'bg-gray-100 cursor-not-allowed': selectedLoteData !== null && !loadingLotes
            }"
          >
            <option value="">{{ loadingLotes ? 'Cargando lotes...' : 'Selecciona un lote' }}</option>
            <option v-for="lote in lotes" :key="lote.id" :value="lote.id">
              {{ lote.identificador || lote.nombre }} - {{ lote.variedad || 'Sin variedad' }}
            </option>
          </select>
          <!-- Botón para deseleccionar lote -->
          <button
            v-if="formData.lote && !loadingLotes && selectedLoteData === null"
            @click="clearLoteSelection"
            type="button"
            class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-red-600 transition-colors duration-200 p-1 rounded-lg hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500"
            title="Deseleccionar lote"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
          <p v-if="errors.lote" class="mt-1 text-sm text-amber-600 flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            {{ errors.lote }}
          </p>
          <p v-if="selectedLoteData" class="mt-2 text-xs text-green-600 flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            Información del lote cargada automáticamente
          </p>
        </div>
        
        <!-- Si no hay lotes, mostrar botón para crear -->
        <div v-else-if="!loadingLotes && formData.farm" class="mt-1">
          <div class="bg-amber-50 border-2 border-amber-200 rounded-xl p-4">
            <div class="flex items-start gap-3">
              <div class="flex-shrink-0">
                <svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                </svg>
              </div>
              <div class="flex-1">
                <h3 class="text-sm font-semibold text-amber-800 mb-1">Esta finca no tiene lotes registrados</h3>
                <p class="text-xs text-amber-700 mb-3">Necesitas crear un lote para poder realizar el análisis.</p>
                <button
                  type="button"
                  @click="openCreateLoteModal"
                  class="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white text-sm font-semibold rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-all duration-200"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                  </svg>
                  Crear Nuevo Lote
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Modal para crear lote -->
    <Teleport to="body">
      <CreateLoteModal
        v-if="showCreateLoteModal && selectedFincaId"
        :key="`modal-${selectedFincaId}-${showCreateLoteModal}`"
        :finca-id="selectedFincaId"
        :finca-nombre="formData.farm || 'Finca'"
        @close="closeCreateLoteModal"
        @lote-created="handleLoteCreated"
      />
    </Teleport>

    <!-- Modal para crear finca -->
    <Teleport to="body">
      <FincaForm
        v-if="showCreateFincaModal"
        :finca="null"
        :is-editing="false"
        @close="closeCreateFincaModal"
        @saved="handleFincaCreated"
      />
    </Teleport>
    
    <!-- Debug info (remover en producción) -->
    <!-- <div v-if="showCreateLoteModal" class="fixed top-0 left-0 bg-red-500 text-white p-2 z-[10000]">
      Modal should be visible: {{ showCreateLoteModal }}, FincaId: {{ selectedFincaId }}
    </div> -->
  </div>
</template>

<script setup>
// 1. Vue core
import { ref, watch, onMounted, nextTick, Teleport } from 'vue'

// 2. Stores
import { useAuthStore } from '@/stores/auth'

// 3. Services
import { getFincas, getLotesByFinca } from '@/services/fincasApi'
import { getLoteById } from '@/services/lotesApi'
import authApi from '@/services/authApi'

// 4. Components
import CreateLoteModal from './CreateLoteModal.vue'
import FincaForm from '@/components/common/FincasViewComponents/FincaForm.vue'

// 5. Composables
import { useNotifications } from '@/composables/useNotifications'

const { showError } = useNotifications()

// Props
const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  errors: {
    type: Object,
    default: () => ({})
  },
  userRole: {
    type: String,
    default: 'admin'
  },
  userName: {
    type: String,
    default: ''
  },
  userId: {
    type: Number,
    default: null
  }
})

// Emits
const emit = defineEmits(['update:modelValue'])

// Stores
const authStore = useAuthStore()

// State
const formData = ref({
  name: '',
  farm: '',
  originPlace: '',
  farmer: '',
  genetics: '',
  lote: '',
  collectionDate: '',
  notes: '',
  ...props.modelValue
})

const fincas = ref([])
const loadingFincas = ref(false)
const agricultores = ref([])
const loadingAgricultores = ref(false)
const allFincas = ref([])
const lotes = ref([])
const loadingLotes = ref(false)
const selectedFincaId = ref(null)
const selectedLoteData = ref(null)
const loadingLoteData = ref(false)
const showCreateLoteModal = ref(false)
const showCreateFincaModal = ref(false)
const errors = ref({})

// Computed
const maxDate = new Date().toISOString().split('T')[0]

// Functions
const loadAgricultores = async () => {
  if (props.userRole !== 'admin') return
  
  loadingAgricultores.value = true
  try {
    const response = await authApi.getUsers()
    agricultores.value = response.results?.filter(user => 
      !user.is_superuser && !user.is_staff && user.role === 'farmer'
    ) || []
  } catch (error) {
    agricultores.value = []
  } finally {
    loadingAgricultores.value = false
  }
}

const loadAllFincas = async () => {
  try {
    const response = await getFincas({ activa: true })
    allFincas.value = response.results || []
  } catch (error) {
    allFincas.value = []
  }
}

const validateForm = () => {
  const validationErrors = {}
  
  // Validar agricultor (solo para admin)
  if (props.userRole === 'admin') {
    if (!formData.value.farmer || formData.value.farmer.trim().length === 0) {
      validationErrors.farmer = 'Debes seleccionar un agricultor'
    }
  }
  
  // Validar finca
  if (!formData.value.farm || formData.value.farm.trim().length === 0) {
    validationErrors.farm = 'Debes seleccionar una finca'
  }
  
  // Validar lote
  if (!formData.value.lote || formData.value.lote.toString().trim().length === 0) {
    validationErrors.lote = 'Debes seleccionar un lote'
  } else {
    // Si hay un lote seleccionado, el nombre debería estar autocompletado
    // Si no está, puede ser que aún se esté cargando
    if (!formData.value.name || formData.value.name.trim().length === 0) {
      // Solo mostrar error si no se está cargando el lote
      if (!loadingLoteData.value) {
        validationErrors.name = 'El nombre del lote es requerido. Selecciona un lote para autocompletarlo.'
      }
    }
  }
  
  return validationErrors
}

const updateForm = () => {
  // Asegurar que el nombre esté presente si hay un lote seleccionado
  if (formData.value.lote && (!formData.value.name || formData.value.name.trim().length === 0)) {
    // Si hay lote pero no nombre, intentar obtenerlo del lote seleccionado
    const selectedLote = lotes.value.find(l => l.id === parseInt(formData.value.lote, 10))
    if (selectedLote) {
      formData.value.name = selectedLote.identificador || selectedLote.nombre || `Lote-${formData.value.lote}`
    }
  }
  
  const mappedData = {
    name: formData.value.name || '',
    farm: formData.value.farm || '',
    originPlace: formData.value.originPlace || '',
    genetics: formData.value.genetics || '',
    collectionDate: formData.value.collectionDate || '',
    origin: '',
    notes: formData.value.notes || '',
    farmer: formData.value.farmer || '',
    lote: formData.value.lote || ''
  }
  
  // Emitir el evento con los datos actualizados
  emit('update:modelValue', mappedData)
  
  // Validar después de emitir para mostrar errores si los hay
  const validationErrors = validateForm()
  errors.value = validationErrors
}

const openCreateLoteModal = () => {
  // Intentar obtener el ID de la finca si no está definido
  if (!selectedFincaId.value) {
    if (formData.value.farm) {
      const selectedFinca = fincas.value.find(f => f.nombre === formData.value.farm) || 
                            allFincas.value.find(f => f.nombre === formData.value.farm)
      if (selectedFinca && selectedFinca.id) {
        selectedFincaId.value = selectedFinca.id
      } else {
        errors.value.farm = 'Primero debes seleccionar una finca válida'
        showError('Primero debes seleccionar una finca válida')
        return
      }
    } else {
      errors.value.farm = 'Primero debes seleccionar una finca'
      showError('Primero debes seleccionar una finca')
      return
    }
  }
  
  // Verificar que tenemos un ID válido
  if (!selectedFincaId.value || selectedFincaId.value <= 0) {
    errors.value.farm = 'No se pudo identificar la finca. Por favor, selecciona una finca nuevamente.'
    showError('No se pudo identificar la finca. Por favor, selecciona una finca nuevamente.')
    return
  }
  
  // Abrir el modal
  showCreateLoteModal.value = true
}

const closeCreateLoteModal = () => {
  showCreateLoteModal.value = false
}

const openCreateFincaModal = () => {
  showCreateFincaModal.value = true
}

const closeCreateFincaModal = () => {
  showCreateFincaModal.value = false
}

const handleFincaCreated = async () => {
  // Cerrar modal
  closeCreateFincaModal()
  
  // Recargar todas las fincas
  await loadAllFincas()
  
  // Si es agricultor, actualizar su lista de fincas
  if (props.userRole === 'agricultor' && props.userId) {
    fincas.value = allFincas.value.filter(finca => finca.agricultor_id === props.userId && finca.activa === true) || []
  } else if (props.userRole === 'admin' && formData.value.farmer) {
    // Si es admin y hay agricultor seleccionado, actualizar lista de fincas de ese agricultor
    const selectedAgricultor = agricultores.value.find(a => a.username === formData.value.farmer)
    if (selectedAgricultor) {
      fincas.value = allFincas.value.filter(finca => finca.agricultor_id === selectedAgricultor.id && finca.activa === true)
    }
  }
  
  // Si solo hay una finca, seleccionarla automáticamente
  if (fincas.value.length === 1) {
    formData.value.farm = fincas.value[0].nombre
    await handleFincaChange()
  }
  
  updateForm()
}

const handleLoteCreated = async (newLote) => {
  // Cerrar modal
  showCreateLoteModal.value = false
  
  // Recargar lotes de la finca
  await loadLotesByFinca(selectedFincaId.value)
  
  // Seleccionar automáticamente el nuevo lote
  if (newLote) {
    const loteId = newLote.id || newLote.lote?.id || (typeof newLote === 'object' && 'id' in newLote ? newLote.id : null)
    if (loteId) {
      formData.value.lote = loteId.toString()
      await handleLoteChange()
      updateForm()
    } else {
      // Si no tenemos el ID directamente, buscar el lote más reciente en la lista
      if (lotes.value.length > 0) {
        const latestLote = lotes.value[lotes.value.length - 1]
        formData.value.lote = latestLote.id.toString()
        await handleLoteChange()
        updateForm()
      }
    }
  }
}

const handleFarmerChange = async () => {
  if (props.userRole === 'agricultor') return
  
  // Limpiar finca y lote cuando cambia el agricultor
  formData.value.farm = ''
  formData.value.lote = ''
  selectedFincaId.value = null
  selectedLoteData.value = null
  lotes.value = []
  
  if (formData.value.farmer) {
    const selectedAgricultor = agricultores.value.find(a => a.username === formData.value.farmer)
    if (selectedAgricultor) {
      // Filtrar solo fincas activas por agricultor
      fincas.value = allFincas.value.filter(finca => finca.agricultor_id === selectedAgricultor.id && finca.activa === true)
    } else {
      fincas.value = []
    }
  } else {
    fincas.value = []
  }
  
  updateForm()
}

const loadLotesByFinca = async (fincaId) => {
  if (!fincaId) {
    lotes.value = []
    return
  }
  
  loadingLotes.value = true
  try {
    const data = await getLotesByFinca(fincaId)
    
    // Manejar diferentes formatos de respuesta
    if (data && typeof data === 'object') {
      if (data.lotes && Array.isArray(data.lotes)) {
        lotes.value = data.lotes
      } else if (data.results && Array.isArray(data.results)) {
        lotes.value = data.results
      } else if (Array.isArray(data)) {
        lotes.value = data
      } else {
        lotes.value = []
      }
    } else if (Array.isArray(data)) {
      lotes.value = data
    } else {
      lotes.value = []
    }
  } catch (error) {
    lotes.value = []
  } finally {
    loadingLotes.value = false
  }
}

const clearFincaSelection = () => {
  formData.value.farm = ''
  formData.value.lote = ''
  selectedFincaId.value = null
  selectedLoteData.value = null
  lotes.value = []
  // Limpiar campos autocompletados
  formData.value.name = ''
  formData.value.genetics = ''
  formData.value.collectionDate = ''
  formData.value.originPlace = ''
  updateForm()
}

const clearLoteSelection = () => {
  formData.value.lote = ''
  selectedLoteData.value = null
  // Limpiar campos autocompletados
  formData.value.name = ''
  formData.value.genetics = ''
  formData.value.collectionDate = ''
  formData.value.originPlace = ''
  updateForm()
}

const clearFarmerSelection = () => {
  formData.value.farmer = ''
  formData.value.farm = ''
  formData.value.lote = ''
  selectedFincaId.value = null
  selectedLoteData.value = null
  fincas.value = []
  lotes.value = []
  // Limpiar campos autocompletados
  formData.value.name = ''
  formData.value.genetics = ''
  formData.value.collectionDate = ''
  formData.value.originPlace = ''
  updateForm()
}

const handleFincaChange = async () => {
  // Si se deselecciona la finca (valor vacío), limpiar todo
  if (!formData.value.farm || formData.value.farm.trim() === '') {
    clearFincaSelection()
    return
  }
  
  // Limpiar lote seleccionado cuando cambia la finca
  formData.value.lote = ''
  selectedLoteData.value = null
  
  if (formData.value.farm) {
    // Buscar la finca seleccionada
    const selectedFinca = fincas.value.find(f => f.nombre === formData.value.farm) || 
                          allFincas.value.find(f => f.nombre === formData.value.farm)
    
    if (selectedFinca && selectedFinca.id) {
      selectedFincaId.value = selectedFinca.id
      await loadLotesByFinca(selectedFinca.id)
      
      // Para admin, asegurar que el agricultor esté seleccionado
      if (props.userRole === 'admin' && selectedFinca.agricultor_id) {
        const associatedAgricultor = agricultores.value.find(a => a.id === selectedFinca.agricultor_id)
        if (associatedAgricultor && formData.value.farmer !== associatedAgricultor.username) {
          formData.value.farmer = associatedAgricultor.username
          // Actualizar lista de fincas activas para este agricultor
          fincas.value = allFincas.value.filter(f => f.agricultor_id === selectedFinca.agricultor_id && f.activa === true)
        }
      }
    }
  } else {
    selectedFincaId.value = null
    lotes.value = []
  }
  
  updateForm()
}

const handleLoteChange = async () => {
  if (!formData.value.lote || formData.value.lote === null || formData.value.lote === '') {
    // Si se deselecciona el lote, limpiar datos autocompletados
    selectedLoteData.value = null
    formData.value.name = ''
    formData.value.genetics = ''
    updateForm()
    return
  }
  
  loadingLoteData.value = true
  try {
    // Obtener datos completos del lote
    const loteId = parseInt(formData.value.lote, 10)
    
    // Primero intentar obtener de la lista de lotes (más rápido y no requiere petición)
    let loteData = lotes.value.find(l => l.id === loteId)
    
    if (!loteData) {
      // Si no está en la lista, intentar obtenerlo del API
      try {
        loteData = await getLoteById(loteId)
      } catch (apiError) {
        // Si falla el API, usar datos básicos del lote seleccionado
        const loteFromSelect = lotes.value.find(l => l.id === loteId)
        if (loteFromSelect) {
          loteData = loteFromSelect
        } else {
          throw new Error('No se pudo obtener información del lote')
        }
      }
    }
    
    if (!loteData) {
      return
    }
    
    selectedLoteData.value = loteData
    
    // Autocompletar información del formulario
    // Nombre del lote (prioridad: identificador > nombre)
    const loteNombre = loteData.identificador || loteData.nombre || ''
    if (loteNombre) {
      formData.value.name = String(loteNombre).trim()
    } else {
      // Si no hay nombre, usar el ID del lote como fallback
      formData.value.name = `Lote-${loteId}`
    }
    
    // Asegurar que el nombre no esté vacío
    if (!formData.value.name || formData.value.name.trim().length === 0) {
      formData.value.name = `Lote-${loteId}`
    }
    
    // Genética/Variedad
    if (loteData.variedad) {
      formData.value.genetics = loteData.variedad
    }
    
    // Fecha de recolección (usar fecha_cosecha si está disponible, o fecha actual como fallback)
    if (loteData.fecha_cosecha) {
      // Asegurar que la fecha esté en formato YYYY-MM-DD
      let fechaCosecha = loteData.fecha_cosecha
      if (typeof fechaCosecha === 'string') {
        // Si viene como string, usar directamente (remover hora si viene con ISO format)
        formData.value.collectionDate = fechaCosecha.split('T')[0]
      } else if (fechaCosecha instanceof Date) {
        // Si es un objeto Date, convertir a string
        formData.value.collectionDate = fechaCosecha.toISOString().split('T')[0]
      } else {
        formData.value.collectionDate = String(fechaCosecha).split('T')[0]
      }
    } else {
      // Si no hay fecha de cosecha, usar la fecha actual como fecha de recolección
      const today = new Date().toISOString().split('T')[0]
      formData.value.collectionDate = today
    }
    
    // Lugar de origen (usar ubicación de la finca)
    if (loteData.finca) {
      const fincaId = typeof loteData.finca === 'object' ? loteData.finca.id : loteData.finca
      const finca = allFincas.value.find(f => f.id === fincaId)
      if (finca) {
        // Usar ubicación completa o ubicación básica
        if (finca.ubicacion_completa) {
          formData.value.originPlace = finca.ubicacion_completa
        } else if (finca.ubicacion) {
          formData.value.originPlace = finca.ubicacion
        } else if (finca.municipio && finca.departamento) {
          formData.value.originPlace = `${finca.municipio}, ${finca.departamento}`
        }
      }
    }
    
    // Finca (asegurarse de que esté seleccionada)
    if (loteData.finca) {
      const fincaId = typeof loteData.finca === 'object' ? loteData.finca.id : loteData.finca
      const finca = allFincas.value.find(f => f.id === fincaId)
      if (finca) {
        if (!formData.value.farm || formData.value.farm !== finca.nombre) {
          formData.value.farm = finca.nombre
          selectedFincaId.value = finca.id
          await loadLotesByFinca(finca.id)
        }
      }
    }
    
    // Agricultor (si es admin)
    if (props.userRole === 'admin' && loteData.finca) {
      const fincaId = typeof loteData.finca === 'object' ? loteData.finca.id : loteData.finca
      const finca = allFincas.value.find(f => f.id === fincaId)
      if (finca && finca.agricultor_id) {
        const associatedAgricultor = agricultores.value.find(a => a.id === finca.agricultor_id)
        if (associatedAgricultor && formData.value.farmer !== associatedAgricultor.username) {
          formData.value.farmer = associatedAgricultor.username
          // Actualizar lista de fincas activas para este agricultor
          fincas.value = allFincas.value.filter(f => f.agricultor_id === finca.agricultor_id && f.activa === true)
        }
      }
    }
    
    // Limpiar errores del nombre antes de actualizar
    if (errors.value.name) {
      delete errors.value.name
    }
    
    // Verificar que el nombre se haya asignado correctamente
    if (!formData.value.name || formData.value.name.trim().length === 0) {
      // Intentar nuevamente con el identificador o nombre
      const fallbackNombre = loteData.identificador || loteData.nombre || `Lote-${loteId}`
      formData.value.name = String(fallbackNombre).trim()
    }
    
    // Asegurar que el nombre no esté vacío
    if (!formData.value.name || formData.value.name.trim().length === 0) {
      formData.value.name = `Lote-${loteId}`
    }
    
    // Forzar actualización inmediata del formulario
    // Usar nextTick para asegurar que todos los cambios se hayan aplicado
    await nextTick()
    
    // Actualizar el formulario con todos los datos autocompletados
    updateForm()
    
    // Esperar un tick más y actualizar nuevamente para asegurar la propagación
    await nextTick()
    updateForm()
    
    // Verificar una vez más que el nombre esté presente
    if (!formData.value.name || formData.value.name.trim().length === 0) {
      // Último intento: usar el identificador del lote de la lista
      const loteFromList = lotes.value.find(l => l.id === loteId)
      if (loteFromList) {
        formData.value.name = loteFromList.identificador || loteFromList.nombre || `Lote-${loteId}`
        updateForm()
      }
    }
  } catch (error) {
    selectedLoteData.value = null
  } finally {
    loadingLoteData.value = false
  }
}

// Watchers
watch(() => props.modelValue, (newValue) => {
  // Solo actualizar campos específicos que no estén siendo editados activamente
  // No sobrescribir el nombre si ya está establecido y hay un lote seleccionado
  if (formData.value.lote && formData.value.name && formData.value.name.trim().length > 0) {
    // Si hay lote y nombre, solo actualizar otros campos, no el nombre
    formData.value = {
      ...formData.value,
      ...newValue,
      name: formData.value.name // Preservar el nombre autocompletado
    }
  } else {
    // Si no hay lote o nombre, actualizar normalmente
    formData.value = { ...formData.value, ...newValue }
  }
}, { deep: true })

watch(() => formData.value.farmer, (newFarmer, oldFarmer) => {
  if (newFarmer !== oldFarmer && props.userRole === 'admin') {
    handleFarmerChange()
  }
})

watch(() => formData.value.farm, (newFarm, oldFarm) => {
  if (newFarm !== oldFarm) {
    handleFincaChange()
  }
})

watch(() => formData.value.lote, async (newLote, oldLote) => {
  if (newLote !== oldLote && newLote) {
    // El handleLoteChange ya se llama desde @change, pero por si acaso
    // No llamar updateForm aquí porque handleLoteChange ya lo hace
  }
})

// Watcher específico para el nombre del lote
watch(() => formData.value.name, (newName) => {
  if (newName) {
    // Actualizar el formulario cuando cambia el nombre
    updateForm()
  }
})

// Validar cuando cambian los campos
watch([() => formData.value.farmer, () => formData.value.farm, () => formData.value.lote, () => formData.value.name], () => {
  const validationErrors = validateForm()
  errors.value = { ...errors.value, ...validationErrors }
}, { immediate: false })

// Lifecycle
onMounted(async () => {
  await loadAllFincas()
  await loadAgricultores()
  
  if (props.userRole === 'agricultor' && props.userId) {
    // Para agricultores, mostrar solo sus fincas activas
    fincas.value = allFincas.value.filter(finca => finca.agricultor_id === props.userId && finca.activa === true) || []
    if (props.userName && !formData.value.farmer) {
      formData.value.farmer = props.userName
    }
  } else if (props.userRole === 'admin') {
    // Para admin, no mostrar fincas hasta que seleccione un agricultor
    fincas.value = []
  } else {
    // Solo mostrar fincas activas
    fincas.value = allFincas.value.filter(finca => finca.activa === true)
  }
  
  emit('update:modelValue', { ...formData.value })
  
  // Si ya hay una finca seleccionada en el modelo, cargar sus lotes
  if (formData.value.farm) {
    const selectedFinca = allFincas.value.find(f => f.nombre === formData.value.farm)
    if (selectedFinca && selectedFinca.id) {
      selectedFincaId.value = selectedFinca.id
      await loadLotesByFinca(selectedFinca.id)
      
      // Si es admin y hay finca, asegurar que el agricultor esté seleccionado
      if (props.userRole === 'admin' && selectedFinca.agricultor_id) {
        const associatedAgricultor = agricultores.value.find(a => a.id === selectedFinca.agricultor_id)
        if (associatedAgricultor) {
          formData.value.farmer = associatedAgricultor.username
          fincas.value = allFincas.value.filter(f => f.agricultor_id === selectedFinca.agricultor_id && f.activa === true)
        }
      }
    }
  }
})
</script>

<style scoped>
/* Solo estilos que no están en Tailwind si es necesario */
</style>
