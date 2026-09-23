<!--
  Vista de Constructor (Admin)

  Permite a administradores crear y gestionar aplicaciones, épicas y tickets.
  Flujo: seleccionar aplicación -> crear épica -> crear tickets -> avanzar estado.
-->
<template>
  <div class="p-8 max-w-6xl mx-auto text-[var(--text-primary)]">
    <h1 class="text-3xl font-bold">Constructor de Aplicaciones</h1>
    <p class="mt-2 text-[var(--text-muted)]">
      Crea y gestiona aplicaciones, épicas y tickets
    </p>

    <div class="mt-6 flex flex-wrap items-center justify-between gap-3">
      <div>
        <p class="text-sm uppercase tracking-[0.2em] text-[var(--text-muted)]">Aplicaciones activas</p>
        <p class="text-sm text-[var(--text-muted)] mt-1">
          {{ activeApplications.length }} proyecto{{ activeApplications.length === 1 ? '' : 's' }} disponible{{ activeApplications.length === 1 ? '' : 's' }}
        </p>
      </div>

      <button
        v-if="canManageApplications"
        @click="showNewApp = !showNewApp"
        class="px-3 py-2 rounded-lg text-sm bg-[var(--teal)] hover:bg-[var(--teal-90)]"
      >
        + Nueva aplicación
      </button>
    </div>

    <div v-if="activeApplications.length" class="mt-5 space-y-3">
      <div
        v-for="app in activeApplications"
        :key="app.id"
        class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-4 shadow-sm"
      >
        <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-3">
              <span
                class="inline-block h-3 w-3 rounded-full"
                :style="{ backgroundColor: app.color || '#14b8a6' }"
              ></span>
              <h3 class="font-semibold text-lg text-[var(--text-primary)]">{{ app.name }}</h3>
            </div>
            <p class="mt-2 text-sm text-[var(--text-muted)]">
              {{ app.description || 'Sin descripción disponible.' }}
            </p>
            <div class="mt-3 flex flex-wrap gap-2 text-xs text-[var(--text-muted)]">
              <span class="rounded-full bg-[var(--bg-app)] px-2 py-1">{{ app.epicCount ?? 0 }} épicas</span>
              <span class="rounded-full bg-[var(--bg-app)] px-2 py-1">{{ app.pendingCount ?? 0 }} pendientes</span>
            </div>
          </div>

          <div class="flex flex-wrap gap-2">
            <button
              @click="selectApplication(app.id)"
              :class="[
                'px-3 py-2 rounded-lg text-sm transition-colors',
                selectedAppId === app.id
                  ? 'bg-[var(--teal)] text-white'
                  : 'bg-[var(--bg-app)] text-[var(--text-primary)] border border-[var(--border-subtle)] hover:border-[var(--teal)]'
              ]"
            >
              {{ selectedAppId === app.id ? 'Seleccionada' : 'Seleccionar' }}
            </button>

            <button
              v-if="canManageApplications"
              @click="openAppEditor(app)"
              class="px-3 py-2 rounded-lg text-sm bg-[var(--bg-app)] text-[var(--text-primary)] border border-[var(--border-subtle)] hover:border-[var(--teal)]"
            >
              Editar
            </button>

            <button
              v-if="canManageApplications"
              @click="toggleAppArchive(app)"
              class="px-3 py-2 rounded-lg text-sm border border-[var(--border-subtle)] bg-[var(--bg-app)] text-[var(--text-primary)] hover:border-amber-500"
            >
              {{ app.isActive === false ? 'Reactivar' : 'Archivar' }}
            </button>

            <button
              @click="openEpicCreatorFor(app.id)"
              class="px-3 py-2 rounded-lg text-sm bg-[var(--teal)]/20 text-[var(--teal)] hover:bg-[var(--teal)]/30"
            >
              Crear épicas
            </button>
          </div>
        </div>

        <div v-if="editingAppId === app.id" class="mt-4 border-t border-[var(--border-subtle)] pt-4">
          <div class="mb-3">
            <label class="block text-xs uppercase tracking-[0.15em] text-[var(--text-muted)] mb-2">Nombre</label>
            <input
              v-model="editAppForm.name"
              class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2 outline-none"
              placeholder="Nombre del proyecto"
            />
          </div>

          <div class="mb-3">
            <label class="block text-xs uppercase tracking-[0.15em] text-[var(--text-muted)] mb-2">Descripción</label>
            <textarea
              v-model="editAppForm.description"
              rows="2"
              class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2 outline-none"
              placeholder="Descripción del proyecto"
            ></textarea>
          </div>

          <div class="mb-3 flex items-center justify-between rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)] px-3 py-2">
            <div>
              <p class="text-sm font-medium">Estado del proyecto</p>
              <p class="text-xs text-[var(--text-muted)]">{{ editAppForm.isArchived ? 'Archivado' : 'Activo' }}</p>
            </div>
            <label class="inline-flex items-center cursor-pointer">
              <input v-model="editAppForm.isArchived" type="checkbox" class="h-4 w-4 rounded border-[var(--border-subtle)] text-[var(--teal)] focus:ring-[var(--teal)]" />
              <span class="ml-2 text-sm text-[var(--text-primary)]">Archivado</span>
            </label>
          </div>

          <p v-if="appError" class="text-xs text-red-400 mb-2 font-medium">{{ appError }}</p>

          <div class="flex gap-2">
            <button
              :disabled="!editAppForm.name.trim() || working"
              @click="saveAppEdits(app)"
              class="bg-[var(--teal)] hover:bg-[var(--teal-90)] disabled:opacity-50 px-4 py-1.5 rounded-lg text-sm"
            >
              Guardar cambios
            </button>
            <button @click="cancelAppEdit" class="text-[var(--text-muted)] px-4 py-1.5 text-sm">Cancelar</button>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="mt-5 rounded-2xl border border-dashed border-[var(--border-subtle)] bg-[var(--bg-card)] p-8 text-center text-[var(--text-muted)]">
      No hay aplicaciones activas para mostrar.
    </div>

    <div v-if="authStore.isAdmin && archivedApplications.length" class="mt-8">
      <div class="flex items-center justify-between gap-3 mb-3">
        <h2 class="text-lg font-semibold text-[var(--text-primary)]">Archivados</h2>
        <span class="rounded-full bg-amber-500/10 px-2 py-1 text-xs font-medium text-amber-300 border border-amber-400/20">
          {{ archivedApplications.length }} proyecto{{ archivedApplications.length === 1 ? '' : 's' }}
        </span>
      </div>

      <div class="space-y-3">
        <div
          v-for="app in archivedApplications"
          :key="app.id"
          class="rounded-2xl border border-amber-500/30 bg-[var(--bg-card)] p-4 opacity-80"
        >
          <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div class="flex items-center gap-3">
              <span class="inline-block h-3 w-3 rounded-full bg-amber-500"></span>
              <div>
                <h3 class="font-semibold text-lg text-[var(--text-primary)]">{{ app.name }}</h3>
                <p class="text-xs text-[var(--text-muted)] uppercase tracking-[0.18em]">Archivado</p>
              </div>
            </div>

            <button
              @click="toggleAppArchive(app)"
              class="px-3 py-2 rounded-lg text-sm border border-amber-500/40 bg-amber-500/10 text-amber-200 hover:bg-amber-500/20"
            >
              Reactivar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Formulario nueva aplicación -->
    <div v-if="showNewApp" class="mt-6 bg-[var(--bg-card)] p-4 rounded-xl border border-[var(--teal)]/50">
      <input
        v-model="newAppName"
        placeholder="Nombre de la aplicación…"
        class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2 mb-3 outline-none"
      />
      <textarea
        v-model="newAppDescription"
        placeholder="Descripción (opcional)"
        rows="2"
        class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2 mb-3 outline-none"
      ></textarea>
      <p v-if="appError" class="text-xs text-red-400 mb-2 font-medium">{{ appError }}</p>
      <div class="flex gap-2">
        <button
          :disabled="!newAppName.trim() || working"
          @click="createApp"
          class="bg-[var(--teal)] hover:bg-[var(--teal-90)] disabled:opacity-50 px-4 py-1.5 rounded-lg text-sm"
        >
          Crear aplicación
        </button>
        <button @click="showNewApp = false" class="text-[var(--text-muted)] px-4 py-1.5 text-sm">Cancelar</button>
      </div>
    </div>

    <!-- Nueva épica -->
    <div v-if="selectedAppId" class="mt-8">
      <div v-if="!showNewEpic">
        <button
          @click="showNewEpic = true"
          class="w-full py-3 border-2 border-dashed border-[var(--border-subtle)] rounded-xl text-[var(--text-muted)] hover:border-[var(--teal)] hover:text-[var(--teal)] transition-all font-medium"
        >
          + Añadir nueva Épica
        </button>
      </div>
      <div v-else class="bg-[var(--bg-card)] p-4 rounded-xl border border-[var(--teal)]/50 mb-4">
        <input
          v-model="newEpicTitle"
          @keyup.enter="createEpic"
          placeholder="Nombre de la épica…"
          class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2 mb-3 outline-none"
          autofocus
        />
        <div class="flex gap-2">
          <button
            :disabled="!newEpicTitle.trim() || working"
            @click="createEpic"
            class="bg-[var(--teal)] hover:bg-[var(--teal-90)] disabled:opacity-50 px-4 py-1.5 rounded-lg text-sm"
          >
            Guardar
          </button>
          <button @click="showNewEpic = false" class="text-[var(--text-muted)] px-4 py-1.5 text-sm">Cancelar</button>
        </div>
      </div>

      <!-- Consulta de tickets: filtra por título o estado dentro de la aplicación -->
      <div class="mb-4">
        <input
          v-model="searchQuery"
          placeholder="Buscar tickets por título o estado…"
          class="w-full bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg p-2 outline-none focus:border-[var(--teal)]"
        />
      </div>

      <div v-if="epicsStore.isLoading" class="text-center py-12 text-[var(--text-muted)]">Cargando épicas…</div>
      <div v-else-if="epicsStore.error" class="text-center py-8 text-red-400 text-sm">{{ epicsStore.error }}</div>
      <div v-else-if="epics.length === 0" class="text-center py-12 text-[var(--text-muted)]">
        Todavía no hay épicas en esta aplicación.
      </div>

      <div
        v-for="(epic, index) in epics"
        :key="epic.id"
        draggable="true"
        @dragstart="handleEpicDragStart(epic.id)"
        @dragenter.prevent="dropTargetEpicId = epic.id"
        @dragleave="handleEpicDragLeave(epic.id)"
        @dragover.prevent
        @drop="handleEpicDrop(epic.id)"
        @dragend="handleEpicDragEnd"
        :class="[
          'mt-4 border rounded-xl overflow-hidden cursor-move transition-all duration-150',
          draggedEpicId === epic.id ? 'opacity-60 scale-[0.99]' : 'bg-[var(--bg-card)]/50',
          dropTargetEpicId === epic.id
            ? 'border-[var(--teal)] bg-[var(--teal)]/5 ring-2 ring-[var(--teal)]/40 shadow-lg'
            : 'border-[var(--border-subtle)] bg-[var(--bg-card)]/50'
        ]"
      >
        <div v-if="dropTargetEpicId === epic.id" class="flex items-center justify-center border-b border-dashed border-[var(--teal)] bg-[var(--teal)]/10 px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--teal)]">
          Suelta aquí
        </div>

        <div class="p-4 flex items-center justify-between gap-3">
          <div class="flex items-center gap-2 min-w-0">
            <span class="text-[var(--text-muted)] text-xs">#{{ index + 1 }}</span>
            <div class="min-w-0">
              <h3 class="font-bold text-lg">{{ epic.title }}</h3>
              <div class="mt-2">
                <div class="flex items-center justify-between gap-3 text-[10px] uppercase tracking-[0.16em] text-[var(--text-muted)]">
                  <span>{{ getEpicProgress(epic.id).completed }}/{{ getEpicProgress(epic.id).total }} completados</span>
                  <span
                    :class="getEpicProgressBadgeClass(getEpicProgress(epic.id).percentage)"
                    class="rounded-full px-2 py-0.5 font-semibold"
                  >
                    {{ getEpicProgress(epic.id).isComplete ? 'COMPLETO' : `Faltan ${getEpicProgress(epic.id).remaining}` }}
                  </span>
                </div>

                <div class="mt-2 h-2.5 w-full rounded-full overflow-hidden bg-[var(--bg-app)] border border-[var(--border-subtle)]">
                  <div
                    class="h-full rounded-full transition-all duration-300"
                    :class="getEpicProgressBarClass(getEpicProgress(epic.id).percentage)"
                    :style="{ width: getEpicProgress(epic.id).percentage + '%' }"
                  ></div>
                </div>

                <div class="mt-1 flex items-center justify-between text-[11px] text-[var(--text-muted)]">
                  <span>{{ getEpicProgress(epic.id).percentage }}%</span>
                  <span>
                    {{ getEpicProgress(epic.id).remaining === 0 ? 'Todo listo' : `${getEpicProgress(epic.id).remaining} por terminar` }}
                  </span>
                </div>
              </div>
            </div>
          </div>
          <div class="flex flex-wrap gap-2">
            <button
              v-if="canManageApplications"
              @click="openEpicEditor(epic)"
              class="px-3 py-1.5 rounded-lg text-sm bg-[var(--bg-app)] text-[var(--text-primary)] border border-[var(--border-subtle)] hover:border-[var(--teal)]"
            >
              Editar
            </button>
            <button
              @click="openTicketFormFor = openTicketFormFor === epic.id ? null : epic.id"
              class="px-3 py-1.5 rounded-lg text-sm bg-[var(--teal)]/20 text-[var(--teal)] hover:bg-[var(--teal)]/30"
            >
              + Nuevo ticket
            </button>
          </div>
        </div>

        <div v-if="editingEpicId === epic.id" class="p-4 border-t border-[var(--border-subtle)] bg-[var(--bg-app)]/30">
          <div class="mb-3">
            <label class="block text-xs uppercase tracking-[0.15em] text-[var(--text-muted)] mb-2">Nombre de la épica</label>
            <input
              v-model="editEpicForm.title"
              class="w-full bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg p-2 outline-none"
              placeholder="Nombre de la épica"
            />
          </div>

          <div class="mb-3">
            <label class="block text-xs uppercase tracking-[0.15em] text-[var(--text-muted)] mb-2">Descripción</label>
            <textarea
              v-model="editEpicForm.description"
              rows="2"
              class="w-full bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg p-2 outline-none"
              placeholder="Descripción de la épica"
            ></textarea>
          </div>

          <p v-if="appError" class="text-xs text-red-400 mb-2 font-medium">{{ appError }}</p>

          <div class="flex gap-2">
            <button
              :disabled="!editEpicForm.title.trim() || working"
              @click="saveEpicEdits(epic)"
              class="bg-[var(--teal)] hover:bg-[var(--teal-90)] disabled:opacity-50 px-4 py-1.5 rounded-lg text-sm"
            >
              Guardar cambios
            </button>
            <button @click="cancelEpicEdit" class="text-[var(--text-muted)] px-4 py-1.5 text-sm">Cancelar</button>
          </div>
        </div>

        <div v-if="openTicketFormFor === epic.id" class="p-4 border-t border-[var(--border-subtle)] bg-[var(--bg-app)]/30">
          <input
            v-model="ticketForm.title"
            placeholder="Título del ticket *"
            class="w-full bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg p-2 mb-2 outline-none"
          />
          <textarea
            v-model="ticketForm.description"
            placeholder="Descripción (opcional)"
            rows="2"
            class="w-full bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg p-2 mb-2 outline-none"
          ></textarea>
          <div class="flex flex-wrap gap-2 mb-3">
            <select
              v-model="ticketForm.priority"
              class="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg px-3 py-2 text-sm outline-none"
            >
              <option value="LOW">Prioridad: Baja</option>
              <option value="MEDIUM">Prioridad: Media</option>
              <option value="HIGH">Prioridad: Alta</option>
              <option value="URGENT">Prioridad: Urgente</option>
            </select>
            <input
              v-model="ticketForm.dueDate"
              type="date"
              class="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg px-3 py-2 text-sm outline-none"
            />
          </div>
          <div class="flex gap-2">
            <button
              :disabled="!ticketForm.title.trim() || working"
              @click="createTicket(epic)"
              class="bg-[var(--teal)] hover:bg-[var(--teal-90)] disabled:opacity-50 px-4 py-1.5 rounded-lg text-sm"
            >
              Crear ticket
            </button>
            <button @click="openTicketFormFor = null" class="text-[var(--text-muted)] px-4 py-1.5 text-sm">Cancelar</button>
          </div>
        </div>

        <p v-if="ticketError" class="px-3 py-2 text-xs text-red-400 border-t border-[var(--border-subtle)]">{{ ticketError }}</p>

        <div v-if="visibleTickets(epic.id).length" class="border-t border-[var(--border-subtle)] divide-y divide-[var(--border-subtle)]">
          <div
            v-for="ticket in visibleTickets(epic.id)"
            :key="ticket.id"
            class="p-3 flex flex-wrap items-center justify-between gap-2"
          >
            <div class="min-w-0">
              <p class="font-medium truncate">{{ ticket.title }}</p>
              <div class="flex flex-wrap items-center gap-2 mt-1 text-xs">
                <span :class="statusClass(ticket.status)" class="px-2 py-0.5 rounded-full font-medium">{{ statusLabel(ticket.status) }}</span>
                <span :class="priorityClass(ticket.priority)" class="px-2 py-0.5 rounded-full font-medium">{{ priorityLabel(ticket.priority) }}</span>
                <span v-if="ticket.dueDate" class="text-[var(--text-muted)]">📅 {{ ticket.dueDate.slice(0, 10) }}</span>
              </div>
            </div>
            <div class="flex flex-wrap gap-2">
              <button
                v-if="ticket.status === 'TODO'"
                :disabled="working"
                @click="startTicket(ticket)"
                class="px-3 py-1 rounded-lg text-xs bg-blue-600/20 text-blue-400 hover:bg-blue-600/30 disabled:opacity-50"
              >
                ▶ Iniciar
              </button>
              <button
                v-if="ticket.status === 'IN_PROGRESS'"
                :disabled="working"
                @click="completeTicket(ticket)"
                class="px-3 py-1 rounded-lg text-xs bg-emerald-600/20 text-emerald-400 hover:bg-emerald-600/30 disabled:opacity-50"
              >
                ✓ Finalizar
              </button>
              <button
                @click="toggleSubtaskPanel(ticket.id)"
                class="px-3 py-1 rounded-lg text-xs bg-[var(--bg-app)] text-[var(--text-primary)] border border-[var(--border-subtle)] hover:border-[var(--teal)]"
              >
                ☑ Subtareas ({{ (ticket.subtasks ?? []).length }})
              </button>
              <button
                @click="openTicketEditor(ticket)"
                class="px-3 py-1 rounded-lg text-xs bg-[var(--bg-app)] text-[var(--text-primary)] border border-[var(--border-subtle)] hover:border-[var(--teal)]"
              >
                ✏️ Editar
              </button>
              <button
                @click="toggleTicketDetail(ticket)"
                class="px-3 py-1 rounded-lg text-xs bg-[var(--bg-app)] text-[var(--text-primary)] border border-[var(--border-subtle)] hover:border-[var(--teal)]"
              >
                👁 Detalle
              </button>
              <button
                @click="deleteTicket(ticket)"
                class="px-3 py-1 rounded-lg text-xs bg-red-500/10 text-red-400 border border-red-500/30 hover:bg-red-500/20"
              >
                🗑 Eliminar
              </button>
            </div>

            <!-- Subtareas del ticket (POST/PUT/DELETE /api/subtasks) -->
            <div
              v-if="openSubtasksFor === ticket.id"
              class="w-full mt-2 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)]/40 p-2"
            >
              <p v-if="!(ticket.subtasks ?? []).length" class="text-xs text-[var(--text-muted)] mb-2">
                Este ticket todavía no tiene subtareas.
              </p>
              <ul v-else class="space-y-1 mb-2">
                <li v-for="sub in ticket.subtasks" :key="sub.id" class="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    :checked="sub.isCompleted"
                    :disabled="working"
                    @change="toggleSubtask(ticket, sub)"
                    class="accent-[var(--teal)]"
                  />
                  <template v-if="editingSubtaskId === sub.id">
                    <input
                      v-model="editSubtaskTitle"
                      @keyup.enter="saveSubtaskTitle(ticket)"
                      class="flex-1 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded px-2 py-1 text-sm outline-none"
                    />
                    <button
                      :disabled="working || !editSubtaskTitle.trim()"
                      @click="saveSubtaskTitle(ticket)"
                      class="text-xs text-[var(--teal)] font-medium disabled:opacity-50"
                    >
                      Guardar
                    </button>
                    <button @click="editingSubtaskId = null" class="text-xs text-[var(--text-muted)]">Cancelar</button>
                  </template>
                  <template v-else>
                    <span
                      :class="sub.isCompleted ? 'line-through text-[var(--text-muted)]' : 'text-[var(--text-primary)]'"
                      class="flex-1 min-w-0 truncate"
                    >{{ sub.title }}</span>
                    <button
                      :disabled="working"
                      @click="startEditSubtask(sub)"
                      class="text-xs text-[var(--text-muted)] hover:text-[var(--teal)] disabled:opacity-50"
                      title="Renombrar subtarea"
                    >
                      ✎
                    </button>
                    <button
                      :disabled="working"
                      @click="removeSubtask(ticket, sub)"
                      class="text-xs text-red-400 hover:text-red-300 disabled:opacity-50"
                      title="Eliminar subtarea"
                    >
                      ✕
                    </button>
                  </template>
                </li>
              </ul>
              <div class="flex gap-2">
                <input
                  v-model="newSubtaskTitle"
                  @keyup.enter="addSubtask(ticket)"
                  placeholder="Nueva subtarea…"
                  class="flex-1 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg px-2 py-1 text-sm outline-none"
                />
                <button
                  :disabled="working || !newSubtaskTitle.trim()"
                  @click="addSubtask(ticket)"
                  class="px-3 py-1 rounded-lg text-xs bg-[var(--teal)]/20 text-[var(--teal)] hover:bg-[var(--teal)]/30 disabled:opacity-50"
                >
                  Añadir
                </button>
              </div>
            </div>

            <!-- Edición de ticket: título, descripción, prioridad, fecha, PR, asignado y épica -->
            <div
              v-if="editingTicketId === ticket.id"
              class="w-full mt-2 rounded-lg border border-[var(--teal)]/40 bg-[var(--bg-card)] p-3 space-y-2"
            >
              <input
                v-model="editTicketForm.title"
                placeholder="Título *"
                class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2 text-sm outline-none"
              />
              <textarea
                v-model="editTicketForm.description"
                placeholder="Descripción"
                rows="3"
                class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2 text-sm outline-none"
              ></textarea>
              <div class="flex flex-wrap gap-2">
                <select
                  v-model="editTicketForm.priority"
                  class="bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg px-3 py-2 text-sm outline-none"
                >
                  <option value="LOW">Prioridad: Baja</option>
                  <option value="MEDIUM">Prioridad: Media</option>
                  <option value="HIGH">Prioridad: Alta</option>
                  <option value="URGENT">Prioridad: Urgente</option>
                </select>
                <input
                  v-model="editTicketForm.dueDate"
                  type="date"
                  title="Fecha límite"
                  class="bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg px-3 py-2 text-sm outline-none"
                />
              </div>
              <input
                v-model="editTicketForm.prLink"
                placeholder="Enlace del PR (https://github.com/…)"
                class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2 text-sm outline-none"
              />
              <div class="flex flex-wrap gap-2">
                <select
                  v-model="editTicketForm.assigneeId"
                  class="bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg px-3 py-2 text-sm outline-none"
                >
                  <option value="">Sin asignar</option>
                  <option v-for="u in usersList" :key="u.id" :value="u.id">
                    {{ u.fullName || u.email }}
                  </option>
                </select>
                <select
                  v-model="editTicketForm.epicId"
                  class="bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg px-3 py-2 text-sm outline-none"
                >
                  <option v-for="e in epics" :key="e.id" :value="e.id">
                    Épica: {{ e.title }}
                  </option>
                </select>
              </div>
              <p v-if="ticketError" class="text-xs text-red-400">{{ ticketError }}</p>
              <div class="flex gap-2">
                <button
                  :disabled="working || !editTicketForm.title.trim()"
                  @click="saveTicketEdits(ticket)"
                  class="px-3 py-1.5 rounded-lg text-sm bg-[var(--teal)] hover:bg-[var(--teal-90)] disabled:opacity-50"
                >
                  Guardar cambios
                </button>
                <button @click="editingTicketId = null" class="text-[var(--text-muted)] px-3 py-1.5 text-sm">Cancelar</button>
              </div>
            </div>

            <!-- Detalle del ticket (consulta completa) -->
            <div
              v-if="detailTicketId === ticket.id"
              class="w-full mt-2 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)]/40 p-3 text-sm space-y-1.5"
            >
              <p>
                <span class="text-[var(--text-muted)]">Descripción:</span>
                {{ ticket.description || '—' }}
              </p>
              <p>
                <span class="text-[var(--text-muted)]">Épica:</span>
                {{ epicTitleFor(ticket.epicId) }}
              </p>
              <p>
                <span class="text-[var(--text-muted)]">Asignado:</span>
                {{ ticket.assignee ? (ticket.assignee.fullName || ticket.assignee.email) : 'Sin asignar' }}
              </p>
              <p>
                <span class="text-[var(--text-muted)]">Estado:</span> {{ statusLabel(ticket.status) }}
                · <span class="text-[var(--text-muted)]">Prioridad:</span> {{ priorityLabel(ticket.priority) }}
              </p>
              <p>
                <span class="text-[var(--text-muted)]">Fecha límite:</span> {{ ticket.dueDate ? ticket.dueDate.slice(0, 10) : '—' }}
                · <span class="text-[var(--text-muted)]">Creado:</span> {{ ticket.createdAt ? ticket.createdAt.slice(0, 10) : '—' }}
              </p>
              <p>
                <span class="text-[var(--text-muted)]">PR:</span>
                <a
                  v-if="ticket.prLink"
                  :href="ticket.prLink"
                  target="_blank"
                  rel="noopener"
                  class="text-[var(--teal)] underline break-all"
                >{{ ticket.prLink }}</a>
                <span v-else>—</span>
              </p>
              <p>
                <span class="text-[var(--text-muted)]">Subtareas:</span>
                {{ (ticket.subtasks ?? []).filter((s) => s.isCompleted).length }}/{{ (ticket.subtasks ?? []).length }} completadas
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="!showNewApp && applicationsStore.applications.length === 0" class="mt-10 text-center py-12 text-[var(--text-muted)]">
      No hay aplicaciones todavía. Crea la primera con «+ Nueva aplicación».
    </div>
  </div>
