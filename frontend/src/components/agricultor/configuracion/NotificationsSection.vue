<template>
  <div class="bg-white rounded-2xl border-2 border-gray-200 p-8 shadow-lg">
    <div class="flex items-center gap-3 mb-6">
      <div class="p-2 bg-green-100 rounded-xl">
        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
      </div>
      <h3 class="text-2xl font-bold text-gray-900">Notificaciones</h3>
    </div>

    <div class="space-y-4">
      <!-- Notificaciones por email -->
      <div class="flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-gray-50 border-2 border-green-200 rounded-xl">
        <div class="flex items-center gap-3">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <div>
            <p class="font-semibold text-gray-900">Notificaciones por email</p>
            <p class="text-xs text-gray-500">Recibir alertas por correo electrónico</p>
          </div>
        </div>
        <button 
          @click="$emit('update:notifications', { ...notifications, email: !notifications.email })"
          class="relative w-14 h-8 rounded-full transition-colors duration-200"
          :class="notifications.email ? 'bg-green-600' : 'bg-gray-300'"
        >
          <span 
            class="absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform duration-200 shadow-lg"
            :class="notifications.email ? 'translate-x-6' : 'translate-x-0'"
          ></span>
        </button>
      </div>

      <!-- Notificaciones por WhatsApp -->
      <div class="flex items-center justify-between p-4 bg-gray-50 border-2 border-gray-200 rounded-xl">
        <div class="flex items-center gap-3">
          <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <div>
            <p class="font-semibold text-gray-900">Notificaciones por WhatsApp</p>
            <p class="text-xs text-gray-500">Recibir alertas instantáneas</p>
          </div>
        </div>
        <button 
          @click="$emit('update:notifications', { ...notifications, whatsapp: !notifications.whatsapp })"
          class="relative w-14 h-8 rounded-full transition-colors duration-200"
          :class="notifications.whatsapp ? 'bg-green-600' : 'bg-gray-300'"
        >
          <span 
            class="absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform duration-200 shadow-lg"
            :class="notifications.whatsapp ? 'translate-x-6' : 'translate-x-0'"
          ></span>
        </button>
      </div>

      <!-- Alertas de calidad -->
      <div class="flex items-center justify-between p-4 bg-gray-50 border-2 border-gray-200 rounded-xl">
        <div class="flex items-center gap-3">
          <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
          </svg>
          <div>
            <p class="font-semibold text-gray-900">Alertas de calidad</p>
            <p class="text-xs text-gray-500">Alertas sobre calidad del grano</p>
          </div>
        </div>
        <button 
          @click="$emit('update:notifications', { ...notifications, quality: !notifications.quality })"
          class="relative w-14 h-8 rounded-full transition-colors duration-200"
          :class="notifications.quality ? 'bg-green-600' : 'bg-gray-300'"
        >
          <span 
            class="absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform duration-200 shadow-lg"
            :class="notifications.quality ? 'translate-x-6' : 'translate-x-0'"
          ></span>
        </button>
      </div>

      <!-- Alertas ambientales -->
      <div class="flex items-center justify-between p-4 bg-gray-50 border-2 border-gray-200 rounded-xl">
        <div class="flex items-center gap-3">
          <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <p class="font-semibold text-gray-900">Alertas ambientales</p>
            <p class="text-xs text-gray-500">Temperatura, humedad, clima</p>
          </div>
        </div>
        <button 
          @click="$emit('update:notifications', { ...notifications, environment: !notifications.environment })"
          class="relative w-14 h-8 rounded-full transition-colors duration-200"
          :class="notifications.environment ? 'bg-green-600' : 'bg-gray-300'"
        >
          <span 
            class="absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform duration-200 shadow-lg"
            :class="notifications.environment ? 'translate-x-6' : 'translate-x-0'"
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
      {{ isLoading ? 'Guardando...' : 'Guardar Notificaciones' }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  notifications: {
    type: Object,
    required: true
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['update:notifications', 'save'])
</script>

