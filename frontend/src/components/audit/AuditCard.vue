<template>
  <BaseCard
    :title="cardTitle"
    :icon="cardIcon"
    :variant="cardVariant"
    :clickable="true"
    @click="$emit('view-details', data, auditType)"
  >
    <template #meta>
      <span class="item-type">{{ itemType }}</span>
      <span class="item-status" :class="statusClass">
        {{ itemStatus }}
      </span>
    </template>

    <div class="item-info">
      <div class="info-item">
        <i class="fas fa-user"></i>
        <span>{{ data.usuario || 'Usuario Anónimo' }}</span>
      </div>
      <div class="info-item">
        <i class="fas fa-globe"></i>
        <span>{{ data.ip_address || 'N/A' }}</span>
      </div>
      <div v-if="auditType === 'activity' || auditType === 'both'" class="info-item">
        <i class="fas fa-cube"></i>
        <span>{{ data.modelo }}</span>
      </div>
      <div v-if="auditType === 'login' || auditType === 'both'" class="info-item">
        <i class="fas fa-clock"></i>
        <span>{{ formatDuration(data.session_duration) }}</span>
      </div>
    </div>

    <div v-if="auditType === 'activity' || auditType === 'both'" class="item-description">
      <p>{{ truncateText(data.descripcion, 100) }}</p>
    </div>

    <div v-if="auditType === 'login' || auditType === 'both'" class="session-info">
      <div class="session-item">
        <span class="session-label">Inicio:</span>
        <span class="session-value">{{ formatDateTime(data.login_time) }}</span>
      </div>
      <div v-if="data.logout_time" class="session-item">
        <span class="session-label">Cierre:</span>
        <span class="session-value">{{ formatDateTime(data.logout_time) }}</span>
      </div>
      <div v-if="data.failure_reason" class="session-item">
        <span class="session-label">Error:</span>
        <span class="session-value error">{{ data.failure_reason }}</span>
      </div>
    </div>

    <template #footer>
      <div class="timestamp">
        <i class="fas fa-calendar"></i>
        <span>{{ formatDateTime(data.timestamp || data.login_time) }}</span>
      </div>
    </template>

    <template #actions>
      <button
        @click.stop="$emit('view-details', data, auditType)"
        class="btn btn-sm btn-outline"
      >
        <i class="fas fa-eye"></i>
        Ver Detalles
      </button>
    </template>
  </BaseCard>
</template>

<script setup>
import { computed } from 'vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { useDateFormatting } from '@/composables/useDateFormatting'
import { useAuditHelpers } from '@/composables/useAuditHelpers'

const props = defineProps({
  data: {
    type: Object,
    required: true
  },
  auditType: {
    type: String,
    default: 'activity',
    validator: (value) => ['activity', 'login', 'both'].includes(value)
  }
})

const emit = defineEmits(['view-details'])

// Composables
const { formatDateTime: formatDateTimeUtil, formatDuration: formatDurationUtil } = useDateFormatting()
const {
  getAuditItemTitle,
  getAuditItemType,
  getAuditItemStatus,
  getAuditActionMarkerClass,
  getAuditActionIcon,
  getAuditStatusClass
} = useAuditHelpers()

// Computed properties
const cardTitle = computed(() => getAuditItemTitle(props.data, props.auditType))
const itemType = computed(() => getAuditItemType(props.auditType))
const itemStatus = computed(() => getAuditItemStatus(props.data, props.auditType))
const statusClass = computed(() => getAuditStatusClass(props.data, props.auditType))

const cardVariant = computed(() => {
  if (props.auditType === 'activity' || props.auditType === 'both') {
    const markerClass = getAuditActionMarkerClass(props.data.accion)
    if (markerClass.includes('create')) return 'success'
    if (markerClass.includes('delete')) return 'error'
    if (markerClass.includes('update')) return 'info'
    return 'default'
  } else if (props.auditType === 'login') {
    return props.data.success ? 'success' : 'error'
  }
  return 'default'
})

const cardIcon = computed(() => {
  if (props.auditType === 'activity' || props.auditType === 'both') {
    return getAuditActionIcon(props.data.accion)
  } else if (props.auditType === 'login') {
    return props.data.success ? 'fas fa-check-circle' : 'fas fa-times-circle'
  }
  return 'fas fa-circle'
})

// Methods
const formatDateTime = (dateString) => {
  return formatDateTimeUtil(dateString)
}

const formatDuration = (durationString) => {
  return formatDurationUtil(durationString)
}

const truncateText = (text, maxLength) => {
  if (!text) return 'N/A'
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// Expose methods and computed properties for testing
defineExpose({
  formatDateTime,
  formatDuration,
  truncateText,
  cardVariant,
  cardIcon
})
</script>

<style scoped>
.item-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.info-item i {
  width: 1rem;
  color: #9ca3af;
}

.item-description {
  margin-bottom: 1rem;
}

.item-description p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.5;
}

.session-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.session-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-label {
  color: #9ca3af;
  font-size: 0.75rem;
  font-weight: 500;
}

.session-value {
  color: #374151;
  font-size: 0.875rem;
}

.session-value.error {
  color: #dc2626;
}

.timestamp {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.timestamp i {
  color: #9ca3af;
}

.item-type {
  background: #f3f4f6;
  color: #374151;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.item-status {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-success {
  background: #d1fae5;
  color: #065f46;
}

.status-error {
  background: #fee2e2;
  color: #991b1b;
}

.status-default {
  background: #f3f4f6;
  color: #374151;
}

.btn {
  display: inline-flex;
  align-items: center;
  padding: 0.375rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
  border: 1px solid transparent;
  gap: 0.25rem;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
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

/* Responsive */
@media (max-width: 640px) {
  .item-info {
    gap: 0.375rem;
  }
  
  .session-info {
    gap: 0.375rem;
  }
}
</style>
