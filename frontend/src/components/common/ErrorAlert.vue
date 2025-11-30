<template>
  <BaseAlert
    variant="error"
    :message="message"
    :show="show"
  />
</template>

<script setup>
import BaseAlert from './BaseAlert.vue'

defineProps({
  message: {
    type: String,
    required: true
  },
  show: {
    type: Boolean,
    default: true
  }
})
</script>
