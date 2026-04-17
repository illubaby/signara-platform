// Project Status Page JavaScript

// Track edited PIC values keyed by cell name
const editedPics = {};
// Track edited arbitrary fields per cell: {cellName: {fieldKey: value}}
const editedCells = {};
// Track cells marked for deletion while in edit mode
const deletedCells = new Set();
// Note: hiddenCells is now managed by hide_cell.js module (window.HideCell.hiddenCells)
// Edit mode toggle
let editMode = false;

// Expose to global scope for hide_cell.js module
window.editMode = editMode;
window.editedCells = editedCells;
// Cache the latest loaded result to re-render when toggling edit
let lastLoaded = null;

// Status icons
const SUCCESS_ICON_URL = 'https://www.svgrepo.com/show/13650/success.svg';
const SKIP_ICON_URL = 'https://www.svgrepo.com/show/511020/hide.svg';
const ERROR_ICON_URL = 'https://www.svgrepo.com/show/13658/error.svg';

function renderStatusIcon(kind, size = 16, title = '') {
    let url = ERROR_ICON_URL;
    if (kind === 'success') url = SUCCESS_ICON_URL;
    else if (kind === 'skip') url = SKIP_ICON_URL;
    const safeTitle = title ? ` title="${title}"` : '';
    return `<img src="${url}" alt="${kind}" width="${size}" height="${size}" class="inline-block"${safeTitle}>`;
}

// Column configurations for each table
// Note: netlist_snaphier and ckt_snaphier commented out to speed up page load
const SIS_COLUMNS = ['ckt_macros', 'tool', 'pic', /* 'netlist_snaphier', 'ckt_snaphier', */ 'pvt_summary', 'tmqa', 'final_status'];
// Jira-related columns temporarily disabled (easy re-enable later by uncommenting):
const NT_COLUMNS = ['ckt_macros', 'tool', 'pic', 'pvt_summary', 'tmqa', 'final_status', 'tmqc_spice_vs_nt', 'tmqc_spice_vs_spice', 'equalization'
    /*, 'assignee', 'duedate', 'status', 'jira_link' */
];

// Helpers for Due Date coloring
const MONTHS_ABBR = {
    jan: 0, feb: 1, mar: 2, apr: 3, may: 4, jun: 5,
    jul: 6, aug: 7, sep: 8, oct: 9, nov: 10, dec: 11
};

function parseJiraDate(str) {
    // Expected format: 13/Nov/25
    if (!str) return null;
    const m = str.trim().match(/^([0-3]?\d)\/([A-Za-z]{3})\/(\d{2})$/);
    if (!m) return null;
    const d = parseInt(m[1], 10);
    const mon = (m[2] || '').toLowerCase();
    const yy = parseInt(m[3], 10);
    const monthIdx = MONTHS_ABBR[mon];
    if (monthIdx == null) return null;
    const fullYear = 2000 + yy; // interpret 2-digit year as 20yy
    const dt = new Date(fullYear, monthIdx, d);
    return isNaN(dt.getTime()) ? null : dt;
}

function daysUntil(date) {
    if (!date) return null;
    const today = new Date();
    // Normalize to midnight local for day-based diff
    const start = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const target = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    const msPerDay = 24 * 60 * 60 * 1000;
    return Math.round((target - start) / msPerDay);
}

/**
 * Build HTML snippet for PVT status summary badges.
 * Copied from timing_saf/pvt_status.js
 */
function buildPvtStatusHTML(summary) {
    if (!summary || typeof summary !== 'object') {
        return '<span class="text-xs opacity-50">-</span>';
    }
    
    const badges = [];
    if (summary.passed && summary.passed > 0) {
        badges.push(`<span class="badge badge-xs badge-success" title="${summary.passed} Passed">${summary.passed}✓</span>`);
    }
    if (summary.failed && summary.failed > 0) {
        badges.push(`<span class="badge badge-xs badge-error" title="${summary.failed} Failed">${summary.failed}✗</span>`);
    }
    if (summary.in_progress && summary.in_progress > 0) {
        badges.push(`<span class="badge badge-xs badge-warning" title="${summary.in_progress} In Progress">${summary.in_progress}⟳</span>`);
    }
    if (summary.not_started && summary.not_started > 0) {
        badges.push(`<span class="badge badge-xs badge-ghost" title="${summary.not_started} Not Started">${summary.not_started}○</span>`);
    }
    
    if (!badges.length) {
        return '<span class="text-xs opacity-50">No PVTs</span>';
    }
    
    // Center badges horizontally and vertically within the cell for alignment with header
    return `<div class="flex flex-wrap gap-1 justify-center items-center">${badges.join('')}</div>`;
}

function getSelectedProjectInfo() {
    try {
        const project = localStorage.getItem('timing_selected_project') || 
                       sessionStorage.getItem('timing_selected_project') || '';
        const subproject = localStorage.getItem('timing_selected_subproject') || 
                          sessionStorage.getItem('timing_selected_subproject') || '';
        return { project, subproject };
    } catch (_) {
        return { project: '', subproject: '' };
    }
}

function updateGenReportButtonState(progressSis = 0, progressNt = 0) {
    const genReportButton = document.getElementById('genReportButton');
    const genReportButtonWrapper = document.getElementById('genReportButtonWrapper');
    if (!genReportButton) return;

    const canGenerate = progressSis === 100 && progressNt === 100;
    const tooltipText = canGenerate
        ? 'Generate project report'
        : 'Available only when SiS and NT progress are both 100%';

    genReportButton.disabled = !canGenerate;
    genReportButton.title = tooltipText;
    if (genReportButtonWrapper) {
        genReportButtonWrapper.title = tooltipText;
    }

    // Disabled buttons may not show native title tooltip reliably.
    // Route hover to wrapper when disabled.
    if (canGenerate) {
        genReportButton.classList.remove('pointer-events-none');
    } else {
        genReportButton.classList.add('pointer-events-none');
    }
}

/**
 * Build a table with specified columns
 */
