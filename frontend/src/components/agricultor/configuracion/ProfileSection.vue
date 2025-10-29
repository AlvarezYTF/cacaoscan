<template>
  <div class="bg-white rounded-2xl border-2 border-gray-200 p-8 shadow-lg">
    <!-- Header del formulario -->
    <div class="text-center mb-8">
      <h2 class="text-3xl font-bold text-gray-900 mb-2">Datos Personales</h2>
      <p class="text-gray-600 text-base">Actualiza tu información personal</p>
    </div>

    <!-- Foto de perfil -->
    <div class="flex items-center justify-center gap-4 mb-8">
      <div class="relative">
        <div class="w-24 h-24 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center text-white text-3xl font-bold shadow-lg">
          {{ userInitials }}
        </div>
        <button class="absolute -bottom-1 -right-1 p-2.5 bg-green-600 rounded-full text-white hover:bg-green-700 transition-colors shadow-lg">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </button>
      </div>
      <div>
        <p class="font-semibold text-gray-900 text-lg">{{ userProfile.fullName || 'Sin nombre' }}</p>
        <p class="text-sm text-gray-500">Sube una foto para personalizar tu perfil</p>
      </div>
    </div>

    <form class="space-y-6">
      <!-- Nombre completo en una sola línea -->
      <div>
        <label class="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          Nombre completo *
        </label>
        <div class="relative">
          <input 
            type="text" 
            :value="userProfile.fullName" 
            @input="updateFullName($event)"
            placeholder="Tu nombre completo" 
            :disabled="isLoading"
            class="w-full pl-4 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
            :class="{ 'border-green-300': userProfile.fullName && isValid }"
          />
          <div v-if="userProfile.fullName && isValid && !isLoading" class="absolute inset-y-0 right-0 pr-3 flex items-center">
            <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </div>
      </div>
      
      <!-- Email (solo lectura) -->
      <div>
        <label class="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          Email
        </label>
        <div class="relative">
          <input 
            type="email" 
            :value="userProfile.email" 
            placeholder="tu@email.com" 
            readonly 
            :disabled="isLoading"
            class="w-full pl-4 pr-4 py-3 border-2 border-gray-200 rounded-lg bg-gray-100 cursor-not-allowed"
          />
          <div v-if="!isVerified" class="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
            <span class="px-2 py-1 text-xs font-semibold bg-amber-100 text-amber-700 rounded-full">
              No verificado
            </span>
          </div>
          <div v-else class="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="px-2 py-1 text-xs font-semibold bg-green-100 text-green-700 rounded-full">
              Verificado
            </span>
          </div>
        </div>
        <Transition
          enter-active-class="transform ease-out duration-200"
          enter-from-class="opacity-0 -translate-y-1"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition ease-in duration-150"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0"
        >
          <p v-if="!isVerified" class="mt-1.5 text-sm text-amber-600 font-medium flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <a href="/email-verification" class="text-green-600 font-semibold hover:underline">Verifica tu email para activar todas las funciones</a>
          </p>
        </Transition>
        <p v-if="isVerified" class="mt-1.5 text-sm text-gray-500 flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Contacta al administrador para cambiar tu email
        </p>
      </div>
      
      <!-- Teléfono -->
      <div>
        <label class="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
          </svg>
          Teléfono (opcional)
        </label>
        <div class="relative">
          <input 
            type="tel" 
            :value="userProfile.phone" 
            @input="updatePhone($event)"
            placeholder="+57 300 123 4567" 
            :disabled="isLoading"
            class="w-full pl-4 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
            :class="{ 'border-green-300': userProfile.phone && isValid }"
          />
          <div v-if="userProfile.phone && isValid && !isLoading" class="absolute inset-y-0 right-0 pr-3 flex items-center">
            <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Botón de guardar -->
      <div>
        <button 
          @click.prevent="$emit('save')"
          :disabled="isLoading || !isFormValid"
          class="w-full flex justify-center items-center gap-2 py-3.5 px-4 border border-transparent rounded-xl shadow-lg text-base font-semibold text-white bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 focus:outline-none focus:ring-4 focus:ring-green-500/50 disabled:opacity-60 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-xl active:scale-[0.97] group"
        >
          <svg
            v-if="isLoading"
            class="animate-spin h-5 w-5 text-white"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <span>{{ isLoading ? 'Guardando...' : 'Guardar Cambios' }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  userProfile: {
    type: Object,
    required: true
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  isVerified: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:userProfile', 'save'])

// Computed para iniciales del usuario
const userInitials = computed(() => {
  const name = props.userProfile.fullName || ''
  const parts = name.split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.length > 0 ? name[0].toUpperCase() : 'U'
})

// Validación del formulario
const isValid = computed(() => {
  return !!props.userProfile.fullName && props.userProfile.fullName.trim().length > 0
})

const isFormValid = computed(() => {
  return isValid.value && !props.isLoading
})

// Funciones de actualización
const updateFullName = (event) => {
  emit('update:userProfile', { ...props.userProfile, fullName: event.target.value })
}

const updatePhone = (event) => {
  emit('update:userProfile', { ...props.userProfile, phone: event.target.value })
}
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.6s ease-out;
}
</style>

