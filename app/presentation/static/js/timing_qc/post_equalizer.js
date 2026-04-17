// Timing QC: Post-Equalizer Tab Handler
// This module handles loading and displaying Compatibility_Final.csv (read-only)

(function(global){
  'use strict';

  if(!global.QCSharedHttp || !global.QCState){
    console.error('[Timing QC] post_equalizer.js requires shared_http.js and state.js');
    return;
  }

  const { fetchJSON, escapeHTML } = global.QCSharedHttp;
  const { getSelectionState, getLoadedCell } = global.QCState;

  let postEqualizerData = [];
  let selectedRowIndex = null;

  async function loadPostEqualizerData(){
    const sel = getSelectionState();
    const cellSelect = document.getElementById('cellSelect');
    const cell = cellSelect?.value || getLoadedCell();

    if(!(sel.project && sel.subproject && cell)){
      updateStatus('Select a cell to load Compatibility_Final.csv');
      return;
    }

    updateStatus('Loading...');

    try {
      const url = `/api/qc/${sel.project}/${sel.subproject}/post-equalizer?cell=${encodeURIComponent(cell)}`;
      const data = await fetchJSON(url);

      postEqualizerData = data.rows || [];
      selectedRowIndex = null;
      renderPostEqualizerTable();

      if(data.exists){
        updateStatus(`Loaded ${postEqualizerData.length} rows from Compatibility_Final.csv`);
      } else {
        updateStatus('Compatibility_Final.csv not found');
      }
    } catch(error){
      console.error('[Post-Equalizer] Load error:', error);
      postEqualizerData = [];
      selectedRowIndex = null;
      renderPostEqualizerTable();
      updateStatus('Error loading Compatibility_Final.csv');
    }
  }

  function renderPostEqualizerTable(){
    const tbody = document.querySelector('#postEqualizerTable tbody');
    if(!tbody) return;

    if(postEqualizerData.length === 0){
      tbody.innerHTML = '<tr><td colspan="10" class="text-center italic opacity-60">No data</td></tr>';
      return;
    }

    const rows = postEqualizerData.map((row, idx) => {
      const cornerText = String(row.corner_status || '');
      const hasFail = cornerText.toUpperCase().includes('FAILED');
      const cornerClass = hasFail ? 'badge badge-error badge-sm' : 'badge badge-success badge-sm';

      const rowClass = selectedRowIndex === idx ? 'active' : '';

      return `
        <tr data-index="${idx}" class="cell-row hover:bg-base-200/60 transition-colors ${rowClass}">
          <td>${idx + 1}</td>
          <td>${escapeHTML(row.type)}</td>
          <td>${escapeHTML(row.pin)}</td>
          <td>${escapeHTML(row.related_pin)}</td>
          <td>${escapeHTML(row.when)}</td>
          <td>${escapeHTML(row.ff_max_min)}</td>
          <td>${escapeHTML(row.tt_max_min)}</td>
          <td>${escapeHTML(row.ss_max_min)}</td>
          <td>${escapeHTML(row.sf_max_min)}</td>
          <td><span class="${cornerClass}">${escapeHTML(cornerText || '-')}</span></td>
        </tr>
      `;
    }).join('');

    tbody.innerHTML = rows;
    updateSelectedRowClass();
  }

  function updateSelectedRowClass(){
    const rows = document.querySelectorAll('#postEqualizerTable tbody tr[data-index]');
    rows.forEach((rowEl) => {
      const idx = Number(rowEl.getAttribute('data-index'));
      if(idx === selectedRowIndex){
        rowEl.classList.add('active');
      } else {
        rowEl.classList.remove('active');
      }
    });
  }

  function wireRowSelection(){
    const tbody = document.querySelector('#postEqualizerTable tbody');
    if(!tbody || tbody.dataset.rowSelectionWired === '1') return;

    tbody.addEventListener('click', (event) => {
      const tr = event.target.closest('tr[data-index]');
      if(!tr) return;

      const idx = Number(tr.getAttribute('data-index'));
      if(Number.isNaN(idx)) return;

      selectedRowIndex = idx;
      updateSelectedRowClass();
    });

    tbody.dataset.rowSelectionWired = '1';
  }

  function updateStatus(text){
    const statusEl = document.getElementById('postEqualizerStatus');
    if(statusEl) statusEl.textContent = text;
  }

  global.QCPostEqualizer = {
    load: loadPostEqualizerData
  };

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', wireRowSelection);
  } else {
    wireRowSelection();
  }

})(window);
