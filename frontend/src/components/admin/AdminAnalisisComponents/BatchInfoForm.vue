<template>
  <div class="space-y-6">
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
      <!-- Agricultor -->
      <div>
        <label :for="userRole === 'admin' ? 'farmer' : 'farmer-readonly'" class="flex items-center gap-2 text-sm font-semibold text-gray-700">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
          </svg>
          Agricultor <span class="text-red-500">*</span>
        </label>
        
        <!-- Select for admin -->
        <select
          v-if="userRole === 'admin'"
          id="farmer"
          v-model="formData.farmer"
          :disabled="loadingAgricultores"
          class="mt-1 block w-full rounded-xl border-2 border-gray-200 px-4 py-3 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
          :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/30': errors.farmer, 'bg-gray-100 cursor-wait': loadingAgricultores }"
        >
          <option value="">{{ loadingAgricultores ? 'Cargando agricultores...' : 'Selecciona un agricultor' }}</option>
          <option v-for="agricultor in agricultores" :key="agricultor.id" :value="agricultor.username">
            {{ agricultor.first_name }} {{ agricultor.last_name }} ({{ agricultor.email }})
          </option>
        </select>
        
        <!-- Input readonly for agricultor -->
        <input
          v-else
          type="text"
          id="farmer-readonly"
          v-model="formData.farmer"
          @input="updateForm"
          readonly
          class="mt-1 block w-full rounded-xl border-2 border-gray-200 px-4 py-3 shadow-sm bg-gray-100 cursor-not-allowed"
          :class="{ 'border-red-500': errors.farmer }"
        />
        
        <p v-if="errors.farmer" class="mt-1 text-sm text-red-600">{{ errors.farmer }}</p>
        <p v-if="userRole === 'agricultor'" class="mt-1 text-xs text-gray-500">
          Este campo se completa automáticamente con tu nombre
        </p>
        <p v-if="agricultores.length === 0 && !loadingAgricultores && userRole === 'admin'" class="mt-1 text-xs text-amber-600">
          No hay agricultores registrados
        </p>
      </div>

      <!-- Finca -->
      <div>
        <label for="farm" class="flex items-center gap-2 text-sm font-semibold text-gray-700">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
          </svg>
          Finca <span class="text-red-500">*</span>
        </label>
        <select
          id="farm"
          v-model="formData.farm"
          :disabled="loadingFincas"
          class="mt-1 block w-full rounded-xl border-2 border-gray-200 px-4 py-3 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
          :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/30': errors.farm, 'bg-gray-100 cursor-wait': loadingFincas }"
        >
          <option value="">{{ loadingFincas ? 'Cargando fincas...' : 'Selecciona una finca' }}</option>
          <option v-for="finca in fincas" :key="finca.id" :value="finca.nombre">
            {{ finca.nombre }} - {{ finca.ubicacion || 'Sin ubicación' }}
          </option>
        </select>
        <p v-if="errors.farm" class="mt-1 text-sm text-red-600">{{ errors.farm }}</p>
        <p v-if="fincas.length === 0 && !loadingFincas" class="mt-1 text-xs text-amber-600">
          {{ userRole === 'agricultor' ? 'No tienes fincas registradas' : 'No hay fincas disponibles' }}
        </p>
      </div>

      <!-- Lugar de Origen -->
      <div>
        <label for="originPlace" class="flex items-center gap-2 text-sm font-semibold text-gray-700">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
          </svg>
          Lugar de origen <span class="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="originPlace"
          v-model="formData.originPlace"
          @input="updateForm"
          class="mt-1 block w-full rounded-xl border-2 border-gray-200 px-4 py-3 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
          :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/30': errors.originPlace }"
        />
        <p v-if="errors.originPlace" class="mt-1 text-sm text-red-600">{{ errors.originPlace }}</p>
      </div>

      <!-- Genética -->
      <div>
        <label for="genetics" class="flex items-center gap-2 text-sm font-semibold text-gray-700">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"></path>
          </svg>
          Genética <span class="text-red-500">*</span>
        </label>
        <select
          id="genetics"
          v-model="formData.genetics"
          @change="updateForm"
          class="mt-1 block w-full rounded-xl border-2 border-gray-200 px-4 py-3 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
          :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/30': errors.genetics }"
        >
          <option value="">Selecciona la genética</option>
          <option value="Criollo">Criollo</option>
          <option value="Forastero">Forastero</option>
          <option value="Trinitario">Trinitario</option>
          <option value="Nacional">Nacional</option>
          <option value="Híbrido">Híbrido</option>
          <option value="Otra">Otra</option>
        </select>
        <p v-if="errors.genetics" class="mt-1 text-sm text-red-600">{{ errors.genetics }}</p>
      </div>

      <!-- Nombre del Lote -->
      <div class="col-span-full sm:col-span-2">
        <label for="batchName" class="flex items-center gap-2 text-sm font-semibold text-gray-700">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
          </svg>
          Nombre o código del lote <span class="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="batchName"
          v-model="formData.name"
          @input="updateForm"
          class="mt-1 block w-full rounded-xl border-2 border-gray-200 px-4 py-3 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
          :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/30': errors.name }"
        />
        <p v-if="errors.name" class="mt-1 text-sm text-red-600 font-medium">{{ errors.name }}</p>
      </div>

      <!-- Fecha de Recolección -->
      <div>
        <label for="collectionDate" class="flex items-center gap-2 text-sm font-semibold text-gray-700">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
          </svg>
          Fecha de recolección <span class="text-red-500">*</span>
        </label>
        <input
          type="date"
          id="collectionDate"
          v-model="formData.collectionDate"
          @input="updateForm"
          class="mt-1 block w-full rounded-xl border-2 border-gray-200 px-4 py-3 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
          :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/30': errors.collectionDate }"
          :max="maxDate"
        />
        <p v-if="errors.collectionDate" class="mt-1 text-sm text-red-600 font-medium">{{ errors.collectionDate }}</p>
      </div>

      <!-- Origen -->
      <div>
        <label for="origin" class="flex items-center gap-2 text-sm font-semibold text-gray-700">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          Origen
        </label>
        <div class="mt-1">
          <select
            id="origin"
            v-model="formData.origin"
            @change="updateForm"
            class="block w-full rounded-xl border-2 border-gray-200 px-4 py-3 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
          >
            <option value="">Selecciona un origen</option>
            <option value="Piura">Piura</option>
            <option value="San Martín">San Martín</option>
            <option value="Cajamarca">Cajamarca</option>
            <option value="Otro">Otro</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Observaciones -->
    <div>
      <label for="notes" class="flex items-center gap-2 text-sm font-semibold text-gray-700">
        <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
        </svg>
        Observaciones (opcional)
      </label>
      <div class="mt-1">
        <textarea
          id="notes"
          v-model="formData.notes"
          @input="updateForm"
          rows="3"
          class="block w-full rounded-xl border-2 border-gray-200 px-4 py-3 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
          placeholder="Notas adicionales sobre el lote..."
        ></textarea>
      </div>
    </div>
  </div>
