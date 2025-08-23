<template>
  <section class="bg-gradient-to-r from-emerald-600 to-emerald-800 text-white py-20">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
      <h1 class="text-4xl md:text-6xl font-bold mb-6">Análisis Inteligente de Granos de Cacao</h1>
      <p class="text-xl md:text-2xl mb-8 max-w-3xl mx-auto">Tecnología de vanguardia para la clasificación y análisis de
        calidad de cacao mediante visión por computadora e IA</p>
      <div class="flex justify-center space-x-4">
        <button 
          @click="goToLogin"
          class="bg-white text-emerald-700 hover:bg-gray-50 font-bold py-3 px-8 rounded-lg text-lg transition-all duration-300 shadow-lg hover:shadow-2xl hover:-translate-y-1 transform hover:scale-105"
        >
          Iniciar Sesión
        </button>
        <button 
          @click="goToRegister"
          class="bg-transparent border-2 border-white text-white hover:bg-white hover:text-emerald-700 font-bold py-3 px-8 rounded-lg text-lg transition-all duration-300 hover:-translate-y-1 transform hover:scale-105"
        >
          Registrarse
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const goToLogin = () => {
  router.push('/login');
};

const goToRegister = () => {
  router.push('/registro');
};
</script>
