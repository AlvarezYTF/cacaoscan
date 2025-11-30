<template>
  <div class="stats-grid">
    <BaseStatsCard
      v-for="(stat, index) in stats"
      :key="stat.id || index"
      :title="stat.label"
      :value="stat.value"
      :icon="stat.icon"
      :trend="stat.trend || (stat.change !== undefined ? { value: stat.change, label: stat.changePeriod || `${Math.abs(stat.change)}% desde el mes pasado` } : null)"
      :format="stat.format || 'number'"
      :color="stat.variant || 'default'"
      :loading="stat.loading || false"
      @click="stat.clickable ? handleStatClick(stat) : null"
      :class="{ 'cursor-pointer': stat.clickable }"
    >
      <template v-if="stat.trend" #footer>
        <TrendChart 
          v-if="stat.trend && stat.trend.data" 
          :data="stat.trend.data" 
          :color="stat.trend.color || getStatColor(index)"
          :height="40"
        />
      </template>
    </BaseStatsCard>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import BaseStatsCard from '@/components/common/BaseStatsCard.vue'
import TrendChart from './TrendChart.vue'

const props = defineProps({
  stats: {
    type: Array,
    required: true,
    validator: (stats) => {
      return stats.every(stat => 
        stat.hasOwnProperty('value') && 
        stat.hasOwnProperty('label') &&
        stat.hasOwnProperty('icon')
      )
    }
  },
  columns: {
    type: [Number, String],
    default: 'auto',
    validator: (value) => {
      if (typeof value === 'string') {
        return ['auto', '1', '2', '3', '4', '5', '6'].includes(value)
      }
      return typeof value === 'number' && value >= 1 && value <= 6
    }
  },
  spacing: {
    type: String,
    default: 'normal',
    validator: (value) => ['compact', 'normal', 'spacious'].includes(value)
  }
})

const emit = defineEmits(['stat-click'])

// Configuración de columnas
const gridColumns = computed(() => {
  if (props.columns === 'auto') {
    return 'repeat(auto-fit, minmax(250px, 1fr))'
  }
  return `repeat(${props.columns}, 1fr)`
})

// Espaciado
const gridGap = computed(() => {
  const gaps = {
    compact: '12px',
    normal: '20px',
    spacious: '32px'
  }
  return gaps[props.spacing]
})

// Get stat color based on index
const getStatColor = (index) => {
  const colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
  return colors[index % colors.length]
}

// Manejar click en estadística
const handleStatClick = (stat) => {
  emit('stat-click', stat)
}
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: v-bind(gridColumns);
  gap: v-bind(gridGap);
  margin-bottom: 2rem;
}

.cursor-pointer {
  cursor: pointer;
}

/* Responsive */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    gap: 12px;
  }
}
</style>
