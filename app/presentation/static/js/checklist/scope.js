// Checklist milestone scope and progress logic

(function() {
    'use strict';

    const app = window.TimingChecklistApp;
    if (!app || !app.utils) return;

    const { state, utils, MILESTONE_ORDER } = app;

    async function fetchProjectMilestones(project) {
        const query = `?t=${Date.now()}`;
        let response = await fetch(`/cache/global_project_status.json${query}`);

        if (!response.ok) {
            await fetch('/api/gantt/refresh', { method: 'POST' });
            response = await fetch(`/cache/global_project_status.json${query}`);
        }

        if (!response.ok) return [];
        const data = await response.json();
        if (!Array.isArray(data)) return [];

        return data
            .filter(item => utils.matchesProjectName(item.task, project))
            .map(item => {
                const milestone = utils.normalizeMilestone(item.milestone);
                const startDate = utils.parseIsoDate(item.start);
                const endDate = utils.parseIsoDate(item.end);
                return {
                    milestone,
                    startDate,
                    endDate,
                    raw: item
                };
            })
            .filter(item => item.milestone && item.startDate && item.endDate)
            .sort((a, b) => {
                const aIdx = MILESTONE_ORDER.indexOf(a.milestone);
                const bIdx = MILESTONE_ORDER.indexOf(b.milestone);
                const left = aIdx === -1 ? 999 : aIdx;
                const right = bIdx === -1 ? 999 : bIdx;
                if (left !== right) return left - right;
                return a.startDate - b.startDate;
            });
    }

    async function loadChecklistScopeContext(project) {
        const today = utils.todayAtMidnight();

        try {
            const milestones = await fetchProjectMilestones(project);
            if (!milestones.length) {
                return {
                    today,
                    milestones,
                    hasMilestoneData: false,
                    hasActiveMilestoneToday: false,
                    currentMilestone: '',
                    currentMilestoneStart: null,
                    currentMilestoneEnd: null,
                    currentMilestoneIndex: -1,
                    currentMilestoneLabel: ''
                };
            }

            const current = milestones.find(item => today >= item.startDate && today <= item.endDate) || null;
            const latestPast = milestones.filter(item => today > item.endDate).slice(-1)[0] || null;
            const earliestFuture = milestones.find(item => today < item.startDate) || null;
            const scopedMilestone = current || latestPast || earliestFuture || null;
            const projectStart = milestones.reduce((acc, item) => (acc && acc < item.startDate ? acc : item.startDate), null);
            const projectEnd = milestones.reduce((acc, item) => (acc && acc > item.endDate ? acc : item.endDate), null);

            const currentMilestone = scopedMilestone ? scopedMilestone.milestone : '';
            const currentMilestoneIndex = currentMilestone ? MILESTONE_ORDER.indexOf(currentMilestone) : -1;

            return {
                today,
                milestones,
                projectStart,
                projectEnd,
                hasMilestoneData: true,
                hasActiveMilestoneToday: Boolean(current),
                currentMilestone,
                currentMilestoneStart: scopedMilestone ? scopedMilestone.startDate : null,
                currentMilestoneEnd: scopedMilestone ? scopedMilestone.endDate : null,
                currentMilestoneIndex,
                currentMilestoneLabel: utils.milestoneLabel(currentMilestone)
            };
        } catch (_) {
            return {
                today,
                milestones: [],
                hasMilestoneData: false,
                hasActiveMilestoneToday: false,
                currentMilestone: '',
                currentMilestoneStart: null,
                currentMilestoneEnd: null,
                currentMilestoneIndex: -1,
                currentMilestoneLabel: ''
            };
        }
    }

    function getChecklistProgress(data, scopeContext) {
        const shouldScope = scopeContext && scopeContext.hasMilestoneData && scopeContext.currentMilestone;
        const today = scopeContext && scopeContext.today ? scopeContext.today : utils.todayAtMidnight();
        const currentMilestoneIndex = shouldScope ? scopeContext.currentMilestoneIndex : -1;
        const currentMilestoneStart = shouldScope ? scopeContext.currentMilestoneStart : null;

        let totalTasks = 0;
        let completedTasks = 0;

        (data || []).forEach(section => {
            const sectionMilestone = utils.deriveSectionMilestone(section);
            const sectionMilestoneIndex = MILESTONE_ORDER.indexOf(sectionMilestone);

            if (shouldScope) {
                if (sectionMilestoneIndex === -1 || sectionMilestoneIndex > currentMilestoneIndex) {
                    return;
                }
            }

            let cumulativeDays = 0;
            (section.task_groups || []).forEach(taskGroup => {
                if (shouldScope && sectionMilestone === scopeContext.currentMilestone && currentMilestoneStart) {
                    const durationWeeks = parseInt(taskGroup.duration, 10);
                    const safeWeeks = Number.isFinite(durationWeeks) && durationWeeks > 0 ? durationWeeks : 1;
                    const groupStartDate = utils.addDays(currentMilestoneStart, cumulativeDays);
                    cumulativeDays += safeWeeks * 7;

                    if (today < groupStartDate) {
                        return;
                    }
                }

                (taskGroup.tasks || []).forEach(task => {
                    totalTasks += 1;
                    if (task.done) completedTasks += 1;
                });
            });
        });

        return { completedTasks, totalTasks };
    }

    async function preloadChecklistNavIndicator() {
        const project = utils.getSelectedProject();
        if (!project) return;

        try {
            state.checklistScopeContext = await loadChecklistScopeContext(project);
            const url = `/api/checklist?project=${encodeURIComponent(project)}&refresh=false`;
            const response = await fetch(url);
            if (!response.ok) return;

            const result = await response.json();
            const data = result && result.data ? result.data : null;
            if (!data) return;

            const { completedTasks, totalTasks } = getChecklistProgress(data, state.checklistScopeContext);
            utils.updateChecklistNavIndicator(completedTasks, totalTasks);
        } catch (_) {
            // Ignore preload failures; modal load still handles full error display.
        }
    }

    app.scope = {
        fetchProjectMilestones,
        loadChecklistScopeContext,
        getChecklistProgress,
        preloadChecklistNavIndicator
    };

    window.TimingChecklistApp = app;
})();
