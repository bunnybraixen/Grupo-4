#!/bin/bash
# ═════════════════════════════════════════════════════════════════════════════
# SCRIPT DE VALIDACIÓN MANUAL - PROTOCOLO QA
# CoreStream Sprints 3-4 - FIX-001, 002, 003, 004
# ═════════════════════════════════════════════════════════════════════════════

# ⚠️  PREREQUISITOS:
# - Backend corriendo en http://localhost:8000
# - PostgreSQL con índices creados (ver create_indices_fix_003.sql)
# - Frontend compilado y corriendo en http://localhost:5173

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  PROTOCOLO DE VALIDACIÓN MANUAL - SPRINTS 3-4                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"

# ═════════════════════════════════════════════════════════════════════
# TEST #1: FIX-001 - ATOMICIDAD EN REORDER
# ═════════════════════════════════════════════════════════════════════

echo ""
echo "🔒 TEST #1: ATOMICIDAD EN PATCH /epics/{id}/reorder"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Paso 1: Crear una aplicación"
APP_ID=$(uuidgen)
curl -X POST http://localhost:8000/api/applications \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Test App $(date +%s)\",
    \"description\": \"Para testing de reorder atómico\",
    \"color\": \"#2563EB\",
    \"owner_id\": \"$(uuidgen)\"
  }" 2>/dev/null | jq '.id'

echo ""
echo "Paso 2: Crear 3 épicas"
EPIC_1=$(curl -s -X POST http://localhost:8000/api/epics \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Epic 1\",
    \"application_id\": \"$APP_ID\",
    \"order_index\": 0
  }" | jq -r '.id')

EPIC_2=$(curl -s -X POST http://localhost:8000/api/epics \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Epic 2\",
    \"application_id\": \"$APP_ID\",
    \"order_index\": 1
  }" | jq -r '.id')

EPIC_3=$(curl -s -X POST http://localhost:8000/api/epics \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Epic 3\",
    \"application_id\": \"$APP_ID\",
    \"order_index\": 2
  }" | jq -r '.id')

echo "Epic 1: $EPIC_1"
echo "Epic 2: $EPIC_2"
echo "Epic 3: $EPIC_3"

echo ""
echo "Paso 3: Reordenar Epic 1 (0 → 2)"
curl -X PATCH "http://localhost:8000/api/epics/$EPIC_1/reorder" \
  -H "Content-Type: application/json" \
  -d '{"new_index": 2}' 2>/dev/null | jq '.order_index'

echo ""
echo "Paso 4: Verificar que order_index NO está duplicado"
echo "Esperado: [0, 1, 2] - Actual:"
curl -s "http://localhost:8000/api/epics/by-app/$APP_ID" | jq '[.[] | .order_index] | sort'

echo "✅ PASS: Si el resultado es [0, 1, 2], FIX-001 funciona"

# ═════════════════════════════════════════════════════════════════════
# TEST #2: FIX-002 - VALIDACIÓN CROSS-APP
# ═════════════════════════════════════════════════════════════════════

echo ""
echo ""
echo "🔐 TEST #2: VALIDACIÓN CROSS-APP EN PATCH /tickets/{id}/move"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Paso 1: Crear App A (E-Commerce)"
APP_A=$(curl -s -X POST http://localhost:8000/api/applications \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"App A - E-Commerce\",
    \"description\": \"Tienda online\",
    \"color\": \"#DC2626\",
    \"owner_id\": \"$(uuidgen)\"
  }" | jq -r '.id')

echo "Paso 2: Crear App B (CRM)"
APP_B=$(curl -s -X POST http://localhost:8000/api/applications \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"App B - CRM\",
    \"description\": \"Gestión de clientes\",
    \"color\": \"#2563EB\",
    \"owner_id\": \"$(uuidgen)\"
  }" | jq -r '.id')

echo "App A: $APP_A"
echo "App B: $APP_B"

