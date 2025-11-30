<template>
  <div :class="['base-stats-card', cardClass]">
    <div class="p-5">
      <div class="flex items-center">
        <!-- Icon -->
        <div 
          v-if="icon || $slots.icon"
          class="flex-shrink-0 rounded-md p-3"
          :class="iconBgClass"
        >
          <slot name="icon">
            <span v-if="icon" class="text-2xl">{{ icon }}</span>
          </slot>
        </div>

        <!-- Content -->
        <div :class="icon || $slots.icon ? 'ml-5 w-0 flex-1' : 'w-full'">
          <dl>
            <!-- Label -->
            <dt v-if="label || $slots.label" class="text-sm font-medium text-gray-500 truncate">
              <slot name="label">{{ label }}</slot>
            </dt>
            
            <!-- Value -->
            <dd class="flex items-baseline">
              <div :class="['text-2xl font-semibold', valueClass]">
                <slot name="value">{{ value }}</slot>
              </div>
              
              <!-- Trend/Percentage -->
              <div 
                v-if="trend !== null && trend !== undefined"
                :class="[
                  'ml-2 flex items-baseline text-sm font-semibold',
                  trend > 0 ? 'text-green-600' : trend < 0 ? 'text-red-600' : 'text-gray-500'
                ]"
              >
                <svg 
                  v-if="trend !== 0"
                  :class="[
                    'self-center flex-shrink-0 h-5 w-5',
                    trend > 0 ? 'text-green-500' : 'text-red-500'
                  ]" 
                  fill="currentColor" 
                  viewBox="0 0 20 20" 
                  aria-hidden="true"
                >
                  <path 
                    v-if="trend > 0"
                    fill-rule="evenodd" 
                    d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" 
                    clip-rule="evenodd" 
                  />
                  <path 
                    v-else
                    fill-rule="evenodd" 
                    d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" 
                    clip-rule="evenodd" 
                  />
                </svg>
                <span class="sr-only">
                  {{ trend > 0 ? 'Aumentó' : 'Disminuyó' }} en
                </span>
                {{ Math.abs(trend) }}%<span v-if="trendLabel" class="ml-1">{{ trendLabel }}</span>
              </div>
            </dd>
          </dl>
        </div>
      </div>
      
      <!-- Additional content slot -->
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: {
    type: String,
    default: ''
  },
  value: {
    type: [String, Number],
    default: ''
  },
  icon: {
    type: String,
    default: ''
  },
  color: {
    type: String,
    default: 'blue',
    validator: (value) => ['blue', 'green', 'purple', 'yellow', 'gray', 'red', 'orange'].includes(value)
  },
  trend: {
    type: Number,
    default: null
  },
  trendLabel: {
    type: String,
    default: 'desde el mes pasado'
  },
  cardClass: {
    type: String,
    default: 'bg-white overflow-hidden shadow rounded-lg'
  },
  valueClass: {
    type: String,
    default: 'text-gray-900'
  }
})

const iconBgClass = computed(() => {
  const colorMap = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    gray: 'bg-gray-100 text-gray-600',
    red: 'bg-red-100 text-red-600',
    orange: 'bg-orange-100 text-orange-600'
  }
  return colorMap[props.color] || colorMap.blue
})
</script>

<style scoped>
.base-stats-card {
  transition: all 0.2s;
}

.base-stats-card:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}
</style>
