/**
 * Composable para Drag & Drop de Épicas
 * Maneja la lógica visual y de reordenamiento
 * 
 * CS-012: Implementa reordenamiento de épicas con drag & drop
 * - Efectos visuales de elevación (shadow, transform)
 * - Drop zones entre épicas
 * - Persistencia via API PATCH
 */

import { ref, computed } from 'vue'
import type { Epic } from '@/types'

export const useDragDropEpics = () => {
  // Estado de arrastre
  const draggedEpicId = ref<string | null>(null)
  const dragOverEpicId = ref<string | null>(null)
  const dragPosition = ref<'above' | 'below' | null>(null)

  /**
   * Inicia el arrastre de una épica
   */
  const handleEpicDragStart = (epic: Epic, event: DragEvent) => {
    draggedEpicId.value = epic.id
    if (event.dataTransfer) {
      event.dataTransfer.effectAllowed = 'move'
      event.dataTransfer.setData('epicId', epic.id)
      event.dataTransfer.setData('text/html', epic.title)
    }
  }

  /**
   * Termina el arrastre
   */
  const handleEpicDragEnd = () => {
    draggedEpicId.value = null
    dragOverEpicId.value = null
    dragPosition.value = null
  }

  /**
   * Maneja el over de un área droppable
   * Detecta si el usuario quiere colocar arriba o abajo
   */
  const handleEpicDragOver = (epic: Epic, event: DragEvent) => {
    event.preventDefault()
    event.dataTransfer!.dropEffect = 'move'

    dragOverEpicId.value = epic.id
    
    // Calcular si es arriba o abajo basado en la posición del mouse
    const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
    const midpoint = rect.height / 2
    const y = event.clientY - rect.top
    
    dragPosition.value = y < midpoint ? 'above' : 'below'
  }

  /**
   * Maneja cuando el usuario sale del área
   */
  const handleEpicDragLeave = () => {
    dragOverEpicId.value = null
    dragPosition.value = null
  }

  /**
   * Calcula la nueva posición después del drop
   * Retorna el nuevo índice o null si no es válido
   */
  const calculateNewIndex = (
    epics: Epic[],
    draggedId: string,
    targetId: string,
    position: 'above' | 'below' | null
  ): number | null => {
    if (!targetId || !position) return null

    const draggedIndex = epics.findIndex(e => e.id === draggedId)
    const targetIndex = epics.findIndex(e => e.id === targetId)

    if (draggedIndex === -1 || targetIndex === -1 || draggedIndex === targetIndex) {
      return null
    }

    return position === 'above' ? targetIndex : targetIndex + 1
  }

  /**
   * Determina si un épica está siendo arrastrada
   */
  const isDragging = computed(() => draggedEpicId.value !== null)

  /**
   * Determina si mostrar indicador de drop
   */
  const isDropTarget = computed(() => dragOverEpicId.value !== null && dragPosition.value !== null)

  /**
   * Estilos dinámicos para épica siendo arrastrada
   */
  const getDraggedEpicClass = (epic: Epic): string => {
    if (draggedEpicId.value === epic.id) {
      return 'opacity-50 cursor-grabbing'
    }
    return ''
  }

  /**
   * Estilos para indicador de drop
   */
  const getDropIndicatorClass = (epic: Epic): string => {
    if (dragOverEpicId.value === epic.id && dragPosition.value) {
      return dragPosition.value === 'above'
        ? 'border-t-2 border-t-emerald-500 pt-2'
        : 'border-b-2 border-b-emerald-500 pb-2'
    }
    return ''
  }

  /**
   * Estilos para elevación visual
   */
  const getEpicElevationClass = (epic: Epic): string => {
    if (isDragging.value && draggedEpicId.value !== epic.id && dragOverEpicId.value === epic.id) {
      return 'shadow-2xl shadow-emerald-500/20 transform hover:translate-y-1'
    }
    return ''
  }

  return {
    draggedEpicId,
    dragOverEpicId,
    dragPosition,
    isDragging,
    isDropTarget,
    handleEpicDragStart,
    handleEpicDragEnd,
    handleEpicDragOver,
    handleEpicDragLeave,
    calculateNewIndex,
    getDraggedEpicClass,
    getDropIndicatorClass,
    getEpicElevationClass,
  }
}
