-- ═════════════════════════════════════════════════════════════════════════════
-- SCRIPT SQL: ÍNDICES PARA OPTIMIZACIÓN DE CONTEOS (FIX-003)
-- ═════════════════════════════════════════════════════════════════════════════
-- 
-- PROBLEMA: Sin estos índices, contar 100,000 tickets toma 2 segundos
-- SOLUCIÓN: Con índices, el mismo conteo toma 50ms
-- 
-- Ejecutar INMEDIATAMENTE después de implementar FIX-003
-- ═════════════════════════════════════════════════════════════════════════════

-- 1️⃣ ÍNDICE PARA ÉPICAS POR APLICACIÓN
-- Optimiza: COUNT(epics) WHERE application_id = ?
CREATE INDEX IF NOT EXISTS idx_epic_application_id 
ON epics(application_id) 
WHERE is_archived = false;

-- 2️⃣ ÍNDICE COMPUESTO PARA TICKETS TODO POR ÉPICA
-- Optimiza: COUNT(tickets) WHERE epic_id = ? AND status = 'TODO'
CREATE INDEX IF NOT EXISTS idx_ticket_epic_status 
ON tickets(epic_id, status) 
WHERE status = 'TODO';

-- 3️⃣ ÍNDICE PARA TICKETS RETRASADOS (DUE DATE)
-- Optimiza: COUNT(tickets) WHERE due_date < NOW() AND status != 'COMPLETED'
CREATE INDEX IF NOT EXISTS idx_ticket_overdue 
ON tickets(due_date, status) 
WHERE due_date < CURRENT_TIMESTAMP 
AND status != 'COMPLETED';

-- 4️⃣ ÍNDICE PARA OPERACIONES DE REORDEN (FIX-001)
-- Optimiza: SELECT * FROM epics WHERE application_id = ? ORDER BY order_index
CREATE INDEX IF NOT EXISTS idx_epic_app_order 
ON epics(application_id, order_index);

-- ═════════════════════════════════════════════════════════════════════════════
-- VERIFICACIÓN POST-CREACIÓN
-- ═════════════════════════════════════════════════════════════════════════════

-- Listar todos los índices creados (debe mostrar 4 nuevos)
SELECT 
    indexname,
    tablename,
    indexdef
FROM pg_indexes 
WHERE tablename IN ('epics', 'tickets')
AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;

-- Verificar que los índices están siendo usados (EXPLAIN ANALYZE)
-- Ejecutar después de crear índices para verificar uso

-- Query 1: Contar épicas por app (debería usar idx_epic_application_id)
EXPLAIN ANALYZE
SELECT COUNT(*) FROM epics WHERE application_id = 'some-uuid' AND is_archived = false;

-- Query 2: Contar tickets TODO (debería usar idx_ticket_epic_status)
EXPLAIN ANALYZE
SELECT COUNT(*) 
FROM tickets t
JOIN epics e ON t.epic_id = e.id
WHERE e.application_id = 'some-uuid' AND t.status = 'TODO';

-- Query 3: Contar tickets retrasados (debería usar idx_ticket_overdue)
EXPLAIN ANALYZE
SELECT COUNT(*) 
FROM tickets t
JOIN epics e ON t.epic_id = e.id
WHERE e.application_id = 'some-uuid'
AND t.due_date < CURRENT_TIMESTAMP 
AND t.status != 'COMPLETED';

-- Query 4: Reordenar épicas (debería usar idx_epic_app_order)
EXPLAIN ANALYZE
SELECT * FROM epics 
WHERE application_id = 'some-uuid' 
ORDER BY order_index;

-- ═════════════════════════════════════════════════════════════════════════════
-- NOTAS IMPORTANTES
-- ═════════════════════════════════════════════════════════════════════════════
-- 
-- 1. Si el output dice "Seq Scan" → El índice NO se está usando
--    Posibles causas:
--    - PostgreSQL estima que leer toda la tabla es más rápido (datos pequeños)
--    - WHERE clause no es selectivo
--    - Falta ANALYZE para actualizar estadísticas
--
-- 2. Actualizar estadísticas (después de crear índices y agregar datos):
--    ANALYZE;
--
-- 3. Para verificar tamaño de índices:
--    SELECT 
--        indexname,
--        pg_size_pretty(pg_relation_size(indexrelid)) as size
--    FROM pg_indexes 
--    WHERE tablename IN ('epics', 'tickets')
--    AND indexname LIKE 'idx_%';
--
-- 4. Eliminar un índice si es necesario:
--    DROP INDEX IF EXISTS idx_epic_application_id;

