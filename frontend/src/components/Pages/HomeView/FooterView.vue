<template>
    <!-- Footer mejorado con mejor organización y elementos visuales -->
    <footer class="bg-gray-900 text-white py-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Grid principal con 4 columnas -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-12">
          <!-- Columna 1: Branding -->
          <div class="lg:col-span-1">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 bg-green-600 rounded-xl flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h3 class="text-xl font-bold text-white">{{ configStore.brandName }}</h3>
            </div>
            <p class="text-gray-400 leading-relaxed mb-4">{{ configStore.sistemaLema }}</p>
            <!-- Badge SENA -->
            <div class="inline-flex items-center gap-2 bg-green-600/20 border border-green-500/30 px-3 py-1.5 rounded-lg">
              <svg class="w-4 h-4 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586l-1.293-1.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              <span class="text-xs font-semibold text-green-400">Certificado SENA</span>
            </div>
          </div>

          <!-- Columna 2: Enlaces de navegación -->
          <div>
            <h3 class="text-lg font-bold text-white mb-6">Enlaces rápidos</h3>
            <ul class="space-y-3">
              <li>
                <a href="#" class="text-gray-400 hover:text-green-400 transition-colors flex items-center gap-2 group">
                  <svg class="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                  </svg>
                  Inicio
                </a>
              </li>
              <li>
                <a href="#features" class="text-gray-400 hover:text-green-400 transition-colors flex items-center gap-2 group">
                  <svg class="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  Funcionalidades
                </a>
              </li>
              <li>
                <a href="#about" class="text-gray-400 hover:text-green-400 transition-colors flex items-center gap-2 group">
                  <svg class="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Sobre el sistema
                </a>
              </li>
              <li>
                <button @click="goToLogin" class="text-gray-400 hover:text-green-400 transition-colors flex items-center gap-2 group">
                  <svg class="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                  </svg>
                  Iniciar sesión
                </button>
              </li>
            </ul>
          </div>

          <!-- Columna 3: Información legal -->
          <div>
            <h3 class="text-lg font-bold text-white mb-6">Información legal</h3>
            <ul class="space-y-3">
              <li>
                <router-link 
                  :to="{ name: 'PrivacyPolicy' }" 
                  class="text-gray-400 hover:text-green-400 transition-colors flex items-center gap-2 group"
                >
                  <svg class="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  Política de privacidad
                </router-link>
              </li>
              <li>
                <router-link 
                  :to="{ name: 'LegalTerms' }" 
                  class="text-gray-400 hover:text-green-400 transition-colors flex items-center gap-2 group"
                >
                  <svg class="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Términos y condiciones
                </router-link>
              </li>
            </ul>
          </div>

          <!-- Columna 4: Contacto -->
          <div>
            <h3 class="text-lg font-bold text-white mb-6">Contáctanos</h3>
            <ul class="space-y-3">
              <li class="text-gray-400">
                <span class="flex items-center gap-2">
                  <svg class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  Soporte técnico
                </span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Línea divisoria y copyright -->
        <div class="border-t border-gray-800 pt-8">
          <div class="flex flex-col md:flex-row justify-between items-center gap-4">
            <p class="text-sm text-gray-400 text-center md:text-left">
              © 2025 {{ configStore.brandName }}. Todos los derechos reservados.
            </p>
            <p class="text-sm text-gray-500 text-center md:text-right">
              Desarrollado como parte del programa de formación del SENA - Ficha 2923560
            </p>
          </div>
        </div>
      </div>
    </footer>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useConfigStore } from '@/stores/config';

const router = useRouter();
const configStore = useConfigStore();

const goToLogin = () => {
  router.push('/login');
};
</script>
