<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: WorkbenchDashboard                                   -->
  <!-- ================================================================ -->
  <!-- Panel de "Mis Tickets" para el dashboard personal del dev.      -->
  <!-- Incluye: filtros, controles de tickets (Iniciar, Finalizar,     -->
  <!-- Subtareas, Detalle), barra de progreso de subtareas y asignación-->
  <!-- de equipo para Team Leaders.                                    -->
  <!-- ================================================================ -->

  <div class="flex flex-col h-full bg-[var(--bg-app)]">

    <div class="sticky top-0 z-10 border-b border-[var(--border-subtle)] bg-[var(--bg-card)]/90 backdrop-blur-sm px-6 py-4 space-y-3">
      <div class="flex items-center justify-between gap-3">
        <div class="flex items-center gap-2">
          <span class="text-[var(--teal)] text-lg">🔎</span>
          <span class="text-sm font-semibold text-[var(--text-primary)]">{{ t('workbenchDashboard.globalSearch') }}</span>
        </div>
        <button
          v-if="globalSearchQuery.trim()"
          @click="clearGlobalSearch"
          class="text-[11px] text-[var(--text-muted)] underline hover:text-[var(--teal)]"
        >
          {{ t('workbenchDashboard.clearFilters') }}
        </button>
      </div>

      <div class="flex items-center gap-2">
        <input
          v-model="globalSearchQuery"
          @input="runGlobalSearch"
          type="text"
          :placeholder="t('workbenchDashboard.searchPlaceholder')"
          class="w-full rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)] px-3 py-2 text-xs text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:border-[var(--teal)]"
        />
      </div>

      <div v-if="globalSearchLoading" class="text-[11px] text-[var(--text-muted)]">{{ t('workbenchDashboard.searching') }}</div>
      <div v-else-if="hasGlobalSearchResults" class="space-y-2 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-app)] p-2">
        <div v-for="(items, groupName) in globalSearchResults" :key="groupName">
          <div v-if="items.length" class="space-y-1.5">
            <p class="px-2 text-[10px] font-semibold uppercase tracking-[0.15em] text-[var(--text-muted)]">
              {{ globalSearchLabel(groupName) }}
            </p>
            <button
              v-for="item in items.slice(0, 5)"
              :key="`${groupName}-${item.id || item.title || item.name || item.email}`"
              type="button"
              @click="applyGlobalSearchResult(groupName, item)"
              class="w-full rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-card)] px-2.5 py-1.5 text-left text-xs text-[var(--text-primary)] hover:border-[var(--teal)] hover:bg-[var(--teal)]/5"
            >
              <span class="font-medium">{{ globalSearchDisplayValue(groupName, item) }}</span>
              <span v-if="globalSearchMeta(groupName, item)" class="ml-2 text-[var(--text-muted)]">{{ globalSearchMeta(groupName, item) }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================================== -->
    <!-- BARRA DE FILTROS                                               -->
    <!-- ============================================================== -->
    <div class="flex-shrink-0 border-b border-[var(--border-subtle)] bg-[var(--bg-card)]/80 px-6 py-4 space-y-3">

      <!-- Encabezado de la sección -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-[var(--teal)] text-lg">🎫</span>
          <span class="text-sm font-semibold text-[var(--text-primary)]">{{ t('workbenchDashboard.myTickets') }}</span>
          <span class="px-2 py-0.5 text-xs font-medium bg-[var(--bg-app)] text-[var(--text-muted)] rounded-full border border-[var(--border-subtle)]">
            {{ tickets.length }}
          </span>
        </div>

        <!-- Botón de actualizar -->
        <button
          @click="refresh"
          :disabled="isLoading"
          class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-[var(--text-muted)] bg-[var(--bg-app)] hover:bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span :class="['text-sm', isLoading ? 'animate-spin inline-block' : '']">↻</span>
          {{ t('workbenchDashboard.refresh') }}
        </button>
      </div>

      <!-- Búsqueda libre por título/descripción -->
      <div class="flex items-center gap-2">
        <span class="text-xs font-medium text-[var(--text-muted)] flex-shrink-0">{{ t('workbenchDashboard.search') }}</span>
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="t('workbenchDashboard.titleOrDescription')"
          class="w-full max-w-md rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)] px-3 py-1.5 text-xs text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:border-[var(--teal)]"
        />
      </div>

      <div id="workbench-ticket-filters" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-2">
        <label class="flex flex-col gap-1 text-[11px] text-[var(--text-muted)]">
          <span>{{ t('workbenchDashboard.assignee') }}</span>
          <select
            :value="assigneeFilterIds[0] ?? ''"
            @change="onAssigneeFilterChange($event)"
            class="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)] px-2.5 py-1.5 text-xs text-[var(--text-primary)] outline-none focus:border-[var(--teal)]"
          >
            <option value="">{{ t('workbenchDashboard.statuses.all') }}</option>
            <option v-for="user in availableUsers" :key="user.id" :value="user.id">
              {{ user.fullName || user.email }}
            </option>
          </select>
        </label>

        <label class="flex flex-col gap-1 text-[11px] text-[var(--text-muted)]">
          <span>{{ t('workbenchDashboard.sprint') }}</span>
          <select
            :value="sprintFilterId"
            @change="setSprintFilterId(($event.target as HTMLSelectElement).value)"
            class="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)] px-2.5 py-1.5 text-xs text-[var(--text-primary)] outline-none focus:border-[var(--teal)]"
          >
            <option value="">{{ t('workbenchDashboard.allSprints') }}</option>
            <option v-for="sprint in workbenchSprints" :key="sprint.id" :value="sprint.id">
              {{ sprint.name }}{{ sprint.appName ? ` · ${sprint.appName}` : '' }}
            </option>
          </select>
        </label>

        <label class="flex flex-col gap-1 text-[11px] text-[var(--text-muted)]">
          <span>{{ t('workbenchDashboard.sortBy') }}</span>
          <select
            :value="sortBy"
            @change="setSort(($event.target as HTMLSelectElement).value as any, sortOrder)"
            class="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)] px-2.5 py-1.5 text-xs text-[var(--text-primary)] outline-none focus:border-[var(--teal)]"
          >
            <option value="default">{{ t('workbenchDashboard.defaultSort') }}</option>
            <option value="priority">{{ t('workbenchDashboard.priority').replace(':', '') }}</option>
            <option value="title">{{ t('workbenchDashboard.alphabetical') }}</option>
            <option value="progress">{{ t('workbenchDashboard.progress') }}</option>
            <option value="status">{{ t('analyticsPage.status') }}</option>
            <option value="dueDate">{{ t('workbenchDashboard.dueDate') }}</option>
            <option value="createdAt">{{ t('workbenchDashboard.createdDate') }}</option>
          </select>
        </label>

        <label class="flex flex-col gap-1 text-[11px] text-[var(--text-muted)]">
          <span>{{ t('workbenchDashboard.direction') }}</span>
          <select
            :value="sortOrder"
            @change="setSort(sortBy, ($event.target as HTMLSelectElement).value as any)"
            class="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)] px-2.5 py-1.5 text-xs text-[var(--text-primary)] outline-none focus:border-[var(--teal)]"
          >
            <option value="desc">{{ t('workbenchDashboard.descending') }}</option>
            <option value="asc">{{ t('workbenchDashboard.ascending') }}</option>
          </select>
        </label>
      </div>

      <!-- Filtros de Estado -->
      <div class="flex items-center gap-2 flex-wrap">
        <span class="text-xs font-medium text-[var(--text-muted)] flex-shrink-0">{{ t('workbenchDashboard.statusLabel') }}</span>
        <button
          v-for="f in statusFilters"
          :key="f.value"
          @click="setStatusFilter(f.value)"
          :class="[
            'px-3 py-1 rounded-full text-xs font-medium transition-colors',
            statusFilter === f.value
              ? 'bg-[var(--teal-action)] text-white font-semibold'
              : 'bg-[var(--bg-app)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:border-[var(--teal)]',
          ]"
        >
          {{ f.label }}
        </button>
      </div>

      <!-- Filtros de Prioridad -->
      <div class="flex items-center gap-2 flex-wrap">
        <span class="text-xs font-medium text-[var(--text-muted)] flex-shrink-0">{{ t('workbenchDashboard.priority') }}</span>
        <button
          v-for="f in priorityFilters"
          :key="f.value"
          @click="setPriorityFilter(f.value)"
          :class="[
            'px-3 py-1 rounded-full text-xs font-medium transition-colors',
            priorityFilter === f.value
              ? 'bg-[var(--teal-action)] text-white font-semibold'
              : 'bg-[var(--bg-app)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:border-[var(--teal)]',
          ]"
        >
          {{ f.label }}
        </button>
      </div>

      <!-- Filtros de Fecha -->
      <div class="flex items-center gap-2 flex-wrap">
        <span class="text-xs font-medium text-[var(--text-muted)] flex-shrink-0">{{ t('workbenchDashboard.date') }}</span>
        <button
          v-for="f in dateFilters"
          :key="f.value"
          @click="setDateFilter(f.value)"
          :class="[
            'px-3 py-1 rounded-full text-xs font-medium transition-colors',
            dateFilter === f.value
              ? 'bg-[var(--teal-action)] text-white font-semibold'
              : 'bg-[var(--bg-app)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:border-[var(--teal)]',
          ]"
        >
          {{ f.label }}
        </button>
      </div>

      <!-- ============================================================ -->
      <!-- NEW-03: Filtro por etiquetas (una o varias)                  -->
      <!-- La fila se oculta si el cliente todavía no tiene etiquetas.  -->
      <!-- ============================================================ -->
      <div v-if="availableTags.length" class="flex items-center gap-2 flex-wrap">
        <span class="text-xs font-medium text-[var(--text-muted)] flex-shrink-0">{{ t('workbenchDashboard.tags') }}</span>
        <button
          v-for="tag in availableTags"
          :key="tag.id"
          :data-tag="tag.name"
          @click="toggleTagFilter(tag.id)"
          :class="[
            'px-3 py-1 rounded-full text-xs font-medium transition-colors',
            tagFilterIds.includes(tag.id)
              ? 'bg-[var(--teal-action)] text-white font-semibold'
              : 'bg-[var(--bg-app)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:border-[var(--teal)]',
          ]"
        >
          🏷 {{ tag.name }}
        </button>
        <button
          v-if="tagFilterIds.length"
          @click="setTagFilterIds([])"
          class="text-xs text-[var(--text-muted)] underline hover:text-[var(--teal)]"
        >
          Quitar filtro
        </button>
      </div>
    </div>

    <!-- ============================================================== -->
    <!-- ÁREA DE CONTENIDO: Loading / Empty / Lista de tickets          -->
    <!-- ============================================================== -->
    <div class="flex-1 overflow-y-auto p-6">

      <!-- Estado: Error de carga -->
      <div
        v-if="error && !isLoading"
        class="flex flex-col items-center justify-center h-48 gap-3 text-slate-400"
      >
        <span class="text-5xl opacity-40">⚠️</span>
        <p class="text-sm font-medium text-red-300">{{ t('workbenchDashboard.loadError') }}</p>
        <p class="text-xs opacity-60 max-w-xs text-center">{{ error }}</p>
        <button
          @click="refresh"
          class="mt-1 px-4 py-1.5 text-xs font-medium text-[var(--teal)] border border-[var(--teal)]/40 rounded-lg hover:bg-[var(--teal)]/10 transition-colors"
        >
          {{ t('workbenchDashboard.retry') }}
        </button>
      </div>

      <!-- Estado: Cargando -->
      <div
        v-else-if="isLoading && tickets.length === 0"
        class="flex flex-col items-center justify-center h-48 gap-3 text-slate-400"
      >
        <span class="text-4xl animate-spin inline-block">↻</span>
        <p class="text-sm">{{ t('workbenchDashboard.loading') }}</p>
      </div>

      <!-- Estado: Sin resultados con filtros activos -->
      <div
        v-else-if="!error && tickets.length === 0 && hasActiveFilters"
        class="flex flex-col items-center justify-center h-48 gap-3 text-slate-400"
      >
        <span class="text-5xl opacity-40">🔍</span>
        <p class="text-sm font-medium">{{ t('workbenchDashboard.filteredEmpty') }}</p>
        <button
          @click="clearFilters"
          class="mt-1 px-4 py-1.5 text-xs font-medium text-[var(--teal)] border border-[var(--teal)]/40 rounded-lg hover:bg-[var(--teal)]/10 transition-colors"
        >
          {{ t('workbenchDashboard.clearFilters') }}
        </button>
      </div>

      <!-- Estado: Sin tickets asignados -->
      <div
        v-else-if="!error && tickets.length === 0"
        class="flex flex-col items-center justify-center h-48 gap-3 text-slate-400"
      >
        <span class="text-5xl opacity-40">📭</span>
        <p class="text-sm font-medium">{{ t('workbenchDashboard.assignedEmpty') }}</p>
        <p class="text-xs opacity-60">{{ t('workbenchDashboard.ticketsWillAppear') }}</p>
      </div>

      <!-- Lista de tarjetas de ticket con controles completos -->
      <div
        v-else-if="!error && tickets.length > 0"
        class="space-y-3"
      >
        <p v-if="actionError" class="px-4 py-2 text-xs text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg">
          {{ actionError }}
        </p>

        <div
          v-for="ticket in tickets"
          :key="ticket.id"
          :id="`workbench-ticket-${ticket.id}`"
          class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-4 space-y-3 hover:border-[var(--teal)]/40 transition-colors"
        >
          <!-- Breadcrumb App > Épica -->
          <div class="flex items-center gap-1 text-xs text-[var(--text-muted)] truncate">
            <span>📋</span>
            <span class="truncate max-w-[45%]">{{ ticket.appName || '—' }}</span>
            <span class="text-[var(--border-subtle)] flex-shrink-0">›</span>
            <span class="truncate">{{ ticket.epicTitle || '—' }}</span>
          </div>

          <!-- Título + estado + prioridad -->
          <div class="flex items-start justify-between gap-3">
            <h4 class="text-sm font-semibold text-[var(--text-primary)] leading-snug flex-1">
              {{ ticket.title }}
            </h4>
            <div class="flex items-center gap-1.5 flex-shrink-0">
              <span :class="statusClass(ticket.status)" class="px-2 py-0.5 text-xs font-medium rounded-full whitespace-nowrap">
                {{ statusLabel(ticket.status) }}
              </span>
              <span :class="priorityClass(ticket.priority)" class="px-2 py-0.5 text-xs font-medium rounded-full whitespace-nowrap">
                {{ priorityLabel(ticket.priority) }}
              </span>
            </div>
          </div>

          <!-- Asignado + Fecha -->
          <div class="flex items-center gap-3 text-xs text-[var(--text-muted)] flex-wrap">
            <span v-if="ticket.assignee" class="text-[var(--teal)] font-medium">
              👤 {{ ticket.assignee.fullName || ticket.assignee.email }}
            </span>
            <span v-else>👤 {{ t('workbenchDashboard.unassigned') }}</span>
            <span v-if="ticket.dueDate">📅 {{ ticket.dueDate.slice(0, 10) }}</span>
          </div>

          <!-- NEW-03: etiquetas asociadas al ticket -->
          <TagChips v-if="ticket.tags?.length" :tags="ticket.tags" size="xs" />

          <!-- Barra de progreso subtareas -->
          <div v-if="getSubtaskStats(ticket).total > 0" class="space-y-1">
            <div class="flex items-center justify-between text-[11px] text-[var(--text-muted)]">
              <span>Subtareas: {{ getSubtaskStats(ticket).completed }}/{{ getSubtaskStats(ticket).total }} completadas</span>
              <span class="font-medium text-[var(--teal)]">{{ getSubtaskStats(ticket).percentage }}%</span>
            </div>
            <div class="h-1.5 w-full rounded-full overflow-hidden bg-[var(--bg-app)] border border-[var(--border-subtle)]">
              <div
                class="h-full rounded-full bg-[var(--teal)] transition-all duration-300"
                :style="{ width: getSubtaskStats(ticket).percentage + '%' }"
              ></div>
            </div>
          </div>

          <!-- Botones de acción -->
          <div class="flex flex-wrap gap-2 pt-1 border-t border-[var(--border-subtle)]">
            <!-- Asignar (solo Team Leader / Admin) -->
            <select
              v-if="canAssignTickets"
              :value="ticket.assigneeId || ''"
              @change="handleAssigneeChange(ticket, $event)"
              :disabled="working"
              class="bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg px-2.5 py-1 text-xs text-[var(--text-primary)] outline-none focus:border-[var(--teal)] disabled:opacity-50"
            >
              <option value="">👤 {{ t('workbenchDashboard.assignTo') }}</option>
              <option v-for="u in assignableUsers" :key="u.id" :value="u.id">
                {{ u.fullName || u.email }}
              </option>
            </select>

            <button
              v-if="ticket.status === 'TODO'"
              :disabled="working"
              @click="startTicket(ticket)"
              class="px-3 py-1 rounded-lg text-xs bg-blue-600/20 text-blue-400 border border-blue-500/30 hover:bg-blue-600/30 disabled:opacity-50 font-medium"
            >
              ▶ Iniciar
            </button>

            <button
              v-if="ticket.status === 'IN_PROGRESS'"
              :disabled="working"
              @click="completeTicket(ticket)"
              class="px-3 py-1 rounded-lg text-xs bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-600/30 disabled:opacity-50 font-medium"
            >
              ✓ Finalizar
            </button>

            <button
              v-if="ticket.status === 'TODO' || ticket.status === 'IN_PROGRESS'"
              :title="ticket.status === 'TODO' ? t('actions.startToAsk') : t('actions.raiseQuestion')"
              :disabled="working || ticket.status !== 'IN_PROGRESS'"
              @click="openQuestionFor = openQuestionFor === ticket.id ? null : ticket.id"
              class="px-3 py-1 rounded-lg text-xs bg-amber-500/20 text-amber-300 border border-amber-500/30 hover:bg-amber-500/30 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {{ ticket.status === 'TODO' ? t('actions.startToAskShort') : t('actions.raiseQuestion') }}
            </button>

            <button
              v-if="ticket.status === 'REDIRECTED'"
              :disabled="working"
              @click="acceptRedirect(ticket)"
              class="px-3 py-1 rounded-lg text-xs bg-emerald-600/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-600/30 disabled:opacity-50 font-medium"
            >
              {{ t('actions.acceptTicket') }}
            </button>

            <button
              v-if="ticket.status === 'TODO' || ticket.status === 'IN_PROGRESS' || ticket.status === 'REDIRECTED'"
              :disabled="working"
              @click="openRedirectFor = openRedirectFor === ticket.id ? null : ticket.id"
              class="px-3 py-1 rounded-lg text-xs bg-sky-600/20 text-sky-300 border border-sky-500/30 hover:bg-sky-600/30 disabled:opacity-50 font-medium"
            >
              {{ t('actions.redirect') }}
            </button>

            <button
              @click="toggleSubtaskPanel(ticket.id)"
              class="px-3 py-1 rounded-lg text-xs bg-[var(--bg-app)] text-[var(--text-primary)] border border-[var(--border-subtle)] hover:border-[var(--teal)]"
            >
              ☑ {{ t('workbench.subtasks') }} ({{ (ticket.subtasks ?? []).length }})
            </button>

            <button
              @click="toggleDetail(ticket.id)"
              class="px-3 py-1 rounded-lg text-xs bg-[var(--bg-app)] text-[var(--text-primary)] border border-[var(--border-subtle)] hover:border-[var(--teal)]"
            >
              👁 {{ t('workbenchDashboard.detail') }}
            </button>
          </div>

          <div v-if="ticket.status === 'IN_PROGRESS' || ticket.status === 'BLOCKED'" class="flex gap-4 text-xs text-[var(--text-muted)]">
            <span>Trabajado: {{ formatDuration(liveSeconds(ticket, 'work')) }}</span>
            <span>Bloqueado: {{ formatDuration(liveSeconds(ticket, 'blocked')) }}</span>
          </div>

          <div v-if="openQuestionFor === ticket.id" class="rounded-lg border border-amber-500/30 bg-[var(--bg-app)] p-3 space-y-2">
            <label class="block text-xs font-medium text-[var(--text-secondary)]">{{ t('workbenchDashboard.questionTitle') }}</label>
            <textarea v-model="questionDraft" maxlength="500" rows="3" class="w-full resize-none rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-card)] px-3 py-2 text-xs outline-none focus:border-amber-400" :placeholder="t('workbenchDashboard.questionPlaceholder')"></textarea>
            <div class="flex justify-end gap-2">
              <button @click="openQuestionFor = null; questionDraft = ''" class="px-3 py-1 text-xs text-[var(--text-muted)]">{{ t('common.cancel') }}</button>
              <button :disabled="working || questionDraft.trim().length < 10" @click="raiseQuestion(ticket)" class="px-3 py-1 rounded-lg text-xs bg-amber-500 text-white disabled:opacity-50">{{ t('workbenchDashboard.blockTicket') }}</button>
            </div>
          </div>

          <div v-if="openRedirectFor === ticket.id" class="rounded-lg border border-sky-500/30 bg-[var(--bg-app)] p-3 space-y-2">
            <label class="block text-xs font-medium text-[var(--text-secondary)]">{{ t('workbenchDashboard.newAssignee') }}</label>
            <select v-model="redirectAssigneeId" class="w-full rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-card)] px-3 py-2 text-xs outline-none focus:border-sky-400">
              <option value="">{{ t('workbenchDashboard.selectUser') }}</option>
              <option v-for="user in redirectCandidates" :key="user.id" :value="user.id">{{ user.fullName || user.email }}</option>
            </select>
            <textarea v-model="redirectReason" maxlength="500" rows="2" class="w-full resize-none rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-card)] px-3 py-2 text-xs outline-none focus:border-sky-400" :placeholder="t('workbenchDashboard.requiredReason')"></textarea>
            <div class="flex justify-end gap-2">
              <button @click="openRedirectFor = null; redirectAssigneeId = ''; redirectReason = ''" class="px-3 py-1 text-xs text-[var(--text-muted)]">{{ t('common.cancel') }}</button>
              <button :disabled="working || !redirectAssigneeId || redirectReason.trim().length < 10" @click="redirectTicket(ticket)" class="px-3 py-1 rounded-lg text-xs bg-sky-600 text-white disabled:opacity-50">{{ t('workbenchDashboard.confirmRedirect') }}</button>
            </div>
          </div>

          <!-- Panel de Subtareas -->
          <div
            v-if="openSubtasksFor === ticket.id"
            class="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)] p-3 space-y-2"
          >
              <p v-if="!(ticket.subtasks ?? []).length" class="text-xs text-[var(--text-muted)]">
              {{ t('workbenchDashboard.noSubtasks') }}
            </p>
            <ul v-else class="space-y-1.5">
              <li v-for="sub in ticket.subtasks" :key="sub.id" class="flex items-center gap-2 text-xs">
                <input
                  type="checkbox"
                  :checked="sub.isCompleted"
                  :disabled="working"
                  @change="toggleSubtask(ticket, sub)"
                  class="accent-[var(--teal)] rounded cursor-pointer"
                />
                <span :class="sub.isCompleted ? 'line-through text-[var(--text-muted)]' : 'text-[var(--text-primary)]'">
                  {{ sub.title }}
                </span>
              </li>
            </ul>
            <div
              v-if="canManageSubtasks"
              class="flex gap-2 pt-1 border-t border-[var(--border-subtle)]"
            >
              <input
                v-model="newSubtaskTitle"
                @keyup.enter="addSubtask(ticket)"
                :placeholder="t('workbenchDashboard.newSubtask')"
                class="flex-1 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg px-2.5 py-1 text-xs outline-none focus:border-[var(--teal)]"
              />
              <button
                :disabled="working || !newSubtaskTitle.trim()"
                @click="addSubtask(ticket)"
                class="px-3 py-1 rounded-lg text-xs bg-[var(--teal)]/20 text-[var(--teal)] hover:bg-[var(--teal)]/30 disabled:opacity-50 font-medium"
              >
                {{ t('workbenchDashboard.add') }}
              </button>
            </div>
          </div>

          <!-- Panel de Detalle -->
          <div
            v-if="openDetailFor === ticket.id"
            class="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)] p-3 text-xs space-y-1.5"
          >
            <p><span class="text-[var(--text-muted)]">{{ t('workbenchDashboard.description') }}</span> {{ ticket.description || '—' }}</p>
            <p><span class="text-[var(--text-muted)]">{{ t('workbenchDashboard.epic') }}</span> {{ ticket.epicTitle || '—' }}</p>
            <p><span class="text-[var(--text-muted)]">{{ t('workbenchDashboard.assignedLabel') }}</span> {{ ticket.assignee ? (ticket.assignee.fullName || ticket.assignee.email) : t('workbenchDashboard.noAssignee') }}</p>
            <p v-if="ticket.prLink"><span class="text-[var(--text-muted)]">PR:</span>
              <a :href="ticket.prLink" target="_blank" rel="noopener" class="text-[var(--teal)] underline break-all ml-1">{{ ticket.prLink }}</a>
            </p>
            <p><span class="text-[var(--text-muted)]">{{ t('workbenchDashboard.dueDateLabel') }}</span> {{ ticket.dueDate ? ticket.dueDate.slice(0, 10) : '—' }}</p>

            <!-- ======================================================== -->
            <!-- NEW-03: selector para asociar / desasociar etiquetas     -->
            <!-- Se guarda la lista completa (PUT /tickets/{id}/tags)     -->
            <!-- ======================================================== -->
            <div class="pt-2 border-t border-[var(--border-subtle)] space-y-2">
              <div class="flex items-center justify-between gap-2 flex-wrap">
                <span class="text-[var(--text-muted)]">{{ t('workbenchDashboard.tags') }}</span>
                <TagChips :tags="ticket.tags ?? []" size="xs" show-empty empty-label="Sin etiquetas" />
              </div>
              <p v-if="!availableTags.length" class="italic text-[var(--text-muted)]">
                {{ t('workbenchDashboard.noTags') }}
              </p>
              <div v-else class="flex flex-wrap gap-x-3 gap-y-1">
                <label v-for="tag in availableTags" :key="tag.id" class="inline-flex items-center gap-1.5">
                  <input
                    type="checkbox"
                    :value="tag.id"
                    :checked="draftTagIds(ticket).includes(tag.id)"
                    :disabled="working"
                    class="accent-[var(--teal)]"
                    @change="toggleDraftTag(ticket, tag.id, $event)"
                  />
                  {{ tag.name }}
                </label>
              </div>
              <button
                v-if="availableTags.length"
                :disabled="working"
                @click="saveTicketTags(ticket)"
                class="px-3 py-1 rounded-lg text-xs font-medium bg-[var(--teal)]/20 text-[var(--teal)] hover:bg-[var(--teal)]/30 disabled:opacity-50"
              >
                {{ t('common.save') }}
              </button>
            </div>

            <!-- Documentos del ticket -->
            <div class="pt-2 border-t border-[var(--border-subtle)] space-y-2">
              <div class="flex items-center justify-between gap-3">
                <span class="text-xs font-semibold uppercase tracking-[0.15em] text-[var(--text-muted)]">
                  {{ t('workbenchPage.ticketDocuments') }}
                </span>
                <span class="rounded-full bg-[var(--bg-tag)] px-2 py-0.5 text-[10px] font-medium text-[var(--text-muted)]">
                  {{ t('workbenchPage.attachments') }}
                </span>
              </div>
              <FileUpload v-if="ticket.id && canUploadToTicket(ticket)" :ticket-id="ticket.id" />
              <div v-else class="rounded-lg border border-dashed border-[var(--border-subtle)] p-3 text-center text-xs text-[var(--text-muted)]">
                <p>{{ t('workbenchDashboard.noPermissionUpload') }}</p>
                <div class="mt-2">
                  <FileUpload :ticket-id="ticket.id" />
                </div>
              </div>
            </div>

            <!-- WEB-11: historial cronológico de eventos del ticket -->
            <div class="pt-2 border-t border-[var(--border-subtle)]">
              <p class="mb-2 text-xs font-semibold uppercase tracking-[0.15em] text-[var(--text-muted)]">
                {{ t('workbenchPage.history') }}
              </p>
              <TicketHistory
                :events="ticketEvents[ticket.id] ?? []"
                :loading="ticketEventsLoading === ticket.id"
                :error="ticketEventsError"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useWorkbenchTickets } from '@/composables/useWorkbenchTickets'
