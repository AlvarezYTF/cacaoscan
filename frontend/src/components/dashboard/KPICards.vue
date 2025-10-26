<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <div 
      v-for="card in cards" 
      :key="card.id"
      class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md hover:border-green-200 transition-all duration-200 cursor-pointer group"
      @click="handleCardClick(card)"
    >
      <div class="flex items-center justify-between">
        <div class="flex-1">
          <p class="text-sm font-medium text-gray-600 mb-1">{{ card.label }}</p>
          <p class="text-3xl font-bold text-gray-900 mb-2">
            {{ card.value }}{{ card.suffix || '' }}
          </p>
          <div class="flex items-center" :class="getChangeColorClass(card.change)">
            <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path :d="getChangeIconPath(card.change)" :fill-rule="card.fillRule" :clip-rule="card.clipRule"></path>
            </svg>
            <span class="text-sm font-medium">
              {{ formatChangeText(card.change, card.changePeriod) }}
            </span>
          </div>
        </div>
        <div class="p-3 rounded-lg bg-green-50 group-hover:bg-green-100 transition-colors duration-200">
          <svg class="w-7 h-7 text-green-600 group-hover:text-green-700 transition-colors duration-200" fill="currentColor" viewBox="0 0 20 20">
            <path :d="card.iconPath" :fill-rule="card.fillRule" :clip-rule="card.clipRule"></path>
          </svg>
        </div>
      </div>
      
      <!-- Trend indicator (optional) -->
      <div v-if="card.trend && card.trend.data" class="mt-4 pt-3 border-t border-gray-100">
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-gray-500">Tendencia</span>
          <div class="flex items-center" :class="getTrendColorClass(card.trend.direction)">
            <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path :d="getTrendIconPath(card.trend.direction)" fill-rule="evenodd" clip-rule="evenodd"></path>
            </svg>
            <span class="text-xs font-medium">
              {{ card.trend.direction === 'up' ? 'Subiendo' : card.trend.direction === 'down' ? 'Bajando' : 'Estable' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'KPICards',
  props: {
    cards: {
      type: Array,
      required: true,
      default: () => []
    }
  },
  emits: ['card-click'],
  setup(props, { emit }) {
    // Methods
    const handleCardClick = (card) => {
      emit('card-click', card)
    }

    const getChangeColorClass = (change) => {
      if (change > 0) return 'text-green-600'
      if (change < 0) return 'text-red-600'
      return 'text-gray-600'
    }

    const getChangeIconPath = (change) => {
      if (change > 0) {
        return 'M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z'
      }
      if (change < 0) {
        return 'M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z'
      }
      return 'M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z'
    }

    const formatChangeText = (change, period) => {
      if (change > 0) {
        return `+${change} ${period || 'hoy'}`
      }
      if (change < 0) {
        return `${change} ${period || 'hoy'}`
      }
      return `Sin cambios ${period || 'hoy'}`
    }

    const getIconBgClass = (variant) => {
      const classes = {
        'primary': 'bg-green-50',
        'success': 'bg-green-50',
        'info': 'bg-green-50',
        'warning': 'bg-amber-50',
        'danger': 'bg-red-50',
        'secondary': 'bg-gray-50'
      }
      return classes[variant] || 'bg-green-50'
    }

    const getIconColorClass = (variant) => {
      const classes = {
        'primary': 'text-green-600',
        'success': 'text-green-600',
        'info': 'text-green-600',
        'warning': 'text-amber-600',
        'danger': 'text-red-600',
        'secondary': 'text-gray-600'
      }
      return classes[variant] || 'text-green-600'
    }

    const getTrendColorClass = (direction) => {
      const classes = {
        'up': 'text-green-500',
        'down': 'text-red-500',
        'stable': 'text-gray-500'
      }
      return classes[direction] || 'text-gray-500'
    }

    const getTrendIconPath = (direction) => {
      const paths = {
        'up': 'M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z',
        'down': 'M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z',
        'stable': 'M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z'
      }
      return paths[direction] || paths.stable
    }

    return {
      handleCardClick,
      getChangeColorClass,
      getChangeIconPath,
      formatChangeText,
      getIconBgClass,
      getIconColorClass,
      getTrendColorClass,
      getTrendIconPath
    }
  }
}
</script>

<style scoped>
/* Hover effects mejorados */
.group:hover {
  transform: translateY(-2px);
}

/* Transiciones suaves */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

/* Animaciones de iconos */
.group:hover svg {
  transform: scale(1.05);
}

svg {
  transition: transform 0.2s ease-in-out;
}

/* Mejoras de accesibilidad */
.group:focus-visible {
  outline: 2px solid rgb(34 197 94);
  outline-offset: 2px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .group:hover {
    transform: none;
  }
}

/* Estilos para elementos de estado */
.text-green-600 {
  color: rgb(34 197 94);
}

.text-red-600 {
  color: rgb(220 38 38);
}

.text-gray-600 {
  color: rgb(75 85 99);
}
</style>
