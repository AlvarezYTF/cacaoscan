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
              <router-link :to="`/fincas/${lote?.finca}`" v-if="lote?.finca">
                {{ finca?.nombre || 'Finca' }}
              </router-link>
            </li>
            <li class="breadcrumb-item">
              <router-link :to="`/fincas/${lote?.finca}/lotes`" v-if="lote?.finca">
                Lotes
              </router-link>
            </li>
            <li class="breadcrumb-item active" aria-current="page">
              {{ lote?.identificador || 'Cargando...' }}
            </li>
          </ol>
        </nav>

        <!-- Loading state -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" aria-label="Cargando información del lote">
            <span class="visually-hidden">Cargando...</span>
          </div>
          <p class="mt-3">Cargando información del lote...</p>
        </div>

        <!-- Error state -->
        <div v-else-if="error" class="alert alert-danger" role="alert">
          <h4 class="alert-heading">Error</h4>
          <p>{{ error }}</p>
          <hr>
          <button @click="loadLote" class="btn btn-outline-danger">
            Intentar nuevamente
          </button>
        </div>

        <!-- Lote content -->
        <div v-else-if="lote" class="row">
          <!-- Información principal -->
          <div class="col-lg-8">
            <div class="card">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">
                  <i class="fas fa-seedling me-2"></i>
                  {{ lote.identificador }}
                </h5>
                <div>
                  <button 
                    @click="editLote" 
                    class="btn btn-outline-primary btn-sm me-2"
                    v-if="canEdit"
                  >
                    <i class="fas fa-edit"></i> Editar
                  </button>
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
                </div>
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-md-6">
                    <h6 class="text-muted">Variedad</h6>
                    <p class="mb-3">
                      <i class="fas fa-leaf me-2"></i>
                      {{ lote.variedad }}
                    </p>
                    
                    <h6 class="text-muted">Área</h6>
                    <p class="mb-3">
                      <i class="fas fa-expand-arrows-alt me-2"></i>
                      {{ lote.area_hectareas }} hectáreas
                    </p>
                  </div>
                  <div class="col-md-6">
                    <h6 class="text-muted">Fecha de Plantación</h6>
                    <p class="mb-3">
                      <i class="fas fa-calendar me-2"></i>
                      {{ formatDate(lote.fecha_plantacion) }}
                    </p>
                    
                    <h6 class="text-muted">Fecha de Registro</h6>
                    <p class="mb-3">
                      <i class="fas fa-calendar-plus me-2"></i>
                      {{ formatDate(lote.fecha_registro) }}
                    </p>
                  </div>
                </div>

                <div v-if="lote.descripcion" class="mt-3">
                  <h6 class="text-muted">Descripción</h6>
                  <p class="text-muted">{{ lote.descripcion }}</p>
                </div>

                <!-- Información de la finca -->
                <div v-if="finca" class="mt-3">
                  <h6 class="text-muted">Finca</h6>
                  <p class="text-muted">
                    <i class="fas fa-map-marker-alt me-2"></i>
                    <router-link :to="`/fincas/${finca.id}`" class="text-decoration-none">
                      {{ finca.nombre }}
                    </router-link>
                  </p>
                </div>
              </div>
            </div>

            <!-- Estadísticas del lote -->
            <div class="card mt-4">
              <div class="card-header">
                <h5 class="mb-0">
                  <i class="fas fa-chart-bar me-2"></i>
                  Estadísticas del Lote
                </h5>
              </div>
              <div class="card-body">
                <div class="row text-center">
                  <div class="col-md-3">
                    <div class="border-end">
                      <h3 class="text-primary">{{ lote.total_analisis || 0 }}</h3>
                      <p class="text-muted mb-0">Análisis Realizados</p>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="border-end">
                      <h3 class="text-success">{{ lote.analisis_exitosos || 0 }}</h3>
                      <p class="text-muted mb-0">Análisis Exitosos</p>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="border-end">
                      <h3 class="text-info">{{ lote.promedio_calidad || 0 }}%</h3>
                      <p class="text-muted mb-0">Calidad Promedio</p>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <h3 class="text-warning">{{ lote.ultimo_analisis || 'N/A' }}</h3>
                    <p class="text-muted mb-0">Último Análisis</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Sidebar con acciones -->
          <div class="col-lg-4">
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">
                  <i class="fas fa-tools me-2"></i>
                  Acciones
                </h5>
              </div>
              <div class="card-body">
                <div class="d-grid gap-2">
                  <button 
                    @click="analyzeLote" 
                    class="btn btn-success"
                  >
                    <i class="fas fa-microscope me-2"></i>
                    Realizar Análisis
                  </button>
                  
                  <button 
                    @click="viewAnalisis" 
                    class="btn btn-outline-info"
                    v-if="lote.total_analisis > 0"
                  >
                    <i class="fas fa-chart-line me-2"></i>
                    Ver Análisis
                  </button>
                  
                  <button 
                    @click="generateReport" 
                    class="btn btn-outline-primary"
                  >
                    <i class="fas fa-file-pdf me-2"></i>
                    Generar Reporte
                  </button>
                  
                  <button 
                    @click="deleteLote" 
                    class="btn btn-outline-danger"
                    v-if="canDelete"
                  >
                    <i class="fas fa-trash me-2"></i>
                    Eliminar Lote
                  </button>
                </div>
              </div>
            </div>

            <!-- Análisis recientes -->
            <div class="card mt-4" v-if="analisisRecientes.length > 0">
              <div class="card-header">
                <h5 class="mb-0">
                  <i class="fas fa-microscope me-2"></i>
                  Análisis Recientes
                </h5>
              </div>
              <div class="card-body">
                <div class="list-group list-group-flush">
                  <div 
                    v-for="analisis in analisisRecientes" 
                    :key="analisis.id"
                    class="list-group-item px-0"
                  >
                    <div class="d-flex justify-content-between align-items-center">
                      <div>
                        <h6 class="mb-1">{{ formatDate(analisis.fecha_analisis) }}</h6>
                        <small class="text-muted">{{ analisis.tipo_analisis }}</small>
                      </div>
                      <span 
                        class="badge"
                        :class="{
                          'bg-success': analisis.calidad >= 80,
                          'bg-warning': analisis.calidad >= 60 && analisis.calidad < 80,
                          'bg-danger': analisis.calidad < 60
                        }"
                      >
                        {{ analisis.calidad }}%
                      </span>
                    </div>
                  </div>
                </div>
                <div class="text-center mt-3">
                  <button 
                    @click="viewAnalisis" 
                    class="btn btn-sm btn-outline-primary"
                  >
                    Ver todos los análisis
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import api from '@/services/api'
import Swal from 'sweetalert2'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

