<script setup lang="ts">
/**
 * @file components/incidents/CreateIncidentModal.vue
 * @description Modal para crear un nuevo incidente.
 * Proporciona un formulario completo con validación, categorías, severidades,
 * asignaciones y campos técnicos opcionales.
 */

import { ref, computed, watch } from 'vue';
import { useIncidentsStore } from '@/stores/incidents';
import { IncidentCategory, IncidentSeverity, type CreateIncidentPayload } from '@/types/incidents';
import type { User } from '@/types/incidents';

// ==================== PROPS & EMITS ====================

/**
 * Props del componente.
 */
const props = withDefaults(
  defineProps<{
    // Indica si el modal está abierto o cerrado
    isOpen: boolean;
    // ID de aplicación pre-seleccionada (opcional)
    applicationId?: string;
  }>(),
  {
    isOpen: false,
    applicationId: undefined,
  }
);

/**
 * Eventos que emite el componente.
 */
const emit = defineEmits<{
  // Se emite cuando el usuario cierra el modal
  close: [];
  // Se emite cuando un incidente se crea exitosamente
  created: [incident: any];
}>();

// ==================== STORES ====================

const incidentsStore = useIncidentsStore();

// ==================== REACTIVE STATE ====================

/**
 * Título del incidente.
 * Campo obligatorio con validación de longitud mínima.
 */
const title = ref('');

/**
 * Descripción completa del incidente.
 * Campo obligatorio con validación de longitud mínima.
 */
const description = ref('');

/**
 * ID de la aplicación afectada.
 * Campo obligatorio.
 */
const selectedAppId = ref<string>(props.applicationId || '');

/**
 * Categoría seleccionada del incidente.
 * Determina el tipo de problema.
 */
const selectedCategory = ref<IncidentCategory>(IncidentCategory.CRITICAL_ERROR);

/**
 * Severidad seleccionada.
 * Indica el impacto del incidente.
 */
const selectedSeverity = ref<IncidentSeverity>(IncidentSeverity.MEDIUM);

/**
 * ID del usuario a asignar.
 * Campo opcional.
 */
const selectedAssigneeId = ref<string>('');

/**
 * Fecha de vencimiento.
 * Campo opcional en formato ISO.
 */
const dueDate = ref<string>('');

/**
 * Entorno afectado (ej: Production, Staging, Development).
 * Campo opcional.
 */
const environment = ref<string>('');

/**
 * Pasos para reproducir el incidente.
 * Campo técnico opcional.
 */
const stepsToReproduce = ref<string>('');

/**
 * Comportamiento esperado.
 * Campo técnico opcional.
 */
const expectedBehavior = ref<string>('');

/**
 * Comportamiento actual/observado.
 * Campo técnico opcional.
 */
const actualBehavior = ref<string>('');

/**
 * Indica si la sección de detalles técnicos está expandida.
 */
const showDetailsSection = ref(false);

/**
 * Lista de aplicaciones disponibles.
 * Se cargaría desde el store de aplicaciones.
 * TODO: Conectar con store de aplicaciones
 */
const applications = ref<Array<{ id: string; name: string }>>([]);

/**
 * Lista de usuarios para asignación.
 * Se cargaría desde el store de equipo/usuarios.
 * TODO: Conectar con store de usuarios
 */
const teamMembers = ref<User[]>([]);

/**
 * Términos de búsqueda en el dropdown de asignees.
 */
const assigneeSearchTerm = ref<string>('');

/**
 * Errores de validación por campo.
 */
const validationErrors = ref<Record<string, string>>({});

/**
 * Indica si el formulario se está enviando.
 */
const isSubmitting = ref(false);

// ==================== COMPUTED ====================

/**
 * Miembros del equipo filtrados por término de búsqueda.
 */
const filteredTeamMembers = computed(() => {
  if (!assigneeSearchTerm.value) return teamMembers.value;

  const searchLower = assigneeSearchTerm.value.toLowerCase();
  return teamMembers.value.filter(
    (member) =>
      member.name.toLowerCase().includes(searchLower) ||
      member.email.toLowerCase().includes(searchLower)
  );
});

/**
 * Nombre de la aplicación seleccionada.
 */
const selectedAppName = computed(() => {
  const app = applications.value.find((a) => a.id === selectedAppId.value);
  return app?.name || '';
});

