<template>
  <div class="base-location-map">
    <div v-if="title" class="map-header">
      <h3 class="map-title">{{ title }}</h3>
    </div>

    <!-- Mostrar mapa si hay coordenadas -->
    <div v-if="hasValidCoordinates" class="map-container" :class="containerClass">
      <div ref="mapContainer" :style="mapStyle"></div>
    </div>

    <!-- Mensaje cuando no hay coordenadas -->
    <div v-else class="map-empty" :class="emptyClass">
      <slot name="empty">
        <div class="empty-content">
          <i class="fas fa-map-marker-alt empty-icon"></i>
          <p class="empty-message">{{ emptyMessage }}</p>
        </div>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted, nextTick } from 'vue'
import * as L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  latitude: {
    type: [Number, String],
    default: null
  },
  longitude: {
    type: [Number, String],
    default: null
  },
  title: {
    type: String,
    default: ''
  },
  markerTitle: {
    type: String,
    default: ''
  },
  height: {
    type: [String, Number],
    default: 400
  },
  zoom: {
    type: Number,
    default: 13
  },
  showPopup: {
    type: Boolean,
    default: true
  },
  editable: {
    type: Boolean,
    default: false
  },
  containerClass: {
    type: String,
    default: 'rounded-xl overflow-hidden shadow-md border border-gray-200'
  },
  emptyMessage: {
    type: String,
    default: 'No hay ubicación registrada.'
  },
  emptyClass: {
    type: String,
    default: 'p-4 bg-gray-100 rounded-lg text-gray-600 text-sm'
  },
  tileLayerUrl: {
    type: String,
    default: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
  },
  tileLayerAttribution: {
    type: String,
    default: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }
})

const emit = defineEmits(['marker-click', 'location-change', 'map-ready'])

// Map reference
const mapContainer = ref(null)
let map = null
let marker = null

// Validar y convertir coordenadas
const latitudeNum = computed(() => {
  if (props.latitude === null || props.latitude === undefined || props.latitude === '') {
    return null
  }
  const num = typeof props.latitude === 'string' ? Number.parseFloat(props.latitude) : Number(props.latitude)
  if (Number.isNaN(num) || num < -90 || num > 90) {
    return null
  }
  return num
})

const longitudeNum = computed(() => {
  if (props.longitude === null || props.longitude === undefined || props.longitude === '') {
    return null
  }
  const num = typeof props.longitude === 'string' ? Number.parseFloat(props.longitude) : Number(props.longitude)
  if (Number.isNaN(num) || num < -180 || num > 180) {
    return null
  }
  return num
})

const hasValidCoordinates = computed(() => {
  return latitudeNum.value !== null && longitudeNum.value !== null
})

const mapStyle = computed(() => {
  const height = typeof props.height === 'number' ? `${props.height}px` : props.height
  return {
    height,
    width: '100%'
  }
})

// Fix para iconos de Leaflet
const fixLeafletIcons = () => {
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
const initMap = async () => {
  if (!mapContainer.value || !hasValidCoordinates.value) {
    return
  }

  const lat = Number(latitudeNum.value)
  const lng = Number(longitudeNum.value)

  if (Number.isNaN(lat) || Number.isNaN(lng)) {
    return
  }

  fixLeafletIcons()

  try {
    await nextTick()

    // Crear mapa
    map = L.map(mapContainer.value).setView([lat, lng], props.zoom)

    // Agregar capa de tiles
    L.tileLayer(props.tileLayerUrl, {
      attribution: props.tileLayerAttribution,
      maxZoom: 19
    }).addTo(map)

    // Agregar marcador
    marker = L.marker([lat, lng], {
      draggable: props.editable
    }).addTo(map)

    // Configurar popup
    if (props.showPopup) {
      const popupContent = createPopupContent(lat, lng)
      marker.bindPopup(popupContent)
      marker.openPopup()
    }

    // Eventos
    if (props.editable) {
      marker.on('dragend', (e) => {
        const position = e.target.getLatLng()
        emit('location-change', {
          latitude: position.lat,
          longitude: position.lng
        })
      })
    }

    marker.on('click', () => {
      emit('marker-click', {
        latitude: lat,
        longitude: lng
      })
    })

    emit('map-ready', map)
  } catch (error) {
    }
}

// Crear contenido del popup
const createPopupContent = (lat, lng) => {
  const title = props.markerTitle || 'Ubicación'
  return `
    <div class="text-sm p-2">
      <strong>${title}</strong><br />
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
watch([latitudeNum, longitudeNum], () => {
  cleanupMap()
  if (hasValidCoordinates.value) {
    nextTick(() => {
      setTimeout(() => {
        initMap()
      }, 100)
    })
  }
})

// Lifecycle
onMounted(() => {
  if (hasValidCoordinates.value) {
    initMap()
  }
})

onUnmounted(() => {
  cleanupMap()
})
</script>

<style scoped>
.base-location-map {
  width: 100%;
}

.map-header {
  margin-bottom: 1rem;
}

.map-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

.map-container {
  width: 100%;
}

.map-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.empty-content {
  text-align: center;
}

.empty-icon {
  font-size: 2rem;
  color: #9ca3af;
  margin-bottom: 0.5rem;
}

.empty-message {
  color: #6b7280;
  font-size: 0.875rem;
}

/* Asegurar que Leaflet se muestre correctamente */
::v-deep(.leaflet-container) {
  font-family: inherit;
}
</style>

