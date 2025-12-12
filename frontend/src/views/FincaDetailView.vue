<template>
  <BaseDetailView
    :loading="loading"
    :error="error"
    :title="finca?.nombre || 'Cargando...'"
    :subtitle="finca?.ubicacion_completa"
    :icon="'fas fa-map-marker-alt'"
    :breadcrumbs="breadcrumbs"
    :show-edit-button="true"
    :can-edit="canEdit"
    :status-badge="finca?.activa ? 'Activa' : 'Inactiva'"
    :statistics="statistics"
    loading-text="Cargando información de la finca..."
    @edit="editFinca"
    @retry="loadFinca"
  >
    <template #main>
      <!-- Información principal -->
      <div class="card">
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <h6 class="text-muted">Ubicación</h6>
              <p class="mb-3">
                <i class="fas fa-map-marker-alt me-2"></i>
                {{ finca?.ubicacion_completa || 'N/A' }}
              </p>
              
              <h6 class="text-muted">Agricultor</h6>
              <p class="mb-3">
                <i class="fas fa-user me-2"></i>
                {{ finca?.agricultor_name || 'N/A' }}
              </p>
            </div>
            <div class="col-md-6">
              <h6 class="text-muted">Área</h6>
              <p class="mb-3">
                <i class="fas fa-expand-arrows-alt me-2"></i>
                {{ finca?.hectareas || 0 }} hectáreas
              </p>
              
              <h6 class="text-muted">Fecha de Registro</h6>
              <p class="mb-3">
                <i class="fas fa-calendar me-2"></i>
                {{ formatDate(finca?.fecha_registro) }}
              </p>
            </div>
          </div>

          <div v-if="finca?.descripcion" class="mt-3">
            <h6 class="text-muted">Descripción</h6>
            <p class="text-muted">{{ finca.descripcion }}</p>
          </div>
        </div>
      </div>

      <!-- Mapa de ubicación -->
      <FincaLocationMap
        v-if="finca?.coordenadas_lat && finca?.coordenadas_lng"
        :nombre="finca.nombre"
        :latitud="finca.coordenadas_lat"
        :longitud="finca.coordenadas_lng"
      />
    </template>

    <template #actions>
      <router-link 
        :to="`/fincas/${finca?.id}/lotes`"
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
        v-if="finca?.coordenadas_lat && finca?.coordenadas_lng"
      >
        <i class="fas fa-map me-2"></i>
        Ver en Mapa
      </button>
    </template>

    <template #sidebar>
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
              :to="`/fincas/${finca?.id}/lotes`"
              class="btn btn-sm btn-outline-primary"
            >
              Ver todos los lotes
            </router-link>
          </div>
        </div>
      </div>
    </template>
  </BaseDetailView>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailView from '@/components/common/BaseDetailView.vue'
import FincaLocationMap from '@/components/fincas/FincaLocationMap.vue'
import { useFincas } from '@/composables/useFincas'
import { useDateFormatting } from '@/composables/useDateFormatting'
import Swal from 'sweetalert2'

const route = useRoute()
const router = useRouter()

// Use composables
const { loading, error, finca, loadFinca: loadFincaData, canEdit: canEditFinca } = useFincas()
const { formatDate } = useDateFormatting()

// Local state
const lotesRecientes = ref([])

// Computed
const canEdit = computed(() => canEditFinca(finca.value))

const breadcrumbs = computed(() => [
  { label: 'Fincas', to: '/fincas' },
  { label: finca.value?.nombre || 'Cargando...', to: null }
])

const statistics = computed(() => {
  if (!finca.value?.estadisticas) return []
  
  return [
    {
      label: 'Total de Lotes',
      value: finca.value.estadisticas.total_lotes || 0,
      color: 'primary'
    },
    {
      label: 'Lotes Activos',
      value: finca.value.estadisticas.lotes_activos || 0,
      color: 'success'
    },
    {
      label: 'Análisis Realizados',
      value: finca.value.estadisticas.total_analisis || 0,
      color: 'info'
    },
    {
      label: 'Calidad Promedio',
      value: `${finca.value.estadisticas.calidad_promedio || 0}%`,
      color: 'warning'
    }
  ]
})

// Methods
const loadFinca = async () => {
  try {
    await loadFincaData(route.params.id)
    await loadLotesRecientes()
  } catch (err) {
    if (err.response?.status === 404) {
      router.push({ name: 'Fincas', query: { notFound: 'true' } })
    } else if (err.response?.status === 403) {
      router.push({ name: 'Fincas' })
    }
  }
}

const loadLotesRecientes = async () => {
  if (!finca.value?.id) return
  
  try {
    const { loadLotesByFinca } = useFincas()
    const lotes = await loadLotesByFinca(finca.value.id)
    lotesRecientes.value = lotes.slice(0, 5)
  } catch (err) {
    lotesRecientes.value = []
  }
}

const editFinca = () => {
  if (finca.value?.id) {
    router.push(`/fincas/${finca.value.id}/edit`)
  }
}

const createLote = () => {
  if (finca.value?.id) {
    router.push(`/fincas/${finca.value.id}/lotes/new`)
  }
}

const generateReport = async () => {
  if (!finca.value) return
  
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
        'Authorization': `Bearer ${localStorage.getItem('access_token') || localStorage.getItem('token')}`,
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
      await Swal.fire({
        title: 'Reporte Generado',
        text: 'El reporte se ha generado exitosamente',
        icon: 'success'
      })
      router.push('/reportes')
    } else {
      throw new Error('Error generando reporte')
    }
  } catch (err) {
    await Swal.fire({
      title: 'Error',
      text: err.message || 'No se pudo generar el reporte',
      icon: 'error'
    })
  }
}

const viewOnMap = () => {
  if (!finca.value?.coordenadas_lat || !finca.value?.coordenadas_lng) return
  
  const lat = finca.value.coordenadas_lat
  const lng = finca.value.coordenadas_lng
  const url = `https://www.google.com/maps?q=${lat},${lng}`
  globalThis.open(url, '_blank')
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
