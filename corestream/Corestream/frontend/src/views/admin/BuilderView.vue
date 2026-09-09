<template>
  <div class="flex flex-col min-h-screen bg-[var(--bg-app)] text-[var(--text-primary)]">
    <!-- Global header -->
    <AppHeader />

    <!-- Page header with title and controls -->
    <div class="border-b border-[var(--border-subtle)] bg-[var(--bg-app)] backdrop-blur">
      <div class="mx-auto flex w-full flex-col gap-4 px-4 py-5 lg:px-8 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p class="text-[11px] uppercase tracking-[0.32em] text-[var(--teal-30)]/80">CoreStream Builder</p>
          <h1 class="mt-1 text-3xl font-semibold text-[var(--text-primary)]">{{ t('builderView.title') }}</h1>
          <p class="mt-1 max-w-3xl text-sm text-[var(--text-secondary)]">
            {{ t('builderView.description') }}
          </p>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <button
            type="button"
            class="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-4 py-2 text-sm font-medium text-[var(--text-primary)] transition hover:bg-[var(--bg-card)]/10"
            @click="toggleAllEpics"
          >
            {{ allEpicsCollapsed ? t('builderView.expandEpics') : t('builderView.collapseEpics') }}
          </button>
          <button
            type="button"
            class="flex items-center gap-1.5 rounded-lg border border-[var(--teal)]/30 bg-[var(--teal)] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[var(--teal-90)]"
            @click="openAppModal()"
          >
            <Plus :size="15" />
            {{ t('builderView.newApplication') }}
          </button>
          <button
            type="button"
            class="flex items-center gap-1.5 rounded-lg border border-[var(--status-done-bg)]/30 bg-[var(--status-done-bg)] px-4 py-2 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
            :disabled="!selectedApp"
            @click="openEpicModal()"
          >
            <Plus :size="15" />
            {{ t('builderView.newEpic') }}
          </button>
        </div>
      </div>
    </div>

    <div class="mx-auto grid w-full gap-0 lg:grid-cols-[16rem_1fr] xl:grid-cols-[20rem_1fr]">
      <aside class="border-r border-[var(--border-subtle)] bg-[var(--bg-panel)] p-4 lg:min-h-[calc(100vh-96px)]">
        <div class="mb-4 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-panel)] p-4">
          <div class="flex items-center justify-between gap-3">
            <div>
              <p class="text-xs uppercase tracking-[0.22em] text-[var(--text-muted)]">{{ t('builderView.applicationsCount') }}</p>
              <h2 class="text-lg font-semibold text-[var(--text-primary)]">{{ applications.length }} {{ t('builderView.registered') }}</h2>
            </div>
            <span class="flex items-center gap-1 rounded-full border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-3 py-1 text-xs text-[var(--text-secondary)]">
              <CheckCircle v-if="selectedApp" :size="11" class="text-[var(--teal)]" />
              {{ selectedApp ? t('builderView.activeStatus') : t('builderView.noSelection') }}
            </span>
          </div>
        </div>

        <div class="space-y-3">
          <button
            v-for="app in applications"
            :key="app.id"
            type="button"
            class="group w-full rounded-2xl border px-4 py-4 text-left transition duration-200"
            :class="selectedApp?.id === app.id
              ? 'border-teal-40/60 bg-teal/10 shadow-[0_0_0_1px_rgba(56,189,248,0.15)]'
              : 'border-[var(--border-subtle)] bg-[var(--bg-panel)] hover:border-[var(--teal)]/40 hover:bg-[var(--bg-card)]/10'"
            @click="selectApplication(app)"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="flex min-w-0 items-start gap-3">
                <div
                  class="mt-0.5 h-10 w-10 shrink-0 rounded-2xl border border-[var(--border-subtle)] flex items-center justify-center"
                  :style="{ backgroundColor: app.color || '#06B7B2' }"
                >
                  <AppIcon :icon="app.icon" :size="20" icon-class="text-white" />
                </div>
                <div class="min-w-0">
                  <h3 class="truncate text-sm font-semibold text-[var(--text-primary)]">{{ app.name }}</h3>
                  <p class="mt-1 line-clamp-2 text-xs text-[var(--text-muted)]">
                    {{ app.description || t('builderView.noDescription') }}
                  </p>
                </div>
              </div>

              <div class="flex shrink-0 flex-col items-end gap-2">
                <span class="flex items-center gap-1 rounded-full bg-[var(--bg-card)]/10 px-2 py-1 text-[11px] text-[var(--text-secondary)]">
                  <Layers :size="11" />
                  {{ app.epicCount }} {{ t('builderView.epicCount') }}
                </span>
                <div class="flex gap-1 opacity-0 transition group-hover:opacity-100">
                  <button
                    type="button"
                    class="rounded-md border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-2 py-1 text-[11px] text-[var(--text-secondary)] transition hover:bg-[var(--bg-card)]/10"
                    @click.stop="openAppModal(app)"
                  >
                    {{ t('builderView.edit') }}
                  </button>
                  <button
                    type="button"
                    class="rounded-md border border-[var(--priority-urg-bg)]/60 bg-[var(--priority-urg-bg)] px-2 py-1 text-[11px] text-white transition hover:bg-[var(--priority-urg-bg)]/80"
                    @click.stop="removeApp(app)"
                  >
                    {{ t('builderView.delete') }}
                  </button>
                </div>
              </div>
            </div>

            <div class="mt-4 h-1.5 overflow-hidden rounded-full bg-[var(--bg-card)]/10">
              <div
                class="h-full rounded-full transition-all"
                :style="{ width: `${appProgress(app)}%`, backgroundColor: app.color || '#06B7B2' }"
              />
            </div>
            <div class="mt-2 flex items-center justify-between text-[11px] text-[var(--text-muted)]">
              <span class="flex items-center gap-1">
                <Clock :size="11" />
                {{ app.pendingCount || 0 }} {{ t('builderView.pendingCount') }}
              </span>
              <span class="flex items-center gap-1" :class="(app.delayedCount || 0) > 0 ? 'text-orange-400' : ''">
                <AlertTriangle :size="11" />
                {{ app.delayedCount || 0 }} {{ t('builderView.delayedCount') }}
              </span>
            </div>
          </button>

          <div
            v-if="!applications.length"
            class="rounded-2xl border border-dashed border-[var(--border-subtle)] bg-[var(--bg-panel)] p-6 text-center text-sm text-[var(--text-muted)]"
          >
            {{ t('builderView.noApplications') }}
          </div>
        </div>
      </aside>

      <main class="min-h-[calc(100vh-96px)] overflow-y-auto p-6 lg:p-8">
        <div v-if="selectedApp" class="space-y-6">
          <section class="grid gap-4 md:grid-cols-4">
            <article class="rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-panel)] p-5 shadow-[0_18px_40px_rgba(15,23,42,0.35)]">
              <p class="text-xs uppercase tracking-[0.22em] text-[var(--text-muted)]">{{ t('builderView.applicationLabel') }}</p>
              <h2 class="mt-2 text-xl font-semibold text-[var(--text-primary)]">{{ selectedApp.name }}</h2>
              <p class="mt-2 text-sm text-[var(--text-secondary)]">{{ selectedApp.description || t('builderView.noDescription') }}</p>
            </article>
            <article class="rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-panel)] p-5">
              <p class="text-xs uppercase tracking-[0.22em] text-[var(--text-muted)]">{{ t('builderView.epicsLabel') }}</p>
              <h3 class="mt-2 text-3xl font-semibold text-[var(--text-primary)]">{{ epics.length }}</h3>
              <p class="mt-2 text-sm text-[var(--text-secondary)]">{{ t('builderView.swimmlanesConfigured') }}</p>
            </article>
            <article class="rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-panel)] p-5">
              <p class="text-xs uppercase tracking-[0.22em] text-[var(--text-muted)]">{{ t('builderView.progressLabel') }}</p>
              <h3 class="mt-2 text-3xl font-semibold text-[var(--text-primary)]">{{ overallProgress }}%</h3>
              <p class="mt-2 text-sm text-[var(--text-secondary)]">{{ t('builderView.progressDesc') }}</p>
            </article>
            <article class="rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-panel)] p-5">
              <p class="text-xs uppercase tracking-[0.22em] text-[var(--text-muted)]">{{ t('builderView.tonalityLabel') }}</p>
              <div class="mt-3 flex items-center gap-3">
                <span class="h-12 w-12 rounded-2xl border border-[var(--border-subtle)]" :style="{ backgroundColor: selectedApp.color || '#06B7B2' }" />
                <div>
                  <p class="text-sm text-[var(--text-secondary)]">{{ t('builderView.colorGuide') }}</p>
                  <p class="text-base font-medium text-[var(--text-primary)]">{{ selectedApp.color || '#06B7B2' }}</p>
                </div>
              </div>
            </article>
          </section>

          <section class="rounded-[1.75rem] border border-[var(--border-subtle)] bg-[var(--bg-card)] p-5 shadow-[0_25px_60px_rgba(2,6,23,0.35)]">
            <div class="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <h2 class="text-2xl font-semibold text-[var(--text-primary)]">{{ t('builderView.swimmlanesTitle') }}</h2>
                <p class="mt-1 text-sm text-[var(--text-muted)]">
                  {{ t('builderView.swimmlanesDesc') }}
                </p>
              </div>

              <div class="flex items-center gap-2">
                <button
                  type="button"
                  class="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-3 py-2 text-sm text-[var(--text-secondary)] transition hover:bg-[var(--bg-card)]/10"
                  @click="collapseAllEpics"
                >
                  {{ t('builderView.collapseAll') }}
                </button>
                <button
                  type="button"
                  class="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-3 py-2 text-sm text-[var(--text-secondary)] transition hover:bg-[var(--bg-card)]/10"
                  @click="expandAllEpics"
                >
                  {{ t('builderView.expandAll') }}
                </button>
              </div>
            </div>

            <div v-if="!epics.length" class="rounded-2xl border border-dashed border-[var(--border-subtle)] bg-[var(--bg-panel)] p-10 text-center text-[var(--text-muted)]">
              {{ t('builderView.noEpics') }}
            </div>

            <div v-else class="space-y-4">
              <!-- Drop zone before first epic -->
              <div
                v-if="isDragging && dragPosition === 'above' && dragOverEpicId === epics[0]?.id"
                class="h-1 bg-[var(--status-done-bg)] rounded-full mb-2"
              />

              <article
                v-for="(epic, index) in epics"
                :key="epic.id"
                @dragover="handleEpicArticleDragOver(epic, $event)"
                @dragleave="handleEpicDragLeave"
                @drop="handleEpicArticleDrop(epic, $event)"
                :class="[
                  'overflow-hidden rounded-[1.4rem] border',
                  isDragging ? 'transition-none' : 'transition-all duration-200',
                  getDraggedEpicClass(epic),
                  draggedEpicId === epic.id
                    ? 'opacity-50 bg-[var(--bg-panel)]/50'
                    : 'bg-[var(--bg-card)] border-[var(--border-subtle)] hover:shadow-lg',
                  dragOverEpicId === epic.id && isDragging
                    ? 'shadow-lg border-emerald-500/50'
                    : '',
                ]"
              >
                <!-- Indicador de drop (arriba) -->
                <div
                  v-if="dragOverEpicId === epic.id && dragPosition === 'above' && isDragging"
                  class="h-1 bg-[var(--status-done-bg)] rounded-full mb-2"
                />

                <div class="border-b border-[var(--border-subtle)] bg-[var(--bg-panel)] flex" :style="{ borderLeft: '4px solid ' + (selectedApp?.color || '#06B7B2') }">
                  <!-- Drag Handle Strip -->
                  <div
                    draggable="true"
                    @dragstart.stop="handleEpicDragStart(epic, $event)"
                    @dragend="handleEpicDragEnd"
                    class="w-6 flex-shrink-0 flex items-center justify-center cursor-grab active:cursor-grabbing hover:bg-[var(--border-subtle)]/60 transition-colors"
                    title="Arrastra para reordenar"
                  >
                    <GripVertical :size="14" class="text-[var(--text-muted)]" />
                  </div>

                  <!-- Epic Content -->
                  <div class="flex-1 px-5 py-4">
                  <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                    <div class="flex min-w-0 items-start gap-2">
                      <button
                        type="button"
                        class="mt-1 rounded-full border border-[var(--border-subtle)] bg-[var(--bg-panel)] p-2 text-[var(--text-primary)] transition hover:bg-[var(--bg-card)]/10"
                        @click="toggleEpicCollapse(epic.id)"
                      >
                        <svg
                          class="w-4 h-4 transition-transform duration-200"
                          :class="epicsStore.collapsedEpics.has(epic.id) ? 'rotate-0' : 'rotate-180'"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path d="M5.293 7.293a1 1 0 011.414 0l6.586 6.586a1 1 0 01.414 1.414l-6.586-6.586a1 1 0 01-1.414-1.414z"/>
                        </svg>
                      </button>

                      <div class="min-w-0">
                        <div class="flex flex-wrap items-center gap-2">
                          <h3 class="truncate text-lg font-semibold text-[var(--text-primary)]">{{ epic.title }}</h3>
                          <span class="rounded-full border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-2 py-1 text-[11px] uppercase tracking-[0.18em] text-[var(--text-secondary)]">
                            {{ epic.totalTickets }} {{ t('builderView.tickets') }}
                          </span>
                          <span class="rounded-full border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-2 py-1 text-[11px] text-[var(--text-secondary)]">
                            {{ epic.completedTickets }} {{ t('builderView.completed') }}
                          </span>
                        </div>
                        <p class="mt-1 max-w-3xl text-sm text-[var(--text-secondary)]">
                          {{ epic.description || t('builderView.epicNoDescription') }}
                        </p>
                      </div>
                    </div>

                    <div class="flex flex-wrap items-center gap-2">
                      <button
                        type="button"
                        class="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-3 py-2 text-sm text-[var(--text-secondary)] transition hover:bg-[var(--bg-card)]/10 disabled:opacity-40"
                        :disabled="Number(index) === 0"
                        @click="moveEpic(epic.id, Number(index) - 1)"
                      >
                        ↑
                      </button>
                      <button
                        type="button"
                        class="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-3 py-2 text-sm text-[var(--text-secondary)] transition hover:bg-[var(--bg-card)]/10 disabled:opacity-40"
                        :disabled="Number(index) === epics.length - 1"
                        @click="moveEpic(epic.id, Number(index) + 1)"
                      >
                        ↓
                      </button>
                      <button
                        type="button"
                        class="rounded-lg border border-[var(--teal)]/60 bg-[var(--teal)] px-3 py-2 text-sm text-white transition hover:bg-[var(--teal)]/80"
                        @click="openEpicModal(epic)"
                      >
                        {{ t('builderView.edit') }}
                      </button>
                      <button
                        type="button"
                        class="rounded-lg border border-[var(--priority-urg-bg)]/60 bg-[var(--priority-urg-bg)] px-3 py-2 text-sm text-white transition hover:bg-[var(--priority-urg-bg)]/80"
                        @click="removeEpic(epic)"
                      >
                        {{ t('builderView.delete') }}
                      </button>
                    </div>
                  </div>

                  <div class="mt-4 grid gap-4 md:grid-cols-[minmax(0,1fr)_18rem] md:items-center">
                    <div>
                      <div class="flex items-center justify-between text-xs text-[var(--text-muted)]">
                        <span>{{ t('builderView.progress') }}</span>
                        <span>{{ epic.progress }}%</span>
                      </div>
                      <div class="mt-2 h-2 overflow-hidden rounded-full bg-[var(--border-subtle)]">
                        <div class="h-full rounded-full bg-gradient-to-r from-[var(--teal)] to-[var(--status-done-bg)]" :style="{ width: `${epic.progress}%` }" />
                      </div>
                    </div>
                    <div class="flex items-center gap-2 justify-self-start md:justify-self-end">
                      <span class="rounded-full border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-3 py-1 text-xs text-[var(--text-secondary)]">
                        {{ t('builderView.dueDate') }} {{ formatDate(epic.dueDate) }}
                      </span>
                      <span
                        class="rounded-full px-3 py-1 text-xs font-medium"
                        :class="epicsStore.collapsedEpics.has(epic.id) ? 'bg-[var(--bg-panel)] text-[var(--text-secondary)]' : 'bg-[var(--status-done-bg)]/15 text-[var(--status-done-bg)]'"
                      >
                        {{ epicsStore.collapsedEpics.has(epic.id) ? t('builderView.collapsed') : t('builderView.opened') }}
                      </span>
                    </div>
                  </div>
                  </div>
                </div>

                <!-- Indicador de drop (abajo) -->
                <div
                  v-if="dragOverEpicId === epic.id && dragPosition === 'below' && isDragging"
                  class="h-1 bg-[var(--status-done-bg)] rounded-full mt-2"
                />

                <div v-show="!epicsStore.collapsedEpics.has(epic.id)" class="grid gap-4 p-5 lg:grid-cols-[1fr_18rem]">
                  <div class="space-y-3">
                    <div class="flex items-center justify-between">
                      <h4 class="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">{{ t('builderView.ticketsLabel') }}</h4>
                      <span class="text-xs text-[var(--text-muted)]">{{ epic.totalTickets }} {{ t('builderView.items') }}</span>
                    </div>

                    <div
                      v-if="(epic.tickets || []).length"
                      class="grid gap-3 md:grid-cols-2 xl:grid-cols-3"
                      @dragover.prevent
                      @drop.prevent.stop="handleTicketDropOnEpic(epic, $event)"
                    >
                      <article
                        v-for="ticket in epic.tickets || []"
                        :key="ticket.id"
                        draggable="true"
                        @dragstart="handleTicketDragStart(ticket, epic, $event)"
                        @click="abrirPanelTicket(ticket, epic)"
                        class="rounded-2xl border p-4 cursor-pointer transition-all shadow-sm hover:shadow-md"
                        :class="getCardClass(ticket.status)"
                      >
                        <div class="flex items-start justify-between gap-3">
                          <h5 class="line-clamp-2 text-sm font-medium text-[var(--text-primary)]">{{ ticket.title }}</h5>
                          <span class="rounded-full px-2 py-1 text-[11px] font-bold tracking-wider" :class="getBadgeClass(ticket.status)">
                            {{ getBadgeText(ticket.status) }}
                          </span>
                        </div>
                        <p v-if="ticket.description" class="mt-2 text-xs text-[var(--text-muted)] line-clamp-2">
                          {{ ticket.description }}
                        </p>
                      </article>
                    </div>

                    <div class="mt-4">
                      <div v-if="creatingTicketInEpic === epic.id" class="rounded-xl p-4 border-2 border-dashed border-[var(--teal)] bg-[var(--bg-panel)] transition-all">
                        <input
                          data-cy="inline-ticket-input"
                          v-model="newTicketTitle"
                          type="text"
                          @keydown.enter="guardarTicketInline(epic.id)"
                          @keydown.esc="creatingTicketInEpic = null; newTicketTitle = ''"
                          @blur="!newTicketTitle.trim() ? creatingTicketInEpic = null : null"
                          :placeholder="t('builderView.ticketTitlePlaceholder')"
                          class="w-full px-4 py-2 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-panel)] text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--teal)] focus:ring-1 focus:ring-[var(--teal)]"
                        />
                        <p class="text-xs mt-2 text-[var(--text-muted)]">
                          ↵ Enter para crear • Esc para cancelar
                        </p>
                      </div>
                      
                      <button
                        v-else
                        @click="creatingTicketInEpic = epic.id"
                        class="w-full border-2 border-dashed border-[var(--border-subtle)] rounded-xl p-4 transition-all flex items-center justify-center gap-2 hover:border-[var(--teal)] hover:bg-[var(--teal)]/5 text-[var(--text-muted)] hover:text-[var(--teal)]"
                      >
                        <span class="text-lg">+</span>
                        <span class="text-sm font-medium">{{ t('builderView.addTicket') }}</span>
                      </button>
                    </div>
                  </div>

                  <aside class="rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-app)] p-4">
                    <h4 class="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">{{ t('builderView.quickActions') }}</h4>
                    <div class="mt-4 space-y-3 text-sm text-[var(--text-secondary)]">
                      <div class="rounded-2xl bg-[var(--bg-panel)] px-4 py-3">
                        <p class="text-[var(--text-muted)]">Aplicación</p>
                        <p class="font-medium text-[var(--text-primary)]">{{ selectedApp.name }}</p>
                      </div>
                      <div class="rounded-2xl bg-[var(--bg-panel)] px-4 py-3">
                        <p class="text-[var(--text-muted)]">{{ t('builderView.visualOrder') }}</p>
                        <p class="font-medium text-[var(--text-primary)]">#{{ Number(index) + 1 }}</p>
                      </div>
                      <div class="rounded-2xl bg-[var(--bg-panel)] px-4 py-3">
                        <p class="text-[var(--text-muted)]">Progreso</p>
                        <p class="font-medium text-[var(--text-primary)]">{{ epic.completedTickets }} / {{ epic.totalTickets }}</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      class="mt-4 w-full rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-4 py-2.5 text-sm font-medium text-[var(--text-primary)] transition hover:bg-[var(--bg-card)]/10"
                      @click="openEpicModal(epic)"
                    >
                      Editar épica
                    </button>
                  </aside>
                </div>
              </article>

              <!-- Drop zone after last epic -->
              <div
                v-if="isDragging && dragPosition === 'below' && dragOverEpicId === epics[epics.length - 1]?.id"
                class="h-1 bg-[var(--status-done-bg)] rounded-full mt-2"
              />
            </div>
          </section>
        </div>

        <div v-else class="flex min-h-[60vh] items-center justify-center rounded-[2rem] border border-dashed border-[var(--border-subtle)] bg-[var(--bg-panel)] p-10 text-center">
          <div class="max-w-xl">
            <div class="mx-auto mb-5 flex h-20 w-20 items-center justify-center rounded-3xl border border-teal-40/30 bg-teal/10 text-3xl text-teal-200">
              CS
            </div>
            <h2 class="text-3xl font-semibold text-[var(--text-primary)]">{{ t('builderView.selectApplicationMessage') }}</h2>
            <p class="mt-3 text-sm leading-6 text-[var(--text-secondary)]">
              {{ t('builderView.panelDescription') }}
            </p>
            <div class="mt-6 flex justify-center gap-3">
              <button
                type="button"
                class="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-4 py-2 text-sm font-medium text-[var(--text-primary)] transition hover:bg-[var(--bg-card)]/10"
                @click="openAppModal()"
              >
                {{ t('builderView.createApplication') }}
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>

    <ApplicationFormModal
      :open="showAppModal"
      :title="editingAppId ? t('builderView.editApplication') : t('builderView.newApplicationTitle')"
      :saving="appSaving"
      :error="appError"
      :form="appForm"
      @close="closeAppModal"
      @submit="saveApp"
    />

    <Teleport to="body">
      <div v-if="showEpicModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-[var(--bg-app)]/80 px-4 backdrop-blur-sm">
      <div class="w-full max-w-2xl rounded-[2rem] border border-[var(--border-subtle)] bg-[var(--bg-app)] p-6 shadow-2xl shadow-black/40">
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-xs uppercase tracking-[0.22em] text-emerald-300/80">{{ t('builderView.epicsLabel') }}</p>
            <h3 class="mt-1 text-2xl font-semibold text-[var(--text-primary)]">{{ editingEpicId ? t('builderView.editEpic') : t('builderView.newEpicTitle') }}</h3>
          </div>
          <button type="button" class="rounded-full border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-3 py-1 text-sm text-[var(--text-secondary)]" @click="closeEpicModal">
            {{ t('builderView.close') }}
          </button>
        </div>

        <form class="mt-6 space-y-4" @submit.prevent="saveEpic">
          <div>
            <label class="mb-1 block text-sm text-[var(--text-secondary)]">{{ t('builderView.epicTitleLabel') }}</label>
            <input data-cy="epic-title-input" v-model="epicForm.title" type="text" class="w-full rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-4 py-3 text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:border-emerald-400 focus:outline-none" :placeholder="t('builderView.epicTitlePlaceholder')" />
          </div>
          <div>
            <label class="mb-1 block text-sm text-[var(--text-secondary)]">{{ t('builderView.formDescription') }}</label>
            <textarea v-model="epicForm.description" rows="4" class="w-full rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-4 py-3 text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:border-emerald-400 focus:outline-none" :placeholder="t('builderView.epicDescPlaceholder')"></textarea>
          </div>
          <div class="grid gap-4 md:grid-cols-2">
            <div>
              <label class="mb-1 block text-sm text-[var(--text-secondary)]">{{ t('builderView.dueDateLabel') }}</label>
              <input v-model="epicForm.dueDate" type="date" class="w-full rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-4 py-3 text-[var(--text-primary)] focus:border-emerald-400 focus:outline-none" />
            </div>
            <div class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-4 py-3">
              <p class="text-sm text-[var(--text-secondary)]">{{ t('builderView.targetApplication') }}</p>
              <p class="mt-1 font-medium text-[var(--text-primary)]">{{ selectedApp?.name || t('builderView.noSelection') }}</p>
            </div>
          </div>
          <p v-if="epicError" class="rounded-xl border border-[var(--priority-urg-bg)]/30 bg-[var(--priority-urg-bg)]/10 px-4 py-3 text-sm text-white">{{ epicError }}</p>
          <div class="flex gap-3 pt-2">
            <button data-cy="btn-guardar-epic" type="submit" class="flex-1 rounded-xl bg-[var(--status-done-bg)] px-4 py-3 font-semibold text-[var(--text-primary)] transition hover:bg-emerald-400">
              {{ epicSaving ? t('builderView.saving') : t('builderView.saveEpic') }}
            </button>
            <button type="button" class="flex-1 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-panel)] px-4 py-3 font-semibold text-[var(--text-primary)] transition hover:bg-[var(--bg-card)]/10" @click="closeEpicModal">
              {{ t('common.cancel') }}
            </button>
          </div>
        </form>
      </div>
    </div>
    </Teleport>
  
  <TicketSidePanel
  v-if="selectedTicket"
  :key="selectedTicket.id"
  :ticket="selectedTicket"
  :is-open="isTicketPanelOpen"
  @close="cerrarPanelTicket"
  @ticketUpdated="handleTicketAction"
