<template>
  <!-- Charts con diseño profesional mejorado -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6" data-cy="dashboard-charts">
    <!-- Activity Chart -->
    <div class="lg:col-span-2 bg-white rounded-2xl border-2 border-gray-200 p-8 hover:shadow-xl hover:border-green-300 transition-all duration-300">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-green-100 rounded-xl">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
          </div>
          <h3 class="text-2xl font-bold text-gray-900">{{ activityChartTitle }}</h3>
        </div>
        <div class="flex items-center gap-2">
          <select 
            v-model="activityChartType" 
            @change="handleActivityChartTypeChange" 
            class="text-sm border-2 border-gray-200 rounded-xl px-4 py-2.5 focus:ring-2 focus:ring-green-500 focus:border-green-500 bg-white hover:border-green-300 transition-all duration-200 font-medium"
          >
            <option value="line">Línea</option>
            <option value="bar">Barras</option>
          </select>
          <button 
            @click="handleActivityRefresh" 
            type="button"
            class="group p-2.5 text-gray-500 hover:text-white hover:bg-green-600 rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
            :disabled="loading"
            title="Actualizar datos"
          >
            <BaseSpinner 
              v-if="loading" 
              size="sm" 
              color="gray" 
            />
            <svg 
              v-else
              class="w-5 h-5 group-hover:rotate-180 transition-transform duration-500" 
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
        <BaseChart
          ref="activityChartRef"
          :chart-data="activityChartData"
          :options="mergedActivityOptions"
          :type="activityChartType"
          :height="320"
          :show-legend="true"
          :show-controls="false"
          @chart-click="handleActivityClick"
        />
      </div>
    </div>

    <!-- Quality Distribution Chart -->
    <div class="bg-white rounded-2xl border-2 border-gray-200 p-8 hover:shadow-xl hover:border-green-300 transition-all duration-300">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-green-100 rounded-xl">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900">{{ qualityChartTitle }}</h3>
        </div>
        <button 
          @click="handleQualityRefresh" 
          type="button"
          class="group p-2.5 text-gray-500 hover:text-white hover:bg-green-600 rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
          :disabled="loading"
          title="Actualizar datos"
        >
          <BaseSpinner 
            v-if="loading" 
            size="sm" 
            color="gray" 
          />
          <svg 
            v-else
            class="w-5 h-5 group-hover:rotate-180 transition-transform duration-500" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
        </button>
      </div>
      <div class="h-80">
        <BaseChart
          ref="qualityChartRef"
          :chart-data="qualityChartData"
          :options="mergedQualityOptions"
          type="doughnut"
          :height="320"
          :show-legend="true"
          :show-controls="false"
          @chart-click="handleQualityClick"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import BaseSpinner from '@/components/common/BaseSpinner.vue'
import BaseChart from '@/components/charts/BaseChart.vue'

// Props
const props = defineProps({
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
})

// Emits
const emit = defineEmits(['activity-chart-type-change', 'activity-refresh', 'quality-refresh', 'activity-click', 'quality-click'])

// Chart refs
const activityChartRef = ref(null)
const qualityChartRef = ref(null)
const activityChartType = ref(props.initialActivityChartType)

// Merged options
const mergedActivityOptions = computed(() => {
  return {
    responsive: true,
    maintainAspectRatio: false,
    ...props.activityChartOptions
  }
})

const mergedQualityOptions = computed(() => {
  return {
    responsive: true,
    maintainAspectRatio: false,
    ...props.qualityChartOptions
  }
})

// Event handlers
const handleActivityChartTypeChange = () => {
  emit('activity-chart-type-change', activityChartType.value)
  // Chart type change requires recreating the chart, which BaseChart handles via watch
}

const handleActivityRefresh = () => {
  emit('activity-refresh')
}

const handleQualityRefresh = () => {
  emit('quality-refresh')
}

const handleActivityClick = (data) => {
  emit('activity-click', data)
}

const handleQualityClick = (data) => {
  emit('quality-click', data)
}

// Watch for data changes
watch(() => props.activityChartData, () => {
  if (activityChartRef.value) {
    activityChartRef.value.updateChart(props.activityChartData)
  }
}, { deep: true })

watch(() => props.qualityChartData, () => {
  if (qualityChartRef.value) {
    qualityChartRef.value.updateChart(props.qualityChartData)
  }
}, { deep: true })

watch(() => props.initialActivityChartType, (newValue) => {
  activityChartType.value = newValue
})
</script>

<style scoped>
/* Responsive adjustments */
@media (max-width: 768px) {
  .h-80 {
    height: 250px;
  }
}
</style>