</template>
<script setup lang="ts">
/**
 * BuilderView (Admin) - WEB-08
 * Creación de aplicaciones -> épicas -> tickets y avance básico de estado.
 */
import { ref, computed, onMounted } from 'vue'
import { useApplicationsStore } from '@/stores/applications'
import { useEpicsStore } from '@/stores/epics'
import { useTicketsStore } from '@/stores/tickets'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'
import type { Epic, Subtask, Ticket, User } from '@/types'

type Priority = 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT'

const applicationsStore = useApplicationsStore()
const epicsStore = useEpicsStore()
const ticketsStore = useTicketsStore()
const authStore = useAuthStore()

const selectedAppId = ref('')
const showNewApp = ref(false)
const newAppName = ref('')
const newAppDescription = ref('')
const appError = ref('')
const editingAppId = ref<string | null>(null)
const editAppForm = ref({ name: '', description: '', isArchived: false })
const editingEpicId = ref<string | null>(null)
const editEpicForm = ref({ title: '', description: '' })
const draggedEpicId = ref<string | null>(null)
const dropTargetEpicId = ref<string | null>(null)

const canManageApplications = computed(() => authStore.isAdmin || authStore.isGroupLeader)
const activeApplications = computed(() =>
  applicationsStore.applications.filter((app) => app.isActive !== false)
)
const archivedApplications = computed(() =>
  authStore.isAdmin ? applicationsStore.applications.filter((app) => app.isActive === false) : []
)
const selectedApp = computed(() =>
  applicationsStore.applications.find((app) => app.id === selectedAppId.value) ?? null
)