/>
  
  </div>
</template>

<script setup lang="ts">

import { computed, onMounted, onUnmounted, reactive, ref, watch, defineAsyncComponent } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { eventBus } from '@/utils/eventBus'
import {
  Clock, AlertTriangle, Layers, CheckCircle, Plus, GripVertical,
} from 'lucide-vue-next'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppIcon from '@/components/shared/AppIcon.vue'
import ApplicationFormModal from '@/components/shared/ApplicationFormModal.vue'
import { useApplicationsStore, useEpicsStore, useTicketsStore, useAuthStore } from '@/stores'
import { useDialogStore } from '@/stores/dialog'
import { api } from '@/services/api'
import { useDragDropEpics } from '@/composables/useDragDropEpics'
import type { Application, Epic } from '@/types'
import TicketSidePanel from '@/components/workbench/TicketSidePanel.vue'


const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const appsStore = useApplicationsStore()
const authStore = useAuthStore()
const dialogStore = useDialogStore()
const epicsStore = useEpicsStore()
const ticketsStore = useTicketsStore()
// Controles para la creación inline de tickets
const creatingTicketInEpic = ref<string | null>(null)
const newTicketTitle = ref('')
const {
  draggedEpicId,
  dragOverEpicId,
  dragPosition,
  isDragging,
  handleEpicDragStart,
  handleEpicDragEnd,
  handleEpicDragOver,
  handleEpicDragLeave,
  calculateNewIndex,
  getDraggedEpicClass,
  getDropIndicatorClass,
  getEpicElevationClass,
} = useDragDropEpics()

