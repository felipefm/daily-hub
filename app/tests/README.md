# 🧪 TESTES - DAILY-HUB

Suite de testes abrangente para a aplicação Daily-HUB com logging detalhado.

## ⚡ Quick Start

### Instalação
```bash
pip install -r requirements-test.txt
```

### Executar Testes
```bash
# Todos os testes
pytest test_suite.py -v

# Apenas uma classe
pytest test_suite.py::TestTasks -v

# Com cobertura
pytest test_suite.py --cov
```

### Ver Logs
```
logs/test_results_*.log
```

## 📊 Cobertura

- ✅ Rotinas/Hábitos (CRUD)
- ✅ Tarefas (CRUD)
- ✅ Análise Semanal
- ✅ Calendários (Mensal/Anual)
- ✅ Backup (Import/Export)
- ✅ Integração Completa

## 📝 Funcionalidades dos Testes

### Logging Detalhado
Cada teste registra:
- ✓ Início da execução (`🔄 INICIANDO`)
- ✓ Sucessos (`✅ SUCESSO`)
- ✓ Erros com localização exata (`❌ ERRO`)
- ✓ Arquivo, linha e função do erro
- ✓ Dados relevantes da execução

### Exemplo de Log
```
[2024-05-26 14:30:22,123] - INFO - [test_suite.py:34] - test_create_routine_success() - 🔄 INICIANDO: test_create_routine_success
[2024-05-26 14:30:22,456] - INFO - [test_suite.py:47] - test_create_routine_success() - ✅ SUCESSO: Rotina criada com sucesso
[2024-05-26 14:30:22,457] - INFO - [test_suite.py:48] - test_create_routine_success() - ID: 1
[2024-05-26 14:30:22,458] - INFO - [test_suite.py:49] - test_create_routine_success() - Título: Meditação Diária
```

## 📂 Estrutura

```
tests/
├── __init__.py              # Pacote Python
├── conftest.py              # Configuração pytest + fixtures
├── test_suite.py            # Suite de testes (450+ linhas)
├── requirements-test.txt    # Dependências
├── README.md                # Este arquivo
└── logs/                    # Logs gerados
```

## 🔍 Filtrar Logs

```bash
# Ver apenas sucessos
grep "✅ SUCESSO" logs/test_results_*.log

# Ver apenas erros
grep "❌ ERRO" logs/test_results_*.log

# Ver início de testes
grep "🔄 INICIANDO" logs/test_results_*.log
```

## 📖 Documentação Completa

Ver [TESTING.md](../TESTING.md) na raiz do projeto para documentação completa com:
- Guia de instalação
- Todos os comandos
- Interpretação de erros
- Troubleshooting
- Métricas de qualidade

## ❓ Dúvidas?

Veja [TESTING.md](../TESTING.md) - Seção "Troubleshooting"

---

**Suite de Testes - Daily-HUB v1.0**
