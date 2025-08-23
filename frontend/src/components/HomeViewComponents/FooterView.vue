<template>
    <footer class="bg-gray-800 text-white py-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 class="text-lg font-semibold mb-4">CacaoScan</h3>
            <p class="text-gray-400">Sistema de análisis y clasificación de granos de cacao mediante visión por computadora.</p>
          </div>
          <div>
            <h3 class="text-lg font-semibold mb-4">Enlaces rápidos</h3>
            <ul class="space-y-2">
              <li><a href="#" class="text-gray-400 hover:text-white transition-colors">Inicio</a></li>
              <li><a href="#features" class="text-gray-400 hover:text-white transition-colors">Funcionalidades</a></li>
              <li><a href="#about" class="text-gray-400 hover:text-white transition-colors">Sobre el sistema</a></li>
              <li><button @click="goToLogin" class="text-gray-400 hover:text-white transition-colors">Iniciar sesión</button></li>
            </ul>
          </div>
          <div>
            <h3 class="text-lg font-semibold mb-4">Legal</h3>
            <ul class="space-y-2">
              <li><a href="#" class="text-gray-400 hover:text-white transition-colors">Política de privacidad</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white transition-colors">Términos de servicio</a></li>
            </ul>
          </div>
        </div>
        <div class="border-t border-gray-700 mt-12 pt-8 text-center text-gray-400">
          <p>© 2025 CacaoScan - Desarrollado como parte del programa de formación del SENA - Ficha 2923560</p>
        </div>
      </div>
    </footer>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const goToLogin = () => {
  router.push('/login');
};
</script>
