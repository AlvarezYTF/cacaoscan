<template>
  <div class="mt-6">
    <h3 class="text-lg font-semibold text-gray-800 mb-3">📍 Ubicación geográfica</h3>

    <!-- ✅ Mostrar mapa si hay coordenadas -->
    <div v-if="latitudNum && longitudNum" class="rounded-xl overflow-hidden shadow-md border border-gray-200">
      <div ref="mapContainer" style="height: 400px; width: 100%"></div>
    </div>

    <!-- 🚫 Si no tiene coordenadas -->
    <div v-else class="p-4 bg-gray-100 rounded-lg text-gray-600 text-sm">
      🌱 Esta finca aún no tiene una ubicación registrada.
    </div>
  </div>
</template>

<script setup>
// 1. Vue core
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import * as L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Props
const props = defineProps({
  nombre: {
    type: String,
    required: true
  },
  latitud: {
    type: [Number, String],
    default: null
  },
  longitud: {
    type: [Number, String],
    default: null
  }
})

// Convertir y validar coordenadas (el backend devuelve DecimalField que puede ser string o número)
const latitudNum = computed(() => {
  if (props.latitud === null || props.latitud === undefined || props.latitud === '') {
    return null
  }
  
  // Convertir a número (puede venir como string desde el backend)
  let num = typeof props.latitud === 'string' ? Number.parseFloat(props.latitud) : Number(props.latitud)
  
  // Validar que sea un número válido y esté en el rango correcto
  if (Number.isNaN(num) || num < -90 || num > 90) {
    return null
  }
  
  return num
})

const longitudNum = computed(() => {
  if (props.longitud === null || props.longitud === undefined || props.longitud === '') {
    return null
  }
  
  // Convertir a número (puede venir como string desde el backend)
  let num = typeof props.longitud === 'string' ? Number.parseFloat(props.longitud) : Number(props.longitud)
  
  // Validar que sea un número válido y esté en el rango correcto
  if (Number.isNaN(num) || num < -180 || num > 180) {
    return null
  }
  
  return num
})

// Map reference
const mapContainer = ref(null)
let map = null
let marker = null

// Fix para iconos de Leaflet (problema común con Webpack/Vite)
const fixLeafletIcons = () => {
  // Eliminar método problemático si existe
  if (L.Icon.Default.prototype._getIconUrl) {
    delete L.Icon.Default.prototype._getIconUrl
  }
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png'
  })
}

// Inicializar mapa
const initMap = () => {
  if (!mapContainer.value || latitudNum.value === null || longitudNum.value === null) {
    return
  }
  
  // Validación adicional antes de crear el mapa
  const lat = Number(latitudNum.value)
  const lng = Number(longitudNum.value)
  
  if (Number.isNaN(lat) || Number.isNaN(lng)) {
    return
  }
  
  fixLeafletIcons()
  
  try {
    // Crear mapa con las coordenadas [lat, lng] - Leaflet usa este orden
    map = L.map(mapContainer.value).setView([lat, lng], 13)
    
    // Agregar capa de tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19
    }).addTo(map)
    
    // Agregar marcador en la ubicación
    marker = L.marker([lat, lng]).addTo(map)
    
    // Agregar popup al marcador con información
    const popupContent = `
      <div class="text-sm p-2">
        <strong>${props.nombre}</strong><br />
        <span class="text-gray-600">Lat: ${lat.toFixed(6)}</span><br />
        <span class="text-gray-600">Lng: ${lng.toFixed(6)}</span>
        <br /><br />
        <a
          href="https://www.google.com/maps?q=${lat},${lng}"
          target="_blank"
          rel="noopener noreferrer"
          class="text-green-600 hover:underline font-medium"
        >
          🔗 Ver en Google Maps
        </a>
      </div>
    `
    marker.bindPopup(popupContent)
    
    // Abrir popup automáticamente
    marker.openPopup()
  } catch (error) {
    throw error
  }
}

// Limpiar mapa
const cleanupMap = () => {
  if (map) {
    map.remove()
    map = null
    marker = null
  }
}

// Watch para cambios en coordenadas
watch([latitudNum, longitudNum], () => {
  cleanupMap()
  if (latitudNum.value && longitudNum.value) {
    // Esperar un tick para que el DOM se actualice
    setTimeout(() => {
      initMap()
    }, 100)
  }
})

// Lifecycle
onMounted(() => {
  if (latitudNum.value && longitudNum.value) {
    initMap()
  }
})

onUnmounted(() => {
  cleanupMap()
})
</script>

<style scoped>
/* Asegurar que Leaflet se muestre correctamente */
::v-deep(.leaflet-container) {
  font-family: inherit;
}
</style>