import { useAuthStore } from '@/stores/auth'
import { useTeamsStore } from '@/stores/teams'
import { api } from '@/services/api'
import apiClient from '@/services/api'
import TagChips from '@/components/shared/TagChips.vue'
import TicketHistory from '@/components/shared/TicketHistory.vue'
import FileUpload from '@/components/FileUpload.vue'
import type { Subtask, Tag, Ticket, TicketHistoryEvent, User } from '@/types'

const { t } = useI18n()

// =====================================================================
// COMPOSABLE: tickets del workbench + filtros
// =====================================================================

const {
  tickets,
  statusFilter,
  dateFilter,
  searchQuery,
  priorityFilter,
  assigneeFilterIds,
  sprintFilterId,
  sortBy,
  sortOrder,
  tagFilterIds,
  isLoading,
  error,
  setStatusFilter,
  setDateFilter,
  setSearchQuery,
  setPriorityFilter,
  setAssigneeFilterIds,
  setSprintFilterId,
  setSort,
  setTagFilterIds,
  updateTicketTags,
  refresh,
  rawTickets,
} = useWorkbenchTickets()

const workbenchSprints = computed(() => {
  const sprints = new Map<string, { id: string; name: string; appName?: string }>()
  for (const ticket of rawTickets.value) {
    if (!ticket.sprintId) continue
    sprints.set(ticket.sprintId, {
      id: ticket.sprintId,
      name: ticket.sprintName || 'Sprint',
      appName: ticket.appName,
    })
  }
  return [...sprints.values()].sort((a, b) => a.name.localeCompare(b.name))
})

