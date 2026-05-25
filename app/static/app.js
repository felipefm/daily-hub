// Configurações Globais
const API_URL = '/tasks/';
const ANALYZE_URL = '/analyze-week';
let selectedDateStr = new Date().toLocaleDateString('sv'); // Formato YYYY-MM-DD
let globalTasks = []; // Armazena as tarefas globalmente para o slider

/**
 * 0. GERENCIAMENTO DA INTERFACE (UI)
 */

// Renderiza o slider de datas horizontal
function renderDateSlider() {
    const slider = document.getElementById('date-slider');
    if (!slider) return;
    slider.innerHTML = '';

    const today = new Date();
    const todayStr = today.toLocaleDateString('sv');

    // Gera um range de datas (ex: 14 dias para trás, 14 para frente)
    for (let i = -14; i <= 14; i++) {
        const date = new Date(today);
        date.setDate(today.getDate() + i);
        const dateStr = date.toLocaleDateString('sv');
        
        const dayOfWeek = date.toLocaleDateString('pt-BR', { weekday: 'short' }).replace('.', '');
        const dayOfMonth = date.getDate();

        const button = document.createElement('button');
        button.setAttribute('onclick', `selectDate('${dateStr}')`);
        
        const isSelected = dateStr === selectedDateStr;
        const isToday = dateStr === todayStr;
        
        const jsDay = date.getDay();
        const isWeekend = jsDay === 0 || jsDay === 6; // 0 = Domingo, 6 = Sábado

        // Verifica se há tarefas pendentes para este dia
        const hasPendingTasks = globalTasks.some(t => t.date === dateStr && !t.is_completed);
        const indicatorHtml = hasPendingTasks ? `<div class="w-1.5 h-1.5 bg-indigo-400 dark:bg-indigo-400 rounded-full mt-1 mx-auto"></div>` : `<div class="w-1.5 h-1.5 mt-1 mx-auto opacity-0"></div>`;

        let baseClasses = 'flex flex-col items-center justify-center w-14 h-16 rounded-lg transition-all duration-200 snap-center shrink-0';
        let activeClasses = isSelected ? 'bg-indigo-600 text-white shadow-lg' : 'bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700';
        if (isToday && !isSelected) {
            activeClasses = 'bg-white dark:bg-gray-800 border-2 border-indigo-400';
        }

        let dayColorClass = isSelected ? 'opacity-70' : (isWeekend ? 'text-red-500 dark:text-red-400' : 'text-gray-400');
        let numColorClass = isWeekend && !isSelected ? 'text-red-600 dark:text-red-400' : '';

        button.className = `${baseClasses} ${activeClasses}`;
        button.innerHTML = `
            <span class="text-xs uppercase font-bold ${dayColorClass}">${dayOfWeek}</span>
            <span class="text-2xl font-bold ${numColorClass}">${dayOfMonth}</span>
            ${indicatorHtml}
        `;
        slider.appendChild(button);
    }

    // Rola o slider para a data selecionada
    setTimeout(() => {
        const selectedButton = slider.querySelector('.bg-indigo-600');
        selectedButton?.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
    }, 100);
}

// Atualiza a data selecionada pelo slider e recarrega as tarefas
function selectDate(dateStr) {
    selectedDateStr = dateStr;
    renderDateSlider();
    loadTasks();
}

// Adiciona suporte a arraste (drag) e rolagem do mouse no slider para uso no desktop
function initSliderDesktop() {
    const slider = document.getElementById('date-slider');
    if (!slider) return;

    let isDown = false;
    let startX;
    let scrollLeft;
    let isDragging = false;

    slider.addEventListener('mousedown', (e) => {
        isDown = true;
        isDragging = false;
        slider.style.cursor = 'grabbing';
        startX = e.pageX - slider.offsetLeft;
        scrollLeft = slider.scrollLeft;
    });

    slider.addEventListener('mouseleave', () => {
        isDown = false;
        slider.style.cursor = '';
    });

    slider.addEventListener('mouseup', () => {
        isDown = false;
        slider.style.cursor = '';
    });

    slider.addEventListener('mousemove', (e) => {
        if (!isDown) return;
        const x = e.pageX - slider.offsetLeft;
        const walk = (x - startX) * 1.5; // Velocidade do arraste
        if (Math.abs(walk) > 5) {
            isDragging = true;
            e.preventDefault();
            slider.scrollLeft = scrollLeft - walk;
        }
    });

    // Impede o clique acidental no botão de data se o usuário estiver apenas arrastando o slider
    slider.addEventListener('click', (e) => {
        if (isDragging) {
            e.preventDefault();
            e.stopPropagation();
        }
    }, true);

    // Permite usar a rodinha do mouse para rolar horizontalmente
    slider.addEventListener('wheel', (e) => {
        if (e.deltaY !== 0) {
            e.preventDefault();
            slider.scrollLeft += e.deltaY;
        }
    });
}

/**
 * 1. GERENCIAMENTO DE TAREFAS (CRUD & LOG)
 */

// Função auxiliar para renderizar tarefas do log diário
function renderItems(tasks, container, todayStr) {
    tasks.forEach(task => {
        const li = document.createElement('li');
        // Aplica transparência maior (opacity-30) se concluído
        li.className = `p-4 flex items-center justify-between transition-all duration-300 ${task.is_completed ? 'opacity-30 grayscale-[0.5]' : ''}`;
        
        li.innerHTML = `
            <div class="flex items-center gap-4">
                <input type="checkbox" ${task.is_completed ? 'checked' : ''} 
                    onchange="toggleTask(${task.id}, this.checked)"
                    class="w-5 h-5 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500 cursor-pointer">
                <div id="task-content-${task.id}" class="flex flex-col">
                    <span class="${task.is_completed ? 'line-through text-gray-500' : 'font-medium'}">
                        ${task.title}
                    </span>
                </div>
            </div>
            <div class="flex items-center gap-3">
                <button id="edit-btn-${task.id}" onclick="toggleEditTask(${task.id}, '${task.title.replace(/'/g, "\\'")}', '${task.date}')" class="text-indigo-400 hover:text-indigo-600 transition-opacity" title="Editar Tarefa">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                </button>
                <button onclick="deleteTask(${task.id})" class="text-red-400 hover:text-red-600 transition-opacity">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>
                </button>
            </div>
        `;
        container.appendChild(li);
    });
}

