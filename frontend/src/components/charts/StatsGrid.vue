<template>
  <div class="stats-grid">
    <div 
      v-for="(stat, index) in stats" 
      :key="index"
      class="stat-card"
      :class="stat.variant || 'default'"
      @click="stat.clickable ? handleStatClick(stat) : null"
    >
      <div class="stat-icon">
        <i :class="stat.icon"></i>
      </div>
      <div class="stat-content">
        <div class="stat-value">
          <span class="stat-number">{{ formatValue(stat.value) }}</span>
          <span v-if="stat.suffix" class="stat-suffix">{{ stat.suffix }}</span>
        </div>
        <div class="stat-label">{{ stat.label }}</div>
        <div v-if="stat.change !== undefined" class="stat-change" :class="getChangeClass(stat.change)">
          <i :class="getChangeIcon(stat.change)"></i>
          <span>{{ formatChange(stat.change) }}</span>
          <span v-if="stat.changePeriod" class="change-period">{{ stat.changePeriod }}</span>
        </div>
        <div v-if="stat.description" class="stat-description">
          {{ stat.description }}
        </div>
      </div>
      <div v-if="stat.trend" class="stat-trend">
        <TrendChart 
          :data="stat.trend.data" 
          :color="stat.trend.color || getStatColor(index)"
          :height="40"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import TrendChart from './TrendChart.vue'

export default {
  name: 'StatsGrid',
  components: {
    TrendChart
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
    },
    clickable: {
      type: Boolean,
      default: false
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

    // Colores por defecto para las estadísticas
    const getStatColor = (index) => {
      const colors = [
        '#3498db', '#e74c3c', '#2ecc71', '#f39c12', 
        '#9b59b6', '#1abc9c', '#34495e', '#e67e22'
      ]
      return colors[index % colors.length]
    }

    // Formatear valores
    const formatValue = (value) => {
      if (typeof value === 'number') {
        if (value >= 1000000) {
          return (value / 1000000).toFixed(1) + 'M'
        } else if (value >= 1000) {
          return (value / 1000).toFixed(1) + 'K'
        }
        return value.toLocaleString()
      }
      return value
    }

    // Formatear cambios
    const formatChange = (change) => {
      if (typeof change === 'number') {
        const sign = change >= 0 ? '+' : ''
        return `${sign}${change.toFixed(1)}%`
      }
      return change
    }

    // Clase CSS para cambios
    const getChangeClass = (change) => {
      if (typeof change === 'number') {
        if (change > 0) return 'positive'
        if (change < 0) return 'negative'
        return 'neutral'
      }
      return 'neutral'
    }

    // Icono para cambios
    const getChangeIcon = (change) => {
      if (typeof change === 'number') {
        if (change > 0) return 'fas fa-arrow-up'
        if (change < 0) return 'fas fa-arrow-down'
        return 'fas fa-minus'
      }
      return 'fas fa-minus'
    }

    // Manejar click en estadística
    const handleStatClick = (stat) => {
      emit('stat-click', stat)
    }

    return {
      gridColumns,
      gridGap,
      getStatColor,
      formatValue,
      formatChange,
      getChangeClass,
      getChangeIcon,
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

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  animation: fadeInUp 0.6s ease-out;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.stat-card.clickable {
  cursor: pointer;
}

.stat-card.clickable:hover {
  border-color: #3b82f6;
}

/* Variantes de tarjetas */
.stat-card.primary {
  background: linear-gradient(135deg, #1f4e79 0%, #31235d 100%);
  color: #ffffff;
  border: none;
}

.stat-card.success {
  background: linear-gradient(135deg, #0d5c3d 0%, #0b3f2b 100%);
  color: #ffffff;
  border: none;
}

.stat-card.warning {
  background: linear-gradient(135deg, #8a4b00 0%, #5c3200 100%);
  color: #ffffff;
  border: none;
}

.stat-card.danger {
  background: linear-gradient(135deg, #8b1f1f 0%, #5a1212 100%);
  color: #ffffff;
  border: none;
}

.stat-card.info {
  background: linear-gradient(135deg, #145057 0%, #0b3744 100%);
  color: #ffffff;
  border: none;
}

.stat-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: #1f2937;
  background: rgba(255, 255, 255, 0.9);
}

.stat-card.primary .stat-icon,
.stat-card.success .stat-icon,
.stat-card.danger .stat-icon,
.stat-card.warning .stat-icon,
.stat-card.info .stat-icon {
  background: rgba(255, 255, 255, 0.85);
  color: #1f2937;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-value {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 4px;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  color: #1f2937;
}

.stat-card.primary .stat-number,
.stat-card.success .stat-number,
.stat-card.danger .stat-number,
.stat-card.warning .stat-number,
.stat-card.info .stat-number {
  color: #ffffff;
}

.stat-suffix {
  font-size: 1rem;
  font-weight: 500;
  color: #6b7280;
}

.stat-card.primary .stat-suffix,
.stat-card.success .stat-suffix,
.stat-card.danger .stat-suffix,
.stat-card.warning .stat-suffix,
.stat-card.info .stat-suffix {
  color: rgba(255, 255, 255, 0.95);
}

.stat-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 8px;
}

.stat-card.primary .stat-label,
.stat-card.success .stat-label,
.stat-card.danger .stat-label,
.stat-card.warning .stat-label,
.stat-card.info .stat-label {
  color: rgba(255, 255, 255, 0.95);
}

.stat-change {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 4px;
}

.stat-change.positive {
  color: #059669;
}

.stat-change.negative {
  color: #dc2626;
}

.stat-change.neutral {
  color: #6b7280;
}

.stat-card.primary .stat-change,
.stat-card.success .stat-change,
.stat-card.danger .stat-change,
.stat-card.warning .stat-change,
.stat-card.info .stat-change {
  color: rgba(255, 255, 255, 0.95);
}

.change-period {
  font-weight: 400;
  opacity: 0.8;
}

.stat-description {
  font-size: 0.75rem;
  color: #9ca3af;
  line-height: 1.4;
}

.stat-card.primary .stat-description,
.stat-card.success .stat-description,
.stat-card.danger .stat-description,
.stat-card.warning .stat-description,
.stat-card.info .stat-description {
  color: rgba(255, 255, 255, 0.9);
}

.stat-trend {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 60px;
  height: 40px;
  opacity: 0.7;
}

/* Responsive */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .stat-card {
    padding: 20px;
  }
  
  .stat-number {
    font-size: 1.75rem;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 1.25rem;
  }
}

@media (max-width: 480px) {
  .stat-card {
    padding: 16px;
    flex-direction: column;
    text-align: center;
  }
  
  .stat-icon {
    align-self: center;
  }
  
  .stat-trend {
    position: static;
    margin-top: 12px;
    align-self: center;
  }
}

/* Animaciones */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}


.stat-card:nth-child(1) { animation-delay: 0.1s; }
.stat-card:nth-child(2) { animation-delay: 0.2s; }
.stat-card:nth-child(3) { animation-delay: 0.3s; }
.stat-card:nth-child(4) { animation-delay: 0.4s; }
.stat-card:nth-child(5) { animation-delay: 0.5s; }
.stat-card:nth-child(6) { animation-delay: 0.6s; }
</style>
