<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
    <div class="bg-gradient-to-r from-green-50 to-green-50 px-4 py-3 border-b border-gray-200">
      <div class="flex items-center">
        <div class="bg-green-100 p-1.5 rounded-lg mr-2">
          <svg class="text-green-600 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
          </svg>
        </div>
        <div>
          <h2 class="text-base font-bold text-gray-900">Acciones Contextuales</h2>
          <p class="text-xs text-gray-600">Acciones inteligentes del sistema</p>
        </div>
      </div>
    </div>
    <div class="p-4 space-y-3">
      <button @click="$emit('nuevo-analisis')" class="w-full flex items-center gap-3 p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-all duration-200 border border-gray-200 group">
        <div class="bg-green-500 p-2 rounded-lg flex-shrink-0">
          <svg class="text-white w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </div>
        <div class="flex-1 text-left">
          <h3 class="text-base font-bold text-gray-900">➕ Nuevo Análisis</h3>
          <p class="text-xs text-gray-600">Analizar granos de cacao</p>
        </div>
        <div class="text-green-600 group-hover:translate-x-1 transition-transform duration-300">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
        </div>
      </button>
      
      <button @click="$emit('generar-reporte')" class="w-full flex items-center gap-3 p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-all duration-200 border border-gray-200 group">
        <div class="bg-purple-500 p-2 rounded-lg flex-shrink-0">
          <svg class="text-white w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
        </div>
        <div class="flex-1 text-left">
          <h3 class="text-base font-bold text-gray-900">📄 Generar Reporte del Mes</h3>
          <p class="text-xs text-gray-600">Exportar estadísticas mensuales</p>
        </div>
        <div class="text-purple-600 group-hover:translate-x-1 transition-transform duration-300">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
        </div>
      </button>
      
      <button 
        v-if="hasCriticalAlerts"
        @click="$emit('ver-alertas')"
        class="w-full flex items-center gap-3 p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-all duration-200 border-2 border-red-300 group"
      >
        <div class="bg-red-500 p-2 rounded-lg flex-shrink-0">
          <svg class="text-white w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
          </svg>
        </div>
        <div class="flex-1 text-left">
          <h3 class="text-base font-bold text-gray-900">⚠️ Ver Alertas Críticas</h3>
          <p class="text-xs text-gray-600">{{ criticalAlertsCount }} alerta{{ criticalAlertsCount > 1 ? 's' : '' }} pendiente{{ criticalAlertsCount > 1 ? 's' : '' }}</p>
        </div>
        <div class="text-red-600 group-hover:translate-x-1 transition-transform duration-300">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
        </div>
      </button>
      
      <button @click="$emit('ver-recomendaciones')" class="w-full flex items-center gap-3 p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-all duration-200 border border-gray-200 group">
        <div class="bg-indigo-500 p-2 rounded-lg flex-shrink-0">
          <svg class="text-white w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
          </svg>
        </div>
        <div class="flex-1 text-left">
          <h3 class="text-base font-bold text-gray-900">🧠 Ver Recomendaciones</h3>
          <p class="text-xs text-gray-600">Sugerencias basadas en IA</p>
        </div>
        <div class="text-indigo-600 group-hover:translate-x-1 transition-transform duration-300">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  hasCriticalAlerts: {
    type: Boolean,
    default: false
  },
  criticalAlertsCount: {
    type: Number,
    default: 0
  }
})

defineEmits(['nuevo-analisis', 'generar-reporte', 'ver-alertas', 'ver-recomendaciones'])
</script>

