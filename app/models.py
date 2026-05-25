from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base
import datetime

class RoutineTemplate(Base):
    """Modelo de rotina com tipos de recorrência."""
    __tablename__ = "routine_templates"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    recurrence_type = Column(String)  # Ex: "daily", "weekly", "monthly", "weekdays"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Task(Base):
    """Log diário de execução de tarefas."""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    
    # Controle de conclusão
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Auditoria
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Coluna data para registrar o log em uma data específica
    date = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d"))