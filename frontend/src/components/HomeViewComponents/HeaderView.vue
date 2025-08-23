<template>
  <header class="bg-white shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16 items-center">
        <div class="flex-shrink-0 flex items-center">
          <h1 class="text-2xl font-bold text-emerald-700">CacaoScan</h1>
        </div>
        <nav class="hidden md:ml-6 md:flex space-x-8">
          <a href="#" class="text-gray-900 hover:text-emerald-600 px-3 py-2 text-sm font-medium">Inicio</a>
          <a href="#features" class="text-gray-500 hover:text-emerald-600 px-3 py-2 text-sm font-medium">Funcionalidades</a>
          <a href="#about" class="text-gray-500 hover:text-emerald-600 px-3 py-2 text-sm font-medium">Sobre el sistema</a>
          <button 
            @click="goToLogin"
            class="text-gray-500 hover:text-emerald-600 px-3 py-2 text-sm font-medium transition-all duration-200 hover:bg-emerald-50 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-opacity-50 active:scale-95"
            :disabled="isNavigating"
          >
            <svg v-if="isNavigating" class="w-4 h-4 inline mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            {{ isNavigating ? 'Redirigiendo...' : 'Iniciar sesión' }}
          </button>
        </nav>
        <button class="md:hidden text-gray-500 hover:text-gray-900">
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isNavigating = ref(false);

const goToLogin = async () => {
  try {
    isNavigating.value = true;
    await router.push('/login');
  } catch (error) {
    console.error('Error al navegar al login:', error);
    // Fallback: usar window.location si router falla
    window.location.href = '/login';
  } finally {
    isNavigating.value = false;
  }
};
</script>