const applications = computed(() => appsStore.sortedByName)
const selectedApp = computed(() => appsStore.selectedApp)
const epics = computed<any[]>(() => epicsStore.sortedByOrder)
const overallProgress = computed(() => epicsStore.overallEpicsProgress)
const allEpicsCollapsed = computed(() => epics.value.length > 0 && epics.value.every((epic: any) => epicsStore.collapsedEpics.has(epic.id)))

const showAppModal = ref(false)
const showEpicModal = ref(false)
const editingAppId = ref<string | null>(null)
const editingEpicId = ref<string | null>(null)
const appSaving = ref(false)
const epicSaving = ref(false)
const appError = ref('')
const epicError = ref('')
const draggingTicketId = ref<string | null>(null)

const appForm = reactive({
  name: '',
  description: '',
  color: '#06B7B2',
  icon: 'Folder',
})

const epicForm = reactive({
  title: '',
  description: '',
  dueDate: '',
})

watch(() => appForm.name, (val) => { if (val) appError.value = '' })
watch(() => epicForm.title, (val) => { if (val) epicError.value = '' })

const resetAppForm = () => {
  appForm.name = ''
  appForm.description = ''
  appForm.color = '#06B7B2'
  appForm.icon = 'Folder'
  appError.value = ''
}

const resetEpicForm = () => {
  epicForm.title = ''
  epicForm.description = ''
  epicForm.dueDate = ''
  epicError.value = ''
}

