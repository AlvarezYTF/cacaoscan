import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = fileURLToPath(new URL('.', import.meta.url))

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.js'],
    threads: true,
    maxThreads: 2,
    minThreads: 1,
    isolate: true,
    testTimeout: 60000,
    hookTimeout: 60000,
    teardownTimeout: 30000,
    poolTimeout: 600000,
    sequence: {
      shuffle: false
    },
    poolOptions: {
      threads: {
        singleThread: false,
        isolate: true,
        minThreads: 1,
        maxThreads: 2,
        useAtomics: false
      }
    },
    fileParallelism: false,
    bail: 0,
    retry: 0,
    exclude: [
      'node_modules',
      'dist',
      'coverage'
    ],
    include: ['src/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    css: {
      modules: {
        classNameStrategy: 'non-scoped'
      }
    },
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'lcov'],
      reportsDirectory: './coverage',
      include: ['src/**'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        'src/env.d.ts',
        '**/*.config.js',
        '**/*.config.ts',
        'dist/',
        'coverage/',
        'src/App.vue',
        'src/main.js',
        'src/components/common/BaseFormField.example.vue',
        'src/services/api/index.js'
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    },
    dedupe: ['vue'],
    extensions: ['.mjs', '.js', '.mts', '.ts', '.jsx', '.tsx', '.json', '.vue']
  },
  define: {
    'import.meta.vitest': 'undefined'
  },
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia'],
    esbuildOptions: {
      target: 'node18'
    },
    force: true
  },
  ssr: {
    noExternal: ['vue', 'vue-router', 'pinia']
  },
  server: {
    fs: {
      strict: false
    }
  },
  build: {
    commonjsOptions: {
      include: [/node_modules/]
    }
  }
})
