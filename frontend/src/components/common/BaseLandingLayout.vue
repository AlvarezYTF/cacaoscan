<template>
  <div class="min-h-screen bg-white flex flex-col">
    <!-- Header slot -->
    <header v-if="$slots.header" class="sticky top-0 z-40 bg-white border-b border-gray-200">
      <slot name="header" />
    </header>

    <!-- Main content -->
    <main class="flex-1">
      <slot />
    </main>

    <!-- Footer slot -->
    <footer v-if="$slots.footer" class="bg-gray-900 text-white">
      <slot name="footer" />
    </footer>
  </div>
</template>

<script setup>
// Base landing layout component
// Provides consistent structure for landing pages
</script>

<style scoped>
/* Additional styles if needed */
</style>

