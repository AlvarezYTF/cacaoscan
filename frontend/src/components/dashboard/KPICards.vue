<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
    <div 
      v-for="card in cards" 
      :key="card.id"
      class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow duration-200 cursor-pointer"
      @click="handleCardClick(card)"
    >
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-medium text-gray-600">{{ card.label }}</p>
          <p class="text-2xl font-semibold text-gray-900">
            {{ card.value }}{{ card.suffix || '' }}
          </p>
          <p class="text-xs mt-1" :class="getChangeColorClass(card.change)">
            <span class="inline-flex items-center">
              <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path :d="getChangeIconPath(card.change)" :fill-rule="card.fillRule" :clip-rule="card.clipRule"></path>
              </svg>
              {{ formatChangeText(card.change, card.changePeriod) }}
            </span>
          </p>
        </div>
        <div class="p-3 rounded-full" :class="getIconBgClass(card.variant)">
          <svg class="w-6 h-6" :class="getIconColorClass(card.variant)" fill="currentColor" viewBox="0 0 20 20">
            <path :d="card.iconPath" :fill-rule="card.fillRule" :clip-rule="card.clipRule"></path>
          </svg>
        </div>
      </div>
      
      <!-- Trend indicator (optional) -->
      <div v-if="card.trend && card.trend.data" class="mt-3">
        <div class="flex items-center justify-between text-xs text-gray-500">
          <span>Tendencia</span>
          <span class="flex items-center">
            <svg class="w-3 h-3 mr-1" :class="getTrendColorClass(card.trend.direction)" fill="currentColor" viewBox="0 0 20 20">
              <path :d="getTrendIconPath(card.trend.direction)" fill-rule="evenodd" clip-rule="evenodd"></path>
            </svg>
            {{ card.trend.direction === 'up' ? 'Subiendo' : card.trend.direction === 'down' ? 'Bajando' : 'Estable' }}
          </span>
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
        'primary': 'bg-blue-50',
        'success': 'bg-green-50',
        'info': 'bg-indigo-50',
        'warning': 'bg-amber-50',
        'danger': 'bg-red-50',
        'secondary': 'bg-gray-50'
      }
      return classes[variant] || 'bg-gray-50'
    }

    const getIconColorClass = (variant) => {
      const classes = {
        'primary': 'text-blue-600',
        'success': 'text-green-600',
        'info': 'text-indigo-600',
        'warning': 'text-amber-600',
        'danger': 'text-red-600',
        'secondary': 'text-gray-600'
      }
      return classes[variant] || 'text-gray-600'
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
/* Hover effects */
.cursor-pointer:hover {
  transform: translateY(-1px);
}

/* Smooth transitions */
.transition-shadow {
  transition: box-shadow 0.2s ease-in-out;
}

/* Icon animations */
svg {
  transition: transform 0.2s ease-in-out;
}

.cursor-pointer:hover svg {
  transform: scale(1.05);
}
</style>
