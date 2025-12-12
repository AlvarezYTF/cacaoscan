<template>
  <BaseStatsCard
    :title="title"
    :value="formattedSummary"
    :icon="icon"
    :trend="trend"
    :color="color"
    :format="'number'"
    :loading="loading"
  >
    <template #value>
      <div class="space-y-1">
        <div class="text-lg md:text-2xl font-semibold text-gray-900">{{ formattedSummary }}</div>
        <div v-if="showDetails" class="text-xs text-gray-500 space-y-0.5">
          <div v-if="summary.avgWeight">Peso promedio: {{ summary.avgWeight }}g</div>
          <div v-if="summary.avgDimensions">
            Dimensiones: {{ summary.avgDimensions.width }}×{{ summary.avgDimensions.height }}×{{ summary.avgDimensions.thickness }}mm
          </div>
        </div>
      </div>
    </template>
    <template #footer>
      <div v-if="summary.qualityDistribution && Object.keys(summary.qualityDistribution).length > 0" class="mt-2 pt-2 border-t border-gray-200">
        <div class="flex flex-wrap gap-2">
          <span
            v-for="(count, quality) in summary.qualityDistribution"
            :key="quality"
            class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
            :class="getQualityColor(quality)"
          >
            {{ quality }}: {{ count }}
          </span>
        </div>
      </div>
    </template>
  </BaseStatsCard>
</template>

<script setup>
import { computed } from 'vue'
import BaseStatsCard from './BaseStatsCard.vue'

const props = defineProps({
  title: {
    type: String,
    default: 'Resumen de Análisis'
  },
  summary: {
    type: Object,
    required: true,
    validator: (value) => {
      return value && typeof value === 'object'
    }
  },
  icon: {
    type: [String, Object],
    default: null
  },
  trend: {
    type: Object,
    default: null
  },
  color: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'success', 'warning', 'danger', 'info'].includes(value)
  },
  loading: {
    type: Boolean,
    default: false
  },
  showDetails: {
    type: Boolean,
    default: false
  },
  format: {
    type: String,
    default: 'total',
    validator: (value) => ['total', 'average', 'weight'].includes(value)
  }
})

const formattedSummary = computed(() => {
  switch (props.format) {
    case 'average':
      return props.summary.avgWeight ? `${props.summary.avgWeight}g` : '0g'
    case 'weight':
      return props.summary.avgWeight ? `${props.summary.avgWeight}g` : '0g'
    case 'total':
    default:
      return props.summary.total || 0
  }
})

const getQualityColor = (quality) => {
  const colorMap = {
    excellent: 'bg-green-100 text-green-800',
    good: 'bg-blue-100 text-blue-800',
    fair: 'bg-yellow-100 text-yellow-800',
    poor: 'bg-red-100 text-red-800',
    unknown: 'bg-gray-100 text-gray-800'
  }
  return colorMap[quality?.toLowerCase()] || colorMap.unknown
}
</script>

<style scoped>
/* Additional styles if needed */
</style>