const openAppModal = (app?: Application) => {
  if (app) {
    editingAppId.value = app.id
    appForm.name = app.name
    appForm.description = app.description || ''
    appForm.color = app.color || '#06B7B2'
    appForm.icon = app.icon || 'Folder'
  } else {
    editingAppId.value = null
    resetAppForm()
  }
  showAppModal.value = true
}

const closeAppModal = () => {
  showAppModal.value = false
  editingAppId.value = null
  resetAppForm()
}

const openEpicModal = (epic?: Epic) => {
  if (!selectedApp.value && !epic) {
    epicError.value = 'Primero selecciona una aplicación'
    return
  }

  if (epic) {
    editingEpicId.value = epic.id
    epicForm.title = epic.title
    epicForm.description = epic.description || ''
    epicForm.dueDate = epic.dueDate ? epic.dueDate.slice(0, 10) : ''
  } else {
    editingEpicId.value = null
    resetEpicForm()
  }

  showEpicModal.value = true
}

const closeEpicModal = () => {
  showEpicModal.value = false
  editingEpicId.value = null
  resetEpicForm()
}

const selectApplication = async (app: Application) => {
  appsStore.selectApp(app)
  try {
    await epicsStore.fetchByApp(app.id)
    epicError.value = ''
  } catch (error) {
    epicError.value = error instanceof Error ? error.message : 'Error al cargar épicas'
  }
}

