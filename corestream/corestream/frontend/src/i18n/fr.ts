/**
 * Traductions françaises pour CoreStream
 * Toutes les chaînes de l'interface utilisateur organisées par sections fonctionnelles
 * Utilise la notation pointée pour l'accès aux clés imbriquées (par exemple, common.save)
 */

export default {
  // ==========================================
  // SECTION: Actions communes et termes
  // Mots-clés réutilisables dans l'interface
  // ==========================================
  common: {
    save: 'Enregistrer',
    cancel: 'Annuler',
    delete: 'Supprimer',
    edit: 'Modifier',
    confirm: 'Confirmer',
    close: 'Fermer',
    search: 'Rechercher',
    filter: 'Filtrer',
    loading: 'Chargement...',
    error: 'Erreur',
    success: 'Succès',
    back: 'Retour',
    next: 'Suivant',
    noData: 'Pas de données',
    actions: 'Actions',
    yes: 'Oui',
    no: 'Non',
    required: 'Requis',
    optional: 'Optionnel',
  },

  // ==========================================
  // SECTION: En-tête et navigation supérieure
  // Éléments d'en-tête/barre de navigation
  // ==========================================
  header: {
    administrator: 'Administrateur',
    developer: 'Développeur',
    settings: 'Paramètres',
    notifications: 'Notifications',
    logout: 'Déconnexion',
    profile: 'Profil',
    darkMode: 'Mode sombre',
    language: 'Langue',
  },

  // ==========================================
  // SECTION: Barre latérale
  // Menu de navigation latéral principal
  // ==========================================
  sidebar: {
    applications: 'Applications',
    sortByName: 'Trier par nom',
    sortByPending: 'Trier par en attente',
    sortByDelayed: 'Trier par retardés',
    newApp: 'Nouvelle application',
    noApps: 'Pas d\'applications',
  },

  // ==========================================
  // SECTION: Constructeur/Canevas
  // Panneau de constructeur visuel pour épiques et tickets
  // ==========================================
  builder: {
    projectCanvas: 'Canevas du projet',
    newEpic: 'Nouvel épique',
    addTicket: 'Ajouter un ticket',
    epicPlaceholder: 'Nom de l\'épique',
    ticketPlaceholder: 'Description du ticket',
    dragEpicsHint: 'Faites glisser les épiques pour réorganiser',
    showTickets: 'Afficher les tickets',
    hideTickets: 'Masquer les tickets',
    unassigned: 'Non attribué',
    attachDocs: 'Joindre des documents',
    epicDocs: 'Documents de l\'épique',
    uploadSpec: 'Charger la spécification',
    noDocsAttached: 'Aucun document joint',
  },

  // ==========================================
  // SECTION: Établi
  // Panneau de gestion et de suivi des tâches
  // ==========================================
  workbench: {
    myWorkbench: 'Mon établi',
    allTickets: 'Tous les tickets',
    inProgress: 'En cours',
    todo: 'À faire',
    done: 'Fait',
    overdue: 'En retard',
    today: 'Aujourd\'hui',
    thisWeek: 'Cette semaine',
    later: 'Plus tard',
    noTickets: 'Pas de tickets',
    startWorking: 'Commencer à travailler',
    selectTicket: 'Sélectionner un ticket',
    timer: 'Minuteur',
    timeSpent: 'Temps passé',
    blockedTime: 'Temps bloqué',
    subtasks: 'Sous-tâches',
    subtasksProgress: 'Progression des sous-tâches',
    activityLog: 'Journal d\'activité',
  },

  // ==========================================
  // SECTION: Actions sur les tickets
  // Opérations disponibles pour les tickets
  // ==========================================
  actions: {
    complete: 'Terminer',
    completeTicket: 'Terminer le ticket',
    raiseQuestion: 'Poser une question',
    redirect: 'Rediriger',
    prLink: 'Lien PR',
    prLinkPlaceholder: 'https://github.com/repo/pull/123',
    prRequired: 'Le lien PR est requis',
    invalidPr: 'Lien PR invalide',
    questionPlaceholder: 'Décrivez votre question ici',
    questionMinLength: 'La question doit faire au moins 10 caractères',
    redirectTo: 'Rediriger vers',
    redirectReason: 'Raison de la redirection',
    reasonPlaceholder: 'Expliquez pourquoi ce ticket est redirigé',
    reasonMinLength: 'La raison doit faire au moins 10 caractères',
    confirmComplete: 'Confirmer la complétion',
    confirmRedirect: 'Confirmer la redirection',
  },

  // ==========================================
  // SECTION: Analyses et rapports
  // Métriques, graphiques et statistiques d'équipe
  // ==========================================
  analytics: {
    analytics: 'Analyses',
    commandCenter: 'Centre de commande',
    performanceMetrics: 'Métriques de performance',
    totalTickets: 'Tickets totaux',
    completed: 'Terminés',
    blocked: 'Bloqués',
    avgTime: 'Temps moyen',
    weekChange: 'Changement hebdomadaire',
    efficiency: 'Efficacité',
    blockingIndex: 'Indice de blocage',
    churnIndex: 'Indice de renouvellement',
    heatmap: 'Carte de chaleur',
    burndown: 'Diagramme d\'avancement',
    exportPdf: 'Exporter en PDF',
    exportCsv: 'Exporter en CSV',
    ideal: 'Idéal',
    actual: 'Réel',
    period: 'Période',
    lastWeek: 'Semaine dernière',
    lastMonth: 'Mois dernier',
    lastQuarter: 'Trimestre dernier',
    teamPerformance: 'Performance de l\'équipe',
    sortBy: 'Trier par',
    ticketsProcessed: 'Tickets traités',
    questions: 'Questions',
    redirects: 'Redirections',
    drillDown: 'Détailler',
    insight: 'Analyse',
    noData: 'Pas de données disponibles',
  },

  // ==========================================
  // SECTION: Gestion d'équipe
  // Administration des membres et affectations
  // ==========================================
  team: {
    teamManagement: 'Gestion d\'équipe',
    teamAssignment: 'Affectation d\'équipe',
    addDeveloper: 'Ajouter un développeur',
    editMember: 'Modifier le membre',
    deleteMember: 'Supprimer le membre',
    promoteLeader: 'Promouvoir en leader',
    demoteLeader: 'Rétrograder de leader',
    members: 'Membres',
    name: 'Nom',
    email: 'E-mail',
    role: 'Rôle',
    specialty: 'Spécialité',
    stats: 'Statistiques',
    ticketsCompleted: 'Tickets terminés',
    ticketsPending: 'Tickets en attente',
    ticketsBlocked: 'Tickets bloqués',
    avgTime: 'Temps moyen',
    unassignedTickets: 'Tickets non attribués',
    assignedTickets: 'Tickets attribués',
    workload: 'Charge de travail',
    lowLoad: 'Charge faible',
    mediumLoad: 'Charge moyenne',
    highLoad: 'Charge élevée',
    assignTicket: 'Attribuer un ticket',
    unassignTicket: 'Désattribuer un ticket',
    confirmDelete: 'Confirmer la suppression',
    noMembers: 'Pas de membres d\'équipe',
  },

  // ==========================================
  // SECTION: Code et documentation
  // Gestion des fichiers, dépôt et documentation
  // ==========================================
  codeDocs: {
    codeAndDocs: 'Code et documentation',
    repository: 'Dépôt',
    totalFiles: 'Fichiers totaux',
    codeFiles: 'Fichiers de code',
    docFiles: 'Fichiers de documentation',
    contributors: 'Contributeurs',
    upload: 'Télécharger',
    translate: 'Traduire',
    translateTo: 'Traduire en',
    download: 'Télécharger',
    noFiles: 'Pas de fichiers',
  },

  // ==========================================
  // SECTION: Notifications
  // Messages système et alertes
  // ==========================================
  notifications: {
    title: 'Notifications',
    markAllRead: 'Marquer tout comme lu',
    noNotifications: 'Pas de notifications',
    assignedToYou: 'Un ticket vous a été attribué',
    questionRaised: 'Une question a été posée',
    ticketRedirected: 'Le ticket a été redirigé',
    ticketCompleted: 'Le ticket a été complété',
    systemMessage: 'Message système',
  },

  // ==========================================
  // SECTION: Paramètres
  // Préférences utilisateur et application
  // ==========================================
  settings: {
    settingsTitle: 'Paramètres',
    language: 'Langue',
    theme: 'Thème',
    lightMode: 'Mode clair',
    darkMode: 'Mode sombre',
    profile: 'Profil',
    saveChanges: 'Enregistrer les modifications',
  },

  // ==========================================
  // SECTION: États des tickets
  // États de progression et priorités
  // ==========================================
  statuses: {
    todo: 'À faire',
    inProgress: 'En cours',
    blocked: 'Bloqué',
    redirected: 'Redirigé',
    done: 'Fait',
    low: 'Basse',
    medium: 'Moyenne',
    high: 'Élevée',
    urgent: 'Urgente',
  },

  // ==========================================
  // SECTION: Rôles d'utilisateur
  // Types de permissions et d'accès
  // ==========================================
  roles: {
    admin: 'Administrateur',
    groupLeader: 'Leader du groupe',
    developer: 'Développeur',
  },

  // ==========================================
  // SECTION: Messages d'erreur
  // Texte pour différents types d'erreurs
  // ==========================================
  errors: {
    generic: 'Une erreur s\'est produite',
    unauthorized: 'Non autorisé',
    notFound: 'Non trouvé',
    forbidden: 'Accès refusé',
    serverError: 'Erreur du serveur',
    networkError: 'Erreur réseau',
    validationError: 'Erreur de validation',
    loginFailed: 'Échec de la connexion',
    emailTaken: 'E-mail déjà enregistré',
  },

  // ==========================================
  // SECTION: Dialogues de confirmation
  // Messages de confirmation pour les actions critiques
  // ==========================================
  confirm: {
    deleteTicket: 'Supprimer ce ticket ?',
    deleteEpic: 'Supprimer cet épique ?',
    deleteApp: 'Supprimer cette application ?',
    deleteMember: 'Supprimer ce membre d\'équipe ?',
    redirectTicket: 'Rediriger ce ticket ?',
    completeTicket: 'Marquer comme complet ?',
    logout: 'Déconnexion ?',
  },
}
