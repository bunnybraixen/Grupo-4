# Trabajo Futuro

Este documento contiene ideas, características y planes que fueron propuestos durante los sprints iniciales de desarrollo pero que fueron pospuestos, perdieron prioridad, o se identificaron como mejoras futuras.

## Características y Mejoras

1. **Analíticas Avanzadas y Reportes (S8)**
   - **Gráficos Burndown**: Implementar un gráfico de líneas que muestre el progreso real vs. ideal de una Épica a lo largo del tiempo.
   - **KPIs de Rendimiento**: Calcular índices de eficiencia, bloqueo y rotación (tickets completados/horas trabajadas, preguntas planteadas/tickets procesados, redirecciones/tickets asignados) con indicadores visuales (verde/amarillo/rojo).
   - **Exportación a PDF/CSV**: Permitir exportar los dashboards de analíticas a PDF (resumen visual) y CSV (tabla de rendimiento) directamente desde el navegador.

2. **Internacionalización y Accesibilidad (S8, S10)**
   - **Soporte Multi-idioma (i18n)**: Externalizar por completo todos los textos hacia archivos JSON soportando Español, Inglés, Francés, Alemán y Portugués.
   - **Autotraducción de Documentos**: Integración con APIs (DeepL/Google Translate) para permitir la traducción con un clic de documentos subidos o markdown.
   - **Cumplimiento WCAG AA**: Navegación completa por teclado, pruebas con lectores de pantalla y relaciones de contraste estrictas (4.5:1).

3. **Mejoras del Módulo Code & Docs (S8)**
   - **Vista de Repositorio por Proyecto**: Un dashboard para archivos específicos del proyecto, métricas de código y contribuidores.
   - **Subida de Archivos con Previsualizaciones**: Soportar la subida de `.js`, `.ts`, `.py`, `.md`, `.pdf`, `.docx` con previsualizaciones markdown integradas y visores de PDF.

4. **Preferencias de Usuario e Interfaz (S9)**
   - **Modo Oscuro**: Implementar un tema oscuro con transiciones suaves, persistiendo la preferencia del usuario en el backend y `localStorage`.
   - **Panel de Configuración de Usuario**: Una página completa de ajustes de perfil para avatares, zonas horarias, preferencias de notificaciones y temas.

## Riesgos Identificados y Deuda Técnica a Monitorear

- **Complejidad del Drag & Drop**: Monitorear problemas de rendimiento y sincronización de estados al arrastrar tickets entre columnas.
- **Consistencia de la Máquina de Estados**: Asegurar que las ediciones concurrentes no rompan las transiciones de estado de los tickets (TODO -> IN_PROGRESS -> DONE / BLOCKED_QUESTION / REDIRECTED).
- **Estabilidad de WebSocket**: La lógica de reconexión y los latidos (heartbeat de 30s) deben ser robustos en producción para evitar notificaciones perdidas.
- **Rendimiento Analítico de Consultas**: A medida que los datos crecen, monitorear las consultas pesadas. Considerar el uso de vistas materializadas para los dashboards complejos.