const loadApps = async () => {
  try {
    await appsStore.fetchAll()
    if (!selectedApp.value && applications.value.length > 0) {
      await selectApplication(applications.value[0])
    }
  } catch (error) {
    appError.value = error instanceof Error ? error.message : 'Error al cargar aplicaciones'
  }
}

const saveApp = async () => {
  if (!appForm.name.trim()) {
    appError.value = 'El nombre es obligatorio'
    return
  }

  appSaving.value = true
  appError.value = ''

  try {
    if (editingAppId.value) {
      const updated = await appsStore.update(editingAppId.value, {
        name: appForm.name,
        description: appForm.description,
        color: appForm.color,
        icon: appForm.icon,
      })
      appsStore.selectApp(updated)
      await epicsStore.fetchByApp(updated.id)
    } else {
      const created = await appsStore.create({
        name: appForm.name,
        description: appForm.description,
        color: appForm.color,
        icon: appForm.icon,
      })
      appsStore.selectApp(created)
      await epicsStore.fetchByApp(created.id)
    }

    closeAppModal()
  } catch (error) {
    appError.value = error instanceof Error ? error.message : 'Error al guardar la aplicación'
  } finally {
    appSaving.value = false
  }
}

const removeApp = async (app: Application) => {
  const confirmed = await dialogStore.confirm(`¿Eliminar la aplicación "${app.name}"? Esto borrará sus épicas y tickets.`)
  if (!confirmed) return

  try {
    await appsStore.remove(app.id)
    if (selectedApp.value?.id === app.id) {
      appsStore.selectApp(null)
      epicsStore.clear()
      if (applications.value.length > 0) {
        await selectApplication(applications.value[0])
      }
    }
  } catch (error) {
    appError.value = error instanceof Error ? error.message : 'Error al eliminar la aplicación'
  }
}