/**
 * Usuario asignado actualmente seleccionado.
 */
const selectedAssignee = computed(() => {
  if (!selectedAssigneeId.value) return null;
  return teamMembers.value.find((m) => m.id === selectedAssigneeId.value) || null;
});

/**
 * Determina si el formulario es válido.
 */
const isFormValid = computed(() => {
  return (
    title.value.trim().length >= 5 &&
    description.value.trim().length >= 10 &&
    selectedAppId.value.length > 0 &&
    Object.keys(validationErrors.value).length === 0
  );
});

// ==================== WATCHERS ====================

/**
 * Monitorea cambios en la prop isOpen para resetear el formulario.
 */
watch(
  () => props.isOpen,
  (newVal) => {
    if (newVal) {
      loadApplications();
      loadTeamMembers();
      selectedAppId.value = props.applicationId || '';
    } else {
      resetForm();
    }
  }
);

/**
 * Monitorea cambios en el título para validar.
 */
watch(
  () => title.value,
  (newVal) => {
    if (newVal.trim().length < 5 && newVal.length > 0) {
      validationErrors.value.title = 'El título debe tener al menos 5 caracteres';
    } else {
      delete validationErrors.value.title;
    }
  }
);

/**
 * Monitorea cambios en la descripción para validar.
 */
watch(
  () => description.value,
  (newVal) => {
    if (newVal.trim().length < 10 && newVal.length > 0) {
      validationErrors.value.description = 'La descripción debe tener al menos 10 caracteres';
    } else {
      delete validationErrors.value.description;
    }
  }
);

// ==================== METHODS ====================

/**
 * Carga la lista de aplicaciones disponibles.
 * TODO: Implementar con llamada a API/store real.
 */
const loadApplications = async () => {
  try {
    // TODO: Reemplazar con llamada real
    // const appStore = useApplicationsStore();
    // await appStore.fetchAll();
    // applications.value = appStore.applications;

    // Datos de ejemplo
    applications.value = [
      { id: '1', name: 'CoreStream Dashboard' },
      { id: '2', name: 'User Portal' },
      { id: '3', name: 'API Gateway' },
    ];
  } catch (error) {
    console.error('Error loading applications:', error);
  }
};

/**
 * Carga la lista de miembros del equipo disponibles.
 * TODO: Implementar con llamada a API/store real.
 */
const loadTeamMembers = async () => {
  try {
    // TODO: Reemplazar con llamada real
    // const userStore = useUsersStore();
    // await userStore.fetchTeamMembers();
    // teamMembers.value = userStore.teamMembers;

    // Datos de ejemplo
    teamMembers.value = [
      {
        id: 'user1',
        name: 'Carlos Rodríguez',
        email: 'carlos@example.com',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=carlos',
      },
      {
        id: 'user2',
        name: 'María López',
        email: 'maria@example.com',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=maria',
      },
      {
        id: 'user3',
        name: 'Juan García',
        email: 'juan@example.com',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=juan',
      },
    ];
  } catch (error) {
    console.error('Error loading team members:', error);
  }
};

/**
 * Valida el formulario completo.
 * @returns true si el formulario es válido
 */
const validateForm = (): boolean => {
  validationErrors.value = {};

  if (title.value.trim().length < 5) {
    validationErrors.value.title = 'El título debe tener al menos 5 caracteres';
  }

  if (description.value.trim().length < 10) {
    validationErrors.value.description = 'La descripción debe tener al menos 10 caracteres';
  }

  if (!selectedAppId.value) {
    validationErrors.value.applicationId = 'Debe seleccionar una aplicación';
  }

  return Object.keys(validationErrors.value).length === 0;
};

/**
 * Maneja el envío del formulario.
 * Valida, crea el incidente y emite el evento correspondiente.
 */
