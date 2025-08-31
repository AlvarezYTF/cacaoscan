<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">
              Panel de Reentrenamiento
            </h1>
            <p class="mt-2 text-sm text-gray-600">
              Configure, ejecute y monitoree entrenamientos de modelos ML con configuraciones avanzadas
            </p>
          </div>
          
          <!-- Quick actions -->
          <div class="hidden lg:flex items-center space-x-3">
            <div v-if="activeTrainings.length > 0" class="text-center">
              <div class="text-2xl font-bold text-blue-600">{{ activeTrainings.length }}</div>
              <div class="text-xs text-gray-500">Activos</div>
            </div>
            
            <div class="text-center">
              <div class="text-2xl font-bold text-green-600">{{ completedToday }}</div>
              <div class="text-xs text-gray-500">Hoy</div>
            </div>
            
            <button
              @click="refreshAll"
              :disabled="isRefreshing"
              class="px-3 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
            >
              <svg class="w-4 h-4 inline mr-1" :class="{ 'animate-spin': isRefreshing }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Actualizar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Training Interface -->
      <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <!-- Left Column: Training Configuration -->
        <div class="xl:col-span-2 space-y-6">
          <!-- Model Training Component -->
          <ModelTraining
            :available-dataset-size="datasetSize"
            :auto-refresh-interval="2000"
            @training-started="handleTrainingStarted"
            @training-completed="handleTrainingCompleted"
            @training-failed="handleTrainingFailed"
            @training-cancelled="handleTrainingCancelled"
          />
          
          <!-- Training History -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200">
            <div class="px-6 py-4 border-b border-gray-200">
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold text-gray-900">
                  Historial de Entrenamientos
                </h3>
                <div class="flex items-center space-x-3">
                  <!-- History filters -->
                  <select 
                    v-model="historyFilters.model_type"
                    @change="loadTrainingHistory"
                    class="text-sm border border-gray-300 rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Todos los modelos</option>
                    <option value="regression">Regresión</option>
                    <option value="vision">Visión</option>
                  </select>
                  
                  <select 
                    v-model="historyFilters.status"
                    @change="loadTrainingHistory"
                    class="text-sm border border-gray-300 rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Todos los estados</option>
                    <option value="running">En ejecución</option>
                    <option value="completed">Completados</option>
                    <option value="failed">Fallidos</option>
                    <option value="cancelled">Cancelados</option>
                  </select>
                  
                  <button
                    @click="showHistoryDetails = !showHistoryDetails"
                    class="text-sm text-blue-600 hover:text-blue-500 underline"
                  >
                    {{ showHistoryDetails ? 'Ocultar' : 'Mostrar' }} detalles
                  </button>
                </div>
              </div>
            </div>
            
            <div class="p-6">
              <!-- Loading state -->
              <div v-if="isLoadingHistory" class="text-center py-8">
                <svg class="animate-spin h-8 w-8 text-gray-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <p class="text-sm text-gray-500">Cargando historial...</p>
              </div>
              
              <!-- No data state -->
              <div v-else-if="trainingHistory.length === 0" class="text-center py-8">
                <svg class="w-12 h-12 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 00-2-2z" />
                </svg>
                <p class="text-sm font-medium text-gray-500">No hay entrenamientos en el historial</p>
                <p class="text-xs text-gray-400">Inicia tu primer entrenamiento para ver el historial</p>
              </div>
              
              <!-- History table -->
              <div v-else class="space-y-3">
                <div
                  v-for="job in trainingHistory"
                  :key="job.job_id"
                  class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                  :class="{
                    'border-blue-300 bg-blue-50': job.status === 'running',
                    'border-green-300 bg-green-50': job.status === 'completed',
                    'border-red-300 bg-red-50': job.status === 'failed',
                    'border-gray-400 bg-gray-50': job.status === 'cancelled'
                  }"
                >
                  <div class="flex items-start justify-between">
                    <div class="flex-1">
                      <!-- Job header -->
                      <div class="flex items-center space-x-3 mb-2">
                        <span 
                          class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                          :class="getStatusBadgeClass(job.status)"
                        >
                          {{ getStatusLabel(job.status) }}
                        </span>
                        
                        <span class="text-sm font-medium text-gray-900">
                          {{ getModelTypeLabel(job.model_type) }}
                        </span>
                        
                        <span class="text-xs text-gray-500">
                          #{{ job.job_id.substring(0, 8) }}
                        </span>
                        
                        <span class="text-xs text-gray-500">
                          {{ formatRelativeTime(job.created_at) }}
                        </span>
                      </div>
                      
                      <!-- Experiment info -->
                      <div v-if="job.experiment_name" class="mb-2">
                        <p class="text-sm text-gray-700 font-medium">{{ job.experiment_name }}</p>
                        <p v-if="job.experiment_description" class="text-xs text-gray-500">
                          {{ job.experiment_description.substring(0, 100) }}{{ job.experiment_description.length > 100 ? '...' : '' }}
                        </p>
                      </div>
                      
                      <!-- Progress bar for running jobs -->
                      <div v-if="job.status === 'running'" class="mb-2">
                        <div class="flex justify-between text-xs text-gray-600 mb-1">
                          <span>Progreso</span>
                          <span>{{ Math.round(job.progress || 0) }}%</span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                            :style="{ width: `${job.progress || 0}%` }"
                          ></div>
                        </div>
                      </div>
                      
                      <!-- Details (expandable) -->
                      <div v-if="showHistoryDetails" class="mt-3 pt-3 border-t border-gray-200">
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                          <div v-if="job.current_epoch || job.total_epochs">
                            <span class="text-gray-500">Épocas:</span>
                            <span class="ml-1 text-gray-700">{{ job.current_epoch || 0 }} / {{ job.total_epochs || 0 }}</span>
                          </div>
                          
                          <div v-if="job.current_loss">
                            <span class="text-gray-500">Loss:</span>
                            <span class="ml-1 text-gray-700">{{ formatNumber(job.current_loss) }}</span>
                          </div>
                          
                          <div v-if="job.validation_accuracy">
                            <span class="text-gray-500">Val. Acc:</span>
                            <span class="ml-1 text-gray-700">{{ Math.round(job.validation_accuracy * 100) }}%</span>
                          </div>
                          
                          <div v-if="job.elapsed_time">
                            <span class="text-gray-500">Tiempo:</span>
                            <span class="ml-1 text-gray-700">{{ formatElapsedTime(job.elapsed_time) }}</span>
                          </div>
                        </div>
                        
                        <!-- Tags -->
                        <div v-if="job.experiment_tags && job.experiment_tags.length > 0" class="mt-2">
                          <span 
                            v-for="tag in job.experiment_tags" 
                            :key="tag"
                            class="inline-block bg-gray-100 text-gray-700 px-2 py-1 text-xs rounded mr-1 mb-1"
                          >
                            {{ tag }}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Actions -->
                    <div class="flex items-center space-x-2 ml-4">
                      <button
                        v-if="job.status === 'running'"
                        @click="cancelJob(job.job_id)"
                        class="text-xs text-red-600 hover:text-red-700 underline"
                      >
                        Cancelar
                      </button>
                      
                      <button
                        v-if="job.status === 'completed'"
                        @click="viewMetrics(job)"
                        class="text-xs text-blue-600 hover:text-blue-700 underline"
                      >
                        Ver métricas
                      </button>
                      
                      <button
                        @click="viewJobDetails(job)"
                        class="text-xs text-gray-600 hover:text-gray-700 underline"
                      >
                        Detalles
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Active Trainings & Quick Stats -->
        <div class="space-y-6">
          <!-- Active Trainings Monitor -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-lg font-semibold text-gray-900">
                Entrenamientos Activos
              </h3>
            </div>
            
            <div class="p-6">
              <div v-if="activeTrainings.length === 0" class="text-center py-6">
                <svg class="w-8 h-8 text-gray-300 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p class="text-sm text-gray-500">No hay entrenamientos activos</p>
              </div>
              
              <div v-else class="space-y-3">
                <div
                  v-for="training in activeTrainings"
                  :key="training.job_id"
                  class="border border-blue-200 rounded-lg p-3 bg-blue-50"
                >
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-sm font-medium text-blue-900">
                      {{ getModelTypeLabel(training.model_type) }}
                    </span>
                    <span class="text-xs text-blue-600">
                      {{ Math.round(training.progress || 0) }}%
                    </span>
                  </div>
                  
                  <div class="w-full bg-blue-200 rounded-full h-2 mb-2">
                    <div 
                      class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      :style="{ width: `${training.progress || 0}%` }"
                    ></div>
                  </div>
                  
                  <div class="flex justify-between text-xs text-blue-700">
                    <span>{{ training.current_epoch || 0 }} / {{ training.total_epochs || 0 }}</span>
                    <span v-if="training.elapsed_time">{{ formatElapsedTime(training.elapsed_time) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Statistics -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-lg font-semibold text-gray-900">
                Estadísticas Rápidas
              </h3>
            </div>
            
            <div class="p-6">
              <div class="grid grid-cols-2 gap-4">
                <div class="text-center p-3 bg-green-50 rounded-lg">
                  <div class="text-2xl font-bold text-green-600">{{ stats.completed || 0 }}</div>
                  <div class="text-sm text-green-700">Completados</div>
                </div>
                
                <div class="text-center p-3 bg-blue-50 rounded-lg">
                  <div class="text-2xl font-bold text-blue-600">{{ stats.running || 0 }}</div>
                  <div class="text-sm text-blue-700">En ejecución</div>
                </div>
                
                <div class="text-center p-3 bg-red-50 rounded-lg">
                  <div class="text-2xl font-bold text-red-600">{{ stats.failed || 0 }}</div>
                  <div class="text-sm text-red-700">Fallidos</div>
                </div>
                
                <div class="text-center p-3 bg-purple-50 rounded-lg">
                  <div class="text-2xl font-bold text-purple-600">{{ datasetSize || 0 }}</div>
                  <div class="text-sm text-purple-700">Dataset size</div>
                </div>
              </div>
              
              <!-- Average training time -->
              <div v-if="stats.avgTrainingTime" class="mt-4 pt-4 border-t border-gray-200">
                <div class="text-center">
                  <div class="text-lg font-semibold text-gray-700">{{ formatElapsedTime(stats.avgTrainingTime) }}</div>
                  <div class="text-xs text-gray-500">Tiempo promedio de entrenamiento</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Model Comparison (if available) -->
          <div v-if="completedJobs.length >= 2" class="bg-white rounded-lg shadow-sm border border-gray-200">
            <div class="px-6 py-4 border-b border-gray-200">
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold text-gray-900">
                  Comparación de Modelos
                </h3>
                <button
                  @click="showModelComparison = !showModelComparison"
                  class="text-sm text-blue-600 hover:text-blue-500 underline"
                >
                  {{ showModelComparison ? 'Ocultar' : 'Comparar' }}
                </button>
              </div>
            </div>
            
            <div v-if="showModelComparison" class="p-6">
              <div class="space-y-3">
                <div class="text-sm text-gray-600 mb-3">
                  Selecciona modelos para comparar (máx. 3):
                </div>
                
                <div class="space-y-2 max-h-40 overflow-y-auto">
                  <label
                    v-for="job in completedJobs.slice(0, 10)"
                    :key="job.job_id"
                    class="flex items-center p-2 border border-gray-200 rounded hover:bg-gray-50 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      :value="job.job_id"
                      v-model="selectedJobsForComparison"
                      :disabled="selectedJobsForComparison.length >= 3 && !selectedJobsForComparison.includes(job.job_id)"
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <div class="ml-3 flex-1">
                      <div class="text-sm font-medium text-gray-900">
                        {{ job.experiment_name || getModelTypeLabel(job.model_type) }}
                      </div>
                      <div class="text-xs text-gray-500">
                        {{ formatRelativeTime(job.created_at) }}
                      </div>
                    </div>
                  </label>
                </div>
                
                <button
                  v-if="selectedJobsForComparison.length >= 2"
                  @click="compareSelectedModels"
                  :disabled="isComparingModels"
                  class="w-full px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  <span v-if="isComparingModels">Comparando...</span>
                  <span v-else>Comparar {{ selectedJobsForComparison.length }} modelos</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Success/Error notifications -->
    <Transition name="slide-up">
      <div 
        v-if="showNotification" 
        class="fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50"
        :class="{
          'bg-green-500 text-white': notificationType === 'success',
          'bg-red-500 text-white': notificationType === 'error',
          'bg-blue-500 text-white': notificationType === 'info'
        }"
      >
        <div class="flex items-center">
          <svg v-if="notificationType === 'success'" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <svg v-else-if="notificationType === 'error'" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg v-else class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ notificationMessage }}
        </div>
      </div>
    </Transition>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue';
