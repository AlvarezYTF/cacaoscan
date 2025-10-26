<template>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- Activity Chart -->
    <div class="lg:col-span-2 bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md hover:border-green-200 transition-all duration-200">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-xl font-bold text-gray-900">{{ activityChartTitle }}</h3>
        <div class="flex items-center space-x-3">
          <select 
            v-model="activityChartType" 
            @change="handleActivityChartTypeChange" 
            class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-green-500 focus:border-green-500 bg-white hover:border-green-300 transition-colors duration-200"
          >
            <option value="line">Línea</option>
            <option value="bar">Barras</option>
          </select>
          <button 
            @click="handleActivityRefresh" 
            class="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-500"
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
    <div class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md hover:border-green-200 transition-all duration-200">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-xl font-bold text-gray-900">{{ qualityChartTitle }}</h3>
        <button 
          @click="handleQualityRefresh" 
          class="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-500"
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
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
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
      // ✅ CORRECCIÓN: Verificar que el elemento canvas existe antes de crear el gráfico
      if (!activityChart.value) {
        console.warn('⚠️ Canvas de actividad no está disponible aún')
        return
      }

      // Destruir instancia anterior si existe
      if (activityChartInstance) {
        activityChartInstance.destroy()
        activityChartInstance = null
      }

      try {
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
        console.log('✅ Gráfico de actividad creado correctamente')
      } catch (error) {
        console.error('❌ Error al crear gráfico de actividad:', error)
      }
    }

    const createQualityChart = () => {
      // ✅ CORRECCIÓN: Verificar que el elemento canvas existe antes de crear el gráfico
      if (!qualityChart.value) {
        console.warn('⚠️ Canvas de calidad no está disponible aún')
        return
      }

      // Destruir instancia anterior si existe
      if (qualityChartInstance) {
        qualityChartInstance.destroy()
        qualityChartInstance = null
      }

      try {
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
        console.log('✅ Gráfico de calidad creado correctamente')
      } catch (error) {
        console.error('❌ Error al crear gráfico de calidad:', error)
      }
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
    onMounted(async () => {
      // ✅ CORRECCIÓN: Usar nextTick para asegurar que el DOM está completamente renderizado
      // nextTick espera a que Vue termine de actualizar el DOM después del montaje
      await nextTick()
      
      console.log('📊 Iniciando creación de gráficos...')
      console.log('Canvas actividad:', activityChart.value)
      console.log('Canvas calidad:', qualityChart.value)
      
      // Crear gráficos solo si los elementos canvas están disponibles
      if (activityChart.value && qualityChart.value) {
        createActivityChart()
        createQualityChart()
      } else {
        console.error('❌ Elementos canvas no disponibles en onMounted')
        // Intentar de nuevo después de un pequeño delay como fallback
        setTimeout(() => {
          console.log('🔄 Reintentando creación de gráficos...')
          createActivityChart()
          createQualityChart()
        }, 200)
      }
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
  border-radius: 0.5rem;
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

/* Transiciones suaves */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

/* Mejoras de accesibilidad */
button:focus-visible {
  outline: 2px solid rgb(34 197 94);
  outline-offset: 2px;
}

select:focus-visible {
  outline: 2px solid rgb(34 197 94);
  outline-offset: 2px;
}

/* Estilos para elementos de estado */
.text-green-600 {
  color: rgb(34 197 94);
}

.bg-green-50 {
  background-color: rgb(240 253 244);
}

.border-green-200 {
  border-color: rgb(187 247 208);
}

.hover\:border-green-200:hover {
  border-color: rgb(187 247 208);
}

.hover\:text-green-600:hover {
  color: rgb(34 197 94);
}

.hover\:bg-green-50:hover {
  background-color: rgb(240 253 244);
}

.focus\:ring-green-500:focus {
  --tw-ring-color: rgb(34 197 94);
}
</style>
