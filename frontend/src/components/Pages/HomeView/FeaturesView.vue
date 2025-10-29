<template>
    <!-- Features Section: Destaca las capacidades del sistema -->
    <section id="features" class="py-20 bg-gradient-to-b from-gray-50 to-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Encabezado con badge -->
        <div class="text-center mb-16">
          <div class="inline-flex items-center gap-2 bg-green-100 px-4 py-2 rounded-full mb-4">
            <svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784-.38-1.54.1.118-1.118l-1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            <span class="text-sm font-medium text-green-700">Funcionalidades Principales</span>
          </div>
          <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">Nuestras Soluciones</h2>
          <p class="text-lg text-gray-600 max-w-2xl mx-auto">Tecnología avanzada para revolucionar la industria cacaotera</p>
        </div>

        <!-- Grid de características con animaciones -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
          <!-- Feature 1: Captura de imágenes con efecto hover mejorado -->
          <div class="group bg-white border-2 border-gray-200 rounded-2xl shadow-md p-8 hover:shadow-2xl hover:border-green-300 transition-all duration-300 hover:-translate-y-2 cursor-pointer">
            <div class="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold mb-3 text-gray-900 group-hover:text-green-600 transition-colors">Captura y procesamiento de imágenes</h3>
            <p class="text-gray-600 leading-relaxed">Sistema avanzado de captura y procesamiento de imágenes de granos de cacao con alta precisión.</p>
          </div>

          <!-- Feature 2: IA con badge de precisión -->
          <div class="group bg-white border-2 border-gray-200 rounded-2xl shadow-md p-8 hover:shadow-2xl hover:border-green-300 transition-all duration-300 hover:-translate-y-2 cursor-pointer">
            <div class="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div class="flex items-center gap-2 mb-3">
              <h3 class="text-xl font-bold text-gray-900 group-hover:text-green-600 transition-colors">Clasificación automática con IA</h3>
              <span class="bg-green-100 text-green-700 text-xs font-bold px-2 py-1 rounded-full">95%</span>
            </div>
            <p class="text-gray-600 leading-relaxed">Modelos de inteligencia artificial entrenados para clasificar granos con precisión superior al 95%.</p>
          </div>

          <!-- Feature 3: Reportes con ícono dinámico -->
          <div class="group bg-white border-2 border-gray-200 rounded-2xl shadow-md p-8 hover:shadow-2xl hover:border-green-300 transition-all duration-300 hover:-translate-y-2 cursor-pointer">
            <div class="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold mb-3 text-gray-900 group-hover:text-green-600 transition-colors">Generación de reportes</h3>
            <p class="text-gray-600 leading-relaxed">Informes detallados y personalizables con análisis estadísticos completos de tus lotes de cacao.</p>
          </div>

          <!-- Feature 4: Dashboard en tiempo real -->
          <div class="group bg-white border-2 border-gray-200 rounded-2xl shadow-md p-8 hover:shadow-2xl hover:border-green-300 transition-all duration-300 hover:-translate-y-2 cursor-pointer">
            <div class="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div class="flex items-center gap-2 mb-3">
              <h3 class="text-xl font-bold text-gray-900 group-hover:text-green-600 transition-colors">Dashboard interactivo</h3>
              <span class="inline-flex items-center gap-1 bg-green-100 text-green-700 text-xs font-bold px-2 py-1 rounded-full">
                <span class="relative flex h-2 w-2">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                </span>
                LIVE
              </span>
            </div>
            <p class="text-gray-600 leading-relaxed">Visualización en tiempo real de métricas y tendencias de calidad de tu producción de cacao.</p>
          </div>
        </div>
      </div>
    </section>
</template>