const showNewEpic = ref(false)
const newEpicTitle = ref('')

const openTicketFormFor = ref<string | null>(null)
const ticketForm = ref<{ title: string; description: string; priority: Priority; dueDate: string }>({
  title: '',
  description: '',
  priority: 'MEDIUM',
  dueDate: ''
})

const epicTickets = ref<Record<string, Ticket[]>>({})
const working = ref(false)

/** Id del ticket cuyo panel de subtareas está abierto (null = ninguno) */
const openSubtasksFor = ref<string | null>(null)
/** Título de la subtarea que se está escribiendo */
const newSubtaskTitle = ref('')
/** Mensaje de error de la última acción sobre un ticket */
const ticketError = ref('')

/** Texto de la consulta/búsqueda de tickets (título o estado) */
const searchQuery = ref('')
/** Usuarios del sistema para el combo "Asignado" (GET /api/users/, solo ADMIN) */
const usersList = ref<User[]>([])
/** Ticket cuyo formulario de edición está abierto */
const editingTicketId = ref<string | null>(null)
/** Ticket cuyo panel de detalle está abierto */
const detailTicketId = ref<string | null>(null)
/** Subtarea que se está renombrando */
const editingSubtaskId = ref<string | null>(null)
const editSubtaskTitle = ref('')
/** Formulario de edición de ticket (título, desc, prioridad, fecha, PR, asignado, épica) */
const editTicketForm = ref<{
  title: string
  description: string
  priority: Priority
  dueDate: string
  prLink: string
  assigneeId: string
  epicId: string
}>({
  title: '',
  description: '',
  priority: 'MEDIUM',
  dueDate: '',
  prLink: '',
  assigneeId: '',
  epicId: ''
})