echo ""
echo "Paso 3: Crear Epic A1 en App A"
EPIC_A1=$(curl -s -X POST http://localhost:8000/api/epics \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Epic A1 - Checkout\",
    \"application_id\": \"$APP_A\",
    \"order_index\": 0
  }" | jq -r '.id')

echo "Paso 4: Crear Epic B1 en App B"
EPIC_B1=$(curl -s -X POST http://localhost:8000/api/epics \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Epic B1 - Leads\",
    \"application_id\": \"$APP_B\",
    \"order_index\": 0
  }" | jq -r '.id')

echo "Epic A1: $EPIC_A1"
echo "Epic B1: $EPIC_B1"

echo ""
echo "Paso 5: Crear Ticket en Epic A1"
TICKET=$(curl -s -X POST http://localhost:8000/api/tickets \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Fix button color\",
    \"epic_id\": \"$EPIC_A1\",
    \"status\": \"TODO\"
  }" | jq -r '.id')

echo "Ticket: $TICKET (en App A, Epic A1)"

echo ""
echo "Paso 6: ❌ INTENTAR mover a Epic B1 (DEBE FALLAR)"
echo "Esperado: HTTP 400 - 'Apps diferentes, movimiento rechazado'"
curl -X PATCH "http://localhost:8000/api/tickets/$TICKET/move" \
  -H "Content-Type: application/json" \
  -d "{\"new_epic_id\": \"$EPIC_B1\"}" 2>/dev/null | jq '.detail'

echo ""
echo "✅ PASS: Si retorna 400 + mensaje, FIX-002 funciona"

# ═════════════════════════════════════════════════════════════════════
# TEST #3: FIX-003 - CONTEOS DINÁMICOS
# ═════════════════════════════════════════════════════════════════════

echo ""
echo ""
echo "📊 TEST #3: CONTEOS REALES EN GET /applications"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Paso 1: Consultar GET /applications"
echo "Esperado:"
echo "  - epic_count = 1 (Epic A1)"
echo "  - pending_count = 1 (Ticket TODO)"
echo "  - delayed_count = 0 (ninguno retrasado)"
echo ""
echo "Actual:"
curl -s "http://localhost:8000/api/applications" | jq '.[] | {
  name,
  epic_count,
  pending_count,
  delayed_count
}'

echo ""
echo "✅ PASS: Si los conteos coinciden, FIX-003 funciona"

# ═════════════════════════════════════════════════════════════════════
# TEST #4: FIX-004 - BADGES DINÁMICOS EN UI
# ═════════════════════════════════════════════════════════════════════

echo ""
echo ""
echo "🎨 TEST #4: BADGES DINÁMICOS EN ApplicationList.vue"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Paso 1: Ir al navegador y abrir http://localhost:5173"
echo "Paso 2: Ver barra lateral izquierda (Aplicaciones)"
echo "Paso 3: Buscar App A"
echo ""
echo "Verificar:"
echo "  ✓ Muestra: '1 épicas'"
echo "  ✓ Muestra badge: '📋 1 pendiente' (amarillo)"
echo "  ✓ Si overdue_count > 0, muestra: '⏰ X retrasados' (rojo pulsante)"
echo "  ✓ Si ambos = 0, muestra: '✓ Todo al día' (verde)"
echo ""
echo "✅ PASS: Si todo aparece, FIX-004 funciona"

# ═════════════════════════════════════════════════════════════════════
# RESUMEN FINAL
# ═════════════════════════════════════════════════════════════════════

echo ""
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  CHECKLIST DE VALIDACIÓN COMPLETADO                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "☐ FIX-001: Atomicidad en reorder (order_index nunca duplicado)"
echo "☐ FIX-002: Validación cross-app (movimiento rechazado)"
echo "☐ FIX-003: Conteos reales (epic_count, pending_count, overdue_count)"
echo "☐ FIX-004: Badges dinámicos (visibles en sidebar)"
echo ""
echo "Todos PASSED → Listo para producción ✅"
echo ""

