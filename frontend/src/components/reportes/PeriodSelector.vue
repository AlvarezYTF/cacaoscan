<template>
  <div class="relative w-full sm:w-auto">
    <select 
      :value="modelValue"
      @change="$emit('update:modelValue', $event.target.value)"
      class="w-full sm:w-auto pl-9 pr-4 py-2 border border-gray-300 rounded-md text-xs md:text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 appearance-none transition-all duration-200 bg-white shadow-sm hover:shadow-md"
    >
      <option v-for="option in options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
      <svg class="h-4 w-4 md:h-5 md:w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
      </svg>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PeriodSelector',
  props: {
    modelValue: {
      type: String,
      default: 'last-month'
    },
    options: {
      type: Array,
      default: () => [
        { value: 'last-month', label: 'Último mes' },
        { value: 'last-3-months', label: 'Últimos 3 meses' },
        { value: 'last-year', label: 'Último año' },
        { value: 'custom', label: 'Personalizado' }
      ]
    }
  },
  emits: ['update:modelValue']
};
</script>

<style scoped>
/* Mejoras de responsividad para el selector de período */
@media (max-width: 640px) {
  .w-full {
    width: 100%;
  }
  
  .py-2 {
    padding-top: 0.75rem;
    padding-bottom: 0.75rem;
  }
  
  .text-xs {
    font-size: 0.75rem;
    line-height: 1rem;
  }
}

@media (max-width: 480px) {
  .pl-9 {
    padding-left: 2.5rem;
  }
  
  .pr-4 {
    padding-right: 1rem;
  }
  
  .rounded-md {
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
  select {
    min-height: 44px;
    font-size: 16px; /* Previene zoom en iOS */
  }
}

/* Efectos de hover y focus mejorados */
select:hover {
  border-color: #10b981;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

select:focus {
  transform: translateY(-1px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

/* Animación de entrada */
@keyframes slideInFromLeft {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.relative {
  animation: slideInFromLeft 0.3s ease-out;
}

/* Responsive para pantallas muy grandes */
@media (min-width: 1280px) {
  .sm\:w-auto {
    width: auto;
  }
}

/* Mejoras para orientación landscape en móviles */
@media (max-width: 768px) and (orientation: landscape) {
  .py-2 {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
}

/* Mejoras para accesibilidad */
select:focus-visible {
  outline: 2px solid #10b981;
  outline-offset: 2px;
}
</style>
