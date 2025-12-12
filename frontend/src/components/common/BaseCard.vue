<template>
  <div 
    class="base-card" 
    :class="cardClasses"
    @click="handleClick"
  >
    <!-- Card Header -->
    <div v-if="$slots.header || title || icon" class="base-card-header">
      <div v-if="icon || $slots.icon" class="base-card-icon">
        <slot name="icon">
          <i v-if="icon" :class="icon"></i>
        </slot>
      </div>
      <div v-if="title || $slots.title" class="base-card-title">
        <slot name="title">
          <h4 v-if="title">{{ title }}</h4>
        </slot>
        <div v-if="$slots.meta" class="base-card-meta">
          <slot name="meta"></slot>
        </div>
      </div>
      <div v-if="$slots.headerActions" class="base-card-header-actions">
        <slot name="headerActions"></slot>
      </div>
    </div>

    <!-- Card Body -->
    <div class="base-card-body">
      <slot></slot>
    </div>

    <!-- Card Footer -->
    <div v-if="$slots.footer || $slots.actions" class="base-card-footer">
      <div v-if="$slots.footer" class="base-card-footer-content">
        <slot name="footer"></slot>
      </div>
      <div v-if="$slots.actions" class="base-card-actions">
        <slot name="actions"></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'success', 'error', 'warning', 'info'].includes(value)
  },
  clickable: {
    type: Boolean,
    default: false
  },
  bordered: {
    type: Boolean,
    default: true
  },
  shadow: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['click'])

const cardClasses = computed(() => {
  return [
    `base-card-${props.variant}`,
    {
      'base-card-clickable': props.clickable,
      'base-card-bordered': props.bordered,
      'base-card-shadow': props.shadow
    }
  ]
})

const handleClick = (event) => {
  if (props.clickable) {
    emit('click', event)
  }
}
</script>

<style scoped>
.base-card {
  background: white;
  border-radius: 0.75rem;
  overflow: hidden;
  transition: all 0.2s;
}

.base-card-bordered {
  border: 1px solid #e5e7eb;
}

.base-card-shadow {
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

.base-card-clickable {
  cursor: pointer;
}

.base-card-clickable:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.base-card-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
}

.base-card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.5rem;
  background: #f3f4f6;
  color: #4b5563;
  flex-shrink: 0;
}

.base-card-title {
  flex: 1;
  min-width: 0;
}

.base-card-title h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.5;
}

.base-card-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.base-card-header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.base-card-body {
  padding: 1.25rem;
}

.base-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.base-card-footer-content {
  flex: 1;
}

.base-card-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Variants */
.base-card-success {
  border-left: 4px solid #10b981;
}

.base-card-error {
  border-left: 4px solid #ef4444;
}

.base-card-warning {
  border-left: 4px solid #f59e0b;
}

.base-card-info {
  border-left: 4px solid #3b82f6;
}

.base-card-default {
  border-left: 4px solid #e5e7eb;
}
</style>

