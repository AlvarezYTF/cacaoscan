<template>
  <!-- KPI Cards con diseño profesional mejorado -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <div 
      v-for="(card, index) in cards" 
      :key="card.id"
      class="relative bg-white rounded-2xl border-2 border-gray-200 p-6 hover:shadow-xl hover:border-green-300 transition-all duration-300 cursor-pointer group animate-slide-up"
      :style="{ animationDelay: `${index * 50}ms` }"
      @click="handleCardClick(card)"
    >
      <!-- Indicador decorativo superior -->
      <div class="absolute top-0 right-0 w-20 h-1 bg-gradient-to-l from-green-500 to-transparent rounded-t-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
      
      <div class="flex items-center justify-between">
        <div class="flex-1">
          <!-- Label con badge -->
          <div class="flex items-center gap-2 mb-2">
            <p class="text-sm font-semibold text-gray-500 uppercase tracking-wide">{{ card.label }}</p>
          </div>
          
          <!-- Valor principal destacado -->
          <p class="text-4xl font-bold text-gray-900 mb-3 group-hover:text-green-600 transition-colors duration-300">
            {{ formatValue(card.value) }}{{ card.suffix || '' }}
          </p>
          
          <!-- Indicador de cambio con mejor diseño -->
          <div class="flex items-center gap-2 px-3 py-1.5 rounded-full" :class="getChangeBgClass(card.change)">
            <svg class="w-4 h-4" :class="getChangeColorClass(card.change)" fill="currentColor" viewBox="0 0 20 20">
              <path :d="getChangeIconPath(card.change)" :fill-rule="card.fillRule" :clip-rule="card.clipRule"></path>
            </svg>
            <span class="text-sm font-semibold" :class="getChangeColorClass(card.change)">
              {{ formatChangeText(card.change, card.changePeriod) }}
            </span>
          </div>
        </div>
        
        <!-- Ícono con efecto 3D mejorado -->
        <div class="relative ml-4">
          <div class="absolute inset-0 bg-green-400 rounded-2xl transform rotate-3 opacity-20 group-hover:rotate-6 group-hover:scale-110 transition-transform duration-300"></div>
          <div class="relative p-4 rounded-2xl bg-gradient-to-br from-green-50 to-green-100 group-hover:from-green-100 group-hover:to-green-200 transition-all duration-300 shadow-md group-hover:shadow-lg">
            <svg class="w-8 h-8 text-green-600 group-hover:text-green-700 group-hover:scale-110 transition-all duration-300" fill="currentColor" viewBox="0 0 20 20">
              <path :d="card.iconPath" :fill-rule="card.fillRule" :clip-rule="card.clipRule"></path>
            </svg>
          </div>
        </div>
      </div>
      
      <!-- Indicador de tendencia mejorado -->
      <div v-if="card.trend && card.trend.data" class="mt-5 pt-4 border-t-2 border-gray-100">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-gray-400 uppercase tracking-wide">Tendencia</span>
          <div class="flex items-center gap-2 px-2.5 py-1 rounded-full" :class="getTrendBgClass(card.trend.direction)">
            <svg class="w-3 h-3" :class="getTrendColorClass(card.trend.direction)" fill="currentColor" viewBox="0 0 20 20">
              <path :d="getTrendIconPath(card.trend.direction)" fill-rule="evenodd" clip-rule="evenodd"></path>
            </svg>
            <span class="text-xs font-bold" :class="getTrendColorClass(card.trend.direction)">
              {{ card.trend.direction === 'up' ? 'Subiendo' : card.trend.direction === 'down' ? 'Bajando' : 'Estable' }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- Flecha de navegación en hover -->
      <div class="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transform translate-x-2 group-hover:translate-x-0 transition-all duration-300">
        <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
        </svg>
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

    const formatValue = (value) => {
      if (typeof value === 'number') {
        return value.toLocaleString('es-ES')
      }
      return value
    }

    const getChangeBgClass = (change) => {
      if (change > 0) return 'bg-green-50'
      if (change < 0) return 'bg-red-50'
      return 'bg-gray-50'
    }

    const getTrendBgClass = (direction) => {
      const classes = {
        'up': 'bg-green-50',
        'down': 'bg-red-50',
        'stable': 'bg-gray-50'
      }
      return classes[direction] || classes.stable
    }

    return {
      handleCardClick,
      getChangeColorClass,
      getChangeIconPath,
      formatChangeText,
      getIconBgClass,
      getIconColorClass,
      getTrendColorClass,
      getTrendIconPath,
      formatValue,
      getChangeBgClass,
      getTrendBgClass
    }
  }
}
</script>

<style scoped>
/* Animación de entrada para las cards */
@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-slide-up {
  animation: slide-up 0.5s ease-out both;
}

/* Hover effects mejorados */
.group:hover {
  transform: translateY(-4px);
}

/* Transiciones suaves */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

/* Animaciones de iconos */
.group:hover svg {
  transform: scale(1.05);
}

svg {
  transition: transform 0.3s ease-in-out;
}

/* Mejoras de accesibilidad */
.group:focus-visible {
  outline: 3px solid rgb(34 197 94);
  outline-offset: 2px;
  border-radius: 1rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .group:hover {
    transform: translateY(-2px);
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

.bg-green-50 {
  background-color: rgb(240 253 244);
}

.bg-red-50 {
  background-color: rgb(254 242 242);
}

.bg-gray-50 {
  background-color: rgb(249 250 251);
}

/* Gradient text effect */
.group:hover .text-gray-900 {
  background: linear-gradient(135deg, rgb(55 65 81), rgb(34 197 94));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>
