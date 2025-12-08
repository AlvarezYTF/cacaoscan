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
            <li class="breadcrumb-item">
              <router-link :to="`/lotes/${loteId}`" v-if="loteId">
                {{ lote?.identificador || 'Lote' }}
              </router-link>
            </li>
            <li class="breadcrumb-item active" aria-current="page">
              Análisis
            </li>
          </ol>
        </nav>

        <!-- Header con acciones -->
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h2>
              <i class="fas fa-microscope me-2"></i>
              Análisis del Lote {{ lote?.identificador || 'Cargando...' }}
            </h2>
            <p class="text-muted mb-0">Resultados detallados del análisis de calidad</p>
          </div>
          <div>
            <button 
              @click="goBack" 
              class="btn btn-outline-secondary me-2"
            >
              <i class="fas fa-arrow-left me-2"></i>
              Volver
            </button>
            <button 
              @click="newAnalysis" 
              class="btn btn-primary"
            >
              <i class="fas fa-plus me-2"></i>
              Nuevo Análisis
            </button>
          </div>
        </div>

        <!-- Loading state -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" aria-label="Cargando análisis del lote">
            <span class="visually-hidden">Cargando...</span>
          </div>
          <p class="mt-3">Cargando análisis del lote...</p>
        </div>

        <!-- Error state -->
        <div v-else-if="error" class="alert alert-danger" role="alert">
          <h4 class="alert-heading">Error</h4>
          <p>{{ error }}</p>
          <hr>
          <button @click="loadAnalisis" class="btn btn-outline-danger">
            Intentar nuevamente
          </button>
        </div>

        <!-- Análisis content -->
        <div v-else-if="lote" class="row">
          <!-- Información del lote -->
          <div class="col-lg-4">
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">
                  <i class="fas fa-seedling me-2"></i>
                  Información del Lote
                </h5>
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <h6 class="text-muted">Identificador</h6>
                  <p class="mb-0">{{ lote.identificador }}</p>
                </div>
                <div class="mb-3">
                  <h6 class="text-muted">Variedad</h6>
                  <p class="mb-0">{{ lote.variedad }}</p>
                </div>
                <div class="mb-3">
                  <h6 class="text-muted">Área</h6>
                  <p class="mb-0">{{ lote.area_hectareas }} hectáreas</p>
                </div>
                <div class="mb-3">
                  <h6 class="text-muted">Fecha de Plantación</h6>
                  <p class="mb-0">{{ formatDate(lote.fecha_plantacion) }}</p>
                </div>
                <div v-if="finca">
                  <h6 class="text-muted">Finca</h6>
                  <p class="mb-0">
                    <router-link :to="`/fincas/${finca.id}`" class="text-decoration-none">
                      {{ finca.nombre }}
                    </router-link>
                  </p>
                </div>
              </div>
            </div>

            <!-- Resumen de calidad -->
            <div class="card mt-4">
              <div class="card-header">
                <h5 class="mb-0">
                  <i class="fas fa-chart-pie me-2"></i>
                  Resumen de Calidad
                </h5>
              </div>
              <div class="card-body">
                <div class="text-center">
                  <div class="quality-circle mb-3">
                    <div 
                      class="circle-progress"
                      :class="getQualityClass(analisisResumen.calidad_promedio)"
                    >
                      <span class="percentage">{{ analisisResumen.calidad_promedio || 0 }}%</span>
                    </div>
                  </div>
                  <h6 class="text-muted">Calidad Promedio</h6>
                  <p class="small text-muted">{{ getQualityDescription(analisisResumen.calidad_promedio) }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Resultados del análisis -->
          <div class="col-lg-8">
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">
                  <i class="fas fa-clipboard-list me-2"></i>
                  Resultados del Análisis
                </h5>
              </div>
              <div class="card-body">
                <!-- Estadísticas principales -->
                <div class="row mb-4">
                  <div class="col-md-3">
                    <div class="stat-card text-center">
                      <div class="stat-icon">
                        <i class="fas fa-weight text-primary"></i>
                      </div>
                      <h4 class="stat-value">{{ analisisResumen.peso_promedio || 0 }}g</h4>
                      <p class="stat-label">Peso Promedio</p>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="stat-card text-center">
                      <div class="stat-icon">
                        <i class="fas fa-expand-arrows-alt text-success"></i>
                      </div>
                      <h4 class="stat-value">{{ analisisResumen.tamaño_promedio || 0 }}mm</h4>
                      <p class="stat-label">Tamaño Promedio</p>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="stat-card text-center">
                      <div class="stat-icon">
                        <i class="fas fa-layer-group text-info"></i>
                      </div>
                      <h4 class="stat-value">{{ analisisResumen.grosor_promedio || 0 }}mm</h4>
                      <p class="stat-label">Grosor Promedio</p>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="stat-card text-center">
                      <div class="stat-icon">
                        <i class="fas fa-chart-line text-warning"></i>
                      </div>
                      <h4 class="stat-value">{{ analisisResumen.total_muestras || 0 }}</h4>
                      <p class="stat-label">Total Muestras</p>
                    </div>
                  </div>
                </div>

                <!-- Tabla de análisis detallados -->
                <div v-if="analisisDetallados.length > 0">
                  <h6 class="text-muted mb-3">Análisis Detallados</h6>
                  <div class="table-responsive">
                    <table class="table table-hover" aria-label="Tabla de análisis detallados del lote">
                      <caption class="sr-only">Tabla de análisis detallados mostrando fecha, tipo, peso, tamaño, grosor, calidad y estado de cada análisis</caption>
                      <thead>
                        <tr>  
                          <th>Fecha</th>
                          <th>Tipo</th>
                          <th>Peso (g)</th>
                          <th>Tamaño (mm)</th>
                          <th>Grosor (mm)</th>
                          <th>Calidad (%)</th>
                          <th>Estado</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="analisis in analisisDetallados" :key="analisis.id">
                          <td>{{ formatDate(analisis.fecha_analisis) }}</td>
                          <td>{{ analisis.tipo_analisis }}</td>
                          <td>{{ analisis.peso_promedio }}</td>
                          <td>{{ analisis.tamaño_promedio }}</td>
                          <td>{{ analisis.grosor_promedio }}</td>
                          <td>
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
                          </td>
                          <td>
                            <span 
                              class="badge"
                              :class="{
                                'bg-success': analisis.estado === 'completado',
                                'bg-warning': analisis.estado === 'procesando',
                                'bg-danger': analisis.estado === 'fallido'
                              }"
                            >
                              {{ analisis.estado_display }}
                            </span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <!-- Sin análisis -->
                <div v-else class="text-center py-5">
                  <i class="fas fa-microscope fa-3x text-muted mb-3"></i>
                  <h5 class="text-muted">No hay análisis disponibles</h5>
                  <p class="text-muted">Realiza el primer análisis de este lote</p>
                  <button @click="newAnalysis" class="btn btn-primary">
                    <i class="fas fa-plus me-2"></i>
                    Realizar Análisis
                  </button>
                </div>
              </div>
            </div>

            <!-- Recomendaciones -->
            <div class="card mt-4" v-if="recomendaciones.length > 0">
              <div class="card-header">
                <h5 class="mb-0">
                  <i class="fas fa-lightbulb me-2"></i>
                  Recomendaciones
                </h5>
              </div>
              <div class="card-body">
                <div class="list-group list-group-flush">
                  <div 
                    v-for="(recomendacion, index) in recomendaciones" 
                    :key="index"
                    class="list-group-item px-0"
                  >
                    <div class="d-flex align-items-start">
                      <i 
                        class="fas fa-chevron-right text-primary me-3 mt-1"
                      ></i>
                      <div>
                        <h6 class="mb-1">{{ recomendacion.titulo }}</h6>
                        <p class="mb-0 text-muted">{{ recomendacion.descripcion }}</p>
                      </div>
                    </div>
                  </div>
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

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

