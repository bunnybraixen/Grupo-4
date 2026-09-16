/**
 * Archivo de traducciones en ESPAÑOL para CoreStream
 * Contiene todas las cadenas de texto de la aplicación organizadas por secciones
 * Utiliza nomenclatura de puntos para acceder a las claves anidadas (ej: common.save)
 */

export default {
  // ==========================================
  // SECCIÓN: Acciones y términos comunes
  // Palabras clave reutilizables en toda la interfaz
  // ==========================================
  common: {
    save: 'Guardar',
    cancel: 'Cancelar',
    delete: 'Eliminar',
    edit: 'Editar',
    confirm: 'Confirmar',
    close: 'Cerrar',
    search: 'Buscar',
    filter: 'Filtrar',
    loading: 'Cargando...',
    error: 'Error',
    success: 'Éxito',
    back: 'Atrás',
    next: 'Siguiente',
    noData: 'Sin datos',
    actions: 'Acciones',
    yes: 'Sí',
    no: 'No',
    required: 'Requerido',
    optional: 'Opcional',
  },

  // ==========================================
  // SECCIÓN: Encabezado y navegación superior
  // Elementos del header/navbar de la aplicación
  // ==========================================
  header: {
    administrator: 'Administrador',
    developer: 'Desarrollador',
    settings: 'Configuración',
    notifications: 'Notificaciones',
    logout: 'Cerrar sesión',
    profile: 'Perfil',
    darkMode: 'Modo oscuro',
    language: 'Idioma',
  },

  // ==========================================
  // SECCIÓN: Barra lateral
  // Menú de navegación lateral principal
  // ==========================================
  sidebar: {
    applications: 'Aplicaciones',
    sortByName: 'Ordenar por nombre',
    sortByPending: 'Ordenar por pendientes',
    sortByDelayed: 'Ordenar por retrasados',
    newApp: 'Nueva aplicación',
    noApps: 'No hay aplicaciones',
  },

  // ==========================================
  // SECCIÓN: Constructor visual
  // Panel de construcción de epics y tickets
  // ==========================================
  builder: {
    projectCanvas: 'Lienzo del proyecto',
    newEpic: 'Nuevo épico',
    addTicket: 'Agregar ticket',
    epicPlaceholder: 'Nombre del épico',
    ticketPlaceholder: 'Descripción del ticket',
    dragEpicsHint: 'Arrastra los épicos para reorganizar',
    showTickets: 'Mostrar tickets',
    hideTickets: 'Ocultar tickets',
    unassigned: 'Sin asignar',
    attachDocs: 'Adjuntar documentos',
    epicDocs: 'Documentos del épico',
    uploadSpec: 'Cargar especificación',
    noDocsAttached: 'Sin documentos adjuntos',
  },

  // ==========================================
  // SECCIÓN: Banco de trabajo
  // Panel de gestión de tareas y seguimiento
  // ==========================================
  workbench: {
    myWorkbench: 'Mi banco de trabajo',
    allTickets: 'Todos los tickets',
    inProgress: 'En progreso',
    todo: 'Por hacer',
    done: 'Completado',
    overdue: 'Retrasado',
    today: 'Hoy',
    thisWeek: 'Esta semana',
    later: 'Más tarde',
    noTickets: 'Sin tickets',
    startWorking: 'Comenzar a trabajar',
    selectTicket: 'Seleccionar ticket',
    timer: 'Temporizador',
    timeSpent: 'Tiempo invertido',
    blockedTime: 'Tiempo bloqueado',
    subtasks: 'Subtareas',
    subtasksProgress: 'Progreso de subtareas',
    activityLog: 'Registro de actividad',
  },

  // ==========================================
  // SECCIÓN: Acciones de tickets
  // Operaciones disponibles para los tickets
  // ==========================================
  actions: {
    complete: 'Completar',
    completeTicket: 'Completar ticket',
    raiseQuestion: 'Plantear pregunta',
    redirect: 'Redirigir',
    prLink: 'Enlace de PR',
    prLinkPlaceholder: 'https://github.com/repo/pull/123',
    prRequired: 'Se requiere enlace de PR',
    invalidPr: 'Enlace de PR inválido',
    questionPlaceholder: 'Describe tu pregunta aquí',
    questionMinLength: 'La pregunta debe tener al menos 10 caracteres',
    redirectTo: 'Redirigir a',
    redirectReason: 'Razón de redirección',
    reasonPlaceholder: 'Explica por qué se redirige este ticket',
    reasonMinLength: 'La razón debe tener al menos 10 caracteres',
    confirmComplete: 'Confirmar completación',
    confirmRedirect: 'Confirmar redirección',
  },

  // ==========================================
  // SECCIÓN: Análisis y reportes
  // Métricas, gráficos y estadísticas del equipo
  // ==========================================
  analytics: {
    analytics: 'Análisis',
    commandCenter: 'Centro de comandos',
    performanceMetrics: 'Métricas de desempeño',
    totalTickets: 'Tickets totales',
    completed: 'Completados',
    blocked: 'Bloqueados',
    avgTime: 'Tiempo promedio',
    weekChange: 'Cambio semanal',
    efficiency: 'Eficiencia',
    blockingIndex: 'Índice de bloqueo',
    churnIndex: 'Índice de rotación',
    heatmap: 'Mapa de calor',
    burndown: 'Gráfico de velocidad',
    exportPdf: 'Exportar PDF',
    exportCsv: 'Exportar CSV',
    ideal: 'Ideal',
    actual: 'Real',
    period: 'Período',
    lastWeek: 'Última semana',
    lastMonth: 'Último mes',
    lastQuarter: 'Último trimestre',
    teamPerformance: 'Desempeño del equipo',
    sortBy: 'Ordenar por',
    ticketsProcessed: 'Tickets procesados',
    questions: 'Preguntas',
    redirects: 'Redirecciones',
    drillDown: 'Detallar',
    insight: 'Perspectiva',
    noData: 'Sin datos disponibles',
  },

  // ==========================================
  // SECCIÓN: Gestión de equipo
  // Administración de miembros y asignaciones
  // ==========================================
  team: {
    teamManagement: 'Gestión del equipo',
    teamAssignment: 'Asignación de equipo',
    addDeveloper: 'Agregar desarrollador',
    editMember: 'Editar miembro',
    deleteMember: 'Eliminar miembro',
    promoteLeader: 'Promover a líder',
    demoteLeader: 'Degradar de líder',
    members: 'Miembros',
    name: 'Nombre',
    email: 'Correo electrónico',
    role: 'Rol',
    specialty: 'Especialidad',
    stats: 'Estadísticas',
    ticketsCompleted: 'Tickets completados',
    ticketsPending: 'Tickets pendientes',
    ticketsBlocked: 'Tickets bloqueados',
    avgTime: 'Tiempo promedio',
    unassignedTickets: 'Tickets sin asignar',
    assignedTickets: 'Tickets asignados',
    workload: 'Carga de trabajo',
    lowLoad: 'Carga baja',
    mediumLoad: 'Carga media',
    highLoad: 'Carga alta',
    assignTicket: 'Asignar ticket',
    unassignTicket: 'Desasignar ticket',
    confirmDelete: 'Confirmar eliminación',
    noMembers: 'Sin miembros en el equipo',
  },

  // ==========================================
  // SECCIÓN: Código y documentación
  // Gestión de archivos, repositorio y docs
  // ==========================================
  codeDocs: {
    codeAndDocs: 'Código y documentación',
    repository: 'Repositorio',
    totalFiles: 'Archivos totales',
    codeFiles: 'Archivos de código',
    docFiles: 'Archivos de documentación',
    contributors: 'Colaboradores',
    upload: 'Cargar',
    translate: 'Traducir',
    translateTo: 'Traducir a',
    download: 'Descargar',
    noFiles: 'Sin archivos',
  },

  // ==========================================
  // SECCIÓN: Notificaciones
  // Mensajes y alertas del sistema
  // ==========================================
  notifications: {
    title: 'Notificaciones',
    markAllRead: 'Marcar todo como leído',
    noNotifications: 'Sin notificaciones',
    assignedToYou: 'Te fue asignado un ticket',
    questionRaised: 'Se planteó una pregunta',
    ticketRedirected: 'El ticket fue redirigido',
    ticketCompleted: 'El ticket fue completado',
    systemMessage: 'Mensaje del sistema',
  },

  // ==========================================
  // SECCIÓN: Configuración
  // Preferencias de usuario y aplicación
  // ==========================================
  settings: {
    settingsTitle: 'Configuración',
    language: 'Idioma',
    theme: 'Tema',
    lightMode: 'Modo claro',
    darkMode: 'Modo oscuro',
    profile: 'Perfil',
    saveChanges: 'Guardar cambios',
  },

  // ==========================================
  // SECCIÓN: Estados de tickets
  // Estados de progreso y prioridades
  // ==========================================
  statuses: {
    todo: 'Por hacer',
    inProgress: 'En progreso',
    blocked: 'Bloqueado',
    redirected: 'Redirigido',
    done: 'Completado',
    low: 'Baja',
    medium: 'Media',
    high: 'Alta',
    urgent: 'Urgente',
  },

  // ==========================================
  // SECCIÓN: Roles de usuario
  // Tipos de permisos y acceso
  // ==========================================
  roles: {
    admin: 'Administrador',
    groupLeader: 'Líder del grupo',
    developer: 'Desarrollador',
  },

  // ==========================================
  // SECCIÓN: Mensajes de error
  // Textos para diferentes tipos de errores
  // ==========================================
  errors: {
    generic: 'Ha ocurrido un error',
    unauthorized: 'No autorizado',
    notFound: 'No encontrado',
    forbidden: 'Acceso denegado',
    serverError: 'Error del servidor',
    networkError: 'Error de red',
    validationError: 'Error de validación',
    loginFailed: 'Falló el inicio de sesión',
    emailTaken: 'El correo electrónico ya está registrado',
  },

  // ==========================================
  // SECCIÓN: Diálogos de confirmación
  // Mensajes de confirmación para acciones críticas
  // ==========================================
  confirm: {
    deleteTicket: '¿Eliminar este ticket?',
    deleteEpic: '¿Eliminar este épico?',
    deleteApp: '¿Eliminar esta aplicación?',
    deleteMember: '¿Eliminar este miembro del equipo?',
    redirectTicket: '¿Redirigir este ticket?',
    completeTicket: '¿Marcar como completado?',
    logout: '¿Cerrar sesión?',
  },
}
