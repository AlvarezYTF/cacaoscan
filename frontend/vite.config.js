import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    tailwindcss()
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  vue: {
    template: {
      compilerOptions: {
        isCustomElement: (tag) => tag.startsWith('ion-')
      }
    }
  },
  build: {
    // Aumentar el límite de advertencia a 1500 kB
    chunkSizeWarningLimit: 1500,
    
    // Optimizar el tamaño del bundle con esbuild (más rápido que terser)
    minify: 'esbuild',
    esbuild: {
      drop: ['console', 'debugger'], // Eliminar console.log y debugger en producción
    },
    
    // Configuración de code-splitting optimizada
    rollupOptions: {
      output: {
        // Estrategia de nombrado de chunks
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
        
        // Code-splitting manual optimizado
        manualChunks(id) {
          // Vue core y router en un chunk separado
          if (id.includes('node_modules/vue/') || id.includes('node_modules/@vue/') || id.includes('node_modules/vue-router/')) {
            return 'vue-core'
          }
          
          // Pinia para state management
          if (id.includes('node_modules/pinia/')) {
            return 'pinia'
          }
          
          // Axios y servicios de API
          if (id.includes('node_modules/axios/')) {
            return 'api-client'
          }
          
          // Chart.js y librerías de gráficos
          if (id.includes('node_modules/chart.js/')) {
            return 'charts'
          }
          
          // SweetAlert2 para modales
          if (id.includes('node_modules/sweetalert2/')) {
            return 'sweetalert'
          }
          
          // Tailwind CSS y postcss
          if (id.includes('node_modules/@tailwindcss/') || id.includes('node_modules/tailwindcss/') || id.includes('node_modules/postcss/')) {
            return 'tailwind'
          }
          
          // Otras librerías de node_modules agrupadas en vendor
          if (id.includes('node_modules/')) {
            return 'vendor'
          }
        }
      }
    },
    
    // Optimización de assets
    assetsInlineLimit: 4096, // 4kb - archivos menores se incluyen inline como base64
    
    // Mejor tree-shaking
    reportCompressedSize: true,
    
    // Habilitar source maps para debugging en producción (opcional)
    sourcemap: false
  },
  
  // Optimizaciones de rendimiento
  optimizeDeps: {
    include: [
      'vue',
      'vue-router',
      'pinia',
      'axios',
      'chart.js',
      'sweetalert2'
    ]
  }
})
