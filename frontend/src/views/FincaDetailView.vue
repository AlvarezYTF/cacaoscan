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
            <li class="breadcrumb-item active" aria-current="page">
              {{ finca?.nombre || 'Cargando...' }}
            </li>
          </ol>
        </nav>

        <!-- Loading state -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" aria-live="polite" aria-label="Cargando información">
            <span class="visually-hidden">Cargando...</span>
          </div>
          <p class="mt-3">Cargando información de la finca...</p>
        </div>

        <!-- Error state -->
        <div v-else-if="error" class="alert alert-danger" role="alert">
          <h4 class="alert-heading">Error</h4>
          <p>{{ error }}</p>
          <hr>
          <button @click="loadFinca" class="btn btn-outline-danger">
            Intentar nuevamente
          </button>
        </div>

        <!-- Finca content -->
        <div v-else-if="finca" class="row">
          <!-- Información principal -->
          <div class="col-lg-8">
            <div class="card">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">
                  <i class="fas fa-map-marker-alt me-2"></i>
                  {{ finca.nombre }}
                </h5>
                <div>
                  <button 
                    @click="editFinca" 
                    class="btn btn-outline-primary btn-sm me-2"
                    v-if="canEdit"
                  >
                    <i class="fas fa-edit"></i> Editar
                  </button>
                  <span 
                    class="badge"
                    :class="finca.activa ? 'bg-success' : 'bg-secondary'"
                  >
                    {{ finca.activa ? 'Activa' : 'Inactiva' }}
                  </span>
                </div>
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-md-6">
                    <h6 class="text-muted">Ubicación</h6>
                    <p class="mb-3">
                      <i class="fas fa-map-marker-alt me-2"></i>
                      {{ finca.ubicacion_completa }}
                    </p>
                    
                    <h6 class="text-muted">Agricultor</h6>
                    <p class="mb-3">
                      <i class="fas fa-user me-2"></i>
                      {{ finca.agricultor_name }}
                    </p>
                  </div>
                  <div class="col-md-6">
                    <h6 class="text-muted">Área</h6>
                    <p class="mb-3">
                      <i class="fas fa-expand-arrows-alt me-2"></i>
                      {{ finca.hectareas }} hectáreas
                    </p>
                    
                    <h6 class="text-muted">Fecha de Registro</h6>
                    <p class="mb-3">
                      <i class="fas fa-calendar me-2"></i>
                      {{ formatDate(finca.fecha_registro) }}
                    </p>
                  </div>
                </div>

                <div v-if="finca.descripcion" class="mt-3">
                  <h6 class="text-muted">Descripción</h6>
                  <p class="text-muted">{{ finca.descripcion }}</p>
                </div>
              </div>
            </div>

            <!-- 🌍 Mapa de ubicación -->
            <FincaLocationMap
              :nombre="finca.nombre"
              :latitud="finca.coordenadas_lat"
              :longitud="finca.coordenadas_lng"
            />

            <!-- Estadísticas -->
            <div class="card mt-4">
              <div class="card-header">
                <h5 class="mb-0">
                  <i class="fas fa-chart-bar me-2"></i>
                  Estadísticas
                </h5>
              </div>
              <div class="card-body">
                <div class="row text-center">
                  <div class="col-md-3">
                    <div class="border-end">
                      <h3 class="text-primary">{{ finca.estadisticas?.total_lotes || 0 }}</h3>
                      <p class="text-muted mb-0">Total de Lotes</p>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="border-end">
                      <h3 class="text-success">{{ finca.estadisticas?.lotes_activos || 0 }}</h3>
                      <p class="text-muted mb-0">Lotes Activos</p>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="border-end">
                      <h3 class="text-info">{{ finca.estadisticas?.total_analisis || 0 }}</h3>
                      <p class="text-muted mb-0">Análisis Realizados</p>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <h3 class="text-warning">{{ finca.estadisticas?.calidad_promedio || 0 }}%</h3>
                    <p class="text-muted mb-0">Calidad Promedio</p>
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
                  <router-link 
                    :to="`/fincas/${finca.id}/lotes`"
                    class="btn btn-primary"
                  >
                    <i class="fas fa-seedling me-2"></i>
                    Ver Lotes
                  </router-link>
                  
                  <button 
                    @click="createLote" 
                    class="btn btn-outline-success"
                    v-if="canEdit"
                  >
                    <i class="fas fa-plus me-2"></i>
                    Nuevo Lote
                  </button>
                  
                  <button 
                    @click="generateReport" 
                    class="btn btn-outline-info"
                  >
                    <i class="fas fa-file-pdf me-2"></i>
                    Generar Reporte
                  </button>
                  
                  <button 
                    @click="viewOnMap" 
                    class="btn btn-outline-secondary"
                    v-if="finca.coordenadas_lat && finca.coordenadas_lng"
                  >
                    <i class="fas fa-map me-2"></i>
                    Ver en Mapa
                  </button>
                </div>
              </div>
            </div>

            <!-- Lotes recientes -->
            <div class="card mt-4" v-if="lotesRecientes.length > 0">
              <div class="card-header">
                <h5 class="mb-0">
                  <i class="fas fa-seedling me-2"></i>
                  Lotes Recientes
                </h5>
              </div>
              <div class="card-body">
                <div class="list-group list-group-flush">
                  <div 
                    v-for="lote in lotesRecientes" 
                    :key="lote.id"
                    class="list-group-item px-0"
                  >
                    <div class="d-flex justify-content-between align-items-center">
                      <div>
                        <h6 class="mb-1">{{ lote.identificador }}</h6>
                        <small class="text-muted">{{ lote.variedad }}</small>
                      </div>
                      <span 
                        class="badge"
                        :class="{
                          'bg-success': lote.estado === 'activo',
                          'bg-warning': lote.estado === 'inactivo',
                          'bg-info': lote.estado === 'cosechado'
                        }"
                      >
                        {{ lote.estado }}
                      </span>
                    </div>
                  </div>
                </div>
                <div class="text-center mt-3">
                  <router-link 
                    :to="`/fincas/${finca.id}/lotes`"
                    class="btn btn-sm btn-outline-primary"
                  >
                    Ver todos los lotes
                  </router-link>
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
// 1. Vue core
import { ref, onMounted, computed } from 'vue'

