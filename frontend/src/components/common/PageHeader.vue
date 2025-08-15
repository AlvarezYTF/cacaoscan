<template>
  <div class="mb-10">
    <!-- Back Button -->
    <div class="mb-6">
      <router-link 
        to="/" 
        class="inline-flex items-center group text-green-600 hover:text-green-700 transition-all duration-300 px-4 py-2 rounded-lg hover:bg-green-50"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 transform group-hover:-translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        <span class="font-medium">Volver al inicio</span>
      </router-link>
    </div>
    
    <!-- Header Content -->
    <div class="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-8 shadow-sm border border-green-100">
      <div class="text-center max-w-3xl mx-auto">
        <div class="inline-flex items-center justify-center px-4 py-1.5 rounded-full bg-green-100 text-green-800 text-sm font-medium mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          {{ badgeText }}
        </div>
        <h1 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4 bg-clip-text text-transparent bg-gradient-to-r from-green-600 to-emerald-600">
          {{ title }}
        </h1>
        <div class="w-24 h-1 bg-gradient-to-r from-green-400 to-emerald-400 mx-auto mb-6 rounded-full"></div>
        <p class="text-lg text-gray-600 leading-relaxed">
          {{ description }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PageHeader',
  props: {
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      required: true
    },
    badgeText: {
      type: String,
      default: 'Análisis de Calidad'
    }
  }
}
</script>
