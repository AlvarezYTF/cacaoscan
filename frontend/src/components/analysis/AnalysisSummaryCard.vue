<template>
  <div class="bg-gray-50 p-4 rounded-lg">
    <h3 class="text-lg font-medium text-gray-900 mb-4">Resumen del Análisis</h3>
    <div class="space-y-4">
      <!-- Quality Score -->
      <div>
        <div class="flex justify-between text-sm mb-1">
          <span class="font-medium text-gray-700">Calificación General</span>
          <span class="font-semibold text-green-600">{{ qualityScore }}/100</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2.5">
          <div 
            class="bg-green-600 h-2.5 rounded-full transition-all duration-500" 
            :style="{ width: `${normalizedQualityScore}%` }"
          ></div>
        </div>
      </div>

      <!-- Defect Count -->
      <div class="pt-2">
        <div class="flex justify-between text-sm mb-1">
          <span class="font-medium text-gray-700">Defectos Detectados</span>
          <span class="font-semibold">{{ defectCount }}</span>
        </div>
      </div>

      <!-- Additional Metrics -->
      <div class="space-y-2 pt-2 border-t border-gray-200">
        <div v-for="(metric, index) in metrics" :key="index" class="flex justify-between text-sm">
          <span class="text-gray-600">{{ metric.name }}</span>
          <span class="font-medium">{{ metric.value }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AnalysisSummaryCard',
  props: {
    qualityScore: {
      type: Number,
      default: 0
    },
    defectCount: {
      type: Number,
      default: 0
    },
    metrics: {
      type: Array,
      default: () => []
    }
  },
  computed: {
    normalizedQualityScore() {
      // Clamp value between 0 and 100
      return Math.max(0, Math.min(100, this.qualityScore))
    }
  }
}
</script>
