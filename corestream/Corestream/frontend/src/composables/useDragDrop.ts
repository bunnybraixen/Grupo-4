/**
 * Composable useDragDrop.ts
 * 
 * Composable para funcionalidad de Drag & Drop (arrastrar y soltar) en CoreStream.
 * Gestiona el arrastre de épicas (para reordenar) y tickets (para mover entre épicas).
 * Proporciona feedback visual en tiempo real durante el arrastre.
 * 
 * Características:
 * - Soporte para arrastrar épicas y tickets
 * - Validación de zonas de drop válidas
 * - Feedback visual con clases CSS dinámicas
 * - Prevención de comportamiento por defecto del navegador
 * - Métodos helper para obtener clases CSS según estado
 * - Limpieza automática al desmontar
 * 
 * Flujo de uso:
 * 1. dragStart(item, type) → Inicia arrastre
 * 2. dragOver(e, targetId) → Detecta sobre qué se arrastra
 * 3. drop(e, targetId, targetType) → Suelta el item en destino
 * 4. dragEnd() → Finaliza y limpia el estado
 * 
 * Uso en template:
 * <div
 *   draggable="true"
 *   @dragstart="dragStart(epic, 'epic')"
 *   @dragover="dragOver($event, epic.id)"
 *   @drop="drop($event, epic.id, 'epic')"
 *   @dragend="dragEnd"
 *   :class="getDragClasses(epic.id)"
 * >
 */

import { ref, onUnmounted } from 'vue'
import type { Ref } from 'vue'

/**
 * Interfaz para un item que puede ser arrastrado
 */
interface DraggableItem {
  id: string
  [key: string]: any
}

/**
 * Resultado de una operación de drop
 */
interface DropResult {
  item: DraggableItem
  type: 'epic' | 'ticket'
  targetId: string
}

/**
 * Composable para gestionar drag & drop
 * Proporciona control completo sobre arrastres en la aplicación
 * 
 * @returns Objeto con propiedades y métodos de drag & drop
 */
