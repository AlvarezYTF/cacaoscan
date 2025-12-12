<template>
  <div class="max-w-7xl mx-auto px-4 py-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Gestión de Lotes</h1>
        <p class="text-gray-600 mt-1">Administra los lotes de cacao</p>
      </div>
      <button
        @click="openCreateModal"
        type="button"
        class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
        </svg>
        Nuevo Lote
      </button>
    </div>

    <!-- Filtros -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label for="search" class="block text-sm font-medium text-gray-700 mb-1">Buscar</label>
          <input
            id="search"
            v-model="searchQuery"
            type="text"
            placeholder="Identificador, variedad..."
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 transition-all duration-200"
            @input="debouncedSearch"
          />
        </div>
        <div>
          <label for="finca-filter" class="block text-sm font-medium text-gray-700 mb-1">Finca</label>
          <select
            id="finca-filter"
            v-model="filters.finca"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 transition-all duration-200"
            @change="applyFilters"
          >
            <option value="">Todas las fincas</option>
            <option v-for="finca in fincas" :key="finca.id" :value="finca.id">
              {{ finca.nombre }}
            </option>
          </select>
        </div>
        <div>
          <label for="estado-filter" class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
          <select
            id="estado-filter"
            v-model="filters.estado"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 transition-all duration-200"
            @change="applyFilters"
          >
            <option value="">Todos</option>
            <option v-for="estado in estadosLote" :key="estado.value" :value="estado.value">
              {{ estado.label }}
            </option>
          </select>
        </div>
        <div class="flex items-end">
          <button
            @click="clearFilters"
            type="button"
            class="w-full bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
          >
            Limpiar Filtros
          </button>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <div class="flex items-center">
        <svg class="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <span class="text-red-800">{{ error }}</span>
      </div>
    </div>

    <!-- Lista de lotes -->
    <div v-else-if="lotes.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="lote in lotes"
        :key="lote.id"
        class="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow cursor-pointer"
        @click="viewLote(lote)"
      >
        <div class="p-6">
          <!-- Header -->
          <div class="flex justify-between items-start mb-4">
            <div>
              <h3 class="text-lg font-semibold text-gray-900">{{ lote.identificador }}</h3>
              <p class="text-sm text-gray-600">{{ lote.variedad }}</p>
            </div>
            <span
              :class="[
                'px-2 py-1 text-xs font-medium rounded-full',
                getEstadoColor(lote.estado)
              ]"
            >
              {{ getEstadoLabel(lote.estado) }}
            </span>
          </div>

          <!-- Información -->
          <div class="space-y-2 mb-4">
            <div class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
              </svg>
              {{ lote.finca?.nombre || 'Sin finca' }}
            </div>
            <div class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
              </svg>
              {{ lote.area_hectareas }} hectáreas
            </div>
            <div class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
              </svg>
              Plantado: {{ formatDate(lote.fecha_plantacion) }}
            </div>
          </div>

          <!-- Estadísticas -->
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div class="text-center">
              <div class="text-2xl font-bold text-blue-600">{{ lote.total_analisis || 0 }}</div>
              <div class="text-xs text-gray-500">Análisis</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-green-600">{{ lote.edad_meses || 0 }}</div>
              <div class="text-xs text-gray-500">Meses</div>
            </div>
          </div>

          <!-- Acciones -->
          <div class="flex gap-2">
            <button
              @click.stop="editLote(lote)"
              type="button"
              class="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-md text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Editar
            </button>
            <button
              @click.stop="viewAnalisis(lote)"
              type="button"
              class="flex-1 bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-md text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              Ver Análisis
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
      <h3 class="mt-2 text-sm font-medium text-gray-900">No hay lotes registrados</h3>
      <p class="mt-1 text-sm text-gray-500">Comienza creando tu primer lote.</p>
      <div class="mt-6">
        <button
          @click="openCreateModal"
          type="button"
          class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        >
          Crear Primer Lote
        </button>
      </div>
    </div>

    <!-- Modal de formulario -->
    <LoteForm
      v-if="showModal"
      :lote="selectedLote"
      :is-editing="isEditing"
      @close="closeModal"
      @saved="handleLoteSaved"
    />

    <!-- Modal de detalle de lote -->
    <Teleport to="body">
      <LoteDetailModal
        v-if="showDetailModal"
        :show="showDetailModal"
        :lote-id="selectedLoteId"
        @close="closeDetailModal"
      />
    </Teleport>
  </div>
</template>

<script setup>
// 1. Vue core
import { ref, onMounted, computed } from 'vue'

// 2. Vue router
import { useRouter } from 'vue-router'

// 3. Components
import LoteForm from '@/components/LoteForm.vue'
import LoteDetailModal from '@/components/common/LotesViewComponents/LoteDetailModal.vue'

// 4. Services
import lotesApi from '@/services/lotesApi'
import fincasApi from '@/services/fincasApi'

// Router
const router = useRouter()

// State
const lotes = ref([])
const fincas = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')
const filters = ref({
  finca: '',
  estado: ''
})
const showModal = ref(false)
const selectedLote = ref(null)
const isEditing = ref(false)
const showDetailModal = ref(false)
const selectedLoteId = ref(null)

// Computed
const estadosLote = computed(() => lotesApi.getEstadosLote())

// Debounced search
let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadLotes()
  }, 500)
}

// Functions
const loadLotes = async () => {
  loading.value = true
  error.value = null
  
  try {
    const params = {
      search: searchQuery.value,
      finca: filters.value.finca,
      estado: filters.value.estado
    }
    
    const response = await lotesApi.getLotes(params)
    lotes.value = response.results || response
  } catch (err) {
    error.value = 'Error al cargar los lotes. Intenta nuevamente.'
    } finally {
    loading.value = false
  }
}

const loadFincas = async () => {
  try {
    const response = await fincasApi.getFincas()
    fincas.value = response.results || response
  } catch (err) {
    }
}

const applyFilters = () => {
  loadLotes()
}

const clearFilters = () => {
  searchQuery.value = ''
  filters.value = {
    finca: '',
    estado: ''
  }
  loadLotes()
}

const openCreateModal = () => {
  selectedLote.value = null
  isEditing.value = false
  showModal.value = true
}

const editLote = (lote) => {
  selectedLote.value = lote
  isEditing.value = true
  showModal.value = true
}

const viewLote = (lote) => {
  const loteId = typeof lote === 'object' ? lote.id : lote
  selectedLoteId.value = loteId
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedLoteId.value = null
}

const viewAnalisis = (lote) => {
  router.push(`/lotes/${lote.id}/analisis`)
}

const closeModal = () => {
  showModal.value = false
  selectedLote.value = null
  isEditing.value = false
}

const handleLoteSaved = () => {
  closeModal()
  loadLotes()
}

const getEstadoColor = (estado) => {
  const colors = {
    activo: 'bg-green-100 text-green-800',
    inactivo: 'bg-gray-100 text-gray-800',
    cosechado: 'bg-yellow-100 text-yellow-800',
    renovado: 'bg-blue-100 text-blue-800'
  }
  return colors[estado] || 'bg-gray-100 text-gray-800'
}

const getEstadoLabel = (estado) => {
  const labels = {
    activo: 'Activo',
    inactivo: 'Inactivo',
    cosechado: 'Cosechado',
    renovado: 'Renovado'
  }
  return labels[estado] || estado
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('es-CO')
}

// Lifecycle
onMounted(() => {
  loadLotes()
  loadFincas()
})
</script>

<style scoped>
/* Solo estilos que no están en Tailwind si es necesario */
</style>
