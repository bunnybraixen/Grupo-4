# RBAC — Matriz de permisos

Este documento describe **quién puede hacer qué** en CoreStream. Es la
referencia autoritativa: cualquier cambio de autorización en el backend debe
reflejarse aquí en el mismo commit.

## Roles

Definidos en `app/models/role.py` (`UserRole`) y reflejados en la tabla
`roles` (seedeada por la migración `a2b3c4d5e6f7_seed_base_roles`):

- **ADMIN** — el único que administra usuarios (invitar, cambiar roles,
  resetear contraseñas) y la estructura completa del sistema (aplicaciones,
  épicas, tickets). No ejecuta trabajo operativo sobre tickets (no puede
  iniciar/completar/preguntar) — ver nota sobre `require_non_admin` más
  abajo.
- **TEAM_LEADER** — gestiona el trabajo de su equipo: puede hacer todo lo que
  hace un DEVELOPER sobre tickets propios, más las acciones de gestión
  (crear/editar/borrar/reasignar tickets y épicas, crear/editar/borrar
  aplicaciones, resolver preguntas bloqueantes ajenas, redirigir tickets,
  gestionar reuniones e incidentes). No puede invitar usuarios, cambiar
  roles ni resetear contraseñas — eso queda exclusivo de ADMIN.
- **DEVELOPER** — ejecuta el trabajo: solo puede actuar sobre tickets/
  subtareas/documentos que le pertenecen (asignado o autor de la carga).

`middleware/rbac.py` (`RBACRole`) es el enum histórico usado por el
decorador `require_permissions` (hoy sin llamadas activas); el mecanismo
realmente en uso en los routers es `require_role(...)` de
`middleware/auth.py`, que compara contra este mismo conjunto de roles.
`_normalize_role` en ambos módulos lanza `ValueError`/`RuntimeError` ante un
rol desconocido — un typo en un nombre de rol falla ruidosamente, no deniega
en silencio.

## Helpers de autorización sobre tickets

`app/services/ticket_permissions.py` centraliza las reglas de ownership
sobre tickets, usadas por `routers/tickets.py`, `routers/subtasks.py` y
(para el caso de documentos) `routers/documents.py`:

| Helper | Regla |
|---|---|
| `require_non_admin` | Bloquea a ADMIN de las acciones de "trabajo" (start/complete/question): admins gestionan, no ejecutan. |
| `require_admin_or_leader` | Exige ADMIN o TEAM_LEADER. |
| `assert_can_manage_ticket` | ADMIN/TEAM_LEADER siempre puede; un DEVELOPER solo si es el asignado actual. Usado en edición de campos, mover de épica, reordenar, y en las mismas operaciones de subtareas. |
| `assert_is_current_assignee` | Solo el asignado actual, sin excepción de rol (ni ADMIN ni TEAM_LEADER). Usado en completar y en levantar una pregunta. |
| `claim_or_assert_assignee` | Si el ticket no tiene asignado, quien llama lo reclama; si ya tiene uno distinto, rechaza. Usado en `/start` — antes cualquiera podía "robar" un ticket asignado a otro con solo llamar a este endpoint. |
| `is_admin_or_leader` | Predicado usado para checks de ownership-o-rol (ej. borrar un documento: el autor de la carga, o ADMIN/TEAM_LEADER). |

## Matriz por recurso

### Aplicaciones (`/api/applications`)

| Acción | ADMIN | TEAM_LEADER | DEVELOPER |
|---|---|---|---|
| Listar / ver | ✅ | ✅ | ✅ |
| Crear / editar / borrar | ✅ | ✅ | ❌ |

Antes era ADMIN-only: obligaba al admin a crear cada proyecto nuevo en
persona, sin poder delegarlo en quien lleva el día a día del equipo. Se
extendió a TEAM_LEADER siguiendo el mismo criterio que ya aplicaba a
épicas/tickets — invitar usuarios, cambiar roles y resetear contraseñas
siguen siendo exclusivos de ADMIN (ver más abajo).

### Épicas (`/api/applications/{app_id}/epics`)

| Acción | ADMIN | TEAM_LEADER | DEVELOPER |
|---|---|---|---|
| Listar / ver | ✅ | ✅ | ✅ |
| Crear / editar / borrar / reordenar | ✅ | ✅ | ❌ |

### Tickets (`/api/tickets`)

