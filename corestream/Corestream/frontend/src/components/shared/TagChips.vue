<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: TagChips                                             -->
  <!-- ================================================================ -->
  <!-- NEW-03: chips de solo lectura con las etiquetas de un ticket.     -->
  <!-- Se reutiliza en las tarjetas del tablero, en la lista del         -->
  <!-- Workbench y en los paneles de detalle para "actualizar etiquetas  -->
  <!-- mostradas en el ticket" sin duplicar markup en cada vista.        -->
  <!-- ================================================================ -->

  <div v-if="tagList.length" class="flex flex-wrap items-center gap-1">
    <span
      v-for="tag in tagList"
      :key="tag.id"
      :class="[
        'inline-flex items-center gap-1 rounded-full border border-[var(--teal)]/40 bg-[var(--teal)]/10 text-[var(--teal)] font-medium',
        size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2 py-0.5 text-[11px]',
      ]"
      :title="tag.name"
    >
      <span v-if="showIcon" aria-hidden="true">🏷</span>
      <span class="max-w-[12rem] truncate">{{ tag.name }}</span>
    </span>
  </div>
  <span v-else-if="showEmpty" class="text-xs italic text-[var(--text-muted)]">{{ emptyLabel }}</span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Tag } from '@/types'

const props = withDefaults(
  defineProps<{
    /** Etiquetas del ticket (opcional: los tickets sin etiquetas no se marcan) */
    tags?: Tag[] | null
    /** Tamaño del chip */
    size?: 'sm' | 'xs'
    /** Muestra el emoji 🏷 antes del nombre */
    showIcon?: boolean
    /** Muestra un texto cuando el ticket no tiene etiquetas */
    showEmpty?: boolean
    /** Texto a mostrar cuando no hay etiquetas y showEmpty es true */
    emptyLabel?: string
  }>(),
  {
    tags: null,
    size: 'sm',
    showIcon: true,
    showEmpty: false,
    emptyLabel: 'Sin etiquetas',
  }
)

const tagList = computed<Tag[]>(() => props.tags ?? [])
</script>
