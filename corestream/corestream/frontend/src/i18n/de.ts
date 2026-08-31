/**
 * Deutsche Übersetzungen für CoreStream
 * Alle Benutzeroberflächentexte, organisiert nach funktionalen Abschnitten
 * Verwendet Punktnotation für den Zugriff auf verschachtelte Schlüssel (z. B. common.save)
 */

export default {
  // ==========================================
  // SECTION: Häufige Aktionen und Begriffe
  // Wiederverwendbare Schlüsselwörter in der gesamten Oberfläche
  // ==========================================
  common: {
    save: 'Speichern',
    cancel: 'Abbrechen',
    delete: 'Löschen',
    edit: 'Bearbeiten',
    confirm: 'Bestätigen',
    close: 'Schließen',
    search: 'Suchen',
    filter: 'Filtern',
    loading: 'Wird geladen...',
    error: 'Fehler',
    success: 'Erfolg',
    back: 'Zurück',
    next: 'Weiter',
    noData: 'Keine Daten',
    actions: 'Aktionen',
    yes: 'Ja',
    no: 'Nein',
    required: 'Erforderlich',
    optional: 'Optional',
  },

  // ==========================================
  // SECTION: Kopfzeile und obere Navigation
  // Kopfzeilen-/Navigationselemente der Anwendung
  // ==========================================
  header: {
    administrator: 'Administrator',
    developer: 'Entwickler',
    settings: 'Einstellungen',
    notifications: 'Benachrichtigungen',
    logout: 'Abmelden',
    profile: 'Profil',
    darkMode: 'Dunkler Modus',
    language: 'Sprache',
  },

  // ==========================================
  // SECTION: Seitenleiste
  // Hauptmenü der Seitennavigation
  // ==========================================
  sidebar: {
    applications: 'Anwendungen',
    sortByName: 'Nach Name sortieren',
    sortByPending: 'Nach ausstehend sortieren',
    sortByDelayed: 'Nach verzögert sortieren',
    newApp: 'Neue Anwendung',
    noApps: 'Keine Anwendungen',
  },

  // ==========================================
  // SECTION: Builder/Leinwand
  // Visuelles Builder-Panel für Epics und Tickets
  // ==========================================
  builder: {
    projectCanvas: 'Projekt-Leinwand',
    newEpic: 'Neues Epic',
    addTicket: 'Ticket hinzufügen',
    epicPlaceholder: 'Epic-Name',
    ticketPlaceholder: 'Ticket-Beschreibung',
    dragEpicsHint: 'Ziehen Sie Epics zum Umorganisieren',
    showTickets: 'Tickets anzeigen',
    hideTickets: 'Tickets ausblenden',
    unassigned: 'Nicht zugewiesen',
    attachDocs: 'Dokumente anhängen',
    epicDocs: 'Epic-Dokumente',
    uploadSpec: 'Spezifikation hochladen',
    noDocsAttached: 'Keine Dokumente angehängt',
  },

  // ==========================================
  // SECTION: Werkbank
  // Aufgabenverwaltungs- und Tracking-Panel
  // ==========================================
  workbench: {
    myWorkbench: 'Meine Werkbank',
    allTickets: 'Alle Tickets',
    inProgress: 'In Bearbeitung',
    todo: 'Zu tun',
    done: 'Fertig',
    overdue: 'Überfällig',
    today: 'Heute',
    thisWeek: 'Diese Woche',
    later: 'Später',
    noTickets: 'Keine Tickets',
    startWorking: 'Mit der Arbeit beginnen',
    selectTicket: 'Ticket auswählen',
    timer: 'Timer',
    timeSpent: 'Aufgewendete Zeit',
    blockedTime: 'Blockierte Zeit',
    subtasks: 'Unteraufgaben',
    subtasksProgress: 'Fortschritt der Unteraufgaben',
    activityLog: 'Aktivitätsprotokoll',
  },

  // ==========================================
  // SECTION: Ticket-Aktionen
  // Verfügbare Operationen für Tickets
  // ==========================================
  actions: {
    complete: 'Fertigstellen',
    completeTicket: 'Ticket fertigstellen',
    raiseQuestion: 'Frage stellen',
    redirect: 'Umleiten',
    prLink: 'PR-Link',
    prLinkPlaceholder: 'https://github.com/repo/pull/123',
    prRequired: 'PR-Link erforderlich',
    invalidPr: 'Ungültiger PR-Link',
    questionPlaceholder: 'Beschreiben Sie Ihre Frage hier',
    questionMinLength: 'Die Frage muss mindestens 10 Zeichen lang sein',
    redirectTo: 'Umleiten zu',
    redirectReason: 'Umleitungsgrund',
    reasonPlaceholder: 'Erklären Sie, warum dieses Ticket umgeleitet wird',
    reasonMinLength: 'Der Grund muss mindestens 10 Zeichen lang sein',
    confirmComplete: 'Fertigstellung bestätigen',
    confirmRedirect: 'Umleitung bestätigen',
  },

  // ==========================================
  // SECTION: Analysen und Berichte
  // Team-Metriken, Diagramme und Statistiken
  // ==========================================
  analytics: {
    analytics: 'Analysen',
    commandCenter: 'Kommandozentrale',
    performanceMetrics: 'Leistungsmetriken',
    totalTickets: 'Gesamtickets',
    completed: 'Abgeschlossen',
    blocked: 'Blockiert',
    avgTime: 'Durchschnittliche Zeit',
    weekChange: 'Wochenveränderung',
    efficiency: 'Effizienz',
    blockingIndex: 'Blockierungsindex',
    churnIndex: 'Abwanderungsindex',
    heatmap: 'Wärmekarte',
    burndown: 'Burn-down-Diagramm',
    exportPdf: 'Als PDF exportieren',
    exportCsv: 'Als CSV exportieren',
    ideal: 'Ideal',
    actual: 'Tatsächlich',
    period: 'Zeitraum',
    lastWeek: 'Letzte Woche',
    lastMonth: 'Letzten Monat',
    lastQuarter: 'Letztes Quartal',
    teamPerformance: 'Team-Leistung',
    sortBy: 'Sortieren nach',
    ticketsProcessed: 'Bearbeitete Tickets',
    questions: 'Fragen',
    redirects: 'Umleitungen',
    drillDown: 'Drilldown',
    insight: 'Einsicht',
    noData: 'Keine Daten verfügbar',
  },

  // ==========================================
  // SECTION: Team-Verwaltung
  // Mitgliederverwaltung und Zuweisungen
  // ==========================================
  team: {
    teamManagement: 'Team-Verwaltung',
    teamAssignment: 'Team-Zuweisung',
    addDeveloper: 'Entwickler hinzufügen',
    editMember: 'Mitglied bearbeiten',
    deleteMember: 'Mitglied löschen',
    promoteLeader: 'Zum Leader befördern',
    demoteLeader: 'Von Leader herabstufen',
    members: 'Mitglieder',
    name: 'Name',
    email: 'E-Mail',
    role: 'Rolle',
    specialty: 'Fachgebiet',
    stats: 'Statistiken',
    ticketsCompleted: 'Tickets abgeschlossen',
    ticketsPending: 'Ausstehende Tickets',
    ticketsBlocked: 'Blockierte Tickets',
    avgTime: 'Durchschnittliche Zeit',
    unassignedTickets: 'Nicht zugewiesene Tickets',
    assignedTickets: 'Zugewiesene Tickets',
    workload: 'Arbeitslast',
    lowLoad: 'Geringe Last',
    mediumLoad: 'Mittlere Last',
    highLoad: 'Hohe Last',
    assignTicket: 'Ticket zuweisen',
    unassignTicket: 'Ticket abmelden',
    confirmDelete: 'Löschen bestätigen',
    noMembers: 'Keine Team-Mitglieder',
  },

  // ==========================================
  // SECTION: Code und Dokumentation
  // Dateiverwaltung, Repository und Dokumentation
  // ==========================================
  codeDocs: {
    codeAndDocs: 'Code und Dokumentation',
    repository: 'Repository',
    totalFiles: 'Gesamtdateien',
    codeFiles: 'Code-Dateien',
    docFiles: 'Dokumentationsdateien',
    contributors: 'Mitwirkende',
    upload: 'Hochladen',
    translate: 'Übersetzen',
    translateTo: 'Übersetzen nach',
    download: 'Herunterladen',
    noFiles: 'Keine Dateien',
  },

  // ==========================================
  // SECTION: Benachrichtigungen
  // Systemmeldungen und Warnungen
  // ==========================================
  notifications: {
    title: 'Benachrichtigungen',
    markAllRead: 'Alle als gelesen markieren',
    noNotifications: 'Keine Benachrichtigungen',
    assignedToYou: 'Ein Ticket wurde Ihnen zugewiesen',
    questionRaised: 'Eine Frage wurde gestellt',
    ticketRedirected: 'Das Ticket wurde umgeleitet',
    ticketCompleted: 'Das Ticket wurde abgeschlossen',
    systemMessage: 'Systemmeldung',
  },

  // ==========================================
  // SECTION: Einstellungen
  // Benutzer- und Anwendungseinstellungen
  // ==========================================
  settings: {
    settingsTitle: 'Einstellungen',
    language: 'Sprache',
    theme: 'Thema',
    lightMode: 'Heller Modus',
    darkMode: 'Dunkler Modus',
    profile: 'Profil',
    saveChanges: 'Änderungen speichern',
  },

  // ==========================================
  // SECTION: Ticket-Status
  // Fortschrittsstatus und Prioritäten
  // ==========================================
  statuses: {
    todo: 'Zu tun',
    inProgress: 'In Bearbeitung',
    blocked: 'Blockiert',
    redirected: 'Umgeleitet',
    done: 'Fertig',
    low: 'Niedrig',
    medium: 'Mittel',
    high: 'Hoch',
    urgent: 'Dringend',
  },

  // ==========================================
  // SECTION: Benutzerrollen
  // Arten von Berechtigungen und Zugriff
  // ==========================================
  roles: {
    admin: 'Administrator',
    groupLeader: 'Gruppenleiter',
    developer: 'Entwickler',
  },

  // ==========================================
  // SECTION: Fehlermeldungen
  // Text für verschiedene Fehlertypen
  // ==========================================
  errors: {
    generic: 'Ein Fehler ist aufgetreten',
    unauthorized: 'Nicht autorisiert',
    notFound: 'Nicht gefunden',
    forbidden: 'Zugriff verweigert',
    serverError: 'Serverfehler',
    networkError: 'Netzwerkfehler',
    validationError: 'Validierungsfehler',
    loginFailed: 'Anmeldung fehlgeschlagen',
    emailTaken: 'E-Mail bereits registriert',
  },

  // ==========================================
  // SECTION: Bestätigungsdialogfelder
  // Bestätigungsmeldungen für kritische Aktionen
  // ==========================================
  confirm: {
    deleteTicket: 'Dieses Ticket löschen?',
    deleteEpic: 'Dieses Epic löschen?',
    deleteApp: 'Diese Anwendung löschen?',
    deleteMember: 'Dieses Team-Mitglied löschen?',
    redirectTicket: 'Dieses Ticket umleiten?',
    completeTicket: 'Als abgeschlossen markieren?',
    logout: 'Abmelden?',
  },
}
