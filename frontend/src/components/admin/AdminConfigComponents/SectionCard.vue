<template>
  <BaseSectionCard
    :title="title"
    :description="description"
    :icon="icon"
    container-class="mb-6"
  >
    <slot />
  </BaseSectionCard>
</template>

<script setup>
import BaseSectionCard from '@/components/common/BaseSectionCard.vue'

defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  icon: {
    type: Object,
    default: null
  }
})
</script>
