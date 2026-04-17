// Timing QA v2: Agent Failure Analysis viewer

(function(global) {
  'use strict';

  async function fetchBasePath() {
    try {
      const res = await fetch('/api/config/base-path');
      if (res.ok) {
        const data = await res.json();
        return data.base_path;
      }
    } catch (_) {}
    return '';
  }

  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} fixed bottom-4 right-4 w-auto max-w-sm shadow-lg z-50`;
    toast.innerHTML = `<span>${message}</span>`;
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.remove();
    }, 3000);
  }

  function escapeHtml(input) {
    return String(input)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  async function openAgentFailureAnalysis(project, subproject, cell) {
    if (!project || !subproject || !cell) {
      console.error('[Agent Failure Analysis] Missing required parameters');
      return;
    }

    const viewerWindow = window.open('', '_blank');
    if (!viewerWindow) {
      showToast('Popup blocked. Please allow popups for this site.', 'warning');
      return;
    }

    try {
      const base = await fetchBasePath();
      const sep = base.includes('\\') ? '\\' : '/';
      const filePath = `${base}${sep}${project}${sep}${subproject}${sep}design${sep}timing${sep}release${sep}process${sep}${cell}${sep}timing_qa_analysis_output${sep}Quick_Summary.txt`;

      console.log('[Agent Failure Analysis] Path:', filePath);

      const res = await fetch('/api/files/read', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ path: filePath }),
      });

      if (!res.ok) {
        let detail = 'Failed to read analysis file';
        try {
          const err = await res.json();
          detail = err.detail || detail;
        } catch (_) {}
        throw new Error(detail);
      }

      const data = await res.json();
      const content = data.content || '';
      const safeContent = escapeHtml(content);
      const safeTitle = escapeHtml(`Agent Failure Analysis - ${cell}`);

      viewerWindow.document.write(`<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>${safeTitle}</title>
  <style>
    body { margin: 0; padding: 16px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; background: #0f172a; color: #e2e8f0; }
    .header { font-size: 14px; margin-bottom: 12px; color: #93c5fd; }
    pre { white-space: pre-wrap; word-break: break-word; line-height: 1.4; background: #111827; border: 1px solid #334155; border-radius: 8px; padding: 12px; }
  </style>
</head>
<body>
  <div class="header">${safeTitle}</div>
  <pre>${safeContent}</pre>
</body>
</html>`);
      viewerWindow.document.close();

      showToast('Opened agent failure analysis', 'success');
    } catch (err) {
      console.error('[Agent Failure Analysis] Error:', err);
      viewerWindow.document.write('<pre style="padding:16px;font-family:monospace;">Failed to open analysis file.</pre>');
      viewerWindow.document.close();
      showToast(`Error opening analysis: ${err.message}`, 'error');
    }
  }

  function getCellNameFromLabel(label) {
    const nameSpan = label.querySelector('span.truncate');
    if (!nameSpan) return '';
    return (nameSpan.getAttribute('title') || nameSpan.textContent || '').trim();
  }

  function attachAgentFailureButtons() {
    const labels = document.querySelectorAll('#qaV2CellFilters label');
    if (!labels || labels.length === 0) return;

    labels.forEach((label) => {
      let btn = label.querySelector('.qaV2-open-agent-failure-btn');
      if (btn) {
        const cell = getCellNameFromLabel(label);
        if (cell) btn.setAttribute('data-cell', cell);
        return;
      }

      btn = document.createElement('button');
      btn.className = 'btn btn-ghost btn-xs qaV2-open-agent-failure-btn';
      btn.title = 'View agent failure analysis';
      btn.setAttribute('aria-label', 'View agent failure analysis');
      btn.innerHTML = `
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v4m0 4h.01M5.07 19h13.86c1.54 0 2.5-1.67 1.73-3L13.73 4c-.77-1.33-2.69-1.33-3.46 0L3.34 16c-.77 1.33.19 3 1.73 3z"></path>
        </svg>
      `;

      const cell = getCellNameFromLabel(label);
      if (cell) btn.setAttribute('data-cell', cell);

      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const selectedCell = btn.getAttribute('data-cell') || getCellNameFromLabel(label);
        const sel = global.AppSelection ? global.AppSelection.get() : { project: '', subproject: '' };
        if (selectedCell) {
          openAgentFailureAnalysis(sel.project, sel.subproject, selectedCell);
        } else {
          console.error('[TMQA v2] Missing cell for agent failure analysis');
        }
      });

      label.appendChild(btn);
    });
  }

  function initAgentFailureButtonInjection() {
    const container = document.getElementById('qaV2CellFilters');
    if (!container) return;

    attachAgentFailureButtons();

    const observer = new MutationObserver(() => {
      attachAgentFailureButtons();
    });
    observer.observe(container, { childList: true, subtree: true });
  }

  global.QAV2AgentFailureViewer = {
    open: openAgentFailureAnalysis,
  };

  document.addEventListener('DOMContentLoaded', initAgentFailureButtonInjection);
})(window);
