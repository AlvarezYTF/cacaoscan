<script setup>
import { RouterView } from 'vue-router'
import GlobalLoader from '@/components/common/GlobalLoader.vue'

</script>

<template>
  <div class="app">
    <!-- Router view principal -->
    <RouterView />
    
    <!-- Global loading overlay -->
    <GlobalLoader />
  </div>
</template>

<script>

export default {
  name: 'App',
}

</script>
