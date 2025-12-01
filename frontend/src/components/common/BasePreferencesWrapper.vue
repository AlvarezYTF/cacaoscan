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
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="iconPath" />
        </svg>
      </slot>
    </template>
    <template #content="{ value, update }">
      <slot :name="contentSlotName" :value="value" :update="update">
        <!-- Default content can be provided via props or slots -->
      </slot>
    </template>
    <template #actions>
      <slot name="actions"></slot>
    </template>
  </BasePreferences>
</template>

<script setup>
import BasePreferences from './BasePreferences.vue'
import { basePreferencesProps } from '@/composables/usePreferencesProps'

// Additional props specific to wrapper
defineProps({
  ...basePreferencesProps,
  iconPath: {
    type: String,
    required: true
  },
  contentSlotName: {
    type: String,
    default: 'content'
  }
})

defineEmits(['update:modelValue', 'save', 'reset'])
</script>
