<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
    <!-- Total Agricultores -->
    <div class="bg-white rounded-xl border border-gray-100 p-5 hover:shadow-sm transition-shadow">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <p class="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Cacaocultores</p>
          <p class="text-3xl font-bold text-gray-900">{{ totalItems }}</p>
        </div>
        <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center">
          <svg class="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </div>
      </div>
    </div>

    <!-- Total Fincas -->
    <div class="bg-white rounded-xl border border-gray-100 p-5 hover:shadow-sm transition-shadow">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <p class="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Fincas</p>
          <p class="text-3xl font-bold text-gray-900">{{ getTotalFarms() }}</p>
        </div>
        <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
          <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
        </div>
      </div>
    </div>

    <!-- Activos -->
    <div class="bg-white rounded-xl border border-gray-100 p-5 hover:shadow-sm transition-shadow">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <p class="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Activos</p>
          <p class="text-3xl font-bold text-gray-900">{{ getActiveFarmers() }}</p>
        </div>
        <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-violet-50 flex items-center justify-center">
          <svg class="w-5 h-5 text-violet-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      </div>
    </div>

    <!-- Área Total -->
    <div class="bg-white rounded-xl border border-gray-100 p-5 hover:shadow-sm transition-shadow">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <p class="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Área Total</p>
          <p class="text-3xl font-bold text-gray-900">{{ getTotalArea() }}<span class="text-lg font-normal text-gray-500 ml-1">ha</span></p>
        </div>
        <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center">
          <svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import BaseStatsCard from '@/components/common/BaseStatsCard.vue'

const props = defineProps({
  totalItems: {
    type: Number,
    required: true
  },
  farmers: {
    type: Array,
    required: true
  },
  allFincas: {
    type: Array,
    required: true
  }
})

const getTotalFarms = () => {
  return props.allFincas.length
}

const getActiveFarmers = () => {
  return props.farmers.filter(farmer => farmer.status === 'Activo').length
}

const getTotalArea = () => {
  return props.allFincas.reduce((total, finca) => {
    return total + Number.parseFloat(finca.hectareas || 0)
  }, 0).toFixed(1)
}
</script>

