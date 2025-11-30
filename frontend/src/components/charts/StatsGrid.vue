<template>
  <div class="stats-grid">
    <BaseStatsCard
      v-for="(stat, index) in stats"
      :key="stat.id || index"
      :stat="stat"
      :index="index"
      @stat-click="handleStatClick"
    />
  </div>
</template>

<script>
import { computed } from 'vue'
import BaseStatsCard from '@/components/common/BaseStatsCard.vue'

export default {
  name: 'StatsGrid',
  components: {
    BaseStatsCard
  },
  props: {
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
  },
  emits: ['stat-click'],
  setup(props, { emit }) {
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

    // Manejar click en estadística
    const handleStatClick = (stat) => {
      emit('stat-click', stat)
    }

    return {
      gridColumns,
      gridGap,
      handleStatClick
    }
  }
}
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: v-bind(gridColumns);
  gap: v-bind(gridGap);
  margin-bottom: 2rem;
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
