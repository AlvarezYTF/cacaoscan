<template>
  <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
    <!-- Total Usuarios -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 p-6">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <div class="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
            </svg>
          </div>
        </div>
        <div class="ml-4">
          <p class="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-1">Total Usuarios</p>
          <p class="text-2xl font-bold text-gray-900">{{ totalUsers }}</p>
        </div>
      </div>
    </div>

    <!-- Activos -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 p-6">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
        </div>
        <div class="ml-4">
          <p class="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-1">Activos</p>
          <p class="text-2xl font-bold text-gray-900">{{ activeUsers }}</p>
        </div>
      </div>
    </div>

    <!-- Nuevos Hoy -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 p-6">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
          </div>
        </div>
        <div class="ml-4">
          <p class="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-1">Nuevos Hoy</p>
          <p class="text-2xl font-bold text-gray-900">{{ newUsersToday }}</p>
        </div>
      </div>
    </div>

    <!-- En Línea -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 p-6">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
          </div>
        </div>
        <div class="ml-4">
          <p class="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-1">En Línea</p>
          <p class="text-2xl font-bold text-gray-900">{{ onlineUsers }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UsersStatsCards',
  props: {
    totalUsers: {
      type: Number,
      required: true
    },
    activeUsers: {
      type: Number,
      required: true
    },
    newUsersToday: {
      type: Number,
      required: true
    },
    onlineUsers: {
      type: Number,
      required: true
    }
  }
}
</script>

