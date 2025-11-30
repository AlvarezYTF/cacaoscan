<template>
  <section :class="['base-hero', backgroundClass, containerClass]">
    <!-- Decorative elements -->
    <div v-if="showDecorations" class="absolute inset-0 opacity-10">
      <div class="absolute top-0 left-0 w-96 h-96 bg-white rounded-full -translate-x-1/2 -translate-y-1/2 blur-3xl"></div>
      <div class="absolute bottom-0 right-0 w-96 h-96 bg-white rounded-full translate-x-1/2 translate-y-1/2 blur-3xl"></div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
      <!-- Badge -->
      <div v-if="badge" class="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full mb-6 border border-white/20">
        <slot name="badge-icon">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </slot>
        <span class="text-sm font-medium">{{ badge }}</span>
      </div>

      <!-- Title -->
      <h1 :class="['base-hero-title', titleClass]">
        <slot name="title">{{ title }}</slot>
      </h1>
      
      <!-- Subtitle -->
      <p v-if="subtitle || $slots.subtitle" :class="['base-hero-subtitle', subtitleClass]">
        <slot name="subtitle">{{ subtitle }}</slot>
      </p>
      
      <!-- CTA Buttons -->
      <div v-if="ctaText || ctaLink || $slots.cta" class="flex flex-col sm:flex-row justify-center gap-4 mt-10">
        <slot name="cta">
          <button 
            v-if="ctaText"
            @click="handleCtaClick"
            class="group bg-white text-green-600 hover:bg-gray-50 font-semibold py-4 px-10 rounded-xl text-lg shadow-xl hover:shadow-2xl transition-all duration-200 hover:scale-105 active:scale-100 transform"
          >
            <span class="flex items-center justify-center gap-2">
              {{ ctaText }}
              <svg class="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </span>
          </button>
        </slot>
      </div>

      <!-- Trust indicators -->
      <div v-if="trustIndicators && trustIndicators.length > 0" class="mt-16 flex flex-wrap items-center justify-center gap-8 text-sm">
        <div v-for="(indicator, index) in trustIndicators" :key="index" class="flex items-center gap-2">
          <slot :name="`indicator-icon-${index}`">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </slot>
          <span class="opacity-90">{{ indicator }}</span>
        </div>
      </div>

      <!-- Additional content slot -->
      <slot name="content"></slot>
    </div>
  </section>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  badge: {
    type: String,
    default: ''
  },
  ctaText: {
    type: String,
    default: ''
  },
  ctaLink: {
    type: String,
    default: ''
  },
  backgroundImage: {
    type: String,
    default: ''
  },
  backgroundClass: {
    type: String,
    default: 'bg-green-600 text-white'
  },
  titleClass: {
    type: String,
    default: 'text-4xl md:text-6xl lg:text-7xl font-bold mb-6 animate-fade-in-up'
  },
  subtitleClass: {
    type: String,
    default: 'text-lg md:text-xl lg:text-2xl mb-10 max-w-3xl mx-auto opacity-95 leading-relaxed'
  },
  containerClass: {
    type: String,
    default: 'py-24 relative overflow-hidden'
  },
  showDecorations: {
    type: Boolean,
    default: true
  },
  trustIndicators: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['cta-click'])

const router = useRouter()

const handleCtaClick = () => {
  if (props.ctaLink) {
    router.push(props.ctaLink)
  }
  emit('cta-click')
}
</script>

<style scoped>
.base-hero {
  @apply relative;
}

.base-hero-title {
  @apply text-4xl md:text-6xl lg:text-7xl font-bold mb-6;
}

.base-hero-subtitle {
  @apply text-lg md:text-xl lg:text-2xl mb-10 max-w-3xl mx-auto opacity-95 leading-relaxed;
}

@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fade-in-up 0.8s ease-out;
}
</style>