const saveEpic = async () => {
  if (!selectedApp.value) {
    epicError.value = t('builderView.selectApplicationFirst')
    return
  }

  if (!epicForm.title.trim()) {
    epicError.value = 'El título de la épica es obligatorio'
    return
  }

  epicSaving.value = true
  epicError.value = ''

  try {
    if (editingEpicId.value) {
      try {
        await epicsStore.update(editingEpicId.value, {
          title: epicForm.title,
          description: epicForm.description,
          dueDate: epicForm.dueDate || undefined,
        } as Partial<Epic>)
      } catch (e: any) {
        if (!e.response || e.response.status !== 500) {
          throw e;
        }
      }
    } else {
      await epicsStore.create({
        applicationId: selectedApp.value.id,
        title: epicForm.title,
        description: epicForm.description,
        dueDate: epicForm.dueDate || undefined,
      })
    }

    await new Promise(resolve => setTimeout(resolve, 100))

    await epicsStore.fetchByApp(selectedApp.value.id)
    closeEpicModal()
  } catch (error) {
    epicError.value = error instanceof Error ? error.message : 'Error al guardar la épica'
  } finally {
    epicSaving.value = false
  }
}

const removeEpic = async (epic: Epic) => {
  const confirmed = await dialogStore.confirm(`¿Eliminar la épica "${epic.title}"?`)
  if (!confirmed) return

  try {
    await epicsStore.remove(epic.id)
  } catch (error) {
    epicError.value = error instanceof Error ? error.message : 'Error al eliminar la épica'
  }
}

const moveEpic = async (epicId: string, newIndex: number) => {
  try {
    // Primero actualiza el orden en memoria
    const currentIndex = epics.value.findIndex((e: any) => e.id === epicId)
    if (currentIndex !== -1 && currentIndex !== newIndex) {
      epicsStore.reorderLocal(currentIndex, newIndex)
    }
    // Luego persiste el cambio en el servidor
    await epicsStore.persistEpicReorder(epicId)
  } catch (error) {
    epicError.value = error instanceof Error ? error.message : 'Error al reordenar la épica'
  }
}

/**
 * Maneja el dragover del article: solo activa efectos visuales al arrastrar UNA ÉPICA
 */
const handleEpicArticleDragOver = (epic: Epic, event: DragEvent) => {
  event.preventDefault()
  if (draggedEpicId.value) {
    handleEpicDragOver(epic, event)
  }
}

/**
 * Maneja el drop del article: distingue entre reorden de épicas y tickets en épicas colapsadas
 */
const handleEpicArticleDrop = async (epic: Epic, event: DragEvent) => {
  event.preventDefault()
  event.stopPropagation()

  // Si hay epicId → es un reorden de épica
  const epicId = event.dataTransfer?.getData('epicId')
  if (epicId) {
    await handleEpicDrop(epic, event)
    return
  }

  // Si hay ticketId → es un ticket cayendo sobre la cabecera (épica colapsada)
  const ticketId = event.dataTransfer?.getData('ticketId')
  if (ticketId) {
    draggingTicketId.value = null
    const sourceEpicId = epics.value.find((e: any) =>
      (e.tickets || []).some((t: any) => t.id === ticketId)
    )?.id
    if (sourceEpicId && sourceEpicId !== epic.id) {
      try {
        await ticketsStore.moveToEpic(ticketId, epic.id)
        if (selectedApp.value) {
          await epicsStore.fetchByApp(selectedApp.value.id)
        }
      } catch (error) {
        console.error('Error moviendo ticket:', error)
      }
    }
  }
}