function buildTable(tableHeadId, tableBodyId, data, allColumns, filterColumns) {
    const thead = document.getElementById(tableHeadId);
    const tbody = document.getElementById(tableBodyId);
    
    if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="100" class="text-center">No cells found</td></tr>';
        return;
    }
    
    // Determine which columns to display
    const columnsToShow = filterColumns 
        ? allColumns.filter(col => filterColumns.includes(col.key))
        : allColumns;
    
    // Build header
    const headerRow = document.createElement('tr');
    
    // Add actions column header if in edit mode (spans 2 columns for Hide and Delete)
    if (editMode) {
        const actionsTh = document.createElement('th');
        actionsTh.textContent = 'Actions';
        actionsTh.colSpan = 2;  // Span both Hide and Delete columns
        actionsTh.classList.add('text-base', 'font-semibold', 'text-center');
        headerRow.appendChild(actionsTh);
    }
    
    columnsToShow.forEach(col => {
        // Insert a visual separator column just before Internal Timing section
        if (col.key === 'assignee') {
            const sepTh = document.createElement('th');
            sepTh.className = 'p-0 w-0 border-l-2 border-base-300';
            headerRow.appendChild(sepTh);
        }
        const th = document.createElement('th');
        th.textContent = col.label;
        // Increase header font size and weight for readability, and center align all headers
        th.classList.add('text-base', 'font-semibold', 'text-center');
        headerRow.appendChild(th);
    });
    thead.innerHTML = '';
    thead.appendChild(headerRow);
    
    // Build rows
    tbody.innerHTML = '';
    data.forEach(item => {
        const row = document.createElement('tr');
        
        // Add hide and delete button cells if in edit mode
        if (editMode) {
            // Hide button
            const hideTd = document.createElement('td');
            hideTd.className = 'text-center';
            const hideBtn = document.createElement('button');
            // Check if cell is hidden (handle boolean, string True/true, or any truthy value)
            const hiddenValue = item['hidden'];
            const isHidden = hiddenValue === true || 
                           hiddenValue === 1 || 
                           (typeof hiddenValue === 'string' && hiddenValue.toLowerCase() === 'true');
            console.log(`[buildTable] Cell ${item['ckt_macros']}: hidden=${hiddenValue} (type: ${typeof hiddenValue}), isHidden=${isHidden}`);
            hideBtn.className = isHidden ? 'btn btn-xs btn-warning' : 'btn btn-xs btn-success';
            hideBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clip-rule="evenodd" /><path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z" /></svg>';
            hideBtn.title = isHidden ? 'Unhide cell' : 'Hide cell';
            hideBtn.dataset.cell = item['ckt_macros'];
            hideBtn.dataset.hidden = isHidden ? 'true' : 'false';  // Store current state
            hideBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log(`[Button Click] Hide button clicked for: ${item['ckt_macros']}`);
                // Use hide_cell.js module function
                if (window.HideCell) {
                    window.HideCell.handleHideCell(item['ckt_macros'], row, hideBtn);
                }
            });
            hideTd.appendChild(hideBtn);
            row.appendChild(hideTd);
            
            // If cell is already hidden, mark the row visually
            if (isHidden) {
                row.classList.add('opacity-30');
            }
            
            // Delete button
            const delTd = document.createElement('td');
            delTd.className = 'text-center';
            const delBtn = document.createElement('button');
            delBtn.className = 'btn btn-xs btn-error';
            delBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>';
            delBtn.title = 'Delete cell';
            delBtn.dataset.cell = item['ckt_macros'];
            // In edit mode, toggle mark-for-delete instead of calling server immediately
            delBtn.addEventListener('click', (e) => handleDeleteCell(item['ckt_macros'], row, delBtn));
            delTd.appendChild(delBtn);
            row.appendChild(delTd);
        }
        // Tag row with cell name for easier selection
        try { row.dataset.cell = item['ckt_macros']; } catch (_) {}
        
        columnsToShow.forEach(col => {
            // Insert a visual separator cell just before Internal Timing section
            if (col.key === 'assignee') {
                const sepTd = document.createElement('td');
                sepTd.className = 'p-0 w-0 border-l-2 border-base-300';
                row.appendChild(sepTd);
            }
            const td = document.createElement('td');
            td.className = 'text-center';  // Center align all cells
            // Tag the cell with its column key for later post-processing
            td.dataset.key = col.key;
            const key = col.key;
            
            // Special handling for PVT summary
            if (key === 'pvt_summary') {
                const summary = item[key];
                if (summary && typeof summary === 'object') {
                    // Ensure vertical alignment consistent with header
                    td.classList.add('align-middle');
                    td.innerHTML = buildPvtStatusHTML(summary);
                } else {
                    td.innerHTML = '<span class="text-xs opacity-50">-</span>';
                }
            } else if (key === 'pic') {
                // PIC: show text in view mode; input in edit mode
                if (editMode) {
                    const input = document.createElement('input');
                    input.type = 'text';
                    input.value = item[key] || '';
                    input.className = 'input input-sm input-bordered w-28';
                    input.dataset.cell = item['ckt_macros'];
                    input.dataset.key = key;
                    input.addEventListener('change', (e) => {
                        const cell = e.target.dataset.cell;
                        const val = e.target.value.trim();
                        editedPics[cell] = val; // keep legacy pic updates
                    });
                    td.appendChild(input);
                } else {
                    td.textContent = item[key] || '';
                }
            } else if (key === 'final_status') {
                // Display green checkmark for completed final status
                if (item[key] === '✓') {
                    td.innerHTML = renderStatusIcon('success', 18, 'Completed');
                    td.className = 'text-center';
                } else {
                    // final_status editable when in edit mode
                    if (editMode) {
                        const input = document.createElement('input');
                        input.type = 'text';
                        input.value = item[key] || '';
                        input.className = 'input input-xs input-bordered w-16 text-center';
                        input.dataset.cell = item['ckt_macros'];
                        input.dataset.key = key;
                        input.addEventListener('change', (e) => {
                            const cell = e.target.dataset.cell;
                            const k = e.target.dataset.key;
                            const val = e.target.value.trim();
                            if (!editedCells[cell]) editedCells[cell] = {};
                            editedCells[cell][k] = val;
                        });
                        td.className = 'text-center';
                        td.appendChild(input);
                    } else {
                        const v = (item[key] || '').toString().trim();
                        if (v.toLowerCase() === 'skip') {
                            td.innerHTML = renderStatusIcon('skip', 16, 'Skip');
                        } else if (v === '') {
                            td.innerHTML = renderStatusIcon('error', 16, 'Missing');
                        } else {
                            td.innerHTML = '<span class="text-xs opacity-50">-</span>';
                        }
                        td.className = 'text-center';
                    }
                }
            } else if (key === 'jira_link') {
                // Render JIRA links as compact clickable icons
                const raw = (item[key] || '').toString().trim();
                if (editMode) {
                    const input = document.createElement('input');
                    input.type = 'text';
                    input.value = raw;
                    input.className = 'input input-sm input-bordered w-64';
                    input.dataset.cell = item['ckt_macros'];
                    input.dataset.key = key;
                    input.addEventListener('change', (e) => {
                        const cell = e.target.dataset.cell;
                        const k = e.target.dataset.key;
                        const val = e.target.value.trim();
                        if (!editedCells[cell]) editedCells[cell] = {};
                        editedCells[cell][k] = val;
                    });
                    td.appendChild(input);
                } else {
                    if (!raw) {
                        td.innerHTML = '<span class="text-xs opacity-50">-</span>';
                    } else {
                        const links = raw.split(/\s+/).filter(Boolean);
                        const frag = document.createElement('div');
                        frag.className = 'flex flex-wrap gap-1 items-center justify-center';
                        links.forEach((url) => {
                            const a = document.createElement('a');
                            a.href = url;
                            a.target = '_blank';
                            a.rel = 'noopener noreferrer';
                            a.title = 'Open JIRA';
                            // Simple link icon
                            a.innerHTML = '<span class="inline-block" aria-label="JIRA">🔗</span>';
                            frag.appendChild(a);
                        });
                        td.appendChild(frag);
                    }
                }
            } else {
                // Generic columns: allow editing when editMode and value is primitive (not an object)
                const isObject = item[key] && typeof item[key] === 'object';
                if (editMode && !isObject && key !== 'ckt_macros') {
                    const input = document.createElement('input');
                    input.type = 'text';
                    input.value = item[key] || '';
                    input.className = 'input input-sm input-bordered w-36';
                    input.dataset.cell = item['ckt_macros'];
                    input.dataset.key = key;
                    input.addEventListener('change', (e) => {
                        const cell = e.target.dataset.cell;
                        const k = e.target.dataset.key;
                        const val = e.target.value.trim();
                        if (!editedCells[cell]) editedCells[cell] = {};
                        editedCells[cell][k] = val;
                    });
                    td.appendChild(input);
                } else {
                    // In view mode, render icons for "✓" and "skip" values
                    const raw = item[key] || '';
                    const v = raw.toString().trim();
                    // Special coloring and multi-value rendering for Status
                    if (key === 'status') {
                        const lower = v.toLowerCase();
                        // Show skip icon if value is exactly 'skip'
                        if (lower === 'skip') {
                            td.innerHTML = renderStatusIcon('skip', 16, 'Skip');
                            td.className = 'text-center';
                        } else {
                            const matches = [...v.matchAll(/in\s*progress|done|completed|new/ig)];
                            if (matches.length) {
                                const frag = document.createElement('div');
                                frag.className = 'flex flex-wrap gap-1 items-center justify-center';
                                matches.forEach(m => {
                                    const token = m[0].toLowerCase().replace(/\s+/g, ' ');
                                    const badge = document.createElement('span');
                                    badge.className = 'badge';
                                    if (token === 'done' || token === 'completed') badge.classList.add('badge-success');
                                    else if (token === 'in progress') badge.classList.add('badge-warning');
                                    else if (token === 'new') badge.classList.add('bg-white', 'text-base-content', 'border', 'border-base-300');
                                    badge.textContent = token.replace(/\b\w/g, c => c.toUpperCase());
                                    frag.appendChild(badge);
                                });
                                td.appendChild(frag);
                            } else {
                                const span = document.createElement('span');
                                span.className = 'badge';
                                if (lower === 'done' || lower === 'completed') {
                                    span.classList.add('badge-success');
                                } else if (lower === 'in progress') {
                                    span.classList.add('badge-warning');
                                } else if (lower === 'new') {
                                    span.classList.add('bg-white', 'text-base-content', 'border', 'border-base-300');
                                }
                                span.textContent = v || '-';
                                td.appendChild(span);
                            }
                            td.style.whiteSpace = 'pre-line';
                        }
                    } else if (key === 'duedate') {
                        // Special coloring and multi-value rendering for Due Date
                        const dateRegex = /([0-3]?\d\/[A-Za-z]{3}\/\d{2})/g;
                        const tokens = v.match(dateRegex) || v.split(/\n|,|\s+/).filter(Boolean);
                        let targetDate = null;
                        tokens.forEach(tok => {
                            const dt = parseJiraDate(tok);
                            if (dt && (!targetDate || dt < targetDate)) targetDate = dt;
                        });
                        if (targetDate) {
                            const dleft = daysUntil(targetDate);
                            if (dleft < 0) td.classList.add('text-error');
                            else if (dleft <= 2) td.classList.add('text-warning');
                        }
                        if (tokens && tokens.length) {
                            td.innerHTML = tokens.map(t => `<div>${t}</div>`).join('');
                        } else {
                            td.textContent = v || '';
                        }
                    } else if (v === '✓') {
                        td.innerHTML = renderStatusIcon('success', 16, 'Completed');
                        td.className = 'text-center';
                    } else if (v.toLowerCase() === 'skip') {
                        td.innerHTML = renderStatusIcon('skip', 16, 'Skip');
                        td.className = 'text-center';
                    } else if (v === '') {
                        td.innerHTML = renderStatusIcon('error', 16, 'Missing');
                        td.className = 'text-center';
                    } else {
                        td.textContent = isObject ? '' : (raw || '');
                        // Display newline-separated values as multi-line
                        if (['assignee','duedate','status'].includes(key)) {
                            td.style.whiteSpace = 'pre-line';
                        }
                    }
                }
            }
            
            row.appendChild(td);
        });
        // Note: Mismatch highlighting for netlist_snaphier and ckt_snaphier commented out (columns disabled)
        /* 
        // After all cells are created, highlight mismatches between netlist_snaphier and ckt_snaphier
        try {
            const netVal = (item['netlist_snaphier'] ?? '').toString().trim();
            const cktVal = (item['ckt_snaphier'] ?? '').toString().trim();
            if (netVal !== cktVal) {
                // Find the corresponding cells in this row
                const cells = Array.from(row.children);
                const netCell = cells.find(c => c.dataset && c.dataset.key === 'netlist_snaphier');
                const cktCell = cells.find(c => c.dataset && c.dataset.key === 'ckt_snaphier');
                [netCell, cktCell].forEach(cell => {
                    if (!cell) return;
                    cell.classList.add('text-error', 'font-semibold');
                    const input = cell.querySelector('input');
                    if (input) input.classList.add('input-error');
                    // Optional: tooltip for clarity
                    cell.title = 'Mismatch with counterpart column';
                });
            }
        } catch (_) { } // no-op
        */
        tbody.appendChild(row);
    });
}

