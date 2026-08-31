/**
 * Traduções em Português para CoreStream
 * Todas as cadeias de interface de usuário organizadas por seções funcionais
 * Usa notação de ponto para acesso a chaves aninhadas (por exemplo, common.save)
 */

export default {
  // ==========================================
  // SECTION: Ações comuns e termos
  // Palavras-chave reutilizáveis em toda a interface
  // ==========================================
  common: {
    save: 'Salvar',
    cancel: 'Cancelar',
    delete: 'Excluir',
    edit: 'Editar',
    confirm: 'Confirmar',
    close: 'Fechar',
    search: 'Pesquisar',
    filter: 'Filtrar',
    loading: 'Carregando...',
    error: 'Erro',
    success: 'Sucesso',
    back: 'Voltar',
    next: 'Próximo',
    noData: 'Sem dados',
    actions: 'Ações',
    yes: 'Sim',
    no: 'Não',
    required: 'Obrigatório',
    optional: 'Opcional',
  },

  // ==========================================
  // SECTION: Cabeçalho e navegação superior
  // Elementos de cabeçalho/barra de navegação da aplicação
  // ==========================================
  header: {
    administrator: 'Administrador',
    developer: 'Desenvolvedor',
    settings: 'Configurações',
    notifications: 'Notificações',
    logout: 'Sair',
    profile: 'Perfil',
    darkMode: 'Modo escuro',
    language: 'Idioma',
  },

  // ==========================================
  // SECTION: Barra lateral
  // Menu de navegação lateral principal
  // ==========================================
  sidebar: {
    applications: 'Aplicações',
    sortByName: 'Ordenar por nome',
    sortByPending: 'Ordenar por pendentes',
    sortByDelayed: 'Ordenar por atrasados',
    newApp: 'Nova aplicação',
    noApps: 'Sem aplicações',
  },

  // ==========================================
  // SECTION: Construtor/Tela
  // Painel do construtor visual para épicos e tickets
  // ==========================================
  builder: {
    projectCanvas: 'Tela do projeto',
    newEpic: 'Novo épico',
    addTicket: 'Adicionar ticket',
    epicPlaceholder: 'Nome do épico',
    ticketPlaceholder: 'Descrição do ticket',
    dragEpicsHint: 'Arraste os épicos para reorganizar',
    showTickets: 'Mostrar tickets',
    hideTickets: 'Ocultar tickets',
    unassigned: 'Não atribuído',
    attachDocs: 'Anexar documentos',
    epicDocs: 'Documentos do épico',
    uploadSpec: 'Fazer upload da especificação',
    noDocsAttached: 'Nenhum documento anexado',
  },

  // ==========================================
  // SECTION: Bancada de trabalho
  // Painel de gerenciamento e rastreamento de tarefas
  // ==========================================
  workbench: {
    myWorkbench: 'Minha bancada de trabalho',
    allTickets: 'Todos os tickets',
    inProgress: 'Em progresso',
    todo: 'A fazer',
    done: 'Concluído',
    overdue: 'Atrasado',
    today: 'Hoje',
    thisWeek: 'Esta semana',
    later: 'Mais tarde',
    noTickets: 'Sem tickets',
    startWorking: 'Começar a trabalhar',
    selectTicket: 'Selecionar ticket',
    timer: 'Cronômetro',
    timeSpent: 'Tempo gasto',
    blockedTime: 'Tempo bloqueado',
    subtasks: 'Subtarefas',
    subtasksProgress: 'Progresso das subtarefas',
    activityLog: 'Registro de atividades',
  },

  // ==========================================
  // SECTION: Ações de tickets
  // Operações disponíveis para tickets
  // ==========================================
  actions: {
    complete: 'Completar',
    completeTicket: 'Completar ticket',
    raiseQuestion: 'Fazer uma pergunta',
    redirect: 'Redirecionar',
    prLink: 'Link do PR',
    prLinkPlaceholder: 'https://github.com/repo/pull/123',
    prRequired: 'Link do PR é obrigatório',
    invalidPr: 'Link do PR inválido',
    questionPlaceholder: 'Descreva sua pergunta aqui',
    questionMinLength: 'A pergunta deve ter pelo menos 10 caracteres',
    redirectTo: 'Redirecionar para',
    redirectReason: 'Motivo do redirecionamento',
    reasonPlaceholder: 'Explique por que este ticket está sendo redirecionado',
    reasonMinLength: 'O motivo deve ter pelo menos 10 caracteres',
    confirmComplete: 'Confirmar conclusão',
    confirmRedirect: 'Confirmar redirecionamento',
  },

  // ==========================================
  // SECTION: Análises e relatórios
  // Métricas, gráficos e estatísticas da equipe
  // ==========================================
  analytics: {
    analytics: 'Análises',
    commandCenter: 'Centro de comando',
    performanceMetrics: 'Métricas de desempenho',
    totalTickets: 'Total de tickets',
    completed: 'Concluído',
    blocked: 'Bloqueado',
    avgTime: 'Tempo médio',
    weekChange: 'Mudança semanal',
    efficiency: 'Eficiência',
    blockingIndex: 'Índice de bloqueio',
    churnIndex: 'Índice de rotatividade',
    heatmap: 'Mapa de calor',
    burndown: 'Gráfico de velocidade',
    exportPdf: 'Exportar PDF',
    exportCsv: 'Exportar CSV',
    ideal: 'Ideal',
    actual: 'Real',
    period: 'Período',
    lastWeek: 'Última semana',
    lastMonth: 'Último mês',
    lastQuarter: 'Último trimestre',
    teamPerformance: 'Desempenho da equipe',
    sortBy: 'Ordenar por',
    ticketsProcessed: 'Tickets processados',
    questions: 'Perguntas',
    redirects: 'Redirecionamentos',
    drillDown: 'Detalhar',
    insight: 'Insight',
    noData: 'Nenhum dado disponível',
  },

  // ==========================================
  // SECTION: Gerenciamento de equipe
  // Administração de membros e atribuições
  // ==========================================
  team: {
    teamManagement: 'Gerenciamento de equipe',
    teamAssignment: 'Atribuição de equipe',
    addDeveloper: 'Adicionar desenvolvedor',
    editMember: 'Editar membro',
    deleteMember: 'Excluir membro',
    promoteLeader: 'Promover a líder',
    demoteLeader: 'Rebaixar de líder',
    members: 'Membros',
    name: 'Nome',
    email: 'E-mail',
    role: 'Função',
    specialty: 'Especialidade',
    stats: 'Estatísticas',
    ticketsCompleted: 'Tickets concluídos',
    ticketsPending: 'Tickets pendentes',
    ticketsBlocked: 'Tickets bloqueados',
    avgTime: 'Tempo médio',
    unassignedTickets: 'Tickets não atribuídos',
    assignedTickets: 'Tickets atribuídos',
    workload: 'Carga de trabalho',
    lowLoad: 'Carga baixa',
    mediumLoad: 'Carga média',
    highLoad: 'Carga alta',
    assignTicket: 'Atribuir ticket',
    unassignTicket: 'Remover atribuição de ticket',
    confirmDelete: 'Confirmar exclusão',
    noMembers: 'Nenhum membro da equipe',
  },

  // ==========================================
  // SECTION: Código e documentação
  // Gerenciamento de arquivos, repositório e documentação
  // ==========================================
  codeDocs: {
    codeAndDocs: 'Código e documentação',
    repository: 'Repositório',
    totalFiles: 'Arquivos totais',
    codeFiles: 'Arquivos de código',
    docFiles: 'Arquivos de documentação',
    contributors: 'Colaboradores',
    upload: 'Fazer upload',
    translate: 'Traduzir',
    translateTo: 'Traduzir para',
    download: 'Fazer download',
    noFiles: 'Sem arquivos',
  },

  // ==========================================
  // SECTION: Notificações
  // Mensagens e alertas do sistema
  // ==========================================
  notifications: {
    title: 'Notificações',
    markAllRead: 'Marcar tudo como lido',
    noNotifications: 'Sem notificações',
    assignedToYou: 'Um ticket foi atribuído a você',
    questionRaised: 'Uma pergunta foi feita',
    ticketRedirected: 'O ticket foi redirecionado',
    ticketCompleted: 'O ticket foi concluído',
    systemMessage: 'Mensagem do sistema',
  },

  // ==========================================
  // SECTION: Configurações
  // Preferências de usuário e aplicação
  // ==========================================
  settings: {
    settingsTitle: 'Configurações',
    language: 'Idioma',
    theme: 'Tema',
    lightMode: 'Modo claro',
    darkMode: 'Modo escuro',
    profile: 'Perfil',
    saveChanges: 'Salvar alterações',
  },

  // ==========================================
  // SECTION: Status dos tickets
  // Estados de progresso e prioridades
  // ==========================================
  statuses: {
    todo: 'A fazer',
    inProgress: 'Em progresso',
    blocked: 'Bloqueado',
    redirected: 'Redirecionado',
    done: 'Concluído',
    low: 'Baixa',
    medium: 'Média',
    high: 'Alta',
    urgent: 'Urgente',
  },

  // ==========================================
  // SECTION: Papéis de usuário
  // Tipos de permissões e acesso
  // ==========================================
  roles: {
    admin: 'Administrador',
    groupLeader: 'Líder do grupo',
    developer: 'Desenvolvedor',
  },

  // ==========================================
  // SECTION: Mensagens de erro
  // Texto para diferentes tipos de erros
  // ==========================================
  errors: {
    generic: 'Ocorreu um erro',
    unauthorized: 'Não autorizado',
    notFound: 'Não encontrado',
    forbidden: 'Acesso negado',
    serverError: 'Erro do servidor',
    networkError: 'Erro de rede',
    validationError: 'Erro de validação',
    loginFailed: 'Falha no login',
    emailTaken: 'E-mail já registrado',
  },

  // ==========================================
  // SECTION: Diálogos de confirmação
  // Mensagens de confirmação para ações críticas
  // ==========================================
  confirm: {
    deleteTicket: 'Excluir este ticket?',
    deleteEpic: 'Excluir este épico?',
    deleteApp: 'Excluir esta aplicação?',
    deleteMember: 'Excluir este membro da equipe?',
    redirectTicket: 'Redirecionar este ticket?',
    completeTicket: 'Marcar como concluído?',
    logout: 'Sair?',
  },
}
