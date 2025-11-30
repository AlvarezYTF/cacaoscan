<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-12">
        <!-- Header con breadcrumb -->
        <nav aria-label="breadcrumb" class="mb-4">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link to="/fincas">Fincas</router-link>
            </li>
            <li class="breadcrumb-item">
              <router-link :to="`/fincas/${fincaId}`">{{ finca?.nombre || 'Finca' }}</router-link>
            </li>
            <li class="breadcrumb-item active" aria-current="page">
              Lotes
            </li>
          </ol>
        </nav>

        <!-- Header con acciones -->
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h2>
              <i class="fas fa-seedling me-2"></i>
              Lotes de {{ finca?.nombre || 'Finca' }}
            </h2>
            <p class="text-muted mb-0">Gestiona los lotes de esta finca</p>
          </div>
          <div>
            <button 
              @click="createLote" 
              class="btn btn-primary"
              v-if="canCreate"
            >
              <i class="fas fa-plus me-2"></i>
              Nuevo Lote
            </button>
          </div>
        </div>

        <!-- Loading state -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" aria-label="Cargando lotes">
            <span class="visually-hidden">Cargando...</span>
          </div>
          <p class="mt-3">Cargando lotes...</p>
        </div>

        <!-- Error state -->
        <div v-else-if="error" class="alert alert-danger" role="alert">
          <h4 class="alert-heading">Error</h4>
          <p>{{ error }}</p>
          <hr>
          <button @click="loadLotes" class="btn btn-outline-danger">
            Intentar nuevamente
          </button>
        </div>

        <!-- Lotes content -->
        <div v-else>
          <!-- Filtros -->
          <div class="card mb-4">
            <div class="card-body">
              <div class="row">
                <div class="col-md-4">
                  <label for="search" class="form-label">Buscar</label>
                  <input 
                    type="text" 
                    id="search" 
                    v-model="filters.search" 
                    class="form-control"
                    placeholder="Buscar por identificador o variedad..."
                    @input="debouncedSearch"
                  >
                </div>
                <div class="col-md-3">
                  <label for="estado" class="form-label">Estado</label>
                  <select id="estado" v-model="filters.estado" class="form-select">
                    <option value="">Todos los estados</option>
                    <option value="activo">Activo</option>
                    <option value="inactivo">Inactivo</option>
                    <option value="cosechado">Cosechado</option>
                  </select>
                </div>
                <div class="col-md-3">
                  <label for="variedad" class="form-label">Variedad</label>
                  <select id="variedad" v-model="filters.variedad" class="form-select">
                    <option value="">Todas las variedades</option>
                    <option 
                      v-for="variedad in variedades" 
                      :key="variedad" 
                      :value="variedad"
                    >
                      {{ variedad }}
                    </option>
                  </select>
                </div>
                <div class="col-md-2 d-flex align-items-end">
                  <button @click="clearFilters" class="btn btn-outline-secondary w-100">
                    <i class="fas fa-times me-1"></i>
                    Limpiar
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Estadísticas -->
          <div class="row mb-4">
            <div class="col-md-3">
              <div class="card text-center">
                <div class="card-body">
                  <h3 class="text-primary">{{ stats.total }}</h3>
                  <p class="text-muted mb-0">Total Lotes</p>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="card text-center">
                <div class="card-body">
                  <h3 class="text-success">{{ stats.activos }}</h3>
                  <p class="text-muted mb-0">Activos</p>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="card text-center">
                <div class="card-body">
                  <h3 class="text-warning">{{ stats.cosechados }}</h3>
                  <p class="text-muted mb-0">Cosechados</p>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="card text-center">
                <div class="card-body">
                  <h3 class="text-info">{{ stats.analisis }}</h3>
                  <p class="text-muted mb-0">Con Análisis</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Tabla de lotes -->
          <div class="card">
            <div class="card-body">
              <div class="table-responsive">
                image.png                <table class="table table-hover" aria-label="Tabla de lotes de la finca">
                  <caption class="sr-only">Tabla de lotes mostrando identificador, variedad, área, estado, fecha de plantación, análisis y acciones disponibles</caption>
                  <thead>
                    <tr>
                      <th>Identificador</th>
                      <th>Variedad</th>
                      <th>Área (ha)</th>
                      <th>Estado</th>
                      <th>Fecha Plantación</th>
                      <th>Análisis</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="lote in displayedLotes" :key="lote.id">
                      <td>
                        <div class="d-flex align-items-center">
                          <i class="fas fa-seedling text-success me-2"></i>
                          <strong>{{ lote.identificador }}</strong>
                        </div>
                      </td>
                      <td>{{ lote.variedad }}</td>
                      <td>{{ lote.area_hectareas }}</td>
                      <td>
                        <span 
                          class="badge"
                          :class="{
                            'bg-success': lote.estado === 'activo',
                            'bg-warning': lote.estado === 'inactivo',
                            'bg-info': lote.estado === 'cosechado'
                          }"
                        >
                          {{ lote.estado_display }}
                        </span>
                      </td>
                      <td>{{ formatDate(lote.fecha_plantacion) }}</td>
                      <td>
                        <span class="badge bg-primary" v-if="lote.total_analisis > 0">
                          {{ lote.total_analisis }} análisis
                        </span>
                        <span class="text-muted" v-else>Sin análisis</span>
                      </td>
                      <td>
                        <div class="btn-group btn-group-sm">
                          <button 
                            @click="viewLote(lote.id)" 
                            class="btn btn-outline-primary"
                            title="Ver detalles"
                          >
                            <i class="fas fa-eye"></i>
                          </button>
                          <button 
                            @click="editLote(lote.id)" 
                            class="btn btn-outline-secondary"
                            title="Editar"
                            v-if="canEdit"
                          >
                            <i class="fas fa-edit"></i>
                          </button>
                          <button 
                            @click="analyzeLote(lote.id)" 
                            class="btn btn-outline-success"
                            title="Analizar"
                          >
                            <i class="fas fa-microscope"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Paginación -->
              <nav v-if="totalPages > 1" class="mt-4" aria-label="Navegación de paginación">
                <ul class="pagination justify-content-center">
                  <li class="page-item" :class="{ disabled: currentPage === 1 }">
                    <button 
                      @click="changePage(currentPage - 1)" 
                      class="page-link"
                      :disabled="currentPage === 1"
                    >
                      Anterior
                    </button>
                  </li>
                  <li 
                    v-for="page in visiblePages" 
                    :key="page"
                    class="page-item"
                    :class="{ active: page === currentPage }"
                  >
                    <button @click="changePage(page)" class="page-link">
                      {{ page }}
                    </button>
                  </li>
                  <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                    <button 
                      @click="changePage(currentPage + 1)" 
                      class="page-link"
                      :disabled="currentPage === totalPages"
                    >
                      Siguiente
                    </button>
                  </li>
                </ul>
              </nav>

              <!-- Sin resultados -->
              <div v-if="filteredLotes.length === 0" class="text-center py-5">
                <i class="fas fa-seedling fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">No se encontraron lotes</h5>
                <p class="text-muted">Intenta ajustar los filtros de búsqueda</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import { usePagination } from '@/composables/usePagination'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

