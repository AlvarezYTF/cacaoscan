<template>
  <div class="dashboard-widget" :class="widgetClass">
    <div class="widget-header">
      <div class="widget-title">
        <i v-if="icon" :class="icon" class="widget-icon"></i>
        <h3>{{ title }}</h3>
      </div>
      <div class="widget-actions">
        <slot name="actions"></slot>
        <button 
          v-if="refreshable" 
          @click="handleRefresh" 
          class="refresh-btn"
          :disabled="loading"
        >
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
        </button>
      </div>
    </div>
    
    <div class="widget-content">
      <div v-if="loading" class="widget-loading">
        <div class="loading-spinner"></div>
        <p>{{ loadingText }}</p>
      </div>
      
      <div v-else-if="error" class="widget-error">
        <i class="fas fa-exclamation-triangle"></i>
        <p>{{ error }}</p>
        <button v-if="retryable" @click="handleRetry" class="retry-btn">
          Reintentar
        </button>
      </div>
      
      <div v-else class="widget-body">
        <slot></slot>
      </div>
    </div>
    
    <div v-if="footer" class="widget-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'DashboardWidget',
  props: {
    title: {
      type: String,
      required: true
    },
    icon: {
      type: String,
      default: ''
    },
    variant: {
      type: String,
      default: 'default',
      validator: (value) => ['default', 'primary', 'success', 'warning', 'danger', 'info'].includes(value)
    },
    size: {
      type: String,
      default: 'medium',
      validator: (value) => ['small', 'medium', 'large', 'full'].includes(value)
    },
    loading: {
      type: Boolean,
      default: false
    },
    loadingText: {
      type: String,
      default: 'Cargando...'
    },
    error: {
      type: String,
      default: ''
    },
    refreshable: {
      type: Boolean,
      default: true
    },
    retryable: {
      type: Boolean,
      default: true
    },
    footer: {
      type: Boolean,
      default: false
    },
    clickable: {
      type: Boolean,
      default: false
    }
  },
  emits: ['refresh', 'retry', 'click'],
  setup(props, { emit }) {
    // Clase CSS del widget
    const widgetClass = computed(() => {
      return [
        `widget-${props.variant}`,
        `widget-${props.size}`,
        {
          'widget-loading': props.loading,
          'widget-error': props.error,
          'widget-clickable': props.clickable
        }
      ]
    })

    // Manejar refresh
    const handleRefresh = () => {
      emit('refresh')
    }

    // Manejar retry
    const handleRetry = () => {
      emit('retry')
    }

    // Manejar click
    const handleClick = () => {
      if (props.clickable) {
        emit('click')
      }
    }

    return {
      widgetClass,
      handleRefresh,
      handleRetry,
      handleClick
    }
  }
}
</script>

<style scoped>
.dashboard-widget {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  overflow: hidden;
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.dashboard-widget:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.dashboard-widget.widget-clickable {
  cursor: pointer;
}

.dashboard-widget.widget-clickable:hover {
  transform: translateY(-2px);
}

/* Variantes */
.widget-primary {
  border-left: 4px solid #3b82f6;
}

.widget-success {
  border-left: 4px solid #10b981;
}

.widget-warning {
  border-left: 4px solid #f59e0b;
}

.widget-danger {
  border-left: 4px solid #ef4444;
}

.widget-info {
  border-left: 4px solid #06b6d4;
}

/* Tamaños */
.widget-small {
  min-height: 200px;
}

.widget-medium {
  min-height: 300px;
}

.widget-large {
  min-height: 400px;
}

.widget-full {
  min-height: 500px;
}

/* Header */
.widget-header {
  padding: 20px 20px 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f3f4f6;
  margin-bottom: 20px;
}

.widget-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.widget-icon {
  font-size: 1.25rem;
  color: #6b7280;
}

.widget-primary .widget-icon {
  color: #3b82f6;
}

.widget-success .widget-icon {
  color: #10b981;
}

.widget-warning .widget-icon {
  color: #f59e0b;
}

.widget-danger .widget-icon {
  color: #ef4444;
}

.widget-info .widget-icon {
  color: #06b6d4;
}

.widget-title h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

.widget-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.refresh-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.refresh-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Content */
.widget-content {
  flex: 1;
  padding: 0 20px;
}

.widget-body {
  height: 100%;
}

/* Loading */
.widget-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #6b7280;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f4f6;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.widget-loading p {
  margin: 0;
  font-size: 0.875rem;
}

/* Error */
.widget-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #ef4444;
  text-align: center;
}

.widget-error i {
  font-size: 2rem;
  margin-bottom: 12px;
}

.widget-error p {
  margin: 0 0 16px 0;
  font-size: 0.875rem;
}

.retry-btn {
  background: #ef4444;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-btn:hover {
  background: #dc2626;
}

/* Footer */
.widget-footer {
  padding: 16px 20px;
  border-top: 1px solid #f3f4f6;
  background: #f9fafb;
}

/* Responsive */
@media (max-width: 768px) {
  .widget-header {
    padding: 16px 16px 0 16px;
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .widget-content {
    padding: 0 16px;
  }
  
  .widget-footer {
    padding: 12px 16px;
  }
  
  .widget-title h3 {
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .widget-header {
    padding: 12px 12px 0 12px;
  }
  
  .widget-content {
    padding: 0 12px;
  }
  
  .widget-footer {
    padding: 8px 12px;
  }
}

/* Estados especiales */
.widget-loading .widget-content {
  opacity: 0.6;
}

.widget-error .widget-content {
  opacity: 0.6;
}

/* Animaciones */
.dashboard-widget {
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
