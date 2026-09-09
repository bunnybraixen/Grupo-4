<!--
  Modal de creación/edición de aplicación: nombre, descripción, color e
  ícono. Extraído de BuilderView.vue (el único lugar donde este formulario
  funcionaba completo) para que WorkbenchView.vue pueda ofrecer el mismo
  formulario a TEAM_LEADER sin duplicar la paleta de colores ni la grilla
  de íconos por segunda vez.
-->
<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-[100] flex items-center justify-center bg-[var(--bg-app)]/80 px-4 backdrop-blur-sm">
      <div class="w-full max-w-xl rounded-[2rem] border border-[var(--border-subtle)] bg-[var(--bg-app)] p-6 shadow-2xl shadow-black/40">
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-xs uppercase tracking-[0.22em] text-teal-30/80">{{ t('builderView.applicationsCount') }}</p>
            <h3 class="mt-1 text-2xl font-semibold text-[var(--text-primary)]">{{ title }}</h3>
          </div>
          <button type="button" class="rounded-full border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-3 py-1 text-sm text-[var(--text-secondary)]" @click="emit('close')">
            {{ t('builderView.close') }}
          </button>
        </div>

        <form class="mt-6 space-y-4" @submit.prevent="emit('submit')">
          <div>
            <label class="mb-1 block text-sm text-[var(--text-secondary)]">{{ t('builderView.formName') }}</label>
            <input
              v-model="form.name"
              type="text"
              class="w-full rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-4 py-3 text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:border-teal-40 focus:outline-none"
              :placeholder="t('builderView.appNamePlaceholder')"
            />
          </div>
          <div>
            <label class="mb-1 block text-sm text-[var(--text-secondary)]">{{ t('builderView.formDescription') }}</label>
            <textarea
              v-model="form.description"
              rows="3"
              class="w-full rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-4 py-3 text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:border-teal-40 focus:outline-none"
              :placeholder="t('builderView.appDescPlaceholder')"
            />
          </div>
          <div class="grid gap-4 md:grid-cols-2">
            <div>
              <label class="mb-1 block text-sm text-[var(--text-secondary)]">{{ t('builderView.colorLabel') }}</label>
              <div class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-panel)]/70 p-3">
                <div class="mb-3 flex items-center gap-3 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-3 py-2">
                  <span
                    class="h-8 w-8 rounded-lg border border-[var(--border-subtle)] shadow-[0_0_0_1px_rgba(255,255,255,0.06)]"
                    :style="{ backgroundColor: form.color || '#06B7B2' }"
                  />
                  <div>
                    <p class="text-[11px] uppercase tracking-[0.18em] text-[var(--text-muted)]">{{ t('builderView.currentColor') }}</p>
                    <p class="text-sm font-semibold text-[var(--text-primary)]">{{ form.color || '#06B7B2' }}</p>
                  </div>
                </div>

                <div class="grid grid-cols-6 gap-2">
                  <button
                    v-for="color in PRESET_COLORS"
                    :key="color"
                    type="button"
                    class="h-8 w-full rounded-lg border transition"
                    :class="form.color === color ? 'border-white/90 ring-2 ring-white/40' : 'border-[var(--border-subtle)] hover:border-white/40'"
                    :style="{ backgroundColor: color }"
                    :title="color"
                    @click="form.color = color"
                  />
                </div>

                <div class="mt-3 flex items-center gap-2 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-3 py-2">
                  <span class="text-xs text-[var(--text-secondary)]">{{ t('builderView.advanced') }}</span>
                  <input
                    v-model="form.color"
                    type="color"
                    class="h-8 w-10 cursor-pointer rounded border border-[var(--border-subtle)] bg-transparent p-0"
                  />
                  <input
                    v-model="form.color"
                    type="text"
                    class="w-full rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-3 py-1.5 text-xs text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:border-teal-40 focus:outline-none"
                    placeholder="#06B7B2"
                  />
                </div>
              </div>
            </div>
            <div>
              <label class="mb-1 block text-sm text-[var(--text-secondary)]">{{ t('builderView.icon') }}</label>
              <div class="mb-2 flex items-center gap-3">
                <div
                  class="flex h-10 w-10 items-center justify-center rounded-xl border border-[var(--border-subtle)]"
                  :style="{ backgroundColor: form.color || '#06B7B2' }"
                >
                  <AppIcon :icon="form.icon" :size="20" icon-class="text-white" />
                </div>
                <span class="text-sm text-[var(--text-muted)]">{{ form.icon || '—' }}</span>
              </div>
              <div class="grid grid-cols-6 gap-1.5 max-h-36 overflow-y-auto rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-panel)] p-2">
                <button
                  v-for="(comp, name) in ICON_COMPONENTS"
                  :key="name"
                  type="button"
                  class="flex items-center justify-center rounded-lg p-2 transition-all"
                  :class="form.icon === name
                    ? 'bg-[var(--teal)]/20 border border-[var(--teal)] text-[var(--teal)]'
                    : 'text-[var(--text-secondary)] hover:bg-[var(--bg-card)]/20 hover:text-[var(--text-primary)]'"
                  :title="String(name)"
                  @click="form.icon = String(name)"
                >
                  <component :is="comp" :size="18" />
                </button>
              </div>
            </div>
          </div>
          <p v-if="error" class="rounded-xl border border-[var(--priority-urg-bg)]/30 bg-[var(--priority-urg-bg)]/10 px-4 py-3 text-sm text-red-600 dark:text-red-400">{{ error }}</p>
          <div class="flex gap-3 pt-2">
            <button type="submit" :disabled="saving" class="flex-1 rounded-xl bg-teal px-4 py-3 font-semibold text-[var(--text-primary)] transition hover:bg-teal-40 disabled:opacity-50">
              {{ saving ? t('builderView.saving') : t('builderView.saveApplication') }}
            </button>
            <button type="button" class="flex-1 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-4 py-3 font-semibold text-[var(--text-primary)] transition hover:bg-[var(--bg-card)]/10" @click="emit('close')">
              {{ t('common.cancel') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import {
  Folder, Database, Monitor, Link, Home, Shield, Globe, Code,
  Server, Cloud, Zap, Box, Package, Settings, Users, Star,
  Heart, Bell, Lock, Key, Cpu, Briefcase, Layers, Rocket,
  GitBranch, Terminal
} from 'lucide-vue-next'
import AppIcon from '@/components/shared/AppIcon.vue'

const { t } = useI18n()

const ICON_COMPONENTS: Record<string, object> = {
  Folder, Database, Monitor, Link, Home, Shield, Globe, Code,
  Server, Cloud, Zap, Box, Package, Settings, Users, Star,
  Heart, Bell, Lock, Key, Cpu, Briefcase, Layers, Rocket,
  GitBranch, Terminal
}

const PRESET_COLORS = [
  '#06B7B2',
  '#0EA5E9',
  '#14B8A6',
  '#22C55E',
  '#F59E0B',
  '#F97316',
  '#EF4444',
  '#EC4899',
  '#8B5CF6',
  '#6366F1',
  '#64748B',
  '#0F172A',
]

/**
 * `form` es un objeto (reactive() en BuilderView, ref() en WorkbenchView)
 * que este componente muta directamente por referencia — no se usa
 * v-model porque BuilderView expone su `appForm` como `reactive()`, que no
 * se puede reasignar (rompería el reemplazo completo que hace v-model);
 * mutar sus propiedades sí se propaga al padre al ser el mismo objeto.
 */
defineProps<{
  open: boolean
  title: string
  saving: boolean
  error: string
  form: { name: string; description: string; color: string; icon: string }
}>()

const emit = defineEmits<{
  close: []
  submit: []
}>()
</script>
