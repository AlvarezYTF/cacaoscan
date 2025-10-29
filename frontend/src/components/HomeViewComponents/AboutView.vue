<template>
  <!-- About Section: Información institucional con mejor presentación -->
  <section id="about" class="py-20 bg-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Layout de dos columnas con mejor espaciado -->
      <div class="lg:grid lg:grid-cols-2 lg:gap-16 items-center">
        <!-- Contenido textual con mejor jerarquía -->
        <div class="mb-12 lg:mb-0">
          <!-- Badge y título -->
          <div class="inline-flex items-center gap-2 bg-green-100 px-3 py-1 rounded-full mb-6">
            <svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586l-1.293-1.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <span class="text-xs font-semibold text-green-700 uppercase tracking-wide">Acerca de</span>
          </div>
          <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-8 leading-tight">Sobre el sistema</h2>
          
          <!-- Texto principal con mejor formato -->
          <div class="space-y-6 text-base text-gray-600 leading-relaxed">
            <p class="text-lg leading-relaxed">
              <strong class="text-gray-900 font-semibold">{{ configStore.brandName }}</strong> es una solución tecnológica desarrollada para revolucionar el proceso de clasificación y
              análisis de granos de cacao mediante el uso de visión por computadora e inteligencia artificial.
            </p>
            <p>
              Nuestro sistema permite a los productores y procesadores de cacao evaluar la calidad de sus granos de
              manera <span class="text-green-600 font-medium">objetiva, rápida y precisa</span>, eliminando la subjetividad del análisis visual tradicional.
            </p>
            <p>
              Desarrollado en el marco del programa de formación del <span class="text-green-600 font-medium">SENA</span>, este proyecto combina tecnologías de
              vanguardia con un profundo entendimiento de las necesidades de la industria cacaotera colombiana.
            </p>
          </div>

          <!-- Características destacadas en formato de lista -->
          <div class="mt-10 grid grid-cols-2 gap-6">
            <div class="flex items-start gap-3">
              <div class="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center flex-shrink-0 mt-1">
                <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h4 class="font-semibold text-gray-900 mb-1">Certificado SENA</h4>
                <p class="text-sm text-gray-600">Programa de formación 2923560</p>
              </div>
            </div>
            <div class="flex items-start gap-3">
              <div class="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center flex-shrink-0 mt-1">
                <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h4 class="font-semibold text-gray-900 mb-1">Análisis rápido</h4>
                <p class="text-sm text-gray-600">Resultados en segundos</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Imagen con mejor presentación y efecto hover -->
        <div class="relative">
          <!-- Gradiente decorativo de fondo -->
          <div class="absolute -inset-4 bg-gradient-to-br from-green-100 to-transparent rounded-3xl opacity-50 -z-10"></div>
          
          <!-- Contenedor de imagen con mejor estilo -->
          <div class="bg-white border-2 border-gray-200 rounded-2xl shadow-xl p-4 hover:shadow-2xl transition-all duration-300 group">
            <img 
              src="@/assets/Cacao/GranosCacao.jpg" 
              alt="Granos de cacao" 
              class="rounded-xl w-full h-auto group-hover:scale-[1.02] transition-transform duration-300"
            >
            <!-- Badge sobre la imagen -->
            <div class="absolute top-6 right-6 bg-white/90 backdrop-blur-sm px-3 py-2 rounded-full shadow-md">
              <span class="text-xs font-bold text-green-700 flex items-center gap-1">
                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
                </svg>
                Calidad Premium
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useConfigStore } from '@/stores/config'

const configStore = useConfigStore()
</script>
