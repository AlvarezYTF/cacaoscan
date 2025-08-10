<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <!-- Header -->
    <HeaderView />

    <!-- Hero -->
    <HeroView />


    <!-- Features -->
    <FeaturesView />

    <!-- About -->
    <AboutView />

    <!-- Footer -->
    <FooterView />

  </div>
</template>

<script setup>
// Pinia store can be imported here when needed
// import { useMainStore } from '@/stores/main'
// const store = useMainStore()
import HeaderView from '@/components/HomeViewComponents/HeaderView.vue';
import HeroView from '@/components/HomeViewComponents/HeroView.vue';
import FooterView from '@/components/HomeViewComponents/FooterView.vue';
import FeaturesView from '@/components/HomeViewComponents/FeaturesView.vue';
import AboutView from '@/components/HomeViewComponents/AboutView.vue';
</script>

<style scoped>
/* Custom styles */
.prose p {
  margin-bottom: 1rem;
}
</style>
