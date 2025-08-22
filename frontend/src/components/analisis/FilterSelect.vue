<template>
  <div class="w-full">
    <label :for="id" class="block text-xs sm:text-sm md:text-base font-medium text-gray-700 mb-1 sm:mb-2">{{ label }}</label>
    <div class="relative">
      <select 
        :id="id"
        :value="modelValue"
        @change="$emit('update:modelValue', $event.target.value)"
        class="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-xs sm:text-sm md:text-base transition-all duration-200"
        :class="{
          'py-2 px-3': size === 'small',
          'py-2.5 px-3 md:py-3 md:px-4': size === 'medium',
          'py-3 px-4 md:py-4 md:px-5': size === 'large'
        }"
      >
        <option v-for="option in options" :key="option.value" :value="option.value">
          {{ option.label }}
        </option>
      </select>
      
      <!-- Icono de flecha personalizado -->
      <div class="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
        <svg class="h-4 w-4 md:h-5 md:w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
        </svg>
      </div>
    </div>
    
    <!-- Mensaje de error (opcional) -->
    <p v-if="error" class="mt-1 text-xs text-red-600">{{ error }}</p>
    
    <!-- Mensaje de ayuda (opcional) -->
    <p v-if="helpText" class="mt-1 text-xs text-gray-500">{{ helpText }}</p>
  </div>
</template>

<script>
export default {
  name: 'FilterSelect',
  props: {
    id: {
      type: String,
      required: true
    },
    label: {
      type: String,
      required: true
    },
    modelValue: {
      type: String,
      default: ''
    },
    options: {
      type: Array,
      required: true,
      validator: (value) => value.every(option => 'value' in option && 'label' in option)
    },
    size: {
      type: String,
      default: 'medium', // small, medium, large
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    },
    error: {
      type: String,
      default: ''
    },
    helpText: {
      type: String,
      default: ''
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue']
};
</script>

<style scoped>
/* Mejoras de responsividad para selectores */
@media (max-width: 640px) {
  .text-xs {
    font-size: 0.75rem;
    line-height: 1rem;
  }
  
  .mb-1 {
    margin-bottom: 0.25rem;
  }
  
  .py-2\.5 {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
  
  .px-3 {
    padding-left: 0.75rem;
    padding-right: 0.75rem;
  }
}

@media (max-width: 480px) {
  .py-2 {
    padding-top: 0.375rem;
    padding-bottom: 0.375rem;
  }
  
  .px-3 {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
  }
  
  .rounded-md {
    border-radius: 0.375rem;
  }
  
  .text-xs {
    font-size: 0.75rem;
    line-height: 1rem;
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
  select {
    min-height: 44px;
    font-size: 16px; /* Previene zoom en iOS */
  }
  
  label {
    min-height: 20px;
  }
}

/* Efectos de hover y focus mejorados */
select:hover {
  border-color: #9ca3af;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

select:focus {
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

/* Animación de entrada */
@keyframes slideInFromTop {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.w-full {
  animation: slideInFromTop 0.3s ease-out;
}

/* Responsive para pantallas muy grandes */
@media (min-width: 1280px) {
  .md\:text-base {
    font-size: 1rem;
    line-height: 1.5rem;
  }
  
  .md\:py-4 {
    padding-top: 1rem;
    padding-bottom: 1rem;
  }
  
  .md\:px-5 {
    padding-left: 1.25rem;
    padding-right: 1.25rem;
  }
}

/* Mejoras para orientación landscape en móviles */
@media (max-width: 768px) and (orientation: landscape) {
  .py-2\.5 {
    padding-top: 0.375rem;
    padding-bottom: 0.375rem;
  }
  
  .mb-1 {
    margin-bottom: 0.125rem;
  }
}

/* Responsive para diferentes tamaños */
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

/* Mejoras para accesibilidad */
select:focus-visible {
  outline: 2px solid #10b981;
  outline-offset: 2px;
}
</style>