async function loadProjectStatus(refresh = false) {
    const sisTableBody = document.getElementById('sisTableBody');
    const ntTableBody = document.getElementById('ntTableBody');
    const refreshButton = document.getElementById('refreshButton');
    const spinner = refreshButton.querySelector('.loading-spinner');

    // Disable button and show spinner
    if (refreshButton) refreshButton.disabled = true;
    if (spinner) spinner.classList.remove('hidden');
    updateGenReportButtonState(0, 0);
    
    try {
        const { project, subproject } = getSelectedProjectInfo();
        
        if (!project || !subproject) {
            sisTableBody.innerHTML = '<tr><td colspan="100" class="text-center text-warning">Please select a project first from the home page</td></tr>';
            ntTableBody.innerHTML = '<tr><td colspan="100" class="text-center text-warning">Please select a project first from the home page</td></tr>';
            return;
        }
        
        console.log(`[loadProjectStatus] Fetching data for: ${project}, ${subproject}. Refresh: ${refresh}`);
        
        // Get custom final lib path if provided
        const finalLibPathInput = document.getElementById('finalLibPathInput');
        const finalLibPath = finalLibPathInput?.value?.trim() || '';
        
        let url = `/api/project-status?project=${encodeURIComponent(project)}&subproject=${encodeURIComponent(subproject)}&refresh=${refresh}`;
        if (finalLibPath) {
            url += `&final_lib_path=${encodeURIComponent(finalLibPath)}`;
        }
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log('[loadProjectStatus] Data received:', result);
        console.log('[loadProjectStatus] Total cells from backend:', result.data?.length || 0);
        if (result.data) {
            const hiddenCount = result.data.filter(item => {
                const val = item.hidden;
                return val === true || val === 1 || (typeof val === 'string' && val.toLowerCase() === 'true');
            }).length;
            console.log('[loadProjectStatus] Cells with hidden=true:', hiddenCount);
            if (hiddenCount > 0) {
                const hiddenCellNames = result.data.filter(item => {
                    const val = item.hidden;
                    return val === true || val === 1 || (typeof val === 'string' && val.toLowerCase() === 'true');
                }).map(item => item.ckt_macros);
                console.log('[loadProjectStatus] Hidden cell names:', hiddenCellNames);
            }
        }
        lastLoaded = result;
        
        // Update project-level report statuses
        if (result.project_status) {
            const specialCheckStatus = document.getElementById('specialCheckStatus');
            const packageCompareStatus = document.getElementById('packageCompareStatus');
            
            if (specialCheckStatus) {
                if (result.project_status.special_check === '✓') {
                    specialCheckStatus.textContent = '✓';
                    specialCheckStatus.className = 'badge badge-sm badge-success';
                } else {
                    specialCheckStatus.textContent = '-';
                    specialCheckStatus.className = 'badge badge-sm badge-ghost';
                }
            }
            
            if (packageCompareStatus) {
                if (result.project_status.package_compare === '✓') {
                    packageCompareStatus.textContent = '✓';
                    packageCompareStatus.className = 'badge badge-sm badge-success';
                } else {
                    packageCompareStatus.textContent = '-';
                    packageCompareStatus.className = 'badge badge-sm badge-ghost';
                }
            }
        }
        
        if (result.data && result.data.length > 0) {
            // Helper function to check if cell is hidden (from hide_cell.js module)
            const isHidden = window.HideCell ? window.HideCell.isHiddenCell : (item) => {
                const val = item.hidden;
                return val === true || val === 1 || (typeof val === 'string' && val.toLowerCase() === 'true');
            };
            
            // Split data by tool type
            const sisAll = result.data.filter(item => item.tool && item.tool.toLowerCase() === 'sis');
            const ntAll = result.data.filter(item => item.tool && item.tool.toLowerCase() === 'nt');
            
            // Only filter out hidden cells when NOT in edit mode
            // In edit mode, show all cells including hidden ones (so they can be unhidden)
            let sisCells, ntCells;
            if (editMode) {
                sisCells = sisAll;
                ntCells = ntAll;
                console.log('[loadProjectStatus] Edit mode: Showing all cells including hidden');
                // Log which cells have hidden=true
                const hiddenInData = result.data.filter(item => item.hidden);
                console.log('[loadProjectStatus] Cells with hidden=true in data:', hiddenInData.length);
                if (hiddenInData.length > 0) {
                    console.log('[loadProjectStatus] Hidden cells details:', hiddenInData.map(c => ({name: c.ckt_macros, hidden: c.hidden, type: typeof c.hidden})));
                }
            } else {
                sisCells = sisAll.filter(item => !isHidden(item));
                ntCells = ntAll.filter(item => !isHidden(item));
                const sisHidden = sisAll.filter(item => isHidden(item));
                const ntHidden = ntAll.filter(item => isHidden(item));
                console.log(`[loadProjectStatus] View mode: Filtered out ${sisHidden.length} SiS + ${ntHidden.length} NT hidden cells`);
                if (sisHidden.length > 0) console.log('[loadProjectStatus] SiS hidden:', sisHidden.map(c => c.ckt_macros));
                if (ntHidden.length > 0) console.log('[loadProjectStatus] NT hidden:', ntHidden.map(c => c.ckt_macros));
            }
            
            console.log(`[loadProjectStatus] Before filtering - SiS: ${sisAll.length}, NT: ${ntAll.length}`);
            console.log(`[loadProjectStatus] After filtering - SiS: ${sisCells.length}, NT: ${ntCells.length}`);
            
            // Calculate progress using item counts instead of counting completed cells
            // Note: Use sisCells and ntCells (filtered, excluding hidden) for accurate progress
            // SiS: items are ['tmqa','final_status'] per SiS cell (only count visible cells)
            const sisItemFields = ['tmqa', 'final_status'];
            const sisTotalItems = sisCells.length * sisItemFields.length;
            let sisCompletedItems = sisCells.reduce((acc, item) => {
                if ((item.tmqa || '').toString().trim() === '✓') acc++;
                if ((item.final_status || '').toString().trim() === '✓') acc++;
                return acc;
            }, 0);

            // NT: items are ['tmqa','final_status','tmqc_spice_vs_nt','tmqc_spice_vs_spice','equalization'] per NT cell
            const ntItemFields = ['tmqa', 'final_status', 'tmqc_spice_vs_nt', 'tmqc_spice_vs_spice', 'equalization'];
            const ntTotalItems = ntCells.length * ntItemFields.length;
            const checkField = (val) => {
                const v = (val || '').toString().trim();
                return v === '✓' || v.toLowerCase() === 'skip';
            };
            let ntCompletedItems = ntCells.reduce((acc, item) => {
                ntItemFields.forEach(f => { if (checkField(item[f])) acc++; });
                return acc;
            }, 0);

            // Jira/Internal Timing progress temporarily disabled.
            // To re-enable, uncomment the block below and the Internal radial in the template.
            /*
            // Internal Timing: count individual JIRA status tokens per NT cell
            let internalTotalItems = 0;
            let internalCompletedItems = 0;
            ntCells.forEach(item => {
                // If jira_link is explicitly 'skip' for this cell, do not count it at all
                const jl = (item.jira_link || '').toString().trim().toLowerCase();
                if (jl === 'skip') return;

                const statusVal = (item.status || '').toString().trim();
                if (!statusVal) return;
                const statuses = statusVal.split(/\n|,/).map(s => s.trim()).filter(Boolean);
                internalTotalItems += statuses.length;
                statuses.forEach(status => {
                    const lower = status.toLowerCase();
                    if (lower === 'done' || lower === 'completed' || lower === 'skip') internalCompletedItems++;
                });
            });
            */

            // Debug: show item-level counts
            console.log('[Progress Debug] SiS total items:', sisTotalItems, 'completed items:', sisCompletedItems);
            console.log('[Progress Debug] NT total items:', ntTotalItems, 'completed items:', ntCompletedItems);
            // console.log('[Progress Debug] Internal total items:', internalTotalItems, 'completed items:', internalCompletedItems);

            // Update separate progress radials using item totals
            const progressSis = sisTotalItems > 0 ? Math.round((sisCompletedItems / sisTotalItems) * 100) : 0;
            const progressNt = ntTotalItems > 0 ? Math.round((ntCompletedItems / ntTotalItems) * 100) : 0;
            updateGenReportButtonState(progressSis, progressNt);
            // const progressInternal = internalTotalItems > 0 ? Math.round((internalCompletedItems / internalTotalItems) * 100) : 0;

            const progressElementSis = document.getElementById('projectProgressSis');
            const progressElementNt = document.getElementById('projectProgressNt');
            const progressStatsSis = document.getElementById('progressStatsSis');
            const progressStatsNt = document.getElementById('progressStatsNt');
            // const progressElementInternal = document.getElementById('projectProgressInternal');
            // const progressStatsInternal = document.getElementById('progressStatsInternal');
            if (progressElementSis) {
                progressElementSis.style.setProperty('--value', progressSis);
                progressElementSis.setAttribute('aria-valuenow', progressSis);
                progressElementSis.textContent = `${progressSis}%`;
            }
            if (progressElementNt) {
                progressElementNt.style.setProperty('--value', progressNt);
                progressElementNt.setAttribute('aria-valuenow', progressNt);
                progressElementNt.textContent = `${progressNt}%`;
            }
            // if (progressElementInternal) {
            //     progressElementInternal.style.setProperty('--value', progressInternal);
            //     progressElementInternal.setAttribute('aria-valuenow', progressInternal);
            //     progressElementInternal.textContent = `${progressInternal}%`;
            // }
            if (progressStatsSis) {
                progressStatsSis.textContent = `${sisCompletedItems}/${sisTotalItems} complete`;
            }
            if (progressStatsNt) {
                progressStatsNt.textContent = `${ntCompletedItems}/${ntTotalItems} complete`;
            }
            // if (progressStatsInternal) {
            //     progressStatsInternal.textContent = `${internalCompletedItems}/${internalTotalItems} complete`;
            // }
            
            // Update tab counts
            document.getElementById('sisCount').textContent = sisCells.length;
            document.getElementById('ntCount').textContent = ntCells.length;
            
            // Build SiS table with limited columns
            buildTable('sisTableHead', 'sisTableBody', sisCells, result.columns, SIS_COLUMNS);
            
            // Build NT table with all columns
            buildTable('ntTableHead', 'ntTableBody', ntCells, result.columns, NT_COLUMNS);
        } else {
            sisTableBody.innerHTML = '<tr><td colspan="100" class="text-center">No cells found for this project</td></tr>';
            ntTableBody.innerHTML = '<tr><td colspan="100" class="text-center">No cells found for this project</td></tr>';
            updateGenReportButtonState(0, 0);
        }
    } catch (error) {
        console.error('[loadProjectStatus] Error:', error);
        sisTableBody.innerHTML = 
            `<tr><td colspan="100" class="text-center text-error">Error loading data: ${error.message}</td></tr>`;
        ntTableBody.innerHTML = 
            `<tr><td colspan="100" class="text-center text-error">Error loading data: ${error.message}</td></tr>`;
        updateGenReportButtonState(0, 0);
    } finally {
        // Re-enable button and hide spinner
        if (refreshButton) refreshButton.disabled = false;
        if (spinner) spinner.classList.add('hidden');
    }
}

