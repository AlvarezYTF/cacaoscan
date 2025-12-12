<template>
  <BaseDetailView
    :loading="loading"
    :error="error"
    :title="lote?.identificador || 'Cargando...'"
    :subtitle="finca?.nombre ? `Finca: ${finca.nombre}` : (lote?.finca_nombre ? `Finca: ${lote.finca_nombre}` : '')"
    :icon="'fas fa-seedling'"
    :breadcrumbs="breadcrumbs"
    :show-edit-button="true"
    :can-edit="canEdit"
    :status-badge="getEstadoBadge(lote)"
    :statistics="statistics"
    loading-text="Cargando información del lote..."
    @edit="editLote"
    @retry="loadLote"
  >
    <template #main>
      <!-- Información principal -->
      <div class="card">
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <h6 class="text-muted">Variedad</h6>
              <p class="mb-3">
                <i class="fas fa-leaf me-2"></i>
                {{ variedadDisplay || 'N/A' }}
              </p>
              
              <h6 class="text-muted">Área</h6>
              <p class="mb-3">
                <i class="fas fa-expand-arrows-alt me-2"></i>
                {{ lote?.area_hectareas || 0 }} hectáreas
              </p>
              
              <h6 class="text-muted">Finca</h6>
              <p class="mb-3">
                <i class="fas fa-map-marker-alt me-2"></i>
                <router-link 
                  v-if="finca?.id" 
                  :to="`/fincas/${finca.id}`" 
                  class="text-decoration-none"
                >
                  {{ finca.nombre || 'N/A' }}
                </router-link>
                <span v-else-if="lote?.finca_nombre">{{ lote.finca_nombre }}</span>
                <span v-else>N/A</span>
              </p>
            </div>
            <div class="col-md-6">
              <h6 class="text-muted">Fecha de Plantación</h6>
              <p class="mb-3">
                <i class="fas fa-calendar me-2"></i>
                {{ formatDate(lote?.fecha_plantacion) }}
              </p>
              
              <h6 class="text-muted">Fecha de Registro</h6>
              <p class="mb-3">
                <i class="fas fa-calendar me-2"></i>
                {{ formatDate(lote?.fecha_registro) }}
              </p>
            </div>
          </div>

          <div v-if="lote?.descripcion" class="mt-3">
            <h6 class="text-muted">Descripción</h6>
            <p class="text-muted">{{ lote.descripcion }}</p>
          </div>
        </div>
      </div>
    </template>

    <template #actions>
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
        v-if="(lote?.total_analisis || 0) > 0"
      >
        <i class="fas fa-chart-line me-2"></i>
        Ver Análisis
      </button>
      
      <button 
        @click="generateReport" 
        class="btn btn-outline-info"
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
    </template>

    <template #sidebar>
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
                  <small class="text-muted">{{ analisis.tipo_analisis || 'Análisis' }}</small>
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
      <!-- Mensaje cuando no hay análisis -->
      <div class="card mt-4" v-else-if="lote && !loading">
        <div class="card-header">
          <h5 class="mb-0">
            <i class="fas fa-microscope me-2"></i>
            Análisis Recientes
          </h5>
        </div>
        <div class="card-body text-center py-4">
          <i class="fas fa-microscope text-muted mb-3" style="font-size: 2rem;"></i>
          <p class="text-muted mb-0">No hay análisis disponibles</p>
          <button 
            @click="analyzeLote" 
            class="btn btn-sm btn-success mt-3"
          >
            <i class="fas fa-plus me-2"></i>
            Realizar Primer Análisis
          </button>
        </div>
      </div>
    </template>
  </BaseDetailView>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailView from '@/components/common/BaseDetailView.vue'
import { useLotes } from '@/composables/useLotes'
import { useDateFormatting } from '@/composables/useDateFormatting'
import api from '@/services/api'
import Swal from 'sweetalert2'

const route = useRoute()
const router = useRouter()

// Use composables
const { 
  loading, 
  error, 
  lote, 
  finca, 
  loadLote: loadLoteFromComposable, 
  canEdit: canEditLote,
  canDelete: canDeleteLote
} = useLotes()
const { formatDate } = useDateFormatting()

// Local state
const analisisRecientes = ref([])

// Computed
const canEdit = computed(() => canEditLote(lote.value))
const canDelete = computed(() => canDeleteLote(lote.value))