// Carrega e renderiza as tarefas para a data selecionada
async function loadTasks() {
    const taskList = document.getElementById('task-list');
    const recurringList = document.getElementById('recurring-task-list');
    const recurringCount = document.getElementById('recurring-count');
    const todayStr = new Date().toLocaleDateString('sv');

    try {
        // Usar Promise.all para fazer fetch simultâneo
        const [tasksResponse, routinesResponse] = await Promise.all([
            fetch(API_URL),
            fetch('/routines/')
        ]);
        
        const allTasks = await tasksResponse.json();
        globalTasks = allTasks; // Atualiza o estado global para uso no slider
        const routineTemplates = await routinesResponse.json();
        
        taskList.innerHTML = '';
        recurringList.innerHTML = '';

        // 1. FILTRAGEM: Apenas tarefas da data selecionada no slider
        let filteredTasks = allTasks.filter(t => t.date === selectedDateStr);
        
        // 2. ORDENAÇÃO: Pendentes primeiro, concluídas por último
        filteredTasks.sort((a, b) => a.is_completed - b.is_completed);

        // 3. RENDERIZAÇÃO
        if (filteredTasks.length === 0) {
            const li = document.createElement('li');
            li.className = 'p-8 text-center text-gray-400 text-sm';
            li.textContent = 'Nenhuma tarefa para este dia.';
            taskList.appendChild(li);
        } else {
            renderItems(filteredTasks, taskList, todayStr);
        }
        
        renderRoutineTemplates(routineTemplates, recurringList);
        recurringCount.innerText = routineTemplates.length;
        
        // 4. ATUALIZAÇÃO SILENCIOSA DA MATRIZ (se o dashboard estiver visível)
        const habitDashboard = document.getElementById('habit-dashboard');
        if (habitDashboard && !habitDashboard.classList.contains('hidden')) {
            renderHabitMatrix().catch(() => {}); // Silencioso se houver erro
        }
        
        // Atualiza o slider para refletir os indicadores de tarefas pendentes
        renderDateSlider();

    } catch (error) {
        console.error("Erro ao carregar tarefas:", error);
    }
}

// Função auxiliar: verifica se uma rotina é ativa hoje
// Verifica se a rotina é ativa hoje cruzando JS com Python
function isActiveToday(recurrenceType) {
    const today = new Date();
    const jsDay = today.getDay(); // No JS: 0=Dom, 1=Seg...
    const currentDayNumeric = jsDay === 0 ? 6 : jsDay - 1; // No Python: 0=Seg, 6=Dom

    if (recurrenceType === 'daily') return true;
    if (recurrenceType === 'monthly') return today.getDate() === 1;

    // Verifica strings numéricas de forma segura ('0,2' ou '5')
    const recStr = String(recurrenceType);
    if (recStr.includes(',') || !isNaN(recStr)) {
        const dias = recStr.split(',');
        return dias.includes(String(currentDayNumeric));
    }
    return false;
}

// Função para renderizar templates de rotinas
// Renderizar templates de rotinas traduzindo os números
function renderRoutineTemplates(routines, container) {
    const sortedRoutines = [...routines].sort((a, b) => isActiveToday(b.recurrence_type) - isActiveToday(a.recurrence_type));

    sortedRoutines.forEach(routine => {
        const li = document.createElement('li');
        const isActive = isActiveToday(routine.recurrence_type);

        const baseClasses = 'p-4 flex items-center justify-between border-b border-gray-200 dark:border-gray-700 transition-all duration-300';
        const inactiveClasses = isActive ? '' : 'opacity-40 grayscale';
        li.className = `${baseClasses} ${inactiveClasses}`;

        const recurrenceNames = {
            'daily': 'Diário',
            'monthly': 'Mensal'
        };

        const daysMap = { '0': 'Seg', '1': 'Ter', '2': 'Qua', '3': 'Qui', '4': 'Sex', '5': 'Sáb', '6': 'Dom' };
        let displayRecurrence = recurrenceNames[routine.recurrence_type];

        if (!displayRecurrence) {
            // Converte '0,2,5' para 'Seg, Qua, Sáb' com segurança
            displayRecurrence = String(routine.recurrence_type).split(',')
                .map(num => daysMap[num.trim()])
                .filter(Boolean)
                .join(', ');
        }

        const inactiveText = isActive ? '' : ' <span class="ml-2 text-[8px] px-2 py-1 rounded-full bg-gray-300 dark:bg-gray-600 text-gray-600 dark:text-gray-300 font-semibold">(INATIVO HOJE)</span>';

        li.innerHTML = `
            <div class="flex flex-col flex-grow mr-4" id="routine-info-${routine.id}">
                <span class="font-medium">${routine.title}</span>
                <span class="text-[10px] text-gray-400 uppercase font-bold tracking-tight">${displayRecurrence}${inactiveText}</span>
            </div>
            <div class="flex items-center gap-3">
                <button id="edit-btn-${routine.id}" data-title="${routine.title.replace(/"/g, '&quot;')}" data-recurrence="${routine.recurrence_type}" onclick="toggleEditRoutine(${routine.id})" class="text-indigo-400 hover:text-indigo-600 transition-opacity" title="Editar Rotina">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                </button>
                <button onclick="deleteRoutine(${routine.id})" class="text-red-400 hover:text-red-600 transition-opacity" title="Excluir Rotina">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>
                </button>
            </div>
        `;
        container.appendChild(li);
    });
}