| Acción | ADMIN | TEAM_LEADER | DEVELOPER (asignado) | DEVELOPER (ajeno) |
|---|---|---|---|---|
| Listar / ver / eventos | ✅ | ✅ | ✅ | ✅ |
| Crear | ✅ | ✅ | ❌ | ❌ |
| Editar campos / mover de épica / reordenar | ✅ | ✅ | ✅ | ❌ |
| Reasignar (`assignee_id` en el body de editar) | ✅ | ✅ | ❌ | ❌ |
| Borrar | ✅ | ✅ | ❌ | ❌ |
| Iniciar (`/start`) | ❌ (`require_non_admin`) | ✅ si no asignado o es él, ❌ si es de otro | ✅ (reclama si estaba libre) | ❌ |
| Completar (`/complete`) | ❌ | ❌ salvo que sea el asignado | ✅ | ❌ |
| Levantar pregunta bloqueante (`/question`) | ❌ | ❌ salvo que sea el asignado | ✅ | ❌ |
| Resolver pregunta bloqueante (`/question/resolve`) | ✅ | ✅ | ❌ | ❌ |
| Redirigir a otro usuario (`/redirect`) | ✅ | ✅ | ✅ si es el asignado | ❌ |

Notas:
- "Redirigir" está implementado en `routers/ticket_redirection.py`, montado
  **antes** de `routers/tickets.py` en `main.py` (comentario explícito:
  "MUST come before tickets.router"), por lo que es esa ruta la que
  atiende `POST /api/tickets/{id}/redirect`. `tickets.py` tenía un segundo
  `redirect_ticket` idéntico en path y verbo, inalcanzable — se eliminó en
  la fase de limpieza (fase 9).
- `require_non_admin` es una decisión de producto explícita: un ADMIN no
  ejecuta trabajo de ticket, solo lo gestiona.

### Subtareas (`/api/tickets/{ticket_id}/subtasks`)

Mismas reglas que la gestión de su ticket padre (`assert_can_manage_ticket`
sobre el `Ticket` referenciado por `ticket_id`):

| Acción | ADMIN | TEAM_LEADER | DEVELOPER (asignado al ticket) | DEVELOPER (ajeno) |
|---|---|---|---|---|
| Listar | ✅ | ✅ | ✅ | ✅ |
| Crear / editar / borrar / reordenar | ✅ | ✅ | ✅ | ❌ |

### Documentos (`/api/documents`)

| Acción | Quien subió el documento | ADMIN / TEAM_LEADER | Otro usuario |
|---|---|---|---|
| Listar / ver / descargar / traducir | ✅ (cualquier autenticado) | ✅ | ✅ |
| Cargar | ✅ (cualquier autenticado) | ✅ | ✅ |
| Borrar | ✅ | ✅ | ❌ |

La carga de documentos queda abierta a cualquier autenticado (no es un
recurso "propiedad de" nadie hasta que existe); el borrado sí requiere ser
el autor de la carga o tener rol de gestión.

### Notificaciones y adjuntos (`/api/notifications`, `/api/uploads`)

No usan `require_role`: cada consulta y cada archivo se filtra por
`current_user.id` en la propia query — un usuario solo puede ver o
manipular sus propias notificaciones y sus propios adjuntos, sin
distinción de rol.

### Usuarios e invitaciones (`/api/users`, `/api/invitations`)

| Acción | ADMIN | TEAM_LEADER | DEVELOPER |
|---|---|---|---|
| Crear usuario directamente | ✅ | ❌ | ❌ |
| Listar usuarios | ✅ | ✅ | ❌ |
| Ver perfil propio (`/me`) | ✅ | ✅ | ✅ |
| Editar / borrar / cambiar rol / resetear contraseña de otro usuario | ✅ | ❌ | ❌ |
| Crear invitación | ✅ | ❌ | ❌ |
| Aceptar invitación / consultar token | público (sin autenticar) | | |

### Reuniones (`/api/meetings`)

| Acción | ADMIN | TEAM_LEADER | DEVELOPER |
|---|---|---|---|
| Listar / ver | ✅ | ✅ | ✅ |
| Crear / editar / registrar asistencia | ✅ | ✅ | ❌ |

### Incidentes (`/api/incidents`)

| Acción | ADMIN | TEAM_LEADER | DEVELOPER |
|---|---|---|---|
| Crear / listar / ver | ✅ | ✅ | ✅ |
| Editar (`PATCH /{id}`) | ✅ | ✅ | ❌ |
| Cambiar estado (`PATCH /{id}/status`) | ✅ (cualquier autenticado; sin ownership) | ✅ | ✅ |

### Tickets de soporte (`/api/support-tickets`)

| Acción | ADMIN | TEAM_LEADER | DEVELOPER |
|---|---|---|---|
| Crear / listar / ver / investigar / resolver | ✅ | ✅ | ✅ |
| Asignar (`/assign`) | ❌ | ✅ | ❌ |

## Verificación

Los casos negativos de esta matriz están cubiertos por
`backend/tests/integration/test_rbac.py` y `test_tickets.py`. Los tres casos
concretos detectados en la auditoría original quedan verificados:

- `DELETE /api/tickets/{id}` sobre un ticket ajeno → **403** (antes: 204,
  borrado permanente).
- `POST /api/tickets/{id}/start` sobre un ticket ajeno ya asignado → **403**
  (antes: 200, reasignaba el ticket a quien llamaba).
- `POST /api/epics/` como DEVELOPER → **403** (antes: 201).
