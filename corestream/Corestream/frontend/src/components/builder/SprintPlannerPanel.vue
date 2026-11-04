<!--
  SprintPlannerPanel - Planificación y seguimiento de Sprints

  Se muestra dentro de /admin/builder (pestaña "Sprints") y permite a ADMIN y
  GROUP_LEADER:
    - Crear / editar / eliminar Sprints de un proyecto (nombre, fechas, objetivo)
    - Asociar y quitar Tickets EXISTENTES (sin tocar su Épica)
    - Ver el resumen: pendientes, completados, bloqueados, progreso y Velocity
    - Reutilizar el Kanban existente (tablero por estado con TicketCard)
    - Cerrar el Sprint calculando automáticamente su Velocity
    - Ver las métricas agregadas de SLA del Sprint (el SLA es por ticket)
-->
<template>
  <section class="space-y-6">
    <!-- ============================ ENCABEZADO ============================ -->
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h2 class="text-xl font-bold text-[var(--text-primary)]">{{ t('builderPage.sprintPlanner.title') }}</h2>
        <p class="mt-1 text-sm text-[var(--text-muted)]">
          {{ t('builderPage.sprintPlanner.subtitle') }}
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <select
          v-model="projectFilter"
          class="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)] px-3 py-2 text-sm text-[var(--text-primary)]"
        >
          <option value="">{{ t('builderPage.sprintPlanner.allProjects') }}</option>
          <option v-for="app in applications" :key="app.id" :value="app.id">
            {{ app.name }}
          </option>
        </select>

        <button
          v-if="canManage"
          type="button"
          class="rounded-lg bg-[var(--teal-action)] px-3 py-2 text-sm text-white hover:bg-[var(--teal-90)]"
          @click="openCreateForm"
        >
          {{ t('builderPage.sprintPlanner.newSprint') }}
        </button>
      </div>
    </div>

    <p v-if="store.error" class="rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-400">
      {{ store.error }}
    </p>

    <!-- ============================ FORMULARIO ============================ -->
    <form
      v-if="showForm"
      ref="formSection"
      class="space-y-4 rounded-2xl border border-[var(--teal)]/40 bg-[var(--bg-card)] p-4"
      @submit.prevent="submitForm"
    >
      <h3 class="font-semibold text-[var(--text-primary)]">
        {{ editingId ? t('builderPage.sprintPlanner.editSprint') : t('builderPage.sprintPlanner.newSprintDialog') }}
      </h3>

      <p
        v-if="formError"
        class="rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-400"
      >
        {{ formError }}
      </p>

      <div class="grid gap-3 md:grid-cols-2">
        <label class="block text-sm">
          <span class="text-[var(--text-muted)]">{{ t('builderPage.sprintPlanner.name') }}</span>
          <input
            v-model="form.name"
            type="text"
            required
            :placeholder="t('builderPage.sprintPlanner.name')"
            class="mt-1 w-full rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)] px-3 py-2 text-sm text-[var(--text-primary)]"
          />
        </label>

        <label class="block text-sm">
          <span class="text-[var(--text-muted)]">{{ t('builderPage.sprintPlanner.project') }}</span>
          <select
            v-model="form.applicationId"
            required
            :disabled="Boolean(editingId)"
            class="mt-1 w-full rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)] px-3 py-2 text-sm text-[var(--text-primary)] disabled:opacity-60"
          >
            <option value="" disabled>{{ t('builderPage.sprintPlanner.selectProject') }}</option>
            <option v-for="app in applications" :key="app.id" :value="app.id">
              {{ app.name }}
            </option>
          </select>
        </label>

        <label class="block text-sm">
          <span class="text-[var(--text-muted)]">{{ t('builderPage.sprintPlanner.startDate') }}</span>
          <input
            v-model="form.startDate"
            type="datetime-local"
            required
            class="mt-1 w-full rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)] px-3 py-2 text-sm text-[var(--text-primary)]"
          />
        </label>

        <label class="block text-sm">
          <span class="text-[var(--text-muted)]">{{ t('builderPage.sprintPlanner.endDate') }}</span>
          <input
            v-model="form.endDate"
            type="datetime-local"
            required
            class="mt-1 w-full rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)] px-3 py-2 text-sm text-[var(--text-primary)]"
          />
        </label>

        <label class="block text-sm md:col-span-2">
          <span class="text-[var(--text-muted)]">{{ t('builderPage.sprintPlanner.sprintGoal') }}</span>
          <textarea
            v-model="form.goal"
            rows="2"
            :placeholder="t('builderPage.sprintPlanner.sprintGoalPlaceholder')"
            class="mt-1 w-full resize-none rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)] px-3 py-2 text-sm text-[var(--text-primary)]"
          ></textarea>
        </label>

        <label class="block text-sm">
          <span class="text-[var(--text-muted)]">{{ t('builderPage.sprintPlanner.status') }}</span>
          <select
            v-model="form.status"
            class="mt-1 w-full rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)] px-3 py-2 text-sm text-[var(--text-primary)]"
          >
            <option value="PLANNED">{{ t('builderPage.sprintPlanner.statusPlanned') }}</option>
            <option value="ACTIVE">{{ t('builderPage.sprintPlanner.statusActive') }}</option>
            <option value="COMPLETED" :disabled="form.status !== 'COMPLETED'">
              {{ t('builderPage.sprintPlanner.statusCompleted') }}
            </option>
          </select>
        </label>
      </div>

      <div class="flex justify-end gap-2">
        <button
          type="button"
          class="rounded-lg border border-[var(--border-subtle)] px-3 py-2 text-sm text-[var(--text-primary)]"
          @click="closeForm"
        >
          {{ t('builderPage.sprintPlanner.cancel') }}
        </button>
        <button
          type="submit"
          :disabled="store.isSaving || !form.name.trim() || !form.applicationId"
          class="rounded-lg bg-[var(--teal-action)] px-4 py-2 text-sm text-white hover:bg-[var(--teal-90)] disabled:opacity-50"
        >
          {{ store.isSaving ? t('builderPage.sprintPlanner.saving') : editingId ? t('builderPage.sprintPlanner.saveChanges') : t('builderPage.sprintPlanner.createSprint') }}
        </button>
      </div>
    </form>

    <!-- ============================ LISTA DE SPRINTS ============================ -->
    <div v-if="store.isLoading && !store.sprints.length" class="py-8 text-center text-sm text-[var(--text-muted)]">
      {{ t('builderPage.sprintPlanner.loading') }}
    </div>

    <div v-else-if="!filteredSprints.length" class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-8 text-center text-sm text-[var(--text-muted)]">
      {{ t('builderPage.sprintPlanner.emptyState') }}
    </div>

    <div v-else class="grid gap-3 md:grid-cols-2">
      <article
        v-for="sprint in filteredSprints"
        :key="sprint.id"
        class="cursor-pointer rounded-2xl border bg-[var(--bg-card)] p-4 transition-colors"
        :class="selectedId === sprint.id
          ? 'border-[var(--teal)]'
          : 'border-[var(--border-subtle)] hover:border-[var(--teal)]/60'"
        @click="selectSprint(sprint)"
      >
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0">
            <h3 class="truncate font-semibold text-[var(--text-primary)]">{{ sprint.name }}</h3>
            <p class="mt-0.5 text-xs text-[var(--text-muted)]">
              {{ sprint.applicationName || projectName(sprint.applicationId) }} ·
              {{ formatDate(sprint.startDate) }} → {{ formatDate(sprint.endDate) }}
            </p>
          </div>
          <span :class="['rounded-full px-2 py-0.5 text-[10px] font-semibold whitespace-nowrap', statusClasses(sprint.status)]">
            {{ statusLabel(sprint.status) }}
          </span>
        </div>

        <p v-if="sprint.goal" class="mt-2 line-clamp-2 text-xs text-[var(--text-muted)]">
          🎯 {{ sprint.goal }}
        </p>

        <div class="mt-3">
          <div class="flex items-center justify-between text-[11px] text-[var(--text-muted)]">
            <span>{{ t('builderPage.sprintPlanner.progress') }}</span>
            <span class="font-semibold text-[var(--text-primary)]">{{ Math.round(sprint.progress) }}%</span>
          </div>
          <div class="mt-1 h-2 w-full overflow-hidden rounded-full bg-[var(--bg-app)]">
            <div class="h-full rounded-full bg-[var(--teal)]" :style="{ width: `${Math.min(100, sprint.progress)}%` }"></div>
          </div>
        </div>

        <div class="mt-3 flex flex-wrap gap-1.5 text-[11px]">
          <span class="rounded-full bg-[var(--bg-app)] px-2 py-0.5 text-[var(--text-muted)]">{{ sprint.pendingTickets }} {{ t('builderPage.sprintPlanner.pending') }}</span>
          <span class="rounded-full bg-emerald-500/15 px-2 py-0.5 text-emerald-400">{{ sprint.completedTickets }} {{ t('builderPage.sprintPlanner.completed') }}</span>
          <span class="rounded-full bg-amber-500/15 px-2 py-0.5 text-amber-400">{{ sprint.blockedTickets }} {{ t('builderPage.sprintPlanner.blocked') }}</span>
          <span class="rounded-full bg-[var(--teal)]/15 px-2 py-0.5 font-semibold text-[var(--teal)]">{{ t('builderPage.sprintPlanner.velocity') }} {{ sprint.velocity }}</span>
        </div>

        <div v-if="sprint.sla" class="mt-3 flex flex-wrap items-center gap-2 text-[11px] text-[var(--text-muted)]">
          <span>{{ t('builderPage.sprintPlanner.sla') }}:</span>
          <span class="text-[var(--text-primary)]">{{ t('builderPage.sprintPlanner.compliance', { value: Math.round(sprint.sla.complianceRate) }) }}</span>
          <span v-if="sprint.sla.breached" class="text-red-400">{{ sprint.sla.breached }} {{ t('builderPage.sprintPlanner.breached') }}</span>
          <span v-if="sprint.sla.atRisk" class="text-amber-400">{{ sprint.sla.atRisk }} {{ t('builderPage.sprintPlanner.nearDeadline') }}</span>
        </div>

        <div class="mt-3 flex flex-wrap items-center gap-3 text-[11px] text-[var(--text-muted)]">
          <span>{{ sprint.totalTickets }} tickets · {{ sprint.storyPointsTotal }} {{ t('builderPage.sprintPlanner.points') }}</span>
          <span :class="sprint.isOverdue ? 'font-semibold text-red-400' : ''">
            {{ sprint.status === 'COMPLETED' ? t('builderPage.sprintPlanner.closed') : daysRemainingLabel(sprint.daysRemaining) }}
          </span>
        </div>
      </article>
    </div>

    <section v-if="velocityHistory.length" class="space-y-3 border-y border-[var(--border-subtle)] py-4">
      <div class="flex flex-wrap items-baseline justify-between gap-2">
        <h3 class="text-sm font-semibold text-[var(--text-primary)]">{{ t('builderPage.sprintPlanner.velocityHistory') }}</h3>
        <p class="text-xs text-[var(--text-muted)]">
          {{ t('builderPage.sprintPlanner.average') }}: <span class="font-semibold text-[var(--teal)]">{{ historyAverage }} {{ t('builderPage.sprintPlanner.points') }}</span>
        </p>
      </div>
      <div class="space-y-2">
        <div
          v-for="sprint in velocityHistory"
          :key="sprint.id"
          class="grid grid-cols-[minmax(5rem,1fr)_minmax(5rem,2fr)_auto] items-center gap-3 text-xs"
        >
          <span class="truncate text-[var(--text-primary)]">{{ sprint.name }}</span>
          <div class="h-2 overflow-hidden rounded-full bg-[var(--bg-app)]">
            <div
              class="h-full rounded-full bg-[var(--teal)]"
              :style="{ width: `${historyMax ? (sprint.velocity / historyMax) * 100 : 0}%` }"
            ></div>
          </div>
          <span class="whitespace-nowrap text-[var(--text-muted)]">
            {{ sprint.velocity }} {{ t('builderPage.sprintPlanner.points') }} · {{ sprint.storyPointsCompleted }} {{ t('builderPage.sprintPlanner.completed') }}
          </span>
        </div>
      </div>
    </section>

    <!-- ============================ DETALLE DEL SPRINT ============================ -->
    <div v-if="selected" class="space-y-4 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-4">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 class="text-lg font-bold text-[var(--text-primary)]">{{ selected.name }}</h3>
          <p class="text-xs text-[var(--text-muted)]">
            {{ selected.applicationName || projectName(selected.applicationId) }} ·
            {{ formatDate(selected.startDate) }} → {{ formatDate(selected.endDate) }}
            ({{ t('builderPage.sprintPlanner.durationDays', { count: selected.durationDays }) }})
          </p>
        </div>

        <div v-if="canManage" class="flex flex-wrap gap-2">
          <button
            type="button"
            class="rounded-lg border border-[var(--border-subtle)] px-3 py-1.5 text-sm text-[var(--text-primary)]"
            @click="openEditForm(selected)"
          >
            {{ t('common.edit') }}
          </button>
          <button
            type="button"
            :disabled="selected.status === 'COMPLETED' || store.isSaving"
            class="rounded-lg border border-[var(--teal)]/60 px-3 py-1.5 text-sm text-[var(--teal)] disabled:opacity-40"
            @click="finishSprint(selected)"
          >
            {{ t('builderPage.sprintPlanner.closeAndCalculateVelocity') }}
          </button>
          <button
            type="button"
            class="rounded-lg border border-red-500/40 px-3 py-1.5 text-sm text-red-400"
            @click="removeSprint(selected)"
          >
            {{ t('builderPage.sprintPlanner.delete') }}
          </button>
        </div>
      </div>

      <!-- Métricas agregadas -->
      <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <div class="rounded-xl bg-[var(--bg-app)] p-3">
          <p class="text-[11px] uppercase tracking-wide text-[var(--text-muted)]">{{ t('builderPage.sprintPlanner.pending') }}</p>
          <p class="text-xl font-bold text-[var(--text-primary)]">{{ selected.pendingTickets }}</p>
        </div>
        <div class="rounded-xl bg-[var(--bg-app)] p-3">
          <p class="text-[11px] uppercase tracking-wide text-[var(--text-muted)]">{{ t('builderPage.sprintPlanner.completed') }}</p>
          <p class="text-xl font-bold text-emerald-400">{{ selected.completedTickets }}</p>
        </div>
        <div class="rounded-xl bg-[var(--bg-app)] p-3">
          <p class="text-[11px] uppercase tracking-wide text-[var(--text-muted)]">{{ t('builderPage.sprintPlanner.blocked') }}</p>
          <p class="text-xl font-bold text-amber-400">{{ selected.blockedTickets }}</p>
        </div>
        <div class="rounded-xl bg-[var(--bg-app)] p-3">
          <p class="text-[11px] uppercase tracking-wide text-[var(--text-muted)]">{{ t('builderPage.sprintPlanner.velocity') }}</p>
          <p class="text-xl font-bold text-[var(--teal)]">
            {{ selected.velocity }}
            <span class="text-xs font-normal text-[var(--text-muted)]">{{ t('builderPage.sprintPlanner.points') }}</span>
          </p>
        </div>
      </div>

      <!-- SLA agregado del Sprint -->
      <div class="rounded-xl border border-[var(--border-subtle)] p-3">
        <p class="text-sm font-semibold text-[var(--text-primary)]">{{ t('builderPage.sprintPlanner.slaTitle') || 'Sprint SLA' }}</p>
        <p class="text-xs text-[var(--text-muted)]">
          {{ t('builderPage.sprintPlanner.slaDescription') || 'The SLA is defined per ticket (priority/severity + admin settings); this area displays the aggregated results.' }}
        </p>
        <div class="mt-2 flex flex-wrap gap-2 text-[11px]">
          <span class="rounded-full bg-[var(--bg-app)] px-2 py-0.5 text-[var(--text-muted)]">{{ t('builderPage.sprintPlanner.total') }}: {{ selected.sla.total }}</span>
          <span class="rounded-full bg-slate-500/15 px-2 py-0.5 text-slate-400">{{ t('builderPage.sprintPlanner.onTrack') }}: {{ selected.sla.onTrack }}</span>
          <span class="rounded-full bg-amber-500/15 px-2 py-0.5 text-amber-400">{{ t('builderPage.sprintPlanner.nearDeadline') }}: {{ selected.sla.atRisk }}</span>
          <span class="rounded-full bg-red-500/15 px-2 py-0.5 text-red-400">{{ t('builderPage.sprintPlanner.breached') }}: {{ selected.sla.breached }}</span>
          <span class="rounded-full bg-emerald-500/15 px-2 py-0.5 text-emerald-400">{{ t('builderPage.sprintPlanner.met') }}: {{ selected.sla.met }}</span>
          <span class="rounded-full bg-[var(--teal)]/15 px-2 py-0.5 font-semibold text-[var(--teal)]">
            {{ t('builderPage.sprintPlanner.compliance', { value: selected.sla.complianceRate }) }}
          </span>
        </div>
      </div>

      <!-- ================= TABLERO POR ESTADO (Kanban existente) ================= -->
      <div>
        <p class="mb-2 text-sm font-semibold text-[var(--text-primary)]">{{ t('builderPage.sprintPlanner.board') }}</p>
        <div class="flex gap-3 overflow-x-auto pb-2">
          <div
            v-for="column in selected.board ?? []"
            :key="column.status"
            class="min-w-[240px] flex-1 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-app)]/60 p-2"
          >
            <div class="mb-2 flex items-center justify-between">
              <span class="text-xs font-semibold text-[var(--text-primary)]">{{ column.label }}</span>
              <span class="rounded-full bg-[var(--bg-card)] px-2 py-0.5 text-[10px] text-[var(--text-muted)]">
                {{ column.tickets.length }}
              </span>
            </div>

            <div v-if="!column.tickets.length" class="rounded-lg border border-dashed border-[var(--border-subtle)] px-2 py-3 text-center text-[11px] text-[var(--text-muted)]">
              {{ t('builderPage.sprintPlanner.noTicketsInColumn') }}
            </div>

            <div class="space-y-2">
              <TicketCard
                v-for="ticket in column.tickets"
                :key="ticket.id"
                :ticket="toCardTicket(ticket)"
                @select="onCardSelect"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- ================= TICKETS DEL SPRINT (esfuerzo) ================= -->
      <div class="grid gap-4 lg:grid-cols-2">
        <div class="rounded-xl border border-[var(--border-subtle)] p-3">
          <p class="text-sm font-semibold text-[var(--text-primary)]">
            {{ t('builderPage.sprintPlanner.ticketsInSprint', { count: selected.tickets?.length ?? 0 }) }}
          </p>
          <p class="text-xs text-[var(--text-muted)]">
            {{ t('builderPage.sprintPlanner.storyPointsInfo') }}
          </p>

          <div v-if="!(selected.tickets ?? []).length" class="mt-3 rounded-lg border border-dashed border-[var(--border-subtle)] px-3 py-4 text-center text-xs text-[var(--text-muted)]">
            {{ t('builderPage.sprintPlanner.noTicketsInSprint') }}
          </div>

          <ul v-else class="mt-3 space-y-2">
            <li
              v-for="ticket in selected.tickets"
              :key="ticket.id"
              class="rounded-lg border bg-[var(--bg-app)]/60 p-2"
              :class="focusedTicketId === ticket.id ? 'border-[var(--teal)]' : 'border-[var(--border-subtle)]'"
            >
              <div class="flex items-start justify-between gap-2">
                <div class="min-w-0">
                  <p class="truncate text-sm text-[var(--text-primary)]">{{ ticket.title }}</p>
                  <p class="mt-0.5 text-[11px] text-[var(--text-muted)]">
                    {{ t('builderPage.sprintPlanner.epic') }}: {{ ticket.epicTitle || epicTitleFor(ticket.epicId) }} · {{ t('builderPage.sprintPlanner.state') }}: {{ ticket.status }}
                  </p>
                </div>
                <SlaBadge :status="store.slaForTicket(ticket.id)" />
              </div>

              <div class="mt-2 flex flex-wrap items-center gap-2">
                <label class="flex items-center gap-1 text-[11px] text-[var(--text-muted)]">
                  {{ t('builderPage.sprintPlanner.points') }}
                  <input
                    :value="ticket.storyPoints ?? 0"
                    type="number"
                    min="0"
                    max="1000"
                    class="w-20 rounded border border-[var(--border-subtle)] bg-[var(--bg-card)] px-2 py-1 text-xs text-[var(--text-primary)]"
                    @change="onStoryPointsChange(ticket, $event)"
                  />
                </label>

                <button
                  v-if="canManage"
                  type="button"
                  class="rounded border border-red-500/40 px-2 py-1 text-[11px] text-red-400"
                  @click="detachTicket(ticket)"
                >
                  {{ t('builderPage.sprintPlanner.removeFromSprint') }}
                </button>
              </div>
            </li>
          </ul>
        </div>

        <!-- ================= ASOCIAR TICKETS EXISTENTES ================= -->
        <div class="rounded-xl border border-[var(--border-subtle)] p-3">
          <p class="text-sm font-semibold text-[var(--text-primary)]">{{ t('builderPage.sprintPlanner.associateExisting') }}</p>
          <p class="text-xs text-[var(--text-muted)]">
            {{ t('builderPage.sprintPlanner.associateDescription') }}
          </p>

          <input
            v-model="availableSearch"
            type="search"
            :placeholder="t('builderPage.sprintPlanner.searchTickets')"
            class="mt-3 w-full rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)] px-3 py-2 text-sm text-[var(--text-primary)]"
          />

          <div class="mt-3 max-h-72 space-y-1 overflow-y-auto">
            <label
              v-for="ticket in filteredAvailableTickets"
              :key="ticket.id"
              class="flex cursor-pointer items-start gap-2 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)]/60 p-2"
            >
              <input v-model="assignSelection" type="checkbox" :value="ticket.id" class="mt-1" />
              <span class="min-w-0 flex-1">
                <span class="block truncate text-sm text-[var(--text-primary)]">{{ ticket.title }}</span>
                <span class="block text-[11px] text-[var(--text-muted)]">
                  {{ ticket.epicTitle || epicTitleFor(ticket.epicId) }} · {{ ticket.status }}
                  <template v-if="ticket.sprintId"> · {{ t('builderPage.sprintPlanner.currentSprint') || 'Current sprint:' }} {{ ticket.sprintName || t('builderPage.sprintPlanner.noSprint') }}</template>
                </span>
              </span>
              <SlaBadge :status="store.slaForTicket(ticket.id)" compact />
            </label>

            <p v-if="!filteredAvailableTickets.length" class="rounded-lg border border-dashed border-[var(--border-subtle)] px-3 py-4 text-center text-xs text-[var(--text-muted)]">
              {{ t('builderPage.sprintPlanner.noTicketsAvailable') }}
            </p>
          </div>

          <div class="mt-3 flex items-center justify-between gap-2">
            <span class="text-[11px] text-[var(--text-muted)]">{{ t('builderPage.sprintPlanner.selected', { count: assignSelection.length }) }}</span>
            <button
              type="button"
              :disabled="!assignSelection.length || store.isSaving || !canManage"
              class="rounded-lg bg-[var(--teal-action)] px-3 py-1.5 text-sm text-white hover:bg-[var(--teal-90)] disabled:opacity-50"
              @click="attachTickets"
            >
              {{ t('builderPage.sprintPlanner.associateToSprint') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
/**
 * SprintPlannerPanel - planificación y seguimiento de Sprints + SLA.
 *
 * Se apoya en `useSprintsStore` para el CRUD de Sprints, la asociación de
 * tickets existentes y el estado de SLA por ticket (que se muestra con
 * `SlaBadge`). El tablero reutiliza `TicketCard`, el mismo componente del
 * Kanban del Builder.
 */
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSprintsStore } from '@/stores/sprints'
import SlaBadge from '@/components/shared/SlaBadge.vue'
import TicketCard from './TicketCard.vue'
import type { Epic, Ticket } from '@/types'
import type { Sprint, SprintStatus } from '@/types/sprint'

const props = defineProps<{
  /** Proyectos disponibles para crear/filtrar Sprints */
  applications: { id: string; name: string; isActive?: boolean }[]
  /** Épicas del proyecto seleccionado en el Builder (para resolver títulos) */
  epics: Epic[]
  /** Tickets ya cargados en el Builder, por épica */
  ticketsByEpic: Record<string, Ticket[]>
  /** ADMIN o GROUP_LEADER pueden crear/editar/eliminar Sprints */
  canManage: boolean
  /** Proyecto inicialmente seleccionado en el Builder */
  initialApplicationId?: string
}>()

const emit = defineEmits<{
  /** Solicita al Builder recargar los tickets de las épicas indicadas */
  refresh: [epicIds: string[]]
}>()

const { t } = useI18n()
const store = useSprintsStore()

const projectFilter = ref(props.initialApplicationId ?? '')
const selectedId = ref<string | null>(null)
const focusedTicketId = ref<string | null>(null)
const availableSearch = ref('')
const assignSelection = ref<string[]>([])
const showForm = ref(false)
const formSection = ref<HTMLElement | null>(null)
const editingId = ref<string | null>(null)
const formError = ref('')

const form = ref<{
  name: string
  applicationId: string
  startDate: string
  endDate: string
  goal: string
  status: SprintStatus
}>({
  name: '',
  applicationId: '',
  startDate: '',
  endDate: '',
  goal: '',
  status: 'PLANNED'
})

// ============================ COMPUTADAS ============================

/** Sprints visibles según el filtro de proyecto */
const filteredSprints = computed((): Sprint[] =>
  projectFilter.value
    ? store.sprints.filter((sprint) => sprint.applicationId === projectFilter.value)
    : store.sprints
)

/** Velocity de los Sprints cerrados, de más antiguo a más reciente */
const velocityHistory = computed((): Sprint[] =>
  filteredSprints.value
    .filter((sprint) => sprint.status === 'COMPLETED')
    .sort((first, second) => new Date(first.startDate).getTime() - new Date(second.startDate).getTime())
)

const historyAverage = computed((): string => {
  if (!velocityHistory.value.length) return '0'
  const average = velocityHistory.value.reduce((sum, sprint) => sum + sprint.velocity, 0) / velocityHistory.value.length
  return average.toFixed(1)
})

const historyMax = computed((): number =>
  Math.max(0, ...velocityHistory.value.map((sprint) => sprint.velocity))
)

/** Sprint en detalle (el store mantiene la versión fresca con tablero) */
const selected = computed((): Sprint | null => {
  // Sin selección explícita no hay detalle: NO se cae al último Sprint del
  // store. Antes, al cambiar de proyecto/filtro, `selectedId` se limpiaba pero
  // seguía apareciendo abajo el Sprint anterior (de otro proyecto), lo que
  // confundía. Con `selectedId` nulo el detalle desaparece.
  if (!selectedId.value) return null
  if (store.selectedSprint?.id === selectedId.value) return store.selectedSprint
  return store.sprints.find((sprint) => sprint.id === selectedId.value) ?? null
})

/** Épicas del proyecto del Sprint seleccionado */
const projectEpicIds = computed((): string[] => {
  const applicationId = selected.value?.applicationId ?? projectFilter.value
  return props.epics
    .filter((epic) => !applicationId || epic.applicationId === applicationId)
    .map((epic) => epic.id)
})

/** Tickets del proyecto que todavía no están en el Sprint seleccionado */
const availableTickets = computed((): Ticket[] => {
  if (!selected.value) return []
  const alreadyInSprint = new Set((selected.value.tickets ?? []).map((ticket) => ticket.id))
  return projectEpicIds.value
    .flatMap((epicId) => props.ticketsByEpic[epicId] ?? [])
    .filter((ticket) => !alreadyInSprint.has(ticket.id))
})

/** Tickets disponibles filtrados por la búsqueda */
const filteredAvailableTickets = computed((): Ticket[] => {
  const term = availableSearch.value.trim().toLowerCase()
  if (!term) return availableTickets.value
  return availableTickets.value.filter((ticket) => ticket.title.toLowerCase().includes(term))
})

// ============================ CARGA DE DATOS ============================

/** Carga Sprints y estados de SLA del filtro actual */
const loadData = async (): Promise<void> => {
  const filters = projectFilter.value ? { applicationId: projectFilter.value } : undefined
  await store.fetchSprints(filters)
  await store.fetchSlaStatuses({ ...(filters ?? {}), limit: 1000 })

  if (selectedId.value && !store.sprints.some((sprint) => sprint.id === selectedId.value)) {
    selectedId.value = null
  }
}

watch(projectFilter, () => {
  selectedId.value = null
  focusedTicketId.value = null
  assignSelection.value = []
  // Limpia también el detalle cacheado en el store: así no reaparece abajo el
  // Sprint que estaba seleccionado antes de cambiar de proyecto/filtro.
  if (store.selectedSprint) store.selectedSprint = null
  void loadData()
})

// El proyecto elegido en el Builder manda: al cambiarlo se sincroniza el filtro
// del panel (el watch de `projectFilter` limpia la selección y recarga). Antes
// solo se aplicaba si el filtro estaba vacío, así que al cambiar de proyecto en
// el selector seguía mostrándose el Sprint del proyecto anterior.
watch(
  () => props.initialApplicationId,
  (value) => {
    const next = value ?? ''
    if (next === projectFilter.value) return
    projectFilter.value = next
  }
)

onMounted(() => {
  void loadData()
})

// ============================ ACCIONES ============================

/** Selecciona un Sprint y carga su detalle (tickets + tablero + SLA) */
const selectSprint = async (sprint: Sprint): Promise<void> => {
  selectedId.value = sprint.id
  focusedTicketId.value = null
  assignSelection.value = []
  try {
    await store.fetchSprint(sprint.id)
  } catch {
    // El error queda en store.error y se muestra en el aviso superior
  }
}

/** Desplaza la vista hasta el formulario (crear/editar) para que sea visible */
const revealForm = async (): Promise<void> => {
  await nextTick()
  formSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

/** Abre el formulario vacío para crear un Sprint */
const openCreateForm = (): void => {
  editingId.value = null
  formError.value = ''
  // El proyecto por defecto es el del selector del panel (o el del Builder)
  const defaultAppId =
    projectFilter.value || props.initialApplicationId || props.applications[0]?.id || ''
  form.value = {
    name: '',
    applicationId: defaultAppId,
    startDate: toLocalInput(new Date().toISOString()),
    endDate: toLocalInput(new Date(Date.now() + 14 * 86400000).toISOString()),
    goal: '',
    status: 'PLANNED'
  }
  showForm.value = true
  void revealForm()
}

/** Abre el formulario con los datos de un Sprint existente */
const openEditForm = (sprint: Sprint): void => {
  editingId.value = sprint.id
  formError.value = ''
  form.value = {
    name: sprint.name,
    applicationId: sprint.applicationId,
    startDate: toLocalInput(sprint.startDate),
    endDate: toLocalInput(sprint.endDate),
    goal: sprint.goal ?? '',
    status: (sprint.status as SprintStatus) ?? 'PLANNED'
  }
  showForm.value = true
  void revealForm()
}

/** Cierra el formulario sin guardar */
const closeForm = (): void => {
  showForm.value = false
  editingId.value = null
  formError.value = ''
}

/** Crea o actualiza el Sprint con los datos del formulario */
const submitForm = async (): Promise<void> => {
  formError.value = ''
  if (!form.value.startDate || !form.value.endDate) {
    formError.value = t('builderPage.sprintPlanner.formMissingDates')
    return
  }
  if (new Date(form.value.endDate) <= new Date(form.value.startDate)) {
    formError.value = t('builderPage.sprintPlanner.formEndDateAfterStart')
    return
  }

  const payload = {
    name: form.value.name.trim(),
    applicationId: form.value.applicationId,
    startDate: toIso(form.value.startDate),
    endDate: toIso(form.value.endDate),
    goal: form.value.goal.trim() || null,
    status: form.value.status
  }

  try {
    if (editingId.value) {
      await store.updateSprint(editingId.value, payload)
    } else {
      const created = await store.createSprint(payload)
      selectedId.value = created.id
    }
    closeForm()
    await loadData()
    if (selectedId.value) await store.fetchSprint(selectedId.value)
  } catch {
    // store.error ya contiene el detalle
  }
}

/** Cierra el Sprint y calcula su Velocity */
const finishSprint = async (sprint: Sprint): Promise<void> => {
  if (!window.confirm(t('builderPage.sprintPlanner.confirmCloseSprint', { name: sprint.name }))) return
  try {
    await store.completeSprint(sprint.id)
    selectedId.value = sprint.id
    await store.fetchSprint(sprint.id)
  } catch {
    // store.error ya contiene el detalle
  }
}

/** Elimina el Sprint (los tickets se conservan) */
const removeSprint = async (sprint: Sprint): Promise<void> => {
  if (!window.confirm(t('builderPage.sprintPlanner.confirmDeleteSprint', { name: sprint.name }))) return
  try {
    await store.deleteSprint(sprint.id)
    if (selectedId.value === sprint.id) selectedId.value = null
    emit('refresh', projectEpicIds.value)
    await loadData()
  } catch {
    // store.error ya contiene el detalle
  }
}

/** Guarda los puntos de esfuerzo (story points) de un ticket del Sprint */
const onStoryPointsChange = async (ticket: Ticket, event: Event): Promise<void> => {
  if (!selected.value) return
  const target = event.target as HTMLInputElement
  const value = Number(target.value)
  if (Number.isNaN(value) || value < 0 || value === (ticket.storyPoints ?? 0)) return
  try {
    await store.setStoryPoints(selected.value.id, ticket.id, value)
  } catch {
    target.value = String(ticket.storyPoints ?? 0)
  }
}

/** Asocia los tickets seleccionados al Sprint (sin cambiar su Épica) */
const attachTickets = async (): Promise<void> => {
  if (!selected.value || !assignSelection.value.length) return
  try {
    await store.assignTickets(selected.value.id, [...assignSelection.value])
    assignSelection.value = []
    emit('refresh', projectEpicIds.value)
  } catch {
    // store.error ya contiene el detalle
  }
}

/** Quita un ticket del Sprint (el ticket y su Épica no se modifican) */
const detachTicket = async (ticket: Ticket): Promise<void> => {
  if (!selected.value) return
  try {
    await store.removeTicket(selected.value.id, ticket.id)
    emit('refresh', projectEpicIds.value)
  } catch {
    // store.error ya contiene el detalle
  }
}

/** Resalta el ticket seleccionado en el tablero */
const focusTicket = (ticket: Ticket): void => {
  focusedTicketId.value = ticket.id
}

/** Adapta un Ticket del dominio al contrato de props de TicketCard */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const toCardTicket = (ticket: Ticket): any => ticket

/** Handler del evento select de TicketCard */
const onCardSelect = (ticket: unknown): void => focusTicket(ticket as Ticket)

// ============================ HELPERS DE PRESENTACIÓN ============================

/** Nombre del proyecto por id */
const projectName = (applicationId: string): string =>
  props.applications.find((app) => app.id === applicationId)?.name ?? 'Proyecto'

/** Título de una épica por id */
const epicTitleFor = (epicId: string): string =>
  props.epics.find((epic) => epic.id === epicId)?.title ?? '—'

/** Fecha corta (dd/mm/aaaa) */
const formatDate = (value?: string): string => {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  return `${day}/${month}/${date.getFullYear()}`
}

/** Etiqueta del estado del Sprint */
const statusLabel = (status: string): string => {
  const map: Record<string, string> = {
    PLANNED: t('builderPage.sprintPlanner.statusPlanned'),
    ACTIVE: t('builderPage.sprintPlanner.statusActive'),
    COMPLETED: t('builderPage.sprintPlanner.statusCompleted')
  }
  return map[status] ?? status
}

/** Clases del badge de estado del Sprint */
const statusClasses = (status: string): string => {
  switch (status) {
    case 'ACTIVE':
      return 'bg-[var(--teal)]/15 text-[var(--teal)]'
    case 'COMPLETED':
      return 'bg-emerald-500/15 text-emerald-400'
    default:
      return 'bg-slate-500/15 text-slate-400'
  }
}

/** Texto de días restantes / excedidos */
const daysRemainingLabel = (days: number): string => {
  if (days > 1) return t('builderPage.sprintPlanner.daysRemaining', { count: days })
  if (days === 1) return t('builderPage.sprintPlanner.oneDayRemaining')
  if (days === 0) return t('builderPage.sprintPlanner.dueToday')
  return t('builderPage.sprintPlanner.daysOverdue', { count: Math.abs(days) })
}

/** Convierte un ISO a valor de <input type="datetime-local"> */
const toLocalInput = (iso: string): string => {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''
  const pad = (value: number): string => String(value).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

/** Convierte el valor de <input type="datetime-local"> a ISO (UTC) */
const toIso = (localValue: string): string => {
  const date = new Date(localValue)
  return Number.isNaN(date.getTime()) ? new Date().toISOString() : date.toISOString()
}
</script>

