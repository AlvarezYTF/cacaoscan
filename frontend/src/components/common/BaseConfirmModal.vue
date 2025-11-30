<template>
  <BaseModal
    :show="show"
    :title="title"
    :show-close-button="!loading"
    :close-on-overlay="!loading && closeOnOverlay"
    max-width="md"
    @close="handleCancel"
    @update:show="handleUpdateShow"
  >
    <template #header>
      <div class="confirm-modal-header" :class="headerVariantClass">
        <div class="header-icon">
          <i :class="headerIcon"></i>
        </div>
        <div class="header-content">
          <h3>{{ title }}</h3>
          <p v-if="subtitle" class="header-subtitle">{{ subtitle }}</p>
        </div>
      </div>
    </template>

    <div class="confirm-modal-body">
      <p class="confirm-message">{{ message }}</p>
      
      <div v-if="details && details.length > 0" class="confirm-details">
        <h4>Detalles:</h4>
        <ul>
          <li v-for="(detail, index) in details" :key="index">{{ detail }}</li>
        </ul>
      </div>

      <div v-if="warning" class="confirm-warning">
        <i class="fas fa-exclamation-circle"></i>
        <span>{{ warning }}</span>
      </div>
    </div>

    <template #footer>
      <div class="confirm-modal-footer">
        <button
          @click="handleCancel"
          class="btn btn-outline"
          :disabled="loading"
          type="button"
        >
          {{ cancelText }}
        </button>
        <button
          @click="handleConfirm"
          class="btn"
          :class="confirmButtonClass"
          :disabled="loading"
          type="button"
        >
          <i v-if="loading" class="fas fa-spinner fa-spin"></i>
          <i v-else-if="confirmIcon" :class="confirmIcon"></i>
          {{ confirmText }}
        </button>
      </div>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed } from 'vue'
import BaseModal from './BaseModal.vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Confirmar Acción'
  },
  subtitle: {
    type: String,
    default: null
  },
  message: {
    type: String,
    required: true
  },
  details: {
    type: Array,
    default: null
  },
  warning: {
    type: String,
    default: null
  },
  confirmText: {
    type: String,
    default: 'Confirmar'
  },
  cancelText: {
    type: String,
    default: 'Cancelar'
  },
  variant: {
    type: String,
    default: 'danger',
    validator: (value) => ['danger', 'warning', 'info', 'success', 'default'].includes(value)
  },
  confirmButtonClass: {
    type: String,
    default: 'btn-danger'
  },
  confirmIcon: {
    type: String,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  },
  closeOnOverlay: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['confirm', 'cancel', 'update:show'])

const headerVariantClass = computed(() => {
  return `variant-${props.variant}`
})

const headerIcon = computed(() => {
  const icons = {
    danger: 'fas fa-exclamation-triangle',
    warning: 'fas fa-exclamation-circle',
    info: 'fas fa-info-circle',
    success: 'fas fa-check-circle',
    default: 'fas fa-question-circle'
  }
  return icons[props.variant] || icons.default
})

const handleConfirm = () => {
  if (!props.loading) {
    emit('confirm')
  }
}

const handleCancel = () => {
  if (!props.loading) {
    emit('cancel')
    emit('update:show', false)
  }
}

const handleUpdateShow = (value) => {
  emit('update:show', value)
}
</script>

<style scoped>
.confirm-modal-header {
  padding: 1.5rem 2rem;
  color: white;
  display: flex;
  align-items: center;
  gap: 1rem;
  border-radius: 12px 12px 0 0;
}

.confirm-modal-header.variant-danger {
  background: #dc2626;
}

.confirm-modal-header.variant-warning {
  background: #f59e0b;
}

.confirm-modal-header.variant-info {
  background: #3b82f6;
}

.confirm-modal-header.variant-success {
  background: #10b981;
}

.confirm-modal-header.variant-default {
  background: #6b7280;
}

.header-icon {
  width: 3rem;
  height: 3rem;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.header-content {
  flex: 1;
}

.header-content h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: white;
}

.header-subtitle {
  margin: 0.25rem 0 0 0;
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.9);
}

.confirm-modal-body {
  padding: 2rem;
}

.confirm-message {
  margin: 0 0 1.5rem 0;
  color: #374151;
  font-size: 1rem;
  line-height: 1.5;
}

.confirm-details {
  margin-bottom: 1.5rem;
}

.confirm-details h4 {
  margin: 0 0 0.75rem 0;
  color: #1f2937;
  font-size: 0.875rem;
  font-weight: 600;
}

.confirm-details ul {
  margin: 0;
  padding-left: 1.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.confirm-details li {
  margin-bottom: 0.25rem;
}

.confirm-warning {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: #fef2f2;
  border: 1px solid #fca5a5;
  border-radius: 0.5rem;
  color: #991b1b;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.confirm-warning i {
  font-size: 1.125rem;
  color: #ef4444;
  flex-shrink: 0;
}

.confirm-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem 2rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s ease-in-out;
  cursor: pointer;
  border: 1px solid transparent;
}

.btn:active {
  transform: scale(0.98);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-outline {
  background-color: transparent;
  color: #374151;
  border-color: #d1d5db;
}

.btn-outline:hover:not(:disabled) {
  background-color: #f9fafb;
  border-color: #9ca3af;
}

.btn-danger {
  background-color: #dc2626;
  color: #ffffff;
  border-color: #dc2626;
}

.btn-danger:hover:not(:disabled) {
  background-color: #b91c1c;
  border-color: #b91c1c;
}

.btn-primary {
  background-color: #2563eb;
  color: #ffffff;
  border-color: #2563eb;
}

.btn-primary:hover:not(:disabled) {
  background-color: #1d4ed8;
  border-color: #1d4ed8;
}

.btn-success {
  background-color: #047857;
  color: #ffffff;
  border-color: #047857;
}

.btn-success:hover:not(:disabled) {
  background-color: #047857;
  color: #ffffff;
  border-color: #047857;
}

.btn-warning {
  background-color: #b45309;
  color: #ffffff;
  border-color: #b45309;
}

.btn-warning:hover:not(:disabled) {
  background-color: #b45309;
  color: #ffffff;
  border-color: #b45309;
}

/* Responsive */
@media (max-width: 768px) {
  .confirm-modal-header {
    padding: 1rem;
  }
  
  .confirm-modal-body {
    padding: 1rem;
  }
  
  .confirm-modal-footer {
    padding: 1rem;
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .header-icon {
    width: 2.5rem;
    height: 2.5rem;
    font-size: 1rem;
  }
  
  .header-content h3 {
    font-size: 1.25rem;
  }
  
  .btn {
    padding: 0.625rem 1rem;
    font-size: 0.8125rem;
  }
}
</style>

