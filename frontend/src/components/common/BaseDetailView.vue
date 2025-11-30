<template>
  <div class="base-detail-view container-fluid">
    <div class="row">
      <div class="col-12">
        <!-- Breadcrumb Navigation -->
        <nav v-if="breadcrumbs && breadcrumbs.length > 0" aria-label="breadcrumb" class="mb-4">
          <ol class="breadcrumb">
            <li 
              v-for="(crumb, index) in breadcrumbs" 
              :key="index"
              class="breadcrumb-item"
              :class="{ 'active': index === breadcrumbs.length - 1 }"
              :aria-current="index === breadcrumbs.length - 1 ? 'page' : undefined"
            >
              <router-link v-if="index < breadcrumbs.length - 1" :to="crumb.to">
                {{ crumb.label }}
              </router-link>
              <span v-else>{{ crumb.label }}</span>
            </li>
          </ol>
        </nav>

        <!-- Loading State -->
        <output v-if="loading" class="text-center py-5 block" aria-live="polite">
          <div class="spinner-border text-primary" :aria-label="loadingText || 'Cargando información'">
            <span class="visually-hidden">{{ loadingText || 'Cargando...' }}</span>
          </div>
          <p class="mt-3">{{ loadingText || 'Cargando información...' }}</p>
        </output>

        <!-- Error State -->
        <div v-else-if="error" class="alert alert-danger" role="alert">
          <h4 class="alert-heading">{{ errorTitle || 'Error' }}</h4>
          <p>{{ error }}</p>
          <hr v-if="showRetryButton">
          <button v-if="showRetryButton" @click="handleRetry" class="btn btn-outline-danger">
            {{ retryButtonText || 'Intentar nuevamente' }}
          </button>
        </div>

        <!-- Content -->
        <div v-else-if="!loading && !error" class="row">
          <!-- Main Content Column -->
          <div :class="`col-lg-${mainColumnSize || 8}`">
            <!-- Header Card -->
            <div v-if="$slots.header || title" class="card mb-4">
              <div class="card-header d-flex justify-content-between align-items-center">
                <div class="flex-grow-1">
                  <h5 class="mb-0">
                    <i v-if="icon" :class="icon" class="me-2"></i>
                    <slot name="header">
                      {{ title }}
                    </slot>
                  </h5>
                  <p v-if="subtitle" class="text-muted mb-0 mt-1 small">{{ subtitle }}</p>
                </div>
                <div class="d-flex align-items-center gap-2">
                  <slot name="header-actions">
                    <button 
                      v-if="showEditButton && canEdit"
                      @click="handleEdit" 
                      class="btn btn-outline-primary btn-sm"
                    >
                      <i class="fas fa-edit"></i> {{ editButtonText || 'Editar' }}
                    </button>
                    <span 
                      v-if="statusBadge"
                      class="badge"
                      :class="getStatusBadgeClass(statusBadge)"
                    >
                      {{ statusBadge }}
                    </span>
                  </slot>
                </div>
              </div>
              <div v-if="$slots.header-content || mainContent" class="card-body">
                <slot name="header-content">
                  <div v-if="mainContent">{{ sanitizedMainContent }}</div>
                </slot>
              </div>
            </div>

            <!-- Main Content Slot -->
            <slot name="main">
              <div v-if="mainContent" class="card">
                <div class="card-body">
                  <div>{{ sanitizedMainContent }}</div>
                </div>
              </div>
            </slot>

            <!-- Additional Sections -->
            <slot name="sections"></slot>

            <!-- Statistics Card -->
            <div v-if="statistics && statistics.length > 0" class="card mt-4">
              <div class="card-header">
                <h5 class="mb-0">
                  <i class="fas fa-chart-bar me-2"></i>
                  {{ statisticsTitle || 'Estadísticas' }}
                </h5>
              </div>
              <div class="card-body">
                <div class="row text-center">
                  <div 
                    v-for="(stat, index) in statistics" 
                    :key="index"
                    class="col-md-3"
                  >
                    <div :class="{ 'border-end': index < statistics.length - 1 }">
                      <h3 :class="`text-${stat.color || 'primary'}`">{{ stat.value }}</h3>
                      <p class="text-muted mb-0">{{ stat.label }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Sidebar Column -->
          <div :class="`col-lg-${sidebarColumnSize || 4}`">
            <!-- Actions Card -->
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">
                  <i class="fas fa-tools me-2"></i>
                  {{ actionsTitle || 'Acciones' }}
                </h5>
              </div>
              <div class="card-body">
                <div class="d-grid gap-2">
                  <slot name="actions"></slot>
                </div>
              </div>
            </div>

            <!-- Related Items -->
            <slot name="sidebar"></slot>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { escapeHTML } from '@/utils/security'

const props = defineProps({
  // Breadcrumbs
  breadcrumbs: {
    type: Array,
    default: () => []
  },
  
  // Loading & Error States
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: ''
  },
  error: {
    type: String,
    default: null
  },
  errorTitle: {
    type: String,
    default: 'Error'
  },
  showRetryButton: {
    type: Boolean,
    default: true
  },
  retryButtonText: {
    type: String,
    default: 'Intentar nuevamente'
  },
  
  // Header
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: ''
  },
  
  // Edit Button
  showEditButton: {
    type: Boolean,
    default: false
  },
  canEdit: {
    type: Boolean,
    default: false
  },
  editButtonText: {
    type: String,
    default: 'Editar'
  },
  
  // Status Badge
  statusBadge: {
    type: String,
    default: null
  },
  
  // Content
  mainContent: {
    type: String,
    default: ''
  },
  
  // Statistics
  statistics: {
    type: Array,
    default: () => []
  },
  statisticsTitle: {
    type: String,
    default: 'Estadísticas'
  },
  
  // Layout
  mainColumnSize: {
    type: Number,
    default: 8,
    validator: (value) => [6, 7, 8, 9, 10, 12].includes(value)
  },
  sidebarColumnSize: {
    type: Number,
    default: 4,
    validator: (value) => [2, 3, 4, 5, 6].includes(value)
  },
  
  // Sidebar
  actionsTitle: {
    type: String,
    default: 'Acciones'
  }
})

