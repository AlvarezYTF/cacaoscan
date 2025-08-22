<template>
  <aside class="w-16 md:w-64 bg-gradient-to-b from-green-800 to-green-600 text-white fixed inset-y-0 left-0 z-10 flex flex-col shadow-lg transition-all duration-300">
    <!-- Logo/Brand -->
    <div class="p-4 flex items-center justify-center md:justify-start">
      <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
      </svg>
      <h1 class="text-xl font-bold text-white tracking-tight ml-3 hidden md:block">Panel Admin</h1>
    </div>
    
    <!-- Navigation -->
    <nav class="mt-8 flex-1">
      <div class="px-2 space-y-1">
        <router-link 
          :to="{name: 'admin-dashboard'}" 
          class="group flex items-center px-2 py-3 text-sm font-medium rounded-md hover:bg-green-700 transition-all duration-200 transform hover:scale-105" 
          :class="{'bg-green-700': $route.name === 'admin-dashboard'}"
        >
          <svg class="w-6 h-6 mr-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
          </svg>
          <span class="hidden md:block">Inicio</span>
        </router-link>
        
        <router-link 
          :to="{name: 'agricultores'}" 
          class="group flex items-center px-2 py-3 text-sm font-medium rounded-md hover:bg-green-700 transition-all duration-200 transform hover:scale-105" 
          :class="{'bg-green-700': $route.name === 'agricultores'}"
        >
          <svg class="w-6 h-6 mr-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
          </svg>
          <span class="hidden md:block">Agricultores</span>
        </router-link>
        
        <router-link 
          :to="{name: 'analisis'}" 
          class="group flex items-center px-2 py-3 text-sm font-medium rounded-md hover:bg-green-700 transition-all duration-200 transform hover:scale-105" 
          :class="{'bg-green-700': $route.name === 'analisis'}"
        >
          <svg class="w-6 h-6 mr-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
          </svg>
          <span class="hidden md:block">Análisis</span>
        </router-link>
        
        <router-link 
          :to="{name: 'reportes'}" 
          class="group flex items-center px-2 py-3 text-sm font-medium rounded-md hover:bg-green-700 transition-all duration-200 transform hover:scale-105" 
          :class="{'bg-green-700': $route.name === 'reportes'}"
        >
          <svg class="w-6 h-6 mr-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
          <span class="hidden md:block">Reportes</span>
        </router-link>
      </div>
    </nav>
    
    <!-- User Profile -->
    <div class="p-4 border-t border-green-700">
      <div class="flex items-center">
        <div class="h-8 w-8 rounded-full bg-white flex items-center justify-center text-green-800 font-bold">
          {{ userInitials }}
        </div>
        <div class="ml-3 hidden md:block">
          <p class="text-sm font-medium text-white">{{ userName }}</p>
          <p class="text-xs text-green-200">{{ userRole }}</p>
        </div>
      </div>
    </div>
  </aside>
</template>

<script>
export default {
  name: 'AdminSidebar',
  props: {
    userInitials: {
      type: String,
      default: 'AD'
    },
    userName: {
      type: String,
      default: 'Admin'
    },
    userRole: {
      type: String,
      default: 'Ver perfil'
    }
  }
};
</script>

<style scoped>
/* Mejoras de responsividad para el sidebar */
@media (max-width: 768px) {
  aside {
    width: 4rem;
  }
  
  /* Tooltips para móviles */
  .group:hover::after {
    content: attr(data-tooltip);
    position: absolute;
    left: 100%;
    top: 50%;
    transform: translateY(-50%);
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 0.5rem;
    border-radius: 0.375rem;
    font-size: 0.75rem;
    white-space: nowrap;
    z-index: 50;
    margin-left: 0.5rem;
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
  .group {
    min-height: 44px;
    min-width: 44px;
  }
}

/* Animaciones de hover */
.group:hover {
  transform: translateX(2px);
}

/* Responsive para pantallas muy pequeñas */
@media (max-width: 480px) {
  aside {
    width: 3.5rem;
  }
  
  .p-4 {
    padding: 0.75rem;
  }
  
  .w-8.h-8 {
    width: 2rem;
    height: 2rem;
  }
}
</style>
