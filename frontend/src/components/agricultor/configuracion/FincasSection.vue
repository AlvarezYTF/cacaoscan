<template>
  <div class="bg-white rounded-2xl border-2 border-gray-200 p-8 shadow-lg">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-green-100 rounded-xl">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
        </div>
        <h3 class="text-2xl font-bold text-gray-900">Mis Fincas</h3>
      </div>
    </div>

    <!-- Lista de fincas -->
    <div class="space-y-3 mb-4">
      <div 
        v-for="finca in fincas" 
        :key="finca.id"
        class="flex items-center justify-between p-4 border-2 border-gray-200 rounded-xl hover:border-green-300 transition-all duration-200 group"
        :class="{ 'border-green-500 bg-green-50': finca.isPrimary }"
      >
        <div class="flex-1">
          <div class="flex items-center gap-2 mb-1">
            <p class="font-semibold text-gray-900">{{ finca.nombre }}</p>
            <span v-if="finca.isPrimary" class="px-2 py-0.5 bg-green-600 text-white text-xs font-bold rounded-full">Principal</span>
          </div>
          <p class="text-sm text-gray-500">{{ finca.ubicacion }}</p>
          <p class="text-xs text-gray-400 mt-1">{{ finca.hectareas }} hectáreas</p>
        </div>
        <div class="flex items-center gap-2">
          <button 
            @click="$emit('toggle-status', finca.id)"
            class="p-2 rounded-lg transition-colors"
            :class="finca.isActive ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="finca.isActive ? 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' : 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z'" />
            </svg>
          </button>
          <button 
            @click="$emit('set-primary', finca.id)"
            :disabled="finca.isPrimary"
            class="p-2 rounded-lg transition-colors disabled:opacity-40"
            :class="finca.isPrimary ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-green-100 hover:text-green-600'"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
            </svg>
          </button>
        </div>
      </div>

      <div v-if="fincas.length === 0" class="text-center py-8 text-gray-500">
        <svg class="w-12 h-12 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
        <p>No tienes fincas registradas</p>
      </div>
    </div>

    <button 
      @click="$emit('add-new')"
      class="w-full flex justify-center items-center gap-2 py-3 px-4 border-2 border-dashed border-gray-300 rounded-xl text-green-600 hover:border-green-400 hover:bg-green-50 transition-all duration-200 font-semibold"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
      </svg>
      Nueva Finca
    </button>
  </div>
</template>

<script setup>
defineProps({
  fincas: {
    type: Array,
    required: true
  }
})

defineEmits(['toggle-status', 'set-primary', 'add-new'])
</script>

