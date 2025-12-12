<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
    <div class="bg-gradient-to-r from-blue-50 to-purple-50 px-6 py-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <div class="bg-blue-100 p-2 rounded-xl mr-3">
            <svg class="text-xl text-blue-600 w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
          </div>
          <div>
            <h2 class="text-lg font-bold text-gray-900">Evolución de Calidad</h2>
            <p class="text-sm text-gray-600">Tendencia en el tiempo</p>
          </div>
        </div>
        <select
          v-model="selectedPeriod"
          @change="$emit('period-change', selectedPeriod)"
          class="text-sm border border-gray-300 rounded-lg px-3 py-1 bg-white"
        >
          <option value="7">Últimos 7 días</option>
          <option value="30">Últimos 30 días</option>
          <option value="90">Últimos 90 días</option>
        </select>
      </div>
    </div>
    
    <div class="p-6">
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        <p class="text-gray-600 mt-2">Cargando datos...</p>
      </div>
      
      <div v-else-if="!chartData || chartData.length === 0" class="text-center py-12">
        <div class="text-gray-400 text-4xl mb-2">📊</div>
        <p class="text-gray-600 font-medium">No hay datos disponibles</p>
        <p class="text-gray-500 text-sm mt-1">Realiza análisis para ver la evolución</p>
      </div>
      
      <div v-else ref="chartContainer" class="h-64"></div>
      
      <!-- Legend -->
      <div v-if="chartData && chartData.length > 0" class="mt-4 flex items-center justify-center gap-4 flex-wrap">
        <div class="flex items-center gap-2">
          <div class="w-4 h-4 bg-blue-500 rounded"></div>
          <span class="text-sm text-gray-600">Calidad promedio</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-4 h-4 bg-red-500 rounded"></div>
          <span class="text-sm text-gray-600">% Defectos</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'

const props = defineProps({
  chartData: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['period-change'])

const chartContainer = ref(null)
const selectedPeriod = ref('30')
let chart = null

// Simple line chart using SVG
const renderChart = () => {
  if (!chartContainer.value || !props.chartData || props.chartData.length === 0) {
    return
  }
  
  const container = chartContainer.value
  const width = container.clientWidth
  const height = 256
  const padding = { top: 20, right: 20, bottom: 40, left: 50 }
  const chartWidth = width - padding.left - padding.right
  const chartHeight = height - padding.top - padding.bottom
  
  // Clear previous chart
  container.innerHTML = ''
  
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
  svg.setAttribute('width', width)
  svg.setAttribute('height', height)
  svg.setAttribute('viewBox', `0 0 ${width} ${height}`)
  container.appendChild(svg)
  
  // Calculate scales
  const maxQuality = Math.max(...props.chartData.map(d => d.quality), 100)
  const maxDefects = Math.max(...props.chartData.map(d => d.defects), 100)
  const maxValue = Math.max(maxQuality, maxDefects)
  
  const xScale = (index) => padding.left + (index / (props.chartData.length - 1 || 1)) * chartWidth
  const yScale = (value) => padding.top + chartHeight - (value / maxValue) * chartHeight
  
  // Draw grid lines
  for (let i = 0; i <= 5; i++) {
    const y = padding.top + (chartHeight / 5) * i
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line')
    line.setAttribute('x1', padding.left)
    line.setAttribute('y1', y)
    line.setAttribute('x2', width - padding.right)
    line.setAttribute('y2', y)
    line.setAttribute('stroke', '#e5e7eb')
    line.setAttribute('stroke-width', '1')
    svg.appendChild(line)
  }
  
  // Draw quality line
  const qualityPath = props.chartData.map((d, i) => {
    const x = xScale(i)
    const y = yScale(d.quality)
    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
  }).join(' ')
  
  const qualityLine = document.createElementNS('http://www.w3.org/2000/svg', 'path')
  qualityLine.setAttribute('d', qualityPath)
  qualityLine.setAttribute('fill', 'none')
  qualityLine.setAttribute('stroke', '#3b82f6')
  qualityLine.setAttribute('stroke-width', '2')
  svg.appendChild(qualityLine)
  
  // Draw defects line
  const defectsPath = props.chartData.map((d, i) => {
    const x = xScale(i)
    const y = yScale(d.defects)
    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
  }).join(' ')
  
  const defectsLine = document.createElementNS('http://www.w3.org/2000/svg', 'path')
  defectsLine.setAttribute('d', defectsPath)
  defectsLine.setAttribute('fill', 'none')
  defectsLine.setAttribute('stroke', '#ef4444')
  defectsLine.setAttribute('stroke-width', '2')
  svg.appendChild(defectsLine)
  
  // Draw points
  props.chartData.forEach((d, i) => {
    const x = xScale(i)
    const yQuality = yScale(d.quality)
    const yDefects = yScale(d.defects)
    
    // Quality point
    const qualityPoint = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
    qualityPoint.setAttribute('cx', x)
    qualityPoint.setAttribute('cy', yQuality)
    qualityPoint.setAttribute('r', '4')
    qualityPoint.setAttribute('fill', '#3b82f6')
    svg.appendChild(qualityPoint)
    
    // Defects point
    const defectsPoint = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
    defectsPoint.setAttribute('cx', x)
    defectsPoint.setAttribute('cy', yDefects)
    defectsPoint.setAttribute('r', '4')
    defectsPoint.setAttribute('fill', '#ef4444')
    svg.appendChild(defectsPoint)
  })
  
  // Draw labels
  props.chartData.forEach((d, i) => {
    if (i % Math.ceil(props.chartData.length / 5) === 0 || i === props.chartData.length - 1) {
      const x = xScale(i)
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text')
      text.setAttribute('x', x)
      text.setAttribute('y', height - padding.bottom + 15)
      text.setAttribute('text-anchor', 'middle')
      text.setAttribute('font-size', '10')
      text.setAttribute('fill', '#6b7280')
      text.textContent = d.date
      svg.appendChild(text)
    }
  })
}

watch(() => props.chartData, () => {
  renderChart()
}, { deep: true })

onMounted(() => {
  if (props.chartData && props.chartData.length > 0) {
    setTimeout(renderChart, 100)
  }
})

onUnmounted(() => {
  if (chartContainer.value) {
    chartContainer.value.innerHTML = ''
  }
})
</script>

