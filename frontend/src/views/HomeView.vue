<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <!-- Header -->
    <HeaderView />
  </div>
</template>

<script setup>
// Pinia store can be imported here when needed
// import { useMainStore } from '@/stores/main'
// const store = useMainStore()
import HeaderView from '@/components/HomeViewComponents/HeaderView.vue';
</script>

<style scoped>
/* Custom styles */
.prose p {
  margin-bottom: 1rem;
}
</style>