const epics = computed(() => epicsStore.epics)

const getEpicProgress = (epicId: string) => {
  const tickets = epicTickets.value[epicId] ?? []
  const total = tickets.length
  const completed = tickets.filter((ticket) => ticket.status === 'DONE' || ticket.status === 'COMPLETED').length
  const remaining = Math.max(total - completed, 0)
  const percentage = total === 0 ? 0 : Math.round((completed / total) * 100)

  return {
    total,
    completed,
    remaining,
    percentage,
    isComplete: total > 0 && completed === total
  }
}

const getEpicProgressBarClass = (percentage: number): string => {
  if (percentage >= 100) return 'bg-gradient-to-r from-emerald-500 to-green-500'
  if (percentage >= 75) return 'bg-gradient-to-r from-emerald-500 to-green-400'
  if (percentage >= 50) return 'bg-gradient-to-r from-amber-500 to-yellow-400'
  if (percentage >= 25) return 'bg-gradient-to-r from-sky-500 to-blue-500'
  return 'bg-gradient-to-r from-slate-500 to-slate-400'
}

const getEpicProgressBadgeClass = (percentage: number): string => {
  if (percentage >= 100) return 'bg-emerald-500/15 text-emerald-300 border border-emerald-400/30'
  if (percentage >= 75) return 'bg-emerald-500/10 text-emerald-300 border border-emerald-400/20'
  if (percentage >= 50) return 'bg-amber-500/10 text-amber-300 border border-amber-400/20'
  if (percentage >= 25) return 'bg-sky-500/10 text-sky-300 border border-sky-400/20'
  return 'bg-slate-500/10 text-slate-300 border border-slate-400/20'
}

