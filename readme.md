# Daily-HUB

O Daily-HUB é uma aplicação de gerenciamento de tarefas pessoais, projetada para ser um "hub" central para o planejamento e acompanhamento de rotinas diárias. A ferramenta combina um sistema de tarefas tradicional com funcionalidades avançadas, como análise de produtividade por IA, geração de calendários para impressão e um robusto sistema de backup.

A interface é limpa, moderna e responsiva, com suporte a tema claro e escuro, e foi construída como um Progressive Web App (PWA), permitindo sua "instalação" em dispositivos móveis e desktops para uma experiência mais nativa.

## Funcionalidades Principais

Atualmente, o Daily-HUB conta com as seguintes funcionalidades:

#### 1. Interface Avançada e Gerenciamento de Tarefas
- **Slider Contínuo de Datas**: Controlado por `renderDateSlider()` e `initSliderDesktop()`, substitui as antigas abas. Permite navegar com arraste ou scroll. O estado atual é atualizado por `selectDate()`.
- **Indicadores Visuais em Tempo Real**: Integrado ao `renderDateSlider()`, lê o array global `globalTasks` para desenhar pontos em dias com pendências e destacar sábados e domingos em vermelho.
- **Criação e Edição Inline**: Novos envios usam o event listener principal de `#task-form`. A edição rápida é aberta por `toggleEditTask()` e salva via `saveTask()`.
- **Conclusão de Tarefas**: O clique no checkbox chama `toggleTask()`, que realiza um PUT no backend e atualiza a interface re-executando `loadTasks()`.

#### 2. Motor de Recorrência
- **Criação Automática**: O backend usa `process_recurring_tasks` para ler as configurações de rotina (selecionadas no front-end através de `createDaySelectorHTML()`) e criar as instâncias diárias.
- **Tipos de Recorrência**: Suporte diário, mensal e dias customizados na semana (sendo as lógicas lidas e validadas por `isActiveToday()`).

#### 3. Matriz de Hábitos (Habit Tracker)
- **Renderização Dinâmica**: A função `renderHabitMatrix()` constrói um grid visual de 31 dias cruzando dados de `/routines/` e `/tasks/`, permitindo interagir no estilo "github commits".

#### 4. Análise de Produtividade com IA
- **Mentor de Disciplina**: Disparada pela função `generateAnalysis()`, consome a rota `/analyze-week` avaliando as pendências dos últimos 7 dias.
- **Relatório Detalhado**: O sistema verifica quais tarefas eram esperadas, quais foram concluídas, quais ficaram pendentes e quais foram "faltantes".
- **Feedback Direto**: O backend se comunica com um LLM local. O retorno da IA é injetado na interface e formatado usando a biblioteca `marked.parse()`.

#### 5. Central de Impressão e Devocionais
- **Calendários para Fichário A5**: Gerados por `printMonthly()` e `printAnnual()`, permitindo impressão física.
- **Devocional Diário**: Integrado em `loadDailyDevotional()`, gera anotação automática em log através da função de atalho `completeDevotional()`.

#### 6. Backup e Restauração
- **Exportação Segura**: Exporte todo o banco de dados (`daily_hub.db`) com um único clique.
- **Importação Inteligente**: Restaure a aplicação a partir de um arquivo de backup. O sistema encerra as conexões ativas com o banco de dados antes de substituí-lo para evitar corrupção de dados.

## Arquitetura do Projeto

O projeto é dividido em um backend **FastAPI** e um frontend **Vanilla JavaScript** com **Tailwind CSS**.

```
daily-hub/
├── app/
│   ├── routers/
│   │   ├── tasks.py         # Lógica para CRUD de tarefas e motor de recorrência.
│   │   ├── analysis.py      # Rota e lógica para a análise de produtividade com IA.
│   │   ├── calendar_generator.py # (Inferido) Rotas para gerar os PDFs de calendário.
│   │   └── backup.py        # Rotas para exportar e importar o banco de dados.
│   │
│   ├── static/
│   │   ├── index.html       # Estrutura principal da interface do usuário.
│   │   ├── app.js           # Lógica do frontend (chamadas de API, renderização, eventos).
│   │   ├── manifest.json    # Configuração do PWA.
│   │   └── sw.js            # Service Worker para caching e funcionalidades offline.
│   │
│   ├── main.py              # Ponto de entrada da API FastAPI. Monta os roteadores e arquivos estáticos.
│   ├── database.py          # (Inferido) Configuração do SQLAlchemy (engine, session).
│   ├── models.py            # (Inferido) Definição das tabelas do banco de dados (ORM).
│   └── schemas.py           # (Inferido) Schemas Pydantic para validação de dados da API.
│
└── daily_hub.db             # Arquivo do banco de dados SQLite.
```

