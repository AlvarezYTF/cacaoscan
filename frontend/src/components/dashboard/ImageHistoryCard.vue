<template>
  <BaseHistoryCard
    title="Historial de Análisis"
    :items="filteredImages"
    :loading="loading"
    :error="error"
    :show-filters="true"
    :show-pagination="true"
    :has-more-pages="hasMorePages"
    item-key="id"
    @load-more="loadMore"
  >
    <template #filters>
      <div class="history-controls">
        <select v-model="selectedFilter" @change="applyFilter" class="filter-select">
          <option value="">Todos los análisis</option>
          <option value="completed">Solo completados</option>
          <option value="pending">Solo pendientes</option>
          <option value="high-quality">Alta calidad (>80%)</option>
          <option value="low-quality">Baja calidad (<60%)</option>
        </select>
        <button @click="refreshData" class="btn btn-secondary" :disabled="loading">
          <span v-if="loading">⟳</span>
          <span v-else>↻</span>
        </button>
      </div>
    </template>

    <template #item="{ item: entry }">
      <div 
        class="image-card"
        @click="viewImageDetails(entry)"
      >
        <div class="image-preview">
          <img 
            v-if="entry.image_url" 
            :src="entry.image_url" 
            :alt="`Lote de cacao #${entry.id}`"
            @error="handleImageError"
          />
          <div v-else class="no-image">
            <span>📷</span>
          </div>
        </div>
        
        <div class="image-info">
          <div class="image-id">#{{ entry.id }}</div>
          <div class="image-meta">
            <span class="finca">{{ entry.finca || 'Sin finca' }}</span>
            <span class="region">{{ entry.region || 'Sin región' }}</span>
          </div>
          
          <div v-if="entry.prediction" class="prediction-data">
            <div class="dimensions">
              <span class="dimension">
                <strong>{{ entry.prediction.alto_mm.toFixed(1) }}</strong>mm alto
              </span>
              <span class="dimension">
                <strong>{{ entry.prediction.ancho_mm.toFixed(1) }}</strong>mm ancho
              </span>
              <span class="dimension">
                <strong>{{ entry.prediction.peso_g.toFixed(1) }}</strong>g peso
              </span>
            </div>
            
            <div class="confidence">
              <div class="confidence-bar">
                <div 
                  class="confidence-fill" 
                  :style="{ width: `${entry.prediction.average_confidence * 100}%` }"
                  :class="getConfidenceClass(entry.prediction.average_confidence)"
                ></div>
              </div>
              <span class="confidence-text">
                {{ Math.round(entry.prediction.average_confidence * 100) }}% confianza
              </span>
            </div>
          </div>
          
          <div v-else class="no-prediction">
            <span class="status pending">Pendiente de análisis</span>
          </div>
          
          <div class="image-date">
            {{ formatDate(entry.created_at) }}
          </div>
        </div>
        
        <div class="image-actions">
          <button 
            @click.stop="downloadImage(entry)" 
            class="btn btn-sm btn-secondary"
            title="Descargar imagen"
          >
            ⬇️
          </button>
          <button 
            @click.stop="viewImageDetails(entry)" 
            class="btn btn-sm btn-primary"
            title="Ver detalles"
          >
            👁️
          </button>
        </div>
      </div>
    </template>

    <template #empty>
      <div class="empty-state">
        <div class="empty-icon">📊</div>
        <h3>No hay análisis disponibles</h3>
        <p>Comienza analizando tus primeros granos de cacao</p>
        <router-link to="/nuevo-analisis" class="btn btn-primary">
          Nuevo Análisis
        </router-link>
      </div>
    </template>

    <template #error>
      <div class="error-message">
        <p>{{ error }}</p>
        <button @click="$emit('retry')" class="btn btn-secondary">Reintentar</button>
      </div>
    </template>
  </BaseHistoryCard>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import BaseHistoryCard from '@/components/common/BaseHistoryCard.vue'
import { getImages, downloadImage as downloadImageApi } from '@/services/predictionApi'
import { handleApiError } from '@/services/apiErrorHandler'