const loadTicketsFor = async (epicId: string): Promise<void> => {
  epicTickets.value[epicId] = await ticketsStore.fetchByEpic(epicId)
}

const selectApplication = async (appId: string): Promise<void> => {
  selectedAppId.value = appId
  showNewEpic.value = false
  await fetchEpics()
}

const openEpicCreatorFor = (appId: string): void => {
  selectedAppId.value = appId
  showNewEpic.value = true
  newEpicTitle.value = ''
}

const fetchEpics = async (): Promise<void> => {
  if (!selectedAppId.value) {
    epicsStore.epics = []
    epicTickets.value = {}
    return
  }

  epicTickets.value = {}
  const list = await epicsStore.fetchByApp(selectedAppId.value)
  await Promise.all(list.map((epic) => loadTicketsFor(epic.id)))
}

const openAppEditor = (app: { id: string; name: string; description?: string | null; isActive?: boolean }): void => {
  appError.value = ''
  editingAppId.value = app.id
  editAppForm.value = {
    name: app.name,
    description: app.description || '',
    isArchived: app.isActive === false
  }
}

const cancelAppEdit = (): void => {
  editingAppId.value = null
  editAppForm.value = { name: '', description: '', isArchived: false }
  appError.value = ''
}

const saveAppEdits = async (app: { id: string }): Promise<void> => {
  const name = editAppForm.value.name.trim()
  if (!name) {
    appError.value = 'El nombre del proyecto no puede estar vacío.'
    return
  }

  working.value = true
  appError.value = ''

  try {
    await applicationsStore.update(app.id, {
      name,
      description: editAppForm.value.description.trim() || undefined,
      isActive: !editAppForm.value.isArchived
    })
    editingAppId.value = null
    editAppForm.value = { name: '', description: '', isArchived: false }
  } catch (err: any) {
    console.error('Error al actualizar aplicación:', err)
    if (err?.response?.status === 409) {
      appError.value = `Ya existe una aplicación con el nombre "${name}". Elige otro nombre.`
    } else {
      appError.value = err?.response?.data?.detail || 'Error al guardar los cambios del proyecto.'
    }
  } finally {
    working.value = false
  }
}

