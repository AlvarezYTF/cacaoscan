import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { fileURLToPath } from 'node:url'

describe('vite.config.js', () => {
  let config

  beforeEach(() => {
    vi.resetModules()
  })

  afterEach(() => {
    vi.resetModules()
  })

  describe('config export', () => {
    it('should export a default configuration object', async () => {
      const configModule = await import('../vite.config.js')
      expect(configModule.default).toBeDefined()
      expect(typeof configModule.default).toBe('object')
    })

    it('should have plugins configuration', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.plugins).toBeDefined()
      expect(Array.isArray(config.plugins)).toBe(true)
      expect(config.plugins.length).toBeGreaterThan(0)
    })

    it('should have resolve configuration', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.resolve).toBeDefined()
      expect(typeof config.resolve).toBe('object')
    })

    it('should have vue configuration', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.vue).toBeDefined()
      expect(typeof config.vue).toBe('object')
    })

    it('should have build configuration', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.build).toBeDefined()
      expect(typeof config.build).toBe('object')
    })

    it('should have optimizeDeps configuration', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.optimizeDeps).toBeDefined()
      expect(typeof config.optimizeDeps).toBe('object')
    })
  })

  describe('resolve configuration', () => {
    it('should have alias configuration', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.resolve.alias).toBeDefined()
      expect(typeof config.resolve.alias).toBe('object')
    })

    it('should have correct @ alias pointing to src directory', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.resolve.alias['@']).toBeDefined()
      
      const aliasPath = config.resolve.alias['@']
      const expectedPath = fileURLToPath(new URL('./src', import.meta.url))
      expect(aliasPath).toBe(expectedPath)
    })
  })

  describe('vue configuration', () => {
    it('should have template configuration', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.vue.template).toBeDefined()
      expect(typeof config.vue.template).toBe('object')
    })

    it('should have compilerOptions configuration', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.vue.template.compilerOptions).toBeDefined()
      expect(typeof config.vue.template.compilerOptions).toBe('object')
    })

    it('should have isCustomElement function for ion- tags', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.vue.template.compilerOptions.isCustomElement).toBeDefined()
      expect(typeof config.vue.template.compilerOptions.isCustomElement).toBe('function')
      
      const isCustomElement = config.vue.template.compilerOptions.isCustomElement
      expect(isCustomElement('ion-button')).toBe(true)
      expect(isCustomElement('ion-icon')).toBe(true)
      expect(isCustomElement('div')).toBe(false)
      expect(isCustomElement('button')).toBe(false)
    })
  })

  describe('build configuration', () => {
    it('should have chunkSizeWarningLimit set to 1500', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.build.chunkSizeWarningLimit).toBe(1500)
    })

    it('should have minify set to esbuild', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.build.minify).toBe('esbuild')
    })

    it('should have esbuild configuration', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.build.esbuild).toBeDefined()
      expect(typeof config.build.esbuild).toBe('object')
    })

    it('should have drop console and debugger in esbuild', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.build.esbuild.drop).toBeDefined()
      expect(Array.isArray(config.build.esbuild.drop)).toBe(true)
      expect(config.build.esbuild.drop).toContain('console')
      expect(config.build.esbuild.drop).toContain('debugger')
    })

    it('should have rollupOptions configuration', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.build.rollupOptions).toBeDefined()
      expect(typeof config.build.rollupOptions).toBe('object')
    })

    it('should have output configuration in rollupOptions', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.build.rollupOptions.output).toBeDefined()
      expect(typeof config.build.rollupOptions.output).toBe('object')
    })

    it('should have correct chunkFileNames pattern', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.build.rollupOptions.output.chunkFileNames).toBe('assets/js/[name]-[hash].js')
    })

    it('should have correct entryFileNames pattern', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.build.rollupOptions.output.entryFileNames).toBe('assets/js/[name]-[hash].js')
    })

    it('should have correct assetFileNames pattern', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.build.rollupOptions.output.assetFileNames).toBe('assets/[ext]/[name]-[hash].[ext]')
    })

    it('should have manualChunks function', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.build.rollupOptions.output.manualChunks).toBeDefined()
      expect(typeof config.build.rollupOptions.output.manualChunks).toBe('function')
    })

    it('should return vue-core for Vue related modules', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      const manualChunks = config.build.rollupOptions.output.manualChunks
      
      expect(manualChunks('node_modules/vue/index.js')).toBe('vue-core')
      expect(manualChunks('node_modules/@vue/runtime-core/index.js')).toBe('vue-core')
      expect(manualChunks('node_modules/vue-router/index.js')).toBe('vue-core')
    })

    it('should return pinia for Pinia modules', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      const manualChunks = config.build.rollupOptions.output.manualChunks
      
      expect(manualChunks('node_modules/pinia/index.js')).toBe('pinia')
    })

    it('should return api-client for Axios modules', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      const manualChunks = config.build.rollupOptions.output.manualChunks
      
      expect(manualChunks('node_modules/axios/index.js')).toBe('api-client')
    })

    it('should return charts for Chart.js modules', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      const manualChunks = config.build.rollupOptions.output.manualChunks
      
      expect(manualChunks('node_modules/chart.js/index.js')).toBe('charts')
    })

    it('should return sweetalert for SweetAlert2 modules', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      const manualChunks = config.build.rollupOptions.output.manualChunks
      
      expect(manualChunks('node_modules/sweetalert2/index.js')).toBe('sweetalert')
    })

    it('should return tailwind for Tailwind CSS modules', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      const manualChunks = config.build.rollupOptions.output.manualChunks
      
      expect(manualChunks('node_modules/@tailwindcss/vite/index.js')).toBe('tailwind')
      expect(manualChunks('node_modules/tailwindcss/index.js')).toBe('tailwind')
      expect(manualChunks('node_modules/postcss/index.js')).toBe('tailwind')
    })

    it('should return vendor for other node_modules', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      const manualChunks = config.build.rollupOptions.output.manualChunks
      
      expect(manualChunks('node_modules/lodash/index.js')).toBe('vendor')
      expect(manualChunks('node_modules/other-lib/index.js')).toBe('vendor')
    })

    it('should return undefined for non-node_modules paths', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      const manualChunks = config.build.rollupOptions.output.manualChunks
      
      expect(manualChunks('src/components/MyComponent.vue')).toBeUndefined()
      expect(manualChunks('./src/utils/helper.js')).toBeUndefined()
    })

    it('should have assetsInlineLimit set to 4096', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.build.assetsInlineLimit).toBe(4096)
    })

    it('should have reportCompressedSize set to true', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.build.reportCompressedSize).toBe(true)
    })

    it('should have sourcemap set to false', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.build.sourcemap).toBe(false)
    })
  })

  describe('optimizeDeps configuration', () => {
    it('should have include array', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.optimizeDeps.include).toBeDefined()
      expect(Array.isArray(config.optimizeDeps.include)).toBe(true)
    })

    it('should include vue in optimizeDeps', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.optimizeDeps.include).toContain('vue')
    })

    it('should include vue-router in optimizeDeps', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.optimizeDeps.include).toContain('vue-router')
    })

    it('should include pinia in optimizeDeps', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.optimizeDeps.include).toContain('pinia')
    })

    it('should include axios in optimizeDeps', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.optimizeDeps.include).toContain('axios')
    })

    it('should include chart.js in optimizeDeps', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.optimizeDeps.include).toContain('chart.js')
    })

    it('should include sweetalert2 in optimizeDeps', async () => {
      const configModule = await import('../vite.config.js')
      config = configModule.default
      expect(config.optimizeDeps.include).toContain('sweetalert2')
    })
  })
})


