// Checklist shared state and utility helpers

(function() {
    'use strict';

    const app = window.TimingChecklistApp || {};

    app.state = app.state || {
        currentProject: '',
        checklistData: null,
        editMode: false,
        checklistScopeContext: null
    };

    app.MILESTONE_ORDER = ['prelim', 'prefinal', 'final', 'swap_gds'];

    app.utils = {
        parseIsoDate(dateText) {
            if (!dateText || typeof dateText !== 'string') return null;
            const value = new Date(`${dateText}T00:00:00`);
            return Number.isNaN(value.getTime()) ? null : value;
        },

        todayAtMidnight() {
            const now = new Date();
            return new Date(now.getFullYear(), now.getMonth(), now.getDate());
        },

        addDays(baseDate, days) {
            const next = new Date(baseDate);
            next.setDate(next.getDate() + days);
            return next;
        },

        formatDate(dateValue) {
            if (!(dateValue instanceof Date) || Number.isNaN(dateValue.getTime())) return 'N/A';
            return dateValue.toISOString().split('T')[0];
        },

        normalizeMilestone(value) {
            const text = String(value || '').trim().toLowerCase().replace(/\s+/g, '_');
            if (!text) return '';
            if (text.includes('swap') && text.includes('gds')) return 'swap_gds';
            if (text.includes('prelim') && !text.includes('prefinal')) return 'prelim';
            if (text.includes('prefinal')) return 'prefinal';
            if (text === 'final' || text.endsWith('_final') || text.includes('final_release')) return 'final';
            return text;
        },

        milestoneLabel(milestone) {
            const normalized = app.utils.normalizeMilestone(milestone);
            if (normalized === 'prelim') return 'Preliminary';
            if (normalized === 'prefinal') return 'Prefinal';
            if (normalized === 'final') return 'Final';
            if (normalized === 'swap_gds') return 'SwapGDS';
            return milestone || 'Unknown';
        },

        deriveSectionMilestone(section) {
            const explicit = app.utils.normalizeMilestone(section && section.milestone);
            if (explicit) return explicit;

            const title = String((section && section.title) || '').toLowerCase();
            if (title.includes('swap') && title.includes('gds')) return 'swap_gds';
            if (title.includes('prefinal')) return 'prefinal';
            if (title.includes('prelim')) return 'prelim';
            if (title.includes('final')) return 'final';
            return '';
        },

        matchesProjectName(candidate, project) {
            const left = String(candidate || '').trim().replace(/^\/+/, '').toLowerCase();
            const right = String(project || '').trim().replace(/^\/+/, '').toLowerCase();
            return left && right && left === right;
        },

        getSelectedProject() {
            try {
                return localStorage.getItem('timing_selected_project') ||
                       sessionStorage.getItem('timing_selected_project') || '';
            } catch (_) {
                return '';
            }
        },

        showModal() {
            const modal = document.getElementById('checklistModal');
            if (modal) modal.showModal();
        },

        updateChecklistNavIndicator(completedTasks, totalTasks) {
            const badge = document.getElementById('checklistNavIndicator');
            if (!badge) return;

            const remainingTasks = Math.max(totalTasks - completedTasks, 0);
            if (remainingTasks > 0) {
                badge.textContent = String(remainingTasks);
                badge.classList.remove('hidden');
            } else {
                badge.classList.add('hidden');
            }
        }
    };

    window.TimingChecklistApp = app;
})();
