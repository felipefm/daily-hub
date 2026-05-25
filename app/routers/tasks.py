from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import datetime

import models
import schemas
from database import get_db

# Cria o roteador baseando-se no prefixo /tasks
router = APIRouter(prefix="/tasks", tags=["Tarefas"])

# --- MOTOR DE RECORRÊNCIA ---
def process_recurring_tasks(db: Session):
    hoje = datetime.date.today()
    data_hoje_str = hoje.strftime("%Y-%m-%d")
    
    # Consulta todos os templates de rotina (hábitos)
    routine_templates = db.query(models.RoutineTemplate).all()
    
    for template in routine_templates:
        criar_hoje = False
        dia_da_semana = hoje.weekday()
        rec_type = template.recurrence_type
        
        # Verifica se o hábito deve ser feito hoje
        if rec_type == 'daily':
            criar_hoje = True
        elif rec_type == 'monthly':
            criar_hoje = (hoje.day == 1)
        else:
            # Para dias específicos como '0,2,4' (0=Seg, 6=Dom)
            dias_selecionados = rec_type.split(',')
            if str(dia_da_semana) in dias_selecionados:
                criar_hoje = True
        
        if criar_hoje:
            # Verifica se já existe uma Task com esse título na data de hoje
            existe_hoje = db.query(models.Task).filter(
                models.Task.title == template.title,
                models.Task.date == data_hoje_str
            ).first()
            
            # Se não existir, cria uma nova Task
            if not existe_hoje:
                nova_tarefa = models.Task(
                    title=template.title,
                    date=data_hoje_str,
                    created_at=datetime.datetime.utcnow()
                )
                db.add(nova_tarefa)
    
    db.commit()

# --- CRUD DE TAREFAS ---
@router.post("/", response_model=schemas.TaskResponse)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/", response_model=List[schemas.TaskResponse])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    process_recurring_tasks(db)
    
    # Removemos as variáveis de "hoje" e o ".filter()"
    tasks = db.query(models.Task).order_by(models.Task.created_at.desc()).offset(skip).limit(limit).all()
    
    return tasks

@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task: raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    update_data = task_update.model_dump(exclude_unset=True)
    if update_data.get("is_completed") and not db_task.is_completed:
        db_task.completed_at = datetime.datetime.utcnow()
    elif update_data.get("is_completed") is False:
        db_task.completed_at = None

    for key, value in update_data.items(): setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task: raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    db.delete(db_task)
    db.commit()
    return {"detail": "Tarefa excluída com sucesso"}