### Detalhes dos Componentes

*   **`main.py`**: O coração da API. Inicializa o FastAPI, cria as tabelas do banco de dados (se não existirem) e registra todos os módulos de rotas (`routers`). Também serve o `index.html` como a rota raiz.

*   **`routers/`**: Cada arquivo nesta pasta é um "mini-aplicativo" focado em uma funcionalidade específica, mantendo o código organizado e modular.
    *   `tasks.py`: Contém a lógica de negócio mais central. O motor de recorrência é chamado aqui antes de listar as tarefas.
    *   `analysis.py`: Orquestra a coleta de dados, a montagem do prompt e a comunicação com o LLM.
    *   `backup.py`: Lida com a manipulação de arquivos e o gerenciamento seguro das conexões do banco de dados durante a restauração.

*   **`static/`**: Contém todos os arquivos do lado do cliente.
    *   `index.html`: Define a estrutura visual completa da aplicação.
    *   `app.js`: Coração do front-end. Controla estados globais (`selectedDateStr`, `globalTasks`), processa interfaces (`loadTasks`, `renderDateSlider`, `renderHabitMatrix`) e gerencia APIs CRUD.

*   **`daily_hub.db`**: Um banco de dados SQLite, escolhido pela simplicidade e portabilidade, ideal para uma aplicação de uso pessoal.

## Como Executar

*(Esta seção pode ser preenchida com os detalhes do seu ambiente, por exemplo, Docker).*

1.  **Pré-requisitos**:
    *   Docker e Docker Compose instalados.
    *   Um servidor LLM rodando e acessível na rede (configurado via variável de ambiente `LM_STUDIO_URL`).

2.  **Configuração**:
    *   Configure as variáveis de ambiente necessárias (ex: no arquivo `.env` ou `docker-compose.yml`).
  
```
name: daily-hub
services:
    api:
        cpu_shares: 90
        command:
            - bash
            - -c
            - pip install --no-cache-dir fastapi uvicorn sqlalchemy requests pydantic reportlab python-multipart &&  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
        container_name: daily-hub-api
        deploy:
            resources:
                limits:
                    memory: "8136949760"
        environment:
            LM_STUDIO_URL: http://192.168.0.10:1234/v1
        hostname: daily-hub-api
        image: python:3.11-slim
        networks:
            default: null
        ports:
            - mode: ingress
              target: 8000
              published: "8080"
              protocol: tcp
        restart: unless-stopped
        volumes:
            - type: bind
              source: /DATA/AppData/daily-hub/app
              target: /app
              bind:
                create_host_path: true
        working_dir: /app
networks:
    default:
        name: daily-hub_default
x-casaos:
    author: self
    category: self
    hostname: ""
    icon: ""
    index: /
    is_uncontrolled: false
    port_map: ""
    scheme: http
    title:
        custom: daily-hub

```

3.  **Execução**:
    *   Execute o comando `docker-compose up -d` na raiz do projeto.
    *   Acesse a aplicação em `http://localhost:<porta>`.

## Endpoints Principais da API

- `GET /tasks/`: Retorna todas as tarefas.
- `POST /tasks/`: Cria uma nova tarefa.
- `PUT /tasks/{task_id}`: Atualiza uma tarefa (ex: para marcar como concluída).
- `DELETE /tasks/{task_id}`: Exclui uma tarefa.
- `POST /analyze-week`: Aciona a análise de produtividade da semana.
- `GET /backup/export`: Faz o download do arquivo do banco de dados.
- `POST /backup/import`: Recebe um arquivo `.db` para restaurar o banco de dados.

---