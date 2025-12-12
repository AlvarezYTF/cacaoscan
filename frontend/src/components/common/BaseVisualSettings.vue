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
      <slot :name="contentSlotName" :settings="value" :update="update"></slot>
    </template>
    <template #actions>
      <slot name="actions"></slot>
    </template>
  </BasePreferencesWrapper>
</template>

<script setup>
import BasePreferencesWrapper from './BasePreferencesWrapper.vue'
import { 
  createPreferenceWrapperProps, 
  getPreferenceIconPath, 
  getPreferenceContentSlotName 
} from '@/composables/usePreferencesWrapperConfig'

const PREFERENCE_TYPE = 'VISUAL'

const props = defineProps(createPreferenceWrapperProps(PREFERENCE_TYPE))

const iconPath = getPreferenceIconPath(PREFERENCE_TYPE)
const contentSlotName = getPreferenceContentSlotName(PREFERENCE_TYPE)

defineEmits(['update:modelValue', 'save', 'reset'])
</script>

