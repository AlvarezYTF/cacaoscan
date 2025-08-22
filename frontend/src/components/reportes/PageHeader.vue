<template>
  <header class="bg-white shadow-sm mb-4 md:mb-6">
    <div class="px-3 sm:px-4 lg:px-8 py-4 md:py-6">
      <div class="flex flex-col sm:flex-row sm:items-center space-y-3 sm:space-y-0">
        <!-- Icono y título -->
        <div class="flex items-center">
          <svg class="h-6 w-6 md:h-8 md:w-8 mr-2 md:mr-3 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
          <div class="min-w-0 flex-1">
            <h1 class="text-lg md:text-2xl lg:text-3xl font-bold text-gray-800 truncate">{{ title }}</h1>
            <p class="text-xs md:text-sm lg:text-base text-gray-600 truncate">{{ subtitle }}</p>
          </div>
        </div>
        
        <!-- Acciones adicionales (opcional) -->
        <div class="flex-shrink-0">
          <slot name="actions"></slot>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
export default {
  name: 'PageHeader',
  props: {
    title: {
      type: String,
      required: true
    },
    subtitle: {
      type: String,
      default: ''
    }
  }
};
</script>

<style scoped>
/* Mejoras de responsividad para el header */
@media (max-width: 640px) {
  .px-3 {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .py-4 {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
  }
}

@media (max-width: 480px) {
  .text-lg {
    font-size: 1.125rem;
    line-height: 1.75rem;
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
  header {
    min-height: 60px;
  }
}

/* Animación de entrada */
@keyframes slideInFromTop {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

header {
  animation: slideInFromTop 0.3s ease-out;
}

/* Responsive para pantallas muy grandes */
@media (min-width: 1280px) {
  .lg\:px-8 {
    padding-left: 3rem;
    padding-right: 3rem;
  }
  
  .lg\:py-6 {
    padding-top: 2rem;
    padding-bottom: 2rem;
  }
}

/* Mejoras para orientación landscape en móviles */
@media (max-width: 768px) and (orientation: landscape) {
  .py-4 {
    padding-top: 1rem;
    padding-bottom: 1rem;
  }
  
  .mb-4 {
    margin-bottom: 1rem;
  }
}
</style>
