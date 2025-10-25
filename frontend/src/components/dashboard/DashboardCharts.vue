<template>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
    <!-- Activity Chart -->
    <div class="lg:col-span-2 bg-white rounded-lg border border-gray-200 p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-900">{{ activityChartTitle }}</h3>
        <div class="flex items-center space-x-2">
          <select 
            v-model="activityChartType" 
            @change="handleActivityChartTypeChange" 
            class="text-sm border border-gray-300 rounded-lg px-3 py-1 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="line">Línea</option>
            <option value="bar">Barras</option>
          </select>
          <button 
            @click="handleActivityRefresh" 
            class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
            :disabled="loading"
          >
            <LoadingSpinner 
              v-if="loading" 
              size="sm" 
              color="gray" 
            />
            <svg 
              v-else
              class="w-4 h-4" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
          </button>
        </div>
      </div>
      <div class="h-80">
        <canvas ref="activityChart" @click="handleActivityClick"></canvas>
      </div>
    </div>

    <!-- Quality Distribution Chart -->
    <div class="bg-white rounded-lg border border-gray-200 p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-900">{{ qualityChartTitle }}</h3>
        <button 
          @click="handleQualityRefresh" 
          class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
          :disabled="loading"
        >
          <LoadingSpinner 
            v-if="loading" 
            size="sm" 
            color="gray" 
          />
          <svg 
            v-else
            class="w-4 h-4" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
        </button>
      </div>
      <div class="h-80">
        <canvas ref="qualityChart" @click="handleQualityClick"></canvas>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import Chart from 'chart.js/auto'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

export default {
  name: 'DashboardCharts',
  components: {
    LoadingSpinner
  },
  props: {
    activityChartTitle: {
      type: String,
      default: 'Actividad de Usuarios'
    },
    qualityChartTitle: {
      type: String,
      default: 'Distribución de Calidad'
    },
    activityChartData: {
      type: Object,
      default: () => ({ labels: [], datasets: [] })
    },
    qualityChartData: {
      type: Object,
      default: () => ({ labels: [], datasets: [] })
    },
    activityChartOptions: {
      type: Object,
      default: () => ({})
    },
    qualityChartOptions: {
      type: Object,
      default: () => ({})
    },
    loading: {
      type: Boolean,
      default: false
    },
    initialActivityChartType: {
      type: String,
      default: 'line'
    }
  },
  emits: ['activity-chart-type-change', 'activity-refresh', 'quality-refresh', 'activity-click', 'quality-click'],
  setup(props, { emit }) {
    // Chart refs
    const activityChart = ref(null)
    const qualityChart = ref(null)
    const activityChartType = ref(props.initialActivityChartType)
    
    // Chart instances
    let activityChartInstance = null
    let qualityChartInstance = null

    // Methods
    const createActivityChart = () => {
      if (activityChartInstance) {
        activityChartInstance.destroy()
      }

      const ctx = activityChart.value.getContext('2d')
      activityChartInstance = new Chart(ctx, {
        type: activityChartType.value,
        data: props.activityChartData,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          ...props.activityChartOptions
        }
      })
    }

    const createQualityChart = () => {
      if (qualityChartInstance) {
        qualityChartInstance.destroy()
      }

      const ctx = qualityChart.value.getContext('2d')
      qualityChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: props.qualityChartData,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          ...props.qualityChartOptions
        }
      })
    }

    const updateActivityChart = () => {
      if (activityChartInstance) {
        activityChartInstance.data = props.activityChartData
        activityChartInstance.update()
      }
    }

    const updateQualityChart = () => {
      if (qualityChartInstance) {
        qualityChartInstance.data = props.qualityChartData
        qualityChartInstance.update()
      }
    }

    const handleActivityChartTypeChange = () => {
      emit('activity-chart-type-change', activityChartType.value)
      createActivityChart()
    }

    const handleActivityRefresh = () => {
      emit('activity-refresh')
    }

    const handleQualityRefresh = () => {
      emit('quality-refresh')
    }

    const handleActivityClick = (event) => {
      emit('activity-click', event)
    }

    const handleQualityClick = (event) => {
      emit('quality-click', event)
    }

    // Watch for data changes
    watch(() => props.activityChartData, () => {
      updateActivityChart()
    }, { deep: true })

    watch(() => props.qualityChartData, () => {
      updateQualityChart()
    }, { deep: true })

    watch(() => props.initialActivityChartType, (newValue) => {
      activityChartType.value = newValue
    })

    // Lifecycle
    onMounted(() => {
      // Create charts after component is mounted
      setTimeout(() => {
        createActivityChart()
        createQualityChart()
      }, 100)
    })

    onUnmounted(() => {
      if (activityChartInstance) {
        activityChartInstance.destroy()
      }
      if (qualityChartInstance) {
        qualityChartInstance.destroy()
      }
    })

    return {
      activityChart,
      qualityChart,
      activityChartType,
      handleActivityChartTypeChange,
      handleActivityRefresh,
      handleQualityRefresh,
      handleActivityClick,
      handleQualityClick
    }
  }
}
</script>

<style scoped>
/* Estilos específicos para los gráficos */
canvas {
  max-height: 320px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  canvas {
    max-height: 250px;
  }
}

/* Animation for loading spinner */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Chart container hover effects */
.bg-white:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.2s ease-in-out;
}
</style>
