import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'node:path'

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
    testTimeout: 30000,
    hookTimeout: 30000,
    teardownTimeout: 10000,
    poolTimeout: 300000,
    sequence: {
      shuffle: false
    },
    poolOptions: {
      threads: {
        singleThread: false,
        isolate: true,
        minThreads: 1,
        maxThreads: 2
      }
    },
    exclude: [
      'node_modules',
      'dist',
      'coverage',
      'cypress',
      '**/cypress/**',
      '**/*.cy.js'
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
        'cypress/**',
        '**/cypress/**',
        '**/*.cy.js',
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
    dedupe: ['vue']
  },
  define: {
    'import.meta.vitest': 'undefined'
  },
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia'],
    esbuildOptions: {
      target: 'node18'
    }
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
