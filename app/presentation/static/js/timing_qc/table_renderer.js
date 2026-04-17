// Timing QC: Table Renderer
// This module handles table rendering, status classification, and UI updates

(function(global){
  'use strict';

  // Verify dependencies
  if(!global.QCSharedHttp || !global.QCState){
    console.error('[Timing QC] table_renderer.js requires shared_http.js and state.js');
    return;
  }

  const { escapeHTML } = global.QCSharedHttp;
  const { getFilteredTestbenches, getSelectedIndex, isImportantTestbench, getDelays } = global.QCState;

  // ------------------ Status Classification ------------------
  /**
   * Classify status and return label and CSS class
   * @param {string} raw - Raw status string
   * @returns {object} - {label: '', cls: ''}
   */
  function classifyStatus(raw){
    if(!raw) return {label: 'Not Started', cls: 'badge-ghost'};
    
    const s = raw.toLowerCase();
    
    // Exact matches
    if(s === 'passed') return {label: 'Passed', cls: 'badge-success'};
    if(s === 'fail' || s === 'failed') return {label: 'Fail', cls: 'badge-error'};
    if(s === 'not started') return {label: 'Not Started', cls: 'badge-ghost'};
    if(s === 'in progress') return {label: 'In Progress', cls: 'badge-warning'};
    
    // Heuristics
    if(/fail|error|fatal|missing/.test(s)) return {label: 'Fail', cls: 'badge-error'};
    if(/pass|success|complete|done|ok/.test(s)) return {label: 'Passed', cls: 'badge-success'};
    if(/not.*start|pending|waiting/.test(s)) return {label: 'Not Started', cls: 'badge-ghost'};
    
    return {label: 'In Progress', cls: 'badge-warning'};
  }

  /**
   * Generate PVT status HTML badges
   * @param {Array} pvtDetails - Array of PVT objects with status
   * @returns {string} - HTML string with badges
   */
  function getPvtStatusHTML(pvtDetails){
    if(!pvtDetails || pvtDetails.length === 0) return '';
    
    const passed = pvtDetails.filter(p => p.status === 'Passed').length;
    const failed = pvtDetails.filter(p => p.status === 'Fail').length;
    const inProgress = pvtDetails.filter(p => p.status === 'In Progress').length;
    const notStarted = pvtDetails.filter(p => p.status === 'Not Started' || !p.status).length;
    
    const badges = [];
    if(passed > 0) badges.push(`<span class='badge badge-xs badge-success' title='${passed} Passed'>${passed}✓</span>`);
    if(failed > 0) badges.push(`<span class='badge badge-xs badge-error' title='${failed} Failed'>${failed}✗</span>`);
    if(inProgress > 0) badges.push(`<span class='badge badge-xs badge-warning' title='${inProgress} In Progress'>${inProgress}⟳</span>`);
    if(notStarted > 0) badges.push(`<span class='badge badge-xs badge-ghost' title='${notStarted} Not Started'>${notStarted}○</span>`);
    
    return `<div class='flex flex-wrap gap-1 items-center mt-1'>${badges.join('')}</div>`;
  }

  /**
   * Generate POCV file status HTML badges
   * @param {Array} pvtDetails - Array of PVT objects with pocv_file_status
   * @returns {string} - HTML string with badges
   */
  function getPocvStatusHTML(pvtDetails){
    if(!pvtDetails || pvtDetails.length === 0) return '';
    
    const exist = pvtDetails.filter(p => p.pocv_file_status === 'Exist').length;
    const empty = pvtDetails.filter(p => p.pocv_file_status === 'Empty').length;
    const missing = pvtDetails.filter(p => p.pocv_file_status === 'Missing').length;
    
    const badges = [];
    if(exist > 0) badges.push(`<span class='badge badge-xs badge-success' title='${exist} Exist'>${exist}✓</span>`);
    if(empty > 0) badges.push(`<span class='badge badge-xs badge-warning' title='${empty} Empty'>${empty}○</span>`);
    if(missing > 0) badges.push(`<span class='badge badge-xs badge-error' title='${missing} Missing'>${missing}✗</span>`);
    
    return `<div class='flex flex-wrap gap-1 items-center'>${badges.join('')}</div>`;
  }

  // ------------------ Row Rendering ------------------
  /**
   * Render a single table row
   * @param {object} row - Row data
   * @param {number} index - Row index
   * @param {number} selectedIndex - Currently selected index
   * @returns {string} - HTML string
   */
  function renderRow(row, index, selectedIndex){
    const st = classifyStatus(row.status);
    
    // Determine Run PVT button color based on status
    let runPvtBtnCls = 'btn-success'; // default green
    if(st.label === 'Fail') runPvtBtnCls = 'btn-error';
    else if(st.label === 'In Progress') runPvtBtnCls = 'btn-warning';
    else if(st.label === 'Not Started') runPvtBtnCls = 'btn-ghost';
    
    const pvtStatusHTML = getPvtStatusHTML(row._pvtDetails);
    const pocvHTML = getPocvStatusHTML(row._pvtDetails);
    
    const isSelected = selectedIndex === index;
    const selectedClass = isSelected ? 'active' : '';
    
    // Task Redirect button color based on script existence (will be updated dynamically)
    // Default: btn-ghost, Blue: send exists, Yellow: sim exists, Green: get_back exists
    const taskRedirectCls = row._taskScriptStatus || 'btn-ghost';
    
    return `<tr data-idx='${index}' data-testbench='${escapeHTML(row.testbench)}' class='cell-row hover:bg-base-200/60 transition-colors ${selectedClass}'>
      <td class='text-right'>${index + 1}</td>
      <td><span class='font-mono'>${escapeHTML(row.testbench)}</span></td>
      <td>${pvtStatusHTML}</td>
      <td>${pocvHTML}</td>
      <td>
        <div class='flex gap-1'>
          <button class='btn btn-xs ${runPvtBtnCls} runpvt-btn' data-testbench='${escapeHTML(row.testbench)}'>Run PVT</button>
          <button class='btn btn-xs ${taskRedirectCls} task-redirect-btn' data-testbench='${escapeHTML(row.testbench)}' title='Distributed Task Redirect'>Task Redirect</button>
        </div>
      </td>
    </tr>`;
  }

  // ------------------ Table Rendering ------------------
  /**
   * Render the entire QC table
   */
  function renderTables(){
    const tbody = document.querySelector('#qcTable tbody');
    if(!tbody) return;
    
    const rows = getFilteredTestbenches();
    const selectedIndex = getSelectedIndex();
    
    if(rows.length === 0){
      tbody.innerHTML = `<tr><td colspan='5' class='text-center italic opacity-60'>No rows</td></tr>`;
    } else {
      tbody.innerHTML = rows.map((row, i) => renderRow(row, i, selectedIndex)).join('');
    }
    
    // Update tab counts
    updateTabCounts();
  }

  /**
   * Update tab badge counts
   */
  function updateTabCounts(){
    const allDelays = getDelays();
    const importantCount = allDelays.filter(r => isImportantTestbench(r.testbench)).length;
    const nonImportantCount = allDelays.length - importantCount;
    
    const impCountBadge = document.getElementById('importantCount');
    const nonImpCountBadge = document.getElementById('nonImportantCount');
    
    if(impCountBadge) impCountBadge.textContent = importantCount;
    if(nonImpCountBadge) nonImpCountBadge.textContent = nonImportantCount;
  }

  // ------------------ Row Interaction ------------------
  /**
   * Handle row click event
   * @param {Event} event - Click event
   */
  function handleRowClick(event){
    // Don't handle if clicking on buttons
    if(event.target.closest('.taskqueue-btn') || event.target.closest('.runpvt-btn') || event.target.closest('.task-redirect-btn')) return;
    
    const tr = event.target.closest('tr[data-idx]');
    if(!tr) return;
    
    const index = parseInt(tr.getAttribute('data-idx'));
    global.QCState.setSelectedIndex(index);
    renderTables();
  }

  // ------------------ Export to Global Scope ------------------
  global.QCTableRenderer = {
    // Rendering
    renderTables,
    renderRow,
    updateTabCounts,
    
    // Status
    classifyStatus,
    getPvtStatusHTML,
    getPocvStatusHTML,
    
    // Interaction
    handleRowClick
  };

  console.log('[Timing QC] table_renderer.js loaded');

})(window);
