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
    applicationName: 'Nombre de la aplicación',
    description: 'Descripción',
    descriptionPlaceholder: 'Descripción breve de la aplicación',
    distinctiveColor: 'Color distintivo',
    create: 'Crear',
    applicationExample: 'Ej: Sistema de Autenticación',
    sortNameLabel: 'Nombre',
    sortPendingLabel: 'Pendientes',
    sortDelayedLabel: 'Retrasados',
    retry: 'Reintentar',
    creating: 'Creando...',
    loadError: 'Error al cargar aplicaciones',
    sortByLabel: 'Ordenar por',
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
    performanceTable: 'Tabla de Rendimiento',
    totalTickets: 'Tickets totales',
    completed: 'Completados',
    blocked: 'Bloqueados',
    avgTime: 'Tiempo promedio',
    weekChange: 'Cambio semanal',
    efficiency: 'Eficiencia',
    blockingIndex: 'Índice de bloqueo',
    churnIndex: 'Índice de rotación',
    heatmap: 'Mapa de calor',
    heatmapDescription: 'Visualización de tickets completados por día de la semana.',
    total: 'Total',
    daily: 'Diario',
    colorScale: 'Escala de Actividad',
    low: 'Nula/Baja',
    medium: 'Media',
    high: 'Alta',
    veryHigh: 'Muy Alta',
    ticketsClosedShort: 'tickets',
    noDataPattern: 'Sin datos suficientes para detectar patrones.',
    lowActivityPattern: 'El día con menor actividad históricamente es el ',
    emptyChartTitle: 'Selecciona una épica',
    emptyChartDesc: 'Elige una épica en el menú de arriba para visualizar su progreso ideal contra el real.',
    burndown: 'Gráfico de velocidad',
    burndownTitle: 'Gráfico Burndown',
    burndownDesc: 'Progreso real vs ideal de la épica',
    selectEpic: 'Seleccione una épica...',
    untitledEpic: 'Épica sin título',
    avgVelocity: 'Velocidad Promedio',
    ticketsPerDay: 'tickets por día',
    estimatedTime: 'Tiempo Estimado',
    daysRemaining: 'días restantes',
    status: 'Estado',
    idealLine: 'Línea Ideal',
    actualLine: 'Línea Real',
    onTime: 'A Tiempo',
    delayed: 'Atrasado',
    selectEpicProgress: 'Seleccione una épica para ver el progreso',
    ticketsAhead: 'tickets adelantado',
    ticketsBehind: 'tickets de retraso',
    pendingTickets: 'Tickets Pendientes',
    date: 'Fecha',
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
  // SECCIÓN: Selector de período
  // Usado en componentes de analítica
  // ==========================================
  period: {
    thisWeek: 'Esta semana',
    thisMonth: 'Este mes',
    thisQuarter: 'Este trimestre',
    custom: 'Personalizado',
  },

  // ==========================================
  // SECCIÓN: Encabezados de tabla genéricos
  // ==========================================
  table: {
    developer: 'Desarrollador',
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
    translating: 'Traduciendo...',
    translationResult: 'Resultado de la traducción',
    selectTargetLanguage: 'Selecciona idioma destino',
    copyToClipboard: 'Copiar',
    copied: '¡Copiado!',
    unsupportedFileType: 'Tipo de archivo no compatible para traducción',
    download: 'Descargar',
    translateDownloadHint: 'Traduce y descarga con formato preservado',
    downloading: 'Descargando...',
    serviceStarting: 'Servicio de traducción iniciando',
    serviceStartingDesc: 'El servicio de traducción no está disponible en este momento. Espera unos momentos e intenta de nuevo.',
    retrying: 'Reintentando...',
    retry: 'Reintentar',
    finalizing: 'Finalizando...',
    generatingFile: 'Generando archivo traducido...',
    almostDone: 'Casi listo...',
    minutesRemaining: 'min restantes',
    secondsRemaining: 's restantes',
    noFiles: 'Sin archivos',
    repositoryTitle: 'Repositorio de Código y Documentación',
    repositorySubtitle: 'Ver todos los archivos del proyecto y estadísticas de subida',
    loadingDocs: 'Cargando documentos...',
    noDocsYet: 'No hay documentos subidos aún.',
    noDocsDesc: 'Los archivos subidos a tickets y épicas aparecerán aquí.',
    details: 'Detalles →',
    documentation: 'Documentación',
    epicsTickets: 'Épicas / Tickets',
    byEpicTicket: 'Por Épica / Ticket',
    recentFiles: 'Archivos Recientes',
    filesTotal: '{n} archivos en total',
    fileSingularTotal: '{n} archivo en total',
    fileSingular: '{n} archivo',
    filesPlural: '{n} archivos',
    docTypeCode: 'CÓDIGO',
    docTypeDocumentation: 'DOCUMENTACIÓN',
    noCodeFiles: 'No hay archivos de código subidos aún.',
    noDocFiles: 'No hay documentación subida aún.',
    codeLabel: 'CÓDIGO',
    docsLabel: 'DOCS',
    uploadedLabel: 'SUBIDO',
    epicPrefix: 'Épica',
    ticketPrefix: 'Ticket',
    noContext: 'Sin contexto',
    userPrefix: 'Usuario',
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
    justNow: 'justo ahora',
    minutesAgo: 'hace {n}m',
    hoursAgo: 'hace {n}h',
    daysAgo: 'hace {n}d',
    unreadLabel: '{count} notificaciones no leídas',
    markAllRead2: 'Marcar todas como leídas',
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
    notifSectionTitle: 'Notificaciones',
    notifEmail: 'Por Correo',
    notifEmailDesc: 'Actualizaciones de tickets',
    notifPush: 'Notificaciones del navegador',
    notifPushDesc: 'Alertas en tiempo real',
    notifMobile: 'Móviles',
    notifMobileDesc: 'Alertas en tu teléfono',
    notifReminders: 'Recordatorios',
    notifRemindersDesc: 'Tickets por vencer',
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

  // ==========================================
  // SECCIÓN: Vista de Workbench
  // Panel personal del desarrollador
  // ==========================================
  workbenchView: {
    myTickets: 'Mis Tickets',
    byEpic: 'Por Épica',
    applications: 'Aplicaciones',
    applicationSingular: 'aplicación',
    applicationPlural: 'aplicaciones',
    selectApplication: 'Selecciona una aplicación',
    selectApplicationDesc: 'Elige una aplicación del panel izquierdo para comenzar a gestionar épicas y tareas',
    archivedApplications: 'Aplicaciones archivadas',
    epics: 'épicas',
    pending: 'pendientes',
    delayed: 'retrasadas',
    sortDefault: 'Orden: Predeterminado',
    sortPending: 'Orden: Más Pendientes',
    sortDelayed: 'Orden: Más Retrasados',
    active: 'Activo',
  },

  // ==========================================
  // SECCIÓN: Vista de Builder
  // Constructor visual de aplicaciones
  // ==========================================
  builderView: {
    title: 'Constructor de Aplicaciones',
    description: 'Gestiona aplicaciones, épicas y su progreso con swimlanes colapsables, edición rápida y navegación clara.',
    expandEpics: 'Expandir épicas',
    collapseEpics: 'Colapsar épicas',
    newApplication: 'Nueva aplicación',
    newEpic: 'Nueva épica',
    applicationsCount: 'Aplicaciones',
    registered: 'registradas',
    activeStatus: 'Activa',
    noSelection: 'Sin selección',
    noDescription: 'Sin descripción',
    epicCount: 'épicas',
    pendingCount: 'pendientes',
    delayedCount: 'vencidas',
    noApplications: 'No hay aplicaciones todavía.',
    applicationLabel: 'Aplicación',
    epicsLabel: 'Épicas',
    swimmlanesConfigured: 'Swimlanes configuradas para esta aplicación.',
    progressLabel: 'Progreso',
    progressDesc: 'Promedio de avance sobre los tickets asociados.',
    tonalityLabel: 'Tonalidad',
    colorGuide: 'Color guía',
    swimmlanesTitle: 'Swimlanes de épicas',
    swimmlanesDesc: 'Cada swimlane puede colapsarse, editarse, eliminarse o reordenarse.',
    collapseAll: 'Colapsar todo',
    expandAll: 'Expandir todo',
    noEpics: 'No hay épicas para esta aplicación. Crea la primera desde el botón superior.',
    tickets: 'tickets',
    completed: 'completados',
    epicNoDescription: 'Épica sin descripción',
    edit: 'Editar',
    delete: 'Borrar',
    dueDate: 'Vence:',
    collapsed: 'Colapsada',
    opened: 'Abierta',
    ticketsLabel: 'Tickets',
    items: 'elementos',
    progress: 'Progreso',
    addTicket: 'Agregar Ticket',
    quickActions: 'Acciones rápidas',
    visualOrder: 'Orden visual',
    selectApplicationMessage: 'Selecciona una aplicación',
    panelDescription: 'El panel central mostrará el lienzo de épicas, sus swimlanes colapsables y las acciones de CRUD. Usa la barra lateral para abrir una aplicación o crea una nueva para empezar.',
    createApplication: 'Crear aplicación',
    selectApplicationFirst: 'Selecciona una aplicación primero',
    close: 'Cerrar',
    formName: 'Nombre',
    formDescription: 'Descripción',
    editApplication: 'Editar aplicación',
    newApplicationTitle: 'Nueva aplicación',
    appDescPlaceholder: 'Describe el alcance de esta aplicación',
    colorLabel: 'Color',
    currentColor: 'Color actual',
    advanced: 'Avanzado',
    icon: 'Icono',
    saving: 'Guardando...',
    saveApplication: 'Guardar aplicación',
    editEpic: 'Editar épica',
    newEpicTitle: 'Nueva épica',
    appNamePlaceholder: 'Nombre de la aplicación',
    epicTitlePlaceholder: 'Título de la épica',
    epicTitleLabel: 'Título',
    epicDescPlaceholder: 'Explica el objetivo de esta épica',
    dueDateLabel: 'Fecha límite',
    targetApplication: 'Aplicación destino',
    saveEpic: 'Guardar épica',
    ticketTitlePlaceholder: 'Título del ticket...',
  },

  // ==========================================
  // SECCIÓN: Vista de Analytics
  // Métricas y análisis del equipo
  // ==========================================
  analyticsView: {
    title: 'Analítica Global',
    subtitle: 'Métricas de proyecto y rendimiento del equipo',
    applicationLabel: 'Aplicación',
    periodLabel: 'Período',
    loadingApps: 'Cargando apps...',
    thisWeek: 'Esta Semana',
    thisMonth: 'Este Mes',
    thisQuarter: 'Este Trimestre',
    thisYear: 'Este Año',
    refresh: '🔄 Actualizar',
    teamEfficiency: 'Eficiencia del Equipo',
    completedOnTime: 'Tickets completados a tiempo',
    blockingIndex: 'Índice de Bloqueo',
    blockedTickets: 'Tickets bloqueados',
    redirectionIndex: 'Índice de Redirección',
    redirectedTickets: 'Tickets redirigidos',
    teamPerformanceTitle: 'Rendimiento del Equipo',
    colMember: 'Miembro',
    colCompleted: 'Completadas',
    colInProgress: 'En Progreso',
    colBlocked: 'Bloqueadas',
    colEfficiency: 'Eficiencia',
    colVelocity: 'Velocidad',
    noPerformanceData: 'No hay datos de rendimiento disponibles',
    weeklyActivity: 'Actividad Semanal',
    noTicketsThisWeek: 'Sin tickets completados esta semana',
    unknownDev: 'Desconocido',
    heatmapNoActivity: 'Sin actividad',
    heatmapLow: 'Baja (1-3)',
    heatmapMedium: 'Media (4-6)',
    heatmapHigh: 'Alta (7+)',
    dayMon: 'Lun',
    dayTue: 'Mar',
    dayWed: 'Mié',
    dayThu: 'Jue',
    dayFri: 'Vie',
    daySat: 'Sáb',
    daySun: 'Dom',
    supportTicketsTitle: 'Tickets de Soporte',
    supportTotalSuffix: 'en total',
    supportByStatus: 'Por estado',
    supportBySeverity: 'Por severidad (bugs activos)',
    supportAvgResolution: 'Tiempo prom. de resolución',
    hoursSuffix: 'horas',
    supportNoData: 'No hay datos de tickets de soporte.',
  },

  // ==========================================
  // SECCIÓN: Vista de Team Assignment
  // Asignación de tickets a desarrolladores
  // ==========================================
  teamAssignmentView: {
    title: 'Asignación de Equipo',
    subtitle: 'Distribuye tickets entre desarrolladores',
    applicationLabel: 'Aplicación',
    selectOption: '-- Seleccionar --',
    unassignedTickets: 'Tickets Sin Asignar',
    ticketCount: 'ticket(s)',
    epicFilter: 'Épica',
    allEpics: 'Todas',
    priorityFilter: 'Prioridad',
    allPriorities: 'Todas',
    lowPriority: 'Baja',
    mediumPriority: 'Media',
    highPriority: 'Alta',
    urgentPriority: 'Urgente',
    assignButton: 'Asignar',
    noUnassignedTickets: 'No hay tickets sin asignar',
    allDistributed: 'Todos los tickets han sido distribuidos',
    developerWorkload: 'Carga por Desarrollador',
    developerCount: 'desarrollador(es)',
  },

  // ==========================================
  // SECCIÓN: Navegación de layouts
  // Sidebar y encabezados de AdminLayout y DeveloperLayout
  // ==========================================
  nav: {
    administration: 'Administración',
    builder: 'Constructor',
    analytics: 'Analítica',
    documentation: 'Documentación',
    team: 'Equipo',
    backToLogin: 'Volver al login',
    adminPanel: 'Panel de Administración',
    devPanel: 'Panel de Desarrollo',
    development: 'Desarrollo',
    workbench: 'Workbench',
    myUploads: 'Mis Archivos',
    teamAssignment: 'Asignación de Equipo',
    support: 'Soporte',
  },

  // ==========================================
  // SECCIÓN: Vista de Tickets de Soporte
  // ==========================================
  supportTicketsView: {
    title: 'Soporte',
    reportBugButton: '+ Reportar Bug',
    criticalCountSuffix: 'ticket(s) crítico(s)',
    statusAll: 'Todos',
    statusReported: 'Reportado',
    statusInvestigating: 'En Investigación',
    statusResolved: 'Resuelto',
    severityAll: 'Todas las severidades',
    severityCritical: '🔴 Crítica',
    severityHigh: '🟠 Alta',
    severityMedium: '🟡 Media',
    severityLow: '🟢 Baja',
    severityNone: 'Sin severidad',
    severityTextCritical: 'Crítica',
    severityTextHigh: 'Alta',
    severityTextMedium: 'Media',
    severityTextLow: 'Baja',
    emptyList: 'No hay tickets de soporte',
    loading: 'Cargando tickets...',
    unassigned: 'Sin asignar',
    assignToDeveloper: 'Asignar a Developer',
    assign: 'Asignar',
    assigning: '...',
    startInvestigation: '🔍 Iniciar Investigación',
    processing: 'Procesando...',
    markResolved: '✅ Marcar como Resuelto',
    description: 'Descripción',
    reproductionSteps: 'Pasos de Reproducción',
    stackTrace: 'Stack Trace',
    environment: 'Entorno',
    browser: 'Navegador',
    operatingSystem: 'Sistema Operativo',
    selectTicketPrompt: 'Selecciona un ticket para ver los detalles',
    formTitle: 'Reportar Bug de Soporte',
    fieldTitle: 'Título',
    titlePlaceholder: 'Descripción breve del bug',
    descriptionPlaceholder: 'Explica el comportamiento inesperado...',
    severityLabel: 'Severidad',
    reproductionStepsPlaceholder: '1. Ir a ...\n2. Hacer clic en ...\n3. Observar que ...',
    stackTracePlaceholder: 'Pega aquí el stack trace del error...',
    browserPlaceholder: 'Chrome 120, Firefox 121...',
    osPlaceholder: 'Windows 11, macOS 14...',
    cancel: 'Cancelar',
    submitReport: 'Reportar Bug',
    submitting: 'Reportando...',
    investigatedBy: 'Investigado por',
    linkedTicketLabel: 'Ticket relacionado (opcional)',
    linkedTicketNone: 'Ninguno',
  },

  // ==========================================
  // SECCIÓN: Dashboard de Workbench
  // Filtros y estados del panel personal del Developer
  // ==========================================
  workbenchDashboard: {
    myTickets: 'Mis Tickets',
    refresh: 'Actualizar',
    statusLabel: 'Estado:',
    dateLabel: 'Fecha:',
    statusAll: 'Todos',
    statusInProgress: 'En Progreso',
    statusTodo: 'Por Hacer',
    statusBlocked: 'Bloqueados',
    statusCompleted: 'Completados',
    dateAll: 'Todas',
    dateOverdue: 'Vencidos',
    dateToday: 'Hoy',
    dateThisWeek: 'Esta Semana',
    errorLoading: 'Error al cargar tickets',
    retry: 'Reintentar',
    loading: 'Cargando tickets...',
    noResults: 'Sin resultados para estos filtros',
    clearFilters: 'Limpiar filtros',
    noTickets: 'No tienes tickets asignados',
    ticketsWillAppear: 'Los tickets aparecerán aquí cuando te los asignen',
  },

  // ==========================================
  // SECCIÓN: Login
  // ==========================================
  login: {
    subtitle: 'Plataforma de Inteligencia Operacional',
    email: 'Correo',
    emailPlaceholder: 'tu dirección de correo',
    password: 'Contraseña',
    passwordPlaceholder: 'tu contraseña',
    submit: 'Ingresar',
    submitting: 'Iniciando sesión...',
    footer: '© {year} CoreStream · Plataforma de Inteligencia Operacional',
    lightMode: 'Modo claro',
    darkMode: 'Modo oscuro',
  },

  // ==========================================
  // SECCIÓN: Registro de actividad del ticket
  // Tipos de evento e historial
  // ==========================================
  activityLog: {
    title: 'Historial de Eventos',
    noEvents: 'Sin eventos registrados',
    eventCreated: 'Ticket Creado',
    eventAssigned: 'Asignado',
    eventStatusChanged: 'Estado Cambiado',
    eventQuestionRaised: 'Pregunta Levantada',
    eventQuestionResolved: 'Pregunta Resuelta',
    eventRedirected: 'Redirigido',
    eventCompleted: 'Completado',
    eventComment: 'Comentario',
    eventUpdated: 'Actualizado',
    eventTimerStart: 'Timer Iniciado',
    eventTimerPause: 'Timer Pausado',
    eventTimerSync: 'Timer Sincronizado',
    eventSubtaskCreated: 'Subtarea Creada',
    eventSubtaskCompleted: 'Subtarea Completada',
    eventSubtaskDeleted: 'Subtarea Eliminada',
    eventMoved: 'Ticket Movido',
    eventBlocked: 'Bloqueado',
    eventBlockedQuestion: 'Pregunta Bloqueante',
  },
}
