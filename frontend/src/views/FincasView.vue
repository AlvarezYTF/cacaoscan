<template>
  <div class="fincas-view">
    <!-- Header con título y botón de nueva finca -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Gestión de Fincas</h1>
        <p class="text-gray-600 mt-1">Administra las fincas de cacao registradas</p>
      </div>
      <button
        @click="openCreateModal"
        class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
        </svg>
        Nueva Finca
      </button>
    </div>

    <!-- Filtros y búsqueda -->
    <div class="bg-white rounded-lg shadow-sm border p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Buscar</label>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Nombre, municipio, departamento..."
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            @input="debouncedSearch"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Departamento</label>
          <select
            v-model="filters.departamento"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            @change="applyFilters"
          >
            <option value="">Todos los departamentos</option>
            <option v-for="dept in departamentos" :key="dept" :value="dept">
              {{ dept }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
          <select
            v-model="filters.activa"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            @change="applyFilters"
          >
            <option value="">Todos</option>
            <option value="true">Activas</option>
            <option value="false">Inactivas</option>
          </select>
        </div>
        <div class="flex items-end">
          <button
            @click="clearFilters"
            class="w-full bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-md transition-colors"
          >
            Limpiar Filtros
          </button>
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <div class="flex items-center">
        <svg class="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <span class="text-red-800">{{ error }}</span>
      </div>
    </div>

    <!-- Lista de fincas -->
    <div v-else-if="fincas.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="finca in fincas"
        :key="finca.id"
        class="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow cursor-pointer"
        @click="viewFinca(finca)"
      >
        <div class="p-6">
          <!-- Header de la tarjeta -->
          <div class="flex justify-between items-start mb-4">
            <div>
              <h3 class="text-lg font-semibold text-gray-900">{{ finca.nombre }}</h3>
              <p class="text-sm text-gray-600">{{ finca.municipio }}, {{ finca.departamento }}</p>
            </div>
            <span
              :class="[
                'px-2 py-1 text-xs font-medium rounded-full',
                finca.activa ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              ]"
            >
              {{ finca.activa ? 'Activa' : 'Inactiva' }}
            </span>
          </div>

          <!-- Información de la finca -->
          <div class="space-y-2 mb-4">
            <div class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
              {{ finca.ubicacion }}
            </div>
            <div class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
              </svg>
              {{ finca.hectareas }} hectáreas
            </div>
          </div>

          <!-- Estadísticas -->
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div class="text-center">
              <div class="text-2xl font-bold text-green-600">{{ finca.total_lotes || 0 }}</div>
              <div class="text-xs text-gray-500">Lotes</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-blue-600">{{ finca.total_analisis || 0 }}</div>
              <div class="text-xs text-gray-500">Análisis</div>
            </div>
          </div>

          <!-- Acciones -->
          <div class="flex gap-2">
            <button
              @click.stop="editFinca(finca)"
              class="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-md text-sm transition-colors"
            >
              Editar
            </button>
            <button
              @click.stop="viewLotes(finca)"
              class="flex-1 bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-md text-sm transition-colors"
            >
              Ver Lotes
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">No hay fincas registradas</h3>
      <p class="mt-1 text-sm text-gray-500">Comienza creando tu primera finca.</p>
      <div class="mt-6">
        <button
          @click="openCreateModal"
          class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm transition-colors"
        >
          Crear Primera Finca
        </button>
      </div>
    </div>

    <!-- Modal de formulario -->
    <FincaForm
      v-if="showModal"
      :finca="selectedFinca"
      :is-editing="isEditing"
      @close="closeModal"
      @saved="handleFincaSaved"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import FincaForm from '@/components/FincaForm.vue'
import fincasApi from '@/services/fincasApi'

const router = useRouter()

// Estado reactivo
const fincas = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')
const filters = ref({
  departamento: '',
  activa: ''
})
const showModal = ref(false)
const selectedFinca = ref(null)
const isEditing = ref(false)

// Computed
const departamentos = computed(() => fincasApi.getDepartamentosColombia())

// Debounced search
let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadFincas()
  }, 500)
}

// Métodos
const loadFincas = async () => {
  loading.value = true
  error.value = null
  
  try {
    const params = {
      search: searchQuery.value,
      departamento: filters.value.departamento,
      activa: filters.value.activa
    }
    
    const response = await fincasApi.getFincas(params)
    fincas.value = response.results || response
  } catch (err) {
    error.value = 'Error al cargar las fincas. Intenta nuevamente.'
    console.error('Error loading fincas:', err)
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  loadFincas()
}

const clearFilters = () => {
  searchQuery.value = ''
  filters.value = {
    departamento: '',
    activa: ''
  }
  loadFincas()
}

const openCreateModal = () => {
  selectedFinca.value = null
  isEditing.value = false
  showModal.value = true
}

const editFinca = (finca) => {
  selectedFinca.value = finca
  isEditing.value = true
  showModal.value = true
}

const viewFinca = (finca) => {
  router.push(`/fincas/${finca.id}`)
}

const viewLotes = (finca) => {
  router.push(`/fincas/${finca.id}/lotes`)
}

const closeModal = () => {
  showModal.value = false
  selectedFinca.value = null
  isEditing.value = false
}

const handleFincaSaved = () => {
  closeModal()
  loadFincas()
}

// Lifecycle
onMounted(() => {
  loadFincas()
})
</script>

<style scoped>
.fincas-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}
</style>
