<template>
  <!-- Header fijo adaptado al diseño profesional de LandingView: paleta verde, animaciones suaves, bordes redondeados -->
  <header class="sticky top-0 z-50 bg-white/95 backdrop-blur-sm shadow-md border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-20 items-center">
        <!-- Logo y nombre con efecto hover mejorado -->
        <div class="flex-shrink-0 flex items-center group cursor-pointer">
          <div class="w-10 h-10 bg-green-500 rounded-xl flex items-center justify-center mr-3 group-hover:scale-110 group-hover:bg-green-600 transition-all duration-200 shadow-md hover:shadow-lg">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-green-600 group-hover:text-green-700 transition-colors duration-200">
            {{ configStore.brandName }}
          </h1>
        </div>

        <!-- Navegación principal con estilos consistentes con LandingView -->
        <nav class="hidden md:ml-6 md:flex items-center space-x-2">
          <a 
            href="#" 
            class="relative px-4 py-2 text-sm font-medium text-gray-900 hover:text-green-600 transition-all duration-200 rounded-lg hover:bg-green-50 hover:scale-[1.02]"
          >
            Inicio
          </a>
          <a 
            href="#features" 
            class="relative px-4 py-2 text-sm font-medium text-gray-700 hover:text-green-600 transition-all duration-200 rounded-lg hover:bg-green-50 hover:scale-[1.02]"
          >
            Funcionalidades
          </a>
          <a 
            href="#about" 
            class="relative px-4 py-2 text-sm font-medium text-gray-700 hover:text-green-600 transition-all duration-200 rounded-lg hover:bg-green-50 hover:scale-[1.02]"
          >
            Sobre el sistema
          </a>
          <!-- Botón CTA destacado con estilo consistente (green-500, hover:green-600) -->
          <a 
            href="/login" 
            class="ml-4 inline-flex items-center justify-center gap-2 px-6 py-2 bg-green-500 hover:bg-green-600 text-white text-sm font-semibold rounded-lg shadow-md hover:shadow-lg transition-all duration-200 hover:scale-[1.02] focus:ring-4 focus:ring-green-300"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
            </svg>
            Acceder
          </a>
        </nav>

        <!-- Botón de menú móvil con estilo mejorado -->
        <button 
          class="md:hidden p-2 text-gray-700 hover:text-green-600 hover:bg-green-50 rounded-lg transition-all duration-200 hover:scale-110 focus:ring-4 focus:ring-green-300"
          aria-label="Menú móvil"
        >
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useConfigStore } from '@/stores/config'

const configStore = useConfigStore()
</script>
