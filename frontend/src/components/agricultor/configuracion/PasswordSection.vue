<template>
  <div class="bg-white rounded-2xl border-2 border-gray-200 p-8 shadow-lg">
    <div class="flex items-center gap-3 mb-6">
      <div class="p-2 bg-green-100 rounded-xl">
        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      </div>
      <h3 class="text-2xl font-bold text-gray-900">Cambiar Contraseña</h3>
    </div>

    <div class="space-y-5">
      <div>
        <label class="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          Contraseña actual
        </label>
        <div class="relative">
          <input 
            :type="showCurrentPassword ? 'text' : 'password'" 
            v-model="localPasswordForm.currentPassword" 
            placeholder="••••••••" 
            class="w-full px-4 py-3 pr-12 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500/30 focus:border-green-500 transition-all duration-200"
          >
          <button 
            @click="showCurrentPassword = !showCurrentPassword"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-green-600 transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="!showCurrentPassword" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path v-if="!showCurrentPassword" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L12 12m-3.122-3.122l4.243 4.243M12 12l3 3m0 0l6-6" />
            </svg>
          </button>
        </div>
      </div>

      <div>
        <label class="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
          Nueva contraseña
        </label>
        <div class="relative">
          <input 
            :type="showNewPassword ? 'text' : 'password'" 
            v-model="localPasswordForm.newPassword" 
            placeholder="••••••••" 
            class="w-full px-4 py-3 pr-12 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500/30 focus:border-green-500 transition-all duration-200"
          >
          <button 
            @click="showNewPassword = !showNewPassword"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-green-600 transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="!showNewPassword" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path v-if="!showNewPassword" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L12 12m-3.122-3.122l4.243 4.243M12 12l3 3m0 0l6-6" />
            </svg>
          </button>
        </div>
      </div>

      <div>
        <label class="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Confirmar nueva contraseña
        </label>
        <input 
          :type="showNewPassword ? 'text' : 'password'" 
          v-model="localPasswordForm.confirmPassword" 
          placeholder="••••••••" 
          class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500/30 focus:border-green-500 transition-all duration-200"
        >
      </div>
    </div>

    <button 
      @click="handleSave"
      :disabled="isLoading || !isFormValid"
      class="w-full mt-6 flex justify-center items-center gap-2 py-3.5 px-4 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white rounded-xl font-bold shadow-lg hover:shadow-xl transition-all duration-300 active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed"
    >
      <svg v-if="isLoading" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
      </svg>
      {{ isLoading ? 'Cambiando...' : 'Cambiar Contraseña' }}
    </button>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  isLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['save'])

const showCurrentPassword = ref(false)
const showNewPassword = ref(false)

const localPasswordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const isFormValid = computed(() => {
  return localPasswordForm.value.currentPassword && 
         localPasswordForm.value.newPassword && 
         localPasswordForm.value.confirmPassword &&
         localPasswordForm.value.newPassword === localPasswordForm.value.confirmPassword
})

const handleSave = () => {
  if (!isFormValid.value) return
  emit('save', { ...localPasswordForm.value })
  
  // Limpiar formulario
  localPasswordForm.value = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
}
</script>