function setupEventListeners() {
    // Tab switching
    const sisTab = document.getElementById('sisTab');
    const ntTab = document.getElementById('ntTab');
    const sisContainer = document.getElementById('sisTableContainer');
    const ntContainer = document.getElementById('ntTableContainer');
    
    if (sisTab && ntTab) {
        sisTab.addEventListener('click', () => {
            sisTab.classList.add('tab-active');
            ntTab.classList.remove('tab-active');
            sisContainer.classList.remove('hidden');
            ntContainer.classList.add('hidden');
        });
        
        ntTab.addEventListener('click', () => {
            ntTab.classList.add('tab-active');
            sisTab.classList.remove('tab-active');
            ntContainer.classList.remove('hidden');
            sisContainer.classList.add('hidden');
        });
    }
    
    const refreshButton = document.getElementById('refreshButton');
    if (refreshButton) {
        refreshButton.addEventListener('click', async () => {
            // Show loading immediately
            const spinner = refreshButton.querySelector('.loading-spinner');
            refreshButton.disabled = true;
            if (spinner) spinner.classList.remove('hidden');
            
            // Jira refresh temporarily disabled.
            // To re-enable, uncomment the block below.
            /*
            // First, trigger JIRA refresh to populate assignee/duedate/status
            const { project, subproject } = getSelectedProjectInfo();
            if (project && subproject) {
                try {
                    console.log('[ProjectStatus] Refreshing JIRA statuses...');
                    console.log('[ProjectStatus] Selected:', { project, subproject });
                    const resp = await fetch('/api/project-status/refresh-jira', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ project, subproject })
                    });
                    console.log('[ProjectStatus] Response status:', resp.status, resp.statusText);
                    let data = null;
                    try {
                        data = await resp.json();
                        console.log('[ProjectStatus] Response JSON:', data);
                    } catch (e) {
                        console.warn('[ProjectStatus] Failed to parse JSON response', e);
                    }
                    if (!resp.ok) {
                        console.warn('[ProjectStatus] JIRA refresh failed');
                    } else if (data && typeof data.fields_updated !== 'undefined') {
                        console.log('[ProjectStatus] JIRA fields updated:', data.fields_updated);
                        if (data.fields_updated === 0) {
                            // Provide immediate context: how many cells have jira_link in current data
                            if (lastLoaded && Array.isArray(lastLoaded.data)) {
                                const withJiraArr = lastLoaded.data.filter(c => (c.jira_link||'').trim() !== '');
                                console.log('[ProjectStatus] Cells with jira_link (current view):', withJiraArr.length);
                                console.table(withJiraArr.map(c => ({ cell: c.ckt_macros, jira_link: c.jira_link })));
                            }
                            console.log('[ProjectStatus] If zero with links present, check backend logs for command/parse issues.');
                        }
                    }
                } catch (e) {
                    console.error('[ProjectStatus] Error during JIRA refresh:', e);
                }
            }
            */
            // Then reload project status (force refresh)
            loadProjectStatus(true);
        });
    }

    // Edit/Done button - combined edit mode toggle and save functionality
    const editToggleButton = document.getElementById('editToggleButton');
    const finalLibPathInput = document.getElementById('finalLibPathInput');
    const cutoffDateInput = document.getElementById('cutoffDateInput');
    const addCellButton = document.getElementById('addCellButton');
    const getPicButton = document.getElementById('getPicButton');
    
    if (editToggleButton) {
        editToggleButton.addEventListener('click', async () => {
            if (!editMode) {
                // Entering edit mode - switch to edit and fetch fresh data so inputs render from latest server state
                editMode = true;
                window.editMode = true;  // Expose to hide_cell.js module
                // Update button appearance
                const svgIcon = editToggleButton.querySelector('svg');
                editToggleButton.innerHTML = '<span class="loading loading-spinner hidden"></span>Done';
                editToggleButton.classList.remove('btn-outline');
                editToggleButton.classList.add('btn-primary');

                // Show Add Cell button
                if (addCellButton) addCellButton.classList.remove('hidden');
                // Show Get PIC button
                if (getPicButton) getPicButton.classList.remove('hidden');

                // Enable configuration inputs
                if (finalLibPathInput) finalLibPathInput.disabled = false;
                if (cutoffDateInput) cutoffDateInput.disabled = false;

                // Clear any previous deletion marks and force a fresh load from backend
                deletedCells.clear();
                if (window.HideCell) window.HideCell.clearHiddenCells();
                try {
                    await loadProjectStatus(true);
                } catch (e) {
                    console.error('[Edit Mode] Failed to refresh data on entering edit mode:', e);
                }
            } else {
                // Exiting edit mode - save changes
                const spinner = editToggleButton.querySelector('.loading-spinner');
                
                try {
                    const { project, subproject } = getSelectedProjectInfo();
                    
                    if (!project || !subproject) {
                        console.warn('[Edit/Done] No project/subproject selected');
                        return;
                    }
                    
                    // Collect PIC updates
                    const updates = Object.entries(editedPics).map(([cell, pic]) => ({ 
                        cell, 
                        pic 
                    }));

                    // Collect arbitrary field updates
                    const cellUpdates = Object.entries(editedCells)
                        .map(([cell, values]) => {
                            // Never send PIC in cell_updates; PIC is handled by `updates`
                            const cleaned = { ...(values || {}) };
                            delete cleaned.pic;
                            return { cell, values: cleaned };
                        })
                        .filter(item => item && item.cell && item.values && Object.keys(item.values).length > 0);
                    
                    // Collect configuration updates
                    const finalLibPath = finalLibPathInput?.value?.trim() || '';
                    const cutoffDate = cutoffDateInput?.value?.trim() || '';
                    
                    // Check if config actually changed by comparing with loaded config
                    const configChanged = await checkConfigChanged(project, subproject, finalLibPath, cutoffDate);
                    
                    const config = {};
                    if (configChanged) {
                        if (finalLibPath) {
                            config.final_lib_path = finalLibPath;
                        }
                        config.cutoff_date = cutoffDate || null;
                    }
                    
                    const hiddenSize = window.HideCell ? window.HideCell.hiddenCells.size : 0;
                    
                    if (!updates.length && !cellUpdates.length && !Object.keys(config).length && deletedCells.size === 0 && hiddenSize === 0) {
                        console.log('[Edit/Done] No changes detected, skipping API call');
                        // Exit edit mode without API call
                        editMode = false;
                        window.editMode = false;  // Update global for hide_cell.js module
                        editToggleButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" /></svg>Edit';
                        editToggleButton.classList.remove('btn-primary');
                        editToggleButton.classList.add('btn-outline');
                        
                        // Hide Add Cell button
                        if (addCellButton) addCellButton.classList.add('hidden');
                        // Hide Get PIC button
                        if (getPicButton) getPicButton.classList.add('hidden');
                        
                        if (finalLibPathInput) finalLibPathInput.disabled = true;
                        if (cutoffDateInput) cutoffDateInput.disabled = true;
                        if (lastLoaded && lastLoaded.data) {
                            const sisCells = lastLoaded.data.filter(item => item.tool && item.tool.toLowerCase() === 'sis');
                            const ntCells = lastLoaded.data.filter(item => item.tool && item.tool.toLowerCase() === 'nt');
                            buildTable('sisTableHead', 'sisTableBody', sisCells, lastLoaded.columns, SIS_COLUMNS);
                            buildTable('ntTableHead', 'ntTableBody', ntCells, lastLoaded.columns, NT_COLUMNS);
                        }
                        return;
                    }
                    
                    console.log(`[Edit/Done] Submitting ${updates.length} PIC update(s), ${cellUpdates.length} field update(s), ${deletedCells.size} deletions, ${hiddenSize} hidden, and config...`);
                    
                    // Disable button and show spinner
                    editToggleButton.disabled = true;
                    if (spinner) spinner.classList.remove('hidden');
                    
                    // Send update request
                    const deletions = Array.from(deletedCells);
                    const hidden = window.HideCell ? window.HideCell.getHiddenCellsArray() : [];
                    console.log('[Edit/Done] Sending to backend - Hidden cells:', hidden);
                    const response = await fetch('/api/project-status/update-pic', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ project, subproject, updates, cell_updates: cellUpdates, config, deletions, hidden })
                    });
                    
                    if (!response.ok) {
                        throw new Error(`Update failed: ${response.status} ${response.statusText}`);
                    }
                    
                    const result = await response.json();
                    console.log(`[Edit/Done] Successfully updated ${result.updated} cell(s)`);
                    console.log('[Edit/Done] Backend response - hidden_processed:', result.hidden_processed, '| hidden_failed:', result.hidden_failed);
                    
                    // Clear local change tracking
                    Object.keys(editedPics).forEach(key => delete editedPics[key]);
                    Object.keys(editedCells).forEach(key => delete editedCells[key]);
                    deletedCells.clear();
                    if (window.HideCell) window.HideCell.clearHiddenCells();
                    
                    // Exit edit mode
                    editMode = false;
                    window.editMode = false;  // Update global for hide_cell.js module
                    editToggleButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" /></svg>Edit';
                    editToggleButton.classList.remove('btn-primary');
                    editToggleButton.classList.add('btn-outline');
                    
                    // Hide Add Cell button
                    if (addCellButton) addCellButton.classList.add('hidden');
                    // Hide Get PIC button
                    if (getPicButton) getPicButton.classList.add('hidden');
                    
                    // Disable configuration inputs
                    if (finalLibPathInput) finalLibPathInput.disabled = true;
                    if (cutoffDateInput) cutoffDateInput.disabled = true;
                    
                    // Reload table data and force fresh fetch from backend to reflect updates
                    await loadProjectStatus(true);
                    
                } catch (error) {
                    console.error('[Edit/Done] Error:', error);
                    alert(`Update failed: ${error.message}`);
                } finally {
                    // Re-enable button and hide spinner
                    editToggleButton.disabled = false;
                    if (spinner) spinner.classList.add('hidden');
                }
            }
        });
    }
}

