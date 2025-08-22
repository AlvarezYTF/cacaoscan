<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-all duration-300">
    <div class="p-4 md:p-5">
      <div class="flex items-center">
        <div class="flex-shrink-0 rounded-lg p-2 md:p-3" :class="iconBgColor">
          <component :is="icon" class="h-5 w-5 md:h-6 md:w-6" :class="iconColor" />
        </div>
        <div class="ml-3 md:ml-5">
          <dl>
            <dt class="text-xs md:text-sm font-medium text-gray-500 truncate">{{ title }}</dt>
            <dd class="mt-1">
              <div class="text-lg md:text-2xl font-semibold text-gray-900">{{ value }}</div>
              <div v-if="change" class="text-xs md:text-sm flex items-center mt-1" :class="changeColor">
                <svg v-if="change > 0" class="w-3 h-3 md:w-4 md:h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"></path>
                </svg>
                <svg v-else-if="change < 0" class="w-3 h-3 md:w-4 md:h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
                </svg>
                <span>{{ Math.abs(change) }}% desde el mes pasado</span>
              </div>
            </dd>
          </dl>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatsCard',
  props: {
    title: {
      type: String,
      required: true
    },
    value: {
      type: [String, Number],
      required: true
    },
    change: {
      type: Number,
      default: null
    },
    icon: {
      type: String,
      required: true
    },
    variant: {
      type: String,
      default: 'default', // default, success, warning, danger, info
      validator: (value) => ['default', 'success', 'warning', 'danger', 'info'].includes(value)
    }
  },
  computed: {
    iconBgColor() {
      const colors = {
        default: 'bg-gray-50',
        success: 'bg-green-50',
        warning: 'bg-yellow-50',
        danger: 'bg-red-50',
        info: 'bg-blue-50'
      };
      return colors[this.variant] || colors.default;
    },
    iconColor() {
      const colors = {
        default: 'text-gray-600',
        success: 'text-green-600',
        warning: 'text-yellow-600',
        danger: 'text-red-600',
        info: 'text-blue-600'
      };
      return colors[this.variant] || colors.default;
    },
    changeColor() {
      if (!this.change) return '';
      
      if (this.change > 0) {
        return 'text-green-600';
      } else if (this.change < 0) {
        return 'text-red-600';
      } else {
        return 'text-gray-600';
      }
    }
  }
};
</script>

<style scoped>
/* Mejoras de responsividad para tarjetas de estadísticas */
@media (max-width: 768px) {
  .md\:p-5 {
    padding: 1rem;
  }
  
  .md\:ml-5 {
    margin-left: 0.75rem;
  }
  
  .md\:h-6.md\:w-6 {
    width: 1.25rem;
    height: 1.25rem;
  }
  
  .md\:text-2xl {
    font-size: 1.5rem;
    line-height: 2rem;
  }
}

@media (max-width: 640px) {
  .p-4 {
    padding: 0.75rem;
  }
  
  .ml-3 {
    margin-left: 0.5rem;
  }
  
  .text-lg {
    font-size: 1.125rem;
    line-height: 1.75rem;
  }
  
  .text-xs {
    font-size: 0.75rem;
    line-height: 1rem;
  }
}

@media (max-width: 480px) {
  .p-4 {
    padding: 0.5rem;
  }
  
  .ml-3 {
    margin-left: 0.375rem;
  }
  
  .rounded-xl {
    border-radius: 0.5rem;
  }
}

/* Transiciones suaves */
* {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

/* Mejoras para dispositivos táctiles */
@media (hover: none) and (pointer: coarse) {
  .bg-white {
    min-height: 80px;
  }
}

/* Efectos de hover mejorados */
.hover\:shadow-md:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

/* Animación de entrada */
@keyframes slideInFromBottom {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.bg-white {
  animation: slideInFromBottom 0.4s ease-out;
}

/* Responsive para pantallas muy grandes */
@media (min-width: 1280px) {
  .lg\:p-6 {
    padding: 1.5rem;
  }
  
  .lg\:text-3xl {
    font-size: 1.875rem;
    line-height: 2.25rem;
  }
}

/* Mejoras para orientación landscape en móviles */
@media (max-width: 768px) and (orientation: landscape) {
  .p-4 {
    padding: 0.75rem;
  }
  
  .text-lg {
    font-size: 1rem;
    line-height: 1.5rem;
  }
}

/* Estados de carga */
.loading .bg-white {
  opacity: 0.6;
  pointer-events: none;
}

.loading .bg-white::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 20px;
  height: 20px;
  margin: -10px 0 0 -10px;
  border: 2px solid transparent;
  border-top-color: #9ca3af;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Mejoras para accesibilidad */
.bg-white:focus-within {
  outline: 2px solid #10b981;
  outline-offset: 2px;
}

/* Variantes de color responsivas */
@media (max-width: 640px) {
  .bg-green-50 {
    background-color: #f0fdf4;
  }
  
  .bg-yellow-50 {
    background-color: #fefce8;
  }
  
  .bg-red-50 {
    background-color: #fef2f2;
  }
  
  .bg-blue-50 {
    background-color: #eff6ff;
  }
  
  .bg-gray-50 {
    background-color: #f9fafb;
  }
}
</style>
