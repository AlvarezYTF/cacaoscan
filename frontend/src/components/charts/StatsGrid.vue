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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.stat-card.success {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border: none;
}

.stat-card.warning {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  color: white;
  border: none;
}

.stat-card.danger {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
  color: white;
  border: none;
}

.stat-card.info {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: #374151;
  border: none;
}

.stat-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
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
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card.primary .stat-icon {
  background: rgba(255, 255, 255, 0.2);
}

.stat-card.success .stat-icon {
  background: rgba(255, 255, 255, 0.2);
}

.stat-card.warning .stat-icon {
  background: rgba(255, 255, 255, 0.2);
}

.stat-card.danger .stat-icon {
  background: rgba(255, 255, 255, 0.2);
}

.stat-card.info .stat-icon {
  background: rgba(255, 255, 255, 0.2);
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
.stat-card.warning .stat-number,
.stat-card.danger .stat-number {
  color: white;
}

.stat-suffix {
  font-size: 1rem;
  font-weight: 500;
  color: #6b7280;
}

.stat-card.primary .stat-suffix,
.stat-card.success .stat-suffix,
.stat-card.warning .stat-suffix,
.stat-card.danger .stat-suffix {
  color: rgba(255, 255, 255, 0.8);
}

.stat-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 8px;
}

.stat-card.primary .stat-label,
.stat-card.success .stat-label,
.stat-card.warning .stat-label,
.stat-card.danger .stat-label {
  color: rgba(255, 255, 255, 0.9);
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
.stat-card.warning .stat-change,
.stat-card.danger .stat-change {
  color: rgba(255, 255, 255, 0.9);
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
.stat-card.warning .stat-description,
.stat-card.danger .stat-description {
  color: rgba(255, 255, 255, 0.7);
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

.stat-card {
  animation: fadeInUp 0.6s ease-out;
}

.stat-card:nth-child(1) { animation-delay: 0.1s; }
.stat-card:nth-child(2) { animation-delay: 0.2s; }
.stat-card:nth-child(3) { animation-delay: 0.3s; }
.stat-card:nth-child(4) { animation-delay: 0.4s; }
.stat-card:nth-child(5) { animation-delay: 0.5s; }
.stat-card:nth-child(6) { animation-delay: 0.6s; }
</style>