// Load project configuration (paths)
async function loadProjectConfig() {
    const { project, subproject } = getSelectedProjectInfo();
    console.log('[loadProjectConfig] Loading config for:', project, '/', subproject);
    
    if (!project || !subproject) {
        console.log('[loadProjectConfig] No project/subproject selected');
        return;
    }
    
    try {
        const response = await fetch(`/api/project-status/config?project=${encodeURIComponent(project)}&subproject=${encodeURIComponent(subproject)}`);
        if (response.ok) {
            const result = await response.json();
            const config = result.config || {};
            
            // Store config globally for Gen Report button
            window.projectConfig = config;
            console.log('[loadProjectConfig] Config stored globally:', config);
            
            // Load final_lib_path if exists
            if (config.final_lib_path) {
                const finalLibPathInput = document.getElementById('finalLibPathInput');
                if (finalLibPathInput) {
                    finalLibPathInput.value = config.final_lib_path;
                    console.log('[loadProjectConfig] Loaded final_lib_path:', config.final_lib_path);
                }
            }
            
            // Load cutoff_date if exists
            if (config.cutoff_date) {
                const cutoffDateInput = document.getElementById('cutoffDateInput');
                if (cutoffDateInput) {
                    cutoffDateInput.value = config.cutoff_date;
                    console.log('[loadProjectConfig] Loaded cutoff_date:', config.cutoff_date);
                }
            }
        }
    } catch (error) {
        console.error('[loadProjectConfig] Error loading config:', error);
    }
}

