// Checklist modal UI rendering and interactions

(function() {
    'use strict';

    const app = window.TimingChecklistApp;
    if (!app || !app.utils || !app.scope) return;

    const { state, utils, scope, MILESTONE_ORDER } = app;

    async function loadChecklist(refresh = false) {
        console.log('[Checklist] Loading checklist, refresh=', refresh);

        state.currentProject = utils.getSelectedProject();

        if (!state.currentProject) {
            alert('Please select a project first from the home page');
            return;
        }

        const loadingDiv = document.getElementById('checklistLoading');
        const contentDiv = document.getElementById('checklistContent');
        const errorDiv = document.getElementById('checklistError');

        if (loadingDiv) loadingDiv.classList.remove('hidden');
        if (contentDiv) contentDiv.classList.add('hidden');
        if (errorDiv) errorDiv.classList.add('hidden');

        try {
            state.checklistScopeContext = await scope.loadChecklistScopeContext(state.currentProject);

            const url = `/api/checklist?project=${encodeURIComponent(state.currentProject)}&refresh=${refresh}`;
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('[Checklist] Data received:', result);

            state.checklistData = result.data;
            renderChecklist(state.checklistData);

            if (loadingDiv) loadingDiv.classList.add('hidden');
            if (contentDiv) contentDiv.classList.remove('hidden');
        } catch (error) {
            console.error('[Checklist] Error loading:', error);
            if (loadingDiv) loadingDiv.classList.add('hidden');
            if (errorDiv) {
                errorDiv.textContent = `Error loading checklist: ${error.message}`;
                errorDiv.classList.remove('hidden');
            }
        }
    }

    function isSectionCompleted(section) {
        let totalTasks = 0;
        let completedTasks = 0;

        (section.task_groups || []).forEach(taskGroup => {
            (taskGroup.tasks || []).forEach(task => {
                totalTasks += 1;
                if (task.done) completedTasks += 1;
            });
        });

        return totalTasks > 0 && completedTasks === totalTasks;
    }

    function getSectionCollapseStorageKey() {
        const projectKey = state.currentProject || 'unknown';
        return `timing_checklist_sections_open_${projectKey}`;
    }

    function getDefaultOpenSectionIndex(data) {
        const firstIncomplete = (data || []).findIndex(section => !isSectionCompleted(section));
        return firstIncomplete >= 0 ? firstIncomplete : 0;
    }

    function loadSavedSectionOpenStates(dataLength, defaultOpenIndex) {
        const fallback = Array.from({ length: dataLength }, (_, idx) => idx === defaultOpenIndex);

        try {
            const raw = localStorage.getItem(getSectionCollapseStorageKey());
            if (!raw) return fallback;

            const parsed = JSON.parse(raw);
            if (!Array.isArray(parsed) || parsed.length !== dataLength) return fallback;
            return parsed.map(Boolean);
        } catch (_) {
            return fallback;
        }
    }

    function saveSectionOpenStates(states) {
        try {
            localStorage.setItem(getSectionCollapseStorageKey(), JSON.stringify(states));
        } catch (_) {
            // Ignore storage errors
        }
    }

    function readSectionOpenStatesFromDom(dataLength) {
        const inputs = document.querySelectorAll('#checklistContent input[type="checkbox"][data-section-collapse]');
        if (!inputs || inputs.length !== dataLength) return null;

        const states = Array.from(inputs)
            .sort((a, b) => parseInt(a.dataset.sectionCollapse, 10) - parseInt(b.dataset.sectionCollapse, 10))
            .map(input => input.checked);

        return states.length === dataLength ? states : null;
    }

    function attachSectionCollapseListeners(dataLength) {
        const inputs = document.querySelectorAll('#checklistContent input[type="checkbox"][data-section-collapse]');
        if (!inputs || inputs.length !== dataLength) return;

        const persist = () => {
            const states = Array.from(inputs)
                .sort((a, b) => parseInt(a.dataset.sectionCollapse, 10) - parseInt(b.dataset.sectionCollapse, 10))
                .map(input => input.checked);
            saveSectionOpenStates(states);
        };

        inputs.forEach(input => {
            input.addEventListener('change', persist);
        });
    }

    function getTaskGroupCollapseStorageKey() {
        const projectKey = state.currentProject || 'unknown';
        return `timing_checklist_taskgroups_open_${projectKey}`;
    }

    function buildTaskGroupKey(sectionIdx, tgIdx) {
        return `${sectionIdx}:${tgIdx}`;
    }

    function getDefaultOpenTaskGroupStates(data) {
        const defaults = {};

        (data || []).forEach((section, sectionIdx) => {
            const groups = section.task_groups || [];
            if (!groups.length) return;

            const firstIncompleteIndex = groups.findIndex(group => {
                const tasks = group.tasks || [];
                if (!tasks.length) return true;
                return !tasks.every(task => task.done);
            });

            const openIndex = firstIncompleteIndex >= 0 ? firstIncompleteIndex : 0;
            groups.forEach((_, tgIdx) => {
                defaults[buildTaskGroupKey(sectionIdx, tgIdx)] = tgIdx === openIndex;
            });
        });

        return defaults;
    }

    function normalizeTaskGroupStates(data, candidate, fallback) {
        const normalized = {};
        (data || []).forEach((section, sectionIdx) => {
            (section.task_groups || []).forEach((_, tgIdx) => {
                const key = buildTaskGroupKey(sectionIdx, tgIdx);
                if (candidate && Object.prototype.hasOwnProperty.call(candidate, key)) {
                    normalized[key] = Boolean(candidate[key]);
                } else {
                    normalized[key] = Boolean(fallback[key]);
                }
            });
        });
        return normalized;
    }

    function loadSavedTaskGroupOpenStates(data) {
        const fallback = getDefaultOpenTaskGroupStates(data);

        try {
            const raw = localStorage.getItem(getTaskGroupCollapseStorageKey());
            if (!raw) return fallback;
            const parsed = JSON.parse(raw);
            if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
                return fallback;
            }
            return normalizeTaskGroupStates(data, parsed, fallback);
        } catch (_) {
            return fallback;
        }
    }

    function saveTaskGroupOpenStates(states) {
        try {
            localStorage.setItem(getTaskGroupCollapseStorageKey(), JSON.stringify(states));
        } catch (_) {
            // Ignore storage errors
        }
    }

    function readTaskGroupOpenStatesFromDom(data) {
        const inputs = document.querySelectorAll('#checklistContent input[type="checkbox"][data-taskgroup-collapse]');
        if (!inputs || !inputs.length) return null;

        const states = {};
        inputs.forEach(input => {
            const key = input.dataset.taskgroupCollapse;
            if (key) states[key] = input.checked;
        });

        return normalizeTaskGroupStates(data, states, getDefaultOpenTaskGroupStates(data));
    }

    function attachTaskGroupCollapseListeners(data) {
        const inputs = document.querySelectorAll('#checklistContent input[type="checkbox"][data-taskgroup-collapse]');
        if (!inputs || !inputs.length) return;

        const persist = () => {
            const states = readTaskGroupOpenStatesFromDom(data);
            if (states) saveTaskGroupOpenStates(states);
        };

        inputs.forEach(input => {
            input.addEventListener('change', persist);
        });
    }

    function buildMilestoneDateRangeMap(scopeContext) {
        const ranges = {};
        const milestones = scopeContext && Array.isArray(scopeContext.milestones) ? scopeContext.milestones : [];

        milestones.forEach(item => {
            if (!item || !item.milestone || !item.startDate || !item.endDate) return;

            const key = item.milestone;
            const existing = ranges[key];
            if (!existing) {
                ranges[key] = {
                    startDate: item.startDate,
                    endDate: item.endDate
                };
                return;
            }

            if (item.startDate < existing.startDate) {
                existing.startDate = item.startDate;
            }
            if (item.endDate > existing.endDate) {
                existing.endDate = item.endDate;
            }
        });

        return ranges;
    }

    function renderChecklist(data) {
        const contentDiv = document.getElementById('checklistContent');
        if (!contentDiv || !data) return;

        const defaultOpenSectionIndex = getDefaultOpenSectionIndex(data);
        const domOpenStates = readSectionOpenStatesFromDom(data.length);
        const sectionOpenStates = domOpenStates || loadSavedSectionOpenStates(data.length, defaultOpenSectionIndex);
        if (domOpenStates) {
            saveSectionOpenStates(domOpenStates);
        }

        const domTaskGroupOpenStates = readTaskGroupOpenStatesFromDom(data);
        const taskGroupOpenStates = domTaskGroupOpenStates || loadSavedTaskGroupOpenStates(data);
        if (domTaskGroupOpenStates) {
            saveTaskGroupOpenStates(domTaskGroupOpenStates);
        }

        const { completedTasks, totalTasks } = scope.getChecklistProgress(data, state.checklistScopeContext);
        utils.updateChecklistNavIndicator(completedTasks, totalTasks);
        const allDone = totalTasks > 0 && completedTasks === totalTasks;
        const badgeClass = allDone ? 'badge-success' : 'badge-warning';
        const milestoneDateRanges = buildMilestoneDateRangeMap(state.checklistScopeContext);

        let html = `
            ${state.checklistScopeContext && state.checklistScopeContext.hasMilestoneData ? '' : `
                <div class="alert alert-info mb-4">
                    <span>Milestone date data is unavailable. Counting all checklist items.</span>
                </div>
            `}
            <div class="mb-4 flex justify-end">
                <span class="badge ${badgeClass} badge-lg font-semibold">
                    ${completedTasks}/${totalTasks} completed
                </span>
            </div>
        `;

        data.forEach((section, sectionIdx) => {
            const sectionMilestone = utils.deriveSectionMilestone(section);
            const currentMilestone = state.checklistScopeContext && state.checklistScopeContext.currentMilestone;
            const currentMilestoneIndex = state.checklistScopeContext ? state.checklistScopeContext.currentMilestoneIndex : -1;
            const sectionMilestoneIndex = MILESTONE_ORDER.indexOf(sectionMilestone);
            const isFutureSection = currentMilestone && sectionMilestoneIndex > currentMilestoneIndex;
            const isCurrentSection = currentMilestone && sectionMilestoneIndex === currentMilestoneIndex;
            const isSectionDone = isSectionCompleted(section);
            const timelineDotClass = isSectionDone
                ? 'bg-success ring-2 ring-success/30'
                : (isCurrentSection ? 'bg-warning ring-4 ring-warning/30 animate-pulse' : 'bg-base-300 border border-base-content/20');
            const timelineLineClass = isFutureSection ? 'bg-base-300' : 'bg-success/40';
            const isLastSection = sectionIdx === data.length - 1;
            const sectionDateRange = milestoneDateRanges[sectionMilestone];
            const sectionDateText = sectionDateRange
                ? `${utils.formatDate(sectionDateRange.startDate)} -> ${utils.formatDate(sectionDateRange.endDate)}`
                : '';

            html += `
                <div class="flex gap-3 mb-4">
                    <div class="flex flex-col items-center pt-4 w-5 shrink-0">
                        <span class="w-3 h-3 rounded-full ${timelineDotClass}"></span>
                        ${isLastSection ? '' : `<span class="w-px flex-1 mt-1 ${timelineLineClass}"></span>`}
                    </div>
                    <div class="flex-1">
                        <div class="collapse collapse-plus bg-base-200 ${isFutureSection ? 'opacity-60' : ''}">
                            <input type="checkbox" data-section-collapse="${sectionIdx}" ${sectionOpenStates[sectionIdx] ? 'checked' : ''} />
                            <div class="collapse-title text-xl font-bold">
                                <div class="flex items-center gap-2 flex-wrap">
                                    <span>${section.title}</span>
                                    ${isFutureSection ? '<span class="badge badge-outline badge-sm">Upcoming phase</span>' : ''}
                                </div>
                                ${sectionDateText ? `<div class="text-xs font-normal text-base-content/70 mt-1">${sectionDateText}</div>` : ''}
                            </div>
                            <div class="collapse-content">
            `;

            section.task_groups.forEach((taskGroup, tgIdx) => {
                const isCurrentMilestone = sectionMilestone && state.checklistScopeContext && sectionMilestone === state.checklistScopeContext.currentMilestone;
                let isGroupUnlocked = true;

                if (isCurrentMilestone && state.checklistScopeContext.currentMilestoneStart) {
                    let cumulativeDays = 0;
                    for (let i = 0; i < tgIdx; i += 1) {
                        const prevDuration = parseInt((section.task_groups[i] || {}).duration, 10);
                        cumulativeDays += (Number.isFinite(prevDuration) && prevDuration > 0 ? prevDuration : 1) * 7;
                    }
                    const groupStartDate = utils.addDays(state.checklistScopeContext.currentMilestoneStart, cumulativeDays);
                    isGroupUnlocked = state.checklistScopeContext.today >= groupStartDate;
                }

                if (state.checklistScopeContext && state.checklistScopeContext.currentMilestone) {
                    if (sectionMilestoneIndex > currentMilestoneIndex) {
                        isGroupUnlocked = false;
                    }
                }

                const groupTasks = taskGroup.tasks || [];
                const isTaskGroupDone = groupTasks.length > 0 && groupTasks.every(task => task.done);
                const taskGroupTitleClass = isTaskGroupDone ? 'text-success' : '';
                const taskGroupDoneIndicator = isTaskGroupDone
                    ? '<span class="inline-flex items-center justify-center w-5 h-5 rounded-full border border-success text-success text-xs font-bold">✓</span>'
                    : '';
                const taskGroupKey = buildTaskGroupKey(sectionIdx, tgIdx);

                html += `
                    <div class="collapse collapse-arrow bg-base-100 mb-2 ${isGroupUnlocked ? '' : 'opacity-60'}">
                        <input type="checkbox" data-taskgroup-collapse="${taskGroupKey}" ${taskGroupOpenStates[taskGroupKey] ? 'checked' : ''} />
                        <div class="collapse-title font-semibold flex items-center gap-2">
                            ${taskGroupDoneIndicator}
                            <span class="${taskGroupTitleClass}">${taskGroup.title}</span>
                            <span class="badge badge-ghost badge-sm">${taskGroup.duration} week(s)</span>
                            ${isGroupUnlocked ? '' : '<span class="badge badge-outline badge-sm">Not in current date window</span>'}
                        </div>
                        <div class="collapse-content">
                            <div class="space-y-2">
                `;

                taskGroup.tasks.forEach((task, taskIdx) => {
                    const itemId = `item-${sectionIdx}-${tgIdx}-${taskIdx}`;
                    const checked = task.done ? 'checked' : '';
                    const disabled = state.editMode ? '' : 'disabled';
                    const taskTextClass = task.done ? 'text-success' : '';
                    const taskLabelCursorClass = state.editMode ? 'cursor-pointer' : 'cursor-default';
                    const taskStatusIndicator = !state.editMode
                        ? (task.done
                            ? '<span class="mt-1 inline-flex items-center justify-center w-5 h-5 rounded-full border border-success text-success text-xs font-bold">✓</span>'
                            : '<span class="mt-1 inline-flex items-center justify-center w-5 h-5 rounded-full border border-base-300"></span>')
                        : `
                            <input
                                type="checkbox"
                                id="${itemId}"
                                class="checkbox checkbox-sm mt-1 checkbox-success"
                                ${checked}
                                ${disabled}
                                data-section="${sectionIdx}"
                                data-taskgroup="${tgIdx}"
                                data-task="${taskIdx}"
                            />
                        `;

                    html += `
                        <div class="flex items-start gap-2 p-2 bg-base-200 rounded">
                            ${taskStatusIndicator}
                            <div class="flex-1">
                                <label for="${itemId}" class="${taskLabelCursorClass} ${taskTextClass}">
                                    ${task.item}
                                </label>
                                ${task.date ? `<div class="text-xs text-base-content/60 mt-1">Updated: ${task.date}</div>` : ''}
                                ${task.note ? `<div class="text-xs text-base-content/70 mt-1 italic">${task.note}</div>` : ''}
                            </div>
                        </div>
                    `;
                });

                html += `
                            </div>
                        </div>
                    </div>
                `;
            });

            html += `
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        contentDiv.innerHTML = html;

        attachSectionCollapseListeners(data.length);
        attachTaskGroupCollapseListeners(data);

        if (state.editMode) {
            attachCheckboxListeners();
        }
    }

    function attachCheckboxListeners() {
        const checkboxes = document.querySelectorAll('#checklistContent input[type="checkbox"][data-section]');

        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const sectionIdx = parseInt(e.target.dataset.section, 10);
                const tgIdx = parseInt(e.target.dataset.taskgroup, 10);
                const taskIdx = parseInt(e.target.dataset.task, 10);

                const task = state.checklistData[sectionIdx].task_groups[tgIdx].tasks[taskIdx];

                const note = prompt('Please add a note for this change:', task.note || '');
                if (note === null) {
                    e.target.checked = task.done;
                    return;
                }

                task.done = e.target.checked;
                task.note = note;
                task.date = new Date().toISOString().split('T')[0];

                renderChecklist(state.checklistData);
            });
        });
    }

    async function enterEditMode() {
        console.log('[Checklist] Entering edit mode...');

        const editBtn = document.getElementById('checklistEditBtn');
        if (editBtn) {
            editBtn.disabled = true;
            editBtn.innerHTML = '<span class="loading loading-spinner loading-sm"></span> Loading...';
        }

        await loadChecklist(true);

        state.editMode = true;

        if (editBtn) {
            editBtn.classList.add('hidden');
        }

        const saveBtn = document.getElementById('checklistSaveBtn');
        if (saveBtn) {
            saveBtn.classList.remove('hidden');
        }

        renderChecklist(state.checklistData);
    }

    async function saveChanges() {
        console.log('[Checklist] Saving changes...');

        const saveBtn = document.getElementById('checklistSaveBtn');
        if (saveBtn) {
            saveBtn.disabled = true;
            saveBtn.innerHTML = '<span class="loading loading-spinner loading-sm"></span> Saving...';
        }

        try {
            const response = await fetch('/api/checklist', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    project: state.currentProject,
                    data: state.checklistData
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            await response.json();

            state.editMode = false;

            if (saveBtn) {
                saveBtn.classList.add('hidden');
            }

            const editBtn = document.getElementById('checklistEditBtn');
            if (editBtn) {
                editBtn.classList.remove('hidden');
                editBtn.disabled = false;
                editBtn.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                    </svg>
                    Edit
                `;
            }

            renderChecklist(state.checklistData);
            alert('Checklist saved successfully!');
        } catch (error) {
            console.error('[Checklist] Error saving:', error);
            alert(`Error saving checklist: ${error.message}`);

            if (saveBtn) {
                saveBtn.disabled = false;
                saveBtn.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M7.707 10.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V6h5a2 2 0 012 2v7a2 2 0 01-2 2H4a2 2 0 01-2-2V8a2 2 0 012-2h5v5.586l-1.293-1.293zM9 4a1 1 0 012 0v2H9V4z" />
                    </svg>
                    Save
                `;
            }
        }
    }

    function initChecklistModal() {
        console.log('[Checklist] Initializing modal...');

        const navbarButtons = document.querySelector('.navbar .flex-none');
        if (navbarButtons) {
            const checklistBtn = document.createElement('button');
            checklistBtn.id = 'checklistNavBtn';
            checklistBtn.className = 'btn btn-ghost btn-sm btn-circle';
            checklistBtn.title = 'Project Checklist';
            checklistBtn.innerHTML = `
                <div class="indicator">
                    <span id="checklistNavIndicator" class="indicator-item badge badge-error badge-xs hidden">0</span>
                    <img src="/theme/logo/checklist-on-clipboard.svg"
                         alt="Checklist"
                         class="w-8 h-8" />
                </div>
            `;
            checklistBtn.addEventListener('click', () => {
                loadChecklist(false);
                utils.showModal();
            });

            const themeToggle = document.getElementById('themeToggle');
            if (themeToggle) {
                navbarButtons.insertBefore(checklistBtn, themeToggle);
            } else {
                navbarButtons.appendChild(checklistBtn);
            }
        }

        const editBtn = document.getElementById('checklistEditBtn');
        if (editBtn) {
            editBtn.addEventListener('click', enterEditMode);
        }

        const saveBtn = document.getElementById('checklistSaveBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', saveChanges);
        }

        scope.preloadChecklistNavIndicator();
        console.log('[Checklist] Modal initialized');
    }

    app.ui = {
        loadChecklist,
        renderChecklist,
        enterEditMode,
        saveChanges,
        initChecklistModal
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initChecklistModal);
    } else {
        initChecklistModal();
    }

    window.TimingChecklistApp = app;
})();
