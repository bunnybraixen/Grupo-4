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
    applicationName: 'Application name',
    description: 'Description',
    descriptionPlaceholder: 'Brief application description',
    distinctiveColor: 'Distinctive color',
    create: 'Create',
    applicationExample: 'E.g., Authentication System',
    sortNameLabel: 'Name',
    sortPendingLabel: 'Pending',
    sortDelayedLabel: 'Delayed',
    retry: 'Retry',
    creating: 'Creating...',
    loadError: 'Error loading applications',
    sortByLabel: 'Sort by',
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
    performanceTable: 'Performance Table',
    totalTickets: 'Total tickets',
    completed: 'Completed',
    blocked: 'Blocked',
    avgTime: 'Average time',
    weekChange: 'Week change',
    efficiency: 'Efficiency',
    blockingIndex: 'Blocking index',
    churnIndex: 'Churn index',
    heatmap: 'Heat map',
    heatmapDescription: 'Visualization of completed tickets by day of the week.',
    total: 'Total',
    daily: 'Daily',
    colorScale: 'Activity Scale',
    low: 'None/Low',
    medium: 'Medium',
    high: 'High',
    veryHigh: 'Very High',
    ticketsClosedShort: 'tickets',
    noDataPattern: 'Not enough data to detect patterns.',
    lowActivityPattern: 'The day with the historically lowest activity is ',
    emptyChartTitle: 'Select an epic',
    emptyChartDesc: 'Choose an epic from the menu above to visualize its ideal vs actual progress.',
    burndown: 'Burndown chart',
    burndownTitle: 'Burndown Chart',
    burndownDesc: 'Actual vs ideal epic progress',
    selectEpic: 'Select an epic...',
    untitledEpic: 'Untitled Epic',
    avgVelocity: 'Avg. Velocity',
    ticketsPerDay: 'tickets per day',
    estimatedTime: 'Estimated Time',
    daysRemaining: 'days remaining',
    status: 'Status',
    idealLine: 'Ideal Line',
    actualLine: 'Actual Line',
    onTime: 'On Time',
    delayed: 'Delayed',
    selectEpicProgress: 'Select an epic to view progress',
    ticketsAhead: 'tickets ahead',
    ticketsBehind: 'tickets behind',
    pendingTickets: 'Pending Tickets',
    date: 'Date',
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
  // SECTION: Period selector
  // Used in analytics components
  // ==========================================
  period: {
    thisWeek: 'This week',
    thisMonth: 'This month',
    thisQuarter: 'This quarter',
    custom: 'Custom',
  },

  // ==========================================
  // SECTION: Generic table headers
  // ==========================================
  table: {
    developer: 'Developer',
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
    translating: 'Translating...',
    translationResult: 'Translation result',
    selectTargetLanguage: 'Select target language',
    copyToClipboard: 'Copy',
    copied: 'Copied!',
    unsupportedFileType: 'File type not supported for translation',
    download: 'Download',
    translateDownloadHint: 'Translates and downloads with preserved formatting',
    downloading: 'Downloading...',
    serviceStarting: 'Translation service starting',
    serviceStartingDesc: 'The translation service is currently unavailable. Please wait a moment and try again.',
    retrying: 'Retrying...',
    retry: 'Retry',
    finalizing: 'Finalizing...',
    generatingFile: 'Generating translated file...',
    almostDone: 'Almost done...',
    minutesRemaining: 'min remaining',
    secondsRemaining: 's remaining',
    noFiles: 'No files',
    repositoryTitle: 'Code & Documentation Repository',
    repositorySubtitle: 'View all project files and upload statistics',
    loadingDocs: 'Loading documents...',
    noDocsYet: 'No documents uploaded yet.',
    noDocsDesc: 'Files uploaded to tickets and epics will appear here.',
    details: 'Details →',
    documentation: 'Documentation',
    epicsTickets: 'Epics / Tickets',
    byEpicTicket: 'By Epic / Ticket',
    recentFiles: 'Recent Files',
    filesTotal: '{n} files total',
    fileSingularTotal: '{n} file total',
    fileSingular: '{n} file',
    filesPlural: '{n} files',
    noCodeFiles: 'No code files uploaded yet.',
    noDocFiles: 'No documentation uploaded yet.',
    docTypeCode: 'CODE',
    docTypeDocumentation: 'DOCUMENTATION',
    codeLabel: 'CODE',
    docsLabel: 'DOCS',
    uploadedLabel: 'UPLOADED',
    epicPrefix: 'Epic',
    ticketPrefix: 'Ticket',
    noContext: 'No context',
    userPrefix: 'User',
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
    justNow: 'just now',
    minutesAgo: '{n}m ago',
    hoursAgo: '{n}h ago',
    daysAgo: '{n}d ago',
    unreadLabel: '{count} unread notifications',
    markAllRead2: 'Mark all as read',
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
    notifSectionTitle: 'Notifications',
    notifEmail: 'Email',
    notifEmailDesc: 'Ticket updates',
    notifPush: 'Browser notifications',
    notifPushDesc: 'Real-time alerts',
    notifMobile: 'Mobile',
    notifMobileDesc: 'Alerts on your phone',
    notifReminders: 'Reminders',
    notifRemindersDesc: 'Upcoming ticket deadlines',
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

  // ==========================================
  // SECTION: Workbench View
  // Developer personal panel
  // ==========================================
  workbenchView: {
    myTickets: 'My Tickets',
    byEpic: 'By Epic',
    applications: 'Applications',
    applicationSingular: 'application',
    applicationPlural: 'applications',
    selectApplication: 'Select an application',
    selectApplicationDesc: 'Choose an application from the left panel to start managing epics and tasks',
    archivedApplications: 'Archived applications',
    epics: 'epics',
    pending: 'pending',
    delayed: 'delayed',
    sortDefault: 'Sort: Default',
    sortPending: 'Sort: Most Pending',
    sortDelayed: 'Sort: Most Delayed',
    active: 'Active',
  },

  // ==========================================
  // SECTION: Builder View
  // Visual application builder
  // ==========================================
  builderView: {
    title: 'Application Builder',
    description: 'Manage applications, epics, and progress with collapsible swimlanes, quick editing, and clear navigation.',
    expandEpics: 'Expand epics',
    collapseEpics: 'Collapse epics',
    newApplication: 'New application',
    newEpic: 'New epic',
    applicationsCount: 'Applications',
    registered: 'registered',
    activeStatus: 'Active',
    noSelection: 'No selection',
    noDescription: 'No description',
    epicCount: 'epics',
    pendingCount: 'pending',
    delayedCount: 'overdue',
    noApplications: 'No applications yet.',
    applicationLabel: 'Application',
    epicsLabel: 'Epics',
    swimmlanesConfigured: 'Swimlanes configured for this application.',
    progressLabel: 'Progress',
    progressDesc: 'Average progress across associated tickets.',
    tonalityLabel: 'Tone',
    colorGuide: 'Guide color',
    swimmlanesTitle: 'Epic swimlanes',
    swimmlanesDesc: 'Each swimlane can be collapsed, edited, deleted, or reordered.',
    collapseAll: 'Collapse all',
    expandAll: 'Expand all',
    noEpics: 'No epics for this application. Create the first one using the button above.',
    tickets: 'tickets',
    completed: 'completed',
    epicNoDescription: 'Epic with no description',
    edit: 'Edit',
    delete: 'Delete',
    dueDate: 'Due:',
    collapsed: 'Collapsed',
    opened: 'Opened',
    ticketsLabel: 'Tickets',
    items: 'items',
    progress: 'Progress',
    addTicket: 'Add Ticket',
    quickActions: 'Quick Actions',
    visualOrder: 'Visual Order',
    selectApplicationMessage: 'Select an application',
    panelDescription: 'The central panel will show the epic canvas, its collapsible swimlanes and CRUD actions. Use the sidebar to open an application or create a new one to get started.',
    createApplication: 'Create application',
    selectApplicationFirst: 'Select an application first',
    close: 'Close',
    formName: 'Name',
    formDescription: 'Description',
    editApplication: 'Edit application',
    newApplicationTitle: 'New application',
    appDescPlaceholder: 'Describe the scope of this application',
    colorLabel: 'Color',
    currentColor: 'Current color',
    advanced: 'Advanced',
    icon: 'Icon',
    saving: 'Saving...',
    saveApplication: 'Save application',
    editEpic: 'Edit epic',
    newEpicTitle: 'New epic',
    appNamePlaceholder: 'Application name',
    epicTitlePlaceholder: 'Epic title',
    epicTitleLabel: 'Title',
    epicDescPlaceholder: 'Explain the goal of this epic',
    dueDateLabel: 'Due date',
    targetApplication: 'Target application',
    saveEpic: 'Save epic',
    ticketTitlePlaceholder: 'Ticket title...',
  },

  // ==========================================
  // SECTION: Analytics View
  // Team metrics and analysis
  // ==========================================
  analyticsView: {
    title: 'Global Analytics',
    subtitle: 'Project metrics and team performance',
    applicationLabel: 'Application',
    periodLabel: 'Period',
    loadingApps: 'Loading apps...',
    thisWeek: 'This Week',
    thisMonth: 'This Month',
    thisQuarter: 'This Quarter',
    thisYear: 'This Year',
    refresh: '🔄 Refresh',
    teamEfficiency: 'Team Efficiency',
    completedOnTime: 'Tickets completed on time',
    blockingIndex: 'Blocking Index',
    blockedTickets: 'Blocked tickets',
    redirectionIndex: 'Redirection Index',
    redirectedTickets: 'Redirected tickets',
    teamPerformanceTitle: 'Team Performance',
    colMember: 'Member',
    colCompleted: 'Completed',
    colInProgress: 'In Progress',
    colBlocked: 'Blocked',
    colEfficiency: 'Efficiency',
    colVelocity: 'Velocity',
    noPerformanceData: 'No performance data available',
    weeklyActivity: 'Weekly Activity',
    noTicketsThisWeek: 'No tickets completed this week',
    unknownDev: 'Unknown',
    heatmapNoActivity: 'No activity',
    heatmapLow: 'Low (1-3)',
    heatmapMedium: 'Medium (4-6)',
    heatmapHigh: 'High (7+)',
    dayMon: 'Mon',
    dayTue: 'Tue',
    dayWed: 'Wed',
    dayThu: 'Thu',
    dayFri: 'Fri',
    daySat: 'Sat',
    daySun: 'Sun',
    supportTicketsTitle: 'Support Tickets',
    supportTotalSuffix: 'total',
    supportByStatus: 'By status',
    supportBySeverity: 'By severity (active bugs)',
    supportAvgResolution: 'Avg. resolution time',
    hoursSuffix: 'hours',
    supportNoData: 'No support ticket data available.',
  },

  // ==========================================
  // SECTION: Team Assignment View
  // Ticket assignment to developers
  // ==========================================
  teamAssignmentView: {
    title: 'Team Assignment',
    subtitle: 'Distribute tickets among developers',
    applicationLabel: 'Application',
    selectOption: '-- Select --',
    unassignedTickets: 'Unassigned Tickets',
    ticketCount: 'ticket(s)',
    epicFilter: 'Epic',
    allEpics: 'All',
    priorityFilter: 'Priority',
    allPriorities: 'All',
    lowPriority: 'Low',
    mediumPriority: 'Medium',
    highPriority: 'High',
    urgentPriority: 'Urgent',
    assignButton: 'Assign',
    noUnassignedTickets: 'No unassigned tickets',
    allDistributed: 'All tickets have been distributed',
    developerWorkload: 'Developer Workload',
    developerCount: 'developer(s)',
  },

  nav: {
    administration: 'Administration',
    builder: 'Builder',
    analytics: 'Analytics',
    documentation: 'Documentation',
    team: 'Team',
    backToLogin: 'Back to login',
    adminPanel: 'Administration Panel',
    devPanel: 'Development Panel',
    development: 'Development',
    workbench: 'Workbench',
    myUploads: 'My Files',
    teamAssignment: 'Team Assignment',
    support: 'Support',
  },

  // ==========================================
  // SECTION: Support Tickets View
  // ==========================================
  supportTicketsView: {
    title: 'Support',
    reportBugButton: '+ Report Bug',
    criticalCountSuffix: 'critical ticket(s)',
    statusAll: 'All',
    statusReported: 'Reported',
    statusInvestigating: 'Investigating',
    statusResolved: 'Resolved',
    severityAll: 'All severities',
    severityCritical: '🔴 Critical',
    severityHigh: '🟠 High',
    severityMedium: '🟡 Medium',
    severityLow: '🟢 Low',
    severityNone: 'No severity',
    severityTextCritical: 'Critical',
    severityTextHigh: 'High',
    severityTextMedium: 'Medium',
    severityTextLow: 'Low',
    emptyList: 'No support tickets',
    loading: 'Loading tickets...',
    unassigned: 'Unassigned',
    assignToDeveloper: 'Assign to Developer',
    assign: 'Assign',
    assigning: '...',
    startInvestigation: '🔍 Start Investigation',
    processing: 'Processing...',
    markResolved: '✅ Mark as Resolved',
    description: 'Description',
    reproductionSteps: 'Reproduction Steps',
    stackTrace: 'Stack Trace',
    environment: 'Environment',
    browser: 'Browser',
    operatingSystem: 'Operating System',
    selectTicketPrompt: 'Select a ticket to see the details',
    formTitle: 'Report Support Bug',
    fieldTitle: 'Title',
    titlePlaceholder: 'Brief description of the bug',
    descriptionPlaceholder: 'Explain the unexpected behavior...',
    severityLabel: 'Severity',
    reproductionStepsPlaceholder: '1. Go to ...\n2. Click on ...\n3. Observe that ...',
    stackTracePlaceholder: 'Paste the error stack trace here...',
    browserPlaceholder: 'Chrome 120, Firefox 121...',
    osPlaceholder: 'Windows 11, macOS 14...',
    cancel: 'Cancel',
    submitReport: 'Report Bug',
    submitting: 'Reporting...',
    investigatedBy: 'Investigated by',
    linkedTicketLabel: 'Related ticket (optional)',
    linkedTicketNone: 'None',
  },

  workbenchDashboard: {
    myTickets: 'My Tickets',
    refresh: 'Refresh',
    statusLabel: 'Status:',
    dateLabel: 'Date:',
    statusAll: 'All',
    statusInProgress: 'In Progress',
    statusTodo: 'To Do',
    statusBlocked: 'Blocked',
    statusCompleted: 'Completed',
    dateAll: 'All',
    dateOverdue: 'Overdue',
    dateToday: 'Today',
    dateThisWeek: 'This Week',
    errorLoading: 'Error loading tickets',
    retry: 'Retry',
    loading: 'Loading tickets...',
    noResults: 'No results for these filters',
    clearFilters: 'Clear filters',
    noTickets: 'No tickets assigned to you',
    ticketsWillAppear: 'Tickets will appear here when assigned to you',
  },

  login: {
    subtitle: 'Operational Intelligence Platform',
    email: 'Email',
    emailPlaceholder: 'your email address',
    password: 'Password',
    passwordPlaceholder: 'your password',
    submit: 'Sign in',
    submitting: 'Signing in...',
    footer: '© {year} CoreStream · Operational Intelligence Platform',
    lightMode: 'Light mode',
    darkMode: 'Dark mode',
  },

  // ==========================================
  // SECTION: Ticket activity log
  // Event types and history
  // ==========================================
  activityLog: {
    title: 'Event History',
    noEvents: 'No events recorded',
    eventCreated: 'Ticket Created',
    eventAssigned: 'Assigned',
    eventStatusChanged: 'Status Changed',
    eventQuestionRaised: 'Question Raised',
    eventQuestionResolved: 'Question Resolved',
    eventRedirected: 'Redirected',
    eventCompleted: 'Completed',
    eventComment: 'Comment',
    eventUpdated: 'Updated',
    eventTimerStart: 'Timer Started',
    eventTimerPause: 'Timer Paused',
    eventTimerSync: 'Timer Synced',
    eventSubtaskCreated: 'Subtask Created',
    eventSubtaskCompleted: 'Subtask Completed',
    eventSubtaskDeleted: 'Subtask Deleted',
    eventMoved: 'Ticket Moved',
    eventBlocked: 'Blocked',
    eventBlockedQuestion: 'Blocking Question',
  },
}
