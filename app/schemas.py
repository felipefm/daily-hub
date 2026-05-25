from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ==================== ROUTINE TEMPLATE ====================

class RoutineTemplateBase(BaseModel):
    """Schema base para Routine Template."""
    title: str
    recurrence_type: str  # Ex: "daily", "weekly", "monthly", "weekdays"


class RoutineTemplateCreate(RoutineTemplateBase):
    """Schema para criação de Routine Template."""
    pass


class RoutineTemplateUpdate(BaseModel):
    """Schema para edição de Routine Template."""
    title: Optional[str] = None
    recurrence_type: Optional[str] = None


class RoutineTemplateResponse(RoutineTemplateBase):
    """Schema de resposta para Routine Template."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== TASK ====================

class TaskBase(BaseModel):
    """Schema base para Task (log diário)."""
    title: str
    date: Optional[str] = None  # Se não enviar, assumimos "hoje"
    description: Optional[str] = None


class TaskCreate(TaskBase):
    """Schema para criação de Task."""
    pass


class TaskUpdate(BaseModel):
    """Schema para edição de Task."""
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    date: Optional[str] = None


class TaskResponse(TaskBase):
    """Schema de resposta para Task."""
    id: int
    is_completed: bool
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AIRequest(BaseModel):
    prompt: Optional[str] = "Faça um resumo dos últimos 7 dias e destaque pontos fortes e fracos."