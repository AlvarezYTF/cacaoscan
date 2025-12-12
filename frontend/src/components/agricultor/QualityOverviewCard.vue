<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
    <!-- Header Section -->
    <div class="mb-5">
      <h2 class="text-xl font-bold text-gray-900 mb-0.5">Estado de Calidad del Cacao</h2>
      <p class="text-sm text-gray-600">Calidad promedio global</p>
    </div>
    
    <!-- Circular Gauge Section -->
    <div class="flex flex-col items-center justify-center py-4">
      <div class="relative" style="width: 160px; height: 160px;">
        <svg 
          class="w-full h-full transform -rotate-90" 
          viewBox="0 0 100 100"
        >
          <!-- Background circle -->
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            stroke="#e5e7eb"
            stroke-width="8"
          />
          <!-- Progress circle -->
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            :stroke="gaugeColor"
            stroke-width="8"
            stroke-linecap="round"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="strokeDashoffset"
            class="transition-all duration-500"
          />
        </svg>
        
        <!-- Percentage and Label - Centered inside circle -->
        <div class="absolute inset-0 flex flex-col items-center justify-center">
          <div class="text-4xl font-bold mb-1" :style="{ color: gaugeColor }">
            {{ quality }}%
          </div>
          <!-- Status Badge -->
          <div 
            :class="statusBadgeClass"
            class="px-2.5 py-0.5 rounded-full text-xs font-semibold"
          >
            {{ classification?.label || 'N/A' }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- Trend Indicator -->
    <div v-if="trend !== 'stable'" class="flex items-center justify-center gap-1.5 mt-3">
      <svg 
        v-if="trend === 'up'"
        class="w-3.5 h-3.5 text-green-600"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
      </svg>
      <svg 
        v-else
        class="w-3.5 h-3.5 text-red-600"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6 6"></path>
      </svg>
      <span 
        :class="trend === 'up' ? 'text-green-600' : 'text-red-600'" 
        class="text-xs font-medium"
      >
        {{ trend === 'up' ? 'Mejora' : 'Baja' }} vs último período
      </span>
    </div>
    
    <div v-else class="flex items-center justify-center mt-3">
      <span class="text-xs text-gray-500">Estable</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  quality: {
    type: Number,
    required: true,
    default: 0
  },
  classification: {
    type: Object,
    default: null
  },
  trend: {
    type: String,
    default: 'stable',
    validator: (value) => ['up', 'down', 'stable'].includes(value)
  }
})

const gaugeColor = computed(() => {
  if (props.quality >= 85) return '#10b981' // green
  if (props.quality >= 70) return '#eab308' // yellow
  return '#ef4444' // red
})

const statusBadgeClass = computed(() => {
  if (props.quality >= 85) {
    return 'bg-green-500 text-white'
  }
  if (props.quality >= 70) {
    return 'bg-yellow-500 text-white'
  }
  return 'bg-red-500 text-white'
})

// Calculate circumference for circular progress
const radius = 40
const circumference = computed(() => 2 * Math.PI * radius)

const strokeDashoffset = computed(() => {
  const quality = Math.min(Math.max(props.quality, 0), 100)
  return circumference.value - (circumference.value * quality / 100)
})
</script>