/**
 * Maneja el drop de una épica reordenada via drag & drop
 * Calcula el nuevo índice y actualiza la posición
 */
const handleEpicDrop = async (epic: Epic, event: DragEvent) => {
  event.preventDefault()
  event.stopPropagation()

  try {
    // Obtener ID de la épica siendo arrastrada
    const draggedId = event.dataTransfer?.getData('epicId')
    if (!draggedId || !dragOverEpicId.value || !dragPosition.value) {
      return
    }

    // Calcular nuevo índice
    const newIndex = calculateNewIndex(epics.value, draggedId, dragOverEpicId.value, dragPosition.value)
    if (newIndex === null || newIndex === undefined) {
      return
    }

    // Llamar a moveEpic con el nuevo índice
    await moveEpic(draggedId, newIndex)
  } catch (error) {
    console.error('Error en handleEpicDrop:', error)
    epicError.value = error instanceof Error ? error.message : 'Error al reordenar la épica'
  } finally {
    handleEpicDragEnd()
  }
}

/**
 * Inicia el arrastre de un ticket entre épicas
 */
const handleTicketDragStart = (ticket: any, epic: any, event: DragEvent) => {
  draggingTicketId.value = ticket.id
  event.dataTransfer!.setData('ticketId', ticket.id)
  event.dataTransfer!.setData('sourceEpicId', epic.id)
  event.dataTransfer!.effectAllowed = 'move'
}

/**
 * Maneja el drop de un ticket en una épica destino
 * Mueve el ticket de una épica a otra
 */
const handleTicketDropOnEpic = async (targetEpic: any, event: DragEvent) => {
  const ticketId = event.dataTransfer?.getData('ticketId')
  const sourceEpicId = event.dataTransfer?.getData('sourceEpicId')
  draggingTicketId.value = null
  if (!ticketId) return

  // Si es la misma épica, no hacer nada
  if (sourceEpicId === targetEpic.id) return

  try {
    await ticketsStore.moveToEpic(ticketId, targetEpic.id)
    if (selectedApp.value) {
      await epicsStore.fetchByApp(selectedApp.value.id)
    }
  } catch (error) {
    console.error('Error moviendo ticket entre épicas:', error)
  }
}

const toggleEpicCollapse = (epicId: string) => {
  epicsStore.toggleCollapse(epicId)
}

const collapseAllEpics = () => {
  epicsStore.collapseAll()
}

const expandAllEpics = () => {
  epicsStore.expandAll()
}

const toggleAllEpics = () => {
  if (allEpicsCollapsed.value) {
    expandAllEpics()
    return
  }

  collapseAllEpics()
}

const appProgress = (app: Application) => {
  const total = app.ticketCount || 0
  if (!total) return 0
  return Math.max(0, Math.min(100, Math.round(((total - (app.pendingCount || 0) - (app.delayedCount || 0)) / total) * 100)))
}

const ticketBadge = (status: string) => {
  switch (status) {
    case 'DONE':
    case 'COMPLETED':
      return 'bg-[var(--status-done-bg)]/15 text-[var(--status-done-bg)]'
    case 'BLOCKED':
      return 'bg-rose-500/15 text-white'
    case 'IN_PROGRESS':
      return 'bg-teal/15 text-teal-200'
    default:
      return 'bg-[var(--bg-card)]/10 text-[var(--text-secondary)]'
  }
}

const getCardClass = (rawStatus: string) => {
  const status = String(rawStatus || '').toUpperCase()
  if (status === 'IN_PROGRESS') return 'border-teal/50 bg-teal/10 hover:border-teal-40/80'
  if (status === 'BLOCKED' || status === 'BLOCKED_QUESTION') return 'border-rose-500/50 bg-[var(--priority-urg-bg)]/10 hover:border-rose-400/80'
  if (status === 'COMPLETED' || status === 'DONE') return 'border-emerald-500/50 bg-[var(--status-done-bg)]/10 hover:border-emerald-400/80'
  return 'border-[var(--border-subtle)] bg-[var(--bg-panel)] hover:border-teal-40/50 hover:bg-[var(--bg-card)]/10'
}

const getBadgeClass = (rawStatus: string) => {
  const status = String(rawStatus || '').toUpperCase()
  if (status === 'IN_PROGRESS') return 'bg-teal/15 text-teal-200'
  if (status === 'BLOCKED' || status === 'BLOCKED_QUESTION') return 'bg-rose-500/15 text-white'
  if (status === 'COMPLETED' || status === 'DONE') return 'bg-[var(--status-done-bg)]/15 text-[var(--status-done-bg)]'
  return 'bg-[var(--bg-card)]/10 text-[var(--text-secondary)]'
}

const getBadgeText = (rawStatus: string) => {
  const status = String(rawStatus || '').toUpperCase()
  if (status === 'IN_PROGRESS') return 'EN PROGRESO'
  if (status === 'BLOCKED' || status === 'BLOCKED_QUESTION') return 'BLOQUEADO'
  if (status === 'COMPLETED' || status === 'DONE') return 'COMPLETADO'
  return 'POR HACER'
}

const formatStatus = (status: string) => {
  if (!status) return 'Desconocido'
  const s = status.toUpperCase()
  if (s === 'TODO') return 'Por Hacer'
  if (s === 'IN_PROGRESS') return 'En Progreso'
  if (s === 'BLOCKED') return 'Bloqueado'
  if (s === 'COMPLETED' || s === 'DONE') return 'Completado'
  return s
}

const guardarTicketInline = async (epicId: string) => {
  if (!newTicketTitle.value.trim()) {
    creatingTicketInEpic.value = null
    return
  }

  try {
    await ticketsStore.create({
      epicId: epicId,
      title: newTicketTitle.value.trim(),
      description: '',
      priority: 'MEDIUM',
    })

    // Limpiamos el input y lo cerramos
    newTicketTitle.value = ''
    creatingTicketInEpic.value = null

    // Recargamos la vista
    if (selectedApp.value) {
      await epicsStore.fetchByApp(selectedApp.value.id)
    }
  } catch (error) {
    console.error('Error al crear ticket:', error)
    dialogStore.alert('Hubo un error al crear el ticket: ' + (error instanceof Error ? error.message : String(error)))
  }
}