const openEpicEditor = (epic: { id: string; title: string; description?: string | null }): void => {
  appError.value = ''
  editingEpicId.value = epic.id
  editEpicForm.value = {
    title: epic.title,
    description: epic.description || ''
  }
}

const cancelEpicEdit = (): void => {
  editingEpicId.value = null
  editEpicForm.value = { title: '', description: '' }
  appError.value = ''
}

const saveEpicEdits = async (epic: { id: string }): Promise<void> => {
  const title = editEpicForm.value.title.trim()
  if (!title) {
    appError.value = 'El nombre de la épica no puede estar vacío.'
    return
  }

  working.value = true
  appError.value = ''

  try {
    await epicsStore.update(epic.id, {
      title,
      description: editEpicForm.value.description.trim() || undefined
    })
    editingEpicId.value = null
    editEpicForm.value = { title: '', description: '' }
    await fetchEpics()
  } catch (err: any) {
    console.error('Error al actualizar épica:', err)
    appError.value = err?.response?.data?.detail || 'Error al guardar los cambios de la épica.'
  } finally {
    working.value = false
  }
}

const handleEpicDragStart = (epicId: string): void => {
  draggedEpicId.value = epicId
  dropTargetEpicId.value = null
}

const handleEpicDragLeave = (epicId: string): void => {
  if (dropTargetEpicId.value === epicId) {
    dropTargetEpicId.value = null
  }
}

const handleEpicDragEnd = (): void => {
  draggedEpicId.value = null
  dropTargetEpicId.value = null
}

const handleEpicDrop = async (targetEpicId: string): Promise<void> => {
  if (!draggedEpicId.value || draggedEpicId.value === targetEpicId) {
    handleEpicDragEnd()
    return
  }

  const currentOrder = [...epics.value]
  const fromIndex = currentOrder.findIndex((epic) => epic.id === draggedEpicId.value)
  const toIndex = currentOrder.findIndex((epic) => epic.id === targetEpicId)

  if (fromIndex === -1 || toIndex === -1) {
    handleEpicDragEnd()
    return
  }

  const [moved] = currentOrder.splice(fromIndex, 1)
  currentOrder.splice(toIndex, 0, moved)

  try {
    const targetIndex = Math.max(0, Math.min(toIndex, currentOrder.length - 1))
    await epicsStore.reorder(draggedEpicId.value, targetIndex)
    handleEpicDragEnd()
  } catch (err) {
    console.error('Error al reordenar épicas:', err)
    appError.value = 'No se pudo guardar el nuevo orden de la épica.'
    handleEpicDragEnd()
  }
}

const toggleAppArchive = async (app: { id: string; isActive?: boolean }): Promise<void> => {
  try {
    working.value = true
    await applicationsStore.update(app.id, { isActive: app.isActive === false })
  } catch (err) {
    console.error('Error al cambiar el estado de archivado:', err)
    appError.value = 'No se pudo cambiar el estado del proyecto.'
  } finally {
    working.value = false
  }
}

const createApp = async (): Promise<void> => {
  working.value = true
  appError.value = ''
  try {
    const created = await api.applications.create({
      name: newAppName.value.trim(),
      description: newAppDescription.value.trim() || undefined
    })
    await applicationsStore.fetchAll()
    selectedAppId.value = created.id
    newAppName.value = ''
    newAppDescription.value = ''
    showNewApp.value = false
    await fetchEpics()
  } catch (err: any) {
    console.error('Error al crear aplicación:', err)
    if (err?.response?.status === 409) {
      appError.value = `Ya existe una aplicación con el nombre "${newAppName.value.trim()}". Por favor elige otro nombre o selecciónala en la lista.`
    } else {
      appError.value = err?.response?.data?.detail || 'Error al crear la aplicación.'
    }
  } finally {
    working.value = false
  }
}

