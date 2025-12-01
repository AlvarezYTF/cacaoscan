import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useModal } from '../useModal'

describe('useModal', () => {
  let modalElement

  beforeEach(() => {
    modalElement = {
      classList: {
        add: vi.fn(),
        remove: vi.fn()
      },
      setAttribute: vi.fn()
    }
  })

  it('should initialize with closed state', () => {
    const { isOpen, modalContainer } = useModal()

    expect(isOpen.value).toBe(false)
    expect(modalContainer.value).toBe(null)
  })

  it('should open modal', () => {
    const { openModal, isOpen, modalContainer } = useModal()
    modalContainer.value = modalElement

    openModal()

    expect(isOpen.value).toBe(true)
    expect(modalElement.classList.remove).toHaveBeenCalledWith('hidden')
    expect(modalElement.setAttribute).toHaveBeenCalledWith('aria-hidden', 'false')
  })

  it('should close modal', () => {
    const { closeModal, isOpen, modalContainer } = useModal()
    modalContainer.value = modalElement
    isOpen.value = true

    closeModal()

    expect(isOpen.value).toBe(false)
    expect(modalElement.classList.add).toHaveBeenCalledWith('hidden')
    expect(modalElement.setAttribute).toHaveBeenCalledWith('aria-hidden', 'true')
  })

  it('should toggle modal from closed to open', () => {
    const { toggleModal, isOpen, modalContainer } = useModal()
    modalContainer.value = modalElement

    toggleModal()

    expect(isOpen.value).toBe(true)
  })

  it('should toggle modal from open to closed', () => {
    const { toggleModal, isOpen, modalContainer } = useModal()
    modalContainer.value = modalElement
    isOpen.value = true

    toggleModal()

    expect(isOpen.value).toBe(false)
  })

  it('should handle openModal when modalContainer is null', () => {
    const { openModal, isOpen } = useModal()

    openModal()

    expect(isOpen.value).toBe(true)
  })

  it('should handle closeModal when modalContainer is null', () => {
    const { closeModal, isOpen } = useModal()
    isOpen.value = true

    closeModal()

    expect(isOpen.value).toBe(false)
  })
})

