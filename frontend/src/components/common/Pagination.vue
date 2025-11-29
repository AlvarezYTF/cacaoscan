<template>
  <nav v-if="totalPages > 1" aria-label="Paginación">
    <ul class="pagination justify-content-center">
      <!-- Botón Anterior -->
      <li class="page-item" :class="{ disabled: currentPage === 1 }">
        <button 
          @click="goToPage(currentPage - 1)" 
          class="page-link"
          :disabled="currentPage === 1"
          aria-label="Página anterior"
        >
          <i class="fas fa-chevron-left"></i>
          <span class="d-none d-sm-inline ms-1">Anterior</span>
        </button>
      </li>

      <!-- Primera página -->
      <li 
        v-if="showFirstPage" 
        class="page-item"
        :class="{ active: currentPage === 1 }"
      >
        <button @click="goToPage(1)" class="page-link">1</button>
      </li>

      <!-- Puntos suspensivos inicial -->
      <li v-if="showFirstEllipsis" class="page-item disabled">
        <span class="page-link">...</span>
      </li>

      <!-- Páginas del medio -->
      <li 
        v-for="page in visiblePages" 
        :key="page"
        class="page-item"
        :class="{ active: page === currentPage }"
      >
        <button @click="goToPage(page)" class="page-link">
          {{ page }}
        </button>
      </li>

      <!-- Puntos suspensivos final -->
      <li v-if="showLastEllipsis" class="page-item disabled">
        <span class="page-link">...</span>
      </li>

      <!-- Última página -->
      <li 
        v-if="showLastPage" 
        class="page-item"
        :class="{ active: currentPage === totalPages }"
      >
        <button @click="goToPage(totalPages)" class="page-link">
          {{ totalPages }}
        </button>
      </li>

      <!-- Botón Siguiente -->
      <li class="page-item" :class="{ disabled: currentPage === totalPages }">
        <button 
          @click="goToPage(currentPage + 1)" 
          class="page-link"
          :disabled="currentPage === totalPages"
          aria-label="Página siguiente"
        >
          <span class="d-none d-sm-inline me-1">Siguiente</span>
          <i class="fas fa-chevron-right"></i>
        </button>
      </li>
    </ul>

    <!-- Información de páginas -->
    <div class="text-center mt-2">
      <small class="text-muted">
        Página {{ currentPage }} de {{ totalPages }}
        <span v-if="totalItems > 0">
          ({{ totalItems }} elementos)
        </span>
      </small>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentPage: {
    type: Number,
    required: true
  },
  totalPages: {
    type: Number,
    required: true
  },
  totalItems: {
    type: Number,
    default: 0
  },
  maxVisiblePages: {
    type: Number,
    default: 5
  }
})

const emit = defineEmits(['page-change'])

// Computed properties
const visiblePages = computed(() => {
  const pages = []
  const half = Math.floor(props.maxVisiblePages / 2)
  
  let start = Math.max(1, props.currentPage - half)
  let end = Math.min(props.totalPages, start + props.maxVisiblePages - 1)
  
  // Ajustar el inicio si estamos cerca del final
  if (end - start < props.maxVisiblePages - 1) {
    start = Math.max(1, end - props.maxVisiblePages + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

const showFirstPage = computed(() => {
  return props.totalPages > props.maxVisiblePages && 
         visiblePages.value[0] > 1
})

const showLastPage = computed(() => {
  return props.totalPages > props.maxVisiblePages && 
         visiblePages.value[visiblePages.value.length - 1] < props.totalPages
})

const showFirstEllipsis = computed(() => {
  return showFirstPage.value && visiblePages.value[0] > 2
})

const showLastEllipsis = computed(() => {
  return showLastPage.value && 
         visiblePages.value[visiblePages.value.length - 1] < props.totalPages - 1
})

// Methods
const goToPage = (page) => {
  if (page >= 1 && page <= props.totalPages && page !== props.currentPage) {
    emit('page-change', page)
  }
}
</script>

<style scoped>
.pagination {
  margin-bottom: 0;
}

.page-link {
  color: #007bff;
  border-color: #dee2e6;
  transition: all 0.2s ease-in-out;
}

.page-link:hover {
  color: #0056b3;
  background-color: #e9ecef;
  border-color: #dee2e6;
}

.page-item.active .page-link {
  background-color: #1f4e79;
  border-color: #1f4e79;
  color: #ffffff;
}

.page-item.disabled .page-link {
  color: #6c757d;
  background-color: #fff;
  border-color: #dee2e6;
  cursor: not-allowed;
}

.page-link:focus {
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

/* Responsive adjustments */
@media (max-width: 576px) {
  .pagination {
    font-size: 0.875rem;
  }
  
  .page-link {
    padding: 0.375rem 0.5rem;
  }
}

/* Accessibility improvements */
.page-link:focus-visible {
  outline: 2px solid #007bff;
  outline-offset: 2px;
}

/* Animation for page changes */
.page-item {
  transition: transform 0.1s ease-in-out;
}

.page-item:hover {
  transform: translateY(-1px);
}
</style>
