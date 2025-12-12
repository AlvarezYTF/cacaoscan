<template>
  <BaseHeader
    :title="`Bienvenido, ${farmerName} 👨‍🌾`"
    subtitle="Panel de control para el análisis de tus granos de cacao"
    header-class="dashboard-header mb-8"
  />
</template>

<script setup>
import BaseHeader from '@/components/common/BaseHeader.vue'

defineProps({
  farmerName: {
    type: String,
    default: 'Usuario'
  }
})
</script>

<style scoped>
.dashboard-header {
  margin-bottom: 2rem;
}
</style>
