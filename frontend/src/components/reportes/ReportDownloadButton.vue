<template>
  <div class="report-download-button">
    <button
      v-if="reporte.estado === 'completado' && !reporte.esta_expirado"
      @click="descargarReporte"
      :disabled="descargando"
      class="btn btn-primary btn-sm"
      :class="{ 'loading': descargando }"
    >
      <i v-if="descargando" class="fas fa-spinner fa-spin"></i>
      <i v-else class="fas fa-download"></i>
      {{ descargando ? 'Descargando...' : 'Descargar' }}
    </button>
    
    <button
      v-else-if="reporte.estado === 'generando'"
      disabled
      class="btn btn-secondary btn-sm"
    >
      <i class="fas fa-spinner fa-spin"></i>
      Generando...
    </button>
    
    <button
      v-else-if="reporte.estado === 'fallido'"
      disabled
      class="btn btn-danger btn-sm"
    >
      <i class="fas fa-exclamation-triangle"></i>
      Error
    </button>
    
    <button
      v-else-if="reporte.esta_expirado"
      disabled
      class="btn btn-warning btn-sm"
    >
      <i class="fas fa-clock"></i>
      Expirado
    </button>
    
    <div v-if="error" class="alert alert-danger mt-2">
      <i class="fas fa-exclamation-circle"></i>
      {{ error }}
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'

export default {
  name: 'ReportDownloadButton',
  props: {
    reporte: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const authStore = useAuthStore()
    const notificationStore = useNotificationStore()
    
    const descargando = ref(false)
    const error = ref('')
    
    const descargarReporte = async () => {
      try {
        descargando.value = true
        error.value = ''
        
        const response = await fetch(
          `/api/reportes/${props.reporte.id}/download/`,
          {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${authStore.token}`,
              'Accept': 'application/octet-stream'
            }
          }
        )
        
        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || 'Error al descargar el reporte')
        }
        
        // Obtener el nombre del archivo del header Content-Disposition
        const contentDisposition = response.headers.get('Content-Disposition')
        let filename = `reporte_${props.reporte.id}.${props.reporte.formato}`
        
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="(.+)"/)
          if (filenameMatch) {
            filename = filenameMatch[1]
          }
        }
        
        // Crear blob y descargar
        const blob = await response.blob()
        const url = globalThis.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        link.remove()
        globalThis.URL.revokeObjectURL(url)
        
        notificationStore.addNotification({
          type: 'success',
          title: 'Descarga exitosa',
          message: `El reporte "${props.reporte.titulo}" se ha descargado correctamente.`
        })
        
      } catch (err) {
        error.value = err.message
        notificationStore.addNotification({
          type: 'error',
          title: 'Error en la descarga',
          message: err.message
        })
      } finally {
        descargando.value = false
      }
    }
    
    return {
      descargando,
      error,
      descargarReporte
    }
  }
}
</script>

<style scoped>
.report-download-button {
  display: inline-block;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-primary {
  background-color: #1e40af;
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  background-color: #1e3a8a;
}

.btn-secondary {
  background-color: #4b5563;
  color: #ffffff;
}

.btn-danger {
  background-color: #dc2626;
  color: #ffffff;
}

.btn-warning {
  background-color: #8a4b00;
  color: #ffffff;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
}

.loading {
  opacity: 0.7;
}

.alert {
  padding: 0.75rem;
  margin-top: 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.alert-danger {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
}

.alert-danger i {
  margin-right: 0.5rem;
}
</style>
