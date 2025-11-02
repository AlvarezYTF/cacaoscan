<template>
  <!-- Progress Indicator -->
  <div v-if="show" class="space-y-3 bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-2xl p-6 shadow-sm">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <div class="p-2 bg-green-600 rounded-lg">
          <svg class="w-5 h-5 text-white animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
        </div>
        <span class="text-sm font-bold text-gray-800">{{ label || 'Procesando...' }}</span>
      </div>
      <span class="text-lg font-bold text-green-700">{{ progress }}%</span>
    </div>
    <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden shadow-inner">
      <div
        class="bg-gradient-to-r from-green-500 to-green-600 h-3 rounded-full transition-all duration-500 ease-out shadow-sm"
        :style="{ width: `${progress}%` }"
      ></div>
    </div>
  </div>
</template>

<script setup>
// 1. Vue core
import { defineProps } from 'vue'

// Props
const props = defineProps({
  progress: {
    type: Number,
    required: true,
    validator: (value) => value >= 0 && value <= 100
  },
  label: {
    type: String,
    default: ''
  },
  show: {
    type: Boolean,
    default: true
  }
})
</script>

<style scoped>
/* Solo estilos que no están en Tailwind si es necesario */
</style>
