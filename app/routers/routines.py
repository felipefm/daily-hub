from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import get_db

# Cria o roteador baseando-se no prefixo /routines
router = APIRouter(prefix="/routines", tags=["Rotinas"])

# --- CRUD DE TEMPLATES DE HÁBITOS ---

@router.post("/", response_model=schemas.RoutineTemplateResponse)
def create_routine(routine: schemas.RoutineTemplateCreate, db: Session = Depends(get_db)):
    """Cria um novo template de hábito/rotina."""
    db_routine = models.RoutineTemplate(**routine.model_dump())
    db.add(db_routine)
    db.commit()
    db.refresh(db_routine)
    return db_routine


@router.get("/", response_model=List[schemas.RoutineTemplateResponse])
def list_routines(db: Session = Depends(get_db)):
    """Lista todos os templates de hábitos/rotinas."""
    routines = db.query(models.RoutineTemplate).all()
    return routines


@router.delete("/{routine_id}")
def delete_routine(routine_id: int, db: Session = Depends(get_db)):
    """Deleta um template de hábito/rotina."""
    db_routine = db.query(models.RoutineTemplate).filter(
        models.RoutineTemplate.id == routine_id
    ).first()
    
    if not db_routine:
        raise HTTPException(status_code=404, detail="Rotina não encontrada")
    
    db.delete(db_routine)
    db.commit()
    return {"message": "Rotina deletada com sucesso"}


@router.put("/{routine_id}", response_model=schemas.RoutineTemplateResponse)
def update_routine(
    routine_id: int, 
    routine_update: schemas.RoutineTemplateUpdate, 
    db: Session = Depends(get_db)
):
    """Atualiza um template de hábito/rotina existente."""
    db_routine = db.query(models.RoutineTemplate).filter(
        models.RoutineTemplate.id == routine_id
    ).first()
    
    if not db_routine:
        raise HTTPException(status_code=404, detail="Rotina não encontrada")
    
    update_data = routine_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_routine, key, value)
        
    db.commit()
    db.refresh(db_routine)
    return db_routine
