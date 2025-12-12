<template>
  <BaseToggleSwitch
    :model-value="modelValue"
    :label="label"
    :description="description"
    :required="required"
    :disabled="disabled"
    :error="error"
    :helper-text="helperText"
    @update:modelValue="$emit('update:modelValue', $event)"
  />
</template>

<script setup>
import BaseToggleSwitch from '@/components/common/BaseToggleSwitch.vue'

defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  label: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  helperText: {
    type: String,
    default: ''
  }
})

defineEmits(['update:modelValue'])
</script>

