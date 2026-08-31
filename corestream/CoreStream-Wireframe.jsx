const { useState, useEffect, useRef } = React;

// CoreStream - Operational Intelligence Platform Wireframe
// Views: Administrator (Builder + Analytics) & Employee (Workbench)

const CoreStream = () => {
  const [activeView, setActiveView] = useState('admin'); // 'admin' or 'employee'
  const [activeAdminTab, setActiveAdminTab] = useState('builder'); // 'builder', 'analytics', 'codedocs', or 'team'
  const [activeDeveloperTab, setActiveDeveloperTab] = useState('workbench'); // 'workbench', 'uploads', or 'teamAssignment'
  const [selectedApp, setSelectedApp] = useState(0);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [showQuestionModal, setShowQuestionModal] = useState(false);
  const [showRedirectModal, setShowRedirectModal] = useState(false);
  const [expandedEpics, setExpandedEpics] = useState([]); // Default collapsed
  const [expandedProjects, setExpandedProjects] = useState([0, 1, 2]);
  const [sortBy, setSortBy] = useState('ticketsProcessed'); // 'ticketsProcessed', 'pending', 'blocked', 'name'
  const [sortOrder, setSortOrder] = useState('desc');
  const [showNewDeveloperModal, setShowNewDeveloperModal] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState('all'); // 'all', 'progress', 'todo'
  const [appSortBy, setAppSortBy] = useState('default'); // 'default', 'pending', 'delayed'
  const [dueFilter, setDueFilter] = useState('all'); // 'all', 'overdue', 'today', 'week', 'later'
  const [darkMode, setDarkMode] = useState(false);
  const [language, setLanguage] = useState('en'); // 'en', 'es', 'fr', 'de', 'pt'
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [showLanguageDropdown, setShowLanguageDropdown] = useState(false);
  
  // New state for Builder enhancements
  const [newEpicName, setNewEpicName] = useState('');
  const [isCreatingEpic, setIsCreatingEpic] = useState(false);
  const [newTicketName, setNewTicketName] = useState('');
  const [creatingTicketInEpic, setCreatingTicketInEpic] = useState(null);
  const [draggingTicket, setDraggingTicket] = useState(null);
  const [dragOverEpic, setDragOverEpic] = useState(null);
  
  // New state for Workbench enhancements
  const [ticketTimers, setTicketTimers] = useState({}); // { ticketId: { startTime, elapsed, isRunning } }
  const [questionText, setQuestionText] = useState('');
  const [redirectReason, setRedirectReason] = useState('');
  const [redirectToUser, setRedirectToUser] = useState(null);
  const [ticketEvents, setTicketEvents] = useState([]); // Event log
  
  // Refs
  const newEpicInputRef = useRef(null);
  const newTicketInputRef = useRef(null);
  
  // State for epic documents
  const [epicDocs, setEpicDocs] = useState({
    0: [
      { name: 'payment-spec.pdf', size: '2.4 MB', type: 'pdf', uploadedAt: '2024-12-20' },
      { name: 'api-requirements.md', size: '45 KB', type: 'md', uploadedAt: '2024-12-18' },
    ],
    1: [
      { name: 'refund-flow.pdf', size: '1.2 MB', type: 'pdf', uploadedAt: '2024-12-22' },
    ],
    2: [],
  });
  const [showEpicDocsModal, setShowEpicDocsModal] = useState(null); // epic id or null
  
  // State for ticket PR links
  const [ticketPRLinks, setTicketPRLinks] = useState({});
  const [prLinkError, setPrLinkError] = useState('');
  
  // Validate PR link
  const isValidPRLink = (url) => {
    if (!url) return false;
    const prPatterns = [
      /^https?:\/\/(www\.)?github\.com\/[\w-]+\/[\w-]+\/pull\/\d+/,
      /^https?:\/\/(www\.)?gitlab\.com\/[\w-]+\/[\w-]+\/-\/merge_requests\/\d+/,
      /^https?:\/\/[\w-]+\.atlassian\.net\/.*\/pull-requests\/\d+/,
      /^https?:\/\/bitbucket\.org\/[\w-]+\/[\w-]+\/pull-requests\/\d+/,
    ];
    return prPatterns.some(pattern => pattern.test(url));
  };
  
  // Handle upload document to epic
  const handleUploadEpicDoc = (epicId, file) => {
    const newDoc = {
      name: file.name || 'document.pdf',
      size: file.size ? `${(file.size / 1024).toFixed(0)} KB` : '1 MB',
      type: file.name?.split('.').pop() || 'pdf',
      uploadedAt: new Date().toISOString().split('T')[0],
    };
    setEpicDocs(prev => ({
      ...prev,
      [epicId]: [...(prev[epicId] || []), newDoc]
    }));
  };

  // Language options
  const languages = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
    { code: 'pt', name: 'Português', flag: '🇧🇷' },
  ];

  const currentLanguage = languages.find(l => l.code === language);

  // Translations
  const translations = {
    en: {
      // Header
      administrator: 'Administrator',
      developer: 'Developer',
      settings: 'Settings',
      notifications: 'Notifications',
      
      // Admin Tabs
      projectCanvas: 'Project Canvas',
      analytics: 'Analytics',
      codeDocs: 'Code & Docs',
      teamManagement: 'Team Management',
      
      // Developer Tabs
      myWorkbench: 'My Workbench',
      codeAndDocs: 'Code & Docs',
      
      // Project Canvas
      active: 'Active',
      dragEpicsToReorder: 'Drag epics to reorder priority. Click on epic headers to show/hide tickets.',
      projectHasDelayedTickets: 'Project has delayed tickets',
      ticketsOverdue: 'ticket(s) are past their due date',
      viewAllDelayed: 'View All Delayed',
      delayed: 'delayed',
      epicOverdue: 'Epic Overdue!',
      due: 'Due',
      showTickets: 'Show Tickets',
      hideTickets: 'Hide Tickets',
      tickets: 'tickets',
      unassigned: 'Unassigned',
      completed: 'Completed',
      daysOverdue: 'd overdue',
      dueToday: 'Due today',
      daysLeft: 'd left',
      causingDelay: 'This ticket is causing project delay',
      addTicket: 'Add Ticket',
      addEpic: 'Add Epic',
      
      // Analytics
      commandCenter: 'Command Center',
      teamPerformanceMetrics: 'Team performance metrics and project health',
      totalTickets: 'Total Tickets',
      blocked: 'Blocked',
      avgTime: 'Avg. Time',
      thisWeek: 'this week',
      critical: 'critical',
      vsLastWeek: 'vs last week',
      teamPerformanceByProject: 'Team Performance by Project',
      sortBy: 'Sort by',
      ticketsCompleted: 'Tickets Completed',
      pending: 'Pending',
      name: 'Name',
      questions: 'Questions',
      redirects: 'Redirects',
      burndownChart: 'Burndown Chart',
      ideal: 'Ideal',
      actual: 'Actual',
      activityHeatmap: 'Activity Heatmap',
      
      // Analytics enhancements
      performanceMetrics: 'Performance Metrics',
      keyIndicators: 'Key performance indicators based on ticket events',
      lastWeek: 'Last 7 days',
      efficiency: 'Efficiency',
      efficiencyDesc: 'Tickets completed per hour worked',
      blockingIndex: 'Blocking Index',
      blockingIndexDesc: 'High = needs training or bad specs',
      churnIndex: 'Churn Index',
      churnIndexDesc: 'High = avoiding work or wrong assignments',
      totalHours: 'Total Hours',
      ticketsClosedByDayDev: 'Tickets closed by developer per day of week',
      lessActive: 'Less',
      moreActive: 'More',
      total: 'Total',
      dailyTotal: 'Daily Total',
      insight: 'Insight',
      fridayInsight: 'Activity drops significantly on Fridays. Consider moving sprint reviews to Thursday afternoons.',
      weeklyTrend: 'Weekly Trend',
      
      // Code & Docs Integration
      attachDocs: 'Attach Docs',
      epicDocs: 'Epic Documents',
      uploadSpec: 'Upload Spec/PDF',
      attachedFiles: 'Attached Files',
      noDocsAttached: 'No documents attached',
      prLink: 'Pull Request Link',
      prLinkPlaceholder: 'Paste GitHub/GitLab PR URL...',
      prRequired: 'PR link required to complete',
      validPrRequired: 'Valid PR link is required',
      invalidPrLink: 'Invalid PR URL format',
      
      // Document Translation
      translateDocument: 'Translate Document',
      translateTo: 'Translate to...',
      translatingTo: 'Translating to',
      translated: 'Translated',
      translationComplete: 'Translation complete',
      download: 'Download',
      autoTranslation: 'Auto-Translation',
      autoTranslationDesc: 'Click 🌐 to automatically translate any document to 8+ languages using AI. Translations preserve formatting and technical terms.',
      
      // Team Lead functionality
      teamLead: 'Team Lead',
      developer: 'Developer',
      promoteToLead: 'Promote to Team Lead',
      removeLeadRole: 'Remove Team Lead Role',
      teamLeadBadge: '👑 Lead',
      assignTickets: 'Assign Tickets',
      teamAssignment: 'Team Assignment',
      unassignedTickets: 'Unassigned Tickets',
      assignedTickets: 'Assigned Tickets',
      assignTo: 'Assign to',
      unassign: 'Unassign',
      assignTicket: 'Assign Ticket',
      selectDeveloper: 'Select developer',
      ticketAssigned: 'Ticket assigned successfully',
      ticketUnassigned: 'Ticket unassigned',
      noUnassignedTickets: 'No unassigned tickets',
      noAssignedTickets: 'No assigned tickets',
      dragToAssign: 'Drag tickets to assign to team members',
      teamLeadOnly: 'Team Lead Only',
      manageTeamWorkload: 'Manage your team workload',
      allDevelopers: 'All Developers',
      searchDevelopers: 'Search developers...',
      allRoles: 'All Roles',
      assignedTo: 'Assigned to',
      assignToProject: 'Assign to project',
      inactive: 'Inactive',
      
      // Builder enhancements
      dragTicketsBetweenEpics: 'Drag tickets between epics to reorganize',
      noAssignees: 'No assignees',
      dropTicketHere: 'Drop ticket here',
      collapse: 'Collapse',
      expand: 'Expand',
      epicNamePlaceholder: 'Enter epic name...',
      ticketTitlePlaceholder: 'Enter ticket title...',
      
      // Workbench enhancements
      description: 'Description',
      blockedReason: 'Blocked Reason',
      subtasks: 'Subtasks',
      ticketLifecycle: 'Ticket Lifecycle',
      activityLog: 'Activity Log',
      complete: 'Complete',
      block: 'Block / Ask',
      unblock: 'Unblock',
      redirect: 'Redirect',
      ticketCompleted: 'Ticket completed!',
      raiseQuestion: 'Raise a Question',
      pauseTimerNotify: 'This will pause your timer and notify the owner',
      timerWillPause: 'Timer will pause',
      currentTime: 'Current time',
      whatsBlockingYou: "What's blocking you?",
      describeBlocker: 'Describe the issue preventing progress...',
      ownerWillBeNotified: 'Owner will be notified:',
      submitQuestion: 'Submit Question',
      redirectTicket: 'Redirect Ticket',
      transferResponsibility: 'Transfer responsibility to another team member',
      yourTimeSpent: 'Your time spent',
      willBeRecorded: 'Will be recorded in analytics',
      redirectTo: 'Redirect to',
      handoffNote: 'Handoff note (required)',
      whyPassing: 'Why are you passing this ticket? What context should they know?',
      ticketWillDisappear: 'This ticket will disappear from your workbench immediately',
      selectUser: 'Please select a user',
      reasonRequired: 'Reason is required',
      questionRequired: 'Question is required',
      redirectNow: 'Redirect Now',
      cancel: 'Cancel',
      
      // Team Management
      manageTeam: 'Manage your development team members',
      totalDevelopers: 'Total Developers',
      avgTicketsDev: 'Avg. Tickets/Dev',
      avgResponse: 'Avg. Response',
      addDeveloper: 'Add Developer',
      searchDevelopers: 'Search developers...',
      allRoles: 'All Roles',
      allStatus: 'All Status',
      email: 'Email',
      role: 'Role',
      ticketsProcessed: 'Tickets Processed',
      projects: 'Projects',
      actions: 'Actions',
      
      // Code & Docs (Admin)
      codeDocRepository: 'Code & Documentation Repository',
      viewAllProjectFiles: 'View all project files and developer upload statistics',
      codeFiles: 'Code Files',
      documentation: 'Documentation',
      contributors: 'Contributors',
      lastUpdate: 'Last Update',
      developerUploadStats: 'Developer Upload Statistics',
      filesUploadedBy: 'Files uploaded by each developer in',
      totalFiles: 'Total Files',
      totalSize: 'Total Size',
      lastUpload: 'Last Upload',
      contribution: 'Contribution',
      recentFiles: 'Recent Files',
      latestUploads: 'Latest uploads in',
      all: 'All',
      code: 'Code',
      docs: 'Docs',
      approved: 'Approved',
      pendingReview: 'Pending',
      
      // Developer Workbench
      developerWorkbench: 'Developer Workbench',
      yourAssignedTickets: 'Your assigned tickets and current tasks',
      activeTickets: 'Active Tickets',
      pendingTickets: 'Pending Tickets',
      clickToFilter: 'Click to filter',
      inProgress: 'In progress',
      today: 'today',
      waitingToStart: 'Waiting to start',
      estimated: 'Est.',
      teamRanking: 'Team Ranking',
      yourTeam: 'Your team',
      ticketsCompleted2: 'tickets completed',
      viewAllTeams: 'View All Teams →',
      filterByDueDate: 'Filter by due date:',
      overdue: 'Overdue',
      thisWeek2: 'This Week',
      later: 'Later',
      showing: 'Showing',
      clearAllFilters: 'Clear all filters',
      noOverdueTickets: 'No overdue tickets!',
      nothingDueToday: 'Nothing due today!',
      noTicketsDueThisWeek: 'No tickets due this week!',
      noActiveTickets: 'No active tickets!',
      noPendingTickets: 'No pending tickets!',
      greatJobOnSchedule: 'Great job staying on schedule!',
      allCaughtUp: "You're all caught up.",
      assignedBy: 'Assigned by',
      subtasks: 'Subtasks',
      timeSpent: 'Time spent',
      
      // Developer Uploads Tab
      codeAndDocumentation: 'Code & Documentation',
      uploadCodeAndDocs: 'Upload your code files and related documentation for review',
      dropCodeFiles: 'Drop code files here or click to browse',
      supportsCode: 'Supports: .js, .ts, .py, .java, .go, .rs, .cpp, .json, .yaml',
      linkToTicket: 'Link to Ticket',
      selectTicket: 'Select a ticket...',
      uploadedFiles: 'Uploaded Files',
      dropDocumentation: 'Drop documentation here or click to browse',
      supportsDocs: 'Supports: .md, .pdf, .docx, .txt, .html, .xlsx',
      documentationType: 'Documentation Type',
      apiReference: 'API Reference',
      userGuide: 'User Guide',
      technicalSpec: 'Technical Spec',
      readme: 'README',
      other: 'Other',
      uploadedDocumentation: 'Uploaded Documentation',
      recentUploadActivity: 'Recent Upload Activity',
      uploaded: 'uploaded',
      approvedBy: 'Approved by',
      
      // Ticket Panel
      ticketDetails: 'Ticket Details',
      description: 'Description',
      completeTicket: 'Complete Ticket',
      blockQuestion: 'Block / Question',
      redirect: 'Redirect',
      
      // Settings Modal
      customizeExperience: 'Customize your CoreStream experience',
      appearance: 'Appearance',
      theme: 'Theme',
      chooseLightDark: 'Choose light or dark mode',
      light: 'Light',
      dark: 'Dark',
      selectLanguage: 'Select your preferred language',
      emailNotifications: 'Email Notifications',
      receiveEmailUpdates: 'Receive email for important updates',
      pushNotifications: 'Push Notifications',
      getNotifiedBrowser: 'Get notified in your browser',
      mobileNotifications: 'Mobile Notifications',
      receiveAlerts: 'Receive alerts on your phone',
      dueDateReminders: 'Due Date Reminders',
      getRemindedDeadlines: 'Get reminded before deadlines',
      account: 'Account',
      editProfile: 'Edit Profile',
      changePassword: 'Change Password',
      updateCredentials: 'Update your credentials',
      connectedApps: 'Connected Apps',
      manageIntegrations: 'Manage integrations',
      exportData: 'Export Data',
      downloadYourData: 'Download your data',
      helpSupport: 'Help & Support',
      getAssistance: 'Get assistance',
      dangerZone: 'Danger Zone',
      deleteAccount: 'Delete Account',
      permanentlyDelete: 'Permanently delete your account and all data',
      delete: 'Delete',
      cancel: 'Cancel',
      saveChanges: 'Save Changes',
      
      // Sidebar
      applications: 'Applications',
      sortDefault: 'Sort: Default',
      sortMostPending: 'Sort: Most Pending',
      sortMostDelayed: 'Sort: Most Delayed',
      epics: 'epics',
      archivedApps: 'Archived Apps',
      filtered: 'Filtered',
    },
    es: {
      // Header
      administrator: 'Administrador',
      developer: 'Desarrollador',
      settings: 'Configuración',
      notifications: 'Notificaciones',
      
      // Admin Tabs
      projectCanvas: 'Lienzo de Proyecto',
      analytics: 'Analíticas',
      codeDocs: 'Código y Docs',
      teamManagement: 'Gestión de Equipo',
      
      // Developer Tabs
      myWorkbench: 'Mi Escritorio',
      codeAndDocs: 'Código y Docs',
      
      // Project Canvas
      active: 'Activo',
      dragEpicsToReorder: 'Arrastra épicas para reordenar prioridad. Haz clic en los encabezados para mostrar/ocultar tickets.',
      projectHasDelayedTickets: 'El proyecto tiene tickets retrasados',
      ticketsOverdue: 'ticket(s) han pasado su fecha límite',
      viewAllDelayed: 'Ver Todos los Retrasados',
      delayed: 'retrasados',
      epicOverdue: '¡Épica Vencida!',
      due: 'Vence',
      showTickets: 'Mostrar Tickets',
      hideTickets: 'Ocultar Tickets',
      tickets: 'tickets',
      unassigned: 'Sin asignar',
      completed: 'Completados',
      daysOverdue: 'd vencido',
      dueToday: 'Vence hoy',
      daysLeft: 'd restantes',
      causingDelay: 'Este ticket está causando retraso',
      addTicket: 'Agregar Ticket',
      addEpic: 'Agregar Épica',
      
      // Analytics
      commandCenter: 'Centro de Comando',
      teamPerformanceMetrics: 'Métricas de rendimiento del equipo y salud del proyecto',
      totalTickets: 'Total de Tickets',
      blocked: 'Bloqueados',
      avgTime: 'Tiempo Prom.',
      thisWeek: 'esta semana',
      critical: 'críticos',
      vsLastWeek: 'vs semana pasada',
      teamPerformanceByProject: 'Rendimiento del Equipo por Proyecto',
      sortBy: 'Ordenar por',
      ticketsCompleted: 'Tickets Completados',
      pending: 'Pendientes',
      name: 'Nombre',
      questions: 'Preguntas',
      redirects: 'Redirecciones',
      burndownChart: 'Gráfico de Avance',
      ideal: 'Ideal',
      actual: 'Real',
      activityHeatmap: 'Mapa de Actividad',
      
      // Analytics enhancements
      performanceMetrics: 'Métricas de Rendimiento',
      keyIndicators: 'Indicadores clave basados en eventos de tickets',
      lastWeek: 'Últimos 7 días',
      efficiency: 'Eficiencia',
      efficiencyDesc: 'Tickets completados por hora trabajada',
      blockingIndex: 'Índice de Bloqueo',
      blockingIndexDesc: 'Alto = necesita capacitación o malas specs',
      churnIndex: 'Índice de Pasamanos',
      churnIndexDesc: 'Alto = evita trabajo o asignaciones incorrectas',
      totalHours: 'Total Horas',
      ticketsClosedByDayDev: 'Tickets cerrados por desarrollador por día',
      lessActive: 'Menos',
      moreActive: 'Más',
      total: 'Total',
      dailyTotal: 'Total Diario',
      insight: 'Insight',
      fridayInsight: 'La actividad baja significativamente los viernes. Considera mover las revisiones de sprint al jueves.',
      weeklyTrend: 'Tendencia Semanal',
      
      // Code & Docs Integration
      attachDocs: 'Adjuntar Docs',
      epicDocs: 'Documentos de la Épica',
      uploadSpec: 'Subir Spec/PDF',
      attachedFiles: 'Archivos Adjuntos',
      noDocsAttached: 'Sin documentos adjuntos',
      prLink: 'Link de Pull Request',
      prLinkPlaceholder: 'Pega URL de PR de GitHub/GitLab...',
      prRequired: 'Link de PR requerido para completar',
      validPrRequired: 'Se requiere un link de PR válido',
      invalidPrLink: 'Formato de URL de PR inválido',
      
      // Document Translation
      translateDocument: 'Traducir Documento',
      translateTo: 'Traducir a...',
      translatingTo: 'Traduciendo a',
      translated: 'Traducido',
      translationComplete: 'Traducción completa',
      download: 'Descargar',
      autoTranslation: 'Traducción Automática',
      autoTranslationDesc: 'Haz clic en 🌐 para traducir automáticamente cualquier documento a 8+ idiomas usando IA. Las traducciones preservan el formato y términos técnicos.',
      
      // Team Lead functionality
      teamLead: 'Líder de Grupo',
      developer: 'Desarrollador',
      promoteToLead: 'Promover a Líder de Grupo',
      removeLeadRole: 'Quitar Rol de Líder',
      teamLeadBadge: '👑 Líder',
      assignTickets: 'Asignar Tickets',
      teamAssignment: 'Asignación de Equipo',
      unassignedTickets: 'Tickets Sin Asignar',
      assignedTickets: 'Tickets Asignados',
      assignTo: 'Asignar a',
      unassign: 'Desasignar',
      assignTicket: 'Asignar Ticket',
      selectDeveloper: 'Seleccionar desarrollador',
      ticketAssigned: 'Ticket asignado exitosamente',
      ticketUnassigned: 'Ticket desasignado',
      noUnassignedTickets: 'No hay tickets sin asignar',
      noAssignedTickets: 'Sin tickets asignados',
      dragToAssign: 'Arrastra tickets para asignar a miembros del equipo',
      teamLeadOnly: 'Solo Líder de Grupo',
      manageTeamWorkload: 'Gestiona la carga de trabajo de tu equipo',
      allDevelopers: 'Todos los Desarrolladores',
      searchDevelopers: 'Buscar desarrolladores...',
      allRoles: 'Todos los Roles',
      assignedTo: 'Asignado a',
      assignToProject: 'Asignar a proyecto',
      inactive: 'Inactivo',
      
      // Builder enhancements
      dragTicketsBetweenEpics: 'Arrastra tickets entre épicas para reorganizar',
      noAssignees: 'Sin asignados',
      dropTicketHere: 'Suelta el ticket aquí',
      collapse: 'Colapsar',
      expand: 'Expandir',
      epicNamePlaceholder: 'Nombre de la épica...',
      ticketTitlePlaceholder: 'Título del ticket...',
      
      // Workbench enhancements
      description: 'Descripción',
      blockedReason: 'Razón del Bloqueo',
      ticketLifecycle: 'Ciclo de Vida del Ticket',
      activityLog: 'Registro de Actividad',
      complete: 'Completar',
      block: 'Bloquear / Preguntar',
      unblock: 'Desbloquear',
      redirect: 'Redireccionar',
      ticketCompleted: '¡Ticket completado!',
      raiseQuestion: 'Levantar Pregunta',
      pauseTimerNotify: 'Esto pausará tu cronómetro y notificará al dueño',
      timerWillPause: 'El cronómetro se pausará',
      currentTime: 'Tiempo actual',
      whatsBlockingYou: '¿Qué te está bloqueando?',
      describeBlocker: 'Describe el problema que impide el avance...',
      ownerWillBeNotified: 'Se notificará al dueño:',
      submitQuestion: 'Enviar Pregunta',
      redirectTicket: 'Redireccionar Ticket',
      transferResponsibility: 'Transferir responsabilidad a otro miembro del equipo',
      yourTimeSpent: 'Tu tiempo invertido',
      willBeRecorded: 'Se registrará en analytics',
      redirectTo: 'Redireccionar a',
      handoffNote: 'Nota de entrega (obligatorio)',
      whyPassing: '¿Por qué pasas este ticket? ¿Qué contexto deberían saber?',
      ticketWillDisappear: 'Este ticket desaparecerá de tu escritorio inmediatamente',
      selectUser: 'Por favor selecciona un usuario',
      reasonRequired: 'La razón es obligatoria',
      questionRequired: 'La pregunta es obligatoria',
      redirectNow: 'Redireccionar Ahora',
      cancel: 'Cancelar',
      
      // Team Management
      manageTeam: 'Gestiona los miembros de tu equipo de desarrollo',
      totalDevelopers: 'Total Desarrolladores',
      avgTicketsDev: 'Prom. Tickets/Dev',
      avgResponse: 'Resp. Promedio',
      addDeveloper: 'Agregar Desarrollador',
      searchDevelopers: 'Buscar desarrolladores...',
      allRoles: 'Todos los Roles',
      allStatus: 'Todos los Estados',
      email: 'Correo',
      role: 'Rol',
      ticketsProcessed: 'Tickets Procesados',
      projects: 'Proyectos',
      actions: 'Acciones',
      
      // Code & Docs (Admin)
      codeDocRepository: 'Repositorio de Código y Documentación',
      viewAllProjectFiles: 'Ver todos los archivos del proyecto y estadísticas de subida',
      codeFiles: 'Archivos de Código',
      documentation: 'Documentación',
      contributors: 'Contribuidores',
      lastUpdate: 'Última Actualización',
      developerUploadStats: 'Estadísticas de Subida por Desarrollador',
      filesUploadedBy: 'Archivos subidos por cada desarrollador en',
      totalFiles: 'Total Archivos',
      totalSize: 'Tamaño Total',
      lastUpload: 'Última Subida',
      contribution: 'Contribución',
      recentFiles: 'Archivos Recientes',
      latestUploads: 'Últimas subidas en',
      all: 'Todos',
      code: 'Código',
      docs: 'Docs',
      approved: 'Aprobado',
      pendingReview: 'Pendiente',
      
      // Developer Workbench
      developerWorkbench: 'Escritorio del Desarrollador',
      yourAssignedTickets: 'Tus tickets asignados y tareas actuales',
      activeTickets: 'Tickets Activos',
      pendingTickets: 'Tickets Pendientes',
      clickToFilter: 'Clic para filtrar',
      inProgress: 'En progreso',
      today: 'hoy',
      waitingToStart: 'Esperando inicio',
      estimated: 'Est.',
      teamRanking: 'Ranking de Equipos',
      yourTeam: 'Tu equipo',
      ticketsCompleted2: 'tickets completados',
      viewAllTeams: 'Ver Todos los Equipos →',
      filterByDueDate: 'Filtrar por fecha límite:',
      overdue: 'Vencidos',
      thisWeek2: 'Esta Semana',
      later: 'Después',
      showing: 'Mostrando',
      clearAllFilters: 'Limpiar filtros',
      noOverdueTickets: '¡Sin tickets vencidos!',
      nothingDueToday: '¡Nada vence hoy!',
      noTicketsDueThisWeek: '¡Sin tickets esta semana!',
      noActiveTickets: '¡Sin tickets activos!',
      noPendingTickets: '¡Sin tickets pendientes!',
      greatJobOnSchedule: '¡Excelente trabajo manteniéndote al día!',
      allCaughtUp: 'Estás al día.',
      assignedBy: 'Asignado por',
      subtasks: 'Subtareas',
      timeSpent: 'Tiempo usado',
      
      // Developer Uploads Tab
      codeAndDocumentation: 'Código y Documentación',
      uploadCodeAndDocs: 'Sube tus archivos de código y documentación para revisión',
      dropCodeFiles: 'Arrastra archivos de código aquí o haz clic',
      supportsCode: 'Soporta: .js, .ts, .py, .java, .go, .rs, .cpp, .json, .yaml',
      linkToTicket: 'Vincular a Ticket',
      selectTicket: 'Selecciona un ticket...',
      uploadedFiles: 'Archivos Subidos',
      dropDocumentation: 'Arrastra documentación aquí o haz clic',
      supportsDocs: 'Soporta: .md, .pdf, .docx, .txt, .html, .xlsx',
      documentationType: 'Tipo de Documentación',
      apiReference: 'Referencia API',
      userGuide: 'Guía de Usuario',
      technicalSpec: 'Especificación Técnica',
      readme: 'README',
      other: 'Otro',
      uploadedDocumentation: 'Documentación Subida',
      recentUploadActivity: 'Actividad Reciente de Subidas',
      uploaded: 'subió',
      approvedBy: 'Aprobado por',
      
      // Ticket Panel
      ticketDetails: 'Detalles del Ticket',
      description: 'Descripción',
      completeTicket: 'Completar Ticket',
      blockQuestion: 'Bloquear / Pregunta',
      redirect: 'Redirigir',
      
      // Settings Modal
      customizeExperience: 'Personaliza tu experiencia en CoreStream',
      appearance: 'Apariencia',
      theme: 'Tema',
      chooseLightDark: 'Elige modo claro u oscuro',
      light: 'Claro',
      dark: 'Oscuro',
      selectLanguage: 'Selecciona tu idioma preferido',
      emailNotifications: 'Notificaciones por Correo',
      receiveEmailUpdates: 'Recibe correos para actualizaciones importantes',
      pushNotifications: 'Notificaciones Push',
      getNotifiedBrowser: 'Recibe notificaciones en tu navegador',
      mobileNotifications: 'Notificaciones Móviles',
      receiveAlerts: 'Recibe alertas en tu teléfono',
      dueDateReminders: 'Recordatorios de Fechas',
      getRemindedDeadlines: 'Recibe recordatorios antes de las fechas límite',
      account: 'Cuenta',
      editProfile: 'Editar Perfil',
      changePassword: 'Cambiar Contraseña',
      updateCredentials: 'Actualiza tus credenciales',
      connectedApps: 'Apps Conectadas',
      manageIntegrations: 'Gestiona integraciones',
      exportData: 'Exportar Datos',
      downloadYourData: 'Descarga tus datos',
      helpSupport: 'Ayuda y Soporte',
      getAssistance: 'Obtén asistencia',
      dangerZone: 'Zona de Peligro',
      deleteAccount: 'Eliminar Cuenta',
      permanentlyDelete: 'Elimina permanentemente tu cuenta y todos tus datos',
      delete: 'Eliminar',
      cancel: 'Cancelar',
      saveChanges: 'Guardar Cambios',
      
      // Sidebar
      applications: 'Aplicaciones',
      sortDefault: 'Orden: Predeterminado',
      sortMostPending: 'Orden: Más Pendientes',
      sortMostDelayed: 'Orden: Más Retrasados',
      epics: 'épicas',
      archivedApps: 'Apps Archivadas',
      filtered: 'Filtrado',
    },
    fr: {
      // Header
      administrator: 'Administrateur',
      developer: 'Développeur',
      settings: 'Paramètres',
      notifications: 'Notifications',
      
      // Admin Tabs
      projectCanvas: 'Canevas de Projet',
      analytics: 'Analytiques',
      codeDocs: 'Code et Docs',
      teamManagement: 'Gestion d\'Équipe',
      
      // Developer Tabs
      myWorkbench: 'Mon Espace',
      codeAndDocs: 'Code et Docs',
      
      // Project Canvas
      active: 'Actif',
      dragEpicsToReorder: 'Glissez les épiques pour réordonner. Cliquez sur les en-têtes pour afficher/masquer.',
      projectHasDelayedTickets: 'Le projet a des tickets en retard',
      ticketsOverdue: 'ticket(s) ont dépassé leur date limite',
      viewAllDelayed: 'Voir Tous les Retards',
      delayed: 'en retard',
      epicOverdue: 'Épique en Retard!',
      due: 'Échéance',
      showTickets: 'Afficher Tickets',
      hideTickets: 'Masquer Tickets',
      tickets: 'tickets',
      unassigned: 'Non assigné',
      completed: 'Terminés',
      daysOverdue: 'j en retard',
      dueToday: 'Échéance aujourd\'hui',
      daysLeft: 'j restants',
      causingDelay: 'Ce ticket cause un retard',
      addTicket: 'Ajouter Ticket',
      addEpic: 'Ajouter Épique',
      
      // Analytics
      commandCenter: 'Centre de Commande',
      teamPerformanceMetrics: 'Métriques de performance et santé du projet',
      totalTickets: 'Total Tickets',
      blocked: 'Bloqués',
      avgTime: 'Temps Moy.',
      thisWeek: 'cette semaine',
      critical: 'critiques',
      vsLastWeek: 'vs semaine dernière',
      teamPerformanceByProject: 'Performance par Projet',
      sortBy: 'Trier par',
      ticketsCompleted: 'Tickets Terminés',
      pending: 'En Attente',
      name: 'Nom',
      questions: 'Questions',
      redirects: 'Redirections',
      burndownChart: 'Graphique d\'Avancement',
      ideal: 'Idéal',
      actual: 'Réel',
      activityHeatmap: 'Carte d\'Activité',
      
      // Team Management
      manageTeam: 'Gérez les membres de votre équipe',
      totalDevelopers: 'Total Développeurs',
      avgTicketsDev: 'Moy. Tickets/Dev',
      avgResponse: 'Rép. Moyenne',
      addDeveloper: 'Ajouter Développeur',
      searchDevelopers: 'Rechercher développeurs...',
      allRoles: 'Tous les Rôles',
      allStatus: 'Tous les Statuts',
      email: 'Email',
      role: 'Rôle',
      ticketsProcessed: 'Tickets Traités',
      projects: 'Projets',
      actions: 'Actions',
      
      // Code & Docs (Admin)
      codeDocRepository: 'Dépôt de Code et Documentation',
      viewAllProjectFiles: 'Voir tous les fichiers et statistiques',
      codeFiles: 'Fichiers Code',
      documentation: 'Documentation',
      contributors: 'Contributeurs',
      lastUpdate: 'Dernière Mise à Jour',
      developerUploadStats: 'Statistiques de Téléchargement',
      filesUploadedBy: 'Fichiers téléchargés par développeur dans',
      totalFiles: 'Total Fichiers',
      totalSize: 'Taille Totale',
      lastUpload: 'Dernier Téléchargement',
      contribution: 'Contribution',
      recentFiles: 'Fichiers Récents',
      latestUploads: 'Derniers téléchargements dans',
      all: 'Tous',
      code: 'Code',
      docs: 'Docs',
      approved: 'Approuvé',
      pendingReview: 'En Attente',
      
      // Developer Workbench
      developerWorkbench: 'Espace Développeur',
      yourAssignedTickets: 'Vos tickets assignés et tâches actuelles',
      activeTickets: 'Tickets Actifs',
      pendingTickets: 'Tickets en Attente',
      clickToFilter: 'Cliquez pour filtrer',
      inProgress: 'En cours',
      today: 'aujourd\'hui',
      waitingToStart: 'En attente de démarrage',
      estimated: 'Est.',
      teamRanking: 'Classement Équipes',
      yourTeam: 'Votre équipe',
      ticketsCompleted2: 'tickets terminés',
      viewAllTeams: 'Voir Toutes les Équipes →',
      filterByDueDate: 'Filtrer par échéance:',
      overdue: 'En Retard',
      thisWeek2: 'Cette Semaine',
      later: 'Plus Tard',
      showing: 'Affichage',
      clearAllFilters: 'Effacer les filtres',
      noOverdueTickets: 'Pas de tickets en retard!',
      nothingDueToday: 'Rien pour aujourd\'hui!',
      noTicketsDueThisWeek: 'Pas de tickets cette semaine!',
      noActiveTickets: 'Pas de tickets actifs!',
      noPendingTickets: 'Pas de tickets en attente!',
      greatJobOnSchedule: 'Excellent travail!',
      allCaughtUp: 'Vous êtes à jour.',
      assignedBy: 'Assigné par',
      subtasks: 'Sous-tâches',
      timeSpent: 'Temps passé',
      
      // Developer Uploads Tab
      codeAndDocumentation: 'Code et Documentation',
      uploadCodeAndDocs: 'Téléchargez vos fichiers pour révision',
      dropCodeFiles: 'Déposez les fichiers code ici ou cliquez',
      supportsCode: 'Supporte: .js, .ts, .py, .java, .go, .rs, .cpp, .json, .yaml',
      linkToTicket: 'Lier au Ticket',
      selectTicket: 'Sélectionnez un ticket...',
      uploadedFiles: 'Fichiers Téléchargés',
      dropDocumentation: 'Déposez la documentation ici ou cliquez',
      supportsDocs: 'Supporte: .md, .pdf, .docx, .txt, .html, .xlsx',
      documentationType: 'Type de Documentation',
      apiReference: 'Référence API',
      userGuide: 'Guide Utilisateur',
      technicalSpec: 'Spécification Technique',
      readme: 'README',
      other: 'Autre',
      uploadedDocumentation: 'Documentation Téléchargée',
      recentUploadActivity: 'Activité Récente',
      uploaded: 'a téléchargé',
      approvedBy: 'Approuvé par',
      
      // Ticket Panel
      ticketDetails: 'Détails du Ticket',
      description: 'Description',
      completeTicket: 'Terminer Ticket',
      blockQuestion: 'Bloquer / Question',
      redirect: 'Rediriger',
      
      // Settings Modal
      customizeExperience: 'Personnalisez votre expérience CoreStream',
      appearance: 'Apparence',
      theme: 'Thème',
      chooseLightDark: 'Choisissez mode clair ou sombre',
      light: 'Clair',
      dark: 'Sombre',
      selectLanguage: 'Sélectionnez votre langue préférée',
      emailNotifications: 'Notifications Email',
      receiveEmailUpdates: 'Recevez des emails pour les mises à jour',
      pushNotifications: 'Notifications Push',
      getNotifiedBrowser: 'Soyez notifié dans votre navigateur',
      mobileNotifications: 'Notifications Mobile',
      receiveAlerts: 'Recevez des alertes sur votre téléphone',
      dueDateReminders: 'Rappels d\'Échéance',
      getRemindedDeadlines: 'Soyez rappelé avant les échéances',
      account: 'Compte',
      editProfile: 'Modifier Profil',
      changePassword: 'Changer Mot de Passe',
      updateCredentials: 'Mettez à jour vos identifiants',
      connectedApps: 'Apps Connectées',
      manageIntegrations: 'Gérez les intégrations',
      exportData: 'Exporter Données',
      downloadYourData: 'Téléchargez vos données',
      helpSupport: 'Aide et Support',
      getAssistance: 'Obtenez de l\'aide',
      dangerZone: 'Zone Dangereuse',
      deleteAccount: 'Supprimer Compte',
      permanentlyDelete: 'Supprimez définitivement votre compte et données',
      delete: 'Supprimer',
      cancel: 'Annuler',
      saveChanges: 'Sauvegarder',
      
      // Sidebar
      applications: 'Applications',
      sortDefault: 'Tri: Par Défaut',
      sortMostPending: 'Tri: Plus en Attente',
      sortMostDelayed: 'Tri: Plus en Retard',
      epics: 'épiques',
      archivedApps: 'Apps Archivées',
      filtered: 'Filtré',
    },
    de: {
      // Header
      administrator: 'Administrator',
      developer: 'Entwickler',
      settings: 'Einstellungen',
      notifications: 'Benachrichtigungen',
      
      // Admin Tabs
      projectCanvas: 'Projekt-Canvas',
      analytics: 'Analytik',
      codeDocs: 'Code & Doku',
      teamManagement: 'Teamverwaltung',
      
      // Developer Tabs
      myWorkbench: 'Mein Arbeitsbereich',
      codeAndDocs: 'Code & Doku',
      
      // Common terms
      active: 'Aktiv',
      completed: 'Abgeschlossen',
      pending: 'Ausstehend',
      blocked: 'Blockiert',
      tickets: 'Tickets',
      due: 'Fällig',
      today: 'heute',
      
      // Settings
      customizeExperience: 'Passen Sie Ihre CoreStream-Erfahrung an',
      appearance: 'Erscheinung',
      theme: 'Thema',
      chooseLightDark: 'Wählen Sie Hell- oder Dunkelmodus',
      light: 'Hell',
      dark: 'Dunkel',
      selectLanguage: 'Wählen Sie Ihre bevorzugte Sprache',
      account: 'Konto',
      cancel: 'Abbrechen',
      saveChanges: 'Änderungen Speichern',
      
      // Sidebar
      applications: 'Anwendungen',
      sortDefault: 'Sortierung: Standard',
      sortMostPending: 'Sortierung: Meiste Ausstehend',
      sortMostDelayed: 'Sortierung: Meiste Verzögert',
      epics: 'Epics',
      archivedApps: 'Archivierte Apps',
      filtered: 'Gefiltert',
      
      // Fill in remaining with English as fallback
      dragEpicsToReorder: 'Ziehen Sie Epics zum Neuordnen. Klicken Sie auf Header zum Ein-/Ausblenden.',
      projectHasDelayedTickets: 'Projekt hat verzögerte Tickets',
      ticketsOverdue: 'Ticket(s) sind überfällig',
      viewAllDelayed: 'Alle Verzögerten Anzeigen',
      delayed: 'verzögert',
      epicOverdue: 'Epic Überfällig!',
      showTickets: 'Tickets Anzeigen',
      hideTickets: 'Tickets Ausblenden',
      unassigned: 'Nicht zugewiesen',
      daysOverdue: 't überfällig',
      dueToday: 'Heute fällig',
      daysLeft: 't verbleibend',
      causingDelay: 'Dieses Ticket verursacht Verzögerung',
      addTicket: 'Ticket Hinzufügen',
      addEpic: 'Epic Hinzufügen',
      commandCenter: 'Kommandozentrale',
      teamPerformanceMetrics: 'Teamleistungsmetriken und Projektgesundheit',
      totalTickets: 'Gesamt Tickets',
      avgTime: 'Durchschn. Zeit',
      thisWeek: 'diese Woche',
      critical: 'kritisch',
      vsLastWeek: 'vs letzte Woche',
      developerWorkbench: 'Entwickler-Arbeitsbereich',
      yourAssignedTickets: 'Ihre zugewiesenen Tickets und Aufgaben',
      activeTickets: 'Aktive Tickets',
      pendingTickets: 'Ausstehende Tickets',
      clickToFilter: 'Klicken zum Filtern',
      inProgress: 'In Bearbeitung',
      waitingToStart: 'Warten auf Start',
      estimated: 'Gesch.',
      teamRanking: 'Team-Ranking',
      yourTeam: 'Ihr Team',
      ticketsCompleted2: 'Tickets abgeschlossen',
      viewAllTeams: 'Alle Teams Anzeigen →',
      filterByDueDate: 'Nach Fälligkeit filtern:',
      overdue: 'Überfällig',
      thisWeek2: 'Diese Woche',
      later: 'Später',
      showing: 'Zeige',
      clearAllFilters: 'Filter löschen',
      all: 'Alle',
      assignedBy: 'Zugewiesen von',
      subtasks: 'Unteraufgaben',
      timeSpent: 'Verbrachte Zeit',
    },
    pt: {
      // Header
      administrator: 'Administrador',
      developer: 'Desenvolvedor',
      settings: 'Configurações',
      notifications: 'Notificações',
      
      // Admin Tabs
      projectCanvas: 'Canvas do Projeto',
      analytics: 'Análises',
      codeDocs: 'Código e Docs',
      teamManagement: 'Gestão de Equipe',
      
      // Developer Tabs
      myWorkbench: 'Meu Espaço',
      codeAndDocs: 'Código e Docs',
      
      // Common terms
      active: 'Ativo',
      completed: 'Concluídos',
      pending: 'Pendentes',
      blocked: 'Bloqueados',
      tickets: 'tickets',
      due: 'Vencimento',
      today: 'hoje',
      
      // Settings
      customizeExperience: 'Personalize sua experiência no CoreStream',
      appearance: 'Aparência',
      theme: 'Tema',
      chooseLightDark: 'Escolha modo claro ou escuro',
      light: 'Claro',
      dark: 'Escuro',
      selectLanguage: 'Selecione seu idioma preferido',
      account: 'Conta',
      cancel: 'Cancelar',
      saveChanges: 'Salvar Alterações',
      
      // Sidebar
      applications: 'Aplicações',
      sortDefault: 'Ordem: Padrão',
      sortMostPending: 'Ordem: Mais Pendentes',
      sortMostDelayed: 'Ordem: Mais Atrasados',
      epics: 'épicos',
      archivedApps: 'Apps Arquivados',
      filtered: 'Filtrado',
      
      // Fill in remaining
      dragEpicsToReorder: 'Arraste épicos para reordenar. Clique nos cabeçalhos para mostrar/ocultar.',
      projectHasDelayedTickets: 'Projeto tem tickets atrasados',
      ticketsOverdue: 'ticket(s) passaram do prazo',
      viewAllDelayed: 'Ver Todos Atrasados',
      delayed: 'atrasados',
      epicOverdue: 'Épico Atrasado!',
      showTickets: 'Mostrar Tickets',
      hideTickets: 'Ocultar Tickets',
      unassigned: 'Não atribuído',
      daysOverdue: 'd atrasado',
      dueToday: 'Vence hoje',
      daysLeft: 'd restantes',
      causingDelay: 'Este ticket está causando atraso',
      addTicket: 'Adicionar Ticket',
      addEpic: 'Adicionar Épico',
      commandCenter: 'Centro de Comando',
      teamPerformanceMetrics: 'Métricas de desempenho da equipe e saúde do projeto',
      totalTickets: 'Total de Tickets',
      avgTime: 'Tempo Médio',
      thisWeek: 'esta semana',
      critical: 'críticos',
      vsLastWeek: 'vs semana passada',
      developerWorkbench: 'Área do Desenvolvedor',
      yourAssignedTickets: 'Seus tickets atribuídos e tarefas atuais',
      activeTickets: 'Tickets Ativos',
      pendingTickets: 'Tickets Pendentes',
      clickToFilter: 'Clique para filtrar',
      inProgress: 'Em progresso',
      waitingToStart: 'Aguardando início',
      estimated: 'Est.',
      teamRanking: 'Ranking de Equipes',
      yourTeam: 'Sua equipe',
      ticketsCompleted2: 'tickets concluídos',
      viewAllTeams: 'Ver Todas as Equipes →',
      filterByDueDate: 'Filtrar por prazo:',
      overdue: 'Atrasados',
      thisWeek2: 'Esta Semana',
      later: 'Depois',
      showing: 'Mostrando',
      clearAllFilters: 'Limpar filtros',
      all: 'Todos',
      assignedBy: 'Atribuído por',
      subtasks: 'Subtarefas',
      timeSpent: 'Tempo gasto',
    }
  };

  // Translation helper function
  const t = (key) => {
    return translations[language]?.[key] || translations['en'][key] || key;
  };

  // Mock Data
  const apps = [
    { id: 0, name: 'Payment Gateway', color: '#2563EB', icon: '💳' },
    { id: 1, name: 'User Dashboard', color: '#7C3AED', icon: '📊' },
    { id: 2, name: 'API Platform', color: '#059669', icon: '🔌' },
  ];

  // Epics as state for drag-drop functionality
  const [epics, setEpics] = useState([
    {
      id: 0,
      name: 'Stripe Integration',
      progress: 65,
      dueDate: '2025-01-15',
      tickets: [
        { id: 't1', title: 'Design Checkout Flow', status: 'done', assignee: 'Ana', assigneeId: 1, subtasks: 4, completed: 4, time: '2h 15m', timeSpent: 8100, dueDate: '2024-12-20', completedDate: '2024-12-18', epicId: 0 },
        { id: 't2', title: 'Implement Payment API', status: 'blocked', assignee: 'Carlos', assigneeId: 2, subtasks: 6, completed: 2, time: '4h 30m', timeSpent: 16200, dueDate: '2024-12-25', blockReason: 'Need API credentials', epicId: 0 },
        { id: 't3', title: 'Handle Webhooks', status: 'progress', assignee: 'Ana', assigneeId: 1, subtasks: 5, completed: 3, time: '1h 45m', timeSpent: 6300, dueDate: '2025-01-05', epicId: 0 },
      ]
    },
    {
      id: 1,
      name: 'Refund Processing',
      progress: 30,
      dueDate: '2025-01-20',
      tickets: [
        { id: 't4', title: 'Refund Request Form', status: 'progress', assignee: 'Maria', assigneeId: 3, subtasks: 3, completed: 1, time: '45m', timeSpent: 2700, dueDate: '2025-01-10', epicId: 1 },
        { id: 't5', title: 'Admin Approval Flow', status: 'todo', assignee: 'Carlos', assigneeId: 2, subtasks: 4, completed: 0, time: '0m', timeSpent: 0, dueDate: '2025-01-18', epicId: 1 },
      ]
    },
    {
      id: 2,
      name: 'Invoice Generation',
      progress: 10,
      dueDate: '2024-12-28',
      tickets: [
        { id: 't6', title: 'PDF Template Design', status: 'todo', assignee: null, assigneeId: null, subtasks: 5, completed: 0, time: '0m', timeSpent: 0, dueDate: '2024-12-22', epicId: 2 },
        { id: 't7', title: 'Email Delivery System', status: 'todo', assignee: null, assigneeId: null, subtasks: 3, completed: 0, time: '0m', timeSpent: 0, dueDate: '2024-12-26', epicId: 2 },
      ]
    },
  ]);

  // Timer effect for active tickets
  useEffect(() => {
    const interval = setInterval(() => {
      setTicketTimers(prev => {
        const updated = { ...prev };
        Object.keys(updated).forEach(ticketId => {
          if (updated[ticketId].isRunning) {
            updated[ticketId] = {
              ...updated[ticketId],
              elapsed: updated[ticketId].elapsed + 1
            };
          }
        });
        return updated;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Format seconds to time string
  const formatTime = (seconds) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    if (hrs > 0) return `${hrs}h ${mins}m ${secs}s`;
    if (mins > 0) return `${mins}m ${secs}s`;
    return `${secs}s`;
  };

  // Start timer for a ticket
  const startTimer = (ticketId) => {
    setTicketTimers(prev => ({
      ...prev,
      [ticketId]: {
        startTime: Date.now(),
        elapsed: prev[ticketId]?.elapsed || 0,
        isRunning: true
      }
    }));
  };

  // Pause timer for a ticket
  const pauseTimer = (ticketId) => {
    setTicketTimers(prev => ({
      ...prev,
      [ticketId]: {
        ...prev[ticketId],
        isRunning: false
      }
    }));
  };

  // Handle drag start
  const handleDragStart = (e, ticket, epicId) => {
    setDraggingTicket({ ...ticket, fromEpicId: epicId });
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', JSON.stringify({ ticketId: ticket.id, fromEpicId: epicId }));
  };

  // Handle drag over
  const handleDragOver = (e, epicId) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverEpic(epicId);
  };

  // Handle drag leave
  const handleDragLeave = (e) => {
    setDragOverEpic(null);
  };

  // Handle drop - move ticket to new epic
  const handleDrop = (e, targetEpicId) => {
    e.preventDefault();
    setDragOverEpic(null);
    
    if (!draggingTicket || draggingTicket.fromEpicId === targetEpicId) {
      setDraggingTicket(null);
      return;
    }

    const { fromEpicId } = draggingTicket;
    
    // Simulate API call: PATCH /tickets/{id}
    console.log(`API PATCH /tickets/${draggingTicket.id}`, { epic_id: targetEpicId });
    
    setEpics(prev => {
      const updated = prev.map(epic => {
        if (epic.id === fromEpicId) {
          return {
            ...epic,
            tickets: epic.tickets.filter(t => t.id !== draggingTicket.id)
          };
        }
        if (epic.id === targetEpicId) {
          return {
            ...epic,
            tickets: [...epic.tickets, { ...draggingTicket, epicId: targetEpicId }]
          };
        }
        return epic;
      });
      return updated;
    });

    // Log event
    setTicketEvents(prev => [...prev, {
      type: 'MOVE',
      ticketId: draggingTicket.id,
      fromEpicId,
      toEpicId: targetEpicId,
      timestamp: new Date().toISOString(),
      user: currentUser
    }]);

    setDraggingTicket(null);
  };

  // Create new epic
  const handleCreateEpic = (name) => {
    if (!name.trim()) return;
    
    const newEpic = {
      id: Date.now(),
      name: name.trim(),
      progress: 0,
      dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      tickets: []
    };
    
    setEpics(prev => [...prev, newEpic]);
    setNewEpicName('');
    
    // Keep focus for creating more
    setTimeout(() => {
      newEpicInputRef.current?.focus();
    }, 100);
  };

  // Create new ticket in epic
  const handleCreateTicket = (epicId, title) => {
    if (!title.trim()) return;
    
    const newTicket = {
      id: `t${Date.now()}`,
      title: title.trim(),
      status: 'todo',
      assignee: null,
      assigneeId: null,
      subtasks: 0,
      completed: 0,
      time: '0m',
      timeSpent: 0,
      dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      epicId
    };
    
    setEpics(prev => prev.map(epic => 
      epic.id === epicId 
        ? { ...epic, tickets: [...epic.tickets, newTicket] }
        : epic
    ));
    
    setNewTicketName('');
    setCreatingTicketInEpic(null);
  };

  // Handle raise question
  const handleRaiseQuestion = (ticket, question) => {
    if (!question.trim()) return;
    
    // Pause timer
    pauseTimer(ticket.id);
    
    // Update ticket status
    setEpics(prev => prev.map(epic => ({
      ...epic,
      tickets: epic.tickets.map(t => 
        t.id === ticket.id 
          ? { ...t, status: 'blocked', blockReason: question }
          : t
      )
    })));
    
    // Log event
    setTicketEvents(prev => [...prev, {
      type: 'QUESTION',
      ticketId: ticket.id,
      question,
      timestamp: new Date().toISOString(),
      user: currentUser
    }]);
    
    // Simulate notification to App Owner
    console.log(`NOTIFICATION to App Owner: Question raised on ticket ${ticket.id}: ${question}`);
    
    setQuestionText('');
    setShowQuestionModal(false);
    setSelectedTicket(prev => prev ? { ...prev, status: 'blocked', blockReason: question } : null);
  };

  // Handle redirect
  const handleRedirect = (ticket, toUser, reason) => {
    if (!toUser || !reason.trim()) return;
    
    // Calculate time spent
    const timer = ticketTimers[ticket.id];
    const timeSpent = timer?.elapsed || 0;
    
    // Stop timer
    pauseTimer(ticket.id);
    
    // Update ticket
    setEpics(prev => prev.map(epic => ({
      ...epic,
      tickets: epic.tickets.map(t => 
        t.id === ticket.id 
          ? { 
              ...t, 
              status: 'todo', 
              assignee: toUser.name, 
              assigneeId: toUser.id,
              timeSpent: (t.timeSpent || 0) + timeSpent
            }
          : t
      )
    })));
    
    // Log event
    setTicketEvents(prev => [...prev, {
      type: 'REDIRECT',
      ticketId: ticket.id,
      from: currentUser,
      to: toUser,
      reason,
      timeSpent,
      timestamp: new Date().toISOString()
    }]);
    
    // Simulate API call
    console.log(`API PATCH /tickets/${ticket.id}`, { 
      assignee_id: toUser.id,
      status: 'todo'
    });
    console.log(`API POST /ticket_events`, {
      type: 'REDIRECT',
      ticket_id: ticket.id,
      from_user_id: currentUser.id,
      to_user_id: toUser.id,
      reason,
      time_spent: timeSpent
    });
    
    setRedirectReason('');
    setRedirectToUser(null);
    setShowRedirectModal(false);
    setSelectedTicket(null);
  };

  // Handle complete ticket
  const handleCompleteTicket = (ticket) => {
    const timer = ticketTimers[ticket.id];
    const timeSpent = timer?.elapsed || 0;
    
    pauseTimer(ticket.id);
    
    setEpics(prev => prev.map(epic => ({
      ...epic,
      tickets: epic.tickets.map(t => 
        t.id === ticket.id 
          ? { 
              ...t, 
              status: 'done',
              completed: t.subtasks,
              completedDate: new Date().toISOString().split('T')[0],
              timeSpent: (t.timeSpent || 0) + timeSpent
            }
          : t
      )
    })));
    
    setTicketEvents(prev => [...prev, {
      type: 'COMPLETE',
      ticketId: ticket.id,
      timeSpent,
      timestamp: new Date().toISOString(),
      user: currentUser
    }]);
    
    setSelectedTicket(null);
  };

  // Get unique assignees for an epic (for collapsed view avatars)
  const getEpicAssignees = (epic) => {
    const assignees = {};
    epic.tickets.forEach(t => {
      if (t.assignee && !assignees[t.assigneeId]) {
        assignees[t.assigneeId] = { name: t.assignee, id: t.assigneeId };
      }
    });
    return Object.values(assignees);
  };

  // Helper function to check if a date is overdue
  const isOverdue = (dateStr) => {
    if (!dateStr) return false;
    const today = new Date();
    const dueDate = new Date(dateStr);
    return dueDate < today;
  };

  // Helper function to get days until due or overdue
  const getDaysStatus = (dateStr) => {
    if (!dateStr) return null;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const dueDate = new Date(dateStr);
    dueDate.setHours(0, 0, 0, 0);
    const diffTime = dueDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  // Helper to format date
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  // Check if epic has delayed tickets
  const hasDelayedTickets = (epic) => {
    return epic.tickets.some(t => t.status !== 'done' && isOverdue(t.dueDate));
  };

  // Get delayed tickets count
  const getDelayedTicketsCount = (epic) => {
    return epic.tickets.filter(t => t.status !== 'done' && isOverdue(t.dueDate)).length;
  };

  // Team members with Team Lead role
  const [teamMembersData, setTeamMembersData] = useState([
    { id: 1, name: 'Ana García', avatar: 'AG', role: 'Frontend Dev', email: 'ana.garcia@company.com', ticketsProcessed: 24, questions: 3, redirects: 5, avgTime: '1h 45m', pending: 3, blocked: 1, status: 'active', isTeamLead: true },
    { id: 2, name: 'Carlos Ruiz', avatar: 'CR', role: 'Backend Dev', email: 'carlos.ruiz@company.com', ticketsProcessed: 18, questions: 8, redirects: 2, avgTime: '2h 30m', pending: 5, blocked: 2, status: 'active', isTeamLead: false },
    { id: 3, name: 'Maria López', avatar: 'ML', role: 'Full Stack', email: 'maria.lopez@company.com', ticketsProcessed: 31, questions: 2, redirects: 7, avgTime: '1h 20m', pending: 2, blocked: 0, status: 'active', isTeamLead: true },
    { id: 4, name: 'Pedro Santos', avatar: 'PS', role: 'DevOps', email: 'pedro.santos@company.com', ticketsProcessed: 15, questions: 4, redirects: 3, avgTime: '1h 55m', pending: 4, blocked: 1, status: 'active', isTeamLead: false },
  ]);
  
  // Alias for compatibility
  const teamMembers = teamMembersData;
  
  // Toggle team lead status
  const toggleTeamLead = (memberId) => {
    setTeamMembersData(prev => prev.map(member => 
      member.id === memberId ? { ...member, isTeamLead: !member.isTeamLead } : member
    ));
  };
  
  // Current user simulation (for demo - Ana García is a team lead)
  const currentUser = teamMembersData.find(m => m.id === 1);

  // Project-specific performance data
  const projectPerformance = [
    {
      projectId: 0,
      projectName: 'Payment Gateway',
      projectIcon: '💳',
      projectColor: '#2563EB',
      members: [
        { id: 1, name: 'Ana García', avatar: 'AG', role: 'Frontend Dev', ticketsProcessed: 12, pending: 2, blocked: 1, questions: 2, redirects: 3, avgTime: '1h 30m' },
        { id: 2, name: 'Carlos Ruiz', avatar: 'CR', role: 'Backend Dev', ticketsProcessed: 8, pending: 3, blocked: 1, questions: 5, redirects: 1, avgTime: '2h 15m' },
        { id: 3, name: 'Maria López', avatar: 'ML', role: 'Full Stack', ticketsProcessed: 15, pending: 1, blocked: 0, questions: 1, redirects: 4, avgTime: '1h 10m' },
      ]
    },
    {
      projectId: 1,
      projectName: 'User Dashboard',
      projectIcon: '📊',
      projectColor: '#7C3AED',
      members: [
        { id: 1, name: 'Ana García', avatar: 'AG', role: 'Frontend Dev', ticketsProcessed: 8, pending: 1, blocked: 0, questions: 1, redirects: 1, avgTime: '1h 45m' },
        { id: 3, name: 'Maria López', avatar: 'ML', role: 'Full Stack', ticketsProcessed: 10, pending: 1, blocked: 0, questions: 0, redirects: 2, avgTime: '1h 25m' },
        { id: 4, name: 'Pedro Santos', avatar: 'PS', role: 'DevOps', ticketsProcessed: 6, pending: 2, blocked: 1, questions: 2, redirects: 1, avgTime: '2h 00m' },
      ]
    },
    {
      projectId: 2,
      projectName: 'API Platform',
      projectIcon: '🔌',
      projectColor: '#059669',
      members: [
        { id: 2, name: 'Carlos Ruiz', avatar: 'CR', role: 'Backend Dev', ticketsProcessed: 10, pending: 2, blocked: 1, questions: 3, redirects: 1, avgTime: '2h 45m' },
        { id: 3, name: 'Maria López', avatar: 'ML', role: 'Full Stack', ticketsProcessed: 6, pending: 0, blocked: 0, questions: 1, redirects: 1, avgTime: '1h 30m' },
        { id: 4, name: 'Pedro Santos', avatar: 'PS', role: 'DevOps', ticketsProcessed: 9, pending: 2, blocked: 0, questions: 2, redirects: 2, avgTime: '1h 50m' },
      ]
    },
  ];

  const myTickets = [
    { id: 't3', title: 'Handle Webhooks', epic: 'Stripe Integration', status: 'progress', subtasks: ['Setup endpoint', 'Parse events', 'Update DB', 'Send notifications', 'Error handling'], completed: [true, true, true, false, false], time: '1h 45m', assignedBy: 'Carlos Ruiz', assignedByAvatar: 'CR', estimatedTime: '3h 00m', dueDate: '2025-01-05' },
    { id: 't4', title: 'Refund Request Form', epic: 'Refund Processing', status: 'progress', subtasks: ['UI Design', 'Form validation', 'API integration'], completed: [true, false, false], time: '45m', assignedBy: 'Maria López', assignedByAvatar: 'ML', estimatedTime: '2h 00m', dueDate: '2024-12-28' },
    { id: 't6', title: 'PDF Template Design', epic: 'Invoice Generation', status: 'todo', subtasks: ['Header layout', 'Line items table', 'Footer with totals', 'Company branding', 'QR code'], completed: [false, false, false, false, false], time: '0m', assignedBy: 'Carlos Ruiz', assignedByAvatar: 'CR', estimatedTime: '4h 30m', dueDate: '2024-12-22' },
  ];

  const getStatusColor = (status) => {
    switch(status) {
      case 'done': return 'bg-emerald-500';
      case 'blocked': return 'bg-amber-500';
      case 'progress': return 'bg-blue-500';
      default: return 'bg-slate-300';
    }
  };

  const getStatusBorder = (status) => {
    switch(status) {
      case 'blocked': return 'border-l-4 border-amber-500 animate-pulse';
      case 'progress': return 'border-l-4 border-blue-500';
      case 'done': return 'border-l-4 border-emerald-500';
      default: return 'border-l-4 border-slate-200';
    }
  };

  // Navigation Header
  const Header = () => (
    <header className={`${darkMode ? 'bg-slate-950' : 'bg-slate-900'} text-white px-6 py-4 flex items-center justify-between`}>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          {/* CoreStream Logo - Hexagon with orbital arrows */}
          <div className="w-9 h-9">
            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              {/* Central Hexagon */}
              <path d="M24 14L32 19V29L24 34L16 29V19L24 14Z" fill="#3B82F6"/>
              
              {/* Orbital Arrow 1 - Blue top-right */}
              <path d="M30 8C36 10 40 14 42 20" stroke="#4F46E5" strokeWidth="2.5" strokeLinecap="round" fill="none"/>
              <path d="M42 20L44 16L38 17Z" fill="#4F46E5"/>
              
              {/* Orbital Arrow 2 - Green right */}
              <path d="M42 26C42 32 38 38 32 42" stroke="#10B981" strokeWidth="2.5" strokeLinecap="round" fill="none"/>
              <path d="M32 42L36 44L35 38Z" fill="#10B981"/>
              
              {/* Orbital Arrow 3 - Green bottom */}
              <path d="M26 42C20 42 14 38 10 32" stroke="#059669" strokeWidth="2.5" strokeLinecap="round" fill="none"/>
              <path d="M10 32L8 36L14 35Z" fill="#059669"/>
              
              {/* Orbital Arrow 4 - Blue left */}
              <path d="M8 26C6 20 8 14 14 10" stroke="#3B82F6" strokeWidth="2.5" strokeLinecap="round" fill="none"/>
              <path d="M14 10L10 8L11 14Z" fill="#3B82F6"/>
              
              {/* Orbital Arrow 5 - Blue-green top */}
              <path d="M18 6C22 4 28 4 34 8" stroke="#2563EB" strokeWidth="2.5" strokeLinecap="round" fill="none"/>
              <path d="M34 8L30 6L32 12Z" fill="#2563EB"/>
              
              {/* Orange/Yellow accent arrows */}
              <circle cx="38" cy="32" r="2" fill="#F59E0B"/>
              <circle cx="12" cy="20" r="2" fill="#F59E0B"/>
            </svg>
          </div>
          <span className="text-xl font-semibold tracking-tight">CoreStream</span>
        </div>
        <nav className="ml-8 flex gap-1">
          <button 
            onClick={() => setActiveView('admin')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeView === 'admin' ? 'bg-white/10 text-white' : 'text-slate-400 hover:text-white'}`}
          >
            🏗️ {t('administrator')}
          </button>
          <button 
            onClick={() => setActiveView('employee')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeView === 'employee' ? 'bg-white/10 text-white' : 'text-slate-400 hover:text-white'}`}
          >
            👩‍💻 {t('developer')}
          </button>
        </nav>
      </div>
      <div className="flex items-center gap-2">
        {/* Language Selector */}
        <div className="relative">
          <button 
            onClick={() => setShowLanguageDropdown(!showLanguageDropdown)}
            className="flex items-center gap-2 px-3 py-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <span className="text-lg">{currentLanguage.flag}</span>
            <span className="text-sm">{currentLanguage.code.toUpperCase()}</span>
            <span className="text-xs">▼</span>
          </button>
          {showLanguageDropdown && (
            <div className="absolute right-0 top-full mt-1 bg-white rounded-xl shadow-xl border border-slate-200 py-2 z-50 min-w-[160px]">
              {languages.map(lang => (
                <button
                  key={lang.code}
                  onClick={() => { setLanguage(lang.code); setShowLanguageDropdown(false); }}
                  className={`w-full flex items-center gap-3 px-4 py-2 text-left hover:bg-slate-50 transition-colors ${
                    language === lang.code ? 'bg-blue-50 text-blue-700' : 'text-slate-700'
                  }`}
                >
                  <span className="text-lg">{lang.flag}</span>
                  <span className="text-sm">{lang.name}</span>
                  {language === lang.code && <span className="ml-auto text-blue-600">✓</span>}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Dark/Light Mode Toggle */}
        <button 
          onClick={() => setDarkMode(!darkMode)}
          className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          title={darkMode ? t('light') : t('dark')}
        >
          <span className="text-lg">{darkMode ? '☀️' : '🌙'}</span>
        </button>

        {/* Notifications */}
        <button className="p-2 hover:bg-white/10 rounded-lg transition-colors relative" title={t('notifications')}>
          <span className="text-lg">🔔</span>
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>

        {/* Settings */}
        <button 
          onClick={() => setShowSettingsModal(true)}
          className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          title={t('settings')}
        >
          <span className="text-lg">⚙️</span>
        </button>

        {/* User Profile */}
        <div className="flex items-center gap-2 ml-2 pl-4 border-l border-white/20">
          <div className="w-8 h-8 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-full flex items-center justify-center text-sm font-medium">AG</div>
          <span className="text-sm">Ana García</span>
        </div>
      </div>
    </header>
  );

  // App Sidebar
  const AppSidebar = () => {
    // Calculate pending tickets for each app (mock data)
    const appStats = [
      { pending: 3, delayed: 2 },
      { pending: 5, delayed: 0 },
      { pending: 2, delayed: 1 },
    ];

    const sortedApps = [...apps].map((app, idx) => ({ ...app, ...appStats[idx] }));
    
    if (appSortBy === 'pending') {
      sortedApps.sort((a, b) => b.pending - a.pending);
    } else if (appSortBy === 'delayed') {
      sortedApps.sort((a, b) => b.delayed - a.delayed);
    }

    return (
      <aside className={`w-64 ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'} border-r flex flex-col`}>
        <div className="p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className={`text-xs font-semibold uppercase tracking-wider ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('applications')}</h2>
            <button className="w-6 h-6 bg-blue-600 text-white rounded flex items-center justify-center text-lg hover:bg-blue-700 transition-colors">+</button>
          </div>
          
          {/* Sort Options */}
          <div className="mb-4">
            <select 
              value={appSortBy}
              onChange={(e) => setAppSortBy(e.target.value)}
              className={`w-full text-xs border rounded-lg px-2 py-1.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                darkMode 
                  ? 'bg-slate-700 border-slate-600 text-white' 
                  : 'bg-white border-slate-200 text-slate-700'
              }`}
            >
              <option value="default">{t('sortDefault')}</option>
              <option value="pending">{t('sortMostPending')}</option>
              <option value="delayed">{t('sortMostDelayed')}</option>
            </select>
          </div>

          <div className="space-y-1">
            {sortedApps.map((app) => (
              <button
                key={app.id}
                onClick={() => setSelectedApp(app.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all ${
                  selectedApp === app.id 
                    ? darkMode ? 'bg-slate-700 shadow-sm' : 'bg-slate-100 shadow-sm'
                    : darkMode ? 'hover:bg-slate-700' : 'hover:bg-slate-50'
                }`}
              >
                <span className="text-xl">{app.icon}</span>
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-medium truncate ${darkMode ? 'text-white' : 'text-slate-800'}`}>{app.name}</p>
                  <div className="flex items-center gap-2 text-xs">
                    <span className={darkMode ? 'text-slate-400' : 'text-slate-500'}>3 {t('epics')}</span>
                    {app.pending > 0 && (
                      <span className="px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded-full font-medium">{app.pending} {t('pending')}</span>
                    )}
                    {app.delayed > 0 && (
                      <span className="px-1.5 py-0.5 bg-red-100 text-red-700 rounded-full font-medium">{app.delayed} {t('delayed')}</span>
                    )}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
        
        <div className={`mt-auto p-4 border-t ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
          <button className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
            darkMode 
              ? 'text-slate-400 hover:text-white hover:bg-slate-700' 
              : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50'
          }`}>
            <span>📁</span>
            <span className="text-sm">{t('archivedApps')}</span>
          </button>
        </div>
      </aside>
    );
  };

  // Project Canvas (Builder View)
  // Project Canvas (Builder View) - Enhanced with Drag & Drop
  const ProjectCanvas = () => {
    // CSS for pulsing animation
    const pulsingStyle = `
      @keyframes pulse-border {
        0%, 100% { border-color: rgba(251, 146, 60, 0.5); }
        50% { border-color: rgba(251, 146, 60, 1); }
      }
      .animate-pulse-border {
        animation: pulse-border 1.5s ease-in-out infinite;
      }
    `;

    return (
      <div className={`flex-1 overflow-auto p-6 ${darkMode ? 'bg-slate-900' : 'bg-slate-50'}`}>
        <style>{pulsingStyle}</style>
        
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-2">
            <span className="text-2xl">{apps[selectedApp].icon}</span>
            <h1 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{apps[selectedApp].name}</h1>
            <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">{t('active')}</span>
          </div>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
            {t('dragEpicsToReorder')} • {t('dragTicketsBetweenEpics')}
          </p>
        </div>

        {/* Delayed Alert Banner */}
        {epics.some(epic => hasDelayedTickets(epic)) && (
          <div className={`mb-4 p-4 border rounded-xl flex items-center gap-3 ${darkMode ? 'bg-red-900/30 border-red-800' : 'bg-red-50 border-red-200'}`}>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${darkMode ? 'bg-red-800' : 'bg-red-100'}`}>
              <span className="text-xl">⚠️</span>
            </div>
            <div className="flex-1">
              <p className={`text-sm font-semibold ${darkMode ? 'text-red-300' : 'text-red-800'}`}>{t('projectHasDelayedTickets')}</p>
              <p className={`text-xs ${darkMode ? 'text-red-400' : 'text-red-600'}`}>
                {epics.reduce((sum, epic) => sum + getDelayedTicketsCount(epic), 0)} {t('ticketsOverdue')}
              </p>
            </div>
            <button className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${darkMode ? 'bg-red-800 text-red-200 hover:bg-red-700' : 'bg-red-100 text-red-700 hover:bg-red-200'}`}>
              {t('viewAllDelayed')}
            </button>
          </div>
        )}

        <div className="space-y-4">
          {epics.map((epic, idx) => {
            const isExpanded = expandedEpics.includes(epic.id);
            const epicAssignees = getEpicAssignees(epic);
            const isDragOver = dragOverEpic === epic.id;
            
            return (
              <div 
                key={epic.id} 
                className={`rounded-xl shadow-sm border overflow-hidden transition-all ${
                  isDragOver 
                    ? 'ring-2 ring-blue-500 border-blue-500' 
                    : hasDelayedTickets(epic) 
                      ? darkMode ? 'border-red-700 bg-slate-800' : 'border-red-300 bg-white'
                      : darkMode ? 'border-slate-700 bg-slate-800' : 'border-slate-200 bg-white'
                }`}
                onDragOver={(e) => handleDragOver(e, epic.id)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, epic.id)}
              >
                {/* Epic Header - Accordion Style */}
                <div 
                  className={`flex items-center gap-3 p-4 cursor-pointer transition-colors ${
                    hasDelayedTickets(epic) 
                      ? darkMode ? 'bg-gradient-to-r from-red-900/30 to-slate-800 hover:from-red-900/50' : 'bg-gradient-to-r from-red-50 to-white hover:from-red-100'
                      : darkMode ? 'bg-gradient-to-r from-slate-700 to-slate-800 hover:from-slate-600' : 'bg-gradient-to-r from-slate-50 to-white hover:from-slate-100'
                  }`}
                  onClick={() => setExpandedEpics(prev => prev.includes(epic.id) ? prev.filter(i => i !== epic.id) : [...prev, epic.id])}
                >
                  {/* Drag Handle */}
                  <div className={`flex flex-col gap-0.5 cursor-grab ${darkMode ? 'text-slate-500 hover:text-slate-300' : 'text-slate-300 hover:text-slate-500'}`}>
                    <div className="flex gap-0.5"><div className="w-1 h-1 bg-current rounded-full"></div><div className="w-1 h-1 bg-current rounded-full"></div></div>
                    <div className="flex gap-0.5"><div className="w-1 h-1 bg-current rounded-full"></div><div className="w-1 h-1 bg-current rounded-full"></div></div>
                    <div className="flex gap-0.5"><div className="w-1 h-1 bg-current rounded-full"></div><div className="w-1 h-1 bg-current rounded-full"></div></div>
                  </div>
                  
                  {/* Expand/Collapse Toggle */}
                  <button className={`w-8 h-8 flex items-center justify-center rounded-lg transition-all ${
                    isExpanded 
                      ? darkMode ? 'bg-blue-600 text-white' : 'bg-blue-100 text-blue-700'
                      : darkMode ? 'bg-slate-700 text-slate-400 hover:bg-slate-600' : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
                  }`}>
                    <span className={`transform transition-transform text-sm ${isExpanded ? 'rotate-90' : ''}`}>▶</span>
                  </button>
                  
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{epic.name}</h3>
                      
                      {/* Docs Attachment Button */}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setShowEpicDocsModal(epic.id);
                        }}
                        className={`flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium transition-all hover:scale-105 ${
                          (epicDocs[epic.id]?.length || 0) > 0
                            ? 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200'
                            : darkMode ? 'bg-slate-700 text-slate-400 hover:bg-slate-600' : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
                        }`}
                        title={t('attachDocs')}
                      >
                        <span>📎</span>
                        {(epicDocs[epic.id]?.length || 0) > 0 && (
                          <span>{epicDocs[epic.id].length}</span>
                        )}
                      </button>
                      
                      {hasDelayedTickets(epic) && (
                        <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs font-medium rounded-full flex items-center gap-1">
                          <span>🔴</span> {getDelayedTicketsCount(epic)} {t('delayed')}
                        </span>
                      )}
                    </div>
                    <div className={`flex items-center gap-3 text-xs mt-1 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                      <span>{t('due')}: {formatDate(epic.dueDate)}</span>
                      <span>•</span>
                      <span>{epic.tickets.length} {t('tickets')}</span>
                      {(epicDocs[epic.id]?.length || 0) > 0 && (
                        <>
                          <span>•</span>
                          <span className="text-indigo-500">📄 {epicDocs[epic.id].length} docs</span>
                        </>
                      )}
                      {isOverdue(epic.dueDate) && epic.progress < 100 && (
                        <>
                          <span>•</span>
                          <span className="text-red-500 font-medium">{t('epicOverdue')}</span>
                        </>
                      )}
                    </div>
                  </div>
                  
                  {/* Progress Bar & Avatars (shown when collapsed) */}
                  <div className="flex items-center gap-4">
                    {/* Progress */}
                    <div className="flex items-center gap-2">
                      <div className={`w-32 h-2.5 rounded-full overflow-hidden ${darkMode ? 'bg-slate-600' : 'bg-slate-200'}`}>
                        <div className={`h-full rounded-full transition-all ${hasDelayedTickets(epic) ? 'bg-red-500' : 'bg-emerald-500'}`} style={{ width: `${epic.progress}%` }}></div>
                      </div>
                      <span className={`text-sm font-medium ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>{epic.progress}%</span>
                    </div>
                    
                    {/* Assignee Avatars (always visible, more prominent when collapsed) */}
                    <div className="flex items-center">
                      <div className={`flex -space-x-2 ${!isExpanded ? 'scale-110' : ''} transition-transform`}>
                        {epicAssignees.slice(0, 4).map((assignee, i) => (
                          <div 
                            key={assignee.id} 
                            className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium border-2 ${
                              darkMode ? 'border-slate-800' : 'border-white'
                            } ${
                              i === 0 ? 'bg-gradient-to-br from-blue-400 to-blue-600 text-white' :
                              i === 1 ? 'bg-gradient-to-br from-purple-400 to-purple-600 text-white' :
                              i === 2 ? 'bg-gradient-to-br from-emerald-400 to-emerald-600 text-white' :
                              'bg-gradient-to-br from-amber-400 to-amber-600 text-white'
                            }`}
                            title={assignee.name}
                          >
                            {assignee.name.split(' ').map(n => n[0]).join('')}
                          </div>
                        ))}
                        {epicAssignees.length > 4 && (
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium border-2 ${
                            darkMode ? 'bg-slate-600 border-slate-800 text-slate-300' : 'bg-slate-200 border-white text-slate-600'
                          }`}>
                            +{epicAssignees.length - 4}
                          </div>
                        )}
                      </div>
                      {epicAssignees.length === 0 && (
                        <span className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>{t('noAssignees')}</span>
                      )}
                    </div>
                    
                    {/* Expand/Collapse Button */}
                    <button 
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                        isExpanded 
                          ? darkMode ? 'bg-blue-600 text-white' : 'bg-blue-100 text-blue-700'
                          : darkMode ? 'bg-slate-700 text-slate-300 hover:bg-slate-600' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                      }`}
                      onClick={(e) => {
                        e.stopPropagation();
                        setExpandedEpics(prev => prev.includes(epic.id) ? prev.filter(i => i !== epic.id) : [...prev, epic.id]);
                      }}
                    >
                      {isExpanded ? `▲ ${t('collapse')}` : `▼ ${t('expand')}`}
                    </button>
                  </div>
                </div>

                {/* Tickets Grid - Collapsible with Drag & Drop */}
                {isExpanded && (
                  <div className={`p-4 pt-2 ${darkMode ? 'bg-slate-800/50' : 'bg-slate-50/50'}`}>
                    {/* Drop Zone Indicator */}
                    {isDragOver && (
                      <div className={`mb-3 p-3 border-2 border-dashed rounded-lg text-center ${
                        darkMode ? 'border-blue-500 bg-blue-900/20 text-blue-400' : 'border-blue-400 bg-blue-50 text-blue-600'
                      }`}>
                        <span className="text-sm font-medium">📥 {t('dropTicketHere')}</span>
                      </div>
                    )}
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {epic.tickets.map(ticket => {
                        const daysStatus = getDaysStatus(ticket.dueDate);
                        const ticketOverdue = ticket.status !== 'done' && isOverdue(ticket.dueDate);
                        const isBlocked = ticket.status === 'blocked';
                        
                        return (
                          <div 
                            key={ticket.id}
                            draggable
                            onDragStart={(e) => handleDragStart(e, ticket, epic.id)}
                            onDragEnd={() => setDraggingTicket(null)}
                            onClick={() => setSelectedTicket({ ...ticket, epic: epic.name })}
                            className={`rounded-lg p-4 shadow-sm border-2 cursor-grab active:cursor-grabbing hover:shadow-lg transition-all ${
                              draggingTicket?.id === ticket.id ? 'opacity-50 scale-95' : ''
                            } ${
                              isBlocked 
                                ? 'animate-pulse-border border-orange-400' 
                                : ticketOverdue 
                                  ? darkMode ? 'bg-slate-700 border-red-500' : 'bg-white border-red-400'
                                  : darkMode ? `bg-slate-700 border-slate-600 hover:border-blue-500` : `bg-white border-slate-200 hover:border-blue-400`
                            }`}
                          >
                            {/* Drag Handle Indicator */}
                            <div className="flex items-center justify-between mb-2">
                              <div className={`flex gap-0.5 ${darkMode ? 'text-slate-500' : 'text-slate-300'}`}>
                                <div className="w-1 h-1 bg-current rounded-full"></div>
                                <div className="w-1 h-1 bg-current rounded-full"></div>
                                <div className="w-1 h-1 bg-current rounded-full"></div>
                              </div>
                              <span className={`w-2.5 h-2.5 rounded-full ${getStatusColor(ticket.status)}`}></span>
                            </div>
                            
                            {/* Ticket Title */}
                            <h4 className={`text-sm font-medium mb-2 ${darkMode ? 'text-white' : 'text-slate-800'}`}>{ticket.title}</h4>
                            
                            {/* Assignee */}
                            <div className="flex items-center gap-2 mb-3">
                              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs text-white font-medium ${
                                ticket.assignee 
                                  ? 'bg-gradient-to-br from-blue-400 to-blue-600' 
                                  : darkMode ? 'bg-slate-600' : 'bg-slate-300'
                              }`}>
                                {ticket.assignee ? ticket.assignee.charAt(0) : '?'}
                              </div>
                              <span className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{ticket.assignee || t('unassigned')}</span>
                            </div>
                            
                            {/* Due Date Badge */}
                            <div className={`flex items-center gap-2 mb-3 p-2 rounded-lg ${
                              ticketOverdue 
                                ? darkMode ? 'bg-red-900/30' : 'bg-red-50'
                                : daysStatus !== null && daysStatus <= 3 && ticket.status !== 'done'
                                  ? darkMode ? 'bg-amber-900/30' : 'bg-amber-50'
                                  : darkMode ? 'bg-slate-600' : 'bg-slate-50'
                            }`}>
                              <span className="text-xs">📅</span>
                              <span className={`text-xs font-medium flex-1 ${
                                ticketOverdue 
                                  ? darkMode ? 'text-red-400' : 'text-red-700'
                                  : daysStatus !== null && daysStatus <= 3 && ticket.status !== 'done'
                                    ? darkMode ? 'text-amber-400' : 'text-amber-700'
                                    : darkMode ? 'text-slate-300' : 'text-slate-600'
                              }`}>
                                {ticket.status === 'done' && ticket.completedDate 
                                  ? `✓ ${formatDate(ticket.completedDate)}`
                                  : formatDate(ticket.dueDate)
                                }
                              </span>
                              {ticket.status !== 'done' && daysStatus !== null && (
                                <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${
                                  ticketOverdue 
                                    ? 'bg-red-100 text-red-700' 
                                    : daysStatus <= 3 
                                      ? 'bg-amber-100 text-amber-700'
                                      : darkMode ? 'bg-slate-500 text-slate-200' : 'bg-slate-100 text-slate-600'
                                }`}>
                                  {ticketOverdue 
                                    ? `${Math.abs(daysStatus)}d ⚠️` 
                                    : daysStatus === 0 
                                      ? t('today')
                                      : `${daysStatus}d`
                                  }
                                </span>
                              )}
                            </div>
                            
                            {/* Progress & Time */}
                            <div className="flex items-center justify-between">
                              <div className={`flex items-center gap-1 text-xs ${darkMode ? 'text-slate-400' : 'text-slate-400'}`}>
                                <span>✓</span>
                                <span>{ticket.completed}/{ticket.subtasks}</span>
                              </div>
                              <span className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-400'}`}>⏱️ {ticket.time}</span>
                            </div>
                            
                            {/* Block Reason - Pulsing Orange */}
                            {isBlocked && (
                              <div className={`mt-2 p-2 rounded text-xs flex items-center gap-1 ${darkMode ? 'bg-orange-900/30 text-orange-400' : 'bg-orange-50 text-orange-700'} border border-orange-400`}>
                                <span>❓</span> {ticket.blockReason}
                              </div>
                            )}
                            
                            {/* Delayed Warning */}
                            {ticketOverdue && !isBlocked && (
                              <div className={`mt-2 p-2 rounded text-xs flex items-center gap-1 font-medium ${darkMode ? 'bg-red-900/30 text-red-400' : 'bg-red-50 text-red-700'}`}>
                                <span>🚨</span> {t('causingDelay')}
                              </div>
                            )}
                          </div>
                        );
                      })}
                      
                      {/* Inline Ticket Creation */}
                      {creatingTicketInEpic === epic.id ? (
                        <div className={`rounded-lg p-4 border-2 border-dashed ${darkMode ? 'border-blue-500 bg-slate-700' : 'border-blue-400 bg-blue-50'}`}>
                          <input
                            ref={newTicketInputRef}
                            type="text"
                            value={newTicketName}
                            onChange={(e) => setNewTicketName(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter' && newTicketName.trim()) {
                                handleCreateTicket(epic.id, newTicketName);
                              }
                              if (e.key === 'Escape') {
                                setCreatingTicketInEpic(null);
                                setNewTicketName('');
                              }
                            }}
                            onBlur={() => {
                              if (!newTicketName.trim()) {
                                setCreatingTicketInEpic(null);
                              }
                            }}
                            placeholder={t('ticketTitlePlaceholder')}
                            className={`w-full px-3 py-2 rounded-lg border text-sm focus:ring-2 focus:ring-blue-500 outline-none ${
                              darkMode ? 'bg-slate-800 border-slate-600 text-white placeholder-slate-500' : 'bg-white border-slate-200 text-slate-800 placeholder-slate-400'
                            }`}
                            autoFocus
                          />
                          <p className={`text-xs mt-2 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                            ↵ Enter to create • Esc to cancel
                          </p>
                        </div>
                      ) : (
                        <button 
                          onClick={() => {
                            setCreatingTicketInEpic(epic.id);
                            setTimeout(() => newTicketInputRef.current?.focus(), 100);
                          }}
                          className={`border-2 border-dashed rounded-lg p-4 transition-all flex items-center justify-center gap-2 hover:scale-[1.02] ${
                            darkMode 
                              ? 'border-slate-600 text-slate-400 hover:text-blue-400 hover:border-blue-500 hover:bg-slate-700/50' 
                              : 'border-slate-200 text-slate-400 hover:text-blue-600 hover:border-blue-400 hover:bg-blue-50'
                          }`}
                        >
                          <span className="text-lg">+</span>
                          <span className="text-sm font-medium">{t('addTicket')}</span>
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}

          {/* Inline Epic Creation */}
          {isCreatingEpic ? (
            <div className={`rounded-xl p-4 border-2 border-dashed ${darkMode ? 'border-blue-500 bg-slate-800' : 'border-blue-400 bg-blue-50'}`}>
              <div className="flex items-center gap-3">
                <span className="text-xl">📁</span>
                <input
                  ref={newEpicInputRef}
                  type="text"
                  value={newEpicName}
                  onChange={(e) => setNewEpicName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && newEpicName.trim()) {
                      handleCreateEpic(newEpicName);
                    }
                    if (e.key === 'Escape') {
                      setIsCreatingEpic(false);
                      setNewEpicName('');
                    }
                  }}
                  placeholder={t('epicNamePlaceholder')}
                  className={`flex-1 px-4 py-2 rounded-lg border text-sm font-medium focus:ring-2 focus:ring-blue-500 outline-none ${
                    darkMode ? 'bg-slate-700 border-slate-600 text-white placeholder-slate-400' : 'bg-white border-slate-200 text-slate-800 placeholder-slate-400'
                  }`}
                  autoFocus
                />
              </div>
              <p className={`text-xs mt-2 ml-9 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                ↵ Enter to create and add another • Esc to cancel
              </p>
            </div>
          ) : (
            <button 
              onClick={() => {
                setIsCreatingEpic(true);
                setTimeout(() => newEpicInputRef.current?.focus(), 100);
              }}
              className={`w-full border-2 border-dashed rounded-xl p-4 transition-all flex items-center justify-center gap-2 hover:scale-[1.01] ${
                darkMode 
                  ? 'border-slate-600 text-slate-400 hover:text-blue-400 hover:border-blue-500 hover:bg-slate-800/50' 
                  : 'border-slate-300 text-slate-400 hover:text-blue-600 hover:border-blue-400 hover:bg-blue-50'
              }`}
            >
              <span className="text-xl">+</span>
              <span className="font-medium">{t('addEpic')}</span>
            </button>
          )}
        </div>
      </div>
    );
  };

  // Sort function for team members
  const sortMembers = (members) => {
    return [...members].sort((a, b) => {
      let aVal, bVal;
      switch(sortBy) {
        case 'name': aVal = a.name; bVal = b.name; break;
        case 'pending': aVal = a.pending; bVal = b.pending; break;
        case 'blocked': aVal = a.blocked; bVal = b.blocked; break;
        case 'ticketsProcessed': default: aVal = a.ticketsProcessed; bVal = b.ticketsProcessed; break;
      }
      if (sortBy === 'name') {
        return sortOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      }
      return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
    });
  };

  // Analytics Dashboard
  // Analytics Dashboard - Enhanced with Metrics & Heatmap
  const AnalyticsDashboard = () => {
    // Calculate developer metrics
    const calculateMetrics = (member) => {
      const totalHours = parseFloat(member.avgTime?.replace('h', '').replace('m', '').split(' ')[0]) || 1.5;
      const efficiency = (member.ticketsProcessed / totalHours).toFixed(1);
      const blockingIndex = member.ticketsProcessed > 0 
        ? ((member.questions / member.ticketsProcessed) * 100).toFixed(0) 
        : 0;
      const churnIndex = member.ticketsProcessed > 0 
        ? ((member.redirects / (member.ticketsProcessed + member.pending)) * 100).toFixed(0) 
        : 0;
      return { efficiency, blockingIndex, churnIndex };
    };

    // Heatmap data: Developer activity by day of week
    const heatmapData = {
      developers: [
        { name: 'Ana García', avatar: 'AG', data: [4, 6, 8, 7, 3, 0, 0] },
        { name: 'Carlos Ruiz', avatar: 'CR', data: [3, 5, 6, 4, 2, 1, 0] },
        { name: 'Maria López', avatar: 'ML', data: [5, 7, 9, 8, 6, 0, 0] },
        { name: 'Pedro Santos', avatar: 'PS', data: [2, 4, 5, 3, 1, 0, 0] },
      ],
      days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    };

    // Get color intensity for heatmap
    const getHeatmapColor = (value, maxValue) => {
      if (value === 0) return darkMode ? 'bg-slate-700' : 'bg-slate-100';
      const intensity = value / maxValue;
      if (intensity > 0.8) return 'bg-emerald-600';
      if (intensity > 0.6) return 'bg-emerald-500';
      if (intensity > 0.4) return 'bg-emerald-400';
      if (intensity > 0.2) return 'bg-emerald-300';
      return 'bg-emerald-200';
    };

    const maxActivity = Math.max(...heatmapData.developers.flatMap(d => d.data));

    // Get metric status color
    const getMetricStatus = (value, type) => {
      if (type === 'efficiency') {
        if (value >= 5) return { color: 'text-emerald-600', bg: 'bg-emerald-100', status: 'Excellent' };
        if (value >= 3) return { color: 'text-blue-600', bg: 'bg-blue-100', status: 'Good' };
        if (value >= 1.5) return { color: 'text-amber-600', bg: 'bg-amber-100', status: 'Average' };
        return { color: 'text-red-600', bg: 'bg-red-100', status: 'Low' };
      }
      if (type === 'blocking') {
        if (value <= 10) return { color: 'text-emerald-600', bg: 'bg-emerald-100', status: 'Low' };
        if (value <= 25) return { color: 'text-blue-600', bg: 'bg-blue-100', status: 'Normal' };
        if (value <= 40) return { color: 'text-amber-600', bg: 'bg-amber-100', status: 'High' };
        return { color: 'text-red-600', bg: 'bg-red-100', status: 'Critical' };
      }
      if (type === 'churn') {
        if (value <= 15) return { color: 'text-emerald-600', bg: 'bg-emerald-100', status: 'Low' };
        if (value <= 30) return { color: 'text-amber-600', bg: 'bg-amber-100', status: 'Moderate' };
        return { color: 'text-red-600', bg: 'bg-red-100', status: 'High' };
      }
      return { color: 'text-slate-600', bg: 'bg-slate-100', status: '-' };
    };

    return (
      <div className={`flex-1 overflow-auto p-6 ${darkMode ? 'bg-slate-900' : 'bg-slate-50'}`}>
        <div className="mb-6">
          <h1 className={`text-2xl font-bold mb-1 ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('commandCenter')}</h1>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('teamPerformanceMetrics')}</p>
        </div>

        {/* Stats Row - Side by Side using Flex */}
        <div className="flex gap-4 mb-6">
          <div className={`flex-1 rounded-xl p-4 shadow-sm border ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                <span className="text-2xl">📋</span>
              </div>
              <div className="flex-1">
                <p className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>47</p>
                <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('totalTickets')}</p>
              </div>
              <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-700">+12 {t('thisWeek')}</span>
            </div>
          </div>
          
          <div className={`flex-1 rounded-xl p-4 shadow-sm border ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
                <span className="text-2xl">✅</span>
              </div>
              <div className="flex-1">
                <p className="text-2xl font-bold text-emerald-600">31</p>
                <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('completed')}</p>
              </div>
              <span className="px-2 py-1 text-xs font-medium rounded-full bg-emerald-100 text-emerald-700">66%</span>
            </div>
          </div>
          
          <div className={`flex-1 rounded-xl p-4 shadow-sm border ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center">
                <span className="text-2xl">⚠️</span>
              </div>
              <div className="flex-1">
                <p className="text-2xl font-bold text-amber-600">5</p>
                <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('blocked')}</p>
              </div>
              <span className="px-2 py-1 text-xs font-medium rounded-full bg-amber-100 text-amber-700">3 {t('critical')}</span>
            </div>
          </div>
          
          <div className={`flex-1 rounded-xl p-4 shadow-sm border ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center">
                <span className="text-2xl">⏱️</span>
              </div>
              <div className="flex-1">
                <p className="text-2xl font-bold text-indigo-600">1h 52m</p>
                <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('avgTime')}</p>
              </div>
              <span className="px-2 py-1 text-xs font-medium rounded-full bg-indigo-100 text-indigo-700">-15% {t('vsLastWeek')}</span>
            </div>
          </div>
        </div>

        {/* Performance Metrics Section */}
        <div className={`rounded-xl shadow-sm border mb-6 ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
          <div className={`p-4 border-b ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('performanceMetrics')}</h3>
                <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('keyIndicators')}</p>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${darkMode ? 'bg-slate-700 text-slate-300' : 'bg-slate-100 text-slate-600'}`}>
                  {t('lastWeek')}
                </span>
              </div>
            </div>
          </div>
          
          <div className="p-4">
            {/* Metric Explanation Cards */}
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className={`p-4 rounded-xl ${darkMode ? 'bg-slate-700' : 'bg-gradient-to-br from-emerald-50 to-teal-50'}`}>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xl">⚡</span>
                  <span className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('efficiency')}</span>
                </div>
                <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'} mb-2`}>{t('efficiencyDesc')}</p>
                <div className={`text-xs font-mono p-2 rounded ${darkMode ? 'bg-slate-600 text-slate-300' : 'bg-white text-slate-600'}`}>
                  = Tickets Completed / Total Hours
                </div>
              </div>
              
              <div className={`p-4 rounded-xl ${darkMode ? 'bg-slate-700' : 'bg-gradient-to-br from-amber-50 to-orange-50'}`}>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xl">❓</span>
                  <span className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('blockingIndex')}</span>
                </div>
                <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'} mb-2`}>{t('blockingIndexDesc')}</p>
                <div className={`text-xs font-mono p-2 rounded ${darkMode ? 'bg-slate-600 text-slate-300' : 'bg-white text-slate-600'}`}>
                  = (Questions / Total Tickets) × 100
                </div>
              </div>
              
              <div className={`p-4 rounded-xl ${darkMode ? 'bg-slate-700' : 'bg-gradient-to-br from-indigo-50 to-purple-50'}`}>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xl">↪️</span>
                  <span className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('churnIndex')}</span>
                </div>
                <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'} mb-2`}>{t('churnIndexDesc')}</p>
                <div className={`text-xs font-mono p-2 rounded ${darkMode ? 'bg-slate-600 text-slate-300' : 'bg-white text-slate-600'}`}>
                  = (Redirects / Assigned) × 100
                </div>
              </div>
            </div>

            {/* Developer Metrics Table */}
            <table className="w-full">
              <thead>
                <tr className={`text-xs uppercase tracking-wider ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                  <th className="text-left py-3 px-3 font-medium">{t('developer')}</th>
                  <th className="text-center py-3 px-3 font-medium">{t('ticketsCompleted')}</th>
                  <th className="text-center py-3 px-3 font-medium">{t('totalHours')}</th>
                  <th className="text-center py-3 px-3 font-medium">
                    <div className="flex items-center justify-center gap-1">
                      <span>⚡</span> {t('efficiency')}
                    </div>
                  </th>
                  <th className="text-center py-3 px-3 font-medium">
                    <div className="flex items-center justify-center gap-1">
                      <span>❓</span> {t('blockingIndex')}
                    </div>
                  </th>
                  <th className="text-center py-3 px-3 font-medium">
                    <div className="flex items-center justify-center gap-1">
                      <span>↪️</span> {t('churnIndex')}
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody className={`divide-y ${darkMode ? 'divide-slate-700' : 'divide-slate-100'}`}>
                {teamMembers.map(member => {
                  const metrics = calculateMetrics(member);
                  const efficiencyStatus = getMetricStatus(parseFloat(metrics.efficiency), 'efficiency');
                  const blockingStatus = getMetricStatus(parseFloat(metrics.blockingIndex), 'blocking');
                  const churnStatus = getMetricStatus(parseFloat(metrics.churnIndex), 'churn');
                  
                  return (
                    <tr key={member.id} className={`transition-colors ${darkMode ? 'hover:bg-slate-700' : 'hover:bg-slate-50'}`}>
                      <td className="py-4 px-3">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                            {member.avatar}
                          </div>
                          <div>
                            <p className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-slate-800'}`}>{member.name}</p>
                            <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{member.role}</p>
                          </div>
                        </div>
                      </td>
                      <td className="text-center py-4 px-3">
                        <span className="inline-flex items-center justify-center w-10 h-10 bg-emerald-100 text-emerald-700 rounded-full text-sm font-bold">
                          {member.ticketsProcessed}
                        </span>
                      </td>
                      <td className="text-center py-4 px-3">
                        <span className={`text-sm font-mono ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>{member.avgTime}</span>
                      </td>
                      <td className="text-center py-4 px-3">
                        <div className="flex flex-col items-center gap-1">
                          <span className={`text-lg font-bold ${efficiencyStatus.color}`}>{metrics.efficiency}</span>
                          <span className={`px-2 py-0.5 text-xs rounded-full ${efficiencyStatus.bg} ${efficiencyStatus.color}`}>
                            {efficiencyStatus.status}
                          </span>
                        </div>
                      </td>
                      <td className="text-center py-4 px-3">
                        <div className="flex flex-col items-center gap-1">
                          <span className={`text-lg font-bold ${blockingStatus.color}`}>{metrics.blockingIndex}%</span>
                          <span className={`px-2 py-0.5 text-xs rounded-full ${blockingStatus.bg} ${blockingStatus.color}`}>
                            {blockingStatus.status}
                          </span>
                        </div>
                      </td>
                      <td className="text-center py-4 px-3">
                        <div className="flex flex-col items-center gap-1">
                          <span className={`text-lg font-bold ${churnStatus.color}`}>{metrics.churnIndex}%</span>
                          <span className={`px-2 py-0.5 text-xs rounded-full ${churnStatus.bg} ${churnStatus.color}`}>
                            {churnStatus.status}
                          </span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Activity Heatmap - Developer × Days */}
        <div className={`rounded-xl shadow-sm border mb-6 ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
          <div className={`p-4 border-b ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('activityHeatmap')}</h3>
                <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('ticketsClosedByDayDev')}</p>
              </div>
              <div className="flex items-center gap-3">
                <span className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('lessActive')}</span>
                <div className="flex gap-1">
                  {[100, 200, 300, 400, 500, 600].map((shade, i) => (
                    <div key={i} className={`w-4 h-4 rounded bg-emerald-${shade}`}></div>
                  ))}
                </div>
                <span className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('moreActive')}</span>
              </div>
            </div>
          </div>
          
          <div className="p-6">
            {/* Heatmap Grid */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr>
                    <th className="w-40"></th>
                    {heatmapData.days.map(day => (
                      <th key={day} className={`text-center py-2 px-3 text-sm font-medium ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                        {day}
                      </th>
                    ))}
                    <th className={`text-center py-2 px-3 text-sm font-medium ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                      {t('total')}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {heatmapData.developers.map((dev, devIdx) => (
                    <tr key={dev.name}>
                      <td className="py-2 px-3">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
                            {dev.avatar}
                          </div>
                          <span className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-slate-700'}`}>{dev.name}</span>
                        </div>
                      </td>
                      {dev.data.map((value, dayIdx) => (
                        <td key={dayIdx} className="text-center py-2 px-3">
                          <div 
                            className={`w-12 h-12 mx-auto rounded-lg flex items-center justify-center text-sm font-bold transition-all hover:scale-110 cursor-pointer ${
                              getHeatmapColor(value, maxActivity)
                            } ${value > 0 ? 'text-white' : darkMode ? 'text-slate-500' : 'text-slate-400'}`}
                            title={`${dev.name}: ${value} tickets on ${heatmapData.days[dayIdx]}`}
                          >
                            {value > 0 ? value : '-'}
                          </div>
                        </td>
                      ))}
                      <td className="text-center py-2 px-3">
                        <span className={`inline-flex items-center justify-center w-12 h-12 rounded-lg text-sm font-bold ${
                          darkMode ? 'bg-slate-700 text-white' : 'bg-slate-100 text-slate-700'
                        }`}>
                          {dev.data.reduce((a, b) => a + b, 0)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className={`border-t ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
                    <td className={`py-3 px-3 font-medium ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>{t('dailyTotal')}</td>
                    {heatmapData.days.map((day, idx) => {
                      const dayTotal = heatmapData.developers.reduce((sum, dev) => sum + dev.data[idx], 0);
                      return (
                        <td key={day} className="text-center py-3 px-3">
                          <span className={`text-sm font-bold ${
                            dayTotal === 0 ? 'text-red-500' : dayTotal < 10 ? 'text-amber-500' : 'text-emerald-500'
                          }`}>
                            {dayTotal}
                          </span>
                        </td>
                      );
                    })}
                    <td className="text-center py-3 px-3">
                      <span className="text-lg font-bold text-blue-600">
                        {heatmapData.developers.reduce((sum, dev) => sum + dev.data.reduce((a, b) => a + b, 0), 0)}
                      </span>
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>

            {/* Insights */}
            <div className={`mt-6 p-4 rounded-xl ${darkMode ? 'bg-slate-700' : 'bg-amber-50'}`}>
              <div className="flex items-start gap-3">
                <span className="text-2xl">💡</span>
                <div>
                  <h4 className={`font-semibold mb-1 ${darkMode ? 'text-white' : 'text-amber-800'}`}>{t('insight')}</h4>
                  <p className={`text-sm ${darkMode ? 'text-slate-300' : 'text-amber-700'}`}>
                    {t('fridayInsight')}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Team Performance by Project */}
        <div className={`rounded-xl shadow-sm border mb-6 ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
          <div className={`p-4 border-b ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
            <div className="flex items-center justify-between">
              <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('teamPerformanceByProject')}</h3>
              <div className="flex items-center gap-3">
                <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('sortBy')}:</span>
                <select 
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className={`text-sm border rounded-lg px-3 py-1.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    darkMode ? 'bg-slate-700 border-slate-600 text-white' : 'bg-white border-slate-200'
                  }`}
                >
                  <option value="ticketsProcessed">{t('ticketsCompleted')}</option>
                  <option value="pending">{t('pending')}</option>
                  <option value="blocked">{t('blocked')}</option>
                  <option value="name">{t('name')}</option>
                </select>
                <button 
                  onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
                  className={`p-1.5 border rounded-lg transition-colors ${
                    darkMode ? 'border-slate-600 hover:bg-slate-700 text-slate-300' : 'border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  {sortOrder === 'desc' ? '↓' : '↑'}
                </button>
              </div>
            </div>
          </div>

          <div className={`divide-y ${darkMode ? 'divide-slate-700' : 'divide-slate-100'}`}>
            {projectPerformance.map((project, idx) => (
              <div key={project.projectId}>
                {/* Project Header */}
                <div 
                  className={`flex items-center gap-3 p-4 cursor-pointer transition-colors ${darkMode ? 'hover:bg-slate-700' : 'hover:bg-slate-50'}`}
                  onClick={() => setExpandedProjects(prev => 
                    prev.includes(idx) ? prev.filter(i => i !== idx) : [...prev, idx]
                  )}
                >
                  <span className={`transform transition-transform ${darkMode ? 'text-slate-400' : ''} ${expandedProjects.includes(idx) ? 'rotate-90' : ''}`}>▶</span>
                  <span className="text-xl">{project.projectIcon}</span>
                  <div className="flex-1">
                    <h4 className={`text-sm font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{project.projectName}</h4>
                    <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{project.members.length} team members</p>
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <div className="text-center">
                      <p className="font-semibold text-emerald-600">{project.members.reduce((sum, m) => sum + m.ticketsProcessed, 0)}</p>
                      <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>{t('completed')}</p>
                    </div>
                    <div className="text-center">
                      <p className="font-semibold text-blue-600">{project.members.reduce((sum, m) => sum + m.pending, 0)}</p>
                      <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>{t('pending')}</p>
                    </div>
                    <div className="text-center">
                      <p className="font-semibold text-amber-600">{project.members.reduce((sum, m) => sum + m.blocked, 0)}</p>
                      <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>{t('blocked')}</p>
                    </div>
                  </div>
                </div>

                {/* Team Members Table */}
                {expandedProjects.includes(idx) && (
                  <div className={`px-4 pb-4 ${darkMode ? 'bg-slate-900' : 'bg-slate-50'}`}>
                    <table className="w-full">
                      <thead>
                        <tr className={`text-xs uppercase tracking-wider ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                          <th className="text-left py-2 px-3 font-medium">{t('developer')}</th>
                          <th className="text-center py-2 px-3 font-medium">{t('completed')}</th>
                          <th className="text-center py-2 px-3 font-medium">{t('pending')}</th>
                          <th className="text-center py-2 px-3 font-medium">{t('blocked')}</th>
                          <th className="text-center py-2 px-3 font-medium">{t('questions')}</th>
                          <th className="text-center py-2 px-3 font-medium">{t('redirects')}</th>
                          <th className="text-center py-2 px-3 font-medium">{t('avgTime')}</th>
                        </tr>
                      </thead>
                      <tbody className={`divide-y ${darkMode ? 'divide-slate-700' : 'divide-slate-200'}`}>
                        {sortMembers(project.members).map(member => (
                          <tr key={member.id} className={`transition-colors ${darkMode ? 'bg-slate-800 hover:bg-slate-700' : 'bg-white hover:bg-blue-50'}`}>
                            <td className="py-3 px-3">
                              <div className="flex items-center gap-2">
                                <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full flex items-center justify-center text-white text-xs font-medium">
                                  {member.avatar}
                                </div>
                                <div>
                                  <p className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-slate-800'}`}>{member.name}</p>
                                  <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{member.role}</p>
                                </div>
                              </div>
                            </td>
                            <td className="text-center py-3 px-3">
                              <span className="inline-flex items-center justify-center w-8 h-8 bg-emerald-100 text-emerald-700 rounded-full text-sm font-semibold">
                                {member.ticketsProcessed}
                              </span>
                            </td>
                            <td className="text-center py-3 px-3">
                              <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-semibold ${member.pending > 3 ? 'bg-blue-100 text-blue-700' : darkMode ? 'bg-slate-700 text-slate-300' : 'bg-slate-100 text-slate-600'}`}>
                                {member.pending}
                              </span>
                            </td>
                            <td className="text-center py-3 px-3">
                              <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-semibold ${member.blocked > 0 ? 'bg-amber-100 text-amber-700' : darkMode ? 'bg-slate-700 text-slate-300' : 'bg-slate-100 text-slate-600'}`}>
                                {member.blocked}
                              </span>
                            </td>
                            <td className="text-center py-3 px-3">
                              <span className={`text-sm ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>{member.questions}</span>
                            </td>
                            <td className="text-center py-3 px-3">
                              <span className={`text-sm ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>{member.redirects}</span>
                            </td>
                            <td className="text-center py-3 px-3">
                              <span className="text-sm font-mono text-slate-600">{member.avgTime}</span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className={`rounded-xl p-5 shadow-sm border ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
            <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-800'}`}>Epic Progress (Burndown)</h3>
            <div className="space-y-4">
              {epics.map(epic => (
                <div key={epic.id}>
                  <div className="flex items-center justify-between mb-1">
                    <span className={`text-sm font-medium ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>{epic.name}</span>
                    <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{epic.progress}%</span>
                  </div>
                  <div className={`h-3 rounded-full overflow-hidden ${darkMode ? 'bg-slate-700' : 'bg-slate-100'}`}>
                    <div 
                      className="h-full bg-gradient-to-r from-blue-500 to-emerald-500 rounded-full transition-all"
                      style={{ width: `${epic.progress}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
            <div className={`mt-6 pt-4 border-t ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
              <div className="flex items-center justify-between text-sm">
                <span className={darkMode ? 'text-slate-400' : 'text-slate-500'}>Sprint Progress</span>
                <span className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>Day 8 of 14</span>
              </div>
              <div className={`mt-2 h-2 rounded-full overflow-hidden ${darkMode ? 'bg-slate-700' : 'bg-slate-100'}`}>
                <div className="h-full bg-blue-500 rounded-full" style={{ width: '57%' }}></div>
              </div>
            </div>
          </div>

          <div className={`rounded-xl p-5 shadow-sm border ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
            <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('weeklyTrend')}</h3>
            <div className="h-48 flex items-end gap-2">
              {[
                { day: 'Mon', completed: 8, blocked: 1 },
                { day: 'Tue', completed: 12, blocked: 2 },
                { day: 'Wed', completed: 15, blocked: 1 },
                { day: 'Thu', completed: 11, blocked: 3 },
                { day: 'Fri', completed: 6, blocked: 2 },
                { day: 'Sat', completed: 1, blocked: 0 },
                { day: 'Sun', completed: 0, blocked: 0 },
              ].map((day, idx) => (
                <div key={idx} className="flex-1 flex flex-col items-center gap-1">
                  <div className="w-full flex flex-col gap-1" style={{ height: '140px' }}>
                    <div 
                      className="w-full bg-emerald-500 rounded-t transition-all"
                      style={{ height: `${(day.completed / 15) * 100}%` }}
                    ></div>
                    <div 
                      className="w-full bg-amber-500 rounded-b transition-all"
                      style={{ height: `${(day.blocked / 15) * 100}%` }}
                    ></div>
                  </div>
                  <span className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{day.day}</span>
                </div>
              ))}
            </div>
            <div className="flex items-center justify-center gap-6 mt-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-emerald-500 rounded"></div>
                <span className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('completed')}</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-amber-500 rounded"></div>
                <span className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('blocked')}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Developer Workbench View

  // Team Management Tab
  const TeamManagement = () => (
    <div className={`flex-1 overflow-auto p-6 ${darkMode ? 'bg-slate-900' : 'bg-slate-50'}`}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className={`text-2xl font-bold mb-1 ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('teamManagement')}</h1>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('manageTeam')}</p>
        </div>
        <button 
          onClick={() => setShowNewDeveloperModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-medium shadow-sm"
        >
          <span className="text-lg">+</span>
          <span>{t('addDeveloper')}</span>
        </button>
      </div>

      {/* Team Stats - Single Row Side by Side */}
      <div className="flex gap-4 mb-6">
        <div className={`flex-1 rounded-xl p-4 shadow-sm border ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
              <span className="text-2xl">👥</span>
            </div>
            <div>
              <p className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{teamMembers.length}</p>
              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('totalDevelopers')}</p>
            </div>
          </div>
        </div>
        <div className={`flex-1 rounded-xl p-4 shadow-sm border ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center">
              <span className="text-2xl">👑</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-amber-600">{teamMembers.filter(m => m.isTeamLead).length}</p>
              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('teamLead')}s</p>
            </div>
          </div>
        </div>
        <div className={`flex-1 rounded-xl p-4 shadow-sm border ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
              <span className="text-2xl">✅</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-emerald-600">{teamMembers.filter(m => m.status === 'active').length}</p>
              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('active')}</p>
            </div>
          </div>
        </div>
        <div className={`flex-1 rounded-xl p-4 shadow-sm border ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center">
              <span className="text-2xl">📊</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-indigo-600">{Math.round(teamMembers.reduce((sum, m) => sum + m.ticketsProcessed, 0) / teamMembers.length)}</p>
              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('avgTicketsDev')}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Developer List */}
      <div className={`rounded-xl shadow-sm border ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
        <div className={`p-4 border-b ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
          <div className="flex items-center justify-between">
            <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('allDevelopers')}</h3>
            <div className="flex items-center gap-2">
              <input 
                type="text"
                placeholder={t('searchDevelopers')}
                className={`text-sm border rounded-lg px-3 py-1.5 w-64 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  darkMode ? 'bg-slate-700 border-slate-600 text-white placeholder-slate-400' : 'border-slate-200'
                }`}
              />
              <select className={`text-sm border rounded-lg px-3 py-1.5 ${
                darkMode ? 'bg-slate-700 border-slate-600 text-white' : 'bg-white border-slate-200'
              }`}>
                <option>{t('allRoles')}</option>
                <option>Frontend Dev</option>
                <option>Backend Dev</option>
                <option>Full Stack</option>
                <option>DevOps</option>
                <option>{t('teamLead')}s</option>
              </select>
            </div>
          </div>
        </div>

        <div className={`divide-y ${darkMode ? 'divide-slate-700' : 'divide-slate-100'}`}>
          {teamMembers.map(member => (
            <div key={member.id} className={`p-4 transition-colors ${darkMode ? 'hover:bg-slate-700' : 'hover:bg-slate-50'}`}>
              <div className="flex items-center gap-4">
                <div className="relative">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-semibold ${
                    member.isTeamLead 
                      ? 'bg-gradient-to-br from-amber-400 to-orange-500' 
                      : 'bg-gradient-to-br from-blue-400 to-indigo-500'
                  }`}>
                    {member.avatar}
                  </div>
                  {member.isTeamLead && (
                    <div className="absolute -top-1 -right-1 w-5 h-5 bg-amber-400 rounded-full flex items-center justify-center text-xs">
                      👑
                    </div>
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h4 className={`text-sm font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{member.name}</h4>
                    {member.isTeamLead && (
                      <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-amber-100 text-amber-700">
                        {t('teamLeadBadge')}
                      </span>
                    )}
                    <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${member.status === 'active' ? 'bg-emerald-100 text-emerald-700' : darkMode ? 'bg-slate-600 text-slate-300' : 'bg-slate-100 text-slate-600'}`}>
                      {member.status === 'active' ? t('active') : t('inactive')}
                    </span>
                  </div>
                  <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{member.email}</p>
                  <p className={`text-xs mt-0.5 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>{member.role}</p>
                </div>
                <div className="grid grid-cols-4 gap-6 text-center">
                  <div>
                    <p className="text-lg font-semibold text-emerald-600">{member.ticketsProcessed}</p>
                    <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>{t('completed')}</p>
                  </div>
                  <div>
                    <p className="text-lg font-semibold text-blue-600">{member.pending}</p>
                    <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>{t('pending')}</p>
                  </div>
                  <div>
                    <p className="text-lg font-semibold text-amber-600">{member.blocked}</p>
                    <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>{t('blocked')}</p>
                  </div>
                  <div>
                    <p className={`text-lg font-semibold ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>{member.avgTime}</p>
                    <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>{t('avgTime')}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {/* Team Lead Toggle Button */}
                  <button 
                    onClick={() => toggleTeamLead(member.id)}
                    className={`px-3 py-2 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
                      member.isTeamLead 
                        ? darkMode ? 'bg-amber-900/50 text-amber-300 hover:bg-amber-900' : 'bg-amber-100 text-amber-700 hover:bg-amber-200'
                        : darkMode ? 'bg-slate-700 text-slate-300 hover:bg-slate-600' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                    title={member.isTeamLead ? t('removeLeadRole') : t('promoteToLead')}
                  >
                    <span>👑</span>
                    <span>{member.isTeamLead ? t('removeLeadRole') : t('promoteToLead')}</span>
                  </button>
                  <button className={`p-2 rounded-lg transition-colors ${darkMode ? 'text-slate-400 hover:text-blue-400 hover:bg-slate-700' : 'text-slate-400 hover:text-blue-600 hover:bg-blue-50'}`}>
                    <span>✏️</span>
                  </button>
                  <button className={`p-2 rounded-lg transition-colors ${darkMode ? 'text-slate-400 hover:text-red-400 hover:bg-slate-700' : 'text-slate-400 hover:text-red-600 hover:bg-red-50'}`}>
                    <span>🗑️</span>
                  </button>
                </div>
              </div>

              {/* Project Assignments */}
              <div className={`mt-3 ml-16 flex items-center gap-2 flex-wrap`}>
                <span className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>{t('assignedTo')}:</span>
                {projectPerformance
                  .filter(p => p.members.some(m => m.id === member.id))
                  .map(project => (
                    <span key={project.projectId} className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs ${
                      darkMode ? 'bg-slate-700 text-slate-300' : 'bg-slate-100 text-slate-600'
                    }`}>
                      <span>{project.projectIcon}</span>
                      <span>{project.projectName}</span>
                    </span>
                  ))
                }
                <button className="text-xs text-blue-600 hover:text-blue-700">+ {t('assignToProject')}</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // New Developer Modal
  const NewDeveloperModal = () => (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowNewDeveloperModal(false)}>
      <div className="bg-white rounded-2xl w-full max-w-lg p-6 shadow-2xl" onClick={e => e.stopPropagation()}>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
            <span className="text-2xl">👤</span>
          </div>
          <div>
            <h3 className="text-xl font-semibold text-slate-800">Add New Developer</h3>
            <p className="text-sm text-slate-500">Create a new team member account</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">First Name</label>
              <input 
                type="text"
                className="w-full p-3 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="John"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Last Name</label>
              <input 
                type="text"
                className="w-full p-3 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Doe"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
            <input 
              type="email"
              className="w-full p-3 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="john.doe@company.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Role</label>
            <select className="w-full p-3 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white">
              <option value="">Select a role...</option>
              <option value="frontend">Frontend Developer</option>
              <option value="backend">Backend Developer</option>
              <option value="fullstack">Full Stack Developer</option>
              <option value="devops">DevOps Engineer</option>
              <option value="qa">QA Engineer</option>
              <option value="designer">UI/UX Designer</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Assign to Projects</label>
            <div className="space-y-2">
              {apps.map(app => (
                <label key={app.id} className="flex items-center gap-3 p-3 border border-slate-200 rounded-xl cursor-pointer hover:bg-slate-50 transition-colors">
                  <input type="checkbox" className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500" />
                  <span className="text-lg">{app.icon}</span>
                  <span className="text-sm text-slate-700">{app.name}</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Initial Password</label>
            <div className="flex gap-2">
              <input 
                type="text"
                className="flex-1 p-3 border border-slate-200 rounded-xl text-sm font-mono focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Auto-generated"
                readOnly
                value="xK9#mP2@vL"
              />
              <button className="px-4 py-2 bg-slate-100 text-slate-600 rounded-xl hover:bg-slate-200 transition-colors text-sm">
                Regenerate
              </button>
            </div>
            <p className="text-xs text-slate-400 mt-1">A password reset email will be sent to the developer</p>
          </div>
        </div>

        <div className="flex gap-3 mt-6 pt-4 border-t border-slate-200">
          <button 
            className="flex-1 py-3 border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50 transition-colors font-medium"
            onClick={() => setShowNewDeveloperModal(false)}
          >
            Cancel
          </button>
          <button 
            className="flex-1 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-medium"
            onClick={() => { setShowNewDeveloperModal(false); alert('Developer created successfully! Invitation email sent.'); }}
          >
            Create Developer
          </button>
        </div>
      </div>
    </div>
  );

  // Developer Workbench View
  
  // Filter by status first
  const statusFilteredTickets = selectedStatus === 'all' 
    ? myTickets 
    : myTickets.filter(t => t.status === selectedStatus);

  // Then filter by due date
  const filteredTickets = statusFilteredTickets.filter(ticket => {
    if (dueFilter === 'all') return true;
    
    const days = getDaysStatus(ticket.dueDate);
    if (days === null) return dueFilter === 'later';
    
    switch(dueFilter) {
      case 'overdue': return days < 0;
      case 'today': return days === 0;
      case 'week': return days > 0 && days <= 7;
      case 'later': return days > 7;
      default: return true;
    }
  });

  // Count tickets by due category
  const overdueCount = myTickets.filter(t => getDaysStatus(t.dueDate) !== null && getDaysStatus(t.dueDate) < 0).length;
  const todayCount = myTickets.filter(t => getDaysStatus(t.dueDate) === 0).length;
  const weekCount = myTickets.filter(t => { const d = getDaysStatus(t.dueDate); return d !== null && d > 0 && d <= 7; }).length;
  const laterCount = myTickets.filter(t => { const d = getDaysStatus(t.dueDate); return d === null || d > 7; }).length;

  // Code & Documentation Upload Tab
  const UploadsTab = () => {
    const [codeFiles, setCodeFiles] = useState([
      { id: 1, name: 'payment-handler.ts', size: '12.4 KB', date: 'Dec 27, 2024', status: 'approved', ticket: 't1' },
      { id: 2, name: 'webhook-processor.js', size: '8.2 KB', date: 'Dec 28, 2024', status: 'pending', ticket: 't3' },
    ]);
    const [docFiles, setDocFiles] = useState([
      { id: 1, name: 'API-Integration-Guide.md', size: '24.1 KB', date: 'Dec 26, 2024', status: 'approved', ticket: 't1' },
      { id: 2, name: 'Webhook-Events-Reference.pdf', size: '156 KB', date: 'Dec 28, 2024', status: 'pending', ticket: 't3' },
    ]);

    return (
      <div className="flex-1 bg-slate-50 overflow-auto p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-slate-800 mb-1">Code & Documentation</h1>
          <p className="text-slate-500 text-sm">Upload your code files and related documentation for review</p>
        </div>

        {/* Two Windows Side by Side */}
        <div className="flex gap-6">
          {/* Code Upload Window */}
          <div className="flex-1 bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-4 border-b border-slate-200 bg-gradient-to-r from-slate-800 to-slate-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-slate-600 rounded-lg flex items-center justify-center">
                    <span className="text-xl">💻</span>
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-white">Code Files</h2>
                    <p className="text-xs text-slate-300">Upload source code, scripts, and configs</p>
                  </div>
                </div>
                <span className="px-2 py-1 bg-slate-600 text-slate-200 text-xs font-medium rounded-full">
                  {codeFiles.length} files
                </span>
              </div>
            </div>

            {/* Upload Area */}
            <div className="p-4">
              <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center hover:border-blue-400 hover:bg-blue-50 transition-colors cursor-pointer mb-4">
                <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl">📤</span>
                </div>
                <p className="text-sm font-medium text-slate-700 mb-1">Drop code files here or click to browse</p>
                <p className="text-xs text-slate-400">Supports: .js, .ts, .py, .java, .go, .rs, .cpp, .json, .yaml</p>
              </div>

              {/* Link to Ticket */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">Link to Ticket</label>
                <select className="w-full p-2.5 border border-slate-200 rounded-lg text-sm bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                  <option value="">Select a ticket...</option>
                  {myTickets.map(t => (
                    <option key={t.id} value={t.id}>{t.title} ({t.epic})</option>
                  ))}
                </select>
              </div>

              {/* Uploaded Files List */}
              <div>
                <h3 className="text-sm font-medium text-slate-700 mb-2">Uploaded Files</h3>
                <div className="space-y-2">
                  {codeFiles.map(file => (
                    <div key={file.id} className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors">
                      <div className="w-8 h-8 bg-slate-200 rounded flex items-center justify-center">
                        <span className="text-sm">📄</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-800 truncate">{file.name}</p>
                        <p className="text-xs text-slate-400">{file.size} · {file.date}</p>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        file.status === 'approved' 
                          ? 'bg-emerald-100 text-emerald-700' 
                          : 'bg-amber-100 text-amber-700'
                      }`}>
                        {file.status === 'approved' ? '✓ Approved' : '⏳ Pending'}
                      </span>
                      <button className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors">
                        🗑️
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Documentation Upload Window */}
          <div className="flex-1 bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-4 border-b border-slate-200 bg-gradient-to-r from-indigo-600 to-indigo-500">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-indigo-400 rounded-lg flex items-center justify-center">
                    <span className="text-xl">📚</span>
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-white">Documentation</h2>
                    <p className="text-xs text-indigo-200">Upload guides, specs, and references</p>
                  </div>
                </div>
                <span className="px-2 py-1 bg-indigo-400 text-white text-xs font-medium rounded-full">
                  {docFiles.length} files
                </span>
              </div>
            </div>

            {/* Upload Area */}
            <div className="p-4">
              <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center hover:border-indigo-400 hover:bg-indigo-50 transition-colors cursor-pointer mb-4">
                <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl">📎</span>
                </div>
                <p className="text-sm font-medium text-slate-700 mb-1">Drop documentation here or click to browse</p>
                <p className="text-xs text-slate-400">Supports: .md, .pdf, .docx, .txt, .html, .xlsx</p>
              </div>

              {/* Link to Ticket */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">Link to Ticket</label>
                <select className="w-full p-2.5 border border-slate-200 rounded-lg text-sm bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
                  <option value="">Select a ticket...</option>
                  {myTickets.map(t => (
                    <option key={t.id} value={t.id}>{t.title} ({t.epic})</option>
                  ))}
                </select>
              </div>

              {/* Documentation Type */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">Documentation Type</label>
                <div className="flex gap-2">
                  {['API Reference', 'User Guide', 'Technical Spec', 'README', 'Other'].map(type => (
                    <button 
                      key={type}
                      className="px-3 py-1.5 text-xs font-medium border border-slate-200 rounded-lg hover:bg-indigo-50 hover:border-indigo-300 hover:text-indigo-700 transition-colors"
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>

              {/* Uploaded Files List */}
              <div>
                <h3 className="text-sm font-medium text-slate-700 mb-2">Uploaded Documentation</h3>
                <div className="space-y-2">
                  {docFiles.map(file => (
                    <div key={file.id} className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors">
                      <div className="w-8 h-8 bg-indigo-100 rounded flex items-center justify-center">
                        <span className="text-sm">{file.name.endsWith('.pdf') ? '📕' : '📘'}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-800 truncate">{file.name}</p>
                        <p className="text-xs text-slate-400">{file.size} · {file.date}</p>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        file.status === 'approved' 
                          ? 'bg-emerald-100 text-emerald-700' 
                          : 'bg-amber-100 text-amber-700'
                      }`}>
                        {file.status === 'approved' ? '✓ Approved' : '⏳ Pending'}
                      </span>
                      <button className="p-1.5 text-slate-400 hover:text-blue-500 hover:bg-blue-50 rounded transition-colors">
                        👁️
                      </button>
                      <button className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors">
                        🗑️
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="mt-6 bg-white rounded-xl shadow-sm border border-slate-200 p-4">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">Recent Upload Activity</h3>
          <div className="space-y-3">
            {[
              { action: 'uploaded', file: 'webhook-processor.js', type: 'code', time: '2 hours ago', status: 'pending' },
              { action: 'approved', file: 'API-Integration-Guide.md', type: 'doc', time: '1 day ago', by: 'Carlos Ruiz' },
              { action: 'uploaded', file: 'payment-handler.ts', type: 'code', time: '2 days ago', status: 'approved' },
            ].map((activity, i) => (
              <div key={i} className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  activity.action === 'approved' ? 'bg-emerald-100' : 'bg-blue-100'
                }`}>
                  <span className="text-sm">{activity.action === 'approved' ? '✓' : '↑'}</span>
                </div>
                <div className="flex-1">
                  <p className="text-sm text-slate-700">
                    <span className="font-medium">You {activity.action}</span> {activity.file}
                    {activity.by && <span className="text-slate-500"> · Approved by {activity.by}</span>}
                  </p>
                  <p className="text-xs text-slate-400">{activity.time}</p>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  activity.type === 'code' ? 'bg-slate-100 text-slate-600' : 'bg-indigo-100 text-indigo-600'
                }`}>
                  {activity.type === 'code' ? '💻 Code' : '📚 Doc'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const EmployeeWorkbench = () => (
    <div className="flex-1 flex">
      <div className={`flex-1 overflow-auto p-6 ${darkMode ? 'bg-slate-900' : 'bg-slate-50'}`}>
        <div className="mb-6">
          <h1 className={`text-2xl font-bold mb-1 ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('developerWorkbench')}</h1>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('yourAssignedTickets')}</p>
        </div>

        {/* Stats Row - Side by Side using Flex */}
        <div className="flex gap-4 mb-6">
          {/* Active Tickets Card - Clickable */}
          <div 
            onClick={() => setSelectedStatus(selectedStatus === 'progress' ? 'all' : 'progress')}
            className={`flex-1 rounded-xl p-4 shadow-sm border-2 cursor-pointer transition-all hover:shadow-md ${
              selectedStatus === 'progress' 
                ? 'border-blue-500 ring-2 ring-blue-100' 
                : darkMode ? 'border-slate-700 hover:border-blue-400 bg-slate-800' : 'border-slate-200 hover:border-blue-300 bg-white'
            } ${selectedStatus === 'progress' ? darkMode ? 'bg-slate-800' : 'bg-white' : ''}`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <span className="text-xl">🎯</span>
                </div>
                <span className={`text-sm font-medium ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>{t('activeTickets')}</span>
              </div>
              {selectedStatus === 'progress' && (
                <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">{t('filtered')}</span>
              )}
            </div>
            <p className="text-4xl font-bold text-blue-600 mb-1">{myTickets.filter(t => t.status === 'progress').length}</p>
            <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>{t('clickToFilter')}</p>
            <div className={`mt-3 pt-3 border-t ${darkMode ? 'border-slate-700' : 'border-slate-100'}`}>
              <div className="flex items-center justify-between text-xs">
                <span className={darkMode ? 'text-slate-400' : 'text-slate-500'}>{t('inProgress')}</span>
                <span className="font-medium text-blue-600">⏱️ 2h 30m {t('today')}</span>
              </div>
            </div>
          </div>

          {/* Pending Tickets Card - Clickable */}
          <div 
            onClick={() => setSelectedStatus(selectedStatus === 'todo' ? 'all' : 'todo')}
            className={`flex-1 rounded-xl p-4 shadow-sm border-2 cursor-pointer transition-all hover:shadow-md ${
              selectedStatus === 'todo' 
                ? 'border-amber-500 ring-2 ring-amber-100' 
                : darkMode ? 'border-slate-700 hover:border-amber-400 bg-slate-800' : 'border-slate-200 hover:border-amber-300 bg-white'
            } ${selectedStatus === 'todo' ? darkMode ? 'bg-slate-800' : 'bg-white' : ''}`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                  <span className="text-xl">📥</span>
                </div>
                <span className={`text-sm font-medium ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>{t('pendingTickets')}</span>
              </div>
              {selectedStatus === 'todo' && (
                <span className="px-2 py-1 bg-amber-100 text-amber-700 text-xs font-medium rounded-full">{t('filtered')}</span>
              )}
            </div>
            <p className="text-4xl font-bold text-amber-600 mb-1">{myTickets.filter(t => t.status === 'todo').length}</p>
            <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>{t('clickToFilter')}</p>
            <div className={`mt-3 pt-3 border-t ${darkMode ? 'border-slate-700' : 'border-slate-100'}`}>
              <div className="flex items-center justify-between text-xs">
                <span className={darkMode ? 'text-slate-400' : 'text-slate-500'}>{t('waitingToStart')}</span>
                <span className="font-medium text-amber-600">{t('estimated')} 6h 30m</span>
              </div>
            </div>
          </div>

          {/* Team Ranking Card - Teams vs Teams */}
          <div className={`flex-1 rounded-xl p-4 shadow-sm border ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                <span className="text-xl">🏆</span>
              </div>
              <span className={`text-sm font-medium ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>{t('teamRanking')}</span>
            </div>
            
            {/* Current Team Highlight */}
            <div className={`flex items-center gap-3 mb-3 p-2.5 rounded-lg border ${darkMode ? 'bg-emerald-900/30 border-emerald-700' : 'bg-emerald-50 border-emerald-200'}`}>
              <div className="flex items-center justify-center w-8 h-8 bg-emerald-500 text-white rounded-full font-bold text-sm">
                #2
              </div>
              <div className="flex-1">
                <p className={`text-sm font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>Frontend Team</p>
                <p className="text-xs text-emerald-600">{t('yourTeam')} · 89 {t('ticketsCompleted2')}</p>
              </div>
              <div className="text-right">
                <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('avgTime')}</p>
                <p className="text-sm font-semibold text-emerald-600">1h 32m</p>
              </div>
            </div>

            {/* Other Teams Leaderboard */}
            <div className="space-y-2">
              {[
                { rank: 1, name: 'Backend Team', icon: '🔧', tickets: 124, avgTime: '1h 15m', color: 'amber' },
                { rank: 3, name: 'DevOps Team', icon: '⚙️', tickets: 67, avgTime: '1h 45m', color: 'slate' },
                { rank: 4, name: 'QA Team', icon: '🧪', tickets: 52, avgTime: '2h 10m', color: 'slate' },
              ].map(team => (
                <div key={team.rank} className={`flex items-center gap-2 p-2 rounded-lg transition-colors ${darkMode ? 'hover:bg-slate-700' : 'hover:bg-slate-50'}`}>
                  <span className={`w-6 h-6 flex items-center justify-center rounded-full text-xs font-bold ${
                    team.rank === 1 ? 'bg-amber-100 text-amber-700' : darkMode ? 'bg-slate-700 text-slate-400' : 'bg-slate-100 text-slate-500'
                  }`}>
                    {team.rank === 1 ? '🥇' : `#${team.rank}`}
                  </span>
                  <span className="text-base">{team.icon}</span>
                  <div className="flex-1 min-w-0">
                    <p className={`text-xs font-medium truncate ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>{team.name}</p>
                    <p className={`text-[10px] ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>{team.tickets} {t('tickets')}</p>
                  </div>
                  <span className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{team.avgTime}</span>
                </div>
              ))}
            </div>

            <button className={`w-full mt-3 pt-2 border-t text-xs text-blue-600 hover:text-blue-700 font-medium ${darkMode ? 'border-slate-700' : 'border-slate-100'}`}>
              {t('viewAllTeams')}
            </button>
          </div>
        </div>

        {/* Due Date Filter Row */}
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-2">
            <span className={`text-sm font-medium ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>{t('filterByDueDate')}</span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setDueFilter('all')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
                dueFilter === 'all' 
                  ? 'bg-slate-800 text-white' 
                  : darkMode ? 'bg-slate-800 border border-slate-700 text-slate-300 hover:bg-slate-700' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              <span>📋</span>
              <span>{t('all')}</span>
              <span className={`px-1.5 py-0.5 rounded-full text-xs ${dueFilter === 'all' ? 'bg-white/20' : darkMode ? 'bg-slate-700' : 'bg-slate-100'}`}>
                {myTickets.length}
              </span>
            </button>
            
            <button
              onClick={() => setDueFilter('overdue')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
                dueFilter === 'overdue' 
                  ? 'bg-red-500 text-white' 
                  : darkMode ? 'bg-slate-800 border border-slate-700 text-slate-300 hover:bg-red-900/50 hover:border-red-700' : 'bg-white border border-slate-200 text-slate-600 hover:bg-red-50 hover:border-red-200'
              }`}
            >
              <span>🚨</span>
              <span>{t('overdue')}</span>
              {overdueCount > 0 && (
                <span className={`px-1.5 py-0.5 rounded-full text-xs font-bold ${dueFilter === 'overdue' ? 'bg-white/20' : 'bg-red-100 text-red-700'}`}>
                  {overdueCount}
                </span>
              )}
            </button>
            
            <button
              onClick={() => setDueFilter('today')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
                dueFilter === 'today' 
                  ? 'bg-amber-500 text-white' 
                  : darkMode ? 'bg-slate-800 border border-slate-700 text-slate-300 hover:bg-amber-900/50 hover:border-amber-700' : 'bg-white border border-slate-200 text-slate-600 hover:bg-amber-50 hover:border-amber-200'
              }`}
            >
              <span>📅</span>
              <span>{t('dueToday')}</span>
              {todayCount > 0 && (
                <span className={`px-1.5 py-0.5 rounded-full text-xs font-bold ${dueFilter === 'today' ? 'bg-white/20' : 'bg-amber-100 text-amber-700'}`}>
                  {todayCount}
                </span>
              )}
            </button>
            
            <button
              onClick={() => setDueFilter('week')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
                dueFilter === 'week' 
                  ? 'bg-blue-500 text-white' 
                  : darkMode ? 'bg-slate-800 border border-slate-700 text-slate-300 hover:bg-blue-900/50 hover:border-blue-700' : 'bg-white border border-slate-200 text-slate-600 hover:bg-blue-50 hover:border-blue-200'
              }`}
            >
              <span>📆</span>
              <span>{t('thisWeek2')}</span>
              {weekCount > 0 && (
                <span className={`px-1.5 py-0.5 rounded-full text-xs font-bold ${dueFilter === 'week' ? 'bg-white/20' : 'bg-blue-100 text-blue-700'}`}>
                  {weekCount}
                </span>
              )}
            </button>
            
            <button
              onClick={() => setDueFilter('later')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
                dueFilter === 'later' 
                  ? 'bg-slate-500 text-white' 
                  : darkMode ? 'bg-slate-800 border border-slate-700 text-slate-300 hover:bg-slate-700' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              <span>🗓️</span>
              <span>{t('later')}</span>
              {laterCount > 0 && (
                <span className={`px-1.5 py-0.5 rounded-full text-xs ${dueFilter === 'later' ? 'bg-white/20' : darkMode ? 'bg-slate-700' : 'bg-slate-100'}`}>
                  {laterCount}
                </span>
              )}
            </button>
          </div>
        </div>

        {/* Filter indicator */}
        {(selectedStatus !== 'all' || dueFilter !== 'all') && (
          <div className={`flex items-center justify-between mb-4 p-3 rounded-lg ${darkMode ? 'bg-slate-800' : 'bg-slate-100'}`}>
            <div className="flex items-center gap-2">
              <span className={`text-sm ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                {t('showing')}: 
                {selectedStatus !== 'all' && (
                  <span className="font-semibold ml-1">
                    {selectedStatus === 'progress' ? t('active') : t('pending')}
                  </span>
                )}
                {selectedStatus !== 'all' && dueFilter !== 'all' && <span className="mx-1">·</span>}
                {dueFilter !== 'all' && (
                  <span className="font-semibold ml-1">
                    {dueFilter === 'overdue' ? t('overdue') : 
                     dueFilter === 'today' ? t('dueToday') : 
                     dueFilter === 'week' ? t('thisWeek2') : t('later')}
                  </span>
                )}
                <span className="ml-1">({filteredTickets.length} {t('tickets')})</span>
              </span>
            </div>
            <button 
              onClick={() => { setSelectedStatus('all'); setDueFilter('all'); }}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
            >
              <span>{t('clearAllFilters')}</span>
              <span>✕</span>
            </button>
          </div>
        )}

        {/* Ticket List */}
        <div className="space-y-4">
          {filteredTickets.length === 0 ? (
            <div className="bg-white rounded-xl p-8 shadow-sm border border-slate-200 text-center">
              <span className="text-4xl mb-3 block">
                {dueFilter === 'overdue' ? '🎉' : dueFilter === 'today' ? '✨' : '📭'}
              </span>
              <p className="text-slate-600 font-medium">
                {dueFilter === 'overdue' 
                  ? 'No overdue tickets!' 
                  : dueFilter === 'today'
                    ? 'Nothing due today!'
                    : dueFilter === 'week'
                      ? 'No tickets due this week!'
                      : `No ${selectedStatus === 'progress' ? 'active' : selectedStatus === 'todo' ? 'pending' : ''} tickets!`
                }
              </p>
              <p className="text-slate-400 text-sm">
                {dueFilter === 'overdue' 
                  ? 'Great job staying on schedule!' 
                  : 'You\'re all caught up.'
                }
              </p>
            </div>
          ) : (
            filteredTickets.map(ticket => {
              const daysStatus = getDaysStatus(ticket.dueDate);
              const ticketOverdue = ticket.status !== 'done' && isOverdue(ticket.dueDate);
              
              return (
                <div 
                  key={ticket.id}
                  onClick={() => setSelectedTicket(ticket)}
                  className={`bg-white rounded-xl p-4 shadow-sm border cursor-pointer hover:shadow-md transition-all ${
                    ticketOverdue 
                      ? 'border-red-300 border-l-4 border-l-red-500' 
                      : getStatusBorder(ticket.status)
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="flex items-center gap-2 text-xs text-slate-400 mb-1">
                        <span>{apps[selectedApp].icon}</span>
                        <span>{apps[selectedApp].name}</span>
                        <span>/</span>
                        <span>{ticket.epic}</span>
                      </div>
                      <h3 className="text-lg font-semibold text-slate-800">{ticket.title}</h3>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      ticket.status === 'progress' ? 'bg-blue-100 text-blue-700' :
                      ticket.status === 'blocked' ? 'bg-amber-100 text-amber-700' :
                      'bg-slate-100 text-slate-600'
                    }`}>
                      {ticket.status === 'progress' ? 'In Progress' : ticket.status === 'blocked' ? 'Blocked' : 'To Do'}
                    </span>
                  </div>

                  {/* Due Date Row */}
                  <div className={`flex items-center gap-3 mb-3 p-2.5 rounded-lg ${
                    ticketOverdue 
                      ? 'bg-red-50 border border-red-200' 
                      : daysStatus !== null && daysStatus <= 3 && daysStatus >= 0
                        ? 'bg-amber-50 border border-amber-200'
                        : 'bg-slate-50'
                  }`}>
                    <span className="text-lg">{ticketOverdue ? '🚨' : daysStatus !== null && daysStatus <= 3 && daysStatus >= 0 ? '⏰' : '📅'}</span>
                    <div className="flex-1">
                      <span className={`text-sm font-medium ${
                        ticketOverdue 
                          ? 'text-red-700' 
                          : daysStatus !== null && daysStatus <= 3 && daysStatus >= 0
                            ? 'text-amber-700'
                            : 'text-slate-600'
                      }`}>
                        Due: {formatDate(ticket.dueDate)}
                      </span>
                    </div>
                    {daysStatus !== null && (
                      <span className={`text-xs font-bold px-2 py-1 rounded-full ${
                        ticketOverdue 
                          ? 'bg-red-100 text-red-700' 
                          : daysStatus === 0 
                            ? 'bg-amber-100 text-amber-700'
                            : daysStatus <= 3
                              ? 'bg-amber-100 text-amber-700'
                              : 'bg-slate-100 text-slate-600'
                      }`}>
                        {ticketOverdue 
                          ? `${Math.abs(daysStatus)}d overdue` 
                          : daysStatus === 0 
                            ? 'Due today!'
                            : `${daysStatus}d left`
                        }
                      </span>
                    )}
                  </div>

                  {/* Assigned By Section */}
                  <div className="flex items-center gap-4 mb-3 p-2 bg-slate-50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-slate-500">Assigned by:</span>
                      <div className="flex items-center gap-1.5">
                        <div className="w-5 h-5 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full flex items-center justify-center text-[10px] text-white font-medium">
                          {ticket.assignedByAvatar}
                        </div>
                        <span className="text-xs font-medium text-slate-700">{ticket.assignedBy}</span>
                      </div>
                    </div>
                    <div className="w-px h-4 bg-slate-200"></div>
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs text-slate-500">Estimated:</span>
                      <span className="text-xs font-semibold text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded">⏱️ {ticket.estimatedTime}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs text-slate-500">Subtasks</span>
                        <span className="text-xs font-medium text-slate-700">{ticket.completed.filter(Boolean).length}/{ticket.subtasks.length}</span>
                      </div>
                      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-emerald-500 rounded-full transition-all"
                          style={{ width: `${(ticket.completed.filter(Boolean).length / ticket.subtasks.length) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-slate-400">Time spent</p>
                      <p className="text-sm font-medium text-slate-700">⏱️ {ticket.time}</p>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {selectedTicket && (
        <TicketPanel 
          ticket={selectedTicket} 
          onClose={() => setSelectedTicket(null)}
          onQuestion={() => setShowQuestionModal(true)}
          onRedirect={() => setShowRedirectModal(true)}
        />
      )}
    </div>
  );

  // Ticket Detail Panel (Right Side Drawer - Slides in from right)
  const TicketPanel = ({ ticket, onClose, onQuestion, onRedirect }) => {
    // Start timer when ticket opens if status is progress
    useEffect(() => {
      if (ticket.status === 'progress' || ticket.status === 'todo') {
        startTimer(ticket.id);
        // If opening a todo ticket, change it to in_progress
        if (ticket.status === 'todo') {
          setEpics(prev => prev.map(epic => ({
            ...epic,
            tickets: epic.tickets.map(t => 
              t.id === ticket.id ? { ...t, status: 'progress' } : t
            )
          })));
          setTicketEvents(prev => [...prev, {
            type: 'START',
            ticketId: ticket.id,
            timestamp: new Date().toISOString(),
            user: currentUser
          }]);
        }
      }
    }, [ticket.id]);

    const timer = ticketTimers[ticket.id];
    const currentTime = timer ? formatTime(timer.elapsed) : ticket.time;
    const isTimerRunning = timer?.isRunning;

    // Status state machine display
    const getStatusInfo = (status) => {
      switch(status) {
        case 'todo': return { label: 'TODO', color: 'bg-slate-100 text-slate-700', icon: '📋', desc: 'Waiting to start' };
        case 'progress': return { label: 'IN PROGRESS', color: 'bg-blue-100 text-blue-700', icon: '🔄', desc: 'Timer running' };
        case 'blocked': return { label: 'BLOCKED', color: 'bg-orange-100 text-orange-700', icon: '❓', desc: 'Waiting for answer' };
        case 'redirected': return { label: 'REDIRECTED', color: 'bg-indigo-100 text-indigo-700', icon: '↪️', desc: 'Transferred' };
        case 'done': return { label: 'DONE', color: 'bg-emerald-100 text-emerald-700', icon: '✅', desc: 'Completed' };
        default: return { label: status.toUpperCase(), color: 'bg-slate-100 text-slate-700', icon: '📋', desc: '' };
      }
    };

    const statusInfo = getStatusInfo(ticket.status);

    return (
      <div className={`w-[520px] h-full flex flex-col shadow-2xl border-l transform transition-transform duration-300 ${
        darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'
      }`}>
        {/* Sticky Header */}
        <div className={`p-5 border-b ${darkMode ? 'border-slate-700 bg-gradient-to-r from-slate-700 to-slate-800' : 'border-slate-200 bg-gradient-to-r from-slate-50 to-white'}`}>
          <div className="flex items-center justify-between mb-3">
            <div className={`flex items-center gap-2 text-xs ${darkMode ? 'text-slate-400' : 'text-slate-400'}`}>
              <span>{apps[selectedApp].icon}</span>
              <span>{apps[selectedApp].name}</span>
              <span>/</span>
              <span>{ticket.epic}</span>
              <span>/</span>
              <span className="font-mono">#{ticket.id}</span>
            </div>
            <button onClick={onClose} className={`p-2 rounded-lg transition-colors ${darkMode ? 'hover:bg-slate-700 text-slate-400' : 'hover:bg-slate-100 text-slate-500'}`}>✕</button>
          </div>
          
          <h2 className={`text-xl font-bold mb-4 ${darkMode ? 'text-white' : 'text-slate-800'}`}>{ticket.title}</h2>
          
          {/* Status Badge & Timer Row */}
          <div className="flex items-center justify-between gap-4">
            {/* Status State Machine Badge */}
            <div className={`flex items-center gap-2 px-3 py-2 rounded-xl ${statusInfo.color}`}>
              <span className="text-lg">{statusInfo.icon}</span>
              <div>
                <span className="font-bold text-sm">{statusInfo.label}</span>
                <span className="text-xs opacity-75 ml-2">{statusInfo.desc}</span>
              </div>
            </div>
            
            {/* Live Timer */}
            <div className={`flex items-center gap-2 px-4 py-2 rounded-xl font-mono ${
              isTimerRunning 
                ? 'bg-blue-500 text-white animate-pulse' 
                : darkMode ? 'bg-slate-700 text-slate-300' : 'bg-slate-100 text-slate-600'
            }`}>
              <span className="text-lg">{isTimerRunning ? '⏱️' : '⏸️'}</span>
              <span className="text-lg font-bold">{currentTime}</span>
              {isTimerRunning && <span className="w-2 h-2 bg-white rounded-full animate-ping"></span>}
            </div>
          </div>

          {/* Assignee & Owner Row */}
          <div className={`mt-4 flex items-center gap-4 p-3 rounded-xl ${darkMode ? 'bg-slate-700' : 'bg-slate-50'}`}>
            <div className="flex items-center gap-2 flex-1">
              <div className="w-10 h-10 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-full flex items-center justify-center text-sm text-white font-bold">
                {ticket.assignee ? ticket.assignee.split(' ').map(n => n[0]).join('') : 'AG'}
              </div>
              <div>
                <span className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Current Owner</span>
                <span className={`block text-sm font-medium ${darkMode ? 'text-white' : 'text-slate-700'}`}>{ticket.assignee || 'Ana García'}</span>
              </div>
            </div>
            <div className={`w-px h-10 ${darkMode ? 'bg-slate-600' : 'bg-slate-200'}`}></div>
            <div className="flex items-center gap-2 flex-1">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full flex items-center justify-center text-sm text-white font-bold">
                {ticket.assignedByAvatar || 'CR'}
              </div>
              <div>
                <span className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Assigned By</span>
                <span className={`block text-sm font-medium ${darkMode ? 'text-white' : 'text-slate-700'}`}>{ticket.assignedBy || 'Carlos Ruiz'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-auto p-5">
          {/* Description */}
          <div className="mb-6">
            <h3 className={`text-sm font-semibold mb-2 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>{t('description')}</h3>
            <div className={`text-sm rounded-xl p-4 ${darkMode ? 'bg-slate-700 text-slate-300' : 'bg-slate-50 text-slate-600'}`}>
              Implement the necessary functionality for this feature. Follow the technical specifications and ensure all edge cases are covered.
            </div>
          </div>

          {/* Block Reason (if blocked) */}
          {ticket.status === 'blocked' && ticket.blockReason && (
            <div className={`mb-6 p-4 rounded-xl border-2 ${darkMode ? 'bg-orange-900/20 border-orange-700' : 'bg-orange-50 border-orange-300'}`}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xl">❓</span>
                <h3 className={`text-sm font-bold ${darkMode ? 'text-orange-400' : 'text-orange-700'}`}>{t('blockedReason')}</h3>
              </div>
              <p className={`text-sm ${darkMode ? 'text-orange-300' : 'text-orange-800'}`}>{ticket.blockReason}</p>
            </div>
          )}

          {/* Subtasks */}
          <div className="mb-6">
            <h3 className={`text-sm font-semibold mb-3 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>{t('subtasks')}</h3>
            <div className="space-y-2">
              {['Setup API endpoint', 'Implement business logic', 'Write unit tests', 'Update documentation'].map((task, i) => (
                <label key={i} className={`flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-colors ${
                  darkMode ? 'bg-slate-700 hover:bg-slate-600' : 'bg-slate-50 hover:bg-slate-100'
                }`}>
                  <input 
                    type="checkbox" 
                    checked={i < (ticket.completed || 0)}
                    readOnly
                    className="w-5 h-5 rounded border-slate-300 text-emerald-500 focus:ring-emerald-500"
                  />
                  <span className={`text-sm flex-1 ${i < (ticket.completed || 0) ? 'text-slate-400 line-through' : darkMode ? 'text-slate-200' : 'text-slate-700'}`}>
                    {task}
                  </span>
                  {i < (ticket.completed || 0) && <span className="text-emerald-500">✓</span>}
                </label>
              ))}
            </div>
          </div>

          {/* State Machine Diagram */}
          <div className="mb-6">
            <h3 className={`text-sm font-semibold mb-3 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>{t('ticketLifecycle')}</h3>
            <div className={`p-4 rounded-xl ${darkMode ? 'bg-slate-700' : 'bg-slate-50'}`}>
              <div className="flex items-center justify-between">
                {['todo', 'progress', 'blocked', 'done'].map((state, i) => {
                  const info = getStatusInfo(state);
                  const isActive = ticket.status === state;
                  const isPast = ['todo'].indexOf(ticket.status) > i || ticket.status === 'done';
                  return (
                    <React.Fragment key={state}>
                      <div className={`flex flex-col items-center ${isActive ? 'scale-110' : ''} transition-transform`}>
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg ${
                          isActive ? info.color + ' ring-2 ring-offset-2 ring-current' : 
                          isPast ? 'bg-emerald-100 text-emerald-700' : 
                          darkMode ? 'bg-slate-600 text-slate-400' : 'bg-slate-200 text-slate-400'
                        }`}>
                          {isPast && !isActive ? '✓' : info.icon}
                        </div>
                        <span className={`text-xs mt-1 font-medium ${isActive ? darkMode ? 'text-white' : 'text-slate-800' : darkMode ? 'text-slate-400' : 'text-slate-400'}`}>
                          {info.label}
                        </span>
                      </div>
                      {i < 3 && (
                        <div className={`flex-1 h-0.5 mx-2 ${isPast ? 'bg-emerald-500' : darkMode ? 'bg-slate-600' : 'bg-slate-200'}`}></div>
                      )}
                    </React.Fragment>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Activity Log */}
          <div className="mb-6">
            <h3 className={`text-sm font-semibold mb-3 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>{t('activityLog')}</h3>
            <div className="space-y-3">
              {ticketEvents.filter(e => e.ticketId === ticket.id).slice(-5).reverse().map((event, i) => (
                <div key={i} className={`flex items-start gap-3 text-sm p-3 rounded-lg ${darkMode ? 'bg-slate-700' : 'bg-slate-50'}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${
                    event.type === 'QUESTION' ? 'bg-orange-100 text-orange-700' :
                    event.type === 'REDIRECT' ? 'bg-indigo-100 text-indigo-700' :
                    event.type === 'COMPLETE' ? 'bg-emerald-100 text-emerald-700' :
                    event.type === 'START' ? 'bg-blue-100 text-blue-700' :
                    'bg-slate-200 text-slate-600'
                  }`}>
                    {event.type === 'QUESTION' ? '❓' : event.type === 'REDIRECT' ? '↪️' : event.type === 'COMPLETE' ? '✅' : event.type === 'START' ? '▶️' : '📋'}
                  </div>
                  <div className="flex-1">
                    <p className={darkMode ? 'text-slate-200' : 'text-slate-700'}>
                      <span className="font-medium">{event.user?.name || 'System'}</span>
                      {event.type === 'QUESTION' && ` raised a question`}
                      {event.type === 'REDIRECT' && ` redirected to ${event.to?.name}`}
                      {event.type === 'COMPLETE' && ` completed the ticket`}
                      {event.type === 'START' && ` started working`}
                      {event.type === 'MOVE' && ` moved ticket`}
                    </p>
                    {event.question && <p className={`text-xs mt-1 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>"{event.question}"</p>}
                    {event.reason && <p className={`text-xs mt-1 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Reason: "{event.reason}"</p>}
                    <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>{new Date(event.timestamp).toLocaleString()}</p>
                  </div>
                </div>
              ))}
              {ticketEvents.filter(e => e.ticketId === ticket.id).length === 0 && (
                <div className={`text-center py-6 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>
                  <span className="text-2xl block mb-2">📭</span>
                  <span className="text-sm">No activity yet</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Action Dock - Sticky Footer with PR Link Validation */}
        <div className={`p-4 border-t ${darkMode ? 'border-slate-700 bg-slate-800' : 'border-slate-200 bg-white'}`}>
          {ticket.status !== 'done' && ticket.status !== 'redirected' && (
            <>
              {/* PR Link Input */}
              <div className="mb-4">
                <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                  <span className="flex items-center gap-2">
                    <span>🔗</span>
                    {t('prLink')}
                    <span className="text-red-500">*</span>
                  </span>
                </label>
                <div className="relative">
                  <input
                    type="url"
                    value={ticketPRLinks[ticket.id] || ''}
                    onChange={(e) => {
                      setTicketPRLinks(prev => ({ ...prev, [ticket.id]: e.target.value }));
                      setPrLinkError('');
                    }}
                    placeholder={t('prLinkPlaceholder')}
                    className={`w-full px-4 py-3 rounded-xl border text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      prLinkError 
                        ? 'border-red-500' 
                        : isValidPRLink(ticketPRLinks[ticket.id])
                          ? 'border-emerald-500'
                          : darkMode ? 'bg-slate-700 border-slate-600 text-white placeholder-slate-400' : 'border-slate-200 placeholder-slate-400'
                    }`}
                  />
                  {ticketPRLinks[ticket.id] && (
                    <div className="absolute right-3 top-1/2 -translate-y-1/2">
                      {isValidPRLink(ticketPRLinks[ticket.id]) ? (
                        <span className="text-emerald-500 text-lg">✓</span>
                      ) : (
                        <span className="text-red-500 text-lg">✗</span>
                      )}
                    </div>
                  )}
                </div>
                {prLinkError && <p className="text-red-500 text-xs mt-1">{prLinkError}</p>}
                {!ticketPRLinks[ticket.id] && (
                  <p className={`text-xs mt-1 flex items-center gap-1 ${darkMode ? 'text-amber-400' : 'text-amber-600'}`}>
                    <span>⚠️</span> {t('prRequired')}
                  </p>
                )}
                {ticketPRLinks[ticket.id] && !isValidPRLink(ticketPRLinks[ticket.id]) && (
                  <p className={`text-xs mt-1 flex items-center gap-1 ${darkMode ? 'text-red-400' : 'text-red-600'}`}>
                    <span>❌</span> {t('invalidPrLink')}
                  </p>
                )}
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-3 gap-3">
                <button 
                  disabled={!isValidPRLink(ticketPRLinks[ticket.id])}
                  className={`flex flex-col items-center gap-2 p-4 rounded-xl transition-all shadow-lg transform ${
                    isValidPRLink(ticketPRLinks[ticket.id])
                      ? 'bg-gradient-to-br from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white hover:shadow-xl hover:scale-[1.02]'
                      : darkMode 
                        ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                        : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                  }`}
                  onClick={() => {
                    if (isValidPRLink(ticketPRLinks[ticket.id])) {
                      handleCompleteTicket(ticket);
                    } else {
                      setPrLinkError(t('validPrRequired'));
                    }
                  }}
                >
                  <span className="text-2xl">{isValidPRLink(ticketPRLinks[ticket.id]) ? '✓' : '🔒'}</span>
                  <span className="text-sm font-bold">{t('complete')}</span>
                </button>
                <button 
                  className={`flex flex-col items-center gap-2 p-4 rounded-xl transition-all shadow-lg hover:shadow-xl transform hover:scale-[1.02] ${
                    ticket.status === 'blocked' 
                      ? 'bg-gradient-to-br from-orange-400 to-orange-500 text-white' 
                      : 'bg-gradient-to-br from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-white'
                  }`}
                  onClick={onQuestion}
                >
                  <span className="text-2xl">{ticket.status === 'blocked' ? '🔓' : '✋'}</span>
                  <span className="text-sm font-bold">{ticket.status === 'blocked' ? t('unblock') : t('block')}</span>
                </button>
                <button 
                  className="flex flex-col items-center gap-2 p-4 bg-gradient-to-br from-indigo-500 to-indigo-600 hover:from-indigo-600 hover:to-indigo-700 text-white rounded-xl transition-all shadow-lg hover:shadow-xl transform hover:scale-[1.02]"
                  onClick={onRedirect}
                >
                  <span className="text-2xl">↪</span>
                  <span className="text-sm font-bold">{t('redirect')}</span>
                </button>
              </div>
            </>
          )}
          {ticket.status === 'done' && (
            <div className={`text-center py-4 rounded-xl ${darkMode ? 'bg-emerald-900/30' : 'bg-emerald-50'}`}>
              <span className="text-2xl">🎉</span>
              <p className={`text-sm font-medium mt-1 ${darkMode ? 'text-emerald-400' : 'text-emerald-700'}`}>{t('ticketCompleted')}</p>
              {ticketPRLinks[ticket.id] && (
                <a 
                  href={ticketPRLinks[ticket.id]} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-xs text-blue-500 hover:underline mt-2 inline-flex items-center gap-1"
                >
                  <span>🔗</span> View PR
                </a>
              )}
            </div>
          )}
        </div>
      </div>
    );
  };

  // Enhanced Question Modal with validation
  const QuestionModal = () => {
    const [localQuestion, setLocalQuestion] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = () => {
      if (!localQuestion.trim()) {
        setError(t('questionRequired'));
        return;
      }
      handleRaiseQuestion(selectedTicket, localQuestion);
      setLocalQuestion('');
      setError('');
    };

    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowQuestionModal(false)}>
        <div className={`rounded-2xl w-full max-w-md p-6 shadow-2xl ${darkMode ? 'bg-slate-800' : 'bg-white'}`} onClick={e => e.stopPropagation()}>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-amber-400 to-orange-500 rounded-full flex items-center justify-center">
              <span className="text-2xl">✋</span>
            </div>
            <div>
              <h3 className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('raiseQuestion')}</h3>
              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('pauseTimerNotify')}</p>
            </div>
          </div>
          
          {/* Timer info */}
          <div className={`mb-4 p-3 rounded-xl flex items-center gap-3 ${darkMode ? 'bg-slate-700' : 'bg-slate-50'}`}>
            <span className="text-xl">⏸️</span>
            <div>
              <p className={`text-sm font-medium ${darkMode ? 'text-slate-200' : 'text-slate-700'}`}>{t('timerWillPause')}</p>
              <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('currentTime')}: {ticketTimers[selectedTicket?.id] ? formatTime(ticketTimers[selectedTicket.id].elapsed) : '0s'}</p>
            </div>
          </div>

          <div className="mb-4">
            <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>{t('whatsBlockingYou')} *</label>
            <textarea 
              value={localQuestion}
              onChange={(e) => { setLocalQuestion(e.target.value); setError(''); }}
              className={`w-full p-4 border rounded-xl text-sm resize-none focus:ring-2 focus:ring-amber-500 focus:border-amber-500 ${
                error ? 'border-red-500' : darkMode ? 'bg-slate-700 border-slate-600 text-white placeholder-slate-400' : 'border-slate-200 placeholder-slate-400'
              }`}
              rows={4}
              placeholder={t('describeBlocker')}
              autoFocus
            />
            {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
          </div>
          
          <div className={`mb-4 p-3 rounded-xl ${darkMode ? 'bg-indigo-900/30' : 'bg-indigo-50'}`}>
            <div className="flex items-center gap-2">
              <span>🔔</span>
              <p className={`text-xs ${darkMode ? 'text-indigo-300' : 'text-indigo-700'}`}>
                {t('ownerWillBeNotified')} <strong>{selectedTicket?.assignedBy || 'Carlos Ruiz'}</strong>
              </p>
            </div>
          </div>

          <div className="flex gap-3">
            <button 
              className={`flex-1 py-3 border rounded-xl font-medium transition-colors ${
                darkMode ? 'border-slate-600 text-slate-300 hover:bg-slate-700' : 'border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
              onClick={() => { setShowQuestionModal(false); setLocalQuestion(''); setError(''); }}
            >
              {t('cancel')}
            </button>
            <button 
              className="flex-1 py-3 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl hover:from-amber-600 hover:to-orange-600 transition-all font-bold shadow-lg"
              onClick={handleSubmit}
            >
              {t('submitQuestion')}
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Enhanced Redirect Modal with validation
  const RedirectModal = () => {
    const [localReason, setLocalReason] = useState('');
    const [selectedUser, setSelectedUser] = useState(null);
    const [errors, setErrors] = useState({});

    const handleSubmit = () => {
      const newErrors = {};
      if (!selectedUser) newErrors.user = t('selectUser');
      if (!localReason.trim()) newErrors.reason = t('reasonRequired');
      
      if (Object.keys(newErrors).length > 0) {
        setErrors(newErrors);
        return;
      }

      handleRedirect(selectedTicket, selectedUser, localReason);
      setLocalReason('');
      setSelectedUser(null);
      setErrors({});
    };

    const timer = ticketTimers[selectedTicket?.id];
    const timeSpent = timer ? formatTime(timer.elapsed) : '0s';

    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowRedirectModal(false)}>
        <div className={`rounded-2xl w-full max-w-lg p-6 shadow-2xl ${darkMode ? 'bg-slate-800' : 'bg-white'}`} onClick={e => e.stopPropagation()}>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-indigo-400 to-purple-500 rounded-full flex items-center justify-center">
              <span className="text-2xl">↪</span>
            </div>
            <div>
              <h3 className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('redirectTicket')}</h3>
              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('transferResponsibility')}</p>
            </div>
          </div>
          
          {/* Time spent info */}
          <div className={`mb-4 p-3 rounded-xl flex items-center justify-between ${darkMode ? 'bg-slate-700' : 'bg-slate-50'}`}>
            <div className="flex items-center gap-2">
              <span className="text-xl">⏱️</span>
              <div>
                <p className={`text-sm font-medium ${darkMode ? 'text-slate-200' : 'text-slate-700'}`}>{t('yourTimeSpent')}</p>
                <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('willBeRecorded')}</p>
              </div>
            </div>
            <span className={`text-lg font-mono font-bold ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>{timeSpent}</span>
          </div>

          <div className="mb-4">
            <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>{t('redirectTo')} *</label>
            <div className="grid grid-cols-2 gap-2">
              {teamMembers.filter(m => m.id !== currentUser?.id).map(member => (
                <button 
                  key={member.id} 
                  onClick={() => { setSelectedUser(member); setErrors({ ...errors, user: null }); }}
                  className={`flex items-center gap-3 p-3 border-2 rounded-xl cursor-pointer transition-all ${
                    selectedUser?.id === member.id 
                      ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30' 
                      : errors.user 
                        ? 'border-red-300' 
                        : darkMode ? 'border-slate-600 hover:border-indigo-400 hover:bg-slate-700' : 'border-slate-200 hover:border-indigo-300 hover:bg-slate-50'
                  }`}
                >
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                    {member.avatar}
                  </div>
                  <div className="text-left flex-1">
                    <p className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-slate-800'}`}>{member.name}</p>
                    <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{member.role}</p>
                  </div>
                  {selectedUser?.id === member.id && <span className="text-indigo-600">✓</span>}
                </button>
              ))}
            </div>
            {errors.user && <p className="text-red-500 text-xs mt-1">{errors.user}</p>}
          </div>

          <div className="mb-4">
            <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>{t('handoffNote')} *</label>
            <textarea 
              value={localReason}
              onChange={(e) => { setLocalReason(e.target.value); setErrors({ ...errors, reason: null }); }}
              className={`w-full p-4 border rounded-xl text-sm resize-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                errors.reason ? 'border-red-500' : darkMode ? 'bg-slate-700 border-slate-600 text-white placeholder-slate-400' : 'border-slate-200 placeholder-slate-400'
              }`}
              rows={3}
              placeholder={t('whyPassing')}
            />
            {errors.reason && <p className="text-red-500 text-xs mt-1">{errors.reason}</p>}
          </div>
          
          <div className={`mb-4 p-3 rounded-xl ${darkMode ? 'bg-amber-900/30' : 'bg-amber-50'}`}>
            <div className="flex items-center gap-2">
              <span>⚠️</span>
              <p className={`text-xs ${darkMode ? 'text-amber-300' : 'text-amber-700'}`}>
                {t('ticketWillDisappear')}
              </p>
            </div>
          </div>

          <div className="flex gap-3">
            <button 
              className={`flex-1 py-3 border rounded-xl font-medium transition-colors ${
                darkMode ? 'border-slate-600 text-slate-300 hover:bg-slate-700' : 'border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
              onClick={() => { setShowRedirectModal(false); setLocalReason(''); setSelectedUser(null); setErrors({}); }}
            >
              {t('cancel')}
            </button>
            <button 
              className="flex-1 py-3 bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-xl hover:from-indigo-600 hover:to-purple-600 transition-all font-bold shadow-lg"
              onClick={handleSubmit}
            >
              {t('redirectNow')}
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Epic Documents Modal
  const EpicDocsModal = () => {
    const epicId = showEpicDocsModal;
    const epic = epics.find(e => e.id === epicId);
    const docs = epicDocs[epicId] || [];
    const fileInputRef = useRef(null);

    if (!epic) return null;

    const handleFileUpload = (e) => {
      const files = e.target.files;
      if (files && files.length > 0) {
        Array.from(files).forEach(file => {
          handleUploadEpicDoc(epicId, file);
        });
      }
    };

    const getFileIcon = (type) => {
      switch(type) {
        case 'pdf': return '📄';
        case 'md': return '📝';
        case 'doc': case 'docx': return '📃';
        case 'xls': case 'xlsx': return '📊';
        default: return '📎';
      }
    };

    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowEpicDocsModal(null)}>
        <div className={`rounded-2xl w-full max-w-lg shadow-2xl ${darkMode ? 'bg-slate-800' : 'bg-white'}`} onClick={e => e.stopPropagation()}>
          {/* Header */}
          <div className={`p-5 border-b ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-indigo-400 to-purple-500 rounded-xl flex items-center justify-center">
                  <span className="text-2xl">📎</span>
                </div>
                <div>
                  <h3 className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('epicDocs')}</h3>
                  <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{epic.name}</p>
                </div>
              </div>
              <button 
                onClick={() => setShowEpicDocsModal(null)}
                className={`p-2 rounded-lg transition-colors ${darkMode ? 'hover:bg-slate-700 text-slate-400' : 'hover:bg-slate-100 text-slate-500'}`}
              >
                ✕
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-5 max-h-96 overflow-auto">
            {docs.length === 0 ? (
              <div className={`text-center py-8 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>
                <span className="text-4xl block mb-3">📂</span>
                <p className="font-medium">{t('noDocsAttached')}</p>
                <p className="text-sm mt-1">{t('uploadSpec')}</p>
              </div>
            ) : (
              <div className="space-y-2">
                <p className={`text-sm font-medium mb-3 ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                  {t('attachedFiles')} ({docs.length})
                </p>
                {docs.map((doc, idx) => (
                  <div 
                    key={idx}
                    className={`flex items-center gap-3 p-3 rounded-xl transition-colors ${
                      darkMode ? 'bg-slate-700 hover:bg-slate-600' : 'bg-slate-50 hover:bg-slate-100'
                    }`}
                  >
                    <span className="text-2xl">{getFileIcon(doc.type)}</span>
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-medium truncate ${darkMode ? 'text-white' : 'text-slate-800'}`}>{doc.name}</p>
                      <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                        {doc.size} • {doc.uploadedAt}
                      </p>
                    </div>
                    <div className="flex items-center gap-1">
                      <button className={`p-2 rounded-lg transition-colors ${darkMode ? 'hover:bg-slate-600 text-slate-400' : 'hover:bg-slate-200 text-slate-500'}`}>
                        👁️
                      </button>
                      <button className={`p-2 rounded-lg transition-colors ${darkMode ? 'hover:bg-slate-600 text-slate-400' : 'hover:bg-slate-200 text-slate-500'}`}>
                        ⬇️
                      </button>
                      <button 
                        onClick={() => {
                          setEpicDocs(prev => ({
                            ...prev,
                            [epicId]: prev[epicId].filter((_, i) => i !== idx)
                          }));
                        }}
                        className={`p-2 rounded-lg transition-colors ${darkMode ? 'hover:bg-red-900/50 text-red-400' : 'hover:bg-red-100 text-red-500'}`}
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer with Upload Button */}
          <div className={`p-5 border-t ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf,.md,.doc,.docx,.xls,.xlsx,.txt"
              onChange={handleFileUpload}
              className="hidden"
            />
            <button 
              onClick={() => fileInputRef.current?.click()}
              className="w-full py-3 bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-xl hover:from-indigo-600 hover:to-purple-600 transition-all font-bold shadow-lg flex items-center justify-center gap-2"
            >
              <span className="text-lg">📤</span>
              <span>{t('uploadSpec')}</span>
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Team Assignment Tab - For Team Leads Only
  const TeamAssignmentTab = () => {
    const [assignmentModal, setAssignmentModal] = useState(null); // ticket to assign
    const [selectedMember, setSelectedMember] = useState(null);
    
    // Get all tickets from epics for assignment
    const allTickets = epics.flatMap(epic => 
      epic.tickets.map(ticket => ({ ...ticket, epicName: epic.name, epicId: epic.id }))
    );
    
    // Unassigned tickets (no assigneeId or assigneeId is null)
    const unassignedTickets = allTickets.filter(t => !t.assigneeId);
    
    // Group assigned tickets by member
    const ticketsByMember = teamMembers.map(member => ({
      ...member,
      tickets: allTickets.filter(t => t.assigneeId === member.id)
    }));

    // Handle assign ticket
    const handleAssignTicket = (ticket, memberId) => {
      const member = teamMembers.find(m => m.id === memberId);
      setEpics(prev => prev.map(epic => ({
        ...epic,
        tickets: epic.tickets.map(t => 
          t.id === ticket.id 
            ? { ...t, assigneeId: memberId, assignee: member?.name || 'Unknown' }
            : t
        )
      })));
      setAssignmentModal(null);
      setSelectedMember(null);
      console.log(`API PATCH /tickets/${ticket.id}`, { assignee_id: memberId });
    };

    // Handle unassign ticket
    const handleUnassignTicket = (ticket) => {
      setEpics(prev => prev.map(epic => ({
        ...epic,
        tickets: epic.tickets.map(t => 
          t.id === ticket.id 
            ? { ...t, assigneeId: null, assignee: null }
            : t
        )
      })));
      console.log(`API PATCH /tickets/${ticket.id}`, { assignee_id: null });
    };

    return (
      <div className={`flex-1 overflow-auto p-6 ${darkMode ? 'bg-slate-900' : 'bg-slate-50'}`}>
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-2">
            <span className="text-2xl">👑</span>
            <h1 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('teamAssignment')}</h1>
            <span className="px-3 py-1 text-xs font-medium rounded-full bg-amber-100 text-amber-700">{t('teamLeadOnly')}</span>
          </div>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('manageTeamWorkload')}</p>
        </div>

        <div className="grid grid-cols-12 gap-6">
          {/* Unassigned Tickets Column */}
          <div className="col-span-4">
            <div className={`rounded-xl shadow-sm border ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
              <div className={`p-4 border-b ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
                <div className="flex items-center justify-between">
                  <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>
                    {t('unassignedTickets')}
                  </h3>
                  <span className={`px-2 py-1 text-sm font-bold rounded-full ${
                    unassignedTickets.length > 0 
                      ? 'bg-red-100 text-red-700' 
                      : 'bg-emerald-100 text-emerald-700'
                  }`}>
                    {unassignedTickets.length}
                  </span>
                </div>
              </div>
              
              <div className="p-4 space-y-3 max-h-[600px] overflow-auto">
                {unassignedTickets.length === 0 ? (
                  <div className={`text-center py-8 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>
                    <span className="text-4xl block mb-3">✅</span>
                    <p className="font-medium">{t('noUnassignedTickets')}</p>
                  </div>
                ) : (
                  unassignedTickets.map(ticket => (
                    <div 
                      key={ticket.id}
                      className={`p-4 rounded-xl border transition-all hover:shadow-md ${
                        darkMode ? 'bg-slate-700 border-slate-600 hover:border-blue-500' : 'bg-slate-50 border-slate-200 hover:border-blue-400'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4 className={`text-sm font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{ticket.title}</h4>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          ticket.status === 'blocked' ? 'bg-amber-100 text-amber-700' :
                          ticket.status === 'progress' ? 'bg-blue-100 text-blue-700' :
                          'bg-slate-100 text-slate-600'
                        }`}>
                          {ticket.status}
                        </span>
                      </div>
                      <p className={`text-xs mb-3 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                        📁 {ticket.epicName}
                      </p>
                      <button
                        onClick={() => setAssignmentModal(ticket)}
                        className="w-full py-2 bg-gradient-to-r from-blue-500 to-indigo-500 text-white text-sm font-medium rounded-lg hover:from-blue-600 hover:to-indigo-600 transition-all"
                      >
                        {t('assignTicket')}
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Team Members with Assigned Tickets */}
          <div className="col-span-8">
            <div className={`rounded-xl shadow-sm border ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
              <div className={`p-4 border-b ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
                <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>
                  {t('assignedTickets')}
                </h3>
              </div>
              
              <div className="p-4 space-y-4 max-h-[600px] overflow-auto">
                {ticketsByMember.map(member => (
                  <div 
                    key={member.id}
                    className={`p-4 rounded-xl border ${darkMode ? 'bg-slate-700 border-slate-600' : 'bg-slate-50 border-slate-200'}`}
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold ${
                        member.isTeamLead 
                          ? 'bg-gradient-to-br from-amber-400 to-orange-500' 
                          : 'bg-gradient-to-br from-blue-400 to-indigo-500'
                      }`}>
                        {member.avatar}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h4 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{member.name}</h4>
                          {member.isTeamLead && (
                            <span className="text-xs">👑</span>
                          )}
                        </div>
                        <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{member.role}</p>
                      </div>
                      <div className="text-right">
                        <p className={`text-2xl font-bold ${
                          member.tickets.length > 5 ? 'text-red-500' :
                          member.tickets.length > 3 ? 'text-amber-500' :
                          'text-emerald-500'
                        }`}>
                          {member.tickets.length}
                        </p>
                        <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>{t('tickets')}</p>
                      </div>
                    </div>
                    
                    {/* Workload Bar */}
                    <div className="mb-3">
                      <div className={`h-2 rounded-full overflow-hidden ${darkMode ? 'bg-slate-600' : 'bg-slate-200'}`}>
                        <div 
                          className={`h-full rounded-full transition-all ${
                            member.tickets.length > 5 ? 'bg-red-500' :
                            member.tickets.length > 3 ? 'bg-amber-500' :
                            'bg-emerald-500'
                          }`}
                          style={{ width: `${Math.min((member.tickets.length / 8) * 100, 100)}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Tickets List */}
                    {member.tickets.length > 0 ? (
                      <div className="space-y-2">
                        {member.tickets.map(ticket => (
                          <div 
                            key={ticket.id}
                            className={`flex items-center justify-between p-2 rounded-lg ${
                              darkMode ? 'bg-slate-600' : 'bg-white'
                            }`}
                          >
                            <div className="flex items-center gap-2 flex-1 min-w-0">
                              <span className={`w-2 h-2 rounded-full ${
                                ticket.status === 'blocked' ? 'bg-amber-500' :
                                ticket.status === 'progress' ? 'bg-blue-500' :
                                ticket.status === 'done' ? 'bg-emerald-500' :
                                'bg-slate-400'
                              }`}></span>
                              <span className={`text-sm truncate ${darkMode ? 'text-slate-200' : 'text-slate-700'}`}>
                                {ticket.title}
                              </span>
                            </div>
                            <button
                              onClick={() => handleUnassignTicket(ticket)}
                              className={`px-2 py-1 text-xs rounded transition-colors ${
                                darkMode 
                                  ? 'text-red-400 hover:bg-red-900/50' 
                                  : 'text-red-600 hover:bg-red-100'
                              }`}
                              title={t('unassign')}
                            >
                              ✕
                            </button>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className={`text-xs text-center py-2 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>
                        {t('noAssignedTickets')}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Assignment Modal */}
        {assignmentModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setAssignmentModal(null)}>
            <div className={`rounded-2xl w-full max-w-md shadow-2xl ${darkMode ? 'bg-slate-800' : 'bg-white'}`} onClick={e => e.stopPropagation()}>
              <div className={`p-5 border-b ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
                <h3 className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('assignTicket')}</h3>
                <p className={`text-sm mt-1 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                  {assignmentModal.title}
                </p>
              </div>
              
              <div className="p-5">
                <p className={`text-sm font-medium mb-3 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                  {t('selectDeveloper')}:
                </p>
                <div className="space-y-2 max-h-64 overflow-auto">
                  {teamMembers.map(member => (
                    <button
                      key={member.id}
                      onClick={() => setSelectedMember(member.id)}
                      className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all ${
                        selectedMember === member.id
                          ? 'bg-blue-100 border-2 border-blue-500'
                          : darkMode 
                            ? 'bg-slate-700 hover:bg-slate-600 border-2 border-transparent' 
                            : 'bg-slate-50 hover:bg-slate-100 border-2 border-transparent'
                      }`}
                    >
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold ${
                        member.isTeamLead 
                          ? 'bg-gradient-to-br from-amber-400 to-orange-500' 
                          : 'bg-gradient-to-br from-blue-400 to-indigo-500'
                      }`}>
                        {member.avatar}
                      </div>
                      <div className="flex-1 text-left">
                        <p className={`font-medium ${darkMode ? 'text-white' : 'text-slate-800'}`}>
                          {member.name}
                          {member.isTeamLead && <span className="ml-1">👑</span>}
                        </p>
                        <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                          {member.role} • {ticketsByMember.find(m => m.id === member.id)?.tickets.length || 0} {t('tickets')}
                        </p>
                      </div>
                      {selectedMember === member.id && (
                        <span className="text-blue-600 text-xl">✓</span>
                      )}
                    </button>
                  ))}
                </div>
              </div>
              
              <div className={`p-5 border-t ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
                <div className="flex gap-3">
                  <button 
                    onClick={() => { setAssignmentModal(null); setSelectedMember(null); }}
                    className={`flex-1 py-3 rounded-xl font-medium transition-colors ${
                      darkMode 
                        ? 'bg-slate-700 text-slate-300 hover:bg-slate-600' 
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    {t('cancel')}
                  </button>
                  <button 
                    onClick={() => selectedMember && handleAssignTicket(assignmentModal, selectedMember)}
                    disabled={!selectedMember}
                    className={`flex-1 py-3 rounded-xl font-bold transition-all ${
                      selectedMember
                        ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white hover:from-blue-600 hover:to-indigo-600'
                        : darkMode 
                          ? 'bg-slate-700 text-slate-500 cursor-not-allowed' 
                          : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                    }`}
                  >
                    {t('assignTicket')}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  // Admin Code & Docs Repository Tab
  const AdminCodeDocsTab = () => {
    const [selectedProject, setSelectedProject] = useState(0);
    const [viewMode, setViewMode] = useState('all'); // 'all', 'code', 'docs'
    const [detailView, setDetailView] = useState(null); // 'codeFiles', 'documentation', 'contributors', or null
    
    // Translation state - moved to parent level to avoid hook rules violation
    const [translateDropdown, setTranslateDropdown] = useState(null);
    const [translatingDocs, setTranslatingDocs] = useState({});
    
    // Keyboard handler for Escape key
    useEffect(() => {
      const handleKeyDown = (e) => {
        if (e.key === 'Escape' && detailView) {
          setDetailView(null);
          setTranslateDropdown(null);
        }
      };
      
      if (detailView) {
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
      }
    }, [detailView]);

    // Repository data per project
    const projectRepositories = [
      {
        projectId: 0,
        projectName: 'Payment Gateway',
        projectIcon: '💳',
        totalCodeFiles: 47,
        totalDocFiles: 23,
        lastUpdate: 'Dec 28, 2024',
        developerStats: [
          { id: 1, name: 'Ana García', avatar: 'AG', codeFiles: 18, docFiles: 8, lastUpload: '2 hours ago', totalSize: '245 KB', email: 'ana.garcia@company.com', role: 'Frontend Lead' },
          { id: 2, name: 'Carlos Ruiz', avatar: 'CR', codeFiles: 22, docFiles: 10, lastUpload: '1 day ago', totalSize: '312 KB', email: 'carlos.ruiz@company.com', role: 'Backend Developer' },
          { id: 3, name: 'Maria López', avatar: 'ML', codeFiles: 7, docFiles: 5, lastUpload: '3 days ago', totalSize: '89 KB', email: 'maria.lopez@company.com', role: 'Full Stack Developer' },
        ],
        codeFilesList: [
          { name: 'payment-handler.ts', author: 'Ana García', date: 'Dec 28', size: '12.4 KB', status: 'approved', language: 'TypeScript', lines: 342 },
          { name: 'stripe-webhook.js', author: 'Carlos Ruiz', date: 'Dec 27', size: '8.2 KB', status: 'pending', language: 'JavaScript', lines: 215 },
          { name: 'checkout-flow.ts', author: 'Maria López', date: 'Dec 25', size: '15.7 KB', status: 'approved', language: 'TypeScript', lines: 428 },
          { name: 'refund-processor.ts', author: 'Carlos Ruiz', date: 'Dec 24', size: '9.8 KB', status: 'approved', language: 'TypeScript', lines: 267 },
          { name: 'payment-types.d.ts', author: 'Ana García', date: 'Dec 23', size: '3.2 KB', status: 'approved', language: 'TypeScript', lines: 89 },
          { name: 'card-validator.js', author: 'Maria López', date: 'Dec 22', size: '5.1 KB', status: 'approved', language: 'JavaScript', lines: 134 },
          { name: 'subscription-manager.ts', author: 'Carlos Ruiz', date: 'Dec 21', size: '18.3 KB', status: 'approved', language: 'TypeScript', lines: 512 },
        ],
        docFilesList: [
          { name: 'API-Integration-Guide.md', author: 'Ana García', date: 'Dec 26', size: '24.1 KB', status: 'approved', docType: 'API Reference', pages: 15 },
          { name: 'Error-Handling-Spec.pdf', author: 'Carlos Ruiz', date: 'Dec 24', size: '156 KB', status: 'approved', docType: 'Technical Spec', pages: 8 },
          { name: 'Payment-Flow-Diagram.md', author: 'Maria López', date: 'Dec 22', size: '8.5 KB', status: 'approved', docType: 'Technical Spec', pages: 3 },
          { name: 'Stripe-Setup-Guide.md', author: 'Ana García', date: 'Dec 20', size: '12.3 KB', status: 'approved', docType: 'User Guide', pages: 6 },
          { name: 'Security-Best-Practices.pdf', author: 'Carlos Ruiz', date: 'Dec 18', size: '89 KB', status: 'approved', docType: 'Technical Spec', pages: 12 },
        ],
        recentFiles: [
          { name: 'payment-handler.ts', type: 'code', author: 'Ana García', date: 'Dec 28', size: '12.4 KB', status: 'approved' },
          { name: 'stripe-webhook.js', type: 'code', author: 'Carlos Ruiz', date: 'Dec 27', size: '8.2 KB', status: 'pending' },
          { name: 'API-Integration-Guide.md', type: 'doc', author: 'Ana García', date: 'Dec 26', size: '24.1 KB', status: 'approved' },
          { name: 'checkout-flow.ts', type: 'code', author: 'Maria López', date: 'Dec 25', size: '15.7 KB', status: 'approved' },
          { name: 'Error-Handling-Spec.pdf', type: 'doc', author: 'Carlos Ruiz', date: 'Dec 24', size: '156 KB', status: 'approved' },
        ]
      },
      {
        projectId: 1,
        projectName: 'User Dashboard',
        projectIcon: '📊',
        totalCodeFiles: 35,
        totalDocFiles: 18,
        lastUpdate: 'Dec 27, 2024',
        developerStats: [
          { id: 1, name: 'Ana García', avatar: 'AG', codeFiles: 15, docFiles: 7, lastUpload: '1 day ago', totalSize: '178 KB', email: 'ana.garcia@company.com', role: 'Frontend Lead' },
          { id: 3, name: 'Maria López', avatar: 'ML', codeFiles: 12, docFiles: 6, lastUpload: '2 days ago', totalSize: '134 KB', email: 'maria.lopez@company.com', role: 'Full Stack Developer' },
          { id: 4, name: 'Pedro Santos', avatar: 'PS', codeFiles: 8, docFiles: 5, lastUpload: '4 days ago', totalSize: '92 KB', email: 'pedro.santos@company.com', role: 'Frontend Developer' },
        ],
        codeFilesList: [
          { name: 'dashboard-components.tsx', author: 'Ana García', date: 'Dec 27', size: '22.3 KB', status: 'approved', language: 'TypeScript', lines: 612 },
          { name: 'analytics-service.ts', author: 'Pedro Santos', date: 'Dec 25', size: '11.2 KB', status: 'pending', language: 'TypeScript', lines: 298 },
          { name: 'chart-utils.ts', author: 'Maria López', date: 'Dec 24', size: '8.7 KB', status: 'approved', language: 'TypeScript', lines: 234 },
          { name: 'data-fetcher.ts', author: 'Ana García', date: 'Dec 23', size: '14.5 KB', status: 'approved', language: 'TypeScript', lines: 389 },
        ],
        docFilesList: [
          { name: 'User-Guide.md', author: 'Maria López', date: 'Dec 26', size: '18.5 KB', status: 'approved', docType: 'User Guide', pages: 10 },
          { name: 'Dashboard-Architecture.md', author: 'Ana García', date: 'Dec 24', size: '12.3 KB', status: 'approved', docType: 'Technical Spec', pages: 7 },
          { name: 'Widget-API.md', author: 'Pedro Santos', date: 'Dec 22', size: '9.8 KB', status: 'approved', docType: 'API Reference', pages: 5 },
        ],
        recentFiles: [
          { name: 'dashboard-components.tsx', type: 'code', author: 'Ana García', date: 'Dec 27', size: '22.3 KB', status: 'approved' },
          { name: 'User-Guide.md', type: 'doc', author: 'Maria López', date: 'Dec 26', size: '18.5 KB', status: 'approved' },
          { name: 'analytics-service.ts', type: 'code', author: 'Pedro Santos', date: 'Dec 25', size: '11.2 KB', status: 'pending' },
        ]
      },
      {
        projectId: 2,
        projectName: 'API Platform',
        projectIcon: '🔌',
        totalCodeFiles: 52,
        totalDocFiles: 31,
        lastUpdate: 'Dec 28, 2024',
        developerStats: [
          { id: 2, name: 'Carlos Ruiz', avatar: 'CR', codeFiles: 28, docFiles: 15, lastUpload: '5 hours ago', totalSize: '387 KB', email: 'carlos.ruiz@company.com', role: 'Backend Developer' },
          { id: 3, name: 'Maria López', avatar: 'ML', codeFiles: 14, docFiles: 9, lastUpload: '1 day ago', totalSize: '156 KB', email: 'maria.lopez@company.com', role: 'Full Stack Developer' },
          { id: 4, name: 'Pedro Santos', avatar: 'PS', codeFiles: 10, docFiles: 7, lastUpload: '2 days ago', totalSize: '112 KB', email: 'pedro.santos@company.com', role: 'Frontend Developer' },
        ],
        codeFilesList: [
          { name: 'api-router.go', author: 'Carlos Ruiz', date: 'Dec 28', size: '34.2 KB', status: 'pending', language: 'Go', lines: 892 },
          { name: 'auth-middleware.go', author: 'Maria López', date: 'Dec 27', size: '12.1 KB', status: 'approved', language: 'Go', lines: 324 },
          { name: 'rate-limiter.go', author: 'Pedro Santos', date: 'Dec 26', size: '8.9 KB', status: 'approved', language: 'Go', lines: 245 },
          { name: 'database-connector.go', author: 'Carlos Ruiz', date: 'Dec 25', size: '21.4 KB', status: 'approved', language: 'Go', lines: 567 },
          { name: 'cache-manager.go', author: 'Maria López', date: 'Dec 24', size: '15.8 KB', status: 'approved', language: 'Go', lines: 423 },
        ],
        docFilesList: [
          { name: 'REST-API-Reference.md', author: 'Carlos Ruiz', date: 'Dec 28', size: '45.8 KB', status: 'approved', docType: 'API Reference', pages: 28 },
          { name: 'Authentication-Guide.md', author: 'Maria López', date: 'Dec 26', size: '18.2 KB', status: 'approved', docType: 'User Guide', pages: 12 },
          { name: 'Rate-Limiting-Spec.md', author: 'Pedro Santos', date: 'Dec 24', size: '8.5 KB', status: 'approved', docType: 'Technical Spec', pages: 5 },
          { name: 'Database-Schema.pdf', author: 'Carlos Ruiz', date: 'Dec 22', size: '234 KB', status: 'approved', docType: 'Technical Spec', pages: 15 },
        ],
        recentFiles: [
          { name: 'api-router.go', type: 'code', author: 'Carlos Ruiz', date: 'Dec 28', size: '34.2 KB', status: 'pending' },
          { name: 'REST-API-Reference.md', type: 'doc', author: 'Carlos Ruiz', date: 'Dec 28', size: '45.8 KB', status: 'approved' },
          { name: 'auth-middleware.go', type: 'code', author: 'Maria López', date: 'Dec 27', size: '12.1 KB', status: 'approved' },
          { name: 'rate-limiter.go', type: 'code', author: 'Pedro Santos', date: 'Dec 26', size: '8.9 KB', status: 'approved' },
        ]
      },
    ];

    const currentProject = projectRepositories[selectedProject];
    const filteredFiles = viewMode === 'all' 
      ? currentProject.recentFiles 
      : currentProject.recentFiles.filter(f => f.type === viewMode);

    // Detail Panel - rendered as function, not component (to prevent remounting)
    const renderDetailPanel = () => {
      if (!detailView) return null;

      const closePanel = () => {
        setDetailView(null);
        setTranslateDropdown(null);
      };

      // Code Files Detail
      if (detailView === 'codeFiles') {
        return (
          <div className={`fixed inset-0 z-50 flex justify-end`}>
            {/* Backdrop - click to close disabled */}
            <div 
              className="absolute inset-0 bg-black/30 transition-opacity" 
              onClick={(e) => e.stopPropagation()}
            ></div>
            <div 
              className={`relative w-full max-w-2xl h-full overflow-auto shadow-2xl transform transition-transform duration-300 ${darkMode ? 'bg-slate-800' : 'bg-white'}`}
              onClick={(e) => e.stopPropagation()}
            >
              <div className={`sticky top-0 p-6 border-b z-10 ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center">
                      <span className="text-2xl">💻</span>
                    </div>
                    <div>
                      <h2 className={`text-xl font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('codeFiles')}</h2>
                      <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{currentProject.totalCodeFiles} files in {currentProject.projectName}</p>
                    </div>
                  </div>
                  {/* More prominent close button */}
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      closePanel();
                    }} 
                    className={`p-3 rounded-xl transition-all hover:scale-110 ${darkMode ? 'bg-slate-700 hover:bg-red-900/50 text-slate-400 hover:text-red-400' : 'bg-slate-100 hover:bg-red-100 text-slate-500 hover:text-red-600'}`}
                    title="Close panel"
                  >
                    <span className="text-lg">✕</span>
                  </button>
                </div>
                <p className={`text-xs mt-2 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>
                  Press ✕ or Escape to close this panel
                </p>
              </div>
              
              <div className="p-6">
                {/* Stats Summary */}
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className={`p-4 rounded-xl ${darkMode ? 'bg-slate-700' : 'bg-slate-50'}`}>
                    <p className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{currentProject.codeFilesList?.filter(f => f.status === 'approved').length || 0}</p>
                    <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('approved')}</p>
                  </div>
                  <div className={`p-4 rounded-xl ${darkMode ? 'bg-slate-700' : 'bg-slate-50'}`}>
                    <p className="text-2xl font-bold text-amber-600">{currentProject.codeFilesList?.filter(f => f.status === 'pending').length || 0}</p>
                    <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('pendingReview')}</p>
                  </div>
                  <div className={`p-4 rounded-xl ${darkMode ? 'bg-slate-700' : 'bg-slate-50'}`}>
                    <p className="text-2xl font-bold text-blue-600">{currentProject.codeFilesList?.reduce((sum, f) => sum + (f.lines || 0), 0).toLocaleString() || 0}</p>
                    <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Total Lines</p>
                  </div>
                </div>

                {/* File List */}
                <div className="space-y-3">
                  {currentProject.codeFilesList?.map((file, idx) => (
                    <div key={idx} className={`p-4 rounded-xl border transition-colors ${darkMode ? 'bg-slate-700 border-slate-600 hover:bg-slate-600' : 'bg-white border-slate-200 hover:bg-slate-50'}`}>
                      <div className="flex items-start gap-3">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${darkMode ? 'bg-slate-600' : 'bg-slate-100'}`}>
                          <span className="text-lg">📄</span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <p className={`text-sm font-semibold truncate ${darkMode ? 'text-white' : 'text-slate-800'}`}>{file.name}</p>
                            <span className={`px-2 py-0.5 text-xs rounded-full ${
                              file.status === 'approved' 
                                ? 'bg-emerald-100 text-emerald-700' 
                                : 'bg-amber-100 text-amber-700'
                            }`}>
                              {file.status === 'approved' ? '✓' : '⏳'} {file.status}
                            </span>
                          </div>
                          <div className={`flex items-center gap-3 text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                            <span>{file.author}</span>
                            <span>•</span>
                            <span>{file.date}</span>
                            <span>•</span>
                            <span>{file.size}</span>
                            <span>•</span>
                            <span className="px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded">{file.language}</span>
                            <span>•</span>
                            <span>{file.lines} lines</span>
                          </div>
                        </div>
                        <div className="flex gap-1">
                          <button className={`p-2 rounded-lg transition-colors ${darkMode ? 'hover:bg-slate-500 text-slate-400' : 'hover:bg-blue-50 text-slate-400 hover:text-blue-600'}`}>👁️</button>
                          <button className={`p-2 rounded-lg transition-colors ${darkMode ? 'hover:bg-slate-500 text-slate-400' : 'hover:bg-emerald-50 text-slate-400 hover:text-emerald-600'}`}>⬇️</button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        );
      }

      // Documentation Detail
      if (detailView === 'documentation') {
        const targetLanguages = [
          { code: 'es', name: 'Español', flag: '🇪🇸' },
          { code: 'en', name: 'English', flag: '🇺🇸' },
          { code: 'fr', name: 'Français', flag: '🇫🇷' },
          { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
          { code: 'pt', name: 'Português', flag: '🇧🇷' },
          { code: 'zh', name: '中文', flag: '🇨🇳' },
          { code: 'ja', name: '日本語', flag: '🇯🇵' },
          { code: 'ko', name: '한국어', flag: '🇰🇷' },
        ];

        const startTranslation = (docIdx, lang) => {
          setTranslateDropdown(null);
          setTranslatingDocs(prev => ({
            ...prev,
            [docIdx]: { targetLang: lang, progress: 0, status: 'translating' }
          }));
          
          // Simulate translation progress
          let progress = 0;
          const interval = setInterval(() => {
            progress += Math.random() * 15 + 5;
            if (progress >= 100) {
              progress = 100;
              clearInterval(interval);
              setTranslatingDocs(prev => ({
                ...prev,
                [docIdx]: { ...prev[docIdx], progress: 100, status: 'completed' }
              }));
            } else {
              setTranslatingDocs(prev => ({
                ...prev,
                [docIdx]: { ...prev[docIdx], progress }
              }));
            }
          }, 500);
        };

        return (
          <div className={`fixed inset-0 z-50 flex justify-end`}>
            {/* Backdrop - click to close disabled, only visual overlay */}
            <div 
              className="absolute inset-0 bg-black/30 transition-opacity" 
              onClick={(e) => {
                // Only close if clicking directly on backdrop (double-click for safety)
                e.stopPropagation();
              }}
            ></div>
            <div 
              className={`relative w-full max-w-2xl h-full overflow-auto shadow-2xl transform transition-transform duration-300 ${darkMode ? 'bg-slate-800' : 'bg-white'}`}
              onClick={(e) => e.stopPropagation()}
            >
              <div className={`sticky top-0 p-6 border-b z-10 ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center">
                      <span className="text-2xl">📚</span>
                    </div>
                    <div>
                      <h2 className={`text-xl font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('documentation')}</h2>
                      <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{currentProject.totalDocFiles} documents in {currentProject.projectName}</p>
                    </div>
                  </div>
                  {/* More prominent close button */}
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      closePanel();
                    }} 
                    className={`p-3 rounded-xl transition-all hover:scale-110 ${darkMode ? 'bg-slate-700 hover:bg-red-900/50 text-slate-400 hover:text-red-400' : 'bg-slate-100 hover:bg-red-100 text-slate-500 hover:text-red-600'}`}
                    title="Close panel"
                  >
                    <span className="text-lg">✕</span>
                  </button>
                </div>
                
                {/* Close hint */}
                <p className={`text-xs mt-2 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>
                  Press ✕ or Escape to close this panel
                </p>
              </div>
              
              <div className="p-6">
                {/* Doc Type Summary */}
                <div className="grid grid-cols-4 gap-3 mb-6">
                  {['API Reference', 'User Guide', 'Technical Spec', 'README'].map((docType, idx) => {
                    const count = currentProject.docFilesList?.filter(d => d.docType === docType).length || 0;
                    const icons = ['🔌', '📖', '⚙️', '📝'];
                    return (
                      <div key={docType} className={`p-3 rounded-xl text-center ${darkMode ? 'bg-slate-700' : 'bg-indigo-50'}`}>
                        <span className="text-xl">{icons[idx]}</span>
                        <p className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-indigo-700'}`}>{count}</p>
                        <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-indigo-600'}`}>{docType}</p>
                      </div>
                    );
                  })}
                </div>

                {/* Doc List with Translate Button */}
                <div className="space-y-3">
                  {currentProject.docFilesList?.map((doc, idx) => {
                    const translation = translatingDocs[idx];
                    const isTranslating = translation?.status === 'translating';
                    const isCompleted = translation?.status === 'completed';
                    
                    return (
                      <div key={idx} className={`p-4 rounded-xl border transition-colors ${darkMode ? 'bg-slate-700 border-slate-600 hover:bg-slate-600' : 'bg-white border-slate-200 hover:bg-slate-50'}`}>
                        <div className="flex items-start gap-3">
                          <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                            <span className="text-lg">📄</span>
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <p className={`text-sm font-semibold truncate ${darkMode ? 'text-white' : 'text-slate-800'}`}>{doc.name}</p>
                              <span className="px-2 py-0.5 text-xs rounded-full bg-indigo-100 text-indigo-700">{doc.docType}</span>
                              {isCompleted && (
                                <span className="px-2 py-0.5 text-xs rounded-full bg-emerald-100 text-emerald-700 flex items-center gap-1">
                                  <span>{targetLanguages.find(l => l.code === translation.targetLang)?.flag}</span>
                                  {t('translated')}
                                </span>
                              )}
                            </div>
                            <div className={`flex items-center gap-3 text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                              <span>{doc.author}</span>
                              <span>•</span>
                              <span>{doc.date}</span>
                              <span>•</span>
                              <span>{doc.size}</span>
                              <span>•</span>
                              <span>{doc.pages} pages</span>
                            </div>
                            
                            {/* Translation Progress Bar */}
                            {isTranslating && (
                              <div className="mt-3">
                                <div className="flex items-center justify-between mb-1">
                                  <span className={`text-xs flex items-center gap-1 ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>
                                    <span className="animate-spin">⏳</span>
                                    {t('translatingTo')} {targetLanguages.find(l => l.code === translation.targetLang)?.flag} {targetLanguages.find(l => l.code === translation.targetLang)?.name}...
                                  </span>
                                  <span className={`text-xs font-medium ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>{Math.round(translation.progress)}%</span>
                                </div>
                                <div className={`h-2 rounded-full overflow-hidden ${darkMode ? 'bg-slate-600' : 'bg-slate-200'}`}>
                                  <div 
                                    className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-300"
                                    style={{ width: `${translation.progress}%` }}
                                  ></div>
                                </div>
                              </div>
                            )}
                            
                            {/* Translation Completed */}
                            {isCompleted && (
                              <div className={`mt-3 p-2 rounded-lg flex items-center justify-between ${darkMode ? 'bg-emerald-900/30' : 'bg-emerald-50'}`}>
                                <span className={`text-xs flex items-center gap-1 ${darkMode ? 'text-emerald-400' : 'text-emerald-700'}`}>
                                  <span>✅</span>
                                  {t('translationComplete')} - {doc.name.replace(/\.[^.]+$/, '')}-{translation.targetLang}.{doc.name.split('.').pop()}
                                </span>
                                <button className={`text-xs px-2 py-1 rounded ${darkMode ? 'bg-emerald-800 text-emerald-300 hover:bg-emerald-700' : 'bg-emerald-100 text-emerald-700 hover:bg-emerald-200'}`}>
                                  ⬇️ {t('download')}
                                </button>
                              </div>
                            )}
                          </div>
                          
                          {/* Action Buttons */}
                          <div className="flex gap-1 relative">
                            <button className={`p-2 rounded-lg transition-colors ${darkMode ? 'hover:bg-slate-500 text-slate-400' : 'hover:bg-blue-50 text-slate-400 hover:text-blue-600'}`}>👁️</button>
                            <button className={`p-2 rounded-lg transition-colors ${darkMode ? 'hover:bg-slate-500 text-slate-400' : 'hover:bg-emerald-50 text-slate-400 hover:text-emerald-600'}`}>⬇️</button>
                            
                            {/* Translate Button */}
                            <div className="relative">
                              <button 
                                onClick={() => setTranslateDropdown(translateDropdown === idx ? null : idx)}
                                disabled={isTranslating}
                                className={`p-2 rounded-lg transition-all flex items-center gap-1 ${
                                  isTranslating 
                                    ? 'opacity-50 cursor-not-allowed' 
                                    : translateDropdown === idx
                                      ? darkMode ? 'bg-purple-600 text-white' : 'bg-purple-100 text-purple-700'
                                      : darkMode ? 'hover:bg-purple-900/50 text-purple-400 hover:text-purple-300' : 'hover:bg-purple-50 text-slate-400 hover:text-purple-600'
                                }`}
                                title={t('translateDocument')}
                              >
                                <span>🌐</span>
                              </button>
                              
                              {/* Language Dropdown */}
                              {translateDropdown === idx && (
                                <div className={`absolute right-0 top-full mt-2 w-48 rounded-xl shadow-2xl border z-10 overflow-hidden ${
                                  darkMode ? 'bg-slate-700 border-slate-600' : 'bg-white border-slate-200'
                                }`}>
                                  <div className={`px-3 py-2 border-b ${darkMode ? 'border-slate-600 bg-slate-800' : 'border-slate-100 bg-slate-50'}`}>
                                    <p className={`text-xs font-semibold ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>{t('translateTo')}</p>
                                  </div>
                                  <div className="max-h-64 overflow-auto">
                                    {targetLanguages.map(lang => (
                                      <button
                                        key={lang.code}
                                        onClick={() => startTranslation(idx, lang.code)}
                                        className={`w-full px-3 py-2.5 text-left flex items-center gap-3 transition-colors ${
                                          darkMode ? 'hover:bg-slate-600 text-slate-200' : 'hover:bg-purple-50 text-slate-700'
                                        }`}
                                      >
                                        <span className="text-lg">{lang.flag}</span>
                                        <span className="text-sm font-medium">{lang.name}</span>
                                      </button>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
                
                {/* Translation Info */}
                <div className={`mt-6 p-4 rounded-xl ${darkMode ? 'bg-slate-700' : 'bg-gradient-to-r from-purple-50 to-indigo-50'}`}>
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">🌐</span>
                    <div>
                      <h4 className={`font-semibold mb-1 ${darkMode ? 'text-white' : 'text-purple-800'}`}>{t('autoTranslation')}</h4>
                      <p className={`text-sm ${darkMode ? 'text-slate-300' : 'text-purple-700'}`}>
                        {t('autoTranslationDesc')}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      }

      // Contributors Detail
      if (detailView === 'contributors') {
        return (
          <div className={`fixed inset-0 z-50 flex justify-end`}>
            {/* Backdrop - click to close disabled */}
            <div 
              className="absolute inset-0 bg-black/30 transition-opacity" 
              onClick={(e) => e.stopPropagation()}
            ></div>
            <div 
              className={`relative w-full max-w-2xl h-full overflow-auto shadow-2xl transform transition-transform duration-300 ${darkMode ? 'bg-slate-800' : 'bg-white'}`}
              onClick={(e) => e.stopPropagation()}
            >
              <div className={`sticky top-0 p-6 border-b z-10 ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
                      <span className="text-2xl">👥</span>
                    </div>
                    <div>
                      <h2 className={`text-xl font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('contributors')}</h2>
                      <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{currentProject.developerStats.length} contributors in {currentProject.projectName}</p>
                    </div>
                  </div>
                  {/* More prominent close button */}
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      closePanel();
                    }} 
                    className={`p-3 rounded-xl transition-all hover:scale-110 ${darkMode ? 'bg-slate-700 hover:bg-red-900/50 text-slate-400 hover:text-red-400' : 'bg-slate-100 hover:bg-red-100 text-slate-500 hover:text-red-600'}`}
                    title="Close panel"
                  >
                    <span className="text-lg">✕</span>
                  </button>
                </div>
                <p className={`text-xs mt-2 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>
                  Press ✕ or Escape to close this panel
                </p>
              </div>
              
              <div className="p-6">
                {/* Contributors List */}
                <div className="space-y-4">
                  {currentProject.developerStats.map((dev, idx) => {
                    const totalFiles = dev.codeFiles + dev.docFiles;
                    const projectTotal = currentProject.totalCodeFiles + currentProject.totalDocFiles;
                    const contribution = Math.round((totalFiles / projectTotal) * 100);
                    
                    return (
                      <div key={dev.id} className={`p-5 rounded-xl border ${darkMode ? 'bg-slate-700 border-slate-600' : 'bg-white border-slate-200'}`}>
                        <div className="flex items-start gap-4">
                          <div className="w-14 h-14 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-full flex items-center justify-center text-white text-lg font-bold">
                            {dev.avatar}
                          </div>
                          <div className="flex-1">
                            <div className="flex items-start justify-between mb-2">
                              <div>
                                <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{dev.name}</h3>
                                <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{dev.role}</p>
                                <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>{dev.email}</p>
                              </div>
                              <span className={`px-3 py-1 text-sm font-semibold rounded-full ${
                                idx === 0 ? 'bg-amber-100 text-amber-700' : idx === 1 ? 'bg-slate-200 text-slate-700' : 'bg-orange-100 text-orange-700'
                              }`}>
                                #{idx + 1}
                              </span>
                            </div>
                            
                            {/* Stats */}
                            <div className="grid grid-cols-4 gap-3 mt-4">
                              <div className={`p-3 rounded-lg ${darkMode ? 'bg-slate-600' : 'bg-slate-50'}`}>
                                <div className="flex items-center gap-2 mb-1">
                                  <span>💻</span>
                                  <span className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{dev.codeFiles}</span>
                                </div>
                                <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('codeFiles')}</p>
                              </div>
                              <div className={`p-3 rounded-lg ${darkMode ? 'bg-slate-600' : 'bg-indigo-50'}`}>
                                <div className="flex items-center gap-2 mb-1">
                                  <span>📚</span>
                                  <span className="text-lg font-bold text-indigo-600">{dev.docFiles}</span>
                                </div>
                                <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('documentation')}</p>
                              </div>
                              <div className={`p-3 rounded-lg ${darkMode ? 'bg-slate-600' : 'bg-slate-50'}`}>
                                <p className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{dev.totalSize}</p>
                                <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('totalSize')}</p>
                              </div>
                              <div className={`p-3 rounded-lg ${darkMode ? 'bg-slate-600' : 'bg-emerald-50'}`}>
                                <p className="text-lg font-bold text-emerald-600">{contribution}%</p>
                                <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('contribution')}</p>
                              </div>
                            </div>

                            {/* Contribution Bar */}
                            <div className="mt-4">
                              <div className="flex items-center justify-between mb-1">
                                <span className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('contribution')}</span>
                                <span className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('lastUpload')}: {dev.lastUpload}</span>
                              </div>
                              <div className={`h-2 rounded-full overflow-hidden ${darkMode ? 'bg-slate-600' : 'bg-slate-200'}`}>
                                <div 
                                  className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full transition-all"
                                  style={{ width: `${contribution}%` }}
                                ></div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        );
      }

      return null;
    };

    return (
      <div className={`flex-1 overflow-auto p-6 ${darkMode ? 'bg-slate-900' : 'bg-slate-50'}`}>
        <div className="mb-6">
          <h1 className={`text-2xl font-bold mb-1 ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('codeDocRepository')}</h1>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('viewAllProjectFiles')}</p>
        </div>

        {/* Project Selector */}
        <div className="flex gap-3 mb-6">
          {projectRepositories.map((project, idx) => (
            <button
              key={project.projectId}
              onClick={() => { setSelectedProject(idx); setDetailView(null); }}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                selectedProject === idx 
                  ? darkMode ? 'bg-slate-800 shadow-md border-2 border-blue-500' : 'bg-white shadow-md border-2 border-blue-500'
                  : darkMode ? 'bg-slate-800 border border-slate-700 hover:border-slate-600' : 'bg-white border border-slate-200 hover:border-slate-300'
              }`}
            >
              <span className="text-2xl">{project.projectIcon}</span>
              <div className="text-left">
                <p className={`text-sm font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{project.projectName}</p>
                <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{project.totalCodeFiles + project.totalDocFiles} files</p>
              </div>
            </button>
          ))}
        </div>

        {/* Stats Row - Clickable */}
        <div className="flex gap-4 mb-6">
          <button 
            onClick={() => setDetailView('codeFiles')}
            className={`flex-1 rounded-xl p-4 shadow-sm border-2 transition-all hover:shadow-md cursor-pointer ${
              detailView === 'codeFiles' 
                ? 'border-slate-500 ring-2 ring-slate-200' 
                : darkMode ? 'border-slate-700 hover:border-slate-600 bg-slate-800' : 'border-slate-200 hover:border-slate-300 bg-white'
            } ${detailView === 'codeFiles' ? darkMode ? 'bg-slate-700' : 'bg-slate-50' : ''}`}
          >
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center">
                <span className="text-2xl">💻</span>
              </div>
              <div className="flex-1 text-left">
                <p className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{currentProject.totalCodeFiles}</p>
                <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('codeFiles')}</p>
              </div>
              <span className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>Click for details →</span>
            </div>
          </button>
          <button 
            onClick={() => setDetailView('documentation')}
            className={`flex-1 rounded-xl p-4 shadow-sm border-2 transition-all hover:shadow-md cursor-pointer ${
              detailView === 'documentation' 
                ? 'border-indigo-500 ring-2 ring-indigo-200' 
                : darkMode ? 'border-slate-700 hover:border-indigo-400 bg-slate-800' : 'border-slate-200 hover:border-indigo-300 bg-white'
            } ${detailView === 'documentation' ? darkMode ? 'bg-slate-700' : 'bg-indigo-50' : ''}`}
          >
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center">
                <span className="text-2xl">📚</span>
              </div>
              <div className="flex-1 text-left">
                <p className="text-2xl font-bold text-indigo-600">{currentProject.totalDocFiles}</p>
                <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('documentation')}</p>
              </div>
              <span className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>Click for details →</span>
            </div>
          </button>
          <button 
            onClick={() => setDetailView('contributors')}
            className={`flex-1 rounded-xl p-4 shadow-sm border-2 transition-all hover:shadow-md cursor-pointer ${
              detailView === 'contributors' 
                ? 'border-emerald-500 ring-2 ring-emerald-200' 
                : darkMode ? 'border-slate-700 hover:border-emerald-400 bg-slate-800' : 'border-slate-200 hover:border-emerald-300 bg-white'
            } ${detailView === 'contributors' ? darkMode ? 'bg-slate-700' : 'bg-emerald-50' : ''}`}
          >
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
                <span className="text-2xl">👥</span>
              </div>
              <div className="flex-1 text-left">
                <p className="text-2xl font-bold text-emerald-600">{currentProject.developerStats.length}</p>
                <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('contributors')}</p>
              </div>
              <span className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>Click for details →</span>
            </div>
          </button>
          <div className={`flex-1 rounded-xl p-4 shadow-sm border ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center">
                <span className="text-2xl">📅</span>
              </div>
              <div className="flex-1">
                <p className="text-2xl font-bold text-amber-600">{currentProject.lastUpdate}</p>
                <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('lastUpdate')}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Developer Upload Statistics */}
        <div className={`rounded-xl shadow-sm border mb-6 ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
          <div className={`p-4 border-b ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
            <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('developerUploadStats')}</h3>
            <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('filesUploadedBy')} {currentProject.projectName}</p>
          </div>
          <div className="p-4">
            <table className="w-full">
              <thead>
                <tr className={`text-xs uppercase tracking-wider ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                  <th className="text-left py-2 px-3 font-medium">{t('developer')}</th>
                  <th className="text-center py-2 px-3 font-medium">{t('codeFiles')}</th>
                  <th className="text-center py-2 px-3 font-medium">{t('documentation')}</th>
                  <th className="text-center py-2 px-3 font-medium">{t('totalFiles')}</th>
                  <th className="text-center py-2 px-3 font-medium">{t('totalSize')}</th>
                  <th className="text-center py-2 px-3 font-medium">{t('lastUpload')}</th>
                  <th className="text-center py-2 px-3 font-medium">{t('contribution')}</th>
                </tr>
              </thead>
              <tbody className={`divide-y ${darkMode ? 'divide-slate-700' : 'divide-slate-100'}`}>
                {currentProject.developerStats.map(dev => {
                  const totalFiles = dev.codeFiles + dev.docFiles;
                  const projectTotal = currentProject.totalCodeFiles + currentProject.totalDocFiles;
                  const contribution = Math.round((totalFiles / projectTotal) * 100);
                  
                  return (
                    <tr key={dev.id} className={`transition-colors ${darkMode ? 'hover:bg-slate-700' : 'hover:bg-slate-50'}`}>
                      <td className="py-3 px-3">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full flex items-center justify-center text-white font-medium">
                            {dev.avatar}
                          </div>
                          <div>
                            <p className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-slate-800'}`}>{dev.name}</p>
                          </div>
                        </div>
                      </td>
                      <td className="text-center py-3 px-3">
                        <div className="flex items-center justify-center gap-2">
                          <span className="text-lg">💻</span>
                          <span className={`text-sm font-semibold ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>{dev.codeFiles}</span>
                        </div>
                      </td>
                      <td className="text-center py-3 px-3">
                        <div className="flex items-center justify-center gap-2">
                          <span className="text-lg">📚</span>
                          <span className="text-sm font-semibold text-indigo-600">{dev.docFiles}</span>
                        </div>
                      </td>
                      <td className="text-center py-3 px-3">
                        <span className={`inline-flex items-center justify-center w-10 h-10 rounded-full text-sm font-bold ${darkMode ? 'bg-slate-700 text-slate-300' : 'bg-slate-100 text-slate-700'}`}>
                          {totalFiles}
                        </span>
                      </td>
                      <td className="text-center py-3 px-3">
                        <span className={`text-sm ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>{dev.totalSize}</span>
                      </td>
                      <td className="text-center py-3 px-3">
                        <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{dev.lastUpload}</span>
                      </td>
                      <td className="text-center py-3 px-3">
                        <div className="flex items-center gap-2">
                          <div className={`flex-1 h-2 rounded-full overflow-hidden ${darkMode ? 'bg-slate-700' : 'bg-slate-100'}`}>
                            <div 
                              className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full"
                              style={{ width: `${contribution}%` }}
                            ></div>
                          </div>
                          <span className={`text-xs font-semibold w-10 ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>{contribution}%</span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent Files */}
        <div className={`rounded-xl shadow-sm border ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
          <div className={`p-4 border-b ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('recentFiles')}</h3>
                <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('latestUploads')} {currentProject.projectName}</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setViewMode('all')}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                    viewMode === 'all' 
                      ? 'bg-slate-800 text-white' 
                      : darkMode ? 'bg-slate-700 text-slate-300 hover:bg-slate-600' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {t('all')}
                </button>
                <button
                  onClick={() => setViewMode('code')}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all flex items-center gap-1 ${
                    viewMode === 'code' 
                      ? 'bg-slate-800 text-white' 
                      : darkMode ? 'bg-slate-700 text-slate-300 hover:bg-slate-600' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  <span>💻</span> {t('code')}
                </button>
                <button
                  onClick={() => setViewMode('docs')}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all flex items-center gap-1 ${
                    viewMode === 'docs' 
                      ? 'bg-indigo-600 text-white' 
                      : 'bg-indigo-100 text-indigo-600 hover:bg-indigo-200'
                  }`}
                >
                  <span>📚</span> {t('docs')}
                </button>
              </div>
            </div>
          </div>
          <div className={`divide-y ${darkMode ? 'divide-slate-700' : 'divide-slate-100'}`}>
            {filteredFiles.map((file, idx) => (
              <div key={idx} className={`flex items-center gap-4 p-4 transition-colors ${darkMode ? 'hover:bg-slate-700' : 'hover:bg-slate-50'}`}>
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  file.type === 'code' ? darkMode ? 'bg-slate-700' : 'bg-slate-100' : 'bg-indigo-100'
                }`}>
                  <span className="text-lg">{file.type === 'code' ? '💻' : '📚'}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-medium truncate ${darkMode ? 'text-white' : 'text-slate-800'}`}>{file.name}</p>
                  <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-400'}`}>by {file.author} · {file.date}</p>
                </div>
                <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{file.size}</span>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  file.status === 'approved' 
                    ? 'bg-emerald-100 text-emerald-700' 
                    : 'bg-amber-100 text-amber-700'
                }`}>
                  {file.status === 'approved' ? `✓ ${t('approved')}` : `⏳ ${t('pendingReview')}`}
                </span>
                <div className="flex items-center gap-1">
                  <button className={`p-2 rounded-lg transition-colors ${darkMode ? 'text-slate-400 hover:text-blue-400 hover:bg-slate-700' : 'text-slate-400 hover:text-blue-600 hover:bg-blue-50'}`}>
                    👁️
                  </button>
                  <button className={`p-2 rounded-lg transition-colors ${darkMode ? 'text-slate-400 hover:text-emerald-400 hover:bg-slate-700' : 'text-slate-400 hover:text-emerald-600 hover:bg-emerald-50'}`}>
                    ⬇️
                  </button>
                  {file.status === 'pending' && (
                    <button className={`p-2 rounded-lg transition-colors ${darkMode ? 'text-slate-400 hover:text-emerald-400 hover:bg-slate-700' : 'text-slate-400 hover:text-emerald-600 hover:bg-emerald-50'}`}>
                      ✓
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Detail Panel */}
        {renderDetailPanel()}
      </div>
    );
  };
  // Admin View with Tabs
  const AdminView = () => (
    <div className="flex flex-1 overflow-hidden">
      <AppSidebar />
      <div className="flex-1 flex flex-col">
        <div className={`${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'} border-b px-6 py-3 flex gap-4`}>
          <button 
            onClick={() => setActiveAdminTab('builder')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeAdminTab === 'builder' ? 'bg-blue-100 text-blue-700' : darkMode ? 'text-slate-400 hover:text-white' : 'text-slate-500 hover:text-slate-700'}`}
          >
            🏗️ {t('projectCanvas')}
          </button>
          <button 
            onClick={() => setActiveAdminTab('analytics')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeAdminTab === 'analytics' ? 'bg-blue-100 text-blue-700' : darkMode ? 'text-slate-400 hover:text-white' : 'text-slate-500 hover:text-slate-700'}`}
          >
            📊 {t('analytics')}
          </button>
          <button 
            onClick={() => setActiveAdminTab('codedocs')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeAdminTab === 'codedocs' ? 'bg-blue-100 text-blue-700' : darkMode ? 'text-slate-400 hover:text-white' : 'text-slate-500 hover:text-slate-700'}`}
          >
            📁 {t('codeDocs')}
          </button>
          <button 
            onClick={() => setActiveAdminTab('team')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeAdminTab === 'team' ? 'bg-blue-100 text-blue-700' : darkMode ? 'text-slate-400 hover:text-white' : 'text-slate-500 hover:text-slate-700'}`}
          >
            👥 {t('teamManagement')}
          </button>
        </div>
        {activeAdminTab === 'builder' && <ProjectCanvas />}
        {activeAdminTab === 'analytics' && <AnalyticsDashboard />}
        {activeAdminTab === 'codedocs' && <AdminCodeDocsTab />}
        {activeAdminTab === 'team' && <TeamManagement />}
      </div>
      {selectedTicket && activeAdminTab === 'builder' && (
        <TicketPanel 
          ticket={selectedTicket} 
          onClose={() => setSelectedTicket(null)}
          onQuestion={() => setShowQuestionModal(true)}
          onRedirect={() => setShowRedirectModal(true)}
        />
      )}
    </div>
  );

  // Settings Modal
  const SettingsModal = () => (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowSettingsModal(false)}>
      <div className={`${darkMode ? 'bg-slate-800' : 'bg-white'} rounded-2xl w-full max-w-2xl shadow-2xl max-h-[90vh] overflow-hidden`} onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className={`p-6 border-b ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-12 h-12 ${darkMode ? 'bg-slate-700' : 'bg-slate-100'} rounded-xl flex items-center justify-center`}>
                <span className="text-2xl">⚙️</span>
              </div>
              <div>
                <h2 className={`text-xl font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('settings')}</h2>
                <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('customizeExperience')}</p>
              </div>
            </div>
            <button 
              onClick={() => setShowSettingsModal(false)}
              className={`p-2 ${darkMode ? 'hover:bg-slate-700' : 'hover:bg-slate-100'} rounded-lg transition-colors`}
            >
              ✕
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-auto max-h-[60vh]">
          {/* Appearance Section */}
          <div className="mb-8">
            <h3 className={`text-sm font-semibold uppercase tracking-wider mb-4 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('appearance')}</h3>
            
            {/* Theme Toggle */}
            <div className={`flex items-center justify-between p-4 rounded-xl mb-3 ${darkMode ? 'bg-slate-700' : 'bg-slate-50'}`}>
              <div className="flex items-center gap-3">
                <span className="text-2xl">{darkMode ? '🌙' : '☀️'}</span>
                <div>
                  <p className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('theme')}</p>
                  <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('chooseLightDark')}</p>
                </div>
              </div>
              <div className="flex gap-2">
                <button 
                  onClick={() => setDarkMode(false)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    !darkMode 
                      ? 'bg-blue-600 text-white' 
                      : darkMode ? 'bg-slate-600 text-slate-300' : 'bg-slate-200 text-slate-600'
                  }`}
                >
                  ☀️ {t('light')}
                </button>
                <button 
                  onClick={() => setDarkMode(true)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    darkMode 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-slate-200 text-slate-600'
                  }`}
                >
                  🌙 {t('dark')}
                </button>
              </div>
            </div>

            {/* Language */}
            <div className={`flex items-center justify-between p-4 rounded-xl ${darkMode ? 'bg-slate-700' : 'bg-slate-50'}`}>
              <div className="flex items-center gap-3">
                <span className="text-2xl">🌐</span>
                <div>
                  <p className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-slate-800'}`}>Language</p>
                  <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('selectLanguage')}</p>
                </div>
              </div>
              <select 
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${
                  darkMode 
                    ? 'bg-slate-600 text-white border-slate-500' 
                    : 'bg-white border-slate-200'
                } border focus:ring-2 focus:ring-blue-500`}
              >
                {languages.map(lang => (
                  <option key={lang.code} value={lang.code}>{lang.flag} {lang.name}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Notifications Section */}
          <div className="mb-8">
            <h3 className={`text-sm font-semibold uppercase tracking-wider mb-4 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('notifications')}</h3>
            
            {[
              { icon: '📧', title: t('emailNotifications'), desc: t('receiveEmailUpdates'), enabled: true },
              { icon: '🔔', title: t('pushNotifications'), desc: t('getNotifiedBrowser'), enabled: true },
              { icon: '📱', title: t('mobileNotifications'), desc: t('receiveAlerts'), enabled: false },
              { icon: '⏰', title: t('dueDateReminders'), desc: t('getRemindedDeadlines'), enabled: true },
            ].map((item, i) => (
              <div key={i} className={`flex items-center justify-between p-4 rounded-xl mb-3 ${darkMode ? 'bg-slate-700' : 'bg-slate-50'}`}>
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{item.icon}</span>
                  <div>
                    <p className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-slate-800'}`}>{item.title}</p>
                    <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{item.desc}</p>
                  </div>
                </div>
                <button className={`relative w-12 h-6 rounded-full transition-colors ${item.enabled ? 'bg-blue-600' : darkMode ? 'bg-slate-600' : 'bg-slate-300'}`}>
                  <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all shadow ${item.enabled ? 'right-1' : 'left-1'}`}></div>
                </button>
              </div>
            ))}
          </div>

          {/* Account Section */}
          <div className="mb-8">
            <h3 className={`text-sm font-semibold uppercase tracking-wider mb-4 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('account')}</h3>
            
            <div className={`p-4 rounded-xl mb-3 ${darkMode ? 'bg-slate-700' : 'bg-slate-50'}`}>
              <div className="flex items-center gap-4 mb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-full flex items-center justify-center text-2xl text-white font-bold">AG</div>
                <div>
                  <p className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>Ana García</p>
                  <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>ana.garcia@company.com</p>
                  <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>Frontend Developer</p>
                </div>
                <button className={`ml-auto px-4 py-2 ${darkMode ? 'bg-slate-600 hover:bg-slate-500' : 'bg-slate-200 hover:bg-slate-300'} rounded-lg text-sm font-medium transition-colors ${darkMode ? 'text-white' : 'text-slate-700'}`}>
                  {t('editProfile')}
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button className={`p-4 rounded-xl text-left ${darkMode ? 'bg-slate-700 hover:bg-slate-600' : 'bg-slate-50 hover:bg-slate-100'} transition-colors`}>
                <span className="text-2xl mb-2 block">🔐</span>
                <p className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('changePassword')}</p>
                <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('updateCredentials')}</p>
              </button>
              <button className={`p-4 rounded-xl text-left ${darkMode ? 'bg-slate-700 hover:bg-slate-600' : 'bg-slate-50 hover:bg-slate-100'} transition-colors`}>
                <span className="text-2xl mb-2 block">🔗</span>
                <p className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('connectedApps')}</p>
                <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('manageIntegrations')}</p>
              </button>
              <button className={`p-4 rounded-xl text-left ${darkMode ? 'bg-slate-700 hover:bg-slate-600' : 'bg-slate-50 hover:bg-slate-100'} transition-colors`}>
                <span className="text-2xl mb-2 block">📊</span>
                <p className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('exportData')}</p>
                <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('downloadYourData')}</p>
              </button>
              <button className={`p-4 rounded-xl text-left ${darkMode ? 'bg-slate-700 hover:bg-slate-600' : 'bg-slate-50 hover:bg-slate-100'} transition-colors`}>
                <span className="text-2xl mb-2 block">❓</span>
                <p className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-slate-800'}`}>{t('helpSupport')}</p>
                <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{t('getAssistance')}</p>
              </button>
            </div>
          </div>

          {/* Danger Zone */}
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider mb-4 text-red-500">{t('dangerZone')}</h3>
            <div className={`p-4 rounded-xl border-2 border-dashed border-red-300 ${darkMode ? 'bg-red-900/20' : 'bg-red-50'}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${darkMode ? 'text-red-400' : 'text-red-700'}`}>{t('deleteAccount')}</p>
                  <p className={`text-xs ${darkMode ? 'text-red-400/70' : 'text-red-600'}`}>{t('permanentlyDelete')}</p>
                </div>
                <button className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors">
                  {t('delete')}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className={`p-6 border-t ${darkMode ? 'border-slate-700' : 'border-slate-200'} flex justify-between items-center`}>
          <p className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>CoreStream v2.4.1 · © 2024</p>
          <div className="flex gap-3">
            <button 
              onClick={() => setShowSettingsModal(false)}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${darkMode ? 'bg-slate-700 text-white hover:bg-slate-600' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'} transition-colors`}
            >
              {t('cancel')}
            </button>
            <button 
              onClick={() => { setShowSettingsModal(false); alert('Settings saved!'); }}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
            >
              {t('saveChanges')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className={`h-screen flex flex-col font-sans ${darkMode ? 'bg-slate-900' : 'bg-slate-50'}`}>
      <Header />
      {activeView === 'admin' ? (
        <AdminView />
      ) : (
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Developer Tab Navigation */}
          <div className={`${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'} border-b px-6 py-3 flex gap-4`}>
            <button 
              onClick={() => setActiveDeveloperTab('workbench')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeDeveloperTab === 'workbench' ? 'bg-blue-100 text-blue-700' : darkMode ? 'text-slate-400 hover:text-white' : 'text-slate-500 hover:text-slate-700'}`}
            >
              🎯 {t('myWorkbench')}
            </button>
            <button 
              onClick={() => setActiveDeveloperTab('uploads')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeDeveloperTab === 'uploads' ? 'bg-blue-100 text-blue-700' : darkMode ? 'text-slate-400 hover:text-white' : 'text-slate-500 hover:text-slate-700'}`}
            >
              📤 {t('codeAndDocs')}
            </button>
            {/* Team Assignment Tab - Only visible for Team Leads */}
            {currentUser?.isTeamLead && (
              <button 
                onClick={() => setActiveDeveloperTab('teamAssignment')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
                  activeDeveloperTab === 'teamAssignment' 
                    ? 'bg-amber-100 text-amber-700' 
                    : darkMode ? 'text-slate-400 hover:text-white' : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                <span>👑</span>
                <span>{t('teamAssignment')}</span>
                <span className={`px-1.5 py-0.5 text-xs rounded ${
                  activeDeveloperTab === 'teamAssignment' 
                    ? 'bg-amber-200 text-amber-800' 
                    : darkMode ? 'bg-slate-700 text-slate-400' : 'bg-slate-200 text-slate-500'
                }`}>
                  Lead
                </span>
              </button>
            )}
          </div>
          {activeDeveloperTab === 'workbench' ? (
            <EmployeeWorkbench />
          ) : activeDeveloperTab === 'uploads' ? (
            <UploadsTab />
          ) : activeDeveloperTab === 'teamAssignment' && currentUser?.isTeamLead ? (
            <TeamAssignmentTab />
          ) : (
            <EmployeeWorkbench />
          )}
        </div>
      )}
      {showQuestionModal && <QuestionModal />}
      {showRedirectModal && <RedirectModal />}
      {showNewDeveloperModal && <NewDeveloperModal />}
      {showSettingsModal && <SettingsModal />}
      {showEpicDocsModal !== null && <EpicDocsModal />}
      {showLanguageDropdown && <div className="fixed inset-0 z-40" onClick={() => setShowLanguageDropdown(false)}></div>}
    </div>
  );
};



export default CoreStream;