import ModelTraining from '@/components/admin/ModelTraining.vue';
import { 
  getTrainingHistory, 
  cancelTrainingJob, 
  getModelMetrics, 
  compareModels 
} from '@/services/adminApi.js';
import { getDatasetStats } from '@/services/datasetApi.js';

export default {
  name: 'AdminTraining',
  components: {
    ModelTraining
  },
  
  setup() {
    // Estado principal (SRP - separado por responsabilidad)
    const trainingHistory = ref([]);
    const isLoadingHistory = ref(false);
    const isRefreshing = ref(false);
    const datasetSize = ref(0);
    const showHistoryDetails = ref(false);
    const showModelComparison = ref(false);
    const isComparingModels = ref(false);
    const selectedJobsForComparison = ref([]);
    
    // Filtros de historial (reactivos)
    const historyFilters = reactive({
      model_type: '',
      status: '',
      date_from: '',
      date_to: ''
    });
    
    // Estado de notificaciones (reactivo)
    const showNotification = ref(false);
    const notificationType = ref('info');
    const notificationMessage = ref('');
    
    // Computed properties (DRY - cálculos reutilizables)
    const activeTrainings = computed(() => {
      return trainingHistory.value.filter(job => job.status === 'running');
    });
    
    const completedJobs = computed(() => {
      return trainingHistory.value.filter(job => job.status === 'completed');
    });
    
    const completedToday = computed(() => {
      const today = new Date().toDateString();
      return trainingHistory.value.filter(job => 
        job.status === 'completed' && 
        new Date(job.created_at).toDateString() === today
      ).length;
    });
    
    const stats = computed(() => {
      const counts = trainingHistory.value.reduce((acc, job) => {
        acc[job.status] = (acc[job.status] || 0) + 1;
        return acc;
      }, {});
      
      // Calcular tiempo promedio de entrenamiento
      const completedJobsWithTime = trainingHistory.value.filter(job => 
        job.status === 'completed' && job.training_time
      );
      
      const avgTrainingTime = completedJobsWithTime.length > 0 
        ? completedJobsWithTime.reduce((sum, job) => sum + job.training_time, 0) / completedJobsWithTime.length
        : 0;
      
      return {
        ...counts,
        avgTrainingTime
      };
    });
    
    // Métodos de carga de datos (SRP - solo carga de datos)
    const loadTrainingHistory = async () => {
      isLoadingHistory.value = true;
      
      try {
        const history = await getTrainingHistory(historyFilters);
        trainingHistory.value = history;
      } catch (error) {
        console.error('Error cargando historial:', error);
        showNotificationMessage('Error cargando historial de entrenamientos', 'error');
      } finally {
        isLoadingHistory.value = false;
      }
    };
    
    const loadDatasetSize = async () => {
      try {
        const stats = await getDatasetStats();
        datasetSize.value = stats.processed_images || 0;
      } catch (error) {
        console.error('Error cargando tamaño del dataset:', error);
        datasetSize.value = 0;
      }
    };
    
    const refreshAll = async () => {
      isRefreshing.value = true;
      
      try {
        await Promise.all([
          loadTrainingHistory(),
          loadDatasetSize()
        ]);
      } catch (error) {
        console.error('Error refrescando datos:', error);
      } finally {
        isRefreshing.value = false;
      }
    };
    
    // Métodos de manejo de entrenamientos (SRP - solo gestión de entrenamientos)
    const handleTrainingStarted = (trainingData) => {
      showNotificationMessage(`Entrenamiento de ${trainingData.job.model_type} iniciado`, 'success');
      
      // Agregar al historial inmediatamente
      trainingHistory.value.unshift(trainingData.job);
      
      // Recargar historial completo para obtener datos actualizados
      setTimeout(loadTrainingHistory, 1000);
    };
    
    const handleTrainingCompleted = (job) => {
      showNotificationMessage(`Entrenamiento completado exitosamente`, 'success');
      
      // Actualizar el job en el historial
      const index = trainingHistory.value.findIndex(j => j.job_id === job.job_id);
      if (index !== -1) {
        trainingHistory.value[index] = job;
      }
    };
    
    const handleTrainingFailed = (job) => {
      showNotificationMessage(`Entrenamiento falló: ${job.error || 'Error desconocido'}`, 'error');
      
      // Actualizar el job en el historial
      const index = trainingHistory.value.findIndex(j => j.job_id === job.job_id);
      if (index !== -1) {
        trainingHistory.value[index] = job;
      }
    };
    
    const handleTrainingCancelled = (job) => {
      showNotificationMessage('Entrenamiento cancelado', 'info');
      
      // Actualizar el job en el historial
      const index = trainingHistory.value.findIndex(j => j.job_id === job.job_id);
      if (index !== -1) {
        trainingHistory.value[index] = { ...job, status: 'cancelled' };
      }
    };
    
    // Métodos de acciones sobre jobs (SRP - solo acciones de jobs)
    const cancelJob = async (jobId) => {
      if (!confirm('¿Estás seguro de que quieres cancelar este entrenamiento?')) {
        return;
      }
      
      try {
        await cancelTrainingJob(jobId);
        
        // Actualizar estado local
        const index = trainingHistory.value.findIndex(j => j.job_id === jobId);
        if (index !== -1) {
          trainingHistory.value[index].status = 'cancelled';
        }
        
        showNotificationMessage('Entrenamiento cancelado', 'info');
      } catch (error) {
        console.error('Error cancelando job:', error);
        showNotificationMessage('Error cancelando entrenamiento', 'error');
      }
    };
    
    const viewMetrics = async (job) => {
      try {
        const metrics = await getModelMetrics(job.job_id);
        
        // Aquí podrías abrir un modal con las métricas detalladas
        // Por simplicidad, mostraremos una notificación
        showNotificationMessage('Métricas cargadas (implementar modal)', 'info');
        
        console.log('Métricas del modelo:', metrics);
      } catch (error) {
        console.error('Error obteniendo métricas:', error);
        showNotificationMessage('Error obteniendo métricas', 'error');
      }
    };
    
    const viewJobDetails = (job) => {
      // Aquí podrías abrir un modal con los detalles completos del job
      // Por simplicidad, mostraremos una notificación
      showNotificationMessage('Detalles del trabajo (implementar modal)', 'info');
      
      console.log('Detalles del job:', job);
    };
    
    const compareSelectedModels = async () => {
      if (selectedJobsForComparison.value.length < 2) return;
      
      isComparingModels.value = true;
      
      try {
        const comparison = await compareModels(selectedJobsForComparison.value);
        
        // Aquí podrías mostrar un modal con la comparación
        // Por simplicidad, mostraremos una notificación
        showNotificationMessage('Comparación completada (implementar modal)', 'info');
        
        console.log('Comparación de modelos:', comparison);
      } catch (error) {
        console.error('Error comparando modelos:', error);
        showNotificationMessage('Error comparando modelos', 'error');
      } finally {
        isComparingModels.value = false;
      }
    };
    
    // Utilidades (DRY - funciones reutilizables)
    const getStatusBadgeClass = (status) => {
      const classes = {
        running: 'bg-blue-100 text-blue-800',
        completed: 'bg-green-100 text-green-800',
        failed: 'bg-red-100 text-red-800',
        cancelled: 'bg-gray-100 text-gray-800',
        pending: 'bg-yellow-100 text-yellow-800'
      };
      return classes[status] || 'bg-gray-100 text-gray-800';
    };
    
    const getStatusLabel = (status) => {
      const labels = {
        running: 'En ejecución',
        completed: 'Completado',
        failed: 'Fallido',
        cancelled: 'Cancelado',
        pending: 'Pendiente'
      };
      return labels[status] || status;
    };
    
    const getModelTypeLabel = (type) => {
      const labels = {
        regression: 'Regresión',
        vision: 'Visión'
      };
      return labels[type] || type;
    };
    
    const formatRelativeTime = (dateString) => {
      if (!dateString) return '';
      
      const now = new Date();
      const date = new Date(dateString);
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);
      
      if (diffMins < 1) return 'Hace un momento';
      if (diffMins < 60) return `Hace ${diffMins} minuto${diffMins !== 1 ? 's' : ''}`;
      if (diffHours < 24) return `Hace ${diffHours} hora${diffHours !== 1 ? 's' : ''}`;
      if (diffDays < 7) return `Hace ${diffDays} día${diffDays !== 1 ? 's' : ''}`;
      
      return date.toLocaleDateString('es-ES');
    };
    
    const formatElapsedTime = (seconds) => {
      if (!seconds) return '0s';
      
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      const secs = Math.floor(seconds % 60);
      
      if (hours > 0) return `${hours}h ${minutes}m ${secs}s`;
      if (minutes > 0) return `${minutes}m ${secs}s`;
      return `${secs}s`;
    };
    
    const formatNumber = (value, decimals = 4) => {
      if (value === null || value === undefined || isNaN(value)) return 'N/A';
      return parseFloat(value).toFixed(decimals);
    };
    
    // Métodos de notificaciones (KISS - simple y directo)
    const showNotificationMessage = (message, type = 'info') => {
      notificationMessage.value = message;
      notificationType.value = type;
      showNotification.value = true;
      
      setTimeout(() => {
        showNotification.value = false;
      }, type === 'error' ? 5000 : 3000);
    };
    
    // Auto-refresh de entrenamientos activos
    let refreshTimer = null;
    
    const startAutoRefresh = () => {
      if (activeTrainings.value.length > 0) {
        refreshTimer = setInterval(() => {
          loadTrainingHistory();
        }, 5000); // Cada 5 segundos cuando hay entrenamientos activos
      }
    };
    
    const stopAutoRefresh = () => {
      if (refreshTimer) {
        clearInterval(refreshTimer);
        refreshTimer = null;
      }
    };
    
    // Lifecycle
    onMounted(async () => {
      await refreshAll();
      startAutoRefresh();
    });
    
    onUnmounted(() => {
      stopAutoRefresh();
    });
    
    return {
      // Estado
      trainingHistory,
      isLoadingHistory,
      isRefreshing,
      datasetSize,
      showHistoryDetails,
      showModelComparison,
      isComparingModels,
      selectedJobsForComparison,
      historyFilters,
      showNotification,
      notificationType,
      notificationMessage,
      
      // Computed
      activeTrainings,
      completedJobs,
      completedToday,
      stats,
      
      // Métodos
      loadTrainingHistory,
      refreshAll,
      handleTrainingStarted,
      handleTrainingCompleted,
      handleTrainingFailed,
      handleTrainingCancelled,
      cancelJob,
      viewMetrics,
      viewJobDetails,
      compareSelectedModels,
      
      // Utilidades
      getStatusBadgeClass,
      getStatusLabel,
      getModelTypeLabel,
      formatRelativeTime,
      formatElapsedTime,
      formatNumber
    };
  }
};
</script>

<style scoped>
/* Transiciones */
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

/* Progress bar animations */
.progress-bar {
  transition: width 0.3s ease;
}

/* Grid responsivo */
@media (max-width: 1280px) {
  .xl\:grid-cols-3 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}

/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

/* Focus states */
.focus-visible:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Loading states */
.loading {
  opacity: 0.6;
  pointer-events: none;
}
</style>