// 2. Router
import { useRoute, useRouter } from 'vue-router'

// 3. Stores
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'

// 4. Services
import api from '@/services/api'

// 5. Libraries
import Swal from 'sweetalert2'

// 6. Components
import FincaLocationMap from '@/components/fincas/FincaLocationMap.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

// Reactive data
const finca = ref(null)
const lotesRecientes = ref([])
const loading = ref(true)
const error = ref(null)

// Computed
const canEdit = computed(() => {
  return authStore.userRole === 'admin' || 
         (authStore.userRole === 'farmer' && finca.value?.agricultor === authStore.user?.id)
})

// Methods
const loadFinca = async () => {
  try {
    loading.value = true
    error.value = null
    
    // Usar la instancia de axios con interceptor JWT
    const response = await api.get(`/api/v1/fincas/${route.params.id}/`)
    
    finca.value = response.data
    
    // Cargar lotes recientes
    await loadLotesRecientes()
    
  } catch (err) {
    
    // Manejar diferentes tipos de errores
    if (err.response) {
      if (err.response.status === 404) {
        error.value = 'La finca no existe o fue desactivada.'
        router.push({ name: 'Fincas', query: { notFound: 'true' } })
      } else if (err.response.status === 403) {
        error.value = 'No tienes permiso para ver esta finca.'
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

const loadLotesRecientes = async () => {
  try {
    const response = await api.get(`/api/v1/fincas/${route.params.id}/lotes/`)
    lotesRecientes.value = response.data.results?.slice(0, 5) || []
  } catch (err) {
    // Ignorar errores de lotes - no es crítico para mostrar la finca
  }
}

const editFinca = () => {
  router.push(`/fincas/${finca.value.id}/edit`)
}

const createLote = () => {
  router.push(`/fincas/${finca.value.id}/lotes/new`)
}

const generateReport = async () => {
  try {
    await Swal.fire({
      title: 'Generando Reporte',
      text: 'Se está generando el reporte de la finca...',
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading()
      }
    })
    
    const response = await fetch('/api/reportes/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        tipo_reporte: 'finca',
        formato: 'pdf',
        titulo: `Reporte de Finca: ${finca.value.nombre}`,
        parametros: {
          finca_id: finca.value.id
        }
      })
    })
    
    if (response.ok) {
      await response.json()
      await Swal.fire({
        title: 'Reporte Generado',
        text: 'El reporte se ha generado exitosamente',
        icon: 'success'
      })
      
      // Redirigir a la vista de reportes
      router.push('/reportes')
    } else {
      throw new Error('Error generando reporte')
    }
  } catch (err) {
    await Swal.fire({
      title: 'Error',
      text: 'No se pudo generar el reporte',
      icon: 'error'
    })
  }
}

const viewOnMap = () => {
  const lat = finca.value.coordenadas_lat
  const lng = finca.value.coordenadas_lng
  const url = `https://www.google.com/maps?q=${lat},${lng}`
  window.open(url, '_blank')
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('es-CO')
}

// Lifecycle
onMounted(() => {
  loadFinca()
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
