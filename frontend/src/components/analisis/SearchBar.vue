<template>
  <div class="relative w-full">
    <input 
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      type="text" 
      :placeholder="placeholder" 
      class="w-full sm:w-64 lg:w-80 xl:w-96 pl-9 pr-4 py-2 md:py-3 border border-gray-300 rounded-md text-sm md:text-base focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all duration-200 bg-white shadow-sm hover:shadow-md" 
    />
    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
      <svg class="h-4 w-4 md:h-5 md:w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
      </svg>
    </div>
    
    <!-- Botón de limpiar (opcional) -->
    <button 
      v-if="modelValue && showClearButton"
      @click="$emit('update:modelValue', '')"
      class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 transition-colors duration-200"
    >
      <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
      </svg>
    </button>
  </div>
</template>

<script>
export default {
  name: 'SearchBar',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: 'Buscar análisis...'
    },
    showClearButton: {
      type: Boolean,
      default: true
    }
  },
  emits: ['update:modelValue']
};
</script>

<style scoped>
/* Mejoras de responsividad para la barra de búsqueda */
@media (max-width: 640px) {
  .sm\:w-64 {
    width: 100%;
  }
  
  .py-2 {
    padding-top: 0.75rem;
    padding-bottom: 0.75rem;
  }
  
  .text-sm {
    font-size: 0.875rem;
    line-height: 1.25rem;
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
  input {
    min-height: 44px;
    font-size: 16px; /* Previene zoom en iOS */
  }
  
  button {
    min-height: 44px;
    min-width: 44px;
  }
}

/* Efectos de hover y focus mejorados */
input:hover {
  border-color: #10b981;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

input:focus {
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
  .xl\:w-96 {
    width: 24rem;
  }
}

/* Mejoras para orientación landscape en móviles */
@media (max-width: 768px) and (orientation: landscape) {
  .py-2 {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
}

/* Estados de carga (opcional) */
.loading input {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24'%3E%3Cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 1.25rem;
  padding-right: 2.5rem;
}
</style>
