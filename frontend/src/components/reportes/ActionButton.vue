<template>
  <button 
    :class="buttonClasses"
    @click="$emit('click')"
    :disabled="disabled"
    class="px-3 sm:px-4 md:px-6 py-2 md:py-3 rounded-md text-xs sm:text-sm md:text-base font-medium flex items-center justify-center transition-all duration-200 transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
  >
    <component :is="icon" v-if="icon" class="w-3 h-3 sm:w-4 sm:h-4 md:w-5 md:h-5 mr-1 sm:mr-2 flex-shrink-0" />
    <span class="hidden sm:inline">{{ label }}</span>
    <span class="sm:hidden">{{ shortLabel || label }}</span>
  </button>
</template>

<script>
export default {
  name: 'ActionButton',
  props: {
    label: {
      type: String,
      required: true
    },
    shortLabel: {
      type: String,
      default: ''
    },
    variant: {
      type: String,
      default: 'primary', // primary, secondary, danger
      validator: (value) => ['primary', 'secondary', 'danger'].includes(value)
    },
    icon: {
      type: String,
      default: null
    },
    disabled: {
      type: Boolean,
      default: false
    },
    size: {
      type: String,
      default: 'medium', // small, medium, large
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    }
  },
  computed: {
    buttonClasses() {
      const baseClasses = 'font-medium';
      const sizeClasses = {
        small: 'px-2 py-1.5 text-xs',
        medium: 'px-3 sm:px-4 md:px-6 py-2 md:py-3 text-xs sm:text-sm md:text-base',
        large: 'px-4 sm:px-6 md:px-8 py-3 md:py-4 text-sm md:text-base lg:text-lg'
      };
      
      let variantClasses = '';
      switch (this.variant) {
        case 'primary':
          variantClasses = 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500';
          break;
        case 'secondary':
          variantClasses = 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 focus:ring-gray-500';
          break;
        case 'danger':
          variantClasses = 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500';
          break;
        default:
          variantClasses = 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500';
      }
      
      return `${baseClasses} ${sizeClasses[this.size]} ${variantClasses}`;
    }
  },
  emits: ['click']
};
</script>

<style scoped>
/* Mejoras de responsividad para botones */
@media (max-width: 640px) {
  .px-3 {
    padding-left: 0.75rem;
    padding-right: 0.75rem;
  }
  
  .py-2 {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
  
  .text-xs {
    font-size: 0.75rem;
    line-height: 1rem;
  }
}

@media (max-width: 480px) {
  .px-3 {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
  }
  
  .py-2 {
    padding-top: 0.375rem;
    padding-bottom: 0.375rem;
  }
  
  .rounded-md {
    border-radius: 0.375rem;
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
  button {
    min-height: 44px;
    min-width: 44px;
  }
  
  button:active {
    transform: scale(0.95);
  }
}

/* Efectos de hover mejorados */
button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

button:focus:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

/* Estados de carga */
button.loading {
  position: relative;
  color: transparent;
}

button.loading::after {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  top: 50%;
  left: 50%;
  margin-left: -8px;
  margin-top: -8px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Responsive para pantallas muy grandes */
@media (min-width: 1280px) {
  .lg\:text-lg {
    font-size: 1.125rem;
    line-height: 1.75rem;
  }
}

/* Mejoras para orientación landscape en móviles */
@media (max-width: 768px) and (orientation: landscape) {
  .py-2 {
    padding-top: 0.375rem;
    padding-bottom: 0.375rem;
  }
}

/* Variantes de tamaño responsivas */
@media (max-width: 640px) {
  .size-small {
    padding: 0.375rem 0.5rem;
    font-size: 0.75rem;
  }
  
  .size-large {
    padding: 0.75rem 1rem;
    font-size: 0.875rem;
  }
}
</style>
