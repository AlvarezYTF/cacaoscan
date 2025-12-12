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
                  <p class="mb-0">{{ lote.variedad?.nombre || lote.variedad || 'N/A' }}</p>
                </div>
                <div class="mb-3">
                  <h6 class="text-muted">Peso</h6>
                  <p class="mb-0">{{ lote.peso_kg || 0 }} kg</p>
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
            <!-- Estadísticas principales -->
            <div class="row mb-4">
              <div class="col-md-3 col-6 mb-3">
                <div class="card stat-card text-center h-100">
                  <div class="card-body">
                    <div class="stat-icon mb-2">
                      <i class="fas fa-weight text-primary fa-2x"></i>
                    </div>
                    <h4 class="stat-value mb-1">{{ analisisResumen.peso_promedio || '0.00' }}g</h4>
                    <p class="stat-label mb-0">Peso Promedio</p>
                  </div>
                </div>
              </div>
              <div class="col-md-3 col-6 mb-3">
                <div class="card stat-card text-center h-100">
                  <div class="card-body">
                    <div class="stat-icon mb-2">
                      <i class="fas fa-expand-arrows-alt text-success fa-2x"></i>
                    </div>
                    <h4 class="stat-value mb-1">{{ analisisResumen.tamaño_promedio || '0.00' }}mm</h4>
                    <p class="stat-label mb-0">Tamaño Promedio</p>
                  </div>
                </div>
              </div>
              <div class="col-md-3 col-6 mb-3">
                <div class="card stat-card text-center h-100">
                  <div class="card-body">
                    <div class="stat-icon mb-2">
                      <i class="fas fa-layer-group text-info fa-2x"></i>
                    </div>
                    <h4 class="stat-value mb-1">{{ analisisResumen.grosor_promedio || '0.00' }}mm</h4>
                    <p class="stat-label mb-0">Grosor Promedio</p>
                  </div>
                </div>
              </div>
              <div class="col-md-3 col-6 mb-3">
                <div class="card stat-card text-center h-100">
                  <div class="card-body">
                    <div class="stat-icon mb-2">
                      <i class="fas fa-chart-line text-warning fa-2x"></i>
                    </div>
                    <h4 class="stat-value mb-1">{{ analisisResumen.total_muestras || 0 }}</h4>
                    <p class="stat-label mb-0">Total Muestras</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Grid de imágenes con análisis detallados -->
            <div class="card">
              <div class="card-header bg-white">
                <h5 class="mb-0">
                  <i class="fas fa-images me-2 text-primary"></i>
                  Análisis Detallados por Imagen
                  <span class="badge bg-primary ms-2">{{ analisisDetallados.length }}</span>
                </h5>
              </div>
              <div class="card-body">
                <div v-if="analisisDetallados.length > 0" class="row g-4">
                    <div 
                      v-for="analisis in analisisDetallados" 
                      :key="analisis.id"
                      class="col-md-6 col-lg-4"
                    >
                      <div class="card h-100 shadow-sm border analysis-card">
                        <!-- Imagen -->
                        <div class="position-relative" style="height: 220px; overflow: hidden; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);">
                          <img 
                            v-if="analisis.image_url"
                            :src="analisis.image_url" 
                            :alt="`Análisis ${analisis.id}`"
                            class="w-100 h-100"
                            style="object-fit: cover; transition: transform 0.3s ease;"
                            @error="handleImageError"
                            @mouseenter="$event.target.style.transform = 'scale(1.05)'"
                            @mouseleave="$event.target.style.transform = 'scale(1)'"
                          />
                          <div v-else class="d-flex flex-column align-items-center justify-content-center h-100 text-muted">
                            <i class="fas fa-image fa-4x mb-2 opacity-50"></i>
                            <small>Sin imagen</small>
                          </div>
                          <!-- Badge de calidad -->
                          <div class="position-absolute top-0 end-0 m-2">
                            <span 
                              class="badge shadow-sm"
                              :class="{
                                'bg-success': analisis.calidad >= 80,
                                'bg-warning': analisis.calidad >= 60 && analisis.calidad < 80,
                                'bg-danger': analisis.calidad < 60
                              }"
                              style="font-size: 0.85rem; padding: 0.4rem 0.6rem;"
                            >
                              <i class="fas fa-star me-1"></i>{{ analisis.calidad || 0 }}%
                            </span>
                          </div>
                        </div>
                        
                        <!-- Datos del análisis -->
                        <div class="card-body">
                          <div class="d-flex justify-content-between align-items-center mb-3 pb-2 border-bottom">
                            <h6 class="card-title mb-0">
                              <i class="fas fa-hashtag me-1 text-primary"></i>
                              <small>Análisis #{{ analisis.id }}</small>
                            </h6>
                            <small class="text-muted">
                              <i class="fas fa-calendar-alt me-1"></i>
                              {{ formatDate(analisis.fecha_analisis) }}
                            </small>
                          </div>
                          
                          <!-- Dimensiones -->
                          <div v-if="analisis.prediction" class="mb-3">
                            <div class="row g-2 mb-2">
                              <div class="col-6">
                                <div class="d-flex align-items-center">
                                  <i class="fas fa-arrows-alt-v text-primary me-2"></i>
                                  <div>
                                    <small class="text-muted d-block">Alto</small>
                                    <strong>{{ (analisis.prediction.alto_mm || 0).toFixed(2) }} mm</strong>
                                  </div>
                                </div>
                              </div>
                              <div class="col-6">
                                <div class="d-flex align-items-center">
                                  <i class="fas fa-arrows-alt-h text-success me-2"></i>
                                  <div>
                                    <small class="text-muted d-block">Ancho</small>
                                    <strong>{{ (analisis.prediction.ancho_mm || 0).toFixed(2) }} mm</strong>
                                  </div>
                                </div>
                              </div>
                            </div>
                            <div class="row g-2 mb-2">
                              <div class="col-6">
                                <div class="d-flex align-items-center">
                                  <i class="fas fa-layer-group text-info me-2"></i>
                                  <div>
                                    <small class="text-muted d-block">Grosor</small>
                                    <strong>{{ (analisis.prediction.grosor_mm || 0).toFixed(2) }} mm</strong>
                                  </div>
                                </div>
                              </div>
                              <div class="col-6">
                                <div class="d-flex align-items-center">
                                  <i class="fas fa-weight text-warning me-2"></i>
                                  <div>
                                    <small class="text-muted d-block">Peso</small>
                                    <strong>{{ (analisis.prediction.peso_g || 0).toFixed(2) }} g</strong>
                                  </div>
                                </div>
                              </div>
                            </div>
                            
                            <!-- Confianzas -->
                            <div v-if="analisis.prediction.average_confidence" class="mt-3 pt-3 border-top">
                              <small class="text-muted d-block mb-2">Confianza Promedio</small>
                              <div class="progress" style="height: 8px;">
                                <div 
                                  class="progress-bar"
                                  :class="{
                                    'bg-success': analisis.prediction.average_confidence >= 0.8,
                                    'bg-warning': analisis.prediction.average_confidence >= 0.6 && analisis.prediction.average_confidence < 0.8,
                                    'bg-danger': analisis.prediction.average_confidence < 0.6
                                  }"
                                  :style="{ width: `${(analisis.prediction.average_confidence * 100)}%` }"
                                  role="progressbar"
                                  :aria-valuenow="analisis.prediction.average_confidence * 100"
                                  aria-valuemin="0"
                                  aria-valuemax="100"
                                >
                                </div>
                              </div>
                              <small class="text-muted mt-1">
                                {{ ((analisis.prediction.average_confidence || 0) * 100).toFixed(1) }}%
                              </small>
                            </div>
                          </div>
                          
                          <!-- Sin predicción -->
                          <div v-else class="text-center py-3">
                            <i class="fas fa-exclamation-triangle text-warning mb-2"></i>
                            <p class="text-muted mb-0 small">Sin datos de predicción</p>
                          </div>
                        </div>
                      </div>
                    </div>
                </div>

                <!-- Sin análisis -->
                <div v-else class="text-center py-5">
                  <i class="fas fa-microscope fa-3x text-muted mb-3"></i>
                  <h5 class="text-muted">No hay análisis disponibles</h5>
                  <p class="text-muted mb-4">Realiza el primer análisis de este lote</p>
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
    
    const api = (await import('@/services/api')).default
    
    // Cargar información del lote
    const loteResponse = await api.get(`/lotes/${loteId.value}/`)
    lote.value = loteResponse.data
    
    // Cargar información de la finca
    if (lote.value.finca) {
      await loadFinca(lote.value.finca)
    }
    
    // Cargar análisis del lote
    await loadAnalisisData()
    
    // Generar recomendaciones
    generateRecomendaciones()
    
  } catch (err) {
    console.error('Error loading análisis:', err)
    error.value = err.response?.data?.error || err.message || 'Error al cargar los datos del lote'
    } finally {
    loading.value = false
  }
}

