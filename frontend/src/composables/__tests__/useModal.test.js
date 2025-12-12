/**
 * Unit tests for useModal composable
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { useModal } from '../useModal.js'

describe('useModal', () => {
  let modal

  beforeEach(() => {
    vi.clearAllMocks()
    document.body.style.overflow = ''
    modal = useModal()
  })

  afterEach(() => {
    document.body.style.overflow = ''
  })

  describe('initial state', () => {
    it('should have initial closed state', () => {
      expect(modal.isOpen.value).toBe(false)
      expect(modal.isClosing.value).toBe(false)
      expect(modal.isVisible.value).toBe(false)
    })
  })

  describe('open', () => {
    it('should open modal', () => {
      modal.open()
      
      expect(modal.isOpen.value).toBe(true)
      expect(modal.isClosing.value).toBe(false)
      expect(modal.isVisible.value).toBe(true)
    })

    it('should prevent body scroll when opened', () => {
      modal.open()
      
      expect(document.body.style.overflow).toBe('hidden')
    })

    it('should call onOpen callback if provided', () => {
      const onOpen = vi.fn()
      const modalWithCallback = useModal({ onOpen })
      
      modalWithCallback.open()
      
      expect(onOpen).toHaveBeenCalled()
    })

    it('should not open if already open', () => {
      modal.open()
      const onOpen = vi.fn()
      const modalWithCallback = useModal({ onOpen })
      modalWithCallback.open()
      
      modal.open()
      
      expect(modal.isOpen.value).toBe(true)
    })
  })

  describe('close', () => {
    it('should close modal', async () => {
      modal.open()
      modal.close()
      
      expect(modal.isClosing.value).toBe(true)
      
      // Wait for animation
      await new Promise(resolve => setTimeout(resolve, 350))
      
      expect(modal.isOpen.value).toBe(false)
      expect(modal.isClosing.value).toBe(false)
    })

    it('should restore body scroll when closed', async () => {
      modal.open()
      modal.close()
      
      await new Promise(resolve => setTimeout(resolve, 350))
      
      expect(document.body.style.overflow).toBe('')
    })

    it('should call onClose callback if provided', async () => {
      const onClose = vi.fn()
      const modalWithCallback = useModal({ onClose })
      
      modalWithCallback.open()
      modalWithCallback.close()
      
      await new Promise(resolve => setTimeout(resolve, 350))
      
      expect(onClose).toHaveBeenCalled()
    })

    it('should not close if already closed', () => {
      const onClose = vi.fn()
      const modalWithCallback = useModal({ onClose })
      
      modalWithCallback.close()
      
      expect(onClose).not.toHaveBeenCalled()
    })
  })

  describe('toggle', () => {
    it('should open when closed', () => {
      modal.toggle()
      
      expect(modal.isOpen.value).toBe(true)
    })

    it('should close when open', async () => {
      modal.open()
      modal.toggle()
      
      await new Promise(resolve => setTimeout(resolve, 350))
      
      expect(modal.isOpen.value).toBe(false)
    })
  })

  describe('handleBackdropClick', () => {
    it('should close when closeOnBackdrop is true', async () => {
      modal.open()
      modal.handleBackdropClick()
      
      await new Promise(resolve => setTimeout(resolve, 350))
      
      expect(modal.isOpen.value).toBe(false)
    })

    it('should not close when closeOnBackdrop is false', () => {
      const modalNoBackdrop = useModal({ closeOnBackdrop: false })
      modalNoBackdrop.open()
      modalNoBackdrop.handleBackdropClick()
      
      expect(modalNoBackdrop.isOpen.value).toBe(true)
    })
  })

  describe('handleEscape', () => {
    it('should close on Escape key when closeOnEscape is true', async () => {
      modal.open()
      const escapeEvent = new KeyboardEvent('keydown', { key: 'Escape' })
      modal.handleEscape(escapeEvent)
      
      await new Promise(resolve => setTimeout(resolve, 350))
      
      expect(modal.isOpen.value).toBe(false)
    })

    it('should not close on other keys', () => {
      modal.open()
      const enterEvent = new KeyboardEvent('keydown', { key: 'Enter' })
      modal.handleEscape(enterEvent)
      
      expect(modal.isOpen.value).toBe(true)
    })

    it('should not close when closeOnEscape is false', () => {
      const modalNoEscape = useModal({ closeOnEscape: false })
      modalNoEscape.open()
      const escapeEvent = new KeyboardEvent('keydown', { key: 'Escape' })
      modalNoEscape.handleEscape(escapeEvent)
      
      expect(modalNoEscape.isOpen.value).toBe(true)
    })
  })

  describe('isVisible computed', () => {
    it('should be visible when open and not closing', () => {
      modal.open()
      
      expect(modal.isVisible.value).toBe(true)
    })

    it('should not be visible when closing', () => {
      modal.open()
      modal.close()
      
      expect(modal.isVisible.value).toBe(false)
    })
  })
})

