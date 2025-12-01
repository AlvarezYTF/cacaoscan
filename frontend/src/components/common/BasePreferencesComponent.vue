<template>
  <BasePreferencesWrapper
    :model-value="modelValue"
    :title="title"
    :show-header="showHeader"
    :show-actions="showActions"
    :show-save-button="showSaveButton"
    :show-reset-button="showResetButton"
    :save-button-text="saveButtonText"
    :reset-button-text="resetButtonText"
    :container-class="containerClass"
    :icon-path="iconPath"
    :content-slot-name="contentSlotName"
    @update:model-value="$emit('update:modelValue', $event)"
    @save="$emit('save', $event)"
    @reset="$emit('reset')"
  >
    <template #header-icon>
      <slot name="header-icon"></slot>
    </template>
    <template #[contentSlotName]="{ value, update }">
      <slot :name="contentSlotName" :value="value" :update="update"></slot>
    </template>
    <template #actions>
      <slot name="actions"></slot>
    </template>
  </BasePreferencesWrapper>
</template>

<script setup>
import BasePreferencesWrapper from './BasePreferencesWrapper.vue'

defineProps({
  modelValue: {
    type: Object,
    required: true,
    default: () => ({})
  },
  title: {
    type: String,
    required: true
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
    default: 'Guardar'
  },
  resetButtonText: {
    type: String,
    default: 'Restablecer'
  },
  containerClass: {
    type: String,
    default: 'bg-white rounded-2xl border-2 border-gray-200 p-8 shadow-lg'
  },
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