const handleSubmit = async () => {
  if (!validateForm()) {
    return;
  }

  isSubmitting.value = true;

  try {
    const payload: CreateIncidentPayload = {
      title: title.value.trim(),
      description: description.value.trim(),
      applicationId: selectedAppId.value,
      category: selectedCategory.value,
      severity: selectedSeverity.value,
      assigneeId: selectedAssigneeId.value || undefined,
      dueDate: dueDate.value || undefined,
      environment: environment.value || undefined,
      stepsToReproduce: stepsToReproduce.value || undefined,
      expectedBehavior: expectedBehavior.value || undefined,
      actualBehavior: actualBehavior.value || undefined,
    };

    const createdIncident = await incidentsStore.create(payload);

    if (createdIncident) {
      emit('created', createdIncident);
      resetForm();
      emit('close');
    } else {
      validationErrors.value.submit = 'Error al crear el incidente';
    }
  } catch (error: any) {
    validationErrors.value.submit = error.message || 'Error inesperado';
  } finally {
    isSubmitting.value = false;
  }
};

/**
 * Resetea el formulario a su estado inicial.
 */
const resetForm = () => {
  title.value = '';
  description.value = '';
  selectedAppId.value = props.applicationId || '';
  selectedCategory.value = IncidentCategory.CRITICAL_ERROR;
  selectedSeverity.value = IncidentSeverity.MEDIUM;
  selectedAssigneeId.value = '';
  dueDate.value = '';
  environment.value = '';
  stepsToReproduce.value = '';
  expectedBehavior.value = '';
  actualBehavior.value = '';
  assigneeSearchTerm.value = '';
  showDetailsSection.value = false;
  validationErrors.value = {};
};

/**
 * Cierra el modal.
 */
const handleClose = () => {
  resetForm();
  emit('close');
};

/**
 * Retorna la clase de color para un ícono de categoría.
 * @param category - Categoría del incidente
 */
const getCategoryColorClass = (category: IncidentCategory): string => {
  const colors: Record<IncidentCategory, string> = {
    [IncidentCategory.NEW_FEATURE]: 'text-blue-500',
    [IncidentCategory.CRITICAL_ERROR]: 'text-red-500',
    [IncidentCategory.NON_CRITICAL_ERROR]: 'text-orange-500',
    [IncidentCategory.USABILITY_ISSUE]: 'text-purple-500',
  };
  return colors[category];
};

/**
 * Retorna la clase de fondo para un botón de severidad.
 * @param severity - Severidad a verificar
 */
const getSeverityButtonClass = (severity: IncidentSeverity): string => {
  const isSelected = selectedSeverity.value === severity;
  const baseClass = 'px-4 py-2 rounded-lg font-medium transition-all';

  if (!isSelected) {
    return `${baseClass} bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600`;
  }

  const colors: Record<IncidentSeverity, string> = {
    [IncidentSeverity.CRITICAL]: 'bg-red-500 text-white',
    [IncidentSeverity.HIGH]: 'bg-orange-500 text-white',
    [IncidentSeverity.MEDIUM]: 'bg-yellow-500 text-white',
    [IncidentSeverity.LOW]: 'bg-green-500 text-white',
  };

  return `${baseClass} ${colors[severity]}`;
};
</script>

