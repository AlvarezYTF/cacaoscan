<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
    <div class="bg-gradient-to-r from-green-50 to-green-50 px-6 py-4 border-b border-gray-200">
      <div class="flex items-center">
        <div class="bg-green-100 p-2 rounded-xl mr-3">
          <svg class="text-xl text-green-600 w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
          </svg>
        </div>
        <div>
          <h2 class="text-lg font-bold text-gray-900">Actividad Reciente</h2>
          <p class="text-sm text-gray-600">Últimos análisis realizados</p>
        </div>
      </div>
    </div>
    <div class="p-6">
      <div class="space-y-3">
        <div v-for="analysis in recentAnalyses" :key="analysis.id" @click="$emit('select-analysis', analysis)" class="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-green-50 transition-colors duration-200 cursor-pointer border border-gray-200 hover:border-green-300">
          <div class="flex items-center space-x-3">
            <div class="bg-green-500 p-2 rounded-lg">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
              </svg>
            </div>
            <div>
              <p class="text-sm font-bold text-gray-900">Lote #{{ analysis.id }}</p>
              <p class="text-xs text-gray-600">{{ analysis.date }}</p>
            </div>
          </div>
          <span class="px-3 py-1 bg-green-500 text-white rounded-full text-xs font-bold shadow-sm">{{ analysis.quality }}%</span>
        </div>
        <div v-if="recentAnalyses.length === 0" class="text-center py-8">
          <p class="text-gray-600 font-medium">No hay actividad reciente</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RecentActivity',
  emits: ['select-analysis'],
  props: {
    recentAnalyses: {
      type: Array,
      default: () => []
    }
  }
}
</script>