const props = defineProps({
  initialImages: {
    type: Array,
    default: () => []
  },
  autoLoad: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['image-selected', 'refresh-requested', 'retry'])

const router = useRouter()
const images = ref([...props.initialImages])
const loading = ref(false)
const error = ref(null)
const selectedFilter = ref('')
const currentPage = ref(1)
const hasMorePages = ref(true)

// Computed properties
const filteredImages = computed(() => {
  if (!selectedFilter.value) return images.value
  
  return images.value.filter(image => {
    switch (selectedFilter.value) {
      case 'completed':
        return image.processed && image.prediction
      case 'pending':
        return !image.processed || !image.prediction
      case 'high-quality':
        return image.prediction && image.prediction.average_confidence > 0.8
      case 'low-quality':
        return image.prediction && image.prediction.average_confidence < 0.6
      default:
        return true
    }
  })
})

// Methods
const loadImages = async (page = 1, append = false) => {
  if (loading.value) return
  
  loading.value = true
  error.value = null
  
  try {
    const result = await getImages({ page, page_size: 12 })
    
    // getImages devuelve { success: true, data: response } o { success: false, error: ... }
    if (!result.success) {
      error.value = result.error || 'Error al cargar imágenes'
      return
    }
    
    const response = result.data || result
    
    if (append) {
      images.value = [...images.value, ...(response.results || [])]
    } else {
      images.value = response.results || []
    }
    
    hasMorePages.value = response.next !== null
    currentPage.value = page
    
  } catch (err) {
    const errorInfo = handleApiError(err, { logError: true })
    error.value = errorInfo.message
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  await loadImages(1, false)
  emit('refresh-requested')
}

const loadMore = async () => {
  await loadImages(currentPage.value + 1, true)
}

const applyFilter = () => {
  // El filtro se aplica automáticamente por el computed
}

const viewImageDetails = (image) => {
  router.push(`/detalle-analisis/${image.id}`)
  emit('image-selected', image)
}

const downloadImage = async (image) => {
  try {
    const blob = await downloadImageApi(image.id)
    const url = globalThis.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `cacao_${image.id}_${image.file_name || 'image'}.jpg`
    link.click()
    globalThis.URL.revokeObjectURL(url)
  } catch (err) {
    const errorInfo = handleApiError(err, { logError: true })
    alert(errorInfo.message || 'Error al descargar la imagen')
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getConfidenceClass = (confidence) => {
  if (confidence >= 0.8) return 'high'
  if (confidence >= 0.6) return 'medium'
  return 'low'
}

const handleImageError = (event) => {
  event.target.style.display = 'none'
  event.target.nextElementSibling?.classList.add('show')
}

// Lifecycle
onMounted(() => {
  if (props.autoLoad && images.value.length === 0) {
    loadImages()
  }
})

// Watch for prop changes
watch(() => props.initialImages, (newImages) => {
  images.value = [...newImages]
}, { deep: true })
</script>

<style scoped>
.history-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.filter-select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
}

.image-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s ease;
  cursor: pointer;
}

.image-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.image-preview {
  height: 150px;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  font-size: 2rem;
  color: #6c757d;
}

.image-info {
  padding: 1rem;
}

.image-id {
  font-weight: bold;
  color: #28a745;
  margin-bottom: 0.5rem;
}

.image-meta {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  font-size: 0.9rem;
  color: #6c757d;
}

.finca, .region {
  background: #e9ecef;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.prediction-data {
  margin-bottom: 0.75rem;
}

.dimensions {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.dimension {
  font-size: 0.85rem;
  color: #495057;
}

.confidence {
  margin-top: 0.5rem;
}

.confidence-bar {
  width: 100%;
  height: 6px;
  background: #e9ecef;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 0.25rem;
}

.confidence-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.confidence-fill.high {
  background: #28a745;
}

.confidence-fill.medium {
  background: #ffc107;
}

.confidence-fill.low {
  background: #dc3545;
}

.confidence-text {
  font-size: 0.8rem;
  color: #6c757d;
}

.no-prediction {
  text-align: center;
  padding: 0.5rem;
}

.status.pending {
  background: #fff3cd;
  color: #856404;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.image-date {
  font-size: 0.8rem;
  color: #6c757d;
  margin-top: 0.5rem;
}

.image-actions {
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #0d47a1;
  color: #ffffff;
}

.btn-primary:hover {
  background: #002171;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #545b62;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.error-message {
  text-align: center;
  padding: 2rem;
  color: #dc3545;
}

@media (max-width: 768px) {
  .history-controls {
    justify-content: center;
  }
}
</style>