const loadFinca = async (fincaId) => {
  try {
    const api = (await import('@/services/api')).default
    const response = await api.get(`/fincas/${fincaId}/`)
    finca.value = response.data
  } catch (err) {
    console.error('Error loading finca:', err)
    }
}

const loadAnalisisData = async () => {
  try {
    const api = (await import('@/services/api')).default
    const response = await api.get(`/lotes/${loteId.value}/analisis/`)
    
    const data = response.data
      analisisDetallados.value = data.results || []
      
    // Calcular resumen basado en las predicciones
      if (analisisDetallados.value.length > 0) {
      const predictions = analisisDetallados.value
        .filter(a => a.prediction)
        .map(a => a.prediction)
      
      if (predictions.length > 0) {
        analisisResumen.value = {
          peso_promedio: (predictions.reduce((sum, p) => sum + (parseFloat(p.peso_g) || 0), 0) / predictions.length).toFixed(2),
          tamaño_promedio: (predictions.reduce((sum, p) => sum + (parseFloat(p.alto_mm) || 0), 0) / predictions.length).toFixed(2),
          grosor_promedio: (predictions.reduce((sum, p) => sum + (parseFloat(p.grosor_mm) || 0), 0) / predictions.length).toFixed(2),
          calidad_promedio: Math.round(
            analisisDetallados.value.reduce((sum, a) => sum + (a.calidad || 0), 0) / 
            analisisDetallados.value.length
          ),
          total_muestras: analisisDetallados.value.length
        }
      } else {
        analisisResumen.value = {
          peso_promedio: 0,
          tamaño_promedio: 0,
          grosor_promedio: 0,
          calidad_promedio: 0,
          total_muestras: analisisDetallados.value.length
        }
      }
    }
  } catch (err) {
    console.error('Error loading análisis data:', err)
    error.value = 'Error al cargar los análisis del lote'
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
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('es-CO', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleImageError = (event) => {
  event.target.style.display = 'none'
  const parent = event.target.parentElement
  if (parent) {
    parent.innerHTML = '<div class="d-flex align-items-center justify-content-center h-100 text-muted"><i class="fas fa-image fa-3x"></i></div>'
  }
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
  border: 1px solid #e9ecef;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
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

.analysis-card {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.analysis-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}

.object-fit-cover {
  object-fit: cover;
}
</style>