const breadcrumbs = computed(() => {
  const crumbs = [
    { label: 'Fincas', to: '/fincas' }
  ]
  
  if (finca.value?.id) {
    crumbs.push({ label: finca.value.nombre || 'Finca', to: `/fincas/${finca.value.id}` })
    crumbs.push({ label: 'Lotes', to: `/fincas/${finca.value.id}/lotes` })
  }
  
  crumbs.push({ label: lote.value?.identificador || 'Cargando...', to: null })
  
  return crumbs
})

const getEstadoBadge = (loteData) => {
  if (!loteData) return null
  
  if (loteData.estado_display) {
    return String(loteData.estado_display)
  }
  
  if (loteData.estado) {
    if (typeof loteData.estado === 'object' && loteData.estado.nombre) {
      return String(loteData.estado.nombre)
    }
    if (typeof loteData.estado === 'string') {
      return loteData.estado
    }
  }
  
  return null
}

const variedadDisplay = computed(() => {
  const variedad = lote.value?.variedad
  if (!variedad) return null
  if (typeof variedad === 'object' && variedad.nombre) {
    return variedad.nombre
  }
  if (typeof variedad === 'object' && variedad.codigo) {
    return variedad.codigo
  }
  if (typeof variedad === 'string') {
    return variedad
  }
  return String(variedad)
})

const statistics = computed(() => {
  // Always return statistics, even if lote is not loaded yet
  if (!lote.value) {
    return [
      {
        label: 'Análisis Realizados',
        value: 0,
        color: 'primary'
      },
      {
        label: 'Análisis Exitosos',
        value: 0,
        color: 'success'
      },
      {
        label: 'Calidad Promedio',
        value: '0%',
        color: 'info'
      },
      {
        label: 'Último Análisis',
        value: 'N/A',
        color: 'warning'
      }
    ]
  }
  
  // Usar estadisticas del objeto si está disponible, sino usar valores directos
  const stats = lote.value.estadisticas || {}
  
  const totalAnalisis = stats.total_analisis ?? lote.value.total_analisis ?? 0
  const analisisProcesados = stats.analisis_procesados ?? lote.value.analisis_procesados ?? lote.value.analisis_exitosos ?? 0
  const calidadPromedio = stats.calidad_promedio ?? lote.value.promedio_calidad ?? 0
  const ultimoAnalisis = lote.value.ultimo_analisis || 'N/A'
  
  return [
    {
      label: 'Análisis Realizados',
      value: totalAnalisis,
      color: 'primary'
    },
    {
      label: 'Análisis Exitosos',
      value: analisisProcesados,
      color: 'success'
    },
    {
      label: 'Calidad Promedio',
      value: calidadPromedio ? `${calidadPromedio}%` : '0%',
      color: 'info'
    },
    {
      label: 'Último Análisis',
      value: ultimoAnalisis,
      color: 'warning'
    }
  ]
})

// Methods
const loadLote = async () => {
  try {
    await loadLoteFromComposable(route.params.id)
    await loadAnalisisRecientes()
  } catch (err) {
    if (err.response?.status === 404) {
      router.push({ name: 'Fincas', query: { notFound: 'true' } })
    } else if (err.response?.status === 403) {
      router.push({ name: 'Fincas' })
    }
  }
}

const loadAnalisisRecientes = async () => {
  if (!lote.value?.id) return
  
  try {
    const response = await api.get(`/lotes/${lote.value.id}/analisis/`)
    analisisRecientes.value = response.data.results?.slice(0, 5) || []
  } catch (err) {
    // Silently fail if endpoint doesn't exist or returns 404
    analisisRecientes.value = []
  }
}

const editLote = () => {
  if (lote.value?.id) {
    router.push(`/lotes/${lote.value.id}/edit`)
  }
}

const analyzeLote = () => {
  if (lote.value?.id) {
    router.push(`/analisis?lote=${lote.value.id}`)
  }
}

const viewAnalisis = () => {
  if (lote.value?.id) {
    router.push(`/lotes/${lote.value.id}/analisis`)
  }
}

const generateReport = async () => {
  if (!lote.value) return
  
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
    await Swal.fire({
      title: 'Error',
      text: err.message || 'No se pudo generar el reporte',
      icon: 'error'
    })
  }
}

const deleteLote = async () => {
  if (!lote.value) return
  
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
      
      if (lote.value.finca) {
        const fincaId = typeof lote.value.finca === 'object' ? lote.value.finca.id : lote.value.finca
        router.push(`/fincas/${fincaId}/lotes`)
      } else {
        router.push('/fincas')
      }
    } catch (err) {
      await Swal.fire({
        title: 'Error',
        text: err.message || 'No se pudo eliminar el lote',
        icon: 'error'
      })
    }
  }
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