const createEpic = async (): Promise<void> => {
  if (!newEpicTitle.value.trim()) return
  working.value = true
  try {
    await epicsStore.create({
      applicationId: selectedAppId.value,
      title: newEpicTitle.value.trim()
    })
    newEpicTitle.value = ''
    showNewEpic.value = false
    await fetchEpics()
  } catch (err) {
    console.error('Error al crear épica:', err)
  } finally {
    working.value = false
  }
}

const createTicket = async (epic: Epic): Promise<void> => {
  if (!ticketForm.value.title.trim()) return
  working.value = true
  try {
    /**
     * WEB-08: el POST /tickets/ devuelve el ticket recién creado, así que se
     * pinta de inmediato en la lista del épico (sin esperar a otro fetch).
     * Antes solo se creaba y se cerraba el formulario: el ticket aparecía
     * únicamente al recargar la página (F5).
     */
    const created = await ticketsStore.create({
      epicId: epic.id,
      title: ticketForm.value.title.trim(),
      description: ticketForm.value.description.trim() || undefined,
      priority: ticketForm.value.priority,
      dueDate: ticketForm.value.dueDate || undefined
    })
    ticketForm.value = { title: '', description: '', priority: 'MEDIUM', dueDate: '' }
    openTicketFormFor.value = null
    epicTickets.value[epic.id] = [
      created,
      ...(epicTickets.value[epic.id] ?? []).filter((t) => t.id !== created.id)
    ]
    /** Reconciliar con el servidor (estado/prioridad reales del backend) */
    await loadTicketsFor(epic.id)
  } catch (err) {
    console.error('Error al crear ticket:', err)
  } finally {
    working.value = false
  }
}

/** TODO -> IN_PROGRESS (POST /tickets/{id}/start) */
const startTicket = async (ticket: Ticket): Promise<void> => {
  working.value = true
  ticketError.value = ''
  try {
    await api.tickets.updateStatus(ticket.id, 'IN_PROGRESS')
    await loadTicketsFor(ticket.epicId)
  } catch (err: any) {
    console.error('Error al iniciar ticket:', err)
    ticketError.value = err?.response?.data?.detail || 'No se pudo iniciar el ticket.'
  } finally {
    working.value = false
  }
}

/** IN_PROGRESS -> DONE: pide el PR (opcional para admin) y finaliza */
const completeTicket = async (ticket: Ticket): Promise<void> => {
  const prLink = window.prompt(
    'Enlace del Pull Request para finalizar el ticket (un admin puede dejarlo vacío):'
  )
  if (prLink === null) return
  await finalizeTicket(ticket, prLink.trim())
}

/** Finaliza el ticket (IN_PROGRESS -> DONE, POST /tickets/{id}/complete) */
const finalizeTicket = async (ticket: Ticket, prLink: string): Promise<void> => {
  working.value = true
  ticketError.value = ''
  try {
    await api.tickets.complete(ticket.id, prLink)
    await loadTicketsFor(ticket.epicId)
  } catch (err: any) {
    console.error('Error al finalizar ticket:', err)
    ticketError.value = err?.response?.data?.detail || 'No se pudo finalizar el ticket.'
  } finally {
    working.value = false
  }
}

/** Abre o cierra el panel de subtareas de un ticket */
const toggleSubtaskPanel = (ticketId: string): void => {
  openSubtasksFor.value = openSubtasksFor.value === ticketId ? null : ticketId
  newSubtaskTitle.value = ''
  ticketError.value = ''
}

/** Crea una subtarea (POST /api/subtasks/) y refresca el ticket */
const addSubtask = async (ticket: Ticket): Promise<void> => {
  const title = newSubtaskTitle.value.trim()
  if (!title) return
  working.value = true
  ticketError.value = ''
  try {
    await api.tickets.createSubtask(ticket.id, title)
    newSubtaskTitle.value = ''
    await loadTicketsFor(ticket.epicId)
  } catch (err: any) {
    console.error('Error al crear subtarea:', err)
    ticketError.value = err?.response?.data?.detail || 'No se pudo crear la subtarea.'
  } finally {
    working.value = false
  }
}

/** Marca/desmarca una subtarea (PUT /api/subtasks/{id}) */
const toggleSubtask = async (ticket: Ticket, sub: Subtask): Promise<void> => {
  working.value = true
  ticketError.value = ''
  try {
    await api.tickets.updateSubtask(ticket.id, sub.id, { isCompleted: !sub.isCompleted })
    // Estado local tras el toggle, sin esperar al refetch
    const subs = (ticket.subtasks ?? []).map((s) =>
      s.id === sub.id ? { ...s, isCompleted: !sub.isCompleted } : s
    )
    await loadTicketsFor(ticket.epicId)

    // Todas las subtareas marcadas -> el ticket pasa a finalizado (DONE),
    // lo que además mueve el % de "por terminar" de la épica.
    const allDone = subs.length > 0 && subs.every((s) => s.isCompleted)
    if (allDone && ticket.status !== 'DONE') {
      // DONE solo se alcanza desde IN_PROGRESS: si aún estaba en TODO, se inicia.
      if (ticket.status === 'TODO') {
        await api.tickets.updateStatus(ticket.id, 'IN_PROGRESS')
      }
      // Admin puede finalizar sin PR (lo permite el backend)
      await finalizeTicket(ticket, '')
    }
  } catch (err: any) {
    console.error('Error al actualizar subtarea:', err)
    ticketError.value = err?.response?.data?.detail || 'No se pudo actualizar la subtarea.'
  } finally {
    working.value = false
  }
}

/** Elimina una subtarea (DELETE /api/subtasks/{id}) */
const removeSubtask = async (ticket: Ticket, sub: Subtask): Promise<void> => {
  working.value = true
  ticketError.value = ''
  try {
    await api.tickets.deleteSubtask(ticket.id, sub.id)
    await loadTicketsFor(ticket.epicId)
  } catch (err: any) {
    console.error('Error al eliminar subtarea:', err)
    ticketError.value = err?.response?.data?.detail || 'No se pudo eliminar la subtarea.'
  } finally {
    working.value = false
  }
}

/** Tickets visibles de una épica según la búsqueda (consulta por título/estado) */
const visibleTickets = (epicId: string): Ticket[] => {
  const list = epicTickets.value[epicId] ?? []
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return list
  return list.filter(
    (t) =>
      (t.title ?? '').toLowerCase().includes(q) ||
      statusLabel(t.status).toLowerCase().includes(q)
  )
}