// =====================================================================
// AUTH / PERMISOS
// =====================================================================

const authStore = useAuthStore()
const router = useRouter()
const emit = defineEmits<{ selectApplication: [applicationId: string] }>()
const teamsStore = useTeamsStore()
const userRole = computed(() => authStore.user?.role || localStorage.getItem('userRole') || 'DEVELOPER')
const isGroupLeader = computed(() => {
  const role = String(userRole.value || '').toUpperCase()
  return role === 'GROUP_LEADER' || role === 'TEAM_LEADER'
})
const isAdmin = computed(() => userRole.value === 'ADMIN')
const isDeveloper = computed(() => !isAdmin.value && !isGroupLeader.value)
const currentUserId = computed(() => authStore.user?.id || localStorage.getItem('userId') || '')
const canUploadToTicket = (ticket: Ticket) => !isDeveloper.value || ticket.assigneeId === currentUserId.value
const canAssignTickets = computed(() => isGroupLeader.value || isAdmin.value)

/**
 * Solo ADMIN/TEAM_LEADER crean subtareas (el backend responde 403 a un
 * DEVELOPER en `POST /api/subtasks/`).
 */
const canManageSubtasks = computed(() => authStore.isTeamLeader || isAdmin.value)

// =====================================================================
// ESTADO LOCAL
// =====================================================================

