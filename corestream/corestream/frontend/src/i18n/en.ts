/**
 * English translations for CoreStream
 * All UI strings organized by functional sections
 * Uses dot notation for nested key access (e.g., common.save)
 */

export default {
  // ==========================================
  // SECTION: Common actions and terms
  // Reusable keywords throughout the interface
  // ==========================================
  common: {
    save: 'Save',
    cancel: 'Cancel',
    delete: 'Delete',
    edit: 'Edit',
    confirm: 'Confirm',
    close: 'Close',
    search: 'Search',
    filter: 'Filter',
    loading: 'Loading...',
    error: 'Error',
    success: 'Success',
    back: 'Back',
    next: 'Next',
    noData: 'No data',
    actions: 'Actions',
    yes: 'Yes',
    no: 'No',
    required: 'Required',
    optional: 'Optional',
  },

  // ==========================================
  // SECTION: Header and top navigation
  // Header/navbar elements of the application
  // ==========================================
  header: {
    administrator: 'Administrator',
    developer: 'Developer',
    settings: 'Settings',
    notifications: 'Notifications',
    logout: 'Sign out',
    profile: 'Profile',
    darkMode: 'Dark mode',
    language: 'Language',
  },

  // ==========================================
  // SECTION: Sidebar
  // Main side navigation menu
  // ==========================================
  sidebar: {
    applications: 'Applications',
    sortByName: 'Sort by name',
    sortByPending: 'Sort by pending',
    sortByDelayed: 'Sort by delayed',
    newApp: 'New application',
    noApps: 'No applications',
  },

  // ==========================================
  // SECTION: Builder/Canvas
  // Visual builder panel for epics and tickets
  // ==========================================
  builder: {
    projectCanvas: 'Project canvas',
    newEpic: 'New epic',
    addTicket: 'Add ticket',
    epicPlaceholder: 'Epic name',
    ticketPlaceholder: 'Ticket description',
    dragEpicsHint: 'Drag epics to reorganize',
    showTickets: 'Show tickets',
    hideTickets: 'Hide tickets',
    unassigned: 'Unassigned',
    attachDocs: 'Attach documents',
    epicDocs: 'Epic documents',
    uploadSpec: 'Upload specification',
    noDocsAttached: 'No documents attached',
  },

  // ==========================================
  // SECTION: Workbench
  // Task management and tracking panel
  // ==========================================
  workbench: {
    myWorkbench: 'My workbench',
    allTickets: 'All tickets',
    inProgress: 'In progress',
    todo: 'To do',
    done: 'Done',
    overdue: 'Overdue',
    today: 'Today',
    thisWeek: 'This week',
    later: 'Later',
    noTickets: 'No tickets',
    startWorking: 'Start working',
    selectTicket: 'Select ticket',
    timer: 'Timer',
    timeSpent: 'Time spent',
    blockedTime: 'Blocked time',
    subtasks: 'Subtasks',
    subtasksProgress: 'Subtasks progress',
    activityLog: 'Activity log',
  },

  // ==========================================
  // SECTION: Ticket actions
  // Available operations for tickets
  // ==========================================
  actions: {
    complete: 'Complete',
    completeTicket: 'Complete ticket',
    raiseQuestion: 'Raise question',
    redirect: 'Redirect',
    prLink: 'PR link',
    prLinkPlaceholder: 'https://github.com/repo/pull/123',
    prRequired: 'PR link is required',
    invalidPr: 'Invalid PR link',
    questionPlaceholder: 'Describe your question here',
    questionMinLength: 'Question must be at least 10 characters',
    redirectTo: 'Redirect to',
    redirectReason: 'Redirection reason',
    reasonPlaceholder: 'Explain why this ticket is being redirected',
    reasonMinLength: 'Reason must be at least 10 characters',
    confirmComplete: 'Confirm completion',
    confirmRedirect: 'Confirm redirection',
  },

  // ==========================================
  // SECTION: Analytics and reports
  // Team metrics, charts and statistics
  // ==========================================
  analytics: {
    analytics: 'Analytics',
    commandCenter: 'Command center',
    performanceMetrics: 'Performance metrics',
    totalTickets: 'Total tickets',
    completed: 'Completed',
    blocked: 'Blocked',
    avgTime: 'Average time',
    weekChange: 'Week change',
    efficiency: 'Efficiency',
    blockingIndex: 'Blocking index',
    churnIndex: 'Churn index',
    heatmap: 'Heat map',
    burndown: 'Burndown chart',
    exportPdf: 'Export PDF',
    exportCsv: 'Export CSV',
    ideal: 'Ideal',
    actual: 'Actual',
    period: 'Period',
    lastWeek: 'Last week',
    lastMonth: 'Last month',
    lastQuarter: 'Last quarter',
    teamPerformance: 'Team performance',
    sortBy: 'Sort by',
    ticketsProcessed: 'Tickets processed',
    questions: 'Questions',
    redirects: 'Redirects',
    drillDown: 'Drill down',
    insight: 'Insight',
    noData: 'No data available',
  },

  // ==========================================
  // SECTION: Team management
  // Member administration and assignments
  // ==========================================
  team: {
    teamManagement: 'Team management',
    teamAssignment: 'Team assignment',
    addDeveloper: 'Add developer',
    editMember: 'Edit member',
    deleteMember: 'Delete member',
    promoteLeader: 'Promote to leader',
    demoteLeader: 'Demote from leader',
    members: 'Members',
    name: 'Name',
    email: 'Email',
    role: 'Role',
    specialty: 'Specialty',
    stats: 'Statistics',
    ticketsCompleted: 'Tickets completed',
    ticketsPending: 'Tickets pending',
    ticketsBlocked: 'Tickets blocked',
    avgTime: 'Average time',
    unassignedTickets: 'Unassigned tickets',
    assignedTickets: 'Assigned tickets',
    workload: 'Workload',
    lowLoad: 'Low load',
    mediumLoad: 'Medium load',
    highLoad: 'High load',
    assignTicket: 'Assign ticket',
    unassignTicket: 'Unassign ticket',
    confirmDelete: 'Confirm deletion',
    noMembers: 'No team members',
  },

  // ==========================================
  // SECTION: Code and documentation
  // File management, repository and docs
  // ==========================================
  codeDocs: {
    codeAndDocs: 'Code and documentation',
    repository: 'Repository',
    totalFiles: 'Total files',
    codeFiles: 'Code files',
    docFiles: 'Documentation files',
    contributors: 'Contributors',
    upload: 'Upload',
    translate: 'Translate',
    translateTo: 'Translate to',
    download: 'Download',
    noFiles: 'No files',
  },

  // ==========================================
  // SECTION: Notifications
  // System messages and alerts
  // ==========================================
  notifications: {
    title: 'Notifications',
    markAllRead: 'Mark all as read',
    noNotifications: 'No notifications',
    assignedToYou: 'A ticket was assigned to you',
    questionRaised: 'A question was raised',
    ticketRedirected: 'The ticket was redirected',
    ticketCompleted: 'The ticket was completed',
    systemMessage: 'System message',
  },

  // ==========================================
  // SECTION: Settings
  // User and application preferences
  // ==========================================
  settings: {
    settingsTitle: 'Settings',
    language: 'Language',
    theme: 'Theme',
    lightMode: 'Light mode',
    darkMode: 'Dark mode',
    profile: 'Profile',
    saveChanges: 'Save changes',
  },

  // ==========================================
  // SECTION: Ticket statuses
  // Progress states and priorities
  // ==========================================
  statuses: {
    todo: 'To do',
    inProgress: 'In progress',
    blocked: 'Blocked',
    redirected: 'Redirected',
    done: 'Done',
    low: 'Low',
    medium: 'Medium',
    high: 'High',
    urgent: 'Urgent',
  },

  // ==========================================
  // SECTION: User roles
  // Types of permissions and access
  // ==========================================
  roles: {
    admin: 'Administrator',
    groupLeader: 'Group leader',
    developer: 'Developer',
  },

  // ==========================================
  // SECTION: Error messages
  // Text for different types of errors
  // ==========================================
  errors: {
    generic: 'An error has occurred',
    unauthorized: 'Unauthorized',
    notFound: 'Not found',
    forbidden: 'Access denied',
    serverError: 'Server error',
    networkError: 'Network error',
    validationError: 'Validation error',
    loginFailed: 'Login failed',
    emailTaken: 'Email is already registered',
  },

  // ==========================================
  // SECTION: Confirmation dialogs
  // Confirmation messages for critical actions
  // ==========================================
  confirm: {
    deleteTicket: 'Delete this ticket?',
    deleteEpic: 'Delete this epic?',
    deleteApp: 'Delete this application?',
    deleteMember: 'Delete this team member?',
    redirectTicket: 'Redirect this ticket?',
    completeTicket: 'Mark as completed?',
    logout: 'Sign out?',
  },
}