export function useDragDrop() {
  // =========================================================================
  // ESTADO REACTIVO - Variables para rastrear el estado del arrastre
  // =========================================================================

  /**
   * Indica si actualmente hay un arrastre en progreso
   * true = algo está siendo arrastrado, false = no hay arrastre
   */
  const isDragging: Ref<boolean> = ref(false)

  /**
   * El item (épica o ticket) que está siendo arrastrado actualmente
   * null si no hay arrastre en progreso
   */
  const dragItem: Ref<DraggableItem | null> = ref(null)

  /**
   * Tipo del item siendo arrastrado ('epic' o 'ticket')
   * null si no hay arrastre en progreso
   */
  const dragType: Ref<'epic' | 'ticket' | null> = ref(null)

  /**
   * ID del elemento sobre el cual se está arrastrando actualmente
   * Se usa para mostrar feedback visual de zona de drop válida
   * null si no se está sobre ningún elemento válido
   */
  const dragOverTarget: Ref<string | null> = ref(null)

  // =========================================================================
  // VARIABLES PRIVADAS - Para control del arrastre
  // =========================================================================

  /**
   * Datos de transferencia del arrastre (dataTransfer del evento)
   * Se usa para pasar información personalizada entre eventos drag
   */
  let dragData: Record<string, any> = {}

  /**
   * Contador de operaciones dragenter/dragleave
   * Usado para determinar cuándo salimos completamente de un elemento
   * (considerando elementos anidados)
   */
  let dragOverCount = 0

  // =========================================================================
  // CONSTANTES - Clases CSS para feedback visual
  // =========================================================================

  /**
   * Clase CSS para elementos siendo arrastrados
   * Aplicada al elemento origen del arrastre
   */
  const DRAGGING_CLASS = 'opacity-50 bg-gray-200 cursor-move'

  /**
   * Clase CSS para zonas de drop válidas
   * Aplicada al elemento sobre el cual se arrastra
   */
  const DROP_ZONE_CLASS = 'border-2 border-blue-400 bg-blue-50'

  /**
   * Clase CSS para elementos siendo eliminados
   * Aplicada cuando el arrastre indica una eliminación
   */
  const DROP_DELETE_CLASS = 'border-2 border-red-400 bg-red-50'

  // =========================================================================
  // MÉTODOS PÚBLICOS - API del composable de drag & drop
  // =========================================================================

  /**
   * Inicia un arrastre de un item (épica o ticket)
   * Configura el estado para rastrear qué se está arrastrando
   * Se llama en el evento @dragstart del elemento arrastrable
   * 
   * @param item - Item a arrastrar (épica o ticket)
   * @param type - Tipo del item ('epic' o 'ticket')
   */
  function dragStart(item: DraggableItem, type: 'epic' | 'ticket'): void {
    // Registrar que hay arrastre en progreso
    isDragging.value = true

    // Guardar el item y su tipo para posterior referencia
    dragItem.value = item
    dragType.value = type

    // Resetear contador de dragover
    dragOverCount = 0

    // Guardar datos para posible transferencia
    dragData = {
      itemId: item.id,
      itemType: type,
      timestamp: Date.now()
    }

    console.log(`Iniciando arrastre de ${type}:`, item.id)
  }

  /**
   * Maneja el evento dragend cuando termina el arrastre
   * Reseta completamente el estado del arrastre
   * Se llama en el evento @dragend del elemento arrastrable
   * 
   * Es importante llamar a esta función al final de cualquier operación
   * de arrastre para limpiar el estado
   */
  function dragEnd(): void {
    // Limpiar estado completamente
    isDragging.value = false
    dragItem.value = null
    dragType.value = null
    dragOverTarget.value = null
    dragOverCount = 0

    // Limpiar datos de transferencia
    dragData = {}

    console.log('Arrastre finalizado y estado limpiado')
  }

  /**
   * Maneja el evento dragover para detectar cuándo se arrastra sobre elementos
   * Previene el comportamiento por defecto del navegador
   * Actualiza el destino sobre el cual se está arrastrando
   * Se llama en el evento @dragover de las zonas de drop
   * 
   * @param e - Evento DragEvent del navegador
   * @param targetId - ID del elemento sobre el cual se está arrastrando
   */
  function dragOver(e: DragEvent, targetId: string): void {
    // Prevenir comportamiento por defecto (necesario para permitir drop)
    e.preventDefault()

    // Prevenir propagación para evitar interferencia con elementos anidados
    e.stopPropagation()

    // Actualizar destino actual
    dragOverTarget.value = targetId

    // Indicar que el drop es permitido
    if (e.dataTransfer) {
      e.dataTransfer.dropEffect = 'move'
    }

    console.debug(`Arrastrando sobre: ${targetId}`)
  }

  /**
   * Maneja el evento drop cuando se suelta un item en una zona válida
   * Valida la operación y retorna información del drop
   * Se llama en el evento @drop de las zonas de drop válidas
   * 
   * @param e - Evento DragEvent del navegador
   * @param targetId - ID del destino donde se suelta el item
   * @param targetType - Tipo del destino ('epic' o 'ticket')
   * @returns Objeto DropResult con información del drop, o null si es inválido
   */
  function drop(
    e: DragEvent,
    targetId: string,
    targetType: string
  ): DropResult | null {
    // Prevenir comportamiento por defecto
    e.preventDefault()
    e.stopPropagation()

    // Validar que hay un item siendo arrastrado
    if (!dragItem.value || !dragType.value) {
      console.warn('No hay item siendo arrastrado')
      return null
    }

    // Validar que no estamos soltando sobre el mismo elemento
    if (dragItem.value.id === targetId) {
      console.warn('No se puede soltar sobre el mismo elemento')
      dragEnd()
      return null
    }

    // Validar compatibilidad de tipos según el objetivo
    const isValidDrop = validateDropTarget(targetType)
    if (!isValidDrop) {
      console.warn(
        `Drop inválido: no se puede soltar ${dragType.value} en ${targetType}`
      )
      dragEnd()
      return null
    }

    // Crear resultado del drop
    const result: DropResult = {
      item: dragItem.value,
      type: dragType.value,
      targetId: targetId
    }

    console.log('Drop válido:', result)

    // Limpiar estado después del drop
    dragEnd()

    return result
  }

  // =========================================================================
  // MÉTODOS HELPER - Funciones de soporte para drag & drop
  // =========================================================================

  /**
   * Valida si un destino es válido para soltar el item actual
   * Reglas de validación:
   * - Épica puede soltarse en posición para reordenar (otro área de épica)
   * - Ticket puede soltarse en épica para cambiar de grupo
   * 
   * @param targetType - Tipo del destino
   * @returns true si es un drop válido, false si no
   */
  function validateDropTarget(targetType: string): boolean {
    // Si estamos arrastrando una épica, solo puede soltarse en otra épica
    if (dragType.value === 'epic') {
      return targetType === 'epic'
    }

    // Si estamos arrastrando un ticket, puede soltarse en épica
    if (dragType.value === 'ticket') {
      return targetType === 'epic'
    }

    return false
  }

  /**
   * Retorna las clases CSS dinámicas para feedback visual del arrastre
   * Proporciona estilos visuales para:
   * - Elemento siendo arrastrado (opacidad)
   * - Zona sobre la cual se arrastra (borde y fondo coloreado)
   * 
   * @param elementId - ID del elemento a evaluar
   * @returns String de clases CSS de Tailwind para aplicar al elemento
   */
  function getDragClasses(elementId: string): string {
    const classes: string[] = []

    // Si este elemento es el que se está arrastrando, marcar como tal
    if (isDragging.value && dragItem.value?.id === elementId) {
      classes.push(DRAGGING_CLASS)
    }

    // Si este elemento es el destino del arrastre, mostrar zona de drop
    if (dragOverTarget.value === elementId && isDragging.value) {
      // Evaluar tipo de drop para mostrar color apropiado
      if (dragType.value === 'ticket') {
        // Para tickets, mostrar zona válida (azul)
        classes.push(DROP_ZONE_CLASS)
      } else if (dragType.value === 'epic') {
        // Para épicas, mostrar zona de reorden (azul también)
        classes.push(DROP_ZONE_CLASS)
      }
    }

    return classes.join(' ')
  }

  /**
   * Obtiene información sobre el arrastre actual
   * Útil para debugging y logging
   * 
   * @returns Objeto con información del estado actual del arrastre
   */
  function getDragInfo() {
    return {
      isDragging: isDragging.value,
      dragItem: dragItem.value,
      dragType: dragType.value,
      dragOverTarget: dragOverTarget.value,
      dragData: dragData
    }
  }

  /**
   * Cancela el arrastre actual sin ejecutar el drop
   * Se puede usar para responder a un evento de escape del usuario
   */
  function cancelDrag(): void {
    dragEnd()
    console.log('Arrastre cancelado por usuario')
  }

  // =========================================================================
  // LIMPIEZA - Hook de desmontaje del componente
  // =========================================================================

  /**
   * Hook de ciclo de vida: se ejecuta cuando el componente es desmontado
   * Garantiza la limpieza del estado de arrastre
   * Evita estado inconsistente si el componente se desmonta durante arrastre
   */
  onUnmounted(() => {
    dragEnd()
    console.log('Composable useDragDrop desmontado')
  })

  // =========================================================================
  // RETORNO DEL COMPOSABLE - API pública
  // =========================================================================

  return {
    // Propiedades reactivas para rastrear estado
    isDragging,       // true si algo está siendo arrastrado
    dragItem,         // Item actual siendo arrastrado
    dragType,         // Tipo del item ('epic' o 'ticket')
    dragOverTarget,   // ID del elemento sobre el cual se arrastra

    // Métodos principales para eventos drag
    dragStart,  // Iniciar arrastre
    dragEnd,    // Finalizar arrastre
    dragOver,   // Manejar dragover
    drop,       // Manejar drop

    // Métodos helper y utilidades
    getDragClasses,   // Obtener clases CSS para feedback visual
    getDragInfo,      // Obtener información del estado actual
    cancelDrag        // Cancelar arrastre sin completar
  }
}