const openSubtasksFor = ref<string | null>(null)
const openDetailFor = ref<string | null>(null)
const newSubtaskTitle = ref('')
const working = ref(false)
const actionError = ref('')
const availableUsers = ref<User[]>([])
const redirectCandidates = ref<User[]>([])
const openQuestionFor = ref<string | null>(null)
const questionDraft = ref('')
const openRedirectFor = ref<string | null>(null)
const redirectAssigneeId = ref('')
const redirectReason = ref('')
const clockNow = ref(Date.now())
const clockInterval = window.setInterval(() => { clockNow.value = Date.now() }, 1000)

/**
 * NEW-03: etiquetas reutilizables del cliente. Las crea un ADMIN/TEAM_LEADER
 * en el Builder y aquí se usan para filtrar y para asociarlas a los tickets.
 */
const availableTags = ref<Tag[]>([])
const globalSearchQuery = ref('')
const globalSearchResults = ref<Record<string, any[]>>({})
const globalSearchLoading = ref(false)

const globalSearchLabel = (group: string): string => {
  const groups: Record<string, string> = {
    tickets: 'tickets', incidents: 'incidents', epics: 'epics', subtasks: 'subtasks',
    projects: 'projects', documents: 'documents', users: 'users',
  }
  return groups[group] ? t(`workbenchDashboard.groups.${groups[group]}`) : group
}