</template>

<script setup>
// 1. Vue core
import { ref, watch, onMounted } from 'vue'

// 2. Stores
import { useAuthStore } from '@/stores/auth'

// 3. Services
import { getFincas } from '@/services/fincasApi'
import authApi from '@/services/authApi'

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
  farm: '',
  originPlace: '',
  farmer: '',
  genetics: '',
  ...props.modelValue
})

const fincas = ref([])
const loadingFincas = ref(false)
const agricultores = ref([])
const loadingAgricultores = ref(false)
const allFincas = ref([])

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
    console.error('Error loading agricultores:', error)
    agricultores.value = []
  } finally {
    loadingAgricultores.value = false
  }
}

const loadAllFincas = async () => {
  try {
    const response = await getFincas()
    allFincas.value = response.results || []
  } catch (error) {
    console.error('Error loading all fincas:', error)
    allFincas.value = []
  }
}

const updateForm = () => {
  const mappedData = {
    name: formData.value.name || '',
    farm: formData.value.farm || '',
    originPlace: formData.value.originPlace || '',
    genetics: formData.value.genetics || '',
    collectionDate: formData.value.collectionDate || '',
    origin: '',
    notes: formData.value.notes || '',
    farmer: formData.value.farmer || ''
  }
  emit('update:modelValue', mappedData)
}

const handleFarmerChange = () => {
  if (props.userRole === 'agricultor') return
  
  if (formData.value.farmer) {
    const selectedAgricultor = agricultores.value.find(a => a.username === formData.value.farmer)
    if (selectedAgricultor) {
      fincas.value = allFincas.value.filter(finca => finca.agricultor_id === selectedAgricultor.id)
    } else {
      fincas.value = allFincas.value
    }
  } else {
    fincas.value = allFincas.value
  }
  
  updateForm()
}

const handleFincaChange = () => {
  if (props.userRole === 'agricultor') return
  
  if (formData.value.farm) {
    const selectedFinca = allFincas.value.find(f => f.nombre === formData.value.farm)
    if (selectedFinca && selectedFinca.agricultor_id) {
      const associatedAgricultor = agricultores.value.find(a => a.id === selectedFinca.agricultor_id)
      if (associatedAgricultor) {
        formData.value.farmer = associatedAgricultor.username
      }
    }
  }
  
  updateForm()
}

// Watchers
watch(() => props.modelValue, (newValue) => {
  formData.value = { ...newValue }
}, { deep: true })

watch(() => formData.value.farmer, () => {
  handleFarmerChange()
})

watch(() => formData.value.farm, () => {
  handleFincaChange()
})

// Lifecycle
onMounted(async () => {
  await loadAllFincas()
  await loadAgricultores()
  
  if (props.userRole === 'agricultor' && props.userId) {
    fincas.value = allFincas.value.filter(finca => finca.agricultor_id === props.userId) || []
  } else {
    fincas.value = allFincas.value
  }
  
  if (props.userRole === 'agricultor' && props.userName && !formData.value.farmer) {
    formData.value.farmer = props.userName
    emit('update:modelValue', { ...formData.value })
  }
})
</script>

<style scoped>
/* Solo estilos que no están en Tailwind si es necesario */
</style>
