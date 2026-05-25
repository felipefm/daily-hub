from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import datetime
from datetime import timedelta
import requests
import os
import json
 
import models
import schemas
from database import get_db

router = APIRouter(tags=["IA Analysis"])

LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://192.168.0.10:1234/v1")

def format_date_pt(date_obj: datetime.date) -> str:
    """Formata uma data para o português do Brasil sem depender de locale."""
    dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    
    dia_semana = dias[date_obj.weekday()]
    dia_mes = date_obj.day
    mes = meses[date_obj.month - 1]
    ano = date_obj.year
    return f"{dia_semana}, {dia_mes} de {mes} de {ano}"

def is_task_due(rec_type: str, date_to_check: datetime.date) -> bool:
    """Verifica se uma tarefa recorrente deve ser executada em uma data específica."""
    dia_da_semana = date_to_check.weekday()  # Segunda-feira é 0 e Domingo é 6
    
    if rec_type == "daily": return True
    if rec_type == "weekdays" and dia_da_semana < 5: return True
    if rec_type == "weekend" and dia_da_semana >= 5: return True
    if rec_type == "saturday" and dia_da_semana == 5: return True
    if rec_type == "sunday" and dia_da_semana == 6: return True
    if rec_type == "weekly" and dia_da_semana == 0: return True # Assume que tarefas semanais são na Segunda
    if rec_type == "monthly" and date_to_check.day == 1: return True
    
    return False

@router.post("/analyze-week")
def analyze_week(request: Optional[schemas.AIRequest] = None, db: Session = Depends(get_db)):
    # Garante que mesmo chamadas sem body (do front-end atual) continuem funcionando
    if request is None:
        request = schemas.AIRequest()

    # 1. Busca todas as definições de tarefas recorrentes (rotinas)
    templates = db.query(models.RoutineTemplate.title, models.RoutineTemplate.recurrence_type).all()

    if not templates:
        return {"analysis": "Nenhuma tarefa recorrente (rotina) foi configurada. Crie algumas para analisar sua consistência."}

    analysis_details = []
    total_esperadas = 0
    total_concluidas = 0
    today = datetime.date.today()

    # 2. Itera pelos últimos 7 dias para verificar a aderência
    for i in range(7):
        current_date = today - timedelta(days=i)
        day_str = format_date_pt(current_date)
        day_summary = {"date": day_str, "tasks": []}
        
        # 3. Para cada dia, verifica quais rotinas eram esperadas
        for title, rec_type in templates:
            if is_task_due(rec_type, current_date):
                total_esperadas += 1
                
                # 4. Verifica o status real da tarefa no banco de dados
                target_date_str = current_date.strftime("%Y-%m-%d")
                
                task_instance = db.query(models.Task).filter(
                    models.Task.title == title,
                    models.Task.date == target_date_str
                ).first()

                status = "Faltante"
                if task_instance:
                    if task_instance.is_completed:
                        status = "Concluída"
                        total_concluidas += 1
                    else:
                        status = "Pendente"
                
                day_summary["tasks"].append(f"- **{title}** ({rec_type}): *{status}*")

        if day_summary["tasks"]:
            analysis_details.append(day_summary)

    if total_esperadas == 0:
        return {"analysis": "Nenhuma de suas rotinas estava agendada para os últimos 7 dias."}

    taxa_aderencia = (total_concluidas / total_esperadas) * 100

    # Estruturando os dados de forma legível para o LLM
    dados_tarefas = {
        "metricas": {
            "total_esperadas": total_esperadas,
            "total_concluidas": total_concluidas,
            "taxa_aderencia": f"{taxa_aderencia:.1f}%"
        },
        "relatorio_diario": list(reversed(analysis_details)) # Mantém a ordem do mais antigo pro mais recente
    }

    # 5. Monta o prompt dinâmico final
    prompt = f"{request.prompt}\n\nDados das tarefas em JSON:\n{json.dumps(dados_tarefas, ensure_ascii=False, indent=2)}"

    try:
        url = f"{LM_STUDIO_URL}/chat/completions"
        payload = {
            "messages": [
                {"role": "system", "content": "Você é um mentor de produtividade e disciplina, focado em analisar a consistência de rotinas."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4096
        }
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        dados = response.json()
        return {"analysis": dados["choices"][0]["message"]["content"]}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão com o LM Studio: {str(e)}")