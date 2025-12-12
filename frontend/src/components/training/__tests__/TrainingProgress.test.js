/**
 * Unit tests for TrainingProgress component
 * Tests all functionality including props, events, rendering states, and progress calculation
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import TrainingProgress from '../TrainingProgress.vue'

describe('TrainingProgress', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.clearAllMocks()
  })

  describe('Props validation', () => {
    it('should accept all props with default values', () => {
      wrapper = mount(TrainingProgress)
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.props('isTraining')).toBe(false)
      expect(wrapper.props('progress')).toBe(0)
      expect(wrapper.props('currentEpoch')).toBe(0)
      expect(wrapper.props('totalEpochs')).toBe(100)
      expect(wrapper.props('trainingStatus')).toBe('')
    })

    it('should accept isTraining prop', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: true
        }
      })
      expect(wrapper.props('isTraining')).toBe(true)
    })

    it('should accept progress prop', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          progress: 50
        }
      })
      expect(wrapper.props('progress')).toBe(50)
    })

    it('should accept currentEpoch prop', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          currentEpoch: 25
        }
      })
      expect(wrapper.props('currentEpoch')).toBe(25)
    })

    it('should accept totalEpochs prop', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          totalEpochs: 50
        }
      })
      expect(wrapper.props('totalEpochs')).toBe(50)
    })

    it('should accept trainingStatus prop', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          trainingStatus: 'Training in progress'
        }
      })
      expect(wrapper.props('trainingStatus')).toBe('Training in progress')
    })
  })

  describe('Rendering - Not training state', () => {
    beforeEach(() => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: false,
          progress: 0
        }
      })
    })

    it('should render component title', () => {
      expect(wrapper.text()).toContain('Estado del Entrenamiento')
    })

    it('should show not training message', () => {
      expect(wrapper.text()).toContain('No hay entrenamiento activo')
      expect(wrapper.text()).toContain('Inicia un entrenamiento para ver el progreso aquí')
    })

    it('should show start training button', () => {
      const button = wrapper.find('button')
      expect(button.exists()).toBe(true)
      expect(button.text()).toContain('Iniciar Entrenamiento')
    })

    it('should not show training progress when not training', () => {
      // Look for the progress bar container that only appears when training
      // The progress bar container has classes "w-full bg-gray-200 rounded-full h-3"
      const progressBarContainer = wrapper.find('.bg-gray-200.rounded-full.h-3')
      expect(progressBarContainer.exists()).toBe(false)
    })

    it('should not show training metrics when not training', () => {
      expect(wrapper.text()).not.toContain('Métricas de Entrenamiento')
    })
  })

  describe('Rendering - Training in progress state', () => {
    beforeEach(() => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: true,
          progress: 45.5,
          currentEpoch: 23,
          totalEpochs: 50,
          trainingStatus: 'Entrenando modelo...'
        }
      })
    })

    it('should show training status', () => {
      expect(wrapper.text()).toContain('Entrenando modelo...')
    })

    it('should display progress percentage', () => {
      expect(wrapper.text()).toContain('46%')
    })

    it('should render progress bar with correct width', () => {
      const progressBar = wrapper.find('.bg-green-600')
      expect(progressBar.exists()).toBe(true)
      expect(progressBar.attributes('style')).toContain('width: 45.5%')
    })

    it('should display current epoch', () => {
      expect(wrapper.text()).toContain('23')
      expect(wrapper.text()).toContain('Época Actual')
    })

    it('should display total epochs', () => {
      expect(wrapper.text()).toContain('50')
      expect(wrapper.text()).toContain('Total Épocas')
    })

    it('should show training metrics section', () => {
      expect(wrapper.text()).toContain('Métricas de Entrenamiento')
      expect(wrapper.text()).toContain('Loss:')
      expect(wrapper.text()).toContain('Accuracy:')
      expect(wrapper.text()).toContain('Val Loss:')
      expect(wrapper.text()).toContain('Val Accuracy:')
    })

    it('should show stop training button', () => {
      const button = wrapper.find('button')
      expect(button.exists()).toBe(true)
      expect(button.text()).toContain('Detener Entrenamiento')
    })

    it('should round progress percentage correctly', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: true,
          progress: 33.7
        }
      })
      expect(wrapper.text()).toContain('34%')
    })

    it('should handle 100% progress during training', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: true,
          progress: 100
        }
      })
      expect(wrapper.text()).toContain('100%')
      const progressBar = wrapper.find('.bg-green-600')
      expect(progressBar.attributes('style')).toContain('width: 100%')
    })
  })

  describe('Rendering - Training completed state', () => {
    beforeEach(() => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: false,
          progress: 100
        }
      })
    })

    it('should show completion message', () => {
      expect(wrapper.text()).toContain('Entrenamiento Completado')
      expect(wrapper.text()).toContain('El modelo ha sido entrenado exitosamente')
    })

    it('should show retrain button', () => {
      const buttons = wrapper.findAll('button')
      const retrainButton = buttons.find(btn => btn.text().includes('Reentrenar'))
      expect(retrainButton).toBeDefined()
      expect(retrainButton.exists()).toBe(true)
    })

    it('should show view metrics button', () => {
      const buttons = wrapper.findAll('button')
      const viewMetricsButton = buttons.find(btn => btn.text().includes('Ver Métricas'))
      expect(viewMetricsButton).toBeDefined()
      expect(viewMetricsButton.exists()).toBe(true)
    })
  })

  describe('Events', () => {
    it('should emit start-training when start button is clicked in not training state', async () => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: false,
          progress: 0
        }
      })

      const button = wrapper.find('button')
      await button.trigger('click')

      expect(wrapper.emitted('start-training')).toBeTruthy()
      expect(wrapper.emitted('start-training').length).toBe(1)
    })

    it('should emit stop-training when stop button is clicked during training', async () => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: true,
          progress: 50
        }
      })

      const button = wrapper.find('button')
      await button.trigger('click')

      expect(wrapper.emitted('stop-training')).toBeTruthy()
      expect(wrapper.emitted('stop-training').length).toBe(1)
    })

    it('should emit start-training when retrain button is clicked in completed state', async () => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: false,
          progress: 100
        }
      })

      const buttons = wrapper.findAll('button')
      const retrainButton = buttons.find(btn => btn.text().includes('Reentrenar'))
      await retrainButton.trigger('click')

      expect(wrapper.emitted('start-training')).toBeTruthy()
      expect(wrapper.emitted('start-training').length).toBe(1)
    })
  })

  describe('Progress calculation', () => {
    it('should display 0% when progress is 0', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: true,
          progress: 0
        }
      })
      expect(wrapper.text()).toContain('0%')
    })

    it('should display 50% when progress is 50', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: true,
          progress: 50
        }
      })
      expect(wrapper.text()).toContain('50%')
    })

    it('should display 100% when progress is 100', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: true,
          progress: 100
        }
      })
      expect(wrapper.text()).toContain('100%')
    })

    it('should round decimal progress values correctly', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: true,
          progress: 33.333
        }
      })
      expect(wrapper.text()).toContain('33%')
    })

    it('should round up correctly for values close to next integer', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: true,
          progress: 33.6
        }
      })
      expect(wrapper.text()).toContain('34%')
    })
  })

  describe('Epoch display', () => {
    it('should display epoch 0 when training starts', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: true,
          currentEpoch: 0,
          totalEpochs: 100
        }
      })
      expect(wrapper.text()).toContain('0')
      expect(wrapper.text()).toContain('100')
    })

    it('should display correct epoch values during training', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: true,
          currentEpoch: 15,
          totalEpochs: 30
        }
      })
      expect(wrapper.text()).toContain('15')
      expect(wrapper.text()).toContain('30')
    })

    it('should display final epoch when training completes', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: true,
          currentEpoch: 100,
          totalEpochs: 100
        }
      })
      expect(wrapper.text()).toContain('100')
    })
  })

  describe('Edge cases', () => {
    it('should handle negative progress value', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: true,
          progress: -10
        }
      })
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.text()).toContain('-10%')
    })

    it('should handle progress over 100%', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: true,
          progress: 150
        }
      })
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.text()).toContain('150%')
      const progressBar = wrapper.find('.bg-green-600')
      expect(progressBar.attributes('style')).toContain('width: 150%')
    })

    it('should handle empty training status', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: true,
          trainingStatus: ''
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle zero total epochs', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: true,
          totalEpochs: 0
        }
      })
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.text()).toContain('0')
    })

    it('should handle current epoch greater than total epochs', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: true,
          currentEpoch: 150,
          totalEpochs: 100
        }
      })
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.text()).toContain('150')
      expect(wrapper.text()).toContain('100')
    })

    it('should not show completed state when progress is 100 but isTraining is true', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: true,
          progress: 100
        }
      })
      expect(wrapper.text()).not.toContain('Entrenamiento Completado')
      expect(wrapper.text()).toContain('Detener Entrenamiento')
    })
  })

  describe('Component structure', () => {
    it('should have correct CSS classes for card container', () => {
      wrapper = mount(TrainingProgress)
      const container = wrapper.find('.bg-white.rounded-lg')
      expect(container.exists()).toBe(true)
    })

    it('should have correct structure with header and body', () => {
      wrapper = mount(TrainingProgress)
      expect(wrapper.find('.px-6.py-4.border-b').exists()).toBe(true)
      expect(wrapper.find('.p-6').exists()).toBe(true)
    })

    it('should apply transition classes to progress bar', () => {
      wrapper = mount(TrainingProgress, {
        props: {
          isTraining: true,
          progress: 50
        }
      })
      const progressBar = wrapper.find('.bg-green-600')
      expect(progressBar.classes()).toContain('transition-all')
      expect(progressBar.classes()).toContain('duration-500')
    })
  })
})