const globalSearchDisplayValue = (group: string, item: any): string => {
  if (group === 'users') return item.subtitle || item.email || item.title || t('workbenchDashboard.groups.user')
  return item.title || item.name || item.fullName || item.email || t('workbenchDashboard.groups.result')
}

const globalSearchMeta = (group: string, item: any): string => {
  if (group === 'users') return item.title || item.fullName || ''
  return item.subtitle || item.status || item.projectName || ''
}

const onAssigneeFilterChange = (event: Event) => {
  const value = (event.target as HTMLSelectElement).value
  setAssigneeFilterIds(value ? [value] : [])
}

const runGlobalSearch = async () => {
  const query = globalSearchQuery.value.trim()
  if (!query) {
    globalSearchResults.value = {}
    return
  }

  globalSearchLoading.value = true
  try {
    globalSearchResults.value = await api.tickets.globalSearch(query, 6)
  } catch (err) {
    console.error('Error en búsqueda global del workbench:', err)
    globalSearchResults.value = {}
  } finally {
    globalSearchLoading.value = false
  }
}

const clearGlobalSearch = () => {
  globalSearchQuery.value = ''
  globalSearchResults.value = {}
}

const hasGlobalSearchResults = computed(() => Object.values(globalSearchResults.value).some((items) => items.length > 0))