// Submeter nova tarefa ou rotina
document.getElementById('task-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const titleInput = document.getElementById('task-title');
    const dateInput = document.getElementById('task-date');
    
    const recurrenceContainer = document.getElementById('recurrence-container');
    const recurrenceSelect = recurrenceContainer.querySelector('.recurrence-select');
    let recurrenceValue = recurrenceSelect.value;

    if (recurrenceValue === 'custom') {
        const activeBtns = recurrenceContainer.querySelectorAll('.custom-days-container button.bg-indigo-600');
        const days = Array.from(activeBtns).map(b => b.getAttribute('data-day'));
        recurrenceValue = days.join(',');
    }

    const isRecurring = recurrenceValue !== 'none';

    if (isRecurring) {
        // Criar um RoutineTemplate
        const payload = {
            title: titleInput.value,
            recurrence_type: recurrenceValue
        };
        
        await fetch('/routines/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
    } else {
        // Criar uma Task (log diário)
        let selectedDate = dateInput.value || selectedDateStr; // Usa a data do slider se nenhuma for especificada
        
        const payload = {
            title: titleInput.value,
            date: selectedDate
        };
        
        await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
    }

    // Limpeza e reload
    titleInput.value = '';
    dateInput.value = '';
    document.getElementById('recurrence-container').innerHTML = createDaySelectorHTML(true, 'none');
    document.getElementById('advanced-options').classList.add('hidden');
    loadTasks();
});

