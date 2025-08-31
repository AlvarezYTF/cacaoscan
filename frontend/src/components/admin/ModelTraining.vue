<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold text-gray-900">
            Entrenamiento de Modelos ML
          </h3>
          <p class="text-sm text-gray-600 mt-1">
            Configure y ejecute entrenamientos de modelos con parámetros avanzados
          </p>
        </div>
        <div v-if="isTraining" class="flex items-center text-sm text-blue-600">
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Entrenando {{ getModelTypeLabel(currentTraining.model_type) }}
        </div>
      </div>
    </div>

    <div class="p-6">
      <!-- Training Configuration Form -->
      <form @submit.prevent="handleStartTraining" class="space-y-6">
        <!-- Model Type Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-3">
            Tipo de Modelo
            <span class="text-red-500">*</span>
          </label>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="modelType in modelTypes"
              :key="modelType.value"
              @click="trainingConfig.model_type = modelType.value"
              class="relative rounded-lg border-2 cursor-pointer p-4 hover:border-blue-300 transition-colors"
              :class="{
                'border-blue-500 bg-blue-50': trainingConfig.model_type === modelType.value,
                'border-gray-300': trainingConfig.model_type !== modelType.value
              }"
            >
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg class="w-6 h-6" :class="modelType.color" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="modelType.icon" />
                  </svg>
                </div>
                <div class="ml-3 flex-1">
                  <div class="text-sm font-medium text-gray-900">{{ modelType.label }}</div>
                  <div class="text-xs text-gray-500">{{ modelType.description }}</div>
                </div>
                <div v-if="trainingConfig.model_type === modelType.value" class="absolute top-2 right-2">
                  <svg class="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Training Preset Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-3">
            Configuración Predefinida
          </label>
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-3">
            <div
              v-for="(preset, key) in trainingPresets"
              :key="key"
              @click="selectPreset(key)"
              class="relative rounded-lg border-2 cursor-pointer p-3 hover:border-green-300 transition-colors"
              :class="{
                'border-green-500 bg-green-50': selectedPreset === key,
                'border-gray-300': selectedPreset !== key
              }"
            >
              <div class="text-sm font-medium text-gray-900">{{ preset.name }}</div>
              <div class="text-xs text-gray-500 mt-1">{{ preset.description }}</div>
              <div v-if="selectedPreset === key" class="absolute top-2 right-2">
                <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Training Parameters (shows when CUSTOM is selected or user wants to modify) -->
        <div v-if="selectedPreset === 'CUSTOM' || showAdvancedParams" class="space-y-4">
          <div class="flex items-center justify-between">
            <h4 class="text-md font-medium text-gray-900">Parámetros de Entrenamiento</h4>
            <button
              v-if="selectedPreset !== 'CUSTOM'"
              type="button"
              @click="showAdvancedParams = !showAdvancedParams"
              class="text-sm text-blue-600 hover:text-blue-500"
            >
              {{ showAdvancedParams ? 'Ocultar' : 'Personalizar' }} parámetros
            </button>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Épocas
              </label>
              <input
                v-model.number="trainingConfig.epochs"
                type="number"
                min="1"
                max="1000"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <p class="text-xs text-gray-500 mt-1">Número de iteraciones completas</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Learning Rate
              </label>
              <input
                v-model.number="trainingConfig.learning_rate"
                type="number"
                step="0.00001"
                min="0.00001"
                max="1"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <p class="text-xs text-gray-500 mt-1">Velocidad de aprendizaje</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Batch Size
              </label>
              <input
                v-model.number="trainingConfig.batch_size"
                type="number"
                min="1"
                max="256"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <p class="text-xs text-gray-500 mt-1">Muestras por lote</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Validation Split
              </label>
              <input
                v-model.number="trainingConfig.validation_split"
                type="number"
                step="0.01"
                min="0.1"
                max="0.5"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <p class="text-xs text-gray-500 mt-1">Porción para validación</p>
            </div>

            <div class="flex items-center">
              <input
                v-model="trainingConfig.early_stopping"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label class="ml-2 text-sm text-gray-700">
                Early Stopping
              </label>
            </div>
          </div>
        </div>

        <!-- Data Filters -->
        <div>
          <h4 class="text-md font-medium text-gray-900 mb-3">Filtros de Datos</h4>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Calidad de Datos
              </label>
              <select
                v-model="dataFilters.quality_level"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option v-for="(filter, key) in qualityFilters" :key="key" :value="key">
                  {{ filter.label }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Tipo de Datos
              </label>
              <select
                v-model="dataFilters.data_type"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option v-for="(filter, key) in dataTypeFilters" :key="key" :value="key">
                  {{ filter.label }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Período de Datos
              </label>
              <select
                v-model="dataFilters.time_range"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option v-for="(filter, key) in timeRangeFilters" :key="key" :value="key">
                  {{ filter.label }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <!-- Experiment Information -->
        <div>
          <h4 class="text-md font-medium text-gray-900 mb-3">Información del Experimento</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Nombre del Experimento
              </label>
              <input
                v-model="experimentData.name"
                type="text"
                :placeholder="generateExperimentName()"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Tags (separados por comas)
              </label>
              <input
                v-model="experimentData.tagsInput"
                type="text"
                placeholder="producción, optimizado, v2"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          <div class="mt-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Descripción
            </label>
            <textarea
              v-model="experimentData.description"
              rows="3"
              placeholder="Describe el objetivo de este entrenamiento..."
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            ></textarea>
          </div>
        </div>

        <!-- Training Estimation -->
        <div v-if="trainingEstimation" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 class="text-sm font-medium text-blue-800 mb-2 flex items-center">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Estimación de Entrenamiento
          </h4>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <div class="text-blue-700 font-medium">Tiempo Estimado</div>
              <div class="text-blue-600">{{ trainingEstimation.formatted }}</div>
            </div>
            <div>
              <div class="text-blue-700 font-medium">Finalización Aprox.</div>
              <div class="text-blue-600">{{ formatDateTime(trainingEstimation.estimatedCompletion) }}</div>
            </div>
            <div>
              <div class="text-blue-700 font-medium">Dataset Size</div>
              <div class="text-blue-600">{{ datasetSize || 'Calculando...' }} muestras</div>
            </div>
          </div>
        </div>

        <!-- Validation Errors -->
        <div v-if="validationErrors.length > 0" class="bg-red-50 border border-red-200 rounded-lg p-4">
          <h4 class="text-sm font-medium text-red-800 mb-2 flex items-center">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Errores de Configuración
          </h4>
          <ul class="text-sm text-red-700 space-y-1">
            <li v-for="error in validationErrors" :key="error" class="flex items-start">
              <span class="mr-2">•</span>
              {{ error }}
            </li>
          </ul>
        </div>

        <!-- Submit Button -->
        <div class="flex justify-end space-x-3">
          <button
            type="button"
            @click="resetConfiguration"
            class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Restablecer
          </button>
          
          <button
            type="submit"
            :disabled="!canStartTraining || isTraining"
            class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            <span v-if="isTraining" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-3 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Iniciando...
            </span>
            <span v-else>
              Iniciar Entrenamiento
            </span>
          </button>
        </div>
      </form>

      <!-- Current Training Progress -->
      <div v-if="currentTraining && isTraining" class="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-center justify-between mb-3">
          <h4 class="text-lg font-medium text-blue-800">
            Entrenamiento en Progreso: {{ getModelTypeLabel(currentTraining.model_type) }}
          </h4>
          <button
            @click="cancelCurrentTraining"
            class="text-sm text-red-600 hover:text-red-700 underline"
          >
            Cancelar
          </button>
        </div>
        
        <!-- Progress Bar -->
        <div class="mb-3">
          <div class="flex justify-between text-sm text-blue-700 mb-1">
            <span>Progreso</span>
            <span>{{ Math.round(currentTraining.progress || 0) }}%</span>
          </div>
          <div class="w-full bg-blue-200 rounded-full h-3">
            <div 
              class="bg-blue-600 h-3 rounded-full transition-all duration-300"
              :style="{ width: `${currentTraining.progress || 0}%` }"
            ></div>
          </div>
        </div>
        
        <!-- Training Info -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <div class="text-blue-700 font-medium">Época Actual</div>
            <div class="text-blue-600">{{ currentTraining.current_epoch || 0 }} / {{ currentTraining.total_epochs || 0 }}</div>
          </div>
          <div v-if="currentTraining.current_loss">
            <div class="text-blue-700 font-medium">Loss Actual</div>
            <div class="text-blue-600">{{ formatNumber(currentTraining.current_loss) }}</div>
          </div>
          <div v-if="currentTraining.validation_accuracy">
            <div class="text-blue-700 font-medium">Val. Accuracy</div>
            <div class="text-blue-600">{{ Math.round(currentTraining.validation_accuracy * 100) }}%</div>
          </div>
          <div v-if="currentTraining.elapsed_time">
            <div class="text-blue-700 font-medium">Tiempo Transcurrido</div>
            <div class="text-blue-600">{{ formatElapsedTime(currentTraining.elapsed_time) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue';
import { 
  startAdvancedTraining, 
  cancelTrainingJob,
  getTrainingJobStatus,
  validateTrainingConfig,
  estimateTrainingTime,
  TRAINING_PRESETS,
  DATA_FILTERS 
} from '@/services/adminApi.js';

export default {
  name: 'ModelTraining',
  
  // Props (SRP - configuración específica)
  props: {
    availableDatasetSize: {
      type: Number,
      default: 0
    },
    autoRefreshInterval: {
      type: Number,
      default: 2000
    }
  },
  
  // Eventos (SRP - comunicación clara)
  emits: ['training-started', 'training-completed', 'training-failed', 'training-cancelled'],
  
  setup(props, { emit }) {
    // Estado reactivo (SRP - separado por responsabilidad)
    const selectedPreset = ref('STANDARD');
    const showAdvancedParams = ref(false);
    const isTraining = ref(false);
    const currentTraining = ref(null);
    const datasetSize = ref(props.availableDatasetSize);
    const statusTimer = ref(null);
    
    // Configuración de entrenamiento (reactiva)
    const trainingConfig = reactive({
      model_type: 'regression',
      epochs: 50,
      learning_rate: 0.001,
      batch_size: 32,
      validation_split: 0.2,
      early_stopping: true
    });
    
    // Filtros de datos (reactivos)
    const dataFilters = reactive({
      quality_level: 'HIGH',
      data_type: 'PROCESSED_ONLY',
      time_range: 'ALL'
    });
    
    // Información del experimento (reactiva)
    const experimentData = reactive({
      name: '',
      description: '',
      tagsInput: '',
      tags: []
    });
    
    // Configuraciones estáticas (KISS - definiciones simples)
    const modelTypes = ref([
      {
        value: 'regression',
        label: 'Modelo de Regresión',
        description: 'Predice peso basado en dimensiones',
        icon: 'M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z',
        color: 'text-blue-500'
      },
      {
        value: 'vision',
        label: 'Modelo de Visión',
        description: 'CNN para análisis de imágenes',
        icon: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z',
        color: 'text-purple-500'
      }
    ]);
    
    const trainingPresets = computed(() => TRAINING_PRESETS);
    const qualityFilters = computed(() => DATA_FILTERS.QUALITY_LEVELS);
    const dataTypeFilters = computed(() => DATA_FILTERS.DATA_TYPES);
    const timeRangeFilters = computed(() => DATA_FILTERS.TIME_RANGES);
    
    // Computed properties (DRY - cálculos reutilizables)
    const validationErrors = computed(() => {
      const validation = validateTrainingConfig(trainingConfig.model_type, trainingConfig);
      return validation.errors;
    });
    
    const canStartTraining = computed(() => {
      return validationErrors.value.length === 0 && 
             trainingConfig.model_type && 
             datasetSize.value > 0 &&
             !isTraining.value;
    });
    
    const trainingEstimation = computed(() => {
      if (!canStartTraining.value) return null;
      
      return estimateTrainingTime(
        trainingConfig.model_type,
        trainingConfig,
        datasetSize.value
      );
    });
    
    // Métodos de configuración (SRP - solo configuración)
    const selectPreset = (presetKey) => {
      selectedPreset.value = presetKey;
      
      if (presetKey !== 'CUSTOM') {
        const preset = TRAINING_PRESETS[presetKey];
        const modelConfig = preset[trainingConfig.model_type];
        
        if (modelConfig) {
          Object.assign(trainingConfig, modelConfig);
        }
        
        showAdvancedParams.value = false;
      } else {
        showAdvancedParams.value = true;
      }
    };
    
    const resetConfiguration = () => {
      selectedPreset.value = 'STANDARD';
      showAdvancedParams.value = false;
      selectPreset('STANDARD');
      
      // Reset data filters
      dataFilters.quality_level = 'HIGH';
      dataFilters.data_type = 'PROCESSED_ONLY';
      dataFilters.time_range = 'ALL';
      
      // Reset experiment data
      experimentData.name = '';
      experimentData.description = '';
      experimentData.tagsInput = '';
      experimentData.tags = [];
    };
    
    // Métodos de entrenamiento (SRP - solo entrenamiento)
    const handleStartTraining = async () => {
      if (!canStartTraining.value) return;
      
      isTraining.value = true;
      
      try {
        // Preparar tags
        experimentData.tags = experimentData.tagsInput
          .split(',')
          .map(tag => tag.trim())
          .filter(tag => tag.length > 0);
        
        // Preparar filtros de datos
        const appliedFilters = buildDataFilters();
        
        // Iniciar entrenamiento
        const job = await startAdvancedTraining(
          trainingConfig.model_type,
          { ...trainingConfig },
          appliedFilters,
          { ...experimentData }
        );
        
        currentTraining.value = job;
        
        // Iniciar polling de estado
        startStatusPolling(job.job_id);
        
        emit('training-started', {
          job,
          config: { ...trainingConfig },
          filters: appliedFilters,
          experiment: { ...experimentData }
        });
        
      } catch (error) {
        console.error('Error iniciando entrenamiento:', error);
        isTraining.value = false;
        emit('training-failed', error);
      }
    };
    
    const cancelCurrentTraining = async () => {
      if (!currentTraining.value) return;
      
      try {
        await cancelTrainingJob(currentTraining.value.job_id);
        stopStatusPolling();
        isTraining.value = false;
        currentTraining.value = null;
        
        emit('training-cancelled', currentTraining.value);
        
      } catch (error) {
        console.error('Error cancelando entrenamiento:', error);
      }
    };
    
    const startStatusPolling = (jobId) => {
      statusTimer.value = setInterval(async () => {
        try {
          const status = await getTrainingJobStatus(jobId);
          currentTraining.value = { ...currentTraining.value, ...status };
          
          if (status.status === 'completed') {
            stopStatusPolling();
            isTraining.value = false;
            emit('training-completed', currentTraining.value);
          } else if (status.status === 'failed') {
            stopStatusPolling();
            isTraining.value = false;
            emit('training-failed', currentTraining.value);
          }
        } catch (error) {
          console.error('Error obteniendo estado:', error);
        }
      }, props.autoRefreshInterval);
    };
    
    const stopStatusPolling = () => {
      if (statusTimer.value) {
        clearInterval(statusTimer.value);
        statusTimer.value = null;
      }
    };
    
    // Utilidades (DRY - funciones reutilizables)
    const buildDataFilters = () => {
      const filters = {};
      
      // Aplicar filtros de calidad
      const qualityFilter = qualityFilters.value[dataFilters.quality_level];
      Object.assign(filters, qualityFilter);
      
      // Aplicar filtros de tipo de datos
      const dataTypeFilter = dataTypeFilters.value[dataFilters.data_type];
      Object.assign(filters, dataTypeFilter);
      
      // Aplicar filtros de tiempo
      const timeFilter = timeRangeFilters.value[dataFilters.time_range];
      if (timeFilter.days_back) {
        const date = new Date();
        date.setDate(date.getDate() - timeFilter.days_back);
        filters.date_from = date.toISOString().split('T')[0];
      }
      
      return filters;
    };
    
    const generateExperimentName = () => {
      const date = new Date().toISOString().split('T')[0];
      const modelType = trainingConfig.model_type;
      const preset = selectedPreset.value.toLowerCase();
      return `${modelType}_${preset}_${date}`;
    };
    
    const getModelTypeLabel = (type) => {
      const model = modelTypes.value.find(m => m.value === type);
      return model ? model.label : type;
    };
    
    const formatDateTime = (dateString) => {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
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
    
    // Watchers (reactividad específica)
    watch(() => trainingConfig.model_type, () => {
      if (selectedPreset.value !== 'CUSTOM') {
        selectPreset(selectedPreset.value);
      }
    });
    
    watch(() => experimentData.tagsInput, (newValue) => {
      experimentData.tags = newValue
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0);
    });
    
    watch(() => props.availableDatasetSize, (newSize) => {
      datasetSize.value = newSize;
    });
    
    // Lifecycle
    onMounted(() => {
      // Aplicar preset por defecto
      selectPreset('STANDARD');
      
      // Auto-generar nombre de experimento
      if (!experimentData.name) {
        experimentData.name = generateExperimentName();
      }
    });
    
    onUnmounted(() => {
      stopStatusPolling();
    });
    
    return {
      // Estado
      selectedPreset,
      showAdvancedParams,
      isTraining,
      currentTraining,
      datasetSize,
      trainingConfig,
      dataFilters,
      experimentData,
      
      // Configuraciones
      modelTypes,
      trainingPresets,
      qualityFilters,
      dataTypeFilters,
      timeRangeFilters,
      
      // Computed
      validationErrors,
      canStartTraining,
      trainingEstimation,
      
      // Métodos
      selectPreset,
      resetConfiguration,
      handleStartTraining,
      cancelCurrentTraining,
      generateExperimentName,
      getModelTypeLabel,
      formatDateTime,
      formatElapsedTime,
      formatNumber
    };
  }
};
</script>

<style scoped>
/* Transiciones */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Efectos hover */
.hover-scale:hover {
  transform: scale(1.02);
  transition: transform 0.2s ease;
}

/* Estados de selección */
.selected-preset {
  border-color: #10b981;
  background-color: #ecfdf5;
}

.selected-model {
  border-color: #3b82f6;
  background-color: #eff6ff;
}

/* Progress bar animation */
.progress-bar {
  transition: width 0.3s ease;
}

/* Focus states */
.focus-visible:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Grid responsive */
@media (max-width: 768px) {
  .lg\:grid-cols-3 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .md\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}

/* Loading states */
.loading {
  opacity: 0.6;
  pointer-events: none;
}

/* Custom scrollbar para textarea */
textarea::-webkit-scrollbar {
  width: 6px;
}

textarea::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

textarea::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}
</style>