// Reactive data
const lote = ref(null)
const finca = ref(null)
const analisisDetallados = ref([])
const analisisResumen = ref({})
const recomendaciones = ref([])
const loading = ref(true)
const error = ref(null)

// Computed
const loteId = computed(() => route.params.id)

// Methods
const loadAnalisis = async () => {
  try {
    loading.value = true
    error.value = null
    
    // Cargar información del lote
    const loteResponse = await fetch(`/api/lotes/${loteId.value}/`, {
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!loteResponse.ok) {
      throw new Error(`Error ${loteResponse.status}: ${loteResponse.statusText}`)
    }
    
    lote.value = await loteResponse.json()
    
    // Cargar información de la finca
    if (lote.value.finca) {
      await loadFinca(lote.value.finca)
    }
    
    // Cargar análisis del lote
    await loadAnalisisData()
    
    // Generar recomendaciones
    generateRecomendaciones()
    
  } catch (err) {
    error.value = err.message
    } finally {
    loading.value = false
  }
}

const loadFinca = async (fincaId) => {
  try {
    const response = await fetch(`/api/fincas/${fincaId}/`, {
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      finca.value = await response.json()
    }
  } catch (err) {
    }
}

const loadAnalisisData = async () => {
  try {
    const response = await fetch(`/api/lotes/${loteId.value}/analisis/`, {
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      analisisDetallados.value = data.results || []
      
      // Calcular resumen
      if (analisisDetallados.value.length > 0) {
        analisisResumen.value = {
          peso_promedio: Math.round(
            analisisDetallados.value.reduce((sum, a) => sum + a.peso_promedio, 0) / 
            analisisDetallados.value.length
          ),
          tamaño_promedio: Math.round(
            analisisDetallados.value.reduce((sum, a) => sum + a.tamaño_promedio, 0) / 
            analisisDetallados.value.length
          ),
          grosor_promedio: Math.round(
            analisisDetallados.value.reduce((sum, a) => sum + a.grosor_promedio, 0) / 
            analisisDetallados.value.length
          ),
          calidad_promedio: Math.round(
            analisisDetallados.value.reduce((sum, a) => sum + a.calidad, 0) / 
            analisisDetallados.value.length
          ),
          total_muestras: analisisDetallados.value.length
        }
      }
    }
  } catch (err) {
    }
}

const generateRecomendaciones = () => {
  const calidad = analisisResumen.value.calidad_promedio || 0
  
  recomendaciones.value = []
  
  if (calidad < 60) {
    recomendaciones.value.push({
      titulo: 'Mejorar Proceso de Fermentación',
      descripcion: 'La calidad baja indica problemas en el proceso de fermentación. Revisar tiempos y condiciones.'
    })
  }
  
  if (analisisResumen.value.peso_promedio < 1) {
    recomendaciones.value.push({
      titulo: 'Optimizar Nutrición del Suelo',
      descripcion: 'El peso bajo sugiere deficiencias nutricionales. Considerar fertilización orgánica.'
    })
  }
  
  if (calidad >= 80) {
    recomendaciones.value.push({
      titulo: 'Mantener Estándares Actuales',
      descripcion: 'Excelente calidad. Continuar con las prácticas actuales de cultivo y procesamiento.'
    })
  }
}

const getQualityClass = (calidad) => {
  if (calidad >= 80) return 'quality-excellent'
  if (calidad >= 60) return 'quality-good'
  return 'quality-poor'
}

const getQualityDescription = (calidad) => {
  if (calidad >= 80) return 'Excelente calidad'
  if (calidad >= 60) return 'Buena calidad'
  return 'Calidad mejorable'
}

const goBack = () => {
  router.push(`/lotes/${loteId.value}`)
}

const newAnalysis = () => {
  router.push(`/analisis/new?lote=${loteId.value}`)
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('es-CO')
}

// Lifecycle
onMounted(() => {
  loadAnalisis()
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

.stat-card {
  padding: 1rem;
  border-radius: 0.5rem;
  background-color: #f8f9fa;
  transition: transform 0.2s ease-in-out;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #6c757d;
  margin-bottom: 0;
}

.quality-circle {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto;
}

.circle-progress {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  font-weight: 600;
  color: white;
}

.quality-excellent {
  background: linear-gradient(135deg, #28a745, #20c997);
}

.quality-good {
  background: linear-gradient(135deg, #ffc107, #fd7e14);
}

.quality-poor {
  background: linear-gradient(135deg, #dc3545, #e83e8c);
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

.table th {
  border-top: none;
  font-weight: 600;
  color: #495057;
}
</style>
