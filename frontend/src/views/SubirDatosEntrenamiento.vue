<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header Section -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">
              Entrenamiento Incremental
            </h1>
            <p class="mt-2 text-sm text-gray-600">
              Sube nuevas imágenes con datos reales para mejorar el modelo YOLOv8
            </p>
          </div>
          
          <!-- Stats Summary -->
          <div v-if="trainingStats.totalSamples > 0" class="hidden lg:flex items-center space-x-6">
            <div class="text-center">
              <div class="text-2xl font-bold text-blue-600">{{ trainingStats.totalSamples }}</div>
              <div class="text-xs text-gray-500">Muestras totales</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-green-600">{{ trainingStats.incrementalUpdates }}</div>
              <div class="text-xs text-gray-500">Actualizaciones</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-purple-600">{{ trainingStats.lastAccuracy }}%</div>
              <div class="text-xs text-gray-500">Precisión actual</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        <!-- Left Column: Upload Form -->
        <div class="space-y-6">
          <!-- Upload Form -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200">
            <div class="p-6">
              <div class="flex items-center justify-between mb-6">
                <h2 class="text-xl font-semibold text-gray-900">
                  Subir Nueva Muestra
                </h2>
                <div v-if="isTraining" class="flex items-center text-sm text-blue-600">
                  <svg class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Entrenando modelo...
                </div>
              </div>
              
              <form @submit.prevent="handleSubmit" class="space-y-6">
                <!-- Image Upload -->
                <div class="space-y-4">
                  <label class="block text-sm font-medium text-gray-700">
                    Imagen del Grano
                    <span class="text-red-500">*</span>
                  </label>
                  
                  <div 
                    @dragover.prevent="handleDragOver"
                    @dragleave.prevent="handleDragLeave"
                    @drop.prevent="handleDrop"
                    @click="openFileSelector"
                    class="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200"
                    :class="{
                      'border-green-500 bg-green-50': isDragging,
                      'border-gray-300 hover:border-green-400 hover:bg-gray-50': !isDragging && !selectedFile,
                      'border-green-500 bg-green-50': selectedFile
                    }"
                  >
                    <!-- Upload State -->
                    <div v-if="!selectedFile" class="flex flex-col items-center justify-center space-y-3">
                      <div class="relative">
                        <svg 
                          class="w-16 h-16 text-gray-400 transition-colors duration-200"
                          :class="{ 'text-green-500': isDragging }"
                          fill="none" 
                          stroke="currentColor" 
                          viewBox="0 0 24 24"
                        >
                          <path 
                            stroke-linecap="round" 
                            stroke-linejoin="round" 
                            stroke-width="1.5" 
                            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                          />
                        </svg>
                      </div>
                      <div class="text-sm text-gray-600">
                        <span class="font-medium text-green-600">Haz clic para subir</span> o arrastra y suelta
                      </div>
                      <div class="text-xs text-gray-500">
                        PNG, JPG, BMP hasta 20MB
                      </div>
                    </div>
                    
                    <!-- Selected File State -->
                    <div v-else class="flex flex-col items-center justify-center space-y-3">
                      <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                        <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                        </svg>
                      </div>
                      <div class="text-sm font-medium text-gray-900">{{ selectedFile.name }}</div>
                      <div class="text-xs text-gray-500">{{ formatFileSize(selectedFile.size) }}</div>
                      <button 
                        type="button"
                        @click.stop="removeFile"
                        class="text-xs text-red-600 hover:text-red-700 underline"
                      >
                        Eliminar
                      </button>
                    </div>
                  </div>
                  
                  <input 
                    ref="fileInput"
                    type="file"
                    accept="image/*"
                    @change="handleFileSelect"
                    class="hidden"
                  />
                </div>

                <!-- Grain Data Form -->
                <div class="space-y-4">
                  <h3 class="text-lg font-medium text-gray-900">Datos del Grano</h3>
                  
                  <div class="grid grid-cols-2 gap-4">
                    <!-- ID -->
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        ID de la Muestra
                        <span class="text-red-500">*</span>
                      </label>
                      <input 
                        v-model="grainData.id"
                        type="number"
                        min="1"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="511"
                        required
                      />
                    </div>
                    
                    <!-- Peso -->
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Peso (g)
                        <span class="text-red-500">*</span>
                      </label>
                      <input 
                        v-model="grainData.peso"
                        type="number"
                        step="0.01"
                        min="0.1"
                        max="5.0"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="1.95"
                        required
                      />
                    </div>
                    
                    <!-- Alto -->
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Alto (mm)
                        <span class="text-red-500">*</span>
                      </label>
                      <input 
                        v-model="grainData.alto"
                        type="number"
                        step="0.1"
                        min="5"
                        max="50"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="22.5"
                        required
                      />
                    </div>
                    
                    <!-- Ancho -->
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Ancho (mm)
                        <span class="text-red-500">*</span>
                      </label>
                      <input 
                        v-model="grainData.ancho"
                        type="number"
                        step="0.1"
                        min="3"
                        max="30"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="14.8"
                        required
                      />
                    </div>
                    
                    <!-- Grosor -->
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Grosor (mm)
                        <span class="text-red-500">*</span>
                      </label>
                      <input 
                        v-model="grainData.grosor"
                        type="number"
                        step="0.1"
                        min="2"
                        max="20"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="7.2"
                        required
                      />
                    </div>
                  </div>
                </div>

                <!-- Additional Info -->
                <div class="space-y-4">
                  <h3 class="text-lg font-medium text-gray-900">Información Adicional</h3>
                  
                  <div class="grid grid-cols-1 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Número de Lote
                      </label>
                      <input 
                        v-model="additionalInfo.batch_number"
                        type="text"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="LOTE_INC_001"
                      />
                    </div>
                    
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Origen
                      </label>
                      <input 
                        v-model="additionalInfo.origin"
                        type="text"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Colombia"
                      />
                    </div>
                    
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Notas
                      </label>
                      <textarea 
                        v-model="additionalInfo.notes"
                        rows="3"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Notas adicionales sobre la muestra..."
                      ></textarea>
                    </div>
                  </div>
                </div>

                <!-- Submit Button -->
                <div class="flex justify-end">
                  <button 
                    type="submit"
                    :disabled="!isFormValid || isTraining"
                    class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span v-if="isTraining">Entrenando...</span>
                    <span v-else>Entrenar Modelo</span>
                  </button>
                </div>
              </form>
            </div>
          </div>

          <!-- Error Display -->
          <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-red-400 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="flex-1">
                <h3 class="text-sm font-medium text-red-800">Error en el entrenamiento</h3>
                <p class="text-sm text-red-700 mt-1">{{ error }}</p>
                <button
                  @click="clearError"
                  class="text-sm text-red-600 hover:text-red-500 underline mt-2 focus:outline-none"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>

          <!-- Success Display -->
          <div v-if="lastTrainingResult" class="bg-green-50 border border-green-200 rounded-lg p-4">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-green-400 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <div class="flex-1">
                <h3 class="text-sm font-medium text-green-800">Entrenamiento exitoso</h3>
                <p class="text-sm text-green-700 mt-1">{{ lastTrainingResult.message }}</p>
                <div class="mt-2 text-xs text-green-600">
                  <div>Tiempo: {{ lastTrainingResult.training_stats?.training_time?.toFixed(2) }}s</div>
                  <div>Mejora precisión: {{ (lastTrainingResult.training_stats?.accuracy_improvement * 100)?.toFixed(1) }}%</div>
                  <div>Reducción pérdida: {{ (lastTrainingResult.training_stats?.loss_reduction * 100)?.toFixed(1) }}%</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Training History & Stats -->
        <div class="space-y-6">
          <!-- Training Progress -->
          <div v-if="isTraining" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Progreso del Entrenamiento</h3>
            
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">Preparando datos...</span>
                <div class="w-4 h-4 bg-blue-500 rounded-full animate-pulse"></div>
              </div>
              
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-blue-600 h-2 rounded-full transition-all duration-300" :style="{ width: trainingProgress + '%' }"></div>
              </div>
              
              <div class="text-xs text-gray-500 text-center">
                {{ trainingProgress }}% completado
              </div>
            </div>
          </div>

          <!-- Training Stats -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Estadísticas del Modelo</h3>
            
            <div class="grid grid-cols-2 gap-4">
              <div class="text-center p-3 bg-blue-50 rounded-lg">
                <div class="text-2xl font-bold text-blue-600">{{ trainingStats.totalSamples }}</div>
                <div class="text-sm text-blue-700">Muestras totales</div>
              </div>
              <div class="text-center p-3 bg-green-50 rounded-lg">
                <div class="text-2xl font-bold text-green-600">{{ trainingStats.incrementalUpdates }}</div>
                <div class="text-sm text-green-700">Actualizaciones</div>
              </div>
              <div class="text-center p-3 bg-purple-50 rounded-lg">
                <div class="text-2xl font-bold text-purple-600">{{ trainingStats.lastAccuracy }}%</div>
                <div class="text-sm text-purple-700">Precisión actual</div>
              </div>
              <div class="text-center p-3 bg-orange-50 rounded-lg">
                <div class="text-2xl font-bold text-orange-600">{{ trainingStats.lastTrainingTime }}s</div>
                <div class="text-sm text-orange-700">Último entrenamiento</div>
              </div>
            </div>
          </div>

          <!-- Recent Training History -->
          <div v-if="trainingHistory.length > 0" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Historial Reciente</h3>
            
            <div class="space-y-3">
              <div
                v-for="(training, index) in trainingHistory.slice(0, 5)"
                :key="index"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div class="flex items-center space-x-3">
                  <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <span class="text-sm font-medium text-green-600">#{{ training.sample_id }}</span>
                  </div>
                  <div>
                    <div class="text-sm font-medium text-gray-900">
                      Muestra {{ training.sample_id }}
                    </div>
                    <div class="text-xs text-gray-500">
                      {{ formatRelativeTime(training.timestamp) }}
                    </div>
                  </div>
                </div>
                <div class="text-sm text-gray-600">
                  +{{ (training.accuracy_improvement * 100).toFixed(1) }}%
                </div>
              </div>
            </div>
            
          </div>

          <!-- Tips -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-blue-400 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 class="text-sm font-medium text-blue-800">Consejos para mejores resultados</h3>
                <ul class="text-sm text-blue-700 mt-2 space-y-1">
                  <li>• Usa imágenes claras y bien iluminadas</li>
                  <li>• Asegúrate de que el grano esté completo en la imagen</li>
                  <li>• Mide las dimensiones con precisión</li>
                  <li>• Usa IDs únicos para cada muestra</li>
                  <li>• El entrenamiento incremental toma 30-60 segundos</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'SubirDatosEntrenamiento',
  setup() {
    const router = useRouter()
    
    // Estado reactivo
    const selectedFile = ref(null)
    const isDragging = ref(false)
    const isTraining = ref(false)
    const trainingProgress = ref(0)
    const error = ref('')
    const lastTrainingResult = ref(null)
    
    // Datos del grano
    const grainData = ref({
      id: '',
      peso: '',
      alto: '',
      ancho: '',
      grosor: ''
    })
    
    // Información adicional
    const additionalInfo = ref({
      batch_number: '',
      origin: '',
      notes: ''
    })
    
    // Estadísticas de entrenamiento
    const trainingStats = ref({
      totalSamples: 510,
      incrementalUpdates: 0,
      lastAccuracy: 85.2,
      lastTrainingTime: 0
    })
    
    // Historial de entrenamiento
    const trainingHistory = ref([])
    
    // Referencias
    const fileInput = ref(null)
    
    // Computed properties
    const isFormValid = computed(() => {
      return selectedFile.value && 
             grainData.value.id && 
             grainData.value.peso && 
             grainData.value.alto && 
             grainData.value.ancho && 
             grainData.value.grosor
    })
    
    // Métodos
    const openFileSelector = () => {
      fileInput.value?.click()
    }
    
    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (file) {
        selectedFile.value = file
        clearError()
      }
    }
    
    const handleDragOver = (event) => {
      event.preventDefault()
      isDragging.value = true
    }
    
    const handleDragLeave = (event) => {
      event.preventDefault()
      isDragging.value = false
    }
    
    const handleDrop = (event) => {
      event.preventDefault()
      isDragging.value = false
      
      const files = event.dataTransfer.files
      if (files.length > 0) {
        selectedFile.value = files[0]
        clearError()
      }
    }
    
    const removeFile = () => {
      selectedFile.value = null
      if (fileInput.value) {
        fileInput.value.value = ''
      }
    }
    
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }
    
    const formatRelativeTime = (timestamp) => {
      const now = new Date()
      const time = new Date(timestamp)
      const diff = now - time
      
      if (diff < 60000) return 'Hace un momento'
      if (diff < 3600000) return `Hace ${Math.floor(diff / 60000)} min`
      if (diff < 86400000) return `Hace ${Math.floor(diff / 3600000)} h`
      return `Hace ${Math.floor(diff / 86400000)} días`
    }
    
    const clearError = () => {
      error.value = ''
    }
    
    const handleSubmit = async () => {
      if (!isFormValid.value) return
      
      try {
        isTraining.value = true
        trainingProgress.value = 0
        error.value = ''
        lastTrainingResult.value = null
        
        // Simular progreso
        const progressInterval = setInterval(() => {
          if (trainingProgress.value < 90) {
            trainingProgress.value += Math.random() * 10
          }
        }, 500)
        
        // Preparar FormData
        const formData = new FormData()
        formData.append('image', selectedFile.value)
        formData.append('data', JSON.stringify(grainData.value))
        
        if (additionalInfo.value.batch_number) {
          formData.append('batch_number', additionalInfo.value.batch_number)
        }
        if (additionalInfo.value.origin) {
          formData.append('origin', additionalInfo.value.origin)
        }
        if (additionalInfo.value.notes) {
          formData.append('notes', additionalInfo.value.notes)
        }
        
        // Realizar solicitud
        const response = await fetch('/api/ml/train/incremental-weight/', {
          method: 'POST',
          body: formData,
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        })
        
        const result = await response.json()
        
        clearInterval(progressInterval)
        trainingProgress.value = 100
        
        if (response.ok && result.success) {
          lastTrainingResult.value = result
          
          // Actualizar estadísticas
          trainingStats.value.totalSamples = result.dataset_info.current_size
          trainingStats.value.incrementalUpdates += 1
          trainingStats.value.lastAccuracy = (result.training_stats.accuracy_improvement * 100).toFixed(1)
          trainingStats.value.lastTrainingTime = result.training_stats.training_time.toFixed(1)
          
          // Agregar al historial
          trainingHistory.value.unshift({
            sample_id: grainData.value.id,
            timestamp: new Date().toISOString(),
            accuracy_improvement: result.training_stats.accuracy_improvement,
            training_time: result.training_stats.training_time
          })
          
          // Limpiar formulario
          resetForm()
          
        } else {
          error.value = result.error || 'Error desconocido en el entrenamiento'
        }
        
      } catch (err) {
        error.value = err.message || 'Error de conexión'
      } finally {
        isTraining.value = false
        setTimeout(() => {
          trainingProgress.value = 0
        }, 1000)
      }
    }
    
    const resetForm = () => {
      selectedFile.value = null
      grainData.value = {
        id: '',
        peso: '',
        alto: '',
        ancho: '',
        grosor: ''
      }
      additionalInfo.value = {
        batch_number: '',
        origin: '',
        notes: ''
      }
      if (fileInput.value) {
        fileInput.value.value = ''
      }
    }
    
    // Lifecycle
    onMounted(() => {
      // Cargar estadísticas iniciales
      // En una implementación real, esto vendría de una API
    })
    
    return {
      // Estado
      selectedFile,
      isDragging,
      isTraining,
      trainingProgress,
      error,
      lastTrainingResult,
      grainData,
      additionalInfo,
      trainingStats,
      trainingHistory,
      
      // Referencias
      fileInput,
      
      // Computed
      isFormValid,
      
      // Métodos
      openFileSelector,
      handleFileSelect,
      handleDragOver,
      handleDragLeave,
      handleDrop,
      removeFile,
      formatFileSize,
      formatRelativeTime,
      clearError,
      handleSubmit,
      resetForm
    }
  }
}
</script>

<style scoped>
/* Animaciones suaves */
.transition-all {
  transition: all 0.2s ease-in-out;
}

/* Hover effects */
.hover\:border-green-400:hover {
  border-color: #4ade80;
}

.hover\:bg-gray-50:hover {
  background-color: #f9fafb;
}

.hover\:bg-blue-700:hover {
  background-color: #1d4ed8;
}

/* Focus states */
.focus\:outline-none:focus {
  outline: none;
}

.focus\:ring-2:focus {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}

.focus\:ring-blue-500:focus {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}

/* Disabled states */
.disabled\:opacity-50:disabled {
  opacity: 0.5;
}

.disabled\:cursor-not-allowed:disabled {
  cursor: not-allowed;
}

/* Animaciones de carga */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
