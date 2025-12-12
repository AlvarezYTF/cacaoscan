<template>
  <div class="bg-gray-50 p-4 rounded-lg">
    <h3 class="text-lg font-medium text-gray-900 mb-4">Información del Lote</h3>
    <dl class="space-y-3">
      <div class="sm:grid sm:grid-cols-3 sm:gap-4">
        <dt class="text-sm font-medium text-gray-500">Nombre</dt>
        <dd class="mt-1 text-sm text-gray-900 sm:col-span-2">{{ data.batchName || 'N/A' }}</dd>
      </div>
      <div class="sm:grid sm:grid-cols-3 sm:gap-4">
        <dt class="text-sm font-medium text-gray-500">Fecha de Recolección</dt>
        <dd class="mt-1 text-sm text-gray-900 sm:col-span-2">{{ formatDate(data.collectionDate) }}</dd>
      </div>
      <div class="sm:grid sm:grid-cols-3 sm:gap-4">
        <dt class="text-sm font-medium text-gray-500">Origen</dt>
        <dd class="mt-1 text-sm text-gray-900 sm:col-span-2">{{ data.origin || 'N/A' }}</dd>
      </div>
      <div class="sm:grid sm:grid-cols-3 sm:gap-4" v-if="data.notes">
        <dt class="text-sm font-medium text-gray-500">Notas</dt>
        <dd class="mt-1 text-sm text-gray-900 sm:col-span-2">{{ data.notes }}</dd>
      </div>
    </dl>
  </div>
</template>

<script>
export default {
  name: 'BatchInfoCard',
  props: {
    data: {
      type: Object,
      required: true,
      default: () => ({
        batchName: '',
        collectionDate: '',
        origin: '',
        notes: ''
      })
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const options = { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' };
      // Parse date string to avoid timezone issues with YYYY-MM-DD format
      const dateParts = dateString.split('-');
      if (dateParts.length === 3) {
        const year = Number.parseInt(dateParts[0], 10);
        const month = Number.parseInt(dateParts[1], 10) - 1; // Month is 0-indexed
        const day = Number.parseInt(dateParts[2], 10);
        const date = new Date(Date.UTC(year, month, day));
        return date.toLocaleDateString('es-ES', options);
      }
      return new Date(dateString).toLocaleDateString('es-ES', options);
    }
  }
}
</script>
