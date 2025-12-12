<template>
  <BaseHomeLayout>
    <template #header>
      <HeaderView />
    </template>

    <template #hero>
      <HeroView />
    </template>

    <template #landing>
      <LandingView />
    </template>

    <template #features>
      <FeaturesView />
    </template>

    <template #about>
      <AboutView />
    </template>

    <template #footer>
      <FooterView />
    </template>
  </BaseHomeLayout>
</template>

<script setup>
import BaseHomeLayout from '@/components/common/BaseHomeLayout.vue'
import HeaderView from '@/components/Pages/HomeView/HeaderView.vue'
import LandingView from '@/components/Pages/HomeView/LandingView.vue'
import HeroView from '@/components/Pages/HomeView/HeroView.vue'
import FooterView from '@/components/Pages/HomeView/FooterView.vue'
import FeaturesView from '@/components/Pages/HomeView/FeaturesView.vue'
import AboutView from '@/components/Pages/HomeView/AboutView.vue'
</script>

<style scoped>
/* Custom styles */
.prose p {
  margin-bottom: 1rem;
}
</style>