const applyGlobalSearchResult = async (group: string, item: any) => {
  if (group === 'documents' && item.ticketId) {
    const ticket = rawTickets.value.find((candidate) => candidate.id === item.ticketId)
    if (ticket) {
      clearFilters()
      setSearchQuery(ticket.title)
      await nextTick()
      if (openDetailFor.value !== ticket.id) toggleDetail(ticket.id)
      await nextTick()
      document.getElementById(`workbench-ticket-${ticket.id}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
    globalSearchResults.value = {}
    return
  }
  if ((group === 'projects' || group === 'applications') && item.id) {
    emit('selectApplication', item.id)
    globalSearchResults.value = {}
    return
  }
  if (group === 'users' && item.id) {
    setAssigneeFilterIds([item.id])
    document.getElementById('workbench-ticket-filters')?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    globalSearchResults.value = {}
    return
  }
  if (group === 'incidents' && item.id) {
    router.push({ name: 'MyIncidents', query: { search: item.title || '', incident: item.id } })
    globalSearchResults.value = {}
    return
  }
  const value = globalSearchDisplayValue(group, item)
  if (value) {
    setSearchQuery(value)
    searchQuery.value = value
  }
  globalSearchQuery.value = value
  globalSearchResults.value = {}
}

/**
 * NEW-03: borrador de etiquetas por ticket (id del ticket -> ids elegidos).
 *
 * Los checkboxes no guardan al instante: se editan aquí y se persisten con
 * `saveTicketTags()`, que envía la lista completa al backend.
 */
const tagDraft = ref<Record<string, string[]>>({})

/**
 * WEB-11: historial de eventos por ticket (se carga al abrir el detalle).
 * GET /api/tickets/{id}/events devuelve los eventos cronológicos con autor.
 */
const ticketEvents = ref<Record<string, TicketHistoryEvent[]>>({})

/** Ticket cuyo historial se está cargando (null = ninguno) */
const ticketEventsLoading = ref<string | null>(null)

/** Error al cargar el historial */
const ticketEventsError = ref('')

/**
 * Solo los miembros del equipo del líder pueden recibir el ticket; un ADMIN
 * asigna a cualquiera. `availableUsers` trae la lista completa de la API y el
 * filtro se hace aquí porque los equipos viven en el cliente (localStorage).
 */
const assignableUsers = computed(() =>
  teamsStore.filterUsersByTeams(
    availableUsers.value,
    authStore.user?.email || localStorage.getItem('userEmail'),
    isAdmin.value
  )
)

// =====================================================================
// HELPERS
// =====================================================================

const getSubtaskStats = (ticket: Ticket) => {
  const subs = ticket.subtasks ?? []
  const total = subs.length
  const completed = subs.filter((s) => s.isCompleted).length
  const percentage = total === 0 ? 0 : Math.round((completed / total) * 100)
  return { total, completed, percentage }
}

const liveSeconds = (ticket: Ticket, timer: 'work' | 'blocked'): number => {
  const total = timer === 'work' ? ticket.timeSpentSeconds : ticket.blockedTimeSeconds
  const startedAt = timer === 'work' ? ticket.timerStartedAt : ticket.blockedTimerStartedAt
  const activeStatus = timer === 'work' ? 'IN_PROGRESS' : 'BLOCKED'
  const elapsed = ticket.status === activeStatus && startedAt
    ? Math.max(0, Math.floor((clockNow.value - new Date(startedAt).getTime()) / 1000))
    : 0
  return (total || 0) + elapsed
}

const formatDuration = (seconds: number): string => {
  const total = Math.max(0, Math.floor(seconds))
  return [Math.floor(total / 3600), Math.floor((total % 3600) / 60), total % 60]
    .map((part) => String(part).padStart(2, '0')).join(':')
}

const hasActiveFilters = computed(
  () => statusFilter.value !== 'all' || dateFilter.value !== 'all' || priorityFilter.value !== 'all' || !!searchQuery.value.trim() || tagFilterIds.value.length > 0 || assigneeFilterIds.value.length > 0 || !!sprintFilterId.value,
)

const clearFilters = () => {
  setStatusFilter('all')
  setDateFilter('all')
  setSearchQuery('')
  setPriorityFilter('all')
  setTagFilterIds([])
  setAssigneeFilterIds([])
  setSprintFilterId('')
}

// =====================================================================
// FILTROS
// =====================================================================

const statusFilters = computed(() => [
  { value: 'all' as const, label: t('workbenchDashboard.statuses.all') },
  { value: 'in_progress' as const, label: t('workbenchDashboard.statuses.inProgress') },
  { value: 'todo' as const, label: t('workbenchDashboard.statuses.todo') },
  { value: 'blocked' as const, label: t('workbenchDashboard.statuses.blocked') },
  { value: 'completed' as const, label: t('workbenchDashboard.statuses.completed') },
])

const priorityFilters = computed(() => [
  { value: 'all' as const, label: t('workbenchDashboard.priorities.all') },
  { value: 'LOW' as const, label: t('workbenchDashboard.priorities.low') },
  { value: 'MEDIUM' as const, label: t('workbenchDashboard.priorities.medium') },
  { value: 'HIGH' as const, label: t('workbenchDashboard.priorities.high') },
  { value: 'URGENT' as const, label: t('workbenchDashboard.priorities.urgent') },
])

const dateFilters = computed(() => [
  { value: 'all' as const, label: t('workbenchDashboard.dates.all') },
  { value: 'overdue' as const, label: t('workbenchDashboard.dates.overdue') },
  { value: 'today' as const, label: t('workbenchDashboard.dates.today') },
  { value: 'week' as const, label: t('workbenchDashboard.dates.week') },
])

// =====================================================================
// ACCIONES DE TICKET
// =====================================================================

const startTicket = async (ticket: Ticket) => {
  working.value = true
  actionError.value = ''
  try {
    await api.tickets.updateStatus(ticket.id, 'IN_PROGRESS')
    await refresh()
  } catch (err: any) {
    console.error('Error iniciando ticket:', err?.response?.status, err?.response?.data || err)
    actionError.value = err?.response?.data?.detail || 'No se pudo iniciar el ticket.'
  } finally {
    working.value = false
  }
}

const completeTicket = async (ticket: Ticket) => {
  const prLink = window.prompt('Enlace del Pull Request para finalizar el ticket (opcional):')
  if (prLink === null) return
  working.value = true
  actionError.value = ''
  try {
    await api.tickets.complete(ticket.id, prLink.trim())
    await refresh()
  } catch (err: any) {
    actionError.value = err?.response?.data?.detail || 'No se pudo finalizar el ticket.'
  } finally {
    working.value = false
  }
}

const raiseQuestion = async (ticket: Ticket) => {
  working.value = true
  actionError.value = ''
  try {
    await api.tickets.question(ticket.id, questionDraft.value.trim())
    questionDraft.value = ''
    openQuestionFor.value = null
    await refresh()
    await loadTicketEvents(ticket.id)
  } catch (err: any) {
    console.error('Error levantando pregunta:', err?.response?.status, err?.response?.data || err)
    actionError.value = err?.response?.data?.detail || 'No se pudo bloquear el ticket.'
  } finally {
    working.value = false
  }
}

const redirectTicket = async (ticket: Ticket) => {
  if (!redirectAssigneeId.value || redirectReason.value.trim().length < 10) return
  working.value = true
  actionError.value = ''
  try {
    await api.tickets.redirect(ticket.id, { toUserId: redirectAssigneeId.value, reason: redirectReason.value.trim() })
    redirectAssigneeId.value = ''
    redirectReason.value = ''
    openRedirectFor.value = null
    await refresh()
    await loadTicketEvents(ticket.id)
  } catch (err: any) {
    console.error('Error redireccionando ticket:', err?.response?.status, err?.response?.data || err)
    actionError.value = err?.response?.data?.detail || 'No se pudo redireccionar el ticket.'
  } finally {
    working.value = false
  }
}

const acceptRedirect = async (ticket: Ticket) => {
  working.value = true
  actionError.value = ''
  try {
    await apiClient.post(`/tickets/${ticket.id}/accept-redirect`)
    await refresh()
    await loadTicketEvents(ticket.id)
  } catch (err: any) {
    console.error('Error aceptando ticket redirigido:', err?.response?.status, err?.response?.data || err)
    actionError.value = err?.response?.data?.detail || 'No se pudo aceptar el ticket.'
  } finally {
    working.value = false
  }
}

const toggleSubtaskPanel = (ticketId: string) => {
  openSubtasksFor.value = openSubtasksFor.value === ticketId ? null : ticketId
  openDetailFor.value = null
  newSubtaskTitle.value = ''
}

const toggleDetail = (ticketId: string) => {
  const isOpening = openDetailFor.value !== ticketId
  openDetailFor.value = isOpening ? ticketId : null
  openSubtasksFor.value = null
  // Al abrir/cerrar el detalle se descarta el borrador de etiquetas pendiente
  const next = { ...tagDraft.value }
  delete next[ticketId]
  tagDraft.value = next

  // WEB-11: el historial se recarga cada vez que se abre el detalle
  if (isOpening) loadTicketEvents(ticketId)
}

// =====================================================================
// WEB-11: HISTORIAL DE EVENTOS DEL TICKET
// =====================================================================

/** Carga el historial cronológico de eventos de un ticket */
const loadTicketEvents = async (ticketId: string): Promise<void> => {
  ticketEventsLoading.value = ticketId
  ticketEventsError.value = ''
  try {
    ticketEvents.value[ticketId] = await api.tickets.getEvents(ticketId)
  } catch (err: any) {
    console.error('Error cargando historial del ticket:', err)
    ticketEventsError.value = err?.response?.data?.detail || 'No se pudo cargar el historial.'
    ticketEvents.value[ticketId] = []
  } finally {
    ticketEventsLoading.value = null
  }
}

// =====================================================================
// NEW-03: ETIQUETAS (filtro + asociación a tickets)
// =====================================================================

/** Carga las etiquetas reutilizables (GET /api/tags/) */
const loadAvailableTags = async () => {
  try {
    availableTags.value = await api.tags.list()
  } catch (err) {
    console.error('Error cargando etiquetas:', err)
  }
}

/** Alterna una etiqueta del filtro (coincidencia: tiene ALGUNA de ellas) */
const toggleTagFilter = (tagId: string) => {
  setTagFilterIds(
    tagFilterIds.value.includes(tagId)
      ? tagFilterIds.value.filter((id) => id !== tagId)
      : [...tagFilterIds.value, tagId]
  )
}

/** IDs de etiquetas del ticket en edición (borrador o las ya guardadas) */
const draftTagIds = (ticket: Ticket): string[] =>
  tagDraft.value[ticket.id] ?? (ticket.tags ?? []).map((tag) => tag.id)

/** Marca/desmarca una etiqueta en el borrador del ticket */
const toggleDraftTag = (ticket: Ticket, tagId: string, event: Event) => {
  const checked = (event.target as HTMLInputElement).checked
  const current = draftTagIds(ticket)
  tagDraft.value = {
    ...tagDraft.value,
    [ticket.id]: checked ? [...current, tagId] : current.filter((id) => id !== tagId),
  }
}

/** Guarda las etiquetas del ticket (asocia y desasocia en una sola llamada) */
const saveTicketTags = async (ticket: Ticket) => {
  working.value = true
  actionError.value = ''
  try {
    await updateTicketTags(ticket.id, draftTagIds(ticket))
    const next = { ...tagDraft.value }
    delete next[ticket.id]
    tagDraft.value = next
    await refresh()
  } catch (err: any) {
    actionError.value =
      err?.response?.data?.detail || 'No se pudieron actualizar las etiquetas del ticket.'
  } finally {
    working.value = false
  }
}

const addSubtask = async (ticket: Ticket) => {
  const title = newSubtaskTitle.value.trim()
  if (!title) return
  working.value = true
  actionError.value = ''
  try {
    await api.tickets.createSubtask(ticket.id, title)
    newSubtaskTitle.value = ''
    await refresh()
  } catch (err: any) {
    actionError.value = err?.response?.data?.detail || 'No se pudo crear la subtarea.'
  } finally {
    working.value = false
  }
}

const toggleSubtask = async (ticket: Ticket, sub: Subtask) => {
  working.value = true
  actionError.value = ''
  try {
    await api.tickets.updateSubtask(ticket.id, sub.id, { isCompleted: !sub.isCompleted })
    await refresh()
  } catch (err: any) {
    actionError.value = err?.response?.data?.detail || 'No se pudo actualizar la subtarea.'
  } finally {
    working.value = false
  }
}

const handleAssigneeChange = async (ticket: Ticket, event: Event) => {
  const select = event.target as HTMLSelectElement
  const assigneeId = select.value || null
  working.value = true
  actionError.value = ''
  try {
    await api.tickets.update(ticket.id, { assigneeId } as unknown as Partial<Ticket>)
    await refresh()
  } catch (err: any) {
    actionError.value = err?.response?.data?.detail || 'No se pudo asignar el usuario al ticket.'
  } finally {
    working.value = false
  }
}

// =====================================================================
// CLASES CSS
// =====================================================================

const statusLabel = (status: string): string => {
  const statusKey = status === 'COMPLETED' ? 'DONE' : status
  return t(`analyticsPage.statuses.${statusKey}`)
}

const priorityLabel = (priority: string): string => t(`statuses.${priority.toLowerCase()}`)

const statusClass = (status: string): string =>
  ({
    TODO: 'bg-slate-500/20 text-slate-300',
    IN_PROGRESS: 'bg-blue-500/20 text-blue-300',
    BLOCKED: 'bg-red-500/20 text-red-300',
    REDIRECTED: 'bg-amber-500/20 text-amber-300',
    DONE: 'bg-emerald-500/20 text-emerald-300',
    COMPLETED: 'bg-emerald-500/20 text-emerald-300'
  })[status] ?? 'bg-slate-500/20 text-slate-300'

const priorityClass = (priority: string): string =>
  ({
    LOW: 'bg-slate-500/20 text-slate-300',
    MEDIUM: 'bg-yellow-500/20 text-yellow-300',
    HIGH: 'bg-orange-500/20 text-orange-300',
    URGENT: 'bg-red-500/20 text-red-300'
  })[priority] ?? 'bg-slate-500/20 text-slate-300'

// =====================================================================
// INIT
// =====================================================================

onMounted(async () => {
  // NEW-03: cualquier usuario autenticado puede listar las etiquetas
  loadAvailableTags()

  try {
    const { data } = await apiClient.get<Array<User & { full_name?: string }>>(
      '/tickets/redirect-candidates/list'
    )
    redirectCandidates.value = data
      .map((user) => ({ ...user, fullName: user.fullName ?? user.full_name ?? '' }))
      .filter((user) => user.id !== authStore.user?.id)
  } catch (e) {
    console.error('Error cargando responsables para redirección:', (e as any)?.response?.status, (e as any)?.response?.data || e)
  }

  if (canAssignTickets.value) {
    try {
      const res: any = await api.users.list({ limit: 100 })
      availableUsers.value = Array.isArray(res) ? res : (res?.items ?? res?.data ?? [])
    } catch (e) {
      console.error('Error cargando usuarios:', e)
    }
  }
})

onUnmounted(() => window.clearInterval(clockInterval))
</script>