const formatDate = (date?: string) => {
  if (!date) return 'Sin fecha'
  const parsed = new Date(date)
  if (Number.isNaN(parsed.getTime())) return 'Sin fecha'
  return new Intl.DateTimeFormat('es-ES', { day: '2-digit', month: 'short', year: 'numeric' }).format(parsed)
}
const selectedTicket = ref<any>(null)
const isTicketPanelOpen = ref(false)

const abrirPanelTicket = async (ticket: any, epic: any) => {
  // Mostrar inmediatamente con datos del store para respuesta visual rápida
  selectedTicket.value = {
    ...ticket,
    appName: selectedApp.value?.name,
    epicTitle: epic.title
  }
  isTicketPanelOpen.value = true
  // Fetch datos frescos de la API para garantizar estado actual (ej. BLOCKED_QUESTION)
  try {
    const fresh = await api.tickets.getById(ticket.id)
    selectedTicket.value = {
      ...fresh,
      appName: selectedApp.value?.name,
      epicTitle: epic.title
    }
  } catch {
    // Si falla el fetch, el panel ya está abierto con datos del store
  }
}

const cerrarPanelTicket = async () => {
  isTicketPanelOpen.value = false
  // No se hace null a selectedTicket — el componente permanece montado para preservar el estado del timer
  if (selectedApp.value) {
    await epicsStore.fetchByApp(selectedApp.value.id)
  }
}

const handleTicketAction = async (payload: any) => {
  try {
    const { ticketId, action, data } = payload

    // 'start', 'question', 'resolve', 'questionResolved': TicketSidePanel ya
    // llamó la API directamente antes de emitir. Llamarla aquí causaría 422
    // (estado ya cambiado) y corrompería el ticketsStore.error global.
    // Solo 'complete' y 'redirect' necesitan la llamada al store aquí.
    if (action === 'complete') {
      const prUrl = data?.prUrl || (selectedTicket.value ? selectedTicket.value.prLink : '')
      const prUrlRegex = /^https?:\/\/(github\.com|gitlab\.com|bitbucket\.org)\//i
      if (!prUrl || !prUrlRegex.test(prUrl)) {
        dialogStore.alert('El enlace de PR debe ser válido (GitHub, GitLab o Bitbucket) antes de completar el ticket.')
        return
      }
      await ticketsStore.completeTicket(ticketId, prUrl)
    } else if (action === 'redirect') {
      await ticketsStore.redirectTicket(ticketId, data.toUserId, data.reason)
    }
    // 'questionResolved' es emitido por TicketSidePanel cuando el Admin resuelve
    // directamente desde su propio formulario (sin pasar por ActionDock)

    // Forzamos visualmente el cambio en nuestras variables (Reacción instantánea)
    let targetStatus = ''
    if (action === 'start') targetStatus = 'IN_PROGRESS'
    else if (action === 'question') targetStatus = 'BLOCKED_QUESTION'
    else if (action === 'resolve' || action === 'questionResolved') targetStatus = 'IN_PROGRESS'
    else if (action === 'complete') targetStatus = 'COMPLETED'

    if (targetStatus) {
      // Creamos una copia nueva del objeto para forzar la reactividad en el panel
      if (selectedTicket.value && selectedTicket.value.id === ticketId) {
        selectedTicket.value = {
          ...selectedTicket.value,
          status: targetStatus
        }
      }

      // Actualizamos también las épicas del fondo
      epicsStore.epics.forEach((epic: any) => {
        const t = epic.tickets?.find((t: any) => t.id === ticketId)
        if (t) t.status = targetStatus
      })
    }
    
    // 3. Le damos 300ms de respiro a la base de datos para que guarde, y luego recargamos
    setTimeout(async () => {
      if (selectedApp.value) {
        await epicsStore.fetchByApp(selectedApp.value.id)
      }
    }, 300)
    
    if (action === 'complete' || action === 'redirect') {
      cerrarPanelTicket()
    }
    
  } catch (error) {
    console.error('Error al ejecutar acción del ticket:', error)
  }
}

const handleWsTicketUpdate = (detail: any) => {
  const ticketId = detail?.ticket_id
  const newStatus = detail?.new_status
  if (!ticketId || !newStatus) return
  // 1. Actualizar ticketsStore (para Workbench y otros)
  const idx = ticketsStore.tickets.findIndex((t: any) => t.id === ticketId)
  if (idx !== -1) {
    ticketsStore.tickets[idx] = { ...ticketsStore.tickets[idx], status: newStatus }
  }
  // 2. Actualizar epicsStore — las swimlane cards del Constructor leen de aquí
  for (const epic of epicsStore.epics as any[]) {
    const epicTickets = epic.tickets as any[]
    if (!Array.isArray(epicTickets)) continue
    const tIdx = epicTickets.findIndex((t: any) => t.id === ticketId)
    if (tIdx !== -1) {
      epicTickets[tIdx] = { ...epicTickets[tIdx], status: newStatus }
    }
  }
  // 3. Si el panel está abierto con ese ticket, actualizar también
  if (selectedTicket.value?.id === ticketId) {
    selectedTicket.value = { ...selectedTicket.value, status: newStatus }
  }
}

onUnmounted(() => {
  eventBus.off('ws-update', handleWsTicketUpdate)
})

onMounted(async () => {
  eventBus.on('ws-update', handleWsTicketUpdate)
  await loadApps()
  const notifTicketId = route.query.ticketId as string | undefined
  if (notifTicketId) {
    try {
      const ticket = await api.tickets.getById(notifTicketId)
      selectedTicket.value = ticket
      isTicketPanelOpen.value = true
    } catch {
      // ticket not found or unauthorized — ignore
    }
    router.replace({ query: {} })
  }
})

watch(
  () => selectedApp.value?.id,
  async (appId: any) => {
    if (!appId) return
    try {
      await epicsStore.fetchByApp(appId)
      epicError.value = ''
    } catch (error) {
      epicError.value = error instanceof Error ? error.message : 'Error al cargar épicas'
    }
  }
)
</script>