// Reactive data
const finca = ref(null)
const lotes = ref([])
const variedades = ref([])
const loading = ref(true)
const error = ref(null)

// Paginación usando composable
const pagination = usePagination(1, 10)

// Filters
const filters = reactive({
  search: '',
  estado: '',
  variedad: ''
})

// Computed
const fincaId = computed(() => route.params.id)

const canCreate = computed(() => {
  return authStore.userRole === 'admin' || 
         (authStore.userRole === 'farmer' && finca.value?.agricultor === authStore.user?.id)
})

const canEdit = computed(() => {
  return authStore.userRole === 'admin' || 
         (authStore.userRole === 'farmer' && finca.value?.agricultor === authStore.user?.id)
})

const filteredLotes = computed(() => {
  let filtered = lotes.value

  if (filters.search) {
    const search = filters.search.toLowerCase()
    filtered = filtered.filter(lote => 
      lote.identificador.toLowerCase().includes(search) ||
      lote.variedad.toLowerCase().includes(search)
    )
  }

  if (filters.estado) {
    filtered = filtered.filter(lote => lote.estado === filters.estado)
  }

  if (filters.variedad) {
    filtered = filtered.filter(lote => lote.variedad === filters.variedad)
  }

  return filtered
})

const stats = computed(() => {
  return {
    total: lotes.value.length,
    activos: lotes.value.filter(l => l.estado === 'activo').length,
    cosechados: lotes.value.filter(l => l.estado === 'cosechado').length,
    analisis: lotes.value.filter(l => l.total_analisis > 0).length
  }
})

