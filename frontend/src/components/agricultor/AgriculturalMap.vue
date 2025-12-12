<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
    <div class="bg-gradient-to-r from-green-50 to-blue-50 px-6 py-4 border-b border-gray-200">
      <div class="flex items-center">
        <div class="bg-green-100 p-2 rounded-xl mr-3">
          <svg class="text-xl text-green-600 w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path>
          </svg>
        </div>
        <div>
          <h2 class="text-lg font-bold text-gray-900">Mapa Agrícola</h2>
          <p class="text-sm text-gray-600">Ubicación de fincas y calidad</p>
        </div>
      </div>
    </div>
    
    <div class="p-6">
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        <p class="text-gray-600 mt-2">Cargando mapa...</p>
      </div>
      
      <div v-else-if="fincasWithLocation.length === 0" class="text-center py-12">
        <div class="text-gray-400 text-4xl mb-2">📍</div>
        <p class="text-gray-600 font-medium">No hay fincas con ubicación registrada</p>
        <p class="text-gray-500 text-sm mt-1">Agrega coordenadas a tus fincas para verlas en el mapa</p>
      </div>
      
      <div v-else ref="mapContainer" class="h-96 rounded-lg overflow-hidden border border-gray-200"></div>
      
      <!-- Legend -->
      <div v-if="fincasWithLocation.length > 0" class="mt-4 flex items-center justify-center gap-4 flex-wrap">
        <div class="flex items-center gap-2">
          <div class="w-4 h-4 bg-green-500 rounded-full"></div>
          <span class="text-sm text-gray-600">Excelente (≥85%)</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-4 h-4 bg-yellow-500 rounded-full"></div>
          <span class="text-sm text-gray-600">Aceptable (70-84%)</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-4 h-4 bg-red-500 rounded-full"></div>
          <span class="text-sm text-gray-600">Riesgo (<70%)</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import * as L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  fincas: {
    type: Array,
    required: true,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const mapContainer = ref(null)
let map = null
let markers = []

// Filter fincas with coordinates
const fincasWithLocation = computed(() => {
  return props.fincas.filter(finca => {
    const lat = finca.coordenadas_lat
    const lng = finca.coordenadas_lng
    return lat != null && lng != null && lat !== '' && lng !== ''
  })
})

// Get marker color based on quality
const getMarkerColor = (quality) => {
  if (quality >= 85) return '#10b981' // green
  if (quality >= 70) return '#eab308' // yellow
  return '#ef4444' // red
}

// Initialize map
const initMap = () => {
  if (!mapContainer.value || fincasWithLocation.value.length === 0) {
    return
  }
  
  // Destroy existing map if any
  if (map) {
    map.remove()
    markers.forEach(marker => marker.remove())
    markers = []
  }
  
  // Calculate center from fincas
  const lats = fincasWithLocation.value.map(f => Number.parseFloat(f.coordenadas_lat))
  const lngs = fincasWithLocation.value.map(f => Number.parseFloat(f.coordenadas_lng))
  const centerLat = lats.reduce((a, b) => a + b, 0) / lats.length
  const centerLng = lngs.reduce((a, b) => a + b, 0) / lngs.length
  
  // Create map
  map = L.map(mapContainer.value).setView([centerLat, centerLng], 10)
  
  // Add tile layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map)
  
  // Add markers for each finca
  fincasWithLocation.value.forEach(finca => {
    const lat = Number.parseFloat(finca.coordenadas_lat)
    const lng = Number.parseFloat(finca.coordenadas_lng)
    const quality = finca.quality || 0
    const color = getMarkerColor(quality)
    
    const marker = L.circleMarker([lat, lng], {
      radius: 10,
      fillColor: color,
      color: '#fff',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.8
    }).addTo(map)
    
    const popupContent = `
      <div class="p-2">
        <h3 class="font-bold text-gray-900 mb-1">${finca.nombre}</h3>
        <p class="text-sm text-gray-600">Calidad promedio: ${Math.round(quality)}%</p>
        <p class="text-sm text-gray-600">Total análisis: ${finca.totalAnalyses || 0}</p>
        <p class="text-sm text-gray-600">Última fecha: ${finca.lastAnalysisDate || 'N/A'}</p>
      </div>
    `
    
    marker.bindPopup(popupContent)
    markers.push(marker)
  })
}

onMounted(() => {
  if (fincasWithLocation.value.length > 0) {
    setTimeout(initMap, 100)
  }
})

watch(() => props.fincas, () => {
  if (fincasWithLocation.value.length > 0) {
    setTimeout(initMap, 100)
  }
}, { deep: true })

onUnmounted(() => {
  if (map) {
    map.remove()
    markers.forEach(marker => marker.remove())
  }
})
</script>

