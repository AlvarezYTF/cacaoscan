<template>
  <button 
    :class="buttonClasses"
    @click="$emit('click')"
    class="px-4 py-2 rounded-md text-sm font-medium flex items-center justify-center transition-all duration-200 transform hover:scale-105 active:scale-95"
  >
    <component :is="icon" v-if="icon" class="w-4 h-4 mr-2" />
    <span class="hidden sm:inline">{{ label }}</span>
    <span class="sm:hidden">{{ shortLabel }}</span>
  </button>
</template>

<script>
export default {
  name: 'ActionButton',
  props: {
    label: {
      type: String,
      required: true
    },
    shortLabel: {
      type: String,
      default: ''
    },
    variant: {
      type: String,
      default: 'primary', // primary, secondary, danger
      validator: (value) => ['primary', 'secondary', 'danger'].includes(value)
    },
    icon: {
      type: String,
      default: null
    }
  },
  computed: {
    buttonClasses() {
      const baseClasses = 'font-medium';
      
      switch (this.variant) {
        case 'primary':
          return `${baseClasses} bg-green-600 text-white hover:bg-green-700`;
        case 'secondary':
          return `${baseClasses} bg-white border border-gray-300 text-gray-700 hover:bg-gray-50`;
        case 'danger':
          return `${baseClasses} bg-red-600 text-white hover:bg-red-700`;
        default:
          return `${baseClasses} bg-green-600 text-white hover:bg-green-700`;
      }
    }
  },
  emits: ['click']
};
</script>