/** Título de una épica por id (para el panel de detalle) */
const epicTitleFor = (epicId: string): string =>
  epics.value.find((e) => e.id === epicId)?.title ?? '—'

/** Carga (una sola vez) la lista de usuarios para el combo "Asignado" */
const loadUsers = async (): Promise<void> => {
  if (usersList.value.length) return
  try {
    const res: any = await api.users.list({ limit: 100 })
    usersList.value = Array.isArray(res) ? res : (res?.items ?? res?.data ?? [])
  } catch (err) {
    console.error('Error cargando usuarios:', err)
  }
}

/** Abre/cierra el formulario de edición del ticket (y cierra detalle) */
const openTicketEditor = async (ticket: Ticket): Promise<void> => {
  detailTicketId.value = null
  editingTicketId.value = editingTicketId.value === ticket.id ? null : ticket.id
  ticketError.value = ''
  if (!editingTicketId.value) return
  editTicketForm.value = {
    title: ticket.title ?? '',
    description: ticket.description ?? '',
    priority: (ticket.priority as Priority) ?? 'MEDIUM',
    dueDate: ticket.dueDate ? String(ticket.dueDate).slice(0, 10) : '',
    prLink: ticket.prLink ?? '',
    assigneeId: ticket.assigneeId ?? '',
    epicId: ticket.epicId
  }
  await loadUsers()
}

/** Abre/cierra el panel de detalle del ticket */
const toggleTicketDetail = (ticket: Ticket): void => {
  editingTicketId.value = null
  ticketError.value = ''
  detailTicketId.value = detailTicketId.value === ticket.id ? null : ticket.id
}

/**
 * Guarda la edición (PUT /tickets/{id}) y, si cambió la épica, mueve el ticket
 * (PATCH /tickets/{id}/move). `null` en dueDate/prLink/assigneeId limpia el
 * campo en el backend (actualización parcial con exclude_unset).
 */
const saveTicketEdits = async (ticket: Ticket): Promise<void> => {
  const f = editTicketForm.value
  if (!f.title.trim()) return
  working.value = true
  ticketError.value = ''
  try {
    await api.tickets.update(ticket.id, {
      title: f.title.trim(),
      description: f.description.trim(),
      priority: f.priority,
      dueDate: f.dueDate || null,
      prLink: f.prLink.trim() || null,
      assigneeId: f.assigneeId || null
    } as unknown as Partial<Ticket>)

    const epicChanged = !!f.epicId && f.epicId !== ticket.epicId
    if (epicChanged) {
      await api.tickets.move(ticket.id, f.epicId)
    }

    editingTicketId.value = null
    await loadTicketsFor(ticket.epicId)
    if (epicChanged) await loadTicketsFor(f.epicId)
  } catch (err: any) {
    console.error('Error al guardar ticket:', err)
    ticketError.value = err?.response?.data?.detail || 'No se pudieron guardar los cambios.'
  } finally {
    working.value = false
  }
}

/** Elimina el ticket con confirmación (DELETE /tickets/{id}) */
const deleteTicket = async (ticket: Ticket): Promise<void> => {
  if (!window.confirm(`¿Eliminar el ticket "${ticket.title}"? Esta acción no se puede deshacer.`)) {
    return
  }
  working.value = true
  ticketError.value = ''
  try {
    await api.tickets.delete(ticket.id)
    editingTicketId.value = null
    detailTicketId.value = null
    await loadTicketsFor(ticket.epicId)
  } catch (err: any) {
    console.error('Error al eliminar ticket:', err)
    ticketError.value = err?.response?.data?.detail || 'No se pudo eliminar el ticket.'
  } finally {
    working.value = false
  }
}

/** Activa el modo renombrar de una subtarea */
const startEditSubtask = (sub: Subtask): void => {
  editingSubtaskId.value = sub.id
  editSubtaskTitle.value = sub.title
  ticketError.value = ''
}

/** Guarda el nuevo nombre de la subtarea (PUT /api/subtasks/{id}) */
const saveSubtaskTitle = async (ticket: Ticket): Promise<void> => {
  const title = editSubtaskTitle.value.trim()
  if (!title || !editingSubtaskId.value) return
  working.value = true
  ticketError.value = ''
  try {
    await api.tickets.updateSubtask(ticket.id, editingSubtaskId.value, { title })
    editingSubtaskId.value = null
    await loadTicketsFor(ticket.epicId)
  } catch (err: any) {
    console.error('Error al renombrar subtarea:', err)
    ticketError.value = err?.response?.data?.detail || 'No se pudo renombrar la subtarea.'
  } finally {
    working.value = false
  }
}

const statusLabel = (status: string): string =>
  ({ TODO: 'Por hacer', IN_PROGRESS: 'En progreso', BLOCKED: 'Bloqueado', REDIRECTED: 'Redirigido', DONE: 'Hecho' })[status] ?? status

const priorityLabel = (priority: string): string =>
  ({ LOW: 'Baja', MEDIUM: 'Media', HIGH: 'Alta', URGENT: 'Urgente' })[priority] ?? priority

const statusClass = (status: string): string =>
  ({
    TODO: 'bg-slate-500/20 text-slate-300',
    IN_PROGRESS: 'bg-blue-500/20 text-blue-300',
    BLOCKED: 'bg-red-500/20 text-red-300',
    REDIRECTED: 'bg-amber-500/20 text-amber-300',
    DONE: 'bg-emerald-500/20 text-emerald-300'
  })[status] ?? 'bg-slate-500/20 text-slate-300'

const priorityClass = (priority: string): string =>
  ({
    LOW: 'bg-slate-500/20 text-slate-300',
    MEDIUM: 'bg-yellow-500/20 text-yellow-300',
    HIGH: 'bg-orange-500/20 text-orange-300',
    URGENT: 'bg-red-500/20 text-red-300'
  })[priority] ?? 'bg-slate-500/20 text-slate-300'

onMounted(async () => {
  try {
    await applicationsStore.fetchAll()
    const firstActiveApp = activeApplications.value[0]
    if (firstActiveApp) {
      selectedAppId.value = firstActiveApp.id
      await fetchEpics()
    }
  } catch (err) {
    console.error('Error cargando datos del builder:', err)
  }
})
</script>