// Check if config actually changed
async function checkConfigChanged(project, subproject, finalLibPath, cutoffDate) {
    try {
        const response = await fetch(`/api/project-status/config?project=${encodeURIComponent(project)}&subproject=${encodeURIComponent(subproject)}`);
        if (response.ok) {
            const result = await response.json();
            const config = result.config || {};
            
            const originalFinalLibPath = config.final_lib_path || '';
            const originalCutoffDate = config.cutoff_date || '';
            
            return originalFinalLibPath !== finalLibPath || originalCutoffDate !== cutoffDate;
        }
    } catch (error) {
        console.error('[checkConfigChanged] Error:', error);
    }
    return false;
}

// Load data when page loads
document.addEventListener('DOMContentLoaded', async () => {
    console.log('[Project Status] Page loaded, initializing...');
    
    // Ensure config (including final_lib_path) is loaded before first status fetch
    await loadProjectConfig();
    setupEventListeners();
    loadProjectStatus();
    
    // Gen Report button is handled by gen_report.js module
    
    // Setup Add Cell button
    const addCellButton = document.getElementById('addCellButton');
    const addCellModal = document.getElementById('addCellModal');
    if (addCellButton && addCellModal) {
        addCellButton.addEventListener('click', () => {
            addCellModal.showModal();
        });
    }

    // Setup Get PIC button
    const getPicButton = document.getElementById('getPicButton');
    if (getPicButton) {
        getPicButton.addEventListener('click', async () => {
            if (!editMode) return;

            const { project, subproject } = getSelectedProjectInfo();
            if (!project || !subproject) {
                alert('Please select a project first');
                return;
            }

            // Disable button while processing
            getPicButton.disabled = true;
            const originalText = getPicButton.textContent;
            getPicButton.textContent = 'Getting...';

            try {
                const response = await fetch('/api/project-status/get-pic', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ project, subproject })
                });
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Failed to get PIC');
                }

                const result = await response.json();
                console.log('[Get PIC] Result:', result);

                // Fill only empty PIC inputs locally; persist only when user clicks Done
                const updates = Array.isArray(result.updates) ? result.updates : [];
                let applied = 0;
                updates.forEach(({ cell, pic }) => {
                    if (!cell || !pic) return;
                    const inputs = Array.from(document.querySelectorAll('input[data-key="pic"]'))
                        .filter((el) => el && el.dataset && el.dataset.cell === cell);
                    inputs.forEach((input) => {
                        input.value = pic;
                        editedPics[cell] = pic;
                        applied += 1;
                    });
                });

                console.log(`[Get PIC] Applied to ${applied} input(s)`);
            } catch (error) {
                console.error('[Get PIC] Error:', error);
                alert(`Failed to get PIC: ${error.message}`);
            } finally {
                getPicButton.disabled = false;
                getPicButton.textContent = originalText;
            }
        });
    }
    
    // Setup Add Cell confirmation
    const confirmAddCell = document.getElementById('confirmAddCell');
    if (confirmAddCell && addCellModal) {
        confirmAddCell.addEventListener('click', async () => {
            const cellName = document.getElementById('newCellName').value.trim();
            const tool = document.getElementById('newCellTool').value;
            const pic = document.getElementById('newCellPic').value.trim();
            
            if (!cellName) {
                alert('Cell name is required');
                return;
            }
            
            // Disable button while processing
            confirmAddCell.disabled = true;
            
            try {
                const { project, subproject } = getSelectedProjectInfo();
                if (!project || !subproject) {
                    alert('Please select a project first');
                    return;
                }
                
                const cell_data = {
                    ckt_macros: cellName,
                    tool: tool
                };
                if (pic) {
                    cell_data.pic = pic;
                }
                
                const response = await fetch('/api/project-status/add-cell', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ project, subproject, cell_data })
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Failed to add cell');
                }
                
                const result = await response.json();
                console.log('[Add Cell] Success:', result);
                
                // Close modal and reset form
                addCellModal.close();
                document.getElementById('newCellName').value = '';
                document.getElementById('newCellTool').value = 'sis';
                document.getElementById('newCellPic').value = '';
                
                // Reload table
                await loadProjectStatus(false);
                
            } catch (error) {
                console.error('[Add Cell] Error:', error);
                alert(`Failed to add cell: ${error.message}`);
            } finally {
                confirmAddCell.disabled = false;
            }
        });
    }
});

