<template>
  <div :class="['base-scan-preferences', containerClass]">
    <!-- Header -->
    <div v-if="showHeader" class="flex items-center gap-3 mb-6">
      <div class="p-2 bg-green-100 rounded-xl">
        <slot name="header-icon">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </slot>
      </div>
      <h3 class="text-2xl font-bold text-gray-900">{{ title }}</h3>
    </div>

    <!-- Preferences Content -->
    <div class="space-y-5">
      <slot name="preferences" :preferences="modelValue" :update="updatePreference">
        <!-- Default preference fields can be provided via props or slots -->
      </slot>
    </div>

    <!-- Footer Actions -->
    <div v-if="showActions || $slots.actions" class="mt-6 flex gap-3">
      <slot name="actions">
        <button
          v-if="showSaveButton"
          @click="handleSave"
          class="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-xl transition-all duration-200 flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
          {{ saveButtonText }}
        </button>
        <button
          v-if="showResetButton"
          @click="handleReset"
          class="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-xl transition-all duration-200"
        >
          {{ resetButtonText }}
        </button>
      </slot>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
    default: () => ({})
  },
  title: {
    type: String,
    default: 'Preferencias de Escaneo'
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  showActions: {
    type: Boolean,
    default: true
  },
  showSaveButton: {
    type: Boolean,
    default: true
  },
  showResetButton: {
    type: Boolean,
    default: false
  },
  saveButtonText: {
    type: String,
    default: 'Guardar Preferencias'
  },
  resetButtonText: {
    type: String,
    default: 'Restablecer'
  },
  containerClass: {
    type: String,
    default: 'bg-white rounded-2xl border-2 border-gray-200 p-8 shadow-lg'
  }
})

const emit = defineEmits(['update:modelValue', 'save', 'reset'])

const updatePreference = (key, value) => {
  const updated = { ...props.modelValue, [key]: value }
  emit('update:modelValue', updated)
}

const handleSave = () => {
  emit('save', props.modelValue)
}

const handleReset = () => {
  emit('reset')
}
</script>

<style scoped>
.base-scan-preferences {
  @apply w-full;
}
</style>

