/**
 * Índice de Exportación - Pinia Stores CoreStream
 * 
 * Importa y exporta todas las tiendas para uso en la aplicación
 * 
 * Uso en componentes:
 * import { useAuthStore, useTicketsStore } from '@/stores'
 * 
 * O:
 * import { useAuthStore } from '@/stores/auth'
 */

// Autenticación
export { useAuthStore } from './auth'

// Aplicaciones
export { useApplicationsStore } from './applications'

// Épicos
export { useEpicsStore } from './epics'

// Tickets (la más importante)
export { useTicketsStore } from './tickets'

// Analíticas
export { useAnalyticsStore } from './analytics'

// Notificaciones
export { useNotificationsStore } from './notifications'

// Equipo
export { useTeamStore } from './team'

/**
 * GUÍA DE TIENDAS
 * 
 * useAuthStore
 *   - Estado: user, tokens, isAuthenticated, isLoading, error
 *   - Acciones: login, register, logout, refreshToken, updateProfile, etc.
 *   - Getters: isAdmin, isDeveloper, isGroupLeader, fullName, isTokenExpiringSoon
 * 
 * useApplicationsStore
 *   - Estado: applications, selectedApp, isLoading, error
 *   - Acciones: fetchAll, create, update, remove, selectApp, searchApplications
 *   - Getters: sortedByName, sortedByPending, sortedByDelayed, overallProgress
 * 
 * useEpicsStore
 *   - Estado: epics, collapsedEpics, isLoading, error
 *   - Acciones: fetchByApp, create, update, remove, reorder, toggleCollapse
 *   - Getters: sortedByOrder, withProgress, expandedEpics, overallEpicsProgress
 * 
 * useTicketsStore ⭐ LA MÁS IMPORTANTE
 *   - Estado: tickets, myWorkbench, selectedTicket, statusFilter, dateFilter
 *   - Acciones: fetchByEpic, fetchMyWorkbench, create, update, remove, moveToEpic
 *              completeTicket, startWorking, raiseQuestion, resolveQuestion, redirectTicket
 *   - Getters: filteredTickets, overdueTickets, inProgressTickets, todoTickets
 *             completedTickets, blockedTickets, sortedByDueDate, sortedByPriority
 * 
 * useAnalyticsStore
 *   - Estado: summary, performance, heatmapData, burndownData, dateRange
 *   - Acciones: fetchSummary, fetchPerformance, fetchHeatmap, fetchBurndown
 *              exportCsv, exportPdf, setDateRange, setSortColumn
 *   - Getters: sortedPerformance, topPerformer, teamAverageVelocity, teamBlockedRate
 * 
 * useNotificationsStore
 *   - Estado: notifications, unreadCount, isLoading, error
 *   - Acciones: fetch, fetchUnreadCount, markAsRead, markAllAsRead, addNotification
 *              deleteNotification, deleteAllRead, loadMore
 *   - Getters: unreadNotifications, recentNotifications, sortedByDate, groupedByDate
 * 
 * useTeamStore
 *   - Estado: members, unassignedTickets, showAddModal, isLoading, error
 *   - Acciones: fetchMembers, addMember, updateMember, deleteMember, promoteToLeader
 *              demoteLeader, fetchUnassigned, assignTicket, unassignTicket
 *   - Getters: leaders, developers, admin, sortedByName, groupedByRole
 */