// Handle delete cell
async function handleDeleteCell(cellName, rowEl = null, buttonEl = null) {
    // If we're in edit mode, toggle mark-for-delete locally and visually
    if (editMode) {
        if (deletedCells.has(cellName)) {
            deletedCells.delete(cellName);
            // restore visual state
            if (rowEl) {
                rowEl.classList.remove('opacity-50', 'line-through');
            } else {
                const r = document.querySelector(`tr[data-cell="${cellName}"]`);
                if (r) r.classList.remove('opacity-50', 'line-through');
            }
            if (buttonEl) {
                buttonEl.classList.remove('btn-success');
                buttonEl.classList.add('btn-error');
            } else {
                const btns = document.querySelectorAll(`button[data-cell="${cellName}"]`);
                btns.forEach(b => { b.classList.remove('btn-success'); b.classList.add('btn-error'); });
            }
        } else {
            deletedCells.add(cellName);
            // visually mark row as deleted
            if (rowEl) {
                rowEl.classList.add('opacity-50', 'line-through');
            } else {
                const r = document.querySelector(`tr[data-cell="${cellName}"]`);
                if (r) r.classList.add('opacity-50', 'line-through');
            }
            if (buttonEl) {
                buttonEl.classList.remove('btn-error');
                buttonEl.classList.add('btn-success');
            } else {
                const btns = document.querySelectorAll(`button[data-cell="${cellName}"]`);
                btns.forEach(b => { b.classList.remove('btn-error'); b.classList.add('btn-success'); });
            }
        }
        return;
    }

    // Not in edit mode: perform immediate delete (existing behavior)
    if (!confirm(`Are you sure you want to delete cell "${cellName}"?`)) {
        return;
    }

    // Find the delete button(s) and add loading state
    const deleteButtons = document.querySelectorAll(`button[data-cell="${cellName}"]`);
    deleteButtons.forEach(btn => {
        btn.disabled = true;
        btn.innerHTML = '<span class="loading loading-spinner loading-xs"></span>';
    });

    try {
        const { project, subproject } = getSelectedProjectInfo();
        if (!project || !subproject) {
            alert('Please select a project first');
            return;
        }

        const response = await fetch('/api/project-status/delete-cell', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ project, subproject, cell: cellName })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete cell');
        }

        const result = await response.json();
        console.log('[Delete Cell] Success:', result);

        // Reload table
        await loadProjectStatus(false);

    } catch (error) {
        console.error('[Delete Cell] Error:', error);
        alert(`Failed to delete cell: ${error.message}`);

        // Restore button state on error
        deleteButtons.forEach(btn => {
            btn.disabled = false;
            btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>';
        });
    }
}
