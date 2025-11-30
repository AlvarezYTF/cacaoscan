<template>
  <div class="min-h-screen flex flex-col bg-gray-50" :class="containerClass">
    <!-- Header -->
    <header v-if="$slots.header || showHeader" class="flex-shrink-0">
      <slot name="header">
        <!-- Default header if no slot provided -->
      </slot>
    </header>

    <!-- Hero Section -->
    <section v-if="$slots.hero" class="flex-shrink-0">
      <slot name="hero"></slot>
    </section>

    <!-- Main Content -->
    <main class="flex-1">
      <!-- Landing Section -->
      <section v-if="$slots.landing" class="flex-shrink-0">
        <slot name="landing"></slot>
      </section>

      <!-- Features Section -->
      <section v-if="$slots.features" class="flex-shrink-0">
        <slot name="features"></slot>
      </section>

      <!-- About Section -->
      <section v-if="$slots.about" class="flex-shrink-0">
        <slot name="about"></slot>
      </section>

      <!-- Default content slot -->
      <slot></slot>
    </main>

    <!-- Footer -->
    <footer v-if="$slots.footer || showFooter" class="flex-shrink-0">
      <slot name="footer">
        <!-- Default footer if no slot provided -->
      </slot>
    </footer>
  </div>
</template>

<script setup>
defineProps({
  containerClass: {
    type: String,
    default: ''
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  showFooter: {
    type: Boolean,
    default: true
  }
})
</script>

<style scoped>
/* Styles handled by Tailwind classes */
</style>