<template>
  <!-- Modal overlay -->
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 overflow-y-auto bg-black bg-opacity-50 transition-all"
        @click.self="handleClose"
      >
        <!-- Modal content -->
        <div class="flex min-h-screen items-center justify-center px-4 py-8">
          <Transition name="slide-up">
            <div
              v-if="isOpen"
              class="w-full max-w-2xl space-y-6 rounded-xl bg-white p-8 shadow-2xl dark:bg-gray-800"
              @click.stop
            >
              <!-- Header -->
              <div class="flex items-center justify-between">
                <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
                  {{ $t('incidents.create.title', 'Crear Nuevo Incidente') }}
                </h2>
                <button
                  @click="handleClose"
                  class="rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <svg
                    class="h-6 w-6 text-gray-500 dark:text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <!-- Form -->
              <form @submit.prevent="handleSubmit" class="space-y-6">
                <!-- Título -->
                <div>
                  <label for="title" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {{ $t('incidents.create.title', 'Título') }} *
                  </label>
                  <input
                    id="title"
                    v-model="title"
                    type="text"
                    placeholder="Describe el incidente brevemente"
                    class="mt-2 w-full rounded-lg border border-gray-300 px-4 py-2 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
                    minlength="5"
                    required
                  />
                  <p v-if="validationErrors.title" class="mt-1 text-sm text-red-500">
                    {{ validationErrors.title }}
                  </p>
                </div>

                <!-- Descripción -->
                <div>
                  <label for="description" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {{ $t('incidents.create.description', 'Descripción') }} *
                  </label>
                  <textarea
                    id="description"
                    v-model="description"
                    placeholder="Proporciona una descripción detallada del incidente"
                    rows="4"
                    class="mt-2 w-full rounded-lg border border-gray-300 px-4 py-2 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
                    minlength="10"
                    required
                  />
                  <p v-if="validationErrors.description" class="mt-1 text-sm text-red-500">
                    {{ validationErrors.description }}
                  </p>
                </div>

                <!-- Aplicación -->
                <div>
                  <label for="application" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {{ $t('incidents.create.application', 'Aplicación') }} *
                  </label>
                  <select
                    id="application"
                    v-model="selectedAppId"
                    class="mt-2 w-full rounded-lg border border-gray-300 px-4 py-2 text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                    required
                  >
                    <option value="" disabled>Selecciona una aplicación</option>
                    <option v-for="app in applications" :key="app.id" :value="app.id">
                      {{ app.name }}
                    </option>
                  </select>
                  <p v-if="validationErrors.applicationId" class="mt-1 text-sm text-red-500">
                    {{ validationErrors.applicationId }}
                  </p>
                </div>

                <!-- Categoría -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {{ $t('incidents.create.category', 'Categoría') }} *
                  </label>
                  <div class="mt-3 grid grid-cols-2 gap-3">
                    <!-- Nueva Funcionalidad -->
                    <label
                      class="flex cursor-pointer items-center rounded-lg border-2 p-4 transition-all"
                      :class="
                        selectedCategory === IncidentCategory.NEW_FEATURE
                          ? 'border-blue-500 bg-blue-50 dark:border-blue-500 dark:bg-blue-900'
                          : 'border-gray-300 dark:border-gray-600'
                      "
                    >
                      <input
                        type="radio"
                        :value="IncidentCategory.NEW_FEATURE"
                        v-model="selectedCategory"
                        class="h-4 w-4"
                      />
                      <span class="ml-3 flex items-center space-x-2">
                        <svg
                          class="h-5 w-5 text-blue-500"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                          />
                        </svg>
                        <span class="text-sm font-medium">{{ $t('incidents.category.new_feature', 'Nueva Funcionalidad') }}</span>
                      </span>
                    </label>

                    <!-- Error Crítico -->
                    <label
                      class="flex cursor-pointer items-center rounded-lg border-2 p-4 transition-all"
                      :class="
                        selectedCategory === IncidentCategory.CRITICAL_ERROR
                          ? 'border-red-500 bg-red-50 dark:border-red-500 dark:bg-red-900'
                          : 'border-gray-300 dark:border-gray-600'
                      "
                    >
                      <input
                        type="radio"
                        :value="IncidentCategory.CRITICAL_ERROR"
                        v-model="selectedCategory"
                        class="h-4 w-4"
                      />
                      <span class="ml-3 flex items-center space-x-2">
                        <svg
                          class="h-5 w-5 text-red-500"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fill-rule="evenodd"
                            d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                            clip-rule="evenodd"
                          />
                        </svg>
                        <span class="text-sm font-medium">{{ $t('incidents.category.critical_error', 'Error Crítico') }}</span>
                      </span>
                    </label>

                    <!-- Error No Crítico -->
                    <label
                      class="flex cursor-pointer items-center rounded-lg border-2 p-4 transition-all"
                      :class="
                        selectedCategory === IncidentCategory.NON_CRITICAL_ERROR
                          ? 'border-orange-500 bg-orange-50 dark:border-orange-500 dark:bg-orange-900'
                          : 'border-gray-300 dark:border-gray-600'
                      "
                    >
                      <input
                        type="radio"
                        :value="IncidentCategory.NON_CRITICAL_ERROR"
                        v-model="selectedCategory"
                        class="h-4 w-4"
                      />
                      <span class="ml-3 flex items-center space-x-2">
                        <svg
                          class="h-5 w-5 text-orange-500"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fill-rule="evenodd"
                            d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                            clip-rule="evenodd"
                          />
                        </svg>
                        <span class="text-sm font-medium">{{ $t('incidents.category.non_critical_error', 'Error No Crítico') }}</span>
                      </span>
                    </label>

                    <!-- Problema de Usabilidad -->
                    <label
                      class="flex cursor-pointer items-center rounded-lg border-2 p-4 transition-all"
                      :class="
                        selectedCategory === IncidentCategory.USABILITY_ISSUE
                          ? 'border-purple-500 bg-purple-50 dark:border-purple-500 dark:bg-purple-900'
                          : 'border-gray-300 dark:border-gray-600'
                      "
                    >
                      <input
                        type="radio"
                        :value="IncidentCategory.USABILITY_ISSUE"
                        v-model="selectedCategory"
                        class="h-4 w-4"
                      />
                      <span class="ml-3 flex items-center space-x-2">
                        <svg
                          class="h-5 w-5 text-purple-500"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                          <path
                            fill-rule="evenodd"
                            d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z"
                            clip-rule="evenodd"
                          />
                        </svg>
                        <span class="text-sm font-medium">{{ $t('incidents.category.usability_issue', 'Problema de Usabilidad') }}</span>
                      </span>
                    </label>
                  </div>
                </div>

                <!-- Severidad -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {{ $t('incidents.create.severity', 'Severidad') }} *
                  </label>
                  <div class="mt-3 flex flex-wrap gap-2">
                    <button
                      v-for="severity in Object.values(IncidentSeverity)"
                      :key="severity"
                      type="button"
                      @click="selectedSeverity = severity"
                      :class="getSeverityButtonClass(severity)"
                    >
                      {{ $t(`incidents.severity.${severity.toLowerCase()}`, severity) }}
                    </button>
                  </div>
                </div>

                <!-- Asignado a -->
                <div>
                  <label for="assignee" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {{ $t('incidents.create.assignee', 'Asignar a') }}
                  </label>
                  <div class="relative mt-2">
                    <div
                      class="flex cursor-pointer items-center rounded-lg border border-gray-300 bg-white px-4 py-2 dark:border-gray-600 dark:bg-gray-700"
                      @click="$refs.assigneeDropdown?.toggleOpen?.()"
                    >
                      <input
                        v-model="assigneeSearchTerm"
                        type="text"
                        placeholder="Buscar desarrollador..."
                        class="flex-1 bg-transparent text-gray-900 placeholder-gray-500 focus:outline-none dark:text-white dark:placeholder-gray-400"
                      />
                      <svg
                        class="h-5 w-5 text-gray-400"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </div>

                    <!-- Dropdown de asignees -->
                    <div
                      v-if="assigneeSearchTerm"
                      class="absolute top-full mt-1 max-h-48 w-full overflow-y-auto rounded-lg border border-gray-300 bg-white shadow-lg dark:border-gray-600 dark:bg-gray-700"
                    >
                      <button
                        v-if="selectedAssigneeId"
                        type="button"
                        @click="selectedAssigneeId = ''; assigneeSearchTerm = ''"
                        class="block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-600"
                      >
                        Limpiar selección
                      </button>

                      <button
                        v-for="member in filteredTeamMembers"
                        :key="member.id"
                        type="button"
                        @click="selectedAssigneeId = member.id; assigneeSearchTerm = ''"
                        class="flex w-full items-center space-x-3 border-t border-gray-200 px-4 py-2 text-left hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-600"
                      >
                        <img
                          :src="member.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${member.id}`"
                          :alt="member.name"
                          class="h-8 w-8 rounded-full"
                        />
                        <div class="flex-1">
                          <p class="text-sm font-medium text-gray-900 dark:text-white">{{ member.name }}</p>
                          <p class="text-xs text-gray-500 dark:text-gray-400">{{ member.email }}</p>
                        </div>
                      </button>
                    </div>
                  </div>

                  <!-- Asignado actual -->
                  <div v-if="selectedAssignee" class="mt-2 flex items-center space-x-2 rounded-lg bg-blue-50 px-3 py-2 dark:bg-blue-900">
                    <img
                      :src="selectedAssignee.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${selectedAssignee.id}`"
                      :alt="selectedAssignee.name"
                      class="h-6 w-6 rounded-full"
                    />
                    <span class="text-sm text-gray-900 dark:text-white">{{ selectedAssignee.name }}</span>
                    <button
                      type="button"
                      @click="selectedAssigneeId = ''"
                      class="ml-auto text-blue-600 hover:text-blue-700 dark:text-blue-400"
                    >
                      ×
                    </button>
                  </div>
                </div>

                <!-- Fecha de vencimiento -->
                <div>
                  <label for="dueDate" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {{ $t('incidents.create.dueDate', 'Fecha de Vencimiento') }}
                  </label>
                  <input
                    id="dueDate"
                    v-model="dueDate"
                    type="date"
                    class="mt-2 w-full rounded-lg border border-gray-300 px-4 py-2 text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  />
                </div>

                <!-- Entorno -->
                <div>
                  <label for="environment" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {{ $t('incidents.create.environment', 'Entorno') }}
                  </label>
                  <input
                    id="environment"
                    v-model="environment"
                    type="text"
                    placeholder="ej: Production, Staging, Development"
                    class="mt-2 w-full rounded-lg border border-gray-300 px-4 py-2 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
                  />
                </div>

                <!-- Sección de detalles técnicos (colapsable) -->
                <div class="border-t border-gray-200 pt-4 dark:border-gray-700">
                  <button
                    type="button"
                    @click="showDetailsSection = !showDetailsSection"
                    class="flex items-center space-x-2 text-sm font-medium text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
                  >
                    <svg
                      class="h-5 w-5 transition-transform"
                      :class="{ 'rotate-90': showDetailsSection }"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                    </svg>
                    <span>{{ $t('incidents.create.technicalDetails', 'Detalles Técnicos') }}</span>
                  </button>

                  <!-- Detalles técnicos expandidos -->
                  <div
                    v-if="showDetailsSection"
                    class="mt-4 space-y-4"
                  >
                    <!-- Pasos para reproducir -->
                    <div>
                      <label for="stepsToReproduce" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        {{ $t('incidents.create.stepsToReproduce', 'Pasos para Reproducir') }}
                      </label>
                      <textarea
                        id="stepsToReproduce"
                        v-model="stepsToReproduce"
                        placeholder="1. Hacer clic en...\n2. Luego...\n3. Observar..."
                        rows="3"
                        class="mt-2 w-full rounded-lg border border-gray-300 px-4 py-2 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
                      />
                    </div>

                    <!-- Comportamiento esperado -->
                    <div>
                      <label for="expectedBehavior" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        {{ $t('incidents.create.expectedBehavior', 'Comportamiento Esperado') }}
                      </label>
                      <textarea
                        id="expectedBehavior"
                        v-model="expectedBehavior"
                        placeholder="Describe qué debería suceder..."
                        rows="3"
                        class="mt-2 w-full rounded-lg border border-gray-300 px-4 py-2 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
                      />
                    </div>

                    <!-- Comportamiento actual -->
                    <div>
                      <label for="actualBehavior" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        {{ $t('incidents.create.actualBehavior', 'Comportamiento Actual') }}
                      </label>
                      <textarea
                        id="actualBehavior"
                        v-model="actualBehavior"
                        placeholder="Describe qué está sucediendo actualmente..."
                        rows="3"
                        class="mt-2 w-full rounded-lg border border-gray-300 px-4 py-2 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
                      />
                    </div>
                  </div>
                </div>

                <!-- Error de envío -->
                <div v-if="validationErrors.submit" class="rounded-lg bg-red-50 p-4 dark:bg-red-900">
                  <p class="text-sm text-red-700 dark:text-red-200">{{ validationErrors.submit }}</p>
                </div>

                <!-- Botones -->
                <div class="flex justify-end space-x-3 border-t border-gray-200 pt-6 dark:border-gray-700">
                  <button
                    type="button"
                    @click="handleClose"
                    class="rounded-lg border border-gray-300 px-4 py-2 font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
                  >
                    {{ $t('common.cancel', 'Cancelar') }}
                  </button>
                  <button
                    type="submit"
                    :disabled="!isFormValid || isSubmitting"
                    class="rounded-lg bg-blue-600 px-6 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-blue-700 dark:hover:bg-blue-600"
                  >
                    {{ isSubmitting ? $t('common.creating', 'Creando...') : $t('incidents.create.createButton', 'Crear Incidente') }}
                  </button>
                </div>
              </form>
            </div>
          </Transition>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
/* Transiciones del modal */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(20px);
  opacity: 0;
}
</style>
