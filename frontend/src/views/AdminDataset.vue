<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">
              Gestión de Dataset
            </h1>
            <p class="mt-2 text-sm text-gray-600">
              Administre las imágenes del dataset para entrenamiento de modelos ML
            </p>
          </div>
          
          <!-- Quick stats -->
          <div v-if="stats" class="hidden lg:flex items-center space-x-6">
            <div class="text-center">
              <div class="text-2xl font-bold text-blue-600">{{ stats.total_images || 0 }}</div>
              <div class="text-xs text-gray-500">Total imágenes</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-green-600">{{ stats.processed_images || 0 }}</div>
              <div class="text-xs text-gray-500">Procesadas</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-purple-600">{{ formatNumber(avgQualityScore) }}%</div>
              <div class="text-xs text-gray-500">Calidad promedio</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Upload section (collapsible) -->
      <div class="mb-8">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold text-gray-900">
            Subida de Imágenes
          </h2>
          <button
            @click="showUploadSection = !showUploadSection"
            class="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <svg 
              class="w-4 h-4 mr-2 transition-transform duration-200"
              :class="{ 'rotate-180': !showUploadSection }"
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
            {{ showUploadSection ? 'Ocultar' : 'Mostrar' }} subida
          </button>
        </div>
        
        <Transition name="collapse">
          <div v-if="showUploadSection">
            <DatasetUpload
              :max-files="50"
              @upload-start="handleUploadStart"
              @upload-progress="handleUploadProgress"
              @upload-complete="handleUploadComplete"
              @upload-error="handleUploadError"
            />
          </div>
        </Transition>
      </div>

      <!-- Dataset table -->
      <div class="mb-8">
        <DatasetTable
          :auto-refresh="autoRefresh"
          :refresh-interval="30000"
          @item-view="handleItemView"
          @item-edit="handleItemEdit"
          @item-delete="handleItemDelete"
          @bulk-edit="handleBulkEdit"
          @bulk-delete="handleBulkDelete"
          @data-refresh="handleDataRefresh"
          ref="datasetTable"
        />
      </div>

      <!-- Training section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- Model training card -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">
              Entrenamiento de Modelos
            </h3>
            <svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          
          <div class="space-y-3">
            <button
              @click="initiateTraining('regression')"
              :disabled="isTraining || !canTrain"
              class="w-full px-4 py-3 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
            >
              <svg v-if="isTraining && currentTrainingType === 'regression'" class="animate-spin -ml-1 mr-3 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isTraining && currentTrainingType === 'regression' ? 'Entrenando...' : 'Entrenar Modelo de Regresión' }}
            </button>
            
            <button
              @click="initiateTraining('vision')"
              :disabled="isTraining || !canTrain"
              class="w-full px-4 py-3 bg-purple-600 text-white text-sm font-medium rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
            >
              <svg v-if="isTraining && currentTrainingType === 'vision'" class="animate-spin -ml-1 mr-3 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isTraining && currentTrainingType === 'vision' ? 'Entrenando...' : 'Entrenar Modelo de Visión' }}
            </button>
          </div>
          
          <!-- Training progress -->
          <div v-if="trainingJob" class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
            <div class="flex items-center justify-between text-sm text-blue-800 mb-2">
              <span class="font-medium">{{ getTrainingLabel(trainingJob.model_type) }}</span>
              <span>{{ Math.round(trainingJob.progress || 0) }}%</span>
            </div>
            <div class="w-full bg-blue-200 rounded-full h-2">
              <div 
                class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${trainingJob.progress || 0}%` }"
              ></div>
            </div>
            <div class="flex justify-between text-xs text-blue-600 mt-2">
              <span>Época {{ trainingJob.current_epoch || 0 }} / {{ trainingJob.total_epochs || 100 }}</span>
              <span v-if="trainingJob.current_loss">Loss: {{ formatNumber(trainingJob.current_loss, 4) }}</span>
            </div>
          </div>
          
          <div v-if="!canTrain" class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
            <p class="text-sm text-yellow-800">
              Se necesitan al menos 10 imágenes procesadas para entrenar modelos
            </p>
          </div>
        </div>

        <!-- Data validation card -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">
              Validación de Datos
            </h3>
            <svg class="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          
          <div class="space-y-3">
            <button
              @click="validateDataIntegrity"
              :disabled="isValidating"
              class="w-full px-4 py-3 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
            >
              <svg v-if="isValidating" class="animate-spin -ml-1 mr-3 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isValidating ? 'Validando...' : 'Validar Integridad' }}
            </button>
          </div>
          
          <!-- Validation results -->
          <div v-if="validationReport" class="mt-4">
            <div class="p-3 rounded-md" :class="validationReport.has_issues ? 'bg-red-50 border border-red-200' : 'bg-green-50 border border-green-200'">
              <div class="flex items-center mb-2">
                <svg 
                  class="w-5 h-5 mr-2"
                  :class="validationReport.has_issues ? 'text-red-500' : 'text-green-500'"
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path v-if="!validationReport.has_issues" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-sm font-medium" :class="validationReport.has_issues ? 'text-red-800' : 'text-green-800'">
                  {{ validationReport.has_issues ? 'Problemas encontrados' : 'Datos íntegros' }}
                </span>
              </div>
              <div class="text-xs" :class="validationReport.has_issues ? 'text-red-700' : 'text-green-700'">
                <div>Archivos verificados: {{ validationReport.files_checked || 0 }}</div>
                <div v-if="validationReport.has_issues">
                  Problemas: {{ validationReport.issues_count || 0 }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Dataset stats summary -->
      <div v-if="stats" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">
          Resumen del Dataset
        </h3>
        
        <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <div class="text-center p-3 bg-blue-50 rounded-lg">
            <div class="text-2xl font-bold text-blue-600">{{ stats.total_images || 0 }}</div>
            <div class="text-sm text-blue-700">Total</div>
          </div>
          
          <div class="text-center p-3 bg-green-50 rounded-lg">
            <div class="text-2xl font-bold text-green-600">{{ stats.processed_images || 0 }}</div>
            <div class="text-sm text-green-700">Procesadas</div>
          </div>
          
          <div class="text-center p-3 bg-yellow-50 rounded-lg">
            <div class="text-2xl font-bold text-yellow-600">{{ getQualityCount('excellent') }}</div>
            <div class="text-sm text-yellow-700">Excelentes</div>
          </div>
          
          <div class="text-center p-3 bg-purple-50 rounded-lg">
            <div class="text-2xl font-bold text-purple-600">{{ getQualityCount('good') }}</div>
            <div class="text-sm text-purple-700">Buenas</div>
          </div>
          
          <div class="text-center p-3 bg-orange-50 rounded-lg">
            <div class="text-2xl font-bold text-orange-600">{{ formatStorageSize() }}</div>
            <div class="text-sm text-orange-700">Almacenamiento</div>
          </div>
          
          <div class="text-center p-3 bg-indigo-50 rounded-lg">
            <div class="text-2xl font-bold text-indigo-600">{{ formatNumber(avgDimensionVolume()) }}</div>
            <div class="text-sm text-indigo-700">Vol. prom. (mm³)</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals and overlays -->
    <!-- Success notification -->
    <Transition name="slide-up">
      <div 
        v-if="showSuccessMessage" 
        class="fixed bottom-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50"
      >
        <div class="flex items-center">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          {{ successMessage }}
        </div>
      </div>
    </Transition>

    <!-- Error notification -->
    <Transition name="slide-up">
      <div 
        v-if="showErrorMessage" 
        class="fixed bottom-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50"
      >
        <div class="flex items-center">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ errorMessage }}
        </div>
      </div>
    </Transition>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue';
import DatasetUpload from '@/components/admin/DatasetUpload.vue';
import DatasetTable from '@/components/admin/DatasetTable.vue';
import { 
  getDatasetStats, 
  validateDataIntegrity,
  trainRegressionModel,
  trainVisionModel,
  getTrainingJobStatus,
  formatNumber 
} from '@/services/datasetApi.js';

export default {
  name: 'AdminDataset',
  components: {
    DatasetUpload,
    DatasetTable
  },
  
  setup() {
    // Estado principal (SRP - separado por responsabilidad)
    const showUploadSection = ref(true);
    const autoRefresh = ref(true);
    const stats = ref(null);
    const datasetTable = ref(null);
    
    // Estado de entrenamiento
    const isTraining = ref(false);
    const currentTrainingType = ref(null);
    const trainingJob = ref(null);
    const trainingTimer = ref(null);
    
    // Estado de validación
    const isValidating = ref(false);
    const validationReport = ref(null);
    
    // Notificaciones
    const showSuccessMessage = ref(false);
    const showErrorMessage = ref(false);
    const successMessage = ref('');
    const errorMessage = ref('');
    
    // Computed properties (DRY - cálculos reutilizables)
    const canTrain = computed(() => {
      return stats.value && stats.value.processed_images >= 10;
    });
    
    const avgQualityScore = computed(() => {
      if (!stats.value || !stats.value.quality_distribution) return 0;
      
      const qualityWeights = { excellent: 100, good: 80, fair: 60, poor: 40 };
      let totalWeightedScore = 0;
      let totalImages = 0;
      
      Object.entries(stats.value.quality_distribution).forEach(([quality, count]) => {
        const weight = qualityWeights[quality] || 50;
        totalWeightedScore += weight * count;
        totalImages += count;
      });
      
      return totalImages > 0 ? Math.round(totalWeightedScore / totalImages) : 0;
    });
    
    // Métodos de gestión de datos (SRP - solo datos)
    const loadStats = async () => {
      try {
        stats.value = await getDatasetStats();
      } catch (error) {
        console.error('Error cargando estadísticas:', error);
        stats.value = null;
      }
    };
    
    const refreshData = () => {
      loadStats();
      if (datasetTable.value) {
        datasetTable.value.refreshData();
      }
    };
    
    // Métodos de upload (SRP - solo upload)
    const handleUploadStart = (data) => {
      showSuccess(`Iniciando subida de ${data.fileCount} archivo(s)`);
    };
    
    const handleUploadProgress = (progress) => {
      // Progreso en tiempo real - podrías mostrar una barra global aquí
    };
    
    const handleUploadComplete = (result) => {
      const { successful, failed, total } = result;
      
      if (failed === 0) {
        showSuccess(`¡${successful} archivo(s) subido(s) exitosamente!`);
      } else {
        showError(`${successful} exitosos, ${failed} fallidos de ${total} archivo(s)`);
      }
      
      // Refrescar datos después de subida exitosa
      if (successful > 0) {
        setTimeout(refreshData, 1000);
      }
    };
    
    const handleUploadError = (error) => {
      showError(`Error en la subida: ${error.message}`);
    };
    
    // Métodos de tabla (SRP - solo eventos de tabla)
    const handleItemView = (item) => {
      // Aquí podrías abrir un modal de detalles
      showSuccess(`Viendo detalles de imagen #${item.id}`);
    };
    
    const handleItemEdit = (item) => {
      // Aquí podrías abrir un modal de edición
      showSuccess(`Editando imagen #${item.id}`);
    };
    
    const handleItemDelete = (item) => {
      // Aquí podrías mostrar confirmación de eliminación
      if (confirm(`¿Eliminar imagen #${item.id}?`)) {
        showSuccess(`Imagen #${item.id} eliminada`);
        refreshData();
      }
    };
    
    const handleBulkEdit = (selectedIds) => {
      showSuccess(`Editando ${selectedIds.length} imagen(es)`);
    };
    
    const handleBulkDelete = (selectedIds) => {
      if (confirm(`¿Eliminar ${selectedIds.length} imagen(es) seleccionada(s)?`)) {
        showSuccess(`${selectedIds.length} imagen(es) eliminada(s)`);
        refreshData();
      }
    };
    
    const handleDataRefresh = (info) => {
      // Actualizar stats cuando la tabla se refresque
      loadStats();
    };
    
    // Métodos de entrenamiento (SRP - solo entrenamiento)
    const initiateTraining = async (modelType) => {
      if (!canTrain.value) {
        showError('No hay suficientes datos para entrenar');
        return;
      }
      
      isTraining.value = true;
      currentTrainingType.value = modelType;
      
      try {
        const trainingParams = {
          epochs: 50,
          learning_rate: 0.001,
          batch_size: 32,
          validation_split: 0.2,
          min_quality_score: 0.7
        };
        
        let result;
        if (modelType === 'regression') {
          result = await trainRegressionModel(trainingParams);
        } else {
          result = await trainVisionModel(trainingParams);
        }
        
        trainingJob.value = result;
        
        // Iniciar polling del estado
        startTrainingStatusPolling(result.job_id);
        
        showSuccess(`Entrenamiento de ${getTrainingLabel(modelType)} iniciado`);
        
      } catch (error) {
        console.error('Error iniciando entrenamiento:', error);
        showError(`Error iniciando entrenamiento: ${error.message}`);
        isTraining.value = false;
        currentTrainingType.value = null;
      }
    };
    
    const startTrainingStatusPolling = (jobId) => {
      trainingTimer.value = setInterval(async () => {
        try {
          const status = await getTrainingJobStatus(jobId);
          trainingJob.value = { ...trainingJob.value, ...status };
          
          if (status.status === 'completed' || status.status === 'failed') {
            stopTrainingStatusPolling();
            isTraining.value = false;
            currentTrainingType.value = null;
            
            if (status.status === 'completed') {
              showSuccess(`Entrenamiento completado exitosamente`);
            } else {
              showError(`Entrenamiento falló: ${status.error || 'Error desconocido'}`);
            }
          }
        } catch (error) {
          console.error('Error obteniendo estado de entrenamiento:', error);
        }
      }, 2000);
    };
    
    const stopTrainingStatusPolling = () => {
      if (trainingTimer.value) {
        clearInterval(trainingTimer.value);
        trainingTimer.value = null;
      }
    };
    
    // Métodos de validación (SRP - solo validación)
    const validateDataIntegrity = async () => {
      isValidating.value = true;
      
      try {
        const report = await validateDataIntegrity();
        validationReport.value = report;
        
        if (report.has_issues) {
          showError(`Validación completada: ${report.issues_count} problema(s) encontrado(s)`);
        } else {
          showSuccess('Validación completada: Todos los datos están íntegros');
        }
        
      } catch (error) {
        console.error('Error en validación:', error);
        showError(`Error en validación: ${error.message}`);
      } finally {
        isValidating.value = false;
      }
    };
    
    // Utilidades (DRY - funciones reutilizables)
    const getQualityCount = (quality) => {
      return stats.value?.quality_distribution?.[quality] || 0;
    };
    
    const getTrainingLabel = (type) => {
      const labels = {
        regression: 'Modelo de Regresión',
        vision: 'Modelo de Visión'
      };
      return labels[type] || type;
    };
    
    const formatStorageSize = () => {
      const bytes = stats.value?.storage_usage?.total_size || 0;
      if (bytes === 0) return '0 MB';
      
      const k = 1024;
      const sizes = ['B', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    };
    
    const avgDimensionVolume = () => {
      const dims = stats.value?.dimension_statistics;
      if (!dims) return 0;
      
      const avgWidth = dims.avg_width || 0;
      const avgHeight = dims.avg_height || 0;
      const avgThickness = dims.avg_thickness || 0;
      
      return avgWidth * avgHeight * avgThickness;
    };
    
    // Métodos de notificaciones (KISS - simple y directo)
    const showSuccess = (message) => {
      successMessage.value = message;
      showSuccessMessage.value = true;
      setTimeout(() => {
        showSuccessMessage.value = false;
      }, 3000);
    };
    
    const showError = (message) => {
      errorMessage.value = message;
      showErrorMessage.value = true;
      setTimeout(() => {
        showErrorMessage.value = false;
      }, 5000);
    };
    
    // Lifecycle
    onMounted(() => {
      loadStats();
    });
    
    onUnmounted(() => {
      stopTrainingStatusPolling();
    });
    
    return {
      // Estado
      showUploadSection,
      autoRefresh,
      stats,
      datasetTable,
      isTraining,
      currentTrainingType,
      trainingJob,
      isValidating,
      validationReport,
      showSuccessMessage,
      showErrorMessage,
      successMessage,
      errorMessage,
      
      // Computed
      canTrain,
      avgQualityScore,
      
      // Métodos
      loadStats,
      refreshData,
      handleUploadStart,
      handleUploadProgress,
      handleUploadComplete,
      handleUploadError,
      handleItemView,
      handleItemEdit,
      handleItemDelete,
      handleBulkEdit,
      handleBulkDelete,
      handleDataRefresh,
      initiateTraining,
      validateDataIntegrity,
      
      // Utilidades
      getQualityCount,
      getTrainingLabel,
      formatStorageSize,
      avgDimensionVolume,
      formatNumber
    };
  }
};
</script>

<style scoped>
/* Transiciones */
.collapse-enter-active,
.collapse-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.collapse-enter-from,
.collapse-leave-to {
  max-height: 0;
  opacity: 0;
}

.collapse-enter-to,
.collapse-leave-from {
  max-height: 1000px;
  opacity: 1;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* Efectos hover */
.hover-scale:hover {
  transform: scale(1.02);
  transition: transform 0.2s ease;
}

/* Grid responsivo */
@media (max-width: 1024px) {
  .lg\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .lg\:grid-cols-6 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .md\:grid-cols-4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}

/* Estados de carga */
.loading {
  opacity: 0.6;
  pointer-events: none;
}

/* Focus states */
.focus-visible:focus {
  outline: 2px solid #10b981;
  outline-offset: 2px;
}

/* Animaciones de progreso */
.progress-bar {
  transition: width 0.3s ease;
}

/* Mejoras de accesibilidad */
button:disabled {
  cursor: not-allowed;
}

/* Scrollbar personalizado para modales */
.modal-content::-webkit-scrollbar {
  width: 6px;
}

.modal-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.modal-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}
</style>
