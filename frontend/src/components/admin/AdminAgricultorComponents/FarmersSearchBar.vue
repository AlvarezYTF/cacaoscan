<template>
  <BaseSearchBar
    :model-value="searchQuery"
    :placeholder="placeholder"
    search-cy="filter-agricultores"
    @update:model-value="$emit('update:searchQuery', $event)"
    @clear="$emit('update:searchQuery', '')"
  />
</template>

<script setup>
import BaseSearchBar from '@/components/common/BaseSearchBar.vue'

defineProps({
  searchQuery: {
    type: String,
    required: true
  },
  placeholder: {
    type: String,
    default: 'Buscar cacaocultor por nombre, email o finca...'
  }
})

defineEmits(['update:searchQuery'])
</script>
