<template>
  <!-- Hero Section: Primera impresión profesional y atractiva -->
  <section class="bg-green-600 text-white py-24 relative overflow-hidden">
    <!-- Elementos decorativos sutiles -->
    <div class="absolute inset-0 opacity-10">
      <div class="absolute top-0 left-0 w-96 h-96 bg-white rounded-full -translate-x-1/2 -translate-y-1/2 blur-3xl"></div>
      <div class="absolute bottom-0 right-0 w-96 h-96 bg-white rounded-full translate-x-1/2 translate-y-1/2 blur-3xl"></div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
      <!-- Badge de confianza -->
      <div class="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full mb-6 border border-white/20">
        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="text-sm font-medium">Tecnología SENA certificada</span>
      </div>

      <!-- Título principal con animación de entrada -->
      <h1 class="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 animate-fade-in-up">
        {{ configStore.general.lema || 'Análisis Inteligente de Granos de Cacao' }}
      </h1>
      
      <!-- Descripción -->
      <p class="text-lg md:text-xl lg:text-2xl mb-10 max-w-3xl mx-auto opacity-95 leading-relaxed">
        Sistema de clasificación y análisis de calidad de cacao mediante visión por computadora e inteligencia artificial
      </p>
      
      <!-- Botones de acción con mejor interacción -->
      <div class="flex flex-col sm:flex-row justify-center gap-4">
        <button 
          @click="goToLogin"
          class="group bg-white text-green-600 hover:bg-gray-50 font-semibold py-4 px-10 rounded-xl text-lg shadow-xl hover:shadow-2xl transition-all duration-200 hover:scale-105 active:scale-100 transform"
        >
          <span class="flex items-center justify-center gap-2">
            Iniciar Sesión
            <svg class="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </span>
        </button>
        <button 
          @click="goToRegister"
          class="group bg-transparent border-3 border-white/30 backdrop-blur-sm text-white hover:bg-white hover:text-green-600 font-semibold py-4 px-10 rounded-xl text-lg transition-all duration-200 hover:scale-105 active:scale-100 transform hover:border-white"
        >
          <span class="flex items-center justify-center gap-2">
            Registrarse
            <svg class="w-5 h-5 group-hover:rotate-90 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </span>
        </button>
      </div>

      <!-- Indicadores de confianza -->
      <div class="mt-16 flex flex-wrap items-center justify-center gap-8 text-sm">
        <div class="flex items-center gap-2">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          <span class="opacity-90">Precisión del 95%</span>
        </div>
        <div class="flex items-center gap-2">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
            <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm9.707 5.707a1 1 0 00-1.414-1.414L9 12.586l-1.293-1.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          <span class="opacity-90">IA Avanzada</span>
        </div>
        <div class="flex items-center gap-2">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          <span class="opacity-90">Análisis instantáneo</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useConfigStore } from '@/stores/config';

const router = useRouter();
const configStore = useConfigStore();

const goToLogin = () => {
  router.push('/login');
};

const goToRegister = () => {
  router.push('/registro');
};
</script>

<style scoped>
/* Animación de entrada suave para el título */
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fade-in-up 0.8s ease-out;
}
</style>