const emit = defineEmits(['edit', 'retry'])

const getStatusBadgeClass = (status) => {
  const statusClasses = {
    'activo': 'bg-success',
    'active': 'bg-success',
    'inactivo': 'bg-secondary',
    'inactive': 'bg-secondary',
    'completado': 'bg-success',
    'completed': 'bg-success',
    'pendiente': 'bg-warning',
    'pending': 'bg-warning',
    'procesando': 'bg-info',
    'processing': 'bg-info',
    'error': 'bg-danger',
    'cosechado': 'bg-info',
    'harvested': 'bg-info'
  }
  
  const normalizedStatus = status?.toLowerCase() || ''
  return statusClasses[normalizedStatus] || 'bg-secondary'
}

const handleEdit = () => {
  emit('edit')
}

const handleRetry = () => {
  emit('retry')
}

// Sanitize HTML content to prevent XSS attacks
const sanitizedMainContent = computed(() => {
  if (!props.mainContent) {
    return ''
  }
  // Escape HTML to prevent XSS
  // If HTML rendering is truly needed, use a proper sanitization library like DOMPurify
  return escapeHTML(props.mainContent)
})
</script>

<style scoped>
.base-detail-view {
  min-height: 100vh;
}

.breadcrumb {
  background-color: transparent;
  padding: 0;
  margin-bottom: 1rem;
}

.breadcrumb-item {
  font-size: 0.875rem;
}

.breadcrumb-item + .breadcrumb-item::before {
  content: '>';
  padding: 0 0.5rem;
  color: #6c757d;
}

.breadcrumb-item.active {
  color: #6c757d;
}

.breadcrumb-item a {
  color: #007bff;
  text-decoration: none;
}

.breadcrumb-item a:hover {
  text-decoration: underline;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid rgba(0, 0, 0, 0.125);
  margin-bottom: 1rem;
}

.card-header {
  background-color: rgba(0, 0, 0, 0.03);
  border-bottom: 1px solid rgba(0, 0, 0, 0.125);
  padding: 1rem 1.25rem;
}

.card-body {
  padding: 1.25rem;
}

.border-end {
  border-right: 1px solid #dee2e6 !important;
}

.border-end:last-child {
  border-right: none !important;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

.alert {
  border-radius: 0.375rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.d-grid {
  display: grid;
}

.gap-2 {
  gap: 0.5rem;
}

/* Responsive adjustments */
@media (max-width: 991.98px) {
  .base-detail-view .row > div[class*='col-lg-'] {
    margin-bottom: 1rem;
  }
}
</style>

