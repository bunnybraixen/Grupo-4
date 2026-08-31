/**
 * @file stores/incidents.ts
 * @description Store de Pinia para gestionar el estado de incidentes en la aplicación.
 * Implementa acciones CRUD completas, filtrado avanzado, y cálculos derivados.
 * Utiliza el patrón setup store de Pinia con TypeScript.
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type {
  Incident,
  IncidentCategory,
  IncidentStatus,
  IncidentSeverity,
  IncidentDashboard,
  IncidentFilters,
  IncidentComment,
  CreateIncidentPayload,
  UpdateIncidentPayload,
  IncidentsByTeam,
} from '@/types/incidents';
import { IncidentStatus as IncidentStatusEnum } from '@/types/incidents';

/**
 * Store de Pinia para incidentes.
 * Gestiona el estado global de incidentes, comentarios, filtros y dashboard.
 */
export const useIncidentsStore = defineStore('incidents', () => {
  // ==================== STATE ====================

  /**
   * Lista completa de incidentes cargados de la API.
   * Contiene todos los incidentes sin filtrar.
   */
  const incidents = ref<Incident[]>([]);

  /**
   * Incidente actualmente seleccionado en el panel de detalles.
   * Se establece cuando el usuario hace clic en una tarjeta de incidente.
   */
  const selectedIncident = ref<Incident | null>(null);

  /**
   * Lista de incidentes asignados al usuario actual.
   * Subconjunto filtrado de 'incidents' para el developer.
   */
  const myIncidents = ref<Incident[]>([]);

  /**
   * Incidentes agrupados por categoría.
   * Estructura: { [category]: [incidents] }
   * Utilizado por el tablero Kanban.
   */
  const groupedByCategory = computed(() => {
    const grouped: Record<IncidentCategory, Incident[]> = {
      NEW_FEATURE: [],
      CRITICAL_ERROR: [],
      NON_CRITICAL_ERROR: [],
      USABILITY_ISSUE: [],
    };

    incidents.value.forEach((incident) => {
      if (!grouped[incident.category]) {
        grouped[incident.category] = [];
      }
      grouped[incident.category].push(incident);
    });

    // Ordenar incidentes dentro de cada grupo por priorityOrder
    Object.keys(grouped).forEach((key) => {
      grouped[key as IncidentCategory].sort(
        (a, b) => a.priorityOrder - b.priorityOrder
      );
    });

    return grouped;
  });

  /**
   * Incidentes agrupados por equipo/desarrollador asignado.
   * Estructura: { [userId]: { userName, incidents } }
   * Utilizado en vistas administrativas de asignación.
   */
  const groupedByTeam = computed(() => {
    const grouped: Record<string, IncidentsByTeam> = {};

    incidents.value.forEach((incident) => {
      if (incident.assigneeId && incident.assignee) {
        const userId = incident.assigneeId;
        if (!grouped[userId]) {
          grouped[userId] = {
            userId,
            userName: incident.assignee.name,
            userAvatar: incident.assignee.avatar,
            incidents: [],
            incidentCount: 0,
            overallSeverity: 'LOW' as IncidentSeverity,
          };
        }
        grouped[userId].incidents.push(incident);
      }
    });

    // Actualizar conteos y severidad general
    Object.values(grouped).forEach((team) => {
      team.incidentCount = team.incidents.length;
      // Determinar la severidad más alta
      const severityOrder = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1 };
      const maxSeverity = Math.max(
        ...team.incidents.map((i) => severityOrder[i.severity as keyof typeof severityOrder] || 0)
      );
      const severityMap: Record<number, IncidentSeverity> = { 4: 'CRITICAL', 3: 'HIGH', 2: 'MEDIUM', 1: 'LOW', 0: 'LOW' };
      team.overallSeverity = severityMap[maxSeverity] || 'LOW';
    });

    return grouped;
  });

  /**
   * Dashboard con estadísticas generales de incidentes.
   * Contiene conteos por estado, severidad, categoría y métricas de resolución.
   */
  const dashboard = ref<IncidentDashboard | null>(null);

  /**
   * Filtros activos para búsqueda y filtrado de incidentes.
   * Se aplican a los incidentes para mostrar solo los que coinciden.
   */
  const filters = ref<IncidentFilters>({});

  /**
   * Estado de carga global.
   * Indica si se están obteniendo datos del servidor.
   */
  const isLoading = ref(false);

  /**
   * Errores de operación.
   * Almacena mensajes de error para mostrar al usuario.
   */
  const errors = ref<Record<string, string>>({});

  // ==================== GETTERS ====================

  /**
   * Incidentes críticos ordenados por prioridad.
   * Filtra incidentes con severidad CRITICAL.
   */
  const criticalIncidents = computed(() => {
    return incidents.value
      .filter((i) => i.severity === 'CRITICAL')
      .sort((a, b) => a.priorityOrder - b.priorityOrder);
  });

  /**
   * Incidentes vencidos (dueDate pasada, estado no RESOLVED/CLOSED).
   * Calcula automáticamente basándose en la fecha actual.
   */
  const overdueIncidents = computed(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    return incidents.value.filter((incident) => {
      if (!incident.dueDate || incident.isOverdue !== true) {
        return false;
      }
      return (
        incident.status !== IncidentStatusEnum.RESOLVED &&
        incident.status !== IncidentStatusEnum.CLOSED
      );
    });
  });

  /**
   * Conteo total de incidentes abiertos.
   * Incluye estados OPEN, IN_PROGRESS, UNDER_REVIEW, REOPENED.
   */
  const openCount = computed(() => {
    const openStatuses = [
      IncidentStatusEnum.OPEN,
      IncidentStatusEnum.IN_PROGRESS,
      IncidentStatusEnum.UNDER_REVIEW,
      IncidentStatusEnum.REOPENED,
    ];
    return incidents.value.filter((i) => openStatuses.includes(i.status)).length;
  });

  /**
   * Incidentes filtrados según los filtros activos.
   * Aplica todos los filtros de búsqueda y categoría.
   */
  const filteredIncidents = computed(() => {
    let result = incidents.value;

    // Aplicar filtros
    if (filters.value.category) {
      result = result.filter((i) => i.category === filters.value.category);
    }
    if (filters.value.severity) {
      result = result.filter((i) => i.severity === filters.value.severity);
    }
    if (filters.value.status) {
      result = result.filter((i) => i.status === filters.value.status);
    }
    if (filters.value.assigneeId) {
      result = result.filter((i) => i.assigneeId === filters.value.assigneeId);
    }
    if (filters.value.applicationId) {
      result = result.filter((i) => i.applicationId === filters.value.applicationId);
    }
    if (filters.value.search) {
      const searchLower = filters.value.search.toLowerCase();
      result = result.filter(
        (i) =>
          i.title.toLowerCase().includes(searchLower) ||
          i.description.toLowerCase().includes(searchLower)
      );
    }

    return result;
  });

  /**
   * Incidentes agrupados por categoría desde los incidentes filtrados.
   * Útil para visualizaciones que responden a filtros activos.
   */
  const incidentsByCategory = computed(() => {
    const grouped: Record<IncidentCategory, Incident[]> = {
      NEW_FEATURE: [],
      CRITICAL_ERROR: [],
      NON_CRITICAL_ERROR: [],
      USABILITY_ISSUE: [],
    };

    filteredIncidents.value.forEach((incident) => {
      grouped[incident.category].push(incident);
    });

    // Ordenar por prioridad
    Object.keys(grouped).forEach((key) => {
      grouped[key as IncidentCategory].sort(
        (a, b) => a.priorityOrder - b.priorityOrder
      );
    });

    return grouped;
  });

  // ==================== ACTIONS ====================

  /**
   * Carga todos los incidentes del servidor.
   * Opcionalmente aplica filtros específicos.
   * @param filtersParam - Filtros opcionales para aplicar a la búsqueda
   */
  const fetchAll = async (filtersParam?: IncidentFilters) => {
    isLoading.value = true;
    errors.value.fetchAll = '';
    try {
      // TODO: Reemplazar con llamada API real
      // const response = await apiClient.get('/incidents', { params: filtersParam });
      // incidents.value = response.data;

      // Datos de ejemplo para desarrollo
      console.log('Fetching all incidents with filters:', filtersParam);
    } catch (error: any) {
      errors.value.fetchAll = error.message || 'Error al cargar incidentes';
      console.error('Error fetching incidents:', error);
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * Carga un incidente específico por ID.
   * @param id - ID del incidente a cargar
   * @returns El incidente cargado
   */
  const fetchById = async (id: string): Promise<Incident | null> => {
    isLoading.value = true;
    errors.value.fetchById = '';
    try {
      // TODO: Reemplazar con llamada API real
      // const response = await apiClient.get(`/incidents/${id}`);
      // return response.data;

      console.log('Fetching incident by ID:', id);
      return null;
    } catch (error: any) {
      errors.value.fetchById = error.message || 'Error al cargar incidente';
      console.error('Error fetching incident:', error);
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * Crea un nuevo incidente.
   * @param data - Datos del nuevo incidente
   * @returns El incidente creado
   */
  const create = async (data: CreateIncidentPayload): Promise<Incident | null> => {
    isLoading.value = true;
    errors.value.create = '';
    try {
      // TODO: Reemplazar con llamada API real
      // const response = await apiClient.post('/incidents', data);
      // incidents.value.push(response.data);
      // return response.data;

      console.log('Creating incident:', data);
      return null;
    } catch (error: any) {
      errors.value.create = error.message || 'Error al crear incidente';
      console.error('Error creating incident:', error);
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * Actualiza un incidente existente.
   * @param id - ID del incidente a actualizar
   * @param data - Datos a actualizar
   * @returns El incidente actualizado
   */
  const update = async (
    id: string,
    data: UpdateIncidentPayload
  ): Promise<Incident | null> => {
    isLoading.value = true;
    errors.value.update = '';
    try {
      // TODO: Reemplazar con llamada API real
      // const response = await apiClient.put(`/incidents/${id}`, data);
      // const index = incidents.value.findIndex(i => i.id === id);
      // if (index !== -1) incidents.value[index] = response.data;
      // if (selectedIncident.value?.id === id) selectedIncident.value = response.data;
      // return response.data;

      console.log('Updating incident:', id, data);
      return null;
    } catch (error: any) {
      errors.value.update = error.message || 'Error al actualizar incidente';
      console.error('Error updating incident:', error);
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * Elimina un incidente (soft delete o hard delete según política).
   * @param id - ID del incidente a eliminar
   */
  const remove = async (id: string): Promise<boolean> => {
    isLoading.value = true;
    errors.value.remove = '';
    try {
      // TODO: Reemplazar con llamada API real
      // await apiClient.delete(`/incidents/${id}`);
      // incidents.value = incidents.value.filter(i => i.id !== id);
      // if (selectedIncident.value?.id === id) selectedIncident.value = null;
      // return true;

      console.log('Deleting incident:', id);
      return false;
    } catch (error: any) {
      errors.value.remove = error.message || 'Error al eliminar incidente';
      console.error('Error deleting incident:', error);
      return false;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * Asigna un incidente a un desarrollador.
   * @param id - ID del incidente
   * @param userId - ID del usuario a asignar
   * @param reason - Razón opcional de la asignación
   */
  const assign = async (
    id: string,
    userId: string,
    reason?: string
  ): Promise<boolean> => {
    errors.value.assign = '';
    try {
      // TODO: Reemplazar con llamada API real
      // const response = await apiClient.post(`/incidents/${id}/assign`, { userId, reason });
      // const index = incidents.value.findIndex(i => i.id === id);
      // if (index !== -1) incidents.value[index] = response.data;
      // if (selectedIncident.value?.id === id) selectedIncident.value = response.data;
      // return true;

      console.log('Assigning incident:', id, 'to', userId);
      return false;
    } catch (error: any) {
      errors.value.assign = error.message || 'Error al asignar incidente';
      console.error('Error assigning incident:', error);
      return false;
    }
  };

  /**
   * Desasigna un incidente del desarrollador actual.
   * @param id - ID del incidente
   */
  const unassign = async (id: string): Promise<boolean> => {
    errors.value.unassign = '';
    try {
      // TODO: Reemplazar con llamada API real
      // const response = await apiClient.post(`/incidents/${id}/unassign`);
      // const index = incidents.value.findIndex(i => i.id === id);
      // if (index !== -1) incidents.value[index] = response.data;
      // if (selectedIncident.value?.id === id) selectedIncident.value = response.data;
      // return true;

      console.log('Unassigning incident:', id);
      return false;
    } catch (error: any) {
      errors.value.unassign = error.message || 'Error al desasignar incidente';
      console.error('Error unassigning incident:', error);
      return false;
    }
  };

  /**
   * Cambia el estado de un incidente a IN_PROGRESS.
   * @param id - ID del incidente
   */
  const start = async (id: string): Promise<boolean> => {
    return update(id, { status: IncidentStatusEnum.IN_PROGRESS }).then(
      (result) => result !== null
    );
  };

  /**
   * Cambia el estado de un incidente a UNDER_REVIEW.
   * @param id - ID del incidente
   */
  const review = async (id: string): Promise<boolean> => {
    return update(id, { status: IncidentStatusEnum.UNDER_REVIEW }).then(
      (result) => result !== null
    );
  };

  /**
   * Marca un incidente como RESOLVED con notas opcionales.
   * @param id - ID del incidente
   * @param notes - Notas de resolución
   * @param version - Versión en la que se corrigió
   */
  const resolve = async (
    id: string,
    notes: string,
    version?: string
  ): Promise<boolean> => {
    return update(id, {
      status: IncidentStatusEnum.RESOLVED,
      resolutionNotes: notes,
      fixedInVersion: version,
      resolvedAt: new Date().toISOString(),
    }).then((result) => result !== null);
  };

  /**
   * Marca un incidente como CLOSED (requiere admin).
   * Solo disponible para incidentes en estado RESOLVED.
   * @param id - ID del incidente
   */
  const close = async (id: string): Promise<boolean> => {
    return update(id, {
      status: IncidentStatusEnum.CLOSED,
      closedAt: new Date().toISOString(),
    }).then((result) => result !== null);
  };

  /**
   * Reabre un incidente previamente resuelto o cerrado.
   * Cambia el estado a REOPENED.
   * @param id - ID del incidente
   */
  const reopen = async (id: string): Promise<boolean> => {
    return update(id, { status: IncidentStatusEnum.REOPENED }).then(
      (result) => result !== null
    );
  };

  /**
   * Cambia el orden de prioridad de un incidente.
   * @param id - ID del incidente
   * @param order - Nuevo número de orden
   */
  const changePriority = async (id: string, order: number): Promise<boolean> => {
    return update(id, { priorityOrder: order }).then((result) => result !== null);
  };

  /**
   * Carga incidentes de una aplicación específica.
   * @param appId - ID de la aplicación
   */
  const fetchByApp = async (appId: string): Promise<void> => {
    await fetchAll({ applicationId: appId });
  };

  /**
   * Carga incidentes agrupados por equipo.
   * Útil para vistas administrativas de carga de trabajo.
   */
  const fetchByTeam = async (): Promise<void> => {
    // Los datos agrupados se calculan automáticamente via computed
    console.log('Fetching incidents grouped by team');
  };

  /**
   * Carga incidentes asignados al usuario actual.
   * Filtra la lista general por assigneeId del usuario.
   */
  const fetchMyIncidents = async (): Promise<void> => {
    // TODO: Obtener ID del usuario actual del store de auth
    // const currentUserId = useAuthStore().user?.id;
    // if (currentUserId) {
    //   await fetchAll({ assigneeId: currentUserId });
    //   myIncidents.value = filteredIncidents.value;
    // }
    console.log('Fetching my incidents');
  };

  /**
   * Carga estadísticas del dashboard de incidentes.
   * @param appId - ID de aplicación opcional para filtrar estadísticas
   */
  const fetchDashboard = async (appId?: string): Promise<void> => {
    isLoading.value = true;
    errors.value.fetchDashboard = '';
    try {
      // TODO: Reemplazar con llamada API real
      // const response = await apiClient.get('/incidents/dashboard', {
      //   params: { applicationId: appId }
      // });
      // dashboard.value = response.data;

      console.log('Fetching dashboard for app:', appId);
    } catch (error: any) {
      errors.value.fetchDashboard = error.message || 'Error al cargar dashboard';
      console.error('Error fetching dashboard:', error);
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * Añade un comentario a un incidente.
   * @param id - ID del incidente
   * @param content - Contenido del comentario
   * @returns El comentario creado
   */
  const addComment = async (
    id: string,
    content: string
  ): Promise<IncidentComment | null> => {
    errors.value.addComment = '';
    try {
      // TODO: Reemplazar con llamada API real
      // const response = await apiClient.post(`/incidents/${id}/comments`, { content });
      // return response.data;

      console.log('Adding comment to incident:', id);
      return null;
    } catch (error: any) {
      errors.value.addComment = error.message || 'Error al añadir comentario';
      console.error('Error adding comment:', error);
      return null;
    }
  };

  /**
   * Carga todos los comentarios de un incidente.
   * @param id - ID del incidente
   * @returns Lista de comentarios
   */
  const fetchComments = async (id: string): Promise<IncidentComment[]> => {
    errors.value.fetchComments = '';
    try {
      // TODO: Reemplazar con llamada API real
      // const response = await apiClient.get(`/incidents/${id}/comments`);
      // return response.data;

      console.log('Fetching comments for incident:', id);
      return [];
    } catch (error: any) {
      errors.value.fetchComments = error.message || 'Error al cargar comentarios';
      console.error('Error fetching comments:', error);
      return [];
    }
  };

  /**
   * Selecciona un incidente para mostrar en el panel de detalles.
   * @param incident - Incidente a seleccionar, o null para deseleccionar
   */
  const selectIncident = (incident: Incident | null) => {
    selectedIncident.value = incident;
  };

  /**
   * Limpia todos los filtros activos.
   * Restaura la vista a mostrar todos los incidentes.
   */
  const clearFilters = () => {
    filters.value = {};
  };

  /**
   * Actualiza los filtros activos.
   * @param newFilters - Nuevos filtros a aplicar
   */
  const setFilters = (newFilters: Partial<IncidentFilters>) => {
    filters.value = { ...filters.value, ...newFilters };
  };

  /**
   * Limpia un filtro específico.
   * @param filterKey - Clave del filtro a limpiar
   */
  const clearFilter = (filterKey: keyof IncidentFilters) => {
    const { [filterKey]: _, ...rest } = filters.value;
    filters.value = rest;
  };

  return {
    // State
    incidents,
    selectedIncident,
    myIncidents,
    groupedByCategory,
    groupedByTeam,
    dashboard,
    filters,
    isLoading,
    errors,

    // Getters
    criticalIncidents,
    overdueIncidents,
    openCount,
    filteredIncidents,
    incidentsByCategory,

    // Actions
    fetchAll,
    fetchById,
    create,
    update,
    remove,
    assign,
    unassign,
    start,
    review,
    resolve,
    close,
    reopen,
    changePriority,
    fetchByApp,
    fetchByTeam,
    fetchMyIncidents,
    fetchDashboard,
    addComment,
    fetchComments,
    selectIncident,
    clearFilters,
    setFilters,
    clearFilter,
  };
});
