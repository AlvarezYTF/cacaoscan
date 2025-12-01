<template>
  <BasePreferences
    :model-value="modelValue"
    :title="title"
    :show-header="showHeader"
    :show-actions="showActions"
    :show-save-button="showSaveButton"
    :show-reset-button="showResetButton"
    :save-button-text="saveButtonText"
    :reset-button-text="resetButtonText"
    :container-class="containerClass"
    @update:model-value="$emit('update:modelValue', $event)"
    @save="$emit('save', $event)"
    @reset="$emit('reset')"
  >
    <template #header-icon>
      <slot name="header-icon">
        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      </slot>
    </template>
    <template #content="{ value, update }">
      <slot name="preferences" :preferences="value" :update="update">
        <!-- Default preference fields can be provided via props or slots -->
      </slot>
    </template>
    <template #actions>
      <slot name="actions"></slot>
    </template>
  </BasePreferences>
</template>

<script setup>
import BasePreferences from './BasePreferences.vue'

defineProps({
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

defineEmits(['update:modelValue', 'save', 'reset'])
</script>

