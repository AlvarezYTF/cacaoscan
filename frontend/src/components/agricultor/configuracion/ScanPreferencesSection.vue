<template>
  <div class="bg-white rounded-2xl border-2 border-gray-200 p-8 shadow-lg">
    <div class="flex items-center gap-3 mb-6">
      <div class="p-2 bg-green-100 rounded-xl">
        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      </div>
      <h3 class="text-2xl font-bold text-gray-900">Preferencias de Escaneo</h3>
    </div>

    <div class="space-y-5">
      <!-- Tipo de grano preferido -->
      <div>
        <label for="scan-preferences-grain-type" class="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
          </svg>
          Tipo de grano preferido
        </label>
        <select 
          id="scan-preferences-grain-type"
          :value="preferences.grainType" 
          @change="$emit('update:preferences', { ...preferences, grainType: $event.target.value })"
          class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500/30 focus:border-green-500 transition-all duration-200"
        >
          <option value="Criollo">Criollo</option>
          <option value="Forastero">Forastero</option>
          <option value="Trinitario">Trinitario</option>
          <option value="Nacional">Nacional</option>
          <option value="Híbrido">Híbrido</option>
          <option value="">Todos los tipos</option>
        </select>
      </div>

      <!-- Peso mínimo -->
      <div>
        <label for="scan-preferences-min-weight" class="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
          </svg>
          Peso mínimo por muestra (g)
        </label>
        <input 
          id="scan-preferences-min-weight"
          type="number" 
          :value="preferences.minWeight" 
          @input="$emit('update:preferences', { ...preferences, minWeight: Number.parseInt($event.target.value) || 0 })"
          placeholder="5" 
          min="0" 
          step="0.1" 
          class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500/30 focus:border-green-500 transition-all duration-200"
        >
      </div>

      <!-- Toggle para captura guiada -->
      <div class="flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-gray-50 border-2 border-green-200 rounded-xl">
        <div class="flex items-center gap-3">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <p class="font-semibold text-gray-900">Modo captura guiada</p>
            <p class="text-xs text-gray-500">Ayuda paso a paso durante la captura</p>
          </div>
        </div>
        <button 
          @click="$emit('update:preferences', { ...preferences, guidedMode: !preferences.guidedMode })"
          class="relative w-14 h-8 rounded-full transition-colors duration-200"
          :class="preferences.guidedMode ? 'bg-green-600' : 'bg-gray-300'"
        >
          <span 
            class="absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform duration-200 shadow-lg"
            :class="preferences.guidedMode ? 'translate-x-6' : 'translate-x-0'"
          ></span>
        </button>
      </div>

      <!-- Mostrar resultados avanzados -->
      <div class="flex items-center justify-between p-4 bg-gray-50 border-2 border-gray-200 rounded-xl">
        <div class="flex items-center gap-3">
          <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <div>
            <p class="font-semibold text-gray-900">Resultados avanzados</p>
            <p class="text-xs text-gray-500">Mostrar métricas técnicas detalladas</p>
          </div>
        </div>
        <button 
          @click="$emit('update:preferences', { ...preferences, advancedResults: !preferences.advancedResults })"
          class="relative w-14 h-8 rounded-full transition-colors duration-200"
          :class="preferences.advancedResults ? 'bg-green-600' : 'bg-gray-300'"
        >
          <span 
            class="absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform duration-200 shadow-lg"
            :class="preferences.advancedResults ? 'translate-x-6' : 'translate-x-0'"
          ></span>
        </button>
      </div>
    </div>

    <button 
      @click="$emit('save')"
      :disabled="isLoading"
      class="w-full mt-6 flex justify-center items-center gap-2 py-3.5 px-4 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white rounded-xl font-bold shadow-lg hover:shadow-xl transition-all duration-300 active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed"
    >
      <svg v-if="isLoading" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
      </svg>
      {{ isLoading ? 'Guardando...' : 'Guardar Preferencias' }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  preferences: {
    type: Object,
    required: true
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['update:preferences', 'save'])
</script>

