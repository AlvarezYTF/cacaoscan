<template>
  <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
    <BaseStatsCard
      label="Total Agricultores"
      :value="totalItems"
      icon="👥"
      color="green"
    />
    
    <BaseStatsCard
      label="Total Fincas"
      :value="getTotalFarms()"
      icon="🏠"
      color="blue"
    />
    
    <BaseStatsCard
      label="Activos"
      :value="getActiveFarmers()"
      icon="✓"
      color="purple"
    />
    
    <BaseStatsCard
      label="Área Total"
      :value="`${getTotalArea()} ha`"
      icon="📐"
      color="yellow"
    />
  </div>
</template>

<script setup>
import BaseStatsCard from '@/components/common/BaseStatsCard.vue'

const props = defineProps({
  totalItems: {
    type: Number,
    required: true
  },
  farmers: {
    type: Array,
    required: true
  },
  allFincas: {
    type: Array,
    required: true
  }
})

const getTotalFarms = () => {
  return props.allFincas.length
}

const getActiveFarmers = () => {
  return props.farmers.filter(farmer => farmer.status === 'Activo').length
}

const getTotalArea = () => {
  return props.allFincas.reduce((total, finca) => {
    return total + Number.parseFloat(finca.hectareas || 0)
  }, 0).toFixed(1)
}
</script>

