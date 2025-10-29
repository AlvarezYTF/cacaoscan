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
import HeaderView     from '@/components/Pages/HomeView/HeaderView.vue';
import HeroView       from '@/components/Pages/HomeView/HeroView.vue';
import FooterView     from '@/components/Pages/HomeView/FooterView.vue';
import FeaturesView   from '@/components/Pages/HomeView/FeaturesView.vue';
import AboutView      from '@/components/Pages/HomeView/AboutView.vue';
</script>

<style scoped>
/* Custom styles */
.prose p {
  margin-bottom: 1rem;
}
</style>
