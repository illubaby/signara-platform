// Internal Timing Report Generator
// Adds "Gen Report" button beside the Run button without modifying layout_form

(function() {
  'use strict';

  /**
   * Inject "Gen Report" button beside the Run button
   */
  function injectGenReportButton() {
    // Prefer to place near our phase buttons or above execution output
    const phaseContainer = document.getElementById('intSimBtn') ? document.getElementById('intSimBtn').parentElement : null;
    const execContainer = document.getElementById('layoutFormExecution');
    const btnContainer = phaseContainer || (execContainer ? execContainer.parentElement : null);
    if (!btnContainer) {
      console.warn('[INT Report] Suitable container not found');
      return;
    }

    // Check if Gen Report button already exists
    if (document.getElementById('genReportBtn')) {
      console.log('[INT Report] Gen Report button already exists');
      return;
    }

    // Create Gen Report button
    const genReportBtn = document.createElement('button');
    genReportBtn.type = 'button';
    genReportBtn.id = 'genReportBtn';
    genReportBtn.className = 'btn btn-outline btn-info ml-3';
    genReportBtn.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      Gen Report
    `;

    // Insert at end of phase container or before execution block
    if (phaseContainer) {
      phaseContainer.appendChild(genReportBtn);
    } else if (execContainer) {
      execContainer.parentNode.insertBefore(genReportBtn, execContainer);
    }

    console.log('[INT Report] Gen Report button injected');

    // Wire click handler
    genReportBtn.addEventListener('click', handleGenReport);
  }

  /**
   * Handle Gen Report button click
   */
  async function handleGenReport() {
    const btn = document.getElementById('genReportBtn');
    if (!btn) return;

    // Get project and subproject from AppSelection
    const selection = window.AppSelection ? window.AppSelection.get() : { project: '', subproject: '' };
    const { project, subproject } = selection;

    if (!project || !subproject) {
      alert('Please select a project and subproject first');
      return;
    }

    // Get selected cell from block_path field
    const blockPathInput = document.getElementById('block_path') || document.querySelector('select[name="block_path"]');
    const cell = blockPathInput ? blockPathInput.value : '';

    // if (!cell || cell === '' || cell === 'dummy') {
    //   alert('Please select a cell from Block Path first');
    //   return;
    // }

    // Open a small popup window instead of modal
    try {
      const params = new URLSearchParams({
        project: project || '',
        subproject: subproject || '',
        cell: cell || '',
        embedded: '1'
      });

      const url = `/internal-timing-report?${params.toString()}`;
      console.log('[INT Report] Opening popup for:', { url });

      const features = [
        'popup=yes',
        'width=2000',
        'height=1000',
        'left=100',
        'top=100',
        'menubar=no',
        'toolbar=no',
        'location=no',
        'status=no',
        'resizable=yes',
        'scrollbars=yes'
      ].join(',');

      const popup = window.open(url, 'InternalTimingGenReport', features);
      if (!popup) {
        alert('Popup blocked. Please allow popups for this site.');
      } else {
        popup.focus();
      }
    } catch (err) {
      console.error('[INT Report] Failed to open popup:', err);
      alert(`Failed to open report window: ${err.message}`);
    }
  }

  /**
   * Initialize module
   */
  function init() {
    // Wait for layout_form to initialize
    setTimeout(injectGenReportButton, 500);
  }

  // Initialize on DOMContentLoaded
  window.addEventListener('DOMContentLoaded', init);
})();
