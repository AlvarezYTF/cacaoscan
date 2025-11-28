<template>
  <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
    <div class="bg-white rounded-xl border border-gray-200 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 p-6">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
            </svg>
          </div>
        </div>
        <div class="ml-4">
          <p class="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-1">Total Agricultores</p>
          <p class="text-2xl font-bold text-gray-900">{{ totalItems }}</p>
        </div>
      </div>
    </div>
    
    <div class="bg-white rounded-xl border border-gray-200 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 p-6">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
            </svg>
          </div>
        </div>
        <div class="ml-4">
          <p class="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-1">Total Fincas</p>
          <p class="text-2xl font-bold text-gray-900">{{ getTotalFarms() }}</p>
        </div>
      </div>
    </div>
    
    <div class="bg-white rounded-xl border border-gray-200 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 p-6">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
        </div>
        <div class="ml-4">
          <p class="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-1">Activos</p>
          <p class="text-2xl font-bold text-gray-900">{{ getActiveFarmers() }}</p>
        </div>
      </div>
    </div>
    
    <div class="bg-white rounded-xl border border-gray-200 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 p-6">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <div class="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9"></path>
            </svg>
          </div>
        </div>
        <div class="ml-4">
          <p class="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-1">Área Total</p>
          <p class="text-2xl font-bold text-gray-900">{{ getTotalArea() }} ha</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FarmersStatsCards',
  props: {
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
  },
  methods: {
    getTotalFarms() {
      return this.allFincas.length;
    },
    getActiveFarmers() {
      return this.farmers.filter(farmer => farmer.status === 'Activo').length;
    },
    getTotalArea() {
      return this.allFincas.reduce((total, finca) => {
        return total + Number.parseFloat(finca.hectareas || 0);
      }, 0).toFixed(1);
    }
  }
};
</script>

