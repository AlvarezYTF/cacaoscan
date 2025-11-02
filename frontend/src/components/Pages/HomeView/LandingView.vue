<template>
  <!-- Landing Section -->
  <!-- Mejoras aplicadas: Paleta verde agrícola, tarjetas con sombras suaves, animaciones hover, íconos SVG inline, diseño responsive profesional -->
  <section class="relative py-12 md:py-20 px-4 bg-white overflow-hidden">
    <div class="max-w-7xl mx-auto">

      <!-- Collage de Imágenes - Tarjeta con grid responsive -->
      <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 md:p-8 mb-8 md:mb-16 transition-all duration-200 hover:shadow-xl">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8 max-w-6xl mx-auto">
          <!-- Imágenes en esquina - Container relativo mejorado -->
          <div class="relative h-80 md:h-[450px] lg:h-[500px] rounded-xl overflow-hidden">
            <img
              src="@/assets/cacao_lab1.jpg"
              alt="Análisis de laboratorio de cacao"
              class="absolute top-0 left-0 w-2/3 rounded-2xl shadow-lg border-2 border-gray-200 object-cover h-2/3 transition-all duration-300 hover:scale-[1.02] hover:shadow-xl"
            />
            <img
              src="@/assets/cacao_lab2.jpg"
              alt="Investigación de cacao"
              class="absolute bottom-0 right-0 w-2/3 rounded-2xl shadow-lg border-2 border-gray-200 object-cover h-2/3 transition-all duration-300 hover:scale-[1.02] hover:shadow-xl"
            />
          </div>

          <!-- Bloque de texto - Tarjeta interna con ícono -->
          <div class="flex flex-col justify-center p-4 md:p-6 lg:p-8 bg-gray-50 rounded-xl">
            <!-- Ícono de investigación -->
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
              </div>
              <h2 class="text-2xl md:text-3xl lg:text-4xl font-bold text-gray-900">
                Investigación y Análisis
              </h2>
            </div>
            <p class="text-base md:text-lg text-gray-700 leading-relaxed">
              CacaoScan integra herramientas de inteligencia artificial para analizar las características físicas y visuales de los granos de cacao. Cada muestra es medida y procesada para determinar dimensiones, peso y calidad.
            </p>
            <!-- Badge de estado -->
            <div class="mt-4 flex flex-wrap gap-2">
              <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                IA Activa
              </span>
              <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                Análisis Preciso
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Sección de Evaluación de Fermentación - Tarjeta centrada con ícono -->
      <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 md:p-8 mb-8 md:mb-16 transition-all duration-200 hover:shadow-xl">
        <div class="max-w-4xl mx-auto">
          <!-- Header de sección con ícono -->
          <div class="text-center mb-6 md:mb-8">
            <div class="flex justify-center mb-4">
              <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                </svg>
              </div>
            </div>
            <h2 class="text-2xl md:text-3xl lg:text-4xl font-bold text-gray-900 mb-3 md:mb-4">
              Evaluación de Fermentación
            </h2>
            <p class="text-base md:text-lg text-gray-700 max-w-2xl mx-auto leading-relaxed">
              El sistema permite visualizar el interior de los granos para determinar el grado de fermentación y el estado del cacao.
            </p>
          </div>
          <!-- Imagen con hover effect - Tamaño reducido para mejor proporción -->
          <div class="flex justify-center">
            <div class="relative w-full max-w-2xl rounded-2xl overflow-hidden shadow-lg border-2 border-gray-200 transition-all duration-300 hover:shadow-xl hover:scale-[1.01]">
              <img
                src="@/assets/cacao_lab3.jpg"
                alt="Evaluación de fermentación del cacao"
                class="w-full h-auto max-h-96 object-cover"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
// Componente de landing page con diseño profesional y paleta verde agrícola
// Usa TailwindCSS + Flowbite para estilos y componentes
</script>

<style scoped>
/* Estilos específicos del componente LandingView si son necesarios */
</style>

