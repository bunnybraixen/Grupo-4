# Esquemas de validación para operaciones relacionadas con analítica
# Estos esquemas contienen métricas y datos de desempeño del equipo y tickets

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


class UserPerformance(BaseModel):
    """
    Esquema con métricas de desempeño de un usuario individual.
    Contiene estadísticas sobre su actividad y eficiencia en el sistema.
    
    Atributos:
        user_id: UUID del usuario
        user_name: Nombre completo del usuario
        avatar_url: URL de la imagen de perfil del usuario (opcional)
        tickets_processed: Total de tickets procesados por el usuario
        tickets_completed: Total de tickets completados exitosamente
        questions_raised: Total de preguntas formuladas
        redirections: Total de tickets redirigidos a otros usuarios
        avg_time_hours: Tiempo promedio en horas para completar un ticket
        efficiency: Índice de eficiencia (0-100) basado en tickets completados vs asignados
        blocking_index: Índice de bloqueo (0-100) indicando cuántos tickets se quedan atascados
        churn_index: Índice de desgaste (0-100) indicando rotación de tickets sin completar
    """
    user_id: UUID
    user_name: str
    avatar_url: Optional[str] = None
    tickets_processed: int
    tickets_completed: int
    questions_raised: int
    redirections: int
    avg_time_hours: float
    efficiency: float
    blocking_index: float
    churn_index: float

    @field_validator("tickets_processed", "tickets_completed", "questions_raised", "redirections")
    @classmethod
    def validate_non_negative(cls, v: int) -> int:
        """
        Valida que las métricas de conteo sean números no negativos.
        
        Args:
            v: Valor a validar
            
        Returns:
            El valor validado
            
        Raises:
            ValueError: Si el valor es negativo
        """
        if v < 0:
            raise ValueError("El conteo no puede ser negativo")
        return v

    @field_validator("efficiency", "blocking_index", "churn_index")
    @classmethod
    def validate_percentage_range(cls, v: float) -> float:
        """
        Valida que los índices porcentuales estén entre 0 y 100.
        
        Args:
            v: Valor a validar
            
        Returns:
            El valor validado
            
        Raises:
            ValueError: Si el valor no está en el rango válido
        """
        if not 0 <= v <= 100:
            raise ValueError("El índice debe estar entre 0 y 100")
        return v


class HeatmapEntry(BaseModel):
    """
    Esquema para datos de mapa de calor de actividad de usuario.
    Representa la actividad del usuario por cada día de la semana.
    
    Atributos:
        user_id: UUID del usuario
        user_name: Nombre completo del usuario
        data: Lista de 7 enteros (uno para cada día: lunes a domingo) indicando nivel de actividad
    """
    user_id: UUID
    user_name: str
    data: list[int]

    @field_validator("data")
    @classmethod
    def validate_heatmap_data(cls, v: list[int]) -> list[int]:
        """
        Valida que el mapa de calor tenga exactamente 7 elementos (uno por día).
        
        Args:
            v: Lista de datos a validar
            
        Returns:
            La lista validada
            
        Raises:
            ValueError: Si la lista no tiene exactamente 7 elementos
        """
        if len(v) != 7:
            raise ValueError("El mapa de calor debe tener exactamente 7 valores (uno por día)")
        
        # Validar que todos los valores sean no negativos
        for value in v:
            if value < 0:
                raise ValueError("Los valores del mapa de calor no pueden ser negativos")
        
        return v


class BurndownPoint(BaseModel):
    """
    Esquema para un punto en un gráfico de deuda de trabajo (burndown).
    Representa el estado de trabajo pendiente en una fecha específica.
    
    Atributos:
        date: Fecha del punto en formato string (YYYY-MM-DD)
        remaining: Número de unidades de trabajo pendientes en esa fecha
    """
    date: str
    remaining: int

    @field_validator("remaining")
    @classmethod
    def validate_remaining_non_negative(cls, v: int) -> int:
        """
        Valida que el trabajo pendiente sea no negativo.
        
        Args:
            v: Valor a validar
            
        Returns:
            El valor validado
            
        Raises:
            ValueError: Si el valor es negativo
        """
        if v < 0:
            raise ValueError("El trabajo pendiente no puede ser negativo")
        return v


class BurndownData(BaseModel):
    """
    Esquema con datos de gráfico de deuda de trabajo para una épica.
    Contiene el progreso ideal versus el progreso real.
    
    Atributos:
        epic_id: UUID de la épica
        epic_title: Título de la épica
        ideal: Lista de puntos de deuda de trabajo ideal (progresión teórica)
        actual: Lista de puntos de deuda de trabajo real (progresión observada)
    """
    epic_id: UUID
    epic_title: str
    ideal: list[BurndownPoint]
    actual: list[BurndownPoint]

    @field_validator("ideal", "actual")
    @classmethod
    def validate_burndown_points_not_empty(cls, v: list[BurndownPoint]) -> list[BurndownPoint]:
        """
        Valida que las listas de puntos de deuda de trabajo no estén vacías.
        
        Args:
            v: Lista a validar
            
        Returns:
            La lista validada
            
        Raises:
            ValueError: Si la lista está vacía
        """
        if not v or len(v) == 0:
            raise ValueError("La lista de puntos de deuda de trabajo no puede estar vacía")
        return v


class AnalyticsSummary(BaseModel):
    """
    Esquema con resumen general de analíticas de un equipo o aplicación.
    Proporciona métricas consolidadas y cambios respecto a período anterior.
    
    Atributos:
        total_tickets: Número total de tickets
        completed_tickets: Número de tickets completados
        blocked_tickets: Número de tickets bloqueados
        avg_time_hours: Tiempo promedio en horas para completar tickets
        week_change: Diccionario con cambios porcentuales respecto a la semana anterior
            - total: Cambio porcentual en total de tickets
            - completed: Cambio porcentual en tickets completados
            - blocked: Cambio porcentual en tickets bloqueados
            - avgTime: Cambio porcentual en tiempo promedio
    """
    total_tickets: int
    completed_tickets: int
    blocked_tickets: int
    avg_time_hours: float
    week_change: dict = {
        "total": 0.0,
        "completed": 0.0,
        "blocked": 0.0,
        "avgTime": 0.0,
    }

    @field_validator("total_tickets", "completed_tickets", "blocked_tickets")
    @classmethod
    def validate_tickets_non_negative(cls, v: int) -> int:
        """
        Valida que los conteos de tickets sean no negativos.
        
        Args:
            v: Valor a validar
            
        Returns:
            El valor validado
            
        Raises:
            ValueError: Si el valor es negativo
        """
        if v < 0:
            raise ValueError("El conteo de tickets no puede ser negativo")
        return v

    @field_validator("avg_time_hours")
    @classmethod
    def validate_avg_time_positive(cls, v: float) -> float:
        """
        Valida que el tiempo promedio sea positivo.
        
        Args:
            v: Valor a validar
            
        Returns:
            El valor validado
            
        Raises:
            ValueError: Si el valor es negativo
        """
        if v < 0:
            raise ValueError("El tiempo promedio no puede ser negativo")
        return v