// Actualizar totalItems en paginación cuando cambian los filteredLotes
watch(() => filteredLotes.value.length, (newTotal) => {
  pagination.updatePagination({
    page: pagination.currentPage.value,
    page_size: pagination.itemsPerPage.value,
    count: newTotal
  })
}, { immediate: true })

// Computed para compatibilidad con el template
const currentPage = computed(() => pagination.currentPage.value)
const totalPages = computed(() => pagination.totalPages.value)
const itemsPerPage = computed(() => pagination.itemsPerPage.value)

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, pagination.currentPage.value - 2)
  const end = Math.min(pagination.totalPages.value, start + 4)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// Lotes mostrados en la página actual (paginación en cliente)
const displayedLotes = computed(() => {
  const start = (pagination.currentPage.value - 1) * pagination.itemsPerPage.value
  const end = start + pagination.itemsPerPage.value
  return filteredLotes.value.slice(start, end)
})

// Methods
const loadFinca = async () => {
  try {
    const response = await fetch(`/api/fincas/${fincaId.value}/`, {
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      finca.value = await response.json()
    }
  } catch (err) {
    console.error('Error cargando finca:', err)
  }
}

const loadLotes = async () => {
  try {
    loading.value = true
    error.value = null
    
    const response = await fetch(`/api/fincas/${fincaId.value}/lotes/`, {
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    lotes.value = data.results || []
    
    // Extraer variedades únicas
    variedades.value = [...new Set(lotes.value.map(l => l.variedad))].sort()
    
  } catch (err) {
    error.value = err.message
    console.error('Error cargando lotes:', err)
  } finally {
    loading.value = false
  }
}

const createLote = () => {
  router.push(`/fincas/${fincaId.value}/lotes/new`)
}

const viewLote = (loteId) => {
  router.push(`/lotes/${loteId}`)
}

const editLote = (loteId) => {
  router.push(`/lotes/${loteId}/edit`)
}

const analyzeLote = (loteId) => {
  router.push(`/analisis/new?lote=${loteId}`)
}

const clearFilters = () => {
  filters.search = ''
  filters.estado = ''
  filters.variedad = ''
  pagination.goToPage(1)
}

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    pagination.goToPage(page)
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('es-CO')
}

// Debounced search
let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    pagination.goToPage(1)
  }, 300)
}

// Watchers
watch(() => filters.estado, () => {
  pagination.goToPage(1)
})

watch(() => filters.variedad, () => {
  pagination.goToPage(1)
})

// Lifecycle
onMounted(() => {
  loadFinca()
  loadLotes()
})
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.card-header {
  background-color: rgba(0, 0, 0, 0.03);
  border-bottom: 1px solid rgba(0, 0, 0, 0.125);
}

.table th {
  border-top: none;
  font-weight: 600;
  color: #495057;
}

.btn-group-sm > .btn {
  padding: 0.25rem 0.5rem;
}

.pagination .page-link {
  color: #007bff;
  border-color: #dee2e6;
}

.pagination .page-item.active .page-link {
  background-color: #007bff;
  border-color: #007bff;
}

.pagination .page-item.disabled .page-link {
  color: #6c757d;
  background-color: #fff;
  border-color: #dee2e6;
}
</style>