// Reactive data
const lote = ref(null)
const finca = ref(null)
const analisisRecientes = ref([])
const loading = ref(true)
const error = ref(null)

// Computed
const canEdit = computed(() => {
  return authStore.userRole === 'admin' || 
         (authStore.userRole === 'farmer' && finca.value?.agricultor === authStore.user?.id)
})

const canDelete = computed(() => {
  return authStore.userRole === 'admin' || 
         (authStore.userRole === 'farmer' && finca.value?.agricultor === authStore.user?.id)
})

// Methods
const loadLote = async () => {
  try {
    loading.value = true
    error.value = null
    
    // Usar axios con interceptor JWT
    const response = await api.get(`/lotes/${route.params.id}/`)
    
    lote.value = response.data
    
    // Cargar información de la finca
    if (lote.value.finca) {
      await loadFinca(lote.value.finca)
    }
    
    // Cargar análisis recientes
    await loadAnalisisRecientes()
    
  } catch (err) {
    console.error('Error cargando lote:', err)
    
    // Manejar diferentes tipos de errores
    if (err.response) {
      if (err.response.status === 404) {
        error.value = 'El lote no existe o fue desactivado.'
        router.push({ name: 'Fincas' })
      } else if (err.response.status === 403) {
        error.value = 'No tienes permiso para ver este lote.'
        router.push({ name: 'Fincas' })
      } else if (err.response.status === 401) {
        error.value = 'Tu sesión ha expirado. Redirigiendo al login...'
        setTimeout(() => {
          authStore.logout(false)
        }, 2000)
      } else {
        error.value = err.response.data?.detail || `Error ${err.response.status}`
      }
    } else if (err.request) {
      error.value = 'No se pudo conectar al servidor. Verifica tu conexión.'
    } else {
      error.value = err.message || 'Error desconocido'
    }
  } finally {
    loading.value = false
  }
}

const loadFinca = async (fincaId) => {
  try {
    const response = await api.get(`/api/v1/fincas/${fincaId}/`)
    finca.value = response.data
  } catch (err) {
    console.error('Error cargando finca:', err)
    // Ignorar - no es crítico
  }
}

const loadAnalisisRecientes = async () => {
  try {
    const response = await api.get(`/lotes/${route.params.id}/analisis/`)
    analisisRecientes.value = response.data.results?.slice(0, 5) || []
  } catch (err) {
    console.error('Error cargando análisis:', err)
    // Ignorar - no es crítico
  }
}

const editLote = () => {
  router.push(`/lotes/${lote.value.id}/edit`)
}

const analyzeLote = () => {
  router.push(`/analisis/new?lote=${lote.value.id}`)
}

const viewAnalisis = () => {
  router.push(`/lotes/${lote.value.id}/analisis`)
}

const generateReport = async () => {
  try {
    await Swal.fire({
      title: 'Generando Reporte',
      text: 'Se está generando el reporte del lote...',
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading()
      }
    })
    
    await api.post('/reportes/', {
      tipo_reporte: 'lote',
      formato: 'pdf',
      titulo: `Reporte de Lote: ${lote.value.identificador}`,
      parametros: {
        lote_id: lote.value.id
      }
    })
    
    await Swal.fire({
      title: 'Reporte Generado',
      text: 'El reporte se ha generado exitosamente',
      icon: 'success'
    })
    
    router.push('/reportes')
  } catch (err) {
    console.error('Error generando reporte:', err)
    await Swal.fire({
      title: 'Error',
      text: 'No se pudo generar el reporte',
      icon: 'error'
    })
  }
}

const deleteLote = async () => {
  const result = await Swal.fire({
    title: '¿Eliminar Lote?',
    text: 'Esta acción no se puede deshacer',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    cancelButtonColor: '#3085d6',
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar'
  })
  
  if (result.isConfirmed) {
    try {
      await api.delete(`/lotes/${lote.value.id}/`)
      
      await Swal.fire({
        title: 'Eliminado',
        text: 'El lote ha sido eliminado exitosamente',
        icon: 'success'
      })
      
      router.push(`/fincas/${lote.value.finca}/lotes`)
    } catch (err) {
      console.error('Error eliminando lote:', err)
      await Swal.fire({
        title: 'Error',
        text: 'No se pudo eliminar el lote',
        icon: 'error'
      })
    }
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('es-CO')
}

// Lifecycle
onMounted(() => {
  loadLote()
})
</script>

<style scoped>
.border-end:last-child {
  border-right: none !important;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.card-header {
  background-color: rgba(0, 0, 0, 0.03);
  border-bottom: 1px solid rgba(0, 0, 0, 0.125);
}

.list-group-item {
  border-left: none;
  border-right: none;
}

.list-group-item:first-child {
  border-top: none;
}

.list-group-item:last-child {
  border-bottom: none;
}
</style>
