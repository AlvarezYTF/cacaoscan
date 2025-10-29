<template>
  <div class="bg-white rounded-2xl border-2 border-gray-200 p-8 shadow-lg">
    <div class="flex items-center gap-3 mb-6">
      <div class="p-2 bg-green-100 rounded-xl">
        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
        </svg>
      </div>
      <h3 class="text-2xl font-bold text-gray-900">Ajustes Visuales</h3>
    </div>

    <div class="space-y-5">
      <!-- Modo oscuro/claro -->
      <div class="flex items-center justify-between p-4 bg-gradient-to-r from-gray-900 to-gray-800 text-white rounded-xl">
        <div class="flex items-center gap-3">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
          <div>
            <p class="font-semibold">Modo oscuro</p>
            <p class="text-xs opacity-75">Cambiar al modo oscuro del sistema</p>
          </div>
        </div>
        <button 
          @click="$emit('update:settings', { ...settings, darkMode: !settings.darkMode })"
          class="relative w-14 h-8 rounded-full transition-colors duration-200"
          :class="settings.darkMode ? 'bg-white' : 'bg-gray-500'"
        >
          <span 
            class="absolute top-1 left-1 w-6 h-6 bg-gray-800 rounded-full transition-transform duration-200 shadow-lg"
            :class="settings.darkMode ? 'translate-x-6' : 'translate-x-0'"
          ></span>
        </button>
      </div>

      <!-- Tamaño de fuente -->
      <div>
        <label class="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          Tamaño de fuente
        </label>
        <select 
          :value="settings.fontSize" 
          @change="$emit('update:settings', { ...settings, fontSize: $event.target.value })"
          class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500/30 focus:border-green-500 transition-all duration-200"
        >
          <option value="small">Pequeño</option>
          <option value="medium">Mediano</option>
          <option value="large">Grande</option>
        </select>
      </div>

      <!-- Modo compacto -->
      <div class="flex items-center justify-between p-4 bg-gray-50 border-2 border-gray-200 rounded-xl">
        <div class="flex items-center gap-3">
          <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
          </svg>
          <div>
            <p class="font-semibold text-gray-900">Modo compacto</p>
            <p class="text-xs text-gray-500">Mostrar más información en menos espacio</p>
          </div>
        </div>
        <button 
          @click="$emit('update:settings', { ...settings, compactMode: !settings.compactMode })"
          class="relative w-14 h-8 rounded-full transition-colors duration-200"
          :class="settings.compactMode ? 'bg-green-600' : 'bg-gray-300'"
        >
          <span 
            class="absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform duration-200 shadow-lg"
            :class="settings.compactMode ? 'translate-x-6' : 'translate-x-0'"
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
      {{ isLoading ? 'Guardando...' : 'Guardar Ajustes' }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  settings: {
    type: Object,
    required: true
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['update:settings', 'save'])
</script>