// Atualizar status (Concluído/Pendente)
async function toggleTask(id, isCompleted) {
    await fetch(`${API_URL}${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_completed: isCompleted })
    });
    await loadTasks();
}

// Excluir tarefa
async function deleteTask(id) {
    if(confirm('Deseja excluir esta tarefa?')) {
        await fetch(`${API_URL}${id}`, { method: 'DELETE' });
        await loadTasks();
    }
}

// Excluir rotina (template de hábito)
async function deleteRoutine(id) {
    if(confirm('Deseja excluir esta rotina?')) {
        await fetch(`/routines/${id}`, { method: 'DELETE' });
        await loadTasks();
    }
}

// Ativar edição inline da rotina
function toggleEditRoutine(id) {
    const infoDiv = document.getElementById(`routine-info-${id}`);
    const btn = document.getElementById(`edit-btn-${id}`);
    
    if (!infoDiv || !btn) return;

    const currentTitle = btn.getAttribute('data-title');
    const currentRecurrence = btn.getAttribute('data-recurrence');

    infoDiv.innerHTML = `
        <input type="text" id="edit-title-${id}" value="${currentTitle}" class="w-full text-sm border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded shadow-sm focus:ring-indigo-500 focus:border-indigo-500 mb-2 px-2 py-1">
        <div id="edit-recurrence-container-${id}">
            ${createDaySelectorHTML(false, currentRecurrence)}
        </div>
    `;

    // Muda o botão para "Salvar" (ícone de ✔️)
    btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-500 hover:text-green-600" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>`;
    btn.title = "Salvar Rotina";
    btn.onclick = () => saveRoutine(id);
}

// Salvar edição da rotina no Backend
async function saveRoutine(id) {
    const newTitle = document.getElementById(`edit-title-${id}`).value;
    
    const container = document.getElementById(`edit-recurrence-container-${id}`);
    const select = container.querySelector('.recurrence-select');
    let newRecurrence = select.value;

    if (newRecurrence === 'custom') {
        const activeBtns = container.querySelectorAll('.custom-days-container button.bg-indigo-600');
        const days = Array.from(activeBtns).map(b => b.getAttribute('data-day'));
        newRecurrence = days.join(',');
    }

    if (!newTitle.trim()) {
        alert('O título da rotina não pode estar vazio.');
        return;
    }

    await fetch(`/routines/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            title: newTitle, 
            recurrence_type: newRecurrence 
        })
    });

    await loadTasks();
}

// Toggle do Habit Dashboard
function toggleHabitDashboard() {
    const habitDashboard = document.getElementById('habit-dashboard');
    habitDashboard.classList.toggle('hidden');
    
    // Se o painel foi aberto (classe hidden foi removida), renderizar a matriz
    if (!habitDashboard.classList.contains('hidden')) {
        renderHabitMatrix();
    }
}

// Renderizar a matriz de hábitos (Habit Tracker)
async function renderHabitMatrix() {
    const matrixBody = document.getElementById('habit-matrix-body');
    const currentMonthDisplay = document.getElementById('habit-current-month');
    
    try {
        // 1. BUSCA DE DADOS: Rotinas e Tarefas
        const [routinesResponse, tasksResponse] = await Promise.all([
            fetch('/routines/'),
            fetch(API_URL)
        ]);
        
        const routines = await routinesResponse.json();
        const allTasks = await tasksResponse.json();
        
        // 2. CÁLCULO DO PERÍODO
        const today = new Date();
        const year = today.getFullYear();
        const month = today.getMonth(); // 0-11
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        
        // Atualizar exibição do mês/ano
        const monthNames = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                           'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
        currentMonthDisplay.textContent = `${monthNames[month]} ${year}`;
        
        // 3. LIMPAR O CORPO DA TABELA
        matrixBody.innerHTML = '';
        
        // 4. MONTAR AS LINHAS (uma por rotina)
        routines.forEach(routine => {
            const tr = document.createElement('tr');
            tr.className = 'divide-x divide-gray-200 dark:divide-gray-700';
            
            // Primeira célula: nome do hábito
            const habitNameCell = document.createElement('td');
            habitNameCell.className = 'px-4 py-2 font-medium text-gray-800 dark:text-gray-200 bg-gray-50 dark:bg-gray-700/30 border border-gray-200 dark:border-gray-600 w-40 text-left text-sm';
            habitNameCell.textContent = routine.title;
            tr.appendChild(habitNameCell);
            
            // 5. MONTAR AS CÉLULAS (dias 1 a 31)
            for (let day = 1; day <= 31; day++) {
                const dayCell = document.createElement('td');
                dayCell.className = 'px-1 py-1 text-center border border-gray-200 dark:border-gray-600 min-w-[32px]';
                
                // Montar a data em formato ISO (YYYY-MM-DD)
                const monthStr = String(month + 1).padStart(2, '0');
                const dayStr = String(day).padStart(2, '0');
                const dateStr = `${year}-${monthStr}-${dayStr}`;
                
                // 6. CRUZAMENTO DE DADOS: Procurar tarefa correspondente
                const correspondingTask = allTasks.find(t => 
                    t.title === routine.title && t.date === dateStr
                );
                
                // 7. ESTILIZAÇÃO DO QUADRADO
                const square = document.createElement('button');
                square.type = 'button';
                square.className = `w-6 h-6 rounded transition-all duration-200 ${
                    correspondingTask && correspondingTask.is_completed
                        ? 'bg-indigo-600 hover:bg-indigo-700 shadow-sm flex items-center justify-center'
                        : 'border border-gray-300 dark:border-gray-600 hover:border-indigo-400 dark:hover:border-indigo-500'
                }`;
                
                // Adicionar ícone de check se concluído
                if (correspondingTask && correspondingTask.is_completed) {
                    square.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-white" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>';
                }
                
                // 8. INTERAÇÃO: Evento de clique
                square.addEventListener('click', async (e) => {
                    e.preventDefault();
                    
                    if (correspondingTask) {
                        // Se a tarefa existe, inverter o status
                        await toggleTask(correspondingTask.id, !correspondingTask.is_completed);
                    } else {
                        // Se não existe, criar a tarefa com status concluído
                        const payload = {
                            title: routine.title,
                            date: dateStr
                        };
                        
                        const createResponse = await fetch(API_URL, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(payload)
                        });
                        
                        if (createResponse.ok) {
                            const newTask = await createResponse.json();
                            // Marcar imediatamente como concluído
                            await toggleTask(newTask.id, true);
                        }
                    }
                    
                    // Rerender a matriz após a ação
                    renderHabitMatrix();
                });
                
                dayCell.appendChild(square);
                tr.appendChild(dayCell);
            }
            
            matrixBody.appendChild(tr);
        });
        
    } catch (error) {
        console.error("Erro ao renderizar matriz de hábitos:", error);
    }
}

/**
 * 2. INTEGRAÇÃO COM IA (LM STUDIO)
 */
async function generateAnalysis() {
    const btn = document.getElementById('btn-analyze-new');
    const responseContainer = document.getElementById('ai-response');
    const promptInput = document.getElementById('ai-custom-prompt');

    const customPromptValue = promptInput.value.trim() || "Faça um resumo dos últimos 7 dias e destaque pontos fortes e fracos.";

    btn.disabled = true;
    btn.innerHTML = `<span class="animate-spin mr-2">⏳</span> Analisando...`;
    
    responseContainer.innerHTML = '<div class="flex justify-center p-4"><div class="animate-pulse text-indigo-500">O Mentor está processando sua análise...</div></div>';

    try {
        const response = await fetch(ANALYZE_URL, { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: customPromptValue })
        });
        const data = await response.json();
        
        responseContainer.innerHTML = marked.parse(data.analysis);
    } catch (error) {
        responseContainer.innerHTML = `<div class="p-4 bg-red-50 text-red-600 rounded">Erro na consulta: ${error.message}</div>`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd" />
            </svg>
            Gerar Análise
        `;
    }
}

/**
 * 3. INTERFACE E IMPRESSÃO (FICHÁRIO A5)
 */
function toggleAdvanced() {
    document.getElementById('advanced-options').classList.toggle('hidden');
}

function toggleAIPanel() {
    document.getElementById('ai-panel').classList.toggle('hidden');
}

function togglePrintSection() {
    document.getElementById('print-section').classList.toggle('hidden');
}

function toggleDevotional() {
    document.getElementById('devotional-screen').classList.toggle('hidden');
    // Se está sendo exibido, carrega o devocional do dia
    if (!document.getElementById('devotional-screen').classList.contains('hidden')) {
        loadDailyDevotional();
    }
}

function switchDevoTab(tabName) {
    // Esconde todos os contêineres de abas
    const tabs = ['leituras', 'salmo', 'evangelho', 'santo', 'homilia'];
    tabs.forEach(tab => {
        const tabElement = document.getElementById(`tab-${tab}`);
        if (tabElement) {
            tabElement.classList.add('hidden');
        }
    });
    
    // Remove classe ativa de todos os botões
    tabs.forEach(tab => {
        const btnElement = document.getElementById(`btn-tab-${tab}`);
        if (btnElement) {
            btnElement.classList.remove('text-indigo-600', 'dark:text-indigo-400', 'border-b-2', 'border-indigo-600', 'dark:border-indigo-400');
            btnElement.classList.add('text-stone-400', 'hover:text-stone-600', 'dark:text-stone-500', 'dark:hover:text-stone-300');
        }
    });
    
    // Mostra a aba selecionada
    const selectedTab = document.getElementById(`tab-${tabName}`);
    if (selectedTab) {
        selectedTab.classList.remove('hidden');
    }
    
    // Ativa o botão selecionado
    const selectedBtn = document.getElementById(`btn-tab-${tabName}`);
    if (selectedBtn) {
        selectedBtn.classList.remove('text-stone-400', 'hover:text-stone-600', 'dark:text-stone-500', 'dark:hover:text-stone-300');
        selectedBtn.classList.add('text-indigo-600', 'dark:text-indigo-400', 'border-b-2', 'border-indigo-600', 'dark:border-indigo-400');
    }
}

async function loadDailyDevotional() {
    // Dados estáticos/mockados para demonstração - Liturgia completa
    const devotionals = [
        {
            leituras: `
                <h3 class="font-sans text-xs uppercase tracking-widest text-stone-400 mb-4 text-center">Primeira Leitura</h3>
                <p class="mb-6">Leitura do Livro dos Salmos. Bem-aventurado o homem que não entra no conselho dos iníquos, nem trilha o caminho dos pecadores, nem se assenta na roda dos malfeitores. Mas seu prazer está na lei do Senhor, e na sua lei medita dia e noite.</p>
                <h3 class="font-sans text-xs uppercase tracking-widest text-stone-400 mb-4 text-center">Responsório</h3>
                <p class="mb-6">Graça e paz a vós, pela misericórdia de Deus. Regozijai-vos na esperança que não decepciona. O Senhor é próximo dos que sofrem de coração quebrantado.</p>
            `,
            salmo: `
                <h3 class="font-sans text-xs uppercase tracking-widest text-stone-400 mb-4 text-center">Salmo 23</h3>
                <p class="mb-6">O Senhor é meu pastor, nada me faltará. Em prados verdejantes ele me faz repousar, e me conduz para as águas tranquilas. Ele restaura a minha alma e me guia pelas veredas da justiça, por amor do seu nome.</p>
                <p class="mb-6">Ainda que eu ande pelo vale da sombra da morte, não temerei mal algum, porque tu estás comigo. Teu cajado e teu bordão me consolam. Preparas uma mesa diante de mim na presença dos meus adversários. Unges a minha cabeça com óleo; o meu cálice transborda.</p>
                <p class="mb-6">Certamente que a bondade e a misericórdia me acompanharão todos os dias da minha vida, e habitarei na casa do Senhor para sempre.</p>
            `,
            evangelho: `
                <h3 class="font-sans text-xs uppercase tracking-widest text-stone-400 mb-4 text-center">Evangelho segundo São Mateus 6:25-34</h3>
                <p class="mb-6">Jesus disse a seus discípulos: Não vos preocupeis com a vossa vida, quanto ao que haveis de comer ou beber, nem com o vosso corpo, quanto ao que haveis de vestir. Não é a vida mais do que o alimento, e o corpo mais do que o vestido?</p>
                <p class="mb-6">Olhai para as aves do céu: nem semeiam, nem ceifam, nem ajuntam em celeiros; e vosso Pai celestial as alimenta. Não valeis vós muito mais do que elas? E qual de vós, por mais que se preocupe, pode acrescentar um côvado ao curso de sua vida?</p>
                <p class="mb-6">E por que vos preocupais com o vestido? Observai os lírios do campo, como crescem; não trabalham nem fiam. Mas eu vos digo que nem Salomão em toda a sua glória se vestiu como um deles.</p>
            `,
            santo: `
                <h3 class="font-sans text-xs uppercase tracking-widest text-stone-400 mb-4 text-center">Santo do Dia: São Norberto</h3>
                <p class="mb-6">Norberto de Xanten (1080-1134) foi um reformador religioso que deixou uma vida de luxo para servir a Deus com dedicação absoluta. Fundador da Ordem Premonstratense, sua vida exemplifica a conversão sincera e o amor radical pela justiça.</p>
                <p class="mb-6">Sua espiritualidade unia contemplação profunda com engajamento social. Acreditava que a vida monástica deveria estar a serviço dos pobres e necessitados. Sua canonização reconhece a santidade de quem abraça a cruz com alegria.</p>
                <p class="mb-6">Intercede por nós para que possamos discernir o chamado de Deus em nossas vidas e respondamos com generosidade e fé.</p>
            `,
            homilia: `
                <h3 class="font-sans text-xs uppercase tracking-widest text-stone-400 mb-4 text-center">Homilia</h3>
                <p class="mb-6">Irmãos e irmãs, a liturgia de hoje nos convida a refletir sobre a providência divina. Jesus nos pede para não nos preocuparmos com o amanhã, porque nosso Pai conhece todas as nossas necessidades. Isso não significa negligência ou preguiça, mas confiança radical em Deus.</p>
                <p class="mb-6">No mundo contemporâneo, somos bombardeados de ansiedades e incertezas. Os meios de comunicação nos bombardeiam com crises e catástrofes. Mas Jesus nos oferece um antídoto: a fé. Não uma fé ingênua, mas uma fé enraizada na experiência de um Deus que cuida de seus filhos.</p>
                <p class="mb-6">Que neste dia possamos soltar um pouco o controle que tentamos exercer sobre nossas vidas e permitir que Deus nos guie com sabedoria e amor. Que encontremos paz no silêncio, força na oração, e companhia na comunidade de fé.</p>
            `
        },
        {
            leituras: `
                <h3 class="font-sans text-xs uppercase tracking-widest text-stone-400 mb-4 text-center">Primeira Leitura</h3>
                <p class="mb-6">Leitura do Livro da Sabedoria. Procurai a justiça, vós que julgais a terra. Pensai bem do Senhor e buscai-o com coração sincero. Porque ele se deixa encontrar pelos que não o contradizem, e se manifesta aos que não desconfiam dele.</p>
                <p class="mb-6">Mas os pensamentos perversos nos separam de Deus e o seu poder, quando é colocado à prova, confunde aos insensatos. A sabedoria não entra em alma que nutre malícia, nem habita em corpo escravo do pecado.</p>
            `,
            salmo: `
                <h3 class="font-sans text-xs uppercase tracking-widest text-stone-400 mb-4 text-center">Salmo 42</h3>
                <p class="mb-6">Como a corça suspira pelas águas correntes, assim a minha alma suspira por ti, ó Deus. A minha alma tem sede de Deus, do Deus vivo. Quando poderei vir e contemplar a face de Deus?</p>
                <p class="mb-6">As minhas lágrimas me servem de pão, enquanto me perguntam todo o dia: Onde está o teu Deus? Quando recuerdo estas coisas, derramarei a minha alma, porque lembrado do tempo em que marchava com a multidão, e os conduzia à casa de Deus com vozes de alegria e de louvor.</p>
                <p class="mb-6">Por que estás abatida, ó minha alma? Por que te turbas? Espera em Deus, porque ainda o louvarei, a ele, meu Salvador e meu Deus.</p>
            `,
            evangelho: `
                <h3 class="font-sans text-xs uppercase tracking-widest text-stone-400 mb-4 text-center">Evangelho segundo São Lucas 12:22-31</h3>
                <p class="mb-6">Disse Jesus aos seus discípulos: Por isso vos digo: Não andeis ansiosos pela vossa vida, pelo que haveis de comer, nem pelo vosso corpo, pelo que haveis de vestir. A vida é mais do que o alimento, e o corpo mais do que o vestido.</p>
                <p class="mb-6">Considerai os corvos: não semeiam, nem ceifam; não têm adega nem celeiro, e Deus os alimenta. Quanto mais valeis vós do que as aves? E qual de vós, por mais que se preocupe, pode acrescentar um côvado ao curso de sua vida?</p>
                <p class="mb-6">Se nem isto podeis fazer, por que vos preocupais com o resto? Considerai os lírios, como crescem; não trabalham, nem fiam. Digo-vos que nem Salomão em toda a sua glória se vestiu como um deles. Se Deus assim veste a erva do campo, que hoje existe e amanhã é lançada ao forno, quanto mais a vós, homens de pouca fé?</p>
            `,
            santo: `
                <h3 class="font-sans text-xs uppercase tracking-widest text-stone-400 mb-4 text-center">Santo do Dia: Santa Madalena de Pazzi</h3>
                <p class="mb-6">Madalena (1566-1607) foi uma mística carmelita cuja vida foi marcada por experiências profundas de contemplação. Sua riqueza espiritual nos mostra o caminho da entrega total a Deus através da oração constante. Nascida em Florença, abraçou a vida religiosa e se tornou um instrumento do Espírito Santo.</p>
                <p class="mb-6">Sua sabedoria contemplativa ilumina ainda hoje os corações que buscam a verdade. Através de suas palavras e exemplo, nos convida a morrer para o ego e ressurgir em Cristo. Sua vida foi breve, mas intensamente frutífera em conversões e graças extraordinárias.</p>
                <p class="mb-6">Rogai por nós, santa Madalena, para que possamos conhecer a profundidade do amor de Deus e nos entreguemos completamente a seu serviço.</p>
            `,
            homilia: `
                <h3 class="font-sans text-xs uppercase tracking-widest text-stone-400 mb-4 text-center">Homilia</h3>
                <p class="mb-6">Caríssimos, nesta celebração eucarística, somos convidados a aprofundar nossa comunhão com Cristo. A Eucaristia não é apenas um ritual, mas um encontro vivo com o ressuscitado. Cada vez que nos aproximamos da mesa do Senhor, participamos de seu corpo e sangue, nos unindo na morte e ressurreição.</p>
                <p class="mb-6">Quantas vezes corremos atrás de seguranças falsas? Acreditamos que possuindo coisas seremos felizes, quando na verdade apenas o amor nos plenifica. A Igreja hoje nos recorda que há um alimento que satisfaz verdadeiramente: a Palavra de Deus e o Pão da Vida.</p>
                <p class="mb-6">Saindo daqui, levemos a Eucaristia vivida em nossos corações. Que possamos ser luz para o mundo, sal da terra, fermento de transformação. Que nossa fé seja contagiante e nossa presença deixe marcas de compaixão e esperança.</p>
            `
        },
        {
            leituras: `
                <h3 class="font-sans text-xs uppercase tracking-widest text-stone-400 mb-4 text-center">Primeira Leitura</h3>
                <p class="mb-6">Leitura do Livro de Jeremias. Eis que vêm dias — oráculo do Senhor — em que farei uma aliança nova com a casa de Israel e com a casa de Judá. Não será como a aliança que fiz com seus pais no dia em que os tomei pela mão para tirá-los do Egito.</p>
                <p class="mb-6">Mas esta é a aliança que farei com a casa de Israel depois daqueles dias — oráculo do Senhor: Porei minha lei dentro deles e a escreverei em seu coração. Serei o seu Deus, e eles serão meu povo.</p>
            `,
            salmo: `
                <h3 class="font-sans text-xs uppercase tracking-widest text-stone-400 mb-4 text-center">Salmo 130</h3>
                <p class="mb-6">Do profundo clamo a ti, Senhor. Senhor, ouve a minha voz. Estejam atentos os teus ouvidos à voz da minha súplica. Se observares os crimes, Senhor, quem subsistirá?</p>
                <p class="mb-6">Mas em ti existe perdão, para que sejas temido. Espero no Senhor, minha alma espera, e na sua palavra tenho esperança. A minha alma aspira pelo Senhor mais do que as sentinelas pela alva.</p>
                <p class="mb-6">Espera, Israel, no Senhor, porque nele há misericórdia, e nele há redenção copiosa. Ele redimirá Israel de todos os seus pecados.</p>
            `,
            evangelho: `
                <h3 class="font-sans text-xs uppercase tracking-widest text-stone-400 mb-4 text-center">Evangelho segundo São João 3:16-17</h3>
                <p class="mb-6">Deus amou tanto o mundo que deu seu único Filho, para que todo aquele que nele crê não pereça, mas tenha a vida eterna. Pois Deus não enviou seu Filho ao mundo para condenar o mundo, mas para que o mundo fosse salvo por ele.</p>
                <p class="mb-6">Quem crê nele não é condenado; quem não crê já está condenado, porque não crê no nome do único Filho de Deus. E esta é a condenação: a luz veio ao mundo, e os homens amaram mais as trevas do que a luz, porque as suas obras eram más.</p>
                <p class="mb-6">Porque todo aquele que pratica o mal odeia a luz e não vem para a luz, para que não sejam expostas as suas obras. Mas aquele que pratica a verdade vem para a luz, para que se veja claramente que as suas obras foram feitas em Deus.</p>
            `,
            santo: `
                <h3 class="font-sans text-xs uppercase tracking-widest text-stone-400 mb-4 text-center">Santo do Dia: Santo Agostinho</h3>
                <p class="mb-6">Aurelius Aurelius Augustinus (354-430) é um dos maiores doutores da Igreja. Sua vida exemplifica o poder transformador da graça. Antes de sua conversão, Agostinho buscou satisfação em prazeres mundanos e filosofias humanas, mas encontrou inquietação constante.</p>
                <p class="mb-6">Sua conversão, narrada nas Confissões, mostra como nenhum coração é demasiado endurecido para a graça divina. Seus escritos teológicos influenciaram profundamente o cristianismo ao longo dos séculos. Sua oração permanece verdadeira: Fizeste-nos para ti, e inquieto está o nosso coração enquanto não repousa em ti.</p>
                <p class="mb-6">Rogai por nós, Santo Agostinho, para que possamos também experimentar a conversão e a paz em Deus.</p>
            `,
            homilia: `
                <h3 class="font-sans text-xs uppercase tracking-widest text-stone-400 mb-4 text-center">Homilia</h3>
                <p class="mb-6">Irmãs e irmãos, contemplamos nesta liturgia a misericórdia infinita de Deus. O Evangelho de hoje revela o coração de Deus: ele não veio para condenar, mas para salvar. Quantas vezes nos sentimos distantes de Deus, pensando que nossas falhas são demasiado grandes?</p>
                <p class="mb-6">A mensagem de João é radical: Deus não rejeita ninguém. Ele oferece vida eterna a todo aquele que crê. Essa crença não é intelectual, mas uma confiança que nos transforma. É abraçar o amor oferecido gratuitamente na cruz.</p>
                <p class="mb-6">Deixemos que essa verdade revolucione nossas vidas. Que nos tornemos instrumentos de misericórdia para um mundo ferido. Que nossa fé seja esperança para os desesperados, luz para os perdidos, compaixão para os sofredores. Amém.</p>
            `
        }
    ];
    
    // Seleciona um devocional baseado na data (assim sempre o mesmo para o dia)
    const today = new Date().getDate() % devotionals.length;
    const devotional = devotionals[today];
    
    // Preenche as abas com os dados usando innerHTML para estrutura HTML
    document.getElementById('devo-leituras').innerHTML = devotional.leituras;
    document.getElementById('devo-salmo').innerHTML = devotional.salmo;
    document.getElementById('devo-evangelho').innerHTML = devotional.evangelho;
    document.getElementById('devo-santo').innerHTML = devotional.santo;
    document.getElementById('devo-homilia').innerHTML = devotional.homilia;
}

async function completeDevotional() {
    const btn = document.getElementById('devo-complete-btn');
    const originalText = btn.textContent;
    
    try {
        // Desabilita o botão enquanto processa
        btn.disabled = true;
        btn.textContent = '⏳ Anotando...';
        
        // Obtém a data de hoje no formato YYYY-MM-DD
        const todayStr = new Date().toLocaleDateString('sv');
        
        // Faz fetch para pegar todas as tarefas
        const tasksResponse = await fetch(API_URL);
        const allTasks = await tasksResponse.json();
        
        // Procura por uma tarefa existente com "Devocional" no título para hoje
        const devTask = allTasks.find(task => 
            task.date === todayStr && 
            task.title.toLowerCase().includes('devocional')
        );
        
        let taskId;
        
        if (devTask) {
            // Tarefa existe: marcar como concluída
            console.log('Tarefa devocional encontrada:', devTask.id);
            taskId = devTask.id;
        } else {
            // Tarefa não existe: criar via POST
            console.log('Tarefa devocional não encontrada. Criando nova...');
            const createResponse = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: 'Devocional',
                    date: todayStr,
                    recurrence: null
                })
            });
            
            if (!createResponse.ok) {
                throw new Error('Erro ao criar tarefa devocional');
            }
            
            const newTask = await createResponse.json();
            taskId = newTask.id;
            console.log('Tarefa devocional criada:', taskId);
        }
        
        // Marca a tarefa como concluída via toggleTask
        await toggleTask(taskId, true);
        
        // Feedback visual de sucesso
        btn.textContent = '✨ Reflexão Anotada';
        
        // Mensagem de sucesso discreta
        const notification = document.createElement('div');
        notification.className = 'fixed bottom-4 right-4 bg-stone-600 dark:bg-stone-700 text-stone-50 px-6 py-3 rounded-lg shadow-lg text-sm font-medium';
        notification.textContent = '🙏 Devocional de hoje anotado no caderno';
        document.body.appendChild(notification);
        
        // Remove notificação após 3 segundos
        setTimeout(() => {
            notification.remove();
        }, 3000);
        
        // Aguarda um pouco antes de fechar a tela
        setTimeout(() => {
            // Fecha a tela devocional
            toggleDevotional();
            
            // Restaura o botão
            btn.textContent = originalText;
            btn.disabled = false;
        }, 1500);
        
    } catch (error) {
        console.error('Erro ao completar devocional:', error);
        
        // Exibe mensagem de erro
        const notification = document.createElement('div');
        notification.className = 'fixed bottom-4 right-4 bg-red-600 dark:bg-red-700 text-white px-6 py-3 rounded-lg shadow-lg text-sm font-medium';
        notification.textContent = '❌ Erro ao anotar devocional. Tente novamente.';
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
        
        // Restaura o botão em caso de erro
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

function printMonthly() {
    const month = document.getElementById('print-month').value;
    const year = document.getElementById('print-year-month').value;
    window.open(`/calendar/monthly?month=${month}&year=${year}`, '_blank');
}

function printAnnual() {
    const year = document.getElementById('print-year-annual').value;
    window.open(`/calendar/annual?year=${year}`, '_blank');
}

function printDailyLog() {
    const tasksToPrint = globalTasks.filter(t => t.date === selectedDateStr);
    const printWin = window.open('', '_blank');
    
    const [year, month, day] = selectedDateStr.split('-');
    const formattedDate = `${day}/${month}/${year}`;

    let tasksHtml = '';
    if (tasksToPrint.length === 0) {
        tasksHtml = '<li>Nenhuma tarefa para este dia.</li>';
    } else {
        tasksToPrint.forEach(task => {
            tasksHtml += `
                <li style="margin-bottom: 12px; font-size: 14pt; display: flex; align-items: center; gap: 12px;">
                    <div style="width: 16px; height: 16px; border: 2px solid #333; border-radius: 3px; display: inline-block; flex-shrink: 0;"></div> 
                    <span>${task.title}</span>
                </li>
            `;
        });
    }

    printWin.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Log Diário - ${formattedDate}</title>
            <style>
                @page { size: A5; margin: 15mm; }
                body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #111; line-height: 1.5; }
                h1 { text-align: center; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 20px; font-size: 18pt; text-transform: uppercase; letter-spacing: 1px;}
                ul { list-style-type: none; padding: 0; margin: 0; }
            </style>
        </head>
        <body>
            <h1>Log Diário - ${formattedDate}</h1>
            <ul>
                ${tasksHtml}
            </ul>
        </body>
        </html>
    `);
    
    printWin.document.close();
    setTimeout(() => { printWin.print(); }, 250);
}

// Inicialização e Event Listeners Globais
document.addEventListener('DOMContentLoaded', () => {
    // Carregamento inicial das tarefas
    const recurrenceContainer = document.getElementById('recurrence-container');
    if (recurrenceContainer) recurrenceContainer.innerHTML = createDaySelectorHTML(true, 'none');
    
    initSliderDesktop();
    renderDateSlider();
    loadTasks();

    // --- Lógica de Backup e Restauração ---
    const exportBtn = document.getElementById('export-backup-btn');
    const importInput = document.getElementById('import-backup-input');

    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            // A rota GET /backup/export força o download, então uma simples navegação de janela funciona.
            window.location.href = '/backup/export';
        });
    }

    if (importInput) {
        importInput.addEventListener('change', async (event) => {
            const file = event.target.files[0];
            if (!file) return;

            const confirmation = confirm(
                'ATENÇÃO!\n\nImportar um backup substituirá TODOS os dados atuais.\n\nEsta ação não pode ser desfeita. Deseja continuar?'
            );

            if (!confirmation) {
                importInput.value = ''; // Limpa a seleção do arquivo se o usuário cancelar
                return;
            }

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/backup/import', { method: 'POST', body: formData });
                const result = await response.json();
                if (!response.ok) throw new Error(result.detail || 'Ocorreu um erro desconhecido.');
                alert(result.detail || 'Backup importado com sucesso! A página será recarregada.');
                window.location.reload();
            } catch (error) {
                alert(`Falha na importação: ${error.message}`);
            } finally {
                importInput.value = ''; // Limpa a seleção em qualquer caso
            }
        });
    }
});

// Ativar edição inline da tarefa
// Ativar edição inline da tarefa
function toggleEditTask(id, currentTitle, currentDate) {
    const infoDiv = document.getElementById(`task-content-${id}`);
    const btn = document.getElementById(`edit-btn-${id}`);
    
    if (!infoDiv || !btn) return;

    infoDiv.innerHTML = `
        <input type="text" id="edit-task-title-${id}" value="${currentTitle}" class="w-full text-sm border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded shadow-sm focus:ring-indigo-500 focus:border-indigo-500 mb-1 px-2 py-1">
        <input type="date" id="edit-task-date-${id}" value="${currentDate}" class="w-full text-xs border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded shadow-sm focus:ring-indigo-500 focus:border-indigo-500 px-2 py-1">
    `;

    // Muda o botão para "Salvar" (ícone de ✔️) - SEM BARRAS INVERTIDAS
    btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-500 hover:text-green-600" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>`;
    btn.title = "Salvar Tarefa";
    btn.onclick = () => saveTask(id);
}

// Salvar edição da tarefa no Backend
async function saveTask(id) {
    // USANDO CRASE AQUI PARA LER A VARIÁVEL ${id} CORRETAMENTE
    const newTitle = document.getElementById(`edit-task-title-${id}`).value;
    const newDate = document.getElementById(`edit-task-date-${id}`).value;

    if (!newTitle.trim()) {
        alert('O título da tarefa não pode estar vazio.');
        return;
    }

    await fetch(`${API_URL}${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            title: newTitle, 
            date: newDate 
        })
    });

    await loadTasks();
}

/**
 * 4. COMPONENTES DINÂMICOS
 */
function createDaySelectorHTML(isMainForm = false, currentValue = 'daily') {
    // Verifica se o valor atual possui números indicando os dias (ex: '0,2,4')
    const isCustom = /[0-6]/.test(currentValue) && currentValue !== 'daily' && currentValue !== 'monthly' && currentValue !== 'none';
    const selectValue = isCustom ? 'custom' : currentValue;
    const customDaysArray = isCustom ? currentValue.split(',') : [];

    let optionsHtml = '';
    if (isMainForm) {
        optionsHtml += `<option value="none" ${selectValue === 'none' ? 'selected' : ''}>Não repetir</option>`;
    }
    optionsHtml += `
        <option value="daily" ${selectValue === 'daily' ? 'selected' : ''}>Todos os dias</option>
        <option value="custom" ${selectValue === 'custom' ? 'selected' : ''}>Dias Específicos</option>
        <option value="monthly" ${selectValue === 'monthly' ? 'selected' : ''}>Mensal</option>
    `;

    const days = [
        { label: 'S', val: '0' }, // Segunda
        { label: 'T', val: '1' }, // Terça
        { label: 'Q', val: '2' }, // Quarta
        { label: 'Q', val: '3' }, // Quinta
        { label: 'S', val: '4' }, // Sexta
        { label: 'S', val: '5' }, // Sábado
        { label: 'D', val: '6' }  // Domingo
    ];

    let daysHtml = '';
    days.forEach(d => {
        const isActive = customDaysArray.includes(d.val);
        const btnClass = isActive ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-600';
        daysHtml += `<button type="button" data-day="${d.val}" class="w-8 h-8 rounded-full text-xs font-bold transition-colors ${btnClass}" onclick="this.classList.toggle('bg-indigo-600'); this.classList.toggle('text-white'); this.classList.toggle('bg-gray-200'); this.classList.toggle('text-gray-600');">${d.label}</button>`;
    });

    return `
        <select class="recurrence-select w-full text-xs border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded shadow-sm focus:ring-indigo-500 focus:border-indigo-500 px-2 py-1 mb-2"
            onchange="this.nextElementSibling.classList.toggle('hidden', this.value !== 'custom')">
            ${optionsHtml}
        </select>
        <div class="custom-days-container flex gap-1 justify-center mt-2 ${isCustom ? '' : 'hidden'}">
            ${daysHtml}
        </div>
    `;
}