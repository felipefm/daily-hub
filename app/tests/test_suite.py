"""
SUITE DE TESTES - DAILY-HUB

Suite completa de testes para a aplicação Daily-HUB com logging detalhado.
Cada teste registra:
- Início da execução
- Sucesso ou Falha
- Localização exata do erro
- Dados relevantes

Executar com: pytest app/tests/test_suite.py -v --tb=short
"""

import pytest
import logging
from datetime import datetime, timedelta
from io import BytesIO
import json
import sys
import traceback

logger = logging.getLogger(__name__)

# ================== TESTES DE ROTINAS (ROUTINES) ==================

class TestRoutines:
    """Testes para CRUD de Rotinas/Hábitos."""

    def test_create_routine_success(self, client, test_logger, db):
        """
        ✓ Teste: Criar uma nova rotina com sucesso
        - Objetivo: Verificar se uma rotina é criada corretamente
        """
        test_logger.info("🔄 INICIANDO: test_create_routine_success")
        
        try:
            routine_data = {
                "title": "Meditação Diária",
                "recurrence_type": "daily"
            }
            
            response = client.post("/routines/", json=routine_data)
            
            assert response.status_code == 200, f"Status inválido: {response.status_code}"
            data = response.json()
            
            assert data["title"] == "Meditação Diária", "Título não coincide"
            assert data["recurrence_type"] == "daily", "Tipo de recorrência não coincide"
            assert "id" in data, "ID não foi retornado"
            assert "created_at" in data, "Data de criação não foi retornada"
            
            test_logger.info("✅ SUCESSO: Rotina criada com sucesso")
            test_logger.info(f"   - ID: {data['id']}")
            test_logger.info(f"   - Título: {data['title']}")
            test_logger.info(f"   - Resposta: {data}")
            
        except AssertionError as e:
            test_logger.error(f"❌ ERRO: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            test_logger.error(f"❌ ERRO INESPERADO: {str(e)}", exc_info=True)
            raise

    def test_create_routine_invalid_data(self, client, test_logger):
        """
        ✓ Teste: Rejeitar rotina com dados inválidos
        - Objetivo: Verificar validação de dados de entrada
        """
        test_logger.info("🔄 INICIANDO: test_create_routine_invalid_data")
        
        try:
            routine_data = {
                "title": "",  # Título vazio deve ser rejeitado
                "recurrence_type": "daily"
            }
            
            response = client.post("/routines/", json=routine_data)
            
            # Esperamos erro de validação
            assert response.status_code >= 400, f"Deveria rejeitar entrada inválida, recebeu: {response.status_code}"
            
            test_logger.info("✅ SUCESSO: Dados inválidos foram rejeitados corretamente")
            test_logger.info(f"   - Status Code: {response.status_code}")
            
        except AssertionError as e:
            test_logger.error(f"❌ ERRO: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            test_logger.error(f"❌ ERRO INESPERADO: {str(e)}", exc_info=True)
            raise

    def test_list_routines(self, client, test_logger):
        """
        ✓ Teste: Listar todas as rotinas
        - Objetivo: Verificar recuperação de todas as rotinas
        """
        test_logger.info("🔄 INICIANDO: test_list_routines")
        
        try:
            # Cria 3 rotinas
            routines_data = [
                {"title": "Exercício", "recurrence_type": "daily"},
                {"title": "Leitura", "recurrence_type": "weekdays"},
                {"title": "Planejamento Semanal", "recurrence_type": "weekly"}
            ]
            
            created_ids = []
            for routine_data in routines_data:
                response = client.post("/routines/", json=routine_data)
                assert response.status_code == 200
                created_ids.append(response.json()["id"])
                test_logger.info(f"   - Criada rotina: {routine_data['title']} (ID: {created_ids[-1]})")
            
            # Lista todas as rotinas
            response = client.get("/routines/")
            assert response.status_code == 200, f"Status inválido ao listar: {response.status_code}"
            
            routines = response.json()
            assert len(routines) >= 3, f"Esperava pelo menos 3 rotinas, encontrou {len(routines)}"
            
            test_logger.info("✅ SUCESSO: Rotinas listadas com sucesso")
            test_logger.info(f"   - Total de rotinas: {len(routines)}")
            test_logger.info(f"   - IDs criados: {created_ids}")
            
        except AssertionError as e:
            test_logger.error(f"❌ ERRO: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            test_logger.error(f"❌ ERRO INESPERADO: {str(e)}", exc_info=True)
            raise

    def test_update_routine(self, client, test_logger):
        """
        ✓ Teste: Atualizar uma rotina existente
        - Objetivo: Verificar edição de rotinas
        """
        test_logger.info("🔄 INICIANDO: test_update_routine")
        
        try:
            # Cria rotina
            routine_data = {"title": "Yoga", "recurrence_type": "daily"}
            create_response = client.post("/routines/", json=routine_data)
            assert create_response.status_code == 200
            routine_id = create_response.json()["id"]
            test_logger.info(f"   - Rotina criada com ID: {routine_id}")
            
            # Atualiza rotina
            update_data = {"title": "Yoga Avançada", "recurrence_type": "weekdays"}
            update_response = client.put(f"/routines/{routine_id}", json=update_data)
            
            assert update_response.status_code == 200, f"Status inválido ao atualizar: {update_response.status_code}"
            updated_routine = update_response.json()
            
            assert updated_routine["title"] == "Yoga Avançada", "Título não foi atualizado"
            assert updated_routine["recurrence_type"] == "weekdays", "Recorrência não foi atualizada"
            
            test_logger.info("✅ SUCESSO: Rotina atualizada com sucesso")
            test_logger.info(f"   - Novo título: {updated_routine['title']}")
            test_logger.info(f"   - Nova recorrência: {updated_routine['recurrence_type']}")
            
        except AssertionError as e:
            test_logger.error(f"❌ ERRO: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            test_logger.error(f"❌ ERRO INESPERADO: {str(e)}", exc_info=True)
            raise

    def test_delete_routine(self, client, test_logger):
        """
        ✓ Teste: Deletar uma rotina
        - Objetivo: Verificar remoção de rotinas
        """
        test_logger.info("🔄 INICIANDO: test_delete_routine")
        
        try:
            # Cria rotina
            routine_data = {"title": "Limpeza", "recurrence_type": "weekly"}
            create_response = client.post("/routines/", json=routine_data)
            assert create_response.status_code == 200
            routine_id = create_response.json()["id"]
            test_logger.info(f"   - Rotina criada com ID: {routine_id}")
            
            # Deleta rotina
            delete_response = client.delete(f"/routines/{routine_id}")
            assert delete_response.status_code == 200, f"Status inválido ao deletar: {delete_response.status_code}"
            test_logger.info(f"   - Resposta do delete: {delete_response.json()}")
            
            # Verifica se foi deletada tentando recuperar
            list_response = client.get("/routines/")
            routines = list_response.json()
            routine_ids = [r["id"] for r in routines]
            
            assert routine_id not in routine_ids, "Rotina não foi deletada"
            
            test_logger.info("✅ SUCESSO: Rotina deletada com sucesso")
            test_logger.info(f"   - ID deletado: {routine_id}")
            
        except AssertionError as e:
            test_logger.error(f"❌ ERRO: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            test_logger.error(f"❌ ERRO INESPERADO: {str(e)}", exc_info=True)
            raise

    def test_delete_nonexistent_routine(self, client, test_logger):
        """
        ✓ Teste: Tentar deletar rotina inexistente
        - Objetivo: Verificar tratamento de erros 404
        """
        test_logger.info("🔄 INICIANDO: test_delete_nonexistent_routine")
        
        try:
            delete_response = client.delete("/routines/99999")
            
            assert delete_response.status_code == 404, f"Esperava 404, recebeu: {delete_response.status_code}"
            
            test_logger.info("✅ SUCESSO: Erro 404 retornado corretamente")
            test_logger.info(f"   - Resposta: {delete_response.json()}")
            
        except AssertionError as e:
            test_logger.error(f"❌ ERRO: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            test_logger.error(f"❌ ERRO INESPERADO: {str(e)}", exc_info=True)
            raise


# ================== TESTES DE TAREFAS (TASKS) ==================

class TestTasks:
    """Testes para CRUD de Tarefas."""

    def test_create_task_success(self, client, test_logger):
        """
        ✓ Teste: Criar uma nova tarefa com sucesso
        - Objetivo: Verificar se uma tarefa é criada corretamente
        """
        test_logger.info("🔄 INICIANDO: test_create_task_success")
        
        try:
            task_data = {
                "title": "Revisar código",
                "description": "Revisar o PR #123",
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            
            response = client.post("/tasks/", json=task_data)
            
            assert response.status_code == 200, f"Status inválido: {response.status_code}"
            data = response.json()
            
            assert data["title"] == "Revisar código"
            assert data["description"] == "Revisar o PR #123"
            assert data["is_completed"] == False, "Tarefa não deveria estar completa"
            assert "id" in data
            
            test_logger.info("✅ SUCESSO: Tarefa criada com sucesso")
            test_logger.info(f"   - ID: {data['id']}")
            test_logger.info(f"   - Título: {data['title']}")
            test_logger.info(f"   - Descompleta: {data['is_completed']}")
            
        except AssertionError as e:
            test_logger.error(f"❌ ERRO: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            test_logger.error(f"❌ ERRO INESPERADO: {str(e)}", exc_info=True)
            raise

    def test_list_tasks(self, client, test_logger):
        """
        ✓ Teste: Listar todas as tarefas
        - Objetivo: Verificar recuperação de tarefas
        """
        test_logger.info("🔄 INICIANDO: test_list_tasks")
        
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Cria 2 tarefas
            tasks_data = [
                {"title": "Tarefa 1", "description": "Desc 1", "date": today},
                {"title": "Tarefa 2", "description": "Desc 2", "date": today}
            ]
            
            for task_data in tasks_data:
                response = client.post("/tasks/", json=task_data)
                assert response.status_code == 200
                test_logger.info(f"   - Criada tarefa: {task_data['title']}")
            
            # Lista tarefas
            response = client.get("/tasks/")
            assert response.status_code == 200
            
            tasks = response.json()
            assert len(tasks) >= 2, f"Esperava pelo menos 2 tarefas, encontrou {len(tasks)}"
            
            test_logger.info("✅ SUCESSO: Tarefas listadas com sucesso")
            test_logger.info(f"   - Total de tarefas: {len(tasks)}")
            
        except AssertionError as e:
            test_logger.error(f"❌ ERRO: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            test_logger.error(f"❌ ERRO INESPERADO: {str(e)}", exc_info=True)
            raise

    def test_update_task(self, client, test_logger):
        """
        ✓ Teste: Atualizar uma tarefa
        - Objetivo: Verificar edição de tarefas
        """
        test_logger.info("🔄 INICIANDO: test_update_task")
        
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Cria tarefa
            task_data = {"title": "Tarefa Original", "date": today}
            create_response = client.post("/tasks/", json=task_data)
            assert create_response.status_code == 200
            task_id = create_response.json()["id"]
            test_logger.info(f"   - Tarefa criada com ID: {task_id}")
            
            # Atualiza tarefa
            update_data = {
                "title": "Tarefa Atualizada",
                "is_completed": True
            }
            update_response = client.put(f"/tasks/{task_id}", json=update_data)
            
            assert update_response.status_code == 200
            updated_task = update_response.json()
            
            assert updated_task["title"] == "Tarefa Atualizada"
            assert updated_task["is_completed"] == True
            assert updated_task["completed_at"] is not None, "Data de conclusão não foi registrada"
            
            test_logger.info("✅ SUCESSO: Tarefa atualizada com sucesso")
            test_logger.info(f"   - Novo título: {updated_task['title']}")
            test_logger.info(f"   - Completada: {updated_task['is_completed']}")
            test_logger.info(f"   - Data de conclusão: {updated_task['completed_at']}")
            
        except AssertionError as e:
            test_logger.error(f"❌ ERRO: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            test_logger.error(f"❌ ERRO INESPERADO: {str(e)}", exc_info=True)
            raise

    def test_delete_task(self, client, test_logger):
        """
        ✓ Teste: Deletar uma tarefa
        - Objetivo: Verificar remoção de tarefas
        """
        test_logger.info("🔄 INICIANDO: test_delete_task")
        
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Cria tarefa
            task_data = {"title": "Tarefa a Deletar", "date": today}
            create_response = client.post("/tasks/", json=task_data)
            assert create_response.status_code == 200
            task_id = create_response.json()["id"]
            test_logger.info(f"   - Tarefa criada com ID: {task_id}")
            
            # Deleta tarefa
            delete_response = client.delete(f"/tasks/{task_id}")
            assert delete_response.status_code == 200
            test_logger.info(f"   - Resposta do delete: {delete_response.json()}")
            
            test_logger.info("✅ SUCESSO: Tarefa deletada com sucesso")
            
        except AssertionError as e:
            test_logger.error(f"❌ ERRO: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            test_logger.error(f"❌ ERRO INESPERADO: {str(e)}", exc_info=True)
            raise

    def test_mark_incomplete_task(self, client, test_logger):
        """
        ✓ Teste: Marcar tarefa completa como incompleta
        - Objetivo: Verificar alteração de status
        """
        test_logger.info("🔄 INICIANDO: test_mark_incomplete_task")
        
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Cria e completa tarefa
            task_data = {"title": "Tarefa para Reverter", "date": today}
            create_response = client.post("/tasks/", json=task_data)
            task_id = create_response.json()["id"]
            
            client.put(f"/tasks/{task_id}", json={"is_completed": True})
            
            # Marca como incompleta
            revert_response = client.put(f"/tasks/{task_id}", json={"is_completed": False})
            
            assert revert_response.status_code == 200
            reverted_task = revert_response.json()
            
            assert reverted_task["is_completed"] == False
            assert reverted_task["completed_at"] is None, "Data de conclusão deveria ser None"
            
            test_logger.info("✅ SUCESSO: Tarefa revertida para incompleta")
            test_logger.info(f"   - Status: {reverted_task['is_completed']}")
            
        except AssertionError as e:
            test_logger.error(f"❌ ERRO: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            test_logger.error(f"❌ ERRO INESPERADO: {str(e)}", exc_info=True)
            raise


# ================== TESTES DE ANÁLISE (ANALYSIS) ==================

class TestAnalysis:
    """Testes para funcionalidade de análise semanal."""

    def test_analyze_week_no_routines(self, client, test_logger):
        """
        ✓ Teste: Analisar semana sem rotinas
        - Objetivo: Verificar comportamento quando não há rotinas
        """
        test_logger.info("🔄 INICIANDO: test_analyze_week_no_routines")
        
        try:
            response = client.post("/analyze-week")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "analysis" in data
            assert len(data["analysis"]) > 0
            
            test_logger.info("✅ SUCESSO: Análise sem rotinas funcionou")
            test_logger.info(f"   - Resposta: {data['analysis'][:100]}...")
            
        except AssertionError as e:
            test_logger.error(f"❌ ERRO: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            test_logger.error(f"❌ ERRO INESPERADO: {str(e)}", exc_info=True)
            raise

    def test_analyze_week_with_prompt(self, client, test_logger):
        """
        ✓ Teste: Analisar semana com prompt customizado
        - Objetivo: Verificar análise com prompt personalizado
        """
        test_logger.info("🔄 INICIANDO: test_analyze_week_with_prompt")
        
        try:
            custom_prompt = "Qual é minha taxa de produtividade?"
            
            response = client.post(
                "/analyze-week",
                json={"prompt": custom_prompt}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "analysis" in data
            
            test_logger.info("✅ SUCESSO: Análise com prompt customizado funcionou")
            test_logger.info(f"   - Prompt enviado: {custom_prompt}")
            
        except AssertionError as e:
            test_logger.error(f"❌ ERRO: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            test_logger.error(f"❌ ERRO INESPERADO: {str(e)}", exc_info=True)
            raise


# ================== TESTES DE CALENDÁRIO (CALENDAR) ==================

class TestCalendar:
    """Testes para funcionalidade de geração de calendários."""

    def test_generate_monthly_calendar(self, client, test_logger):
        """
        ✓ Teste: Gerar calendário mensal
        - Objetivo: Verificar geração de PDF mensal
        """
        test_logger.info("🔄 INICIANDO: test_generate_monthly_calendar")
        
        try:
            today = datetime.now()
            year = today.year
            month = today.month
            
            response = client.get(f"/calendar/monthly?year={year}&month={month}")
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/pdf"
            assert len(response.content) > 0, "PDF vazio"
            
            test_logger.info("✅ SUCESSO: Calendário mensal gerado com sucesso")
            test_logger.info(f"   - Mês: {month}/{year}")
            test_logger.info(f"   - Tamanho do PDF: {len(response.content)} bytes")
            
        except AssertionError as e:
            test_logger.error(f"❌ ERRO: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            test_logger.error(f"❌ ERRO INESPERADO: {str(e)}", exc_info=True)
            raise

    def test_generate_monthly_calendar_default(self, client, test_logger):
        """
        ✓ Teste: Gerar calendário mensal padrão (mês atual)
        - Objetivo: Verificar comportamento com parâmetros padrão
        """
        test_logger.info("🔄 INICIANDO: test_generate_monthly_calendar_default")
        
        try:
            response = client.get("/calendar/monthly")
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/pdf"
            assert len(response.content) > 0
            
            test_logger.info("✅ SUCESSO: Calendário mensal padrão gerado com sucesso")
            test_logger.info(f"   - Tamanho do PDF: {len(response.content)} bytes")
            
        except AssertionError as e:
            test_logger.error(f"❌ ERRO: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            test_logger.error(f"❌ ERRO INESPERADO: {str(e)}", exc_info=True)
            raise

    def test_generate_annual_calendar(self, client, test_logger):
        """
        ✓ Teste: Gerar calendário anual
        - Objetivo: Verificar geração de PDF anual
        """
        test_logger.info("🔄 INICIANDO: test_generate_annual_calendar")
        
        try:
            year = datetime.now().year
            
            response = client.get(f"/calendar/annual?year={year}")
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/pdf"
            assert len(response.content) > 0
            
            test_logger.info("✅ SUCESSO: Calendário anual gerado com sucesso")
            test_logger.info(f"   - Ano: {year}")
            test_logger.info(f"   - Tamanho do PDF: {len(response.content)} bytes")
            
        except AssertionError as e:
            test_logger.error(f"❌ ERRO: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            test_logger.error(f"❌ ERRO INESPERADO: {str(e)}", exc_info=True)
            raise

    def test_generate_annual_calendar_default(self, client, test_logger):
        """
        ✓ Teste: Gerar calendário anual padrão (ano atual)
        - Objetivo: Verificar comportamento com parâmetros padrão
        """
        test_logger.info("🔄 INICIANDO: test_generate_annual_calendar_default")
        
        try:
            response = client.get("/calendar/annual")
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/pdf"
            assert len(response.content) > 0
            
            test_logger.info("✅ SUCESSO: Calendário anual padrão gerado com sucesso")
            test_logger.info(f"   - Tamanho do PDF: {len(response.content)} bytes")
            
        except AssertionError as e:
            test_logger.error(f"❌ ERRO: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            test_logger.error(f"❌ ERRO INESPERADO: {str(e)}", exc_info=True)
            raise


# ================== TESTES DE ROOT ==================

class TestRoot:
    """Testes para endpoint raiz."""

    def test_read_root(self, client, test_logger):
        """
        ✓ Teste: Acessar página raiz
        - Objetivo: Verificar se a página HTML é servida
        """
        test_logger.info("🔄 INICIANDO: test_read_root")
        
        try:
            response = client.get("/")
            
            assert response.status_code == 200
            assert "text/html" in response.headers.get("content-type", "")
            
            test_logger.info("✅ SUCESSO: Página raiz acessada com sucesso")
            test_logger.info(f"   - Content-Type: {response.headers.get('content-type')}")
            
        except AssertionError as e:
            test_logger.error(f"❌ ERRO: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            test_logger.error(f"❌ ERRO INESPERADO: {str(e)}", exc_info=True)
            raise


# ================== TESTES DE BACKUP ==================

class TestBackup:
    """Testes para funcionalidade de backup."""

    def test_export_backup(self, client, test_logger):
        """
        ✓ Teste: Exportar backup do banco de dados
        - Objetivo: Verificar se o backup pode ser exportado
        """
        test_logger.info("🔄 INICIANDO: test_export_backup")
        
        try:
            response = client.get("/backup/export")
            
            # Pode ser 200 se o arquivo existe, ou 404 se não existe ainda
            assert response.status_code in [200, 404], f"Status inválido: {response.status_code}"
            
            if response.status_code == 200:
                assert len(response.content) > 0, "Arquivo vazio"
                test_logger.info("✅ SUCESSO: Backup exportado com sucesso")
                test_logger.info(f"   - Tamanho: {len(response.content)} bytes")
            else:
                test_logger.info("ℹ️  INFO: Arquivo de backup não existe (esperado em primeira execução)")
            
        except AssertionError as e:
            test_logger.error(f"❌ ERRO: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            test_logger.error(f"❌ ERRO INESPERADO: {str(e)}", exc_info=True)
            raise

    def test_import_backup_invalid_format(self, client, test_logger):
        """
        ✓ Teste: Rejeitar backup com formato inválido
        - Objetivo: Verificar validação do formato de arquivo
        """
        test_logger.info("🔄 INICIANDO: test_import_backup_invalid_format")
        
        try:
            # Tenta fazer upload de arquivo com extensão inválida
            invalid_file = BytesIO(b"invalid content")
            
            response = client.post(
                "/backup/import",
                files={"file": ("test.txt", invalid_file, "text/plain")}
            )
            
            assert response.status_code == 400, f"Esperava 400, recebeu: {response.status_code}"
            
            test_logger.info("✅ SUCESSO: Arquivo inválido foi rejeitado corretamente")
            test_logger.info(f"   - Resposta: {response.json()}")
            
        except AssertionError as e:
            test_logger.error(f"❌ ERRO: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            test_logger.error(f"❌ ERRO INESPERADO: {str(e)}", exc_info=True)
            raise


# ================== TESTES DE INTEGRAÇÃO ==================

class TestIntegration:
    """Testes de integração entre múltiplas funcionalidades."""

    def test_full_workflow(self, client, test_logger):
        """
        ✓ Teste: Fluxo completo de uso
        - Objetivo: Simular uso real da aplicação
        """
        test_logger.info("🔄 INICIANDO: test_full_workflow")
        
        try:
            # 1. Cria uma rotina
            routine_data = {"title": "Exercício", "recurrence_type": "daily"}
            routine_response = client.post("/routines/", json=routine_data)
            assert routine_response.status_code == 200
            routine = routine_response.json()
            test_logger.info(f"   ✓ Etapa 1: Rotina criada (ID: {routine['id']})")
            
            # 2. Cria tarefas
            today = datetime.now().strftime("%Y-%m-%d")
            task_data = {"title": "Exercício", "date": today}
            task_response = client.post("/tasks/", json=task_data)
            assert task_response.status_code == 200
            task = task_response.json()
            test_logger.info(f"   ✓ Etapa 2: Tarefa criada (ID: {task['id']})")
            
            # 3. Completa a tarefa
            update_response = client.put(f"/tasks/{task['id']}", json={"is_completed": True})
            assert update_response.status_code == 200
            test_logger.info("   ✓ Etapa 3: Tarefa completada")
            
            # 4. Lista tarefas
            list_response = client.get("/tasks/")
            assert list_response.status_code == 200
            assert len(list_response.json()) >= 1
            test_logger.info(f"   ✓ Etapa 4: Tarefas listadas ({len(list_response.json())} encontradas)")
            
            # 5. Gera calendário
            cal_response = client.get("/calendar/monthly")
            assert cal_response.status_code == 200
            test_logger.info("   ✓ Etapa 5: Calendário gerado com sucesso")
            
            test_logger.info("✅ SUCESSO: Fluxo completo executado sem erros")
            
        except AssertionError as e:
            test_logger.error(f"❌ ERRO: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            test_logger.error(f"❌ ERRO INESPERADO: {str(e)}", exc_info=True)
            raise
