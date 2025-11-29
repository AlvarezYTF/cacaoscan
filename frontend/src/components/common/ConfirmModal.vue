<template>
  <div class="confirm-modal-overlay" @click="cancel">
    <div class="confirm-modal-container" @click.stop>
      <div class="confirm-modal-header">
        <div class="header-icon">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <div class="header-content">
          <h3>{{ title }}</h3>
        </div>
      </div>

      <div class="confirm-modal-body">
        <p>{{ message }}</p>
        
        <div v-if="details" class="confirm-details">
          <h4>Detalles:</h4>
          <ul>
            <li v-for="detail in details" :key="detail">{{ detail }}</li>
          </ul>
        </div>

        <div v-if="warning" class="confirm-warning">
          <i class="fas fa-exclamation-circle"></i>
          <span>{{ warning }}</span>
        </div>
      </div>

      <div class="confirm-modal-footer">
        <button
          @click="cancel"
          class="btn btn-outline"
          :disabled="loading"
        >
          {{ cancelText }}
        </button>
        <button
          @click="confirm"
          class="btn"
          :class="confirmButtonClass"
          :disabled="loading"
        >
          <i v-if="loading" class="fas fa-spinner fa-spin"></i>
          <i v-else-if="confirmIcon" :class="confirmIcon"></i>
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConfirmModal',
  props: {
    title: {
      type: String,
      default: 'Confirmar Acción'
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
    }
  },
  emits: ['confirm', 'cancel'],
  methods: {
    confirm() {
      this.$emit('confirm')
    },
    cancel() {
      this.$emit('cancel')
    }
  }
}
</script>

<style scoped>
.confirm-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.confirm-modal-container {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  animation: modalAppear 0.2s ease-out;
}

@keyframes modalAppear {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.confirm-modal-header {
  padding: 1.5rem 2rem;
  background: #dc2626;
  color: white;
  display: flex;
  align-items: center;
  gap: 1rem;
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
}

.header-content h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.confirm-modal-body {
  padding: 2rem;
}

.confirm-modal-body p {
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
}

.confirm-modal-footer {
  padding: 1.5rem 2rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  background: #f8fafc;
}

.btn {
  display: inline-flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s ease-in-out;
  cursor: pointer;
  border: 1px solid transparent;
  gap: 0.5rem;
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
  background-color: #9b1c1c;
  color: #ffffff;
  border-color: #9b1c1c;
}

.btn-danger:hover:not(:disabled) {
  background-color: #7c1515;
  border-color: #7c1515;
}

.btn-primary {
  background-color: #1f4e79;
  color: #ffffff;
  border-color: #1f4e79;
}

.btn-primary:hover:not(:disabled) {
  background-color: #1a3d5b;
  border-color: #1a3d5b;
}

.btn-success {
  background-color: #046c4e;
  color: #ffffff;
  border-color: #046c4e;
}

.btn-success:hover:not(:disabled) {
  background-color: #03503a;
  border-color: #03503a;
}

.btn-warning {
  background-color: #8a4b00;
  color: #ffffff;
  border-color: #8a4b00;
}

.btn-warning:hover:not(:disabled) {
  background-color: #6c3a00;
  border-color: #6c3a00;
}

/* Responsive */
@media (max-width: 768px) {
  .confirm-modal-container {
    margin: 0.5rem;
  }
  
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
  .confirm-modal-overlay {
    padding: 0.25rem;
  }
  
  .confirm-modal-container {
    margin: 0;
    border-radius: 0;
  }
  
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
