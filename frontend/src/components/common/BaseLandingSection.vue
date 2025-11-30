<template>
  <section :class="['base-landing-section', backgroundClass, containerClass]">
    <div class="max-w-7xl mx-auto">
      <slot name="content">
        <!-- Default content structure -->
        <div v-if="title" class="text-center mb-8">
          <h2 v-if="title" :class="['base-landing-title', titleClass]">
            {{ title }}
          </h2>
          <p v-if="subtitle" :class="['base-landing-subtitle', subtitleClass]">
            {{ subtitle }}
          </p>
        </div>
      </slot>
      <slot name="footer"></slot>
    </div>
  </section>
</template>

<script setup>
const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  background: {
    type: String,
    default: 'bg-white'
  },
  backgroundClass: {
    type: String,
    default: 'bg-white'
  },
  containerClass: {
    type: String,
    default: 'py-12 md:py-20 px-4'
  },
  titleClass: {
    type: String,
    default: 'text-2xl md:text-3xl lg:text-4xl font-bold text-gray-900 mb-3 md:mb-4'
  },
  subtitleClass: {
    type: String,
    default: 'text-base md:text-lg text-gray-700 max-w-2xl mx-auto leading-relaxed'
  }
})
</script>

<style scoped>
.base-landing-section {
  @apply relative overflow-hidden;
}

.base-landing-title {
  @apply text-2xl md:text-3xl lg:text-4xl font-bold text-gray-900 mb-3 md:mb-4;
}

.base-landing-subtitle {
  @apply text-base md:text-lg text-gray-700 max-w-2xl mx-auto leading-relaxed;
}
</style>

