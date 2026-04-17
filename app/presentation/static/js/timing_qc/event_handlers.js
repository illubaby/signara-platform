// Timing QC: Event Handlers
// This module wires all DOM event listeners

(function(global){
  'use strict';

  // Verify dependencies
  if(!global.QCState || !global.QCApiClient || !global.QCTableRenderer || 
     !global.QCScriptRunner || !global.QCTaskQueue || !global.QCPvtRunner){
    console.error('[Timing QC] event_handlers.js requires all other modules');
    return;
  }

  const { getSelectionState, setDelays, setSelectedIndex, getCurrentTab, setCurrentTab,
          saveLastTab, saveLastSelection, getLastSelection, clearStatusPoll, setLoadedCell,
          getFilteredTestbenches } = global.QCState;
  const { loadCells, loadDefaults, loadTestbenches, refreshAllStatuses, startStatusPolling } = global.QCApiClient;
  const { renderTables, handleRowClick } = global.QCTableRenderer;
  const { runScript, stopScript, clearOutput, initElements: initScriptRunnerElements } = global.QCScriptRunner;
  const { openModal: openTaskQueueModal } = global.QCTaskQueue;
  const { openModal: openPvtModal } = global.QCPvtRunner;

  // ------------------ Form Handlers ------------------
  /**
   * Build payload from form inputs
   * @returns {object} - Payload object
   */
  function buildPayload(){
    // Get datastore values if handler is available
    const datastoreValues = global.QCDatastoreHandler ? global.QCDatastoreHandler.getValues() : [];
    
    return {
      cell: document.getElementById('cellSelect')?.value,
      qcplan: document.getElementById('qcplanInput')?.value.trim() || undefined,
      netlist: document.getElementById('netlistInput')?.value.trim() || undefined,
      data: document.getElementById('dataInput')?.value.trim() || undefined,
      datastore: datastoreValues.length > 0 ? datastoreValues : undefined,
      common_source: document.getElementById('commonSourceInput')?.value.trim() || undefined,
      ref_data: (document.getElementById('refDataCheckbox')?.checked && document.getElementById('refDataInput')?.value.trim()) || undefined,
      update: document.getElementById('updateOpt')?.checked,
      adjustment: document.getElementById('adjustmentOpt')?.checked,
  no_wf: document.getElementById('noWFOpt')?.checked,
      xtalk_rel_net: document.getElementById('xtalkRelNetOpt')?.checked,
      hierarchy: document.getElementById('hierarchyInput')?.value.trim() || undefined,
      verbose: document.getElementById('verboseInput')?.value.trim() || undefined,
      include: document.getElementById('includeInput')?.value.trim() || undefined,
      xtalk: document.getElementById('xtalkInput')?.value.trim() || undefined,
      primesim: document.getElementById('primesimInput')?.value.trim() || undefined,
      hspice: document.getElementById('hspiceInput')?.value.trim() || undefined,
      index: document.getElementById('indexInput')?.value.trim() || undefined,
      phase: document.getElementById('phaseInput')?.value.trim() || undefined,
      debug_path: document.getElementById('debugInput')?.value.trim() || undefined
    };
  }

  // ------------------ Cell Selection ------------------
  /**
   * Wire cell selection change event
   */
  function wireCellSelection(){
    const cellSelect = document.getElementById('cellSelect');
    const statusNote = document.getElementById('statusNote');
    const openReportBtn = document.getElementById('openReportBtn');
    
    if(cellSelect){
      cellSelect.addEventListener('change', async () => {
        const cell = cellSelect.value;
        const hasCell = !!cell;
        
        if(statusNote) statusNote.textContent = hasCell ? 'Scanning testbenches...' : 'Select a cell';
        
        // Update report button state based on whether report exists for this cell
        if(openReportBtn){
          if(hasCell && global._qcCellsData){
            const cellData = global._qcCellsData.find(c => c.cell === cell);
            openReportBtn.disabled = !(cellData && cellData.tmqc_report_exists === true);
          } else {
            openReportBtn.disabled = true;
          }
        }
        
        setDelays([]);
        setSelectedIndex(null);
        renderTables();
        clearStatusPoll();
        
        if(hasCell){
          // Load defaults and testbenches
          await loadDefaults(cell).then(defaults => {
            if(defaults){
              // Populate form fields
              document.getElementById('qcplanInput').value = defaults.qcplan_path || '';
              document.getElementById('netlistInput').value = defaults.netlist_path || '';
              document.getElementById('dataInput').value = defaults.data_path || '';
              
              // Populate datastore fields
              if(defaults.datastore_paths && defaults.datastore_paths.length > 0 && global.QCDatastoreHandler){
                const container = document.getElementById('datastoreContainer');
                if(container){
                  // Clear existing entries
                  container.innerHTML = '';
                  // Add each datastore path
                  defaults.datastore_paths.forEach((ds, index) => {
                    const entry = document.createElement('div');
                    entry.className = 'flex gap-2 datastore-entry';
                    entry.innerHTML = `
                      <input type="text" class="input input-bordered flex-1 datastore-input" placeholder="Optional: specifies the path to the simulation data" data-index="${index}" value="${ds}">
                      <button type="button" class="btn btn-sm btn-ghost hover:btn-error remove-datastore-btn" title="Remove this datastore">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                      </button>
                    `;
                    container.appendChild(entry);
                  });
                  // Re-attach remove handlers
                  if(global.QCDatastoreHandler.init){
                    global.QCDatastoreHandler.init();
                  }
                }
              }
              
              document.getElementById('debugInput').value = defaults.debug_path || '';
              document.getElementById('commonSourceInput').value = defaults.common_source_path || '';
              const refDataPath = defaults.ref_data_path || '';
              document.getElementById('refDataInput').value = refDataPath;
              const refDataCheckbox = document.getElementById('refDataCheckbox');
              if(refDataCheckbox){
                refDataCheckbox.checked = !!refDataPath;
                document.getElementById('refDataInput').disabled = !refDataPath;
              }
              document.getElementById('updateOpt').checked = defaults.update || false;
              document.getElementById('adjustmentOpt').checked = defaults.adjustment !== undefined ? defaults.adjustment : true;
              const noWFEl = document.getElementById('noWFOpt');
              if(noWFEl){
                noWFEl.checked = defaults.no_wf !== undefined ? defaults.no_wf : true;
              }
              document.getElementById('xtalkRelNetOpt').checked = defaults.xtalk_rel_net || false;
              document.getElementById('hierarchyInput').value = defaults.hierarchy || '';
              document.getElementById('verboseInput').value = defaults.verbose || '';
              document.getElementById('includeInput').value = defaults.include || '';
              document.getElementById('xtalkInput').value = defaults.xtalk || '';
              document.getElementById('primesimInput').value = defaults.primesim || '';
              document.getElementById('hspiceInput').value = defaults.hspice || '';
              const internalNodeMapEl = document.getElementById('tmqcInternalNodeMapPath');
              if(internalNodeMapEl){
                internalNodeMapEl.value = defaults.tmqc_internal_node_map_path || '';
              }
              document.getElementById('indexInput').value = defaults.index || '0 2 3';
              document.getElementById('phaseInput').value = defaults.phase || 'specs clear setup';
              
              if(defaults.note && statusNote) statusNote.textContent = defaults.note;
            }
          });
          
          // Show loading spinner
          const loadingSpinner = document.getElementById('testbenchLoadingSpinner');
          const tableWrap = document.getElementById('qcTableWrap');
          if(loadingSpinner) loadingSpinner.classList.remove('hidden');
          if(tableWrap) tableWrap.classList.add('hidden');
          if(statusNote) statusNote.textContent = 'Loading testbench data (PVT status, POCV files, scripts)...';
          
          await loadTestbenches(cell).then(async result => {
            if(result.added > 0){
              const impCount = global.QCState.getDelays().filter(r => 
                global.QCState.isImportantTestbench(r.testbench)
              ).length;
              const nonImpCount = result.total - impCount;
              
              if(statusNote){
                statusNote.textContent = `Loading status for ${result.added} testbench${result.added > 1 ? 'es' : ''}...`;
              }
              
              // Update task script colors for Task Redirect buttons (this can be slow)
              await global.QCApiClient.updateTaskScriptColors(cell);
              
              // Hide loading spinner after all data is loaded
              if(loadingSpinner) loadingSpinner.classList.add('hidden');
              if(tableWrap) tableWrap.classList.remove('hidden');
              
              if(statusNote){
                statusNote.textContent = `Added ${result.added} testbench${result.added > 1 ? 'es' : ''} (${impCount} important, ${nonImpCount} non-important)`;
              }
              
              renderTables();
              startStatusPolling(cell, renderTables);
            } else if(result.total === 0){
              // Hide loading spinner - no testbenches
              if(loadingSpinner) loadingSpinner.classList.add('hidden');
              if(tableWrap) tableWrap.classList.remove('hidden');
              if(statusNote) statusNote.textContent = 'No testbenches found';
            }
          }).catch(error => {
            // Hide loading spinner on error
            if(loadingSpinner) loadingSpinner.classList.add('hidden');
            if(tableWrap) tableWrap.classList.remove('hidden');
            console.error('[Timing QC] Error loading testbenches:', error);
            if(statusNote) statusNote.textContent = 'Error loading testbenches';
          });
          
          setLoadedCell(cell);
          
          // Save selection to localStorage
          const sel = getSelectionState();
          if(sel.project && sel.subproject){
            saveLastSelection(sel.project, sel.subproject, cell);
          }
        }
      });
    }
  }

  // ------------------ Button Handlers ------------------
  /**
   * Wire button click handlers
   */
  function wireButtonHandlers(){
    // Run Script button
    const runScriptBtn = document.getElementById('runScriptBtn');
    if(runScriptBtn){
      runScriptBtn.addEventListener('click', async () => {
        const cellSelect = document.getElementById('cellSelect');
        const cell = cellSelect ? cellSelect.value : '';
        const payload = buildPayload();
        
        await runScript(cell, payload, {
          startPolling: () => startStatusPolling(cell, renderTables),
          refreshStatuses: () => {
            refreshAllStatuses(cell).then(() => renderTables());
          }
        });
      });
    }
    
    // Stop Script button
    const stopScriptBtn = document.getElementById('stopScriptBtn');
    if(stopScriptBtn){
      stopScriptBtn.addEventListener('click', stopScript);
    }
    
    // Clear Script button - Handled by component but wired to legacy clearOutput for compatibility
    const clearScriptBtn = document.getElementById('clearScriptBtn');
    if(clearScriptBtn){
      clearScriptBtn.addEventListener('click', clearOutput);
    }
    
    // Open Report button
    const openReportBtn = document.getElementById('openReportBtn');
    if(openReportBtn){
      openReportBtn.addEventListener('click', () => {
        const cellSelect = document.getElementById('cellSelect');
        const cell = cellSelect ? cellSelect.value : '';
        const sel = getSelectionState();
        
        if(!cell || !sel.project || !sel.subproject){
          console.warn('[Timing QC] Cannot open report: missing cell or project/subproject');
          return;
        }
        
        if(global.QCReportOpener && global.QCReportOpener.open){
          global.QCReportOpener.open(sel.project, sel.subproject, cell);
        } else {
          console.error('[Timing QC] QCReportOpener module not loaded');
        }
      });
    }
    
    // Refresh Defaults button
    const refreshDefaultsBtn = document.getElementById('refreshDefaultsBtn');
    if(refreshDefaultsBtn){
      refreshDefaultsBtn.addEventListener('click', async () => {
        const cellSelect = document.getElementById('cellSelect');
        const cell = cellSelect ? cellSelect.value : '';
        if(!cell) return;
        
        const statusNote = document.getElementById('statusNote');
        const defaults = await loadDefaults(cell, true); // Force system defaults
        
        if(defaults){
          document.getElementById('qcplanInput').value = defaults.qcplan_path || '';
          document.getElementById('netlistInput').value = defaults.netlist_path || '';
          document.getElementById('dataInput').value = defaults.data_path || '';
          
          // Reset datastore to single empty field
          const container = document.getElementById('datastoreContainer');
          if(container){
            container.innerHTML = `
              <div class="flex gap-2 datastore-entry">
                <input type="text" class="input input-bordered flex-1 datastore-input" placeholder="Optional: specifies the path to the simulation data" data-index="0">
                <button type="button" class="btn btn-sm btn-ghost hover:btn-error remove-datastore-btn" title="Remove this datastore">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                </button>
              </div>
            `;
            // Re-attach remove handlers
            if(global.QCDatastoreHandler && global.QCDatastoreHandler.init){
              global.QCDatastoreHandler.init();
            }
          }
          
          document.getElementById('debugInput').value = defaults.debug_path || '';
          document.getElementById('commonSourceInput').value = defaults.common_source_path || '';
          const refDataPath = defaults.ref_data_path || '';
          document.getElementById('refDataInput').value = refDataPath;
          const refDataCheckbox = document.getElementById('refDataCheckbox');
          if(refDataCheckbox){
            refDataCheckbox.checked = !!refDataPath;
            document.getElementById('refDataInput').disabled = !refDataPath;
          }
          document.getElementById('updateOpt').checked = false;
          document.getElementById('adjustmentOpt').checked = true;
          const noWFEl = document.getElementById('noWFOpt');
          if(noWFEl){ noWFEl.checked = true; }
          document.getElementById('xtalkRelNetOpt').checked = false;
          document.getElementById('hierarchyInput').value = '';
          document.getElementById('verboseInput').value = '';
          document.getElementById('includeInput').value = '';
          document.getElementById('xtalkInput').value = '';
          document.getElementById('primesimInput').value = '';
          document.getElementById('hspiceInput').value = '';
          document.getElementById('indexInput').value = '0 2 3';
          document.getElementById('phaseInput').value = 'specs clear setup';
          
          if(statusNote) statusNote.textContent = 'Reset to system defaults';
        }
      });
    }
    
    // Refresh Testbenches button
    const refreshTestbenchesBtn = document.getElementById('refreshTestbenchesBtn');
    if(refreshTestbenchesBtn){
      refreshTestbenchesBtn.addEventListener('click', async () => {
        const cellSelect = document.getElementById('cellSelect');
        const cell = cellSelect ? cellSelect.value : '';
        if(!cell){
          alert('Select a cell first');
          return;
        }

        // Avoid stale selection/polling while the table is being re-synced
        setSelectedIndex(null);
        clearStatusPoll();
        
        const btn = refreshTestbenchesBtn;
        const icon = document.getElementById('reloadIcon');
        const statusNote = document.getElementById('statusNote');
        const loadingSpinner = document.getElementById('testbenchLoadingSpinner');
        const tableWrap = document.getElementById('qcTableWrap');
        const currentTab = getCurrentTab();
        const isEqualizerTab = currentTab === 'equalizer';
        const isPostEqualizerTab = currentTab === 'post-equalizer';
        
        btn.disabled = true;
        if(icon){
          icon.style.display = 'inline-block';
          icon.style.animation = 'spin 1s linear infinite';
        }
        
        // Show loading spinner
        if(loadingSpinner) loadingSpinner.classList.remove('hidden');
        if(tableWrap && !isEqualizerTab && !isPostEqualizerTab) tableWrap.classList.add('hidden');
        if(statusNote) statusNote.textContent = 'Refreshing testbench data...';
        
        await loadTestbenches(cell);
        
        if(statusNote) statusNote.textContent = 'Updating PVT status and script colors...';
        await refreshAllStatuses(cell);
        await global.QCApiClient.updateTaskScriptColors(cell);

        if(isEqualizerTab){
          // Keep equalizer view isolated from QC table refresh rendering.
          showEqualizerView();
          if(global.QCEqualizer && typeof global.QCEqualizer.load === 'function'){
            await global.QCEqualizer.load();
          }
        } else if(isPostEqualizerTab){
          showPostEqualizerView();
          if(global.QCPostEqualizer && typeof global.QCPostEqualizer.load === 'function'){
            await global.QCPostEqualizer.load();
          }
        } else {
          renderTables();

          // Resume polling after reload
          startStatusPolling(cell, renderTables);
        }
        
        // Hide loading spinner after all operations complete
        if(loadingSpinner) loadingSpinner.classList.add('hidden');
        if(tableWrap && !isEqualizerTab && !isPostEqualizerTab) tableWrap.classList.remove('hidden');
        if(icon) icon.style.animation = '';
        btn.disabled = false;
        if(statusNote) statusNote.textContent = 'Testbenches reloaded';
      });
    }
    
    // Open Explorer button
    const openExplorerBtn = document.getElementById('openExplorerBtn');
    if(openExplorerBtn){
      openExplorerBtn.addEventListener('click', () => {
        const filteredRows = getFilteredTestbenches();
        const selectedIndex = global.QCState.getSelectedIndex();
        
        if(selectedIndex == null || selectedIndex < 0 || selectedIndex >= filteredRows.length){
          alert('Please select a testbench first');
          return;
        }
        
        const row = filteredRows[selectedIndex];
        const sel = getSelectionState();
        const cellSelect = document.getElementById('cellSelect');
        const cell = cellSelect ? cellSelect.value : '';
        
        if(row && sel.project && sel.subproject && cell){
          const relativePath = `quality/4_qc/${cell}/simulations_${cell}/${row.testbench}`;
          const url = `/explorer?project=${encodeURIComponent(sel.project)}&subproject=${encodeURIComponent(sel.subproject)}&path=${encodeURIComponent(relativePath)}`;
          window.open(url, '_blank');
        }
      });
      
      // Enable/disable based on selection
      const qcTable = document.getElementById('qcTable');
      if(qcTable){
        qcTable.addEventListener('click', () => {
          const filteredRows = getFilteredTestbenches();
          const selectedIndex = global.QCState.getSelectedIndex();
          openExplorerBtn.disabled = (selectedIndex === null || selectedIndex < 0 || selectedIndex >= filteredRows.length);
        });
      }
    }
  }

  // ------------------ Tab Handlers ------------------
  /**
   * Wire tab switching handlers
   */
  function wireTabHandlers(){
    const importantTab = document.getElementById('importantTab');
    const nonImportantTab = document.getElementById('nonImportantTab');
    const equalizerTab = document.getElementById('equalizerTab');
    const postEqualizerTab = document.getElementById('postEqualizerTab');
    
    if(importantTab){
      importantTab.addEventListener('click', (e) => {
        e.preventDefault();
        setCurrentTab('important');
        setSelectedIndex(null);
        saveLastTab('important');
        importantTab.classList.add('tab-active');
        if(nonImportantTab) nonImportantTab.classList.remove('tab-active');
        if(equalizerTab) equalizerTab.classList.remove('tab-active');
        if(postEqualizerTab) postEqualizerTab.classList.remove('tab-active');
        showTestbenchView();
        renderTables();
      });
    }
    
    if(nonImportantTab){
      nonImportantTab.addEventListener('click', (e) => {
        e.preventDefault();
        setCurrentTab('non-important');
        setSelectedIndex(null);
        saveLastTab('non-important');
        if(importantTab) importantTab.classList.remove('tab-active');
        nonImportantTab.classList.add('tab-active');
        if(equalizerTab) equalizerTab.classList.remove('tab-active');
        if(postEqualizerTab) postEqualizerTab.classList.remove('tab-active');
        showTestbenchView();
        renderTables();
      });
    }

    if(equalizerTab){
      equalizerTab.addEventListener('click', (e) => {
        e.preventDefault();
        setCurrentTab('equalizer');
        setSelectedIndex(null);
        saveLastTab('equalizer');
        if(importantTab) importantTab.classList.remove('tab-active');
        if(nonImportantTab) nonImportantTab.classList.remove('tab-active');
        equalizerTab.classList.add('tab-active');
        if(postEqualizerTab) postEqualizerTab.classList.remove('tab-active');
        showEqualizerView();
        if(global.QCEqualizer){
          global.QCEqualizer.load();
        }
      });
    }

    if(postEqualizerTab){
      postEqualizerTab.addEventListener('click', (e) => {
        e.preventDefault();
        setCurrentTab('post-equalizer');
        setSelectedIndex(null);
        saveLastTab('post-equalizer');
        if(importantTab) importantTab.classList.remove('tab-active');
        if(nonImportantTab) nonImportantTab.classList.remove('tab-active');
        if(equalizerTab) equalizerTab.classList.remove('tab-active');
        postEqualizerTab.classList.add('tab-active');
        showPostEqualizerView();
        if(global.QCPostEqualizer){
          global.QCPostEqualizer.load();
        }
      });
    }
  }

  /**
   * Show testbench table view
   */
  function showTestbenchView(){
    const qcTableWrap = document.getElementById('qcTableWrap');
    const equalizerTableWrap = document.getElementById('equalizerTableWrap');
    const postEqualizerTableWrap = document.getElementById('postEqualizerTableWrap');
    const testbenchLegend = document.getElementById('testbenchLegend');
    
    if(qcTableWrap) qcTableWrap.classList.remove('hidden');
    if(equalizerTableWrap) equalizerTableWrap.classList.add('hidden');
    if(postEqualizerTableWrap) postEqualizerTableWrap.classList.add('hidden');
    if(testbenchLegend) testbenchLegend.classList.remove('hidden');
  }

  /**
   * Show equalizer table view
   */
  function showEqualizerView(){
    const qcTableWrap = document.getElementById('qcTableWrap');
    const equalizerTableWrap = document.getElementById('equalizerTableWrap');
    const postEqualizerTableWrap = document.getElementById('postEqualizerTableWrap');
    const testbenchLegend = document.getElementById('testbenchLegend');
    
    if(qcTableWrap) qcTableWrap.classList.add('hidden');
    if(equalizerTableWrap) equalizerTableWrap.classList.remove('hidden');
    if(postEqualizerTableWrap) postEqualizerTableWrap.classList.add('hidden');
    if(testbenchLegend) testbenchLegend.classList.add('hidden');
  }

  /**
   * Show post-equalizer table view
   */
  function showPostEqualizerView(){
    const qcTableWrap = document.getElementById('qcTableWrap');
    const equalizerTableWrap = document.getElementById('equalizerTableWrap');
    const postEqualizerTableWrap = document.getElementById('postEqualizerTableWrap');
    const testbenchLegend = document.getElementById('testbenchLegend');

    if(qcTableWrap) qcTableWrap.classList.add('hidden');
    if(equalizerTableWrap) equalizerTableWrap.classList.add('hidden');
    if(postEqualizerTableWrap) postEqualizerTableWrap.classList.remove('hidden');
    if(testbenchLegend) testbenchLegend.classList.add('hidden');
  }

  // ------------------ Toggle Handlers ------------------
  /**
   * Wire collapsible toggle handlers
   */
  function wireToggleHandlers(){
    // Details/Settings toggle
    const detailsToggle = document.getElementById('detailsToggle');
    const detailsContent = document.getElementById('detailsContent');
    const detailsChevron = document.getElementById('detailsChevron');
    
    if(detailsToggle && detailsContent && detailsChevron){
      detailsToggle.addEventListener('click', () => {
        const isHidden = detailsContent.classList.contains('hidden');
        if(isHidden){
          detailsContent.classList.remove('hidden');
          detailsChevron.style.transform = 'rotate(90deg)';
        } else {
          detailsContent.classList.add('hidden');
          detailsChevron.style.transform = 'rotate(0deg)';
        }
      });
    }
    
    // Ref Data checkbox toggle
    const refDataCheckbox = document.getElementById('refDataCheckbox');
    const refDataInput = document.getElementById('refDataInput');
    
    if(refDataCheckbox && refDataInput){
      refDataCheckbox.addEventListener('change', () => {
        refDataInput.disabled = !refDataCheckbox.checked;
      });
    }
    
    // Execution Output toggle - now handled by execution_output.html component template
  }

  // ------------------ Table Handlers ------------------
  /**
   * Wire table interaction handlers
   */
  function wireTableHandlers(){
    const qcTable = document.getElementById('qcTable');
    if(qcTable){
      // Row click handler
      qcTable.addEventListener('click', handleRowClick);
      
      // Task Queue button handler
      qcTable.addEventListener('click', (e) => {
        const btn = e.target.closest('.taskqueue-btn');
        if(!btn) return;
        e.stopPropagation();
        
        const testbench = btn.getAttribute('data-testbench');
        const cellSelect = document.getElementById('cellSelect');
        const cell = cellSelect ? cellSelect.value : '';
        
        if(!cell){
          alert('Select a cell first');
          return;
        }
        
        openTaskQueueModal(cell, testbench);
      });
      
      // Run PVT button handler
      qcTable.addEventListener('click', (e) => {
        const btn = e.target.closest('.runpvt-btn');
        if(!btn) return;
        e.stopPropagation();
        
        const testbench = btn.getAttribute('data-testbench');
        const cellSelect = document.getElementById('cellSelect');
        const cell = cellSelect ? cellSelect.value : '';
        
        if(!cell){
          alert('Select a cell first');
          return;
        }
        
        openPvtModal(cell, testbench);
      });
      
      // Task Redirect button handler
      qcTable.addEventListener('click', async (e) => {
        const btn = e.target.closest('.task-redirect-btn');
        if(!btn) return;
        e.stopPropagation();
        
        const testbench = btn.getAttribute('data-testbench');
        const cellSelect = document.getElementById('cellSelect');
        const cell = cellSelect ? cellSelect.value : '';
        
        if(!cell){
          alert('Select a cell first');
          return;
        }
        
        // Get base path and construct testbench directory
        const basePath = await fetch('/api/config/base-path').then(r => r.json()).then(d => d.base_path);
        const selection = window.AppSelection ? window.AppSelection.get() : {project: '', subproject: ''};
        
        if(!selection.project || !selection.subproject){
          alert('Please select a project and subproject');
          return;
        }
        
        // Construct testbench directory path (support both legacy and canonical patterns)
        // Canonical: quality/4_qc/{cell}/simulations_{cell}/{testbench}
        // Legacy: quality/4_qc/simulation_{cell}/{testbench}
        // Try canonical first, fallback to legacy
        const canonicalPath = `${basePath}/${selection.project}/${selection.subproject}/design/timing/quality/4_qc/${cell}/simulations_${cell}/${testbench}`;
        
        // Check which path exists (in reality, just use canonical as primary)
        const folder_run_dir = canonicalPath;
        
        // Construct remote directory path (use canonical structure)
        const username = await fetch('/api/distributed-task/remote-hosts')
          .then(r => r.json())
          .then(hosts => hosts.length > 0 ? hosts[0].username : 'user')
          .catch(() => 'user');
        const remote_dir = `/u/${username}/p4_ws/projects/ucie/${selection.project}/${selection.subproject}/design/timing/quality/4_qc/${cell}/simulations_${cell}/${testbench}`;
        
        // Open distributed task modal
        if(window.DistributedTaskModal){
          window.DistributedTaskModal.open({
            folder_run_dir: folder_run_dir,
            remote_dir: remote_dir,
            sim_command: './runall.csh'
          });
        } else {
          console.error('[Timing QC] DistributedTaskModal not available');
          alert('Task Redirect module not loaded');
        }
      });
    }
  }

  // ------------------ Tab Restoration ------------------
  /**
   * Restore tab selection on page load
   */
  function restoreTabSelection(){
    const savedTab = getCurrentTab();
    const importantTab = document.getElementById('importantTab');
    const nonImportantTab = document.getElementById('nonImportantTab');
    const equalizerTab = document.getElementById('equalizerTab');
    const postEqualizerTab = document.getElementById('postEqualizerTab');

    if(savedTab === 'post-equalizer'){
      if(importantTab) importantTab.classList.remove('tab-active');
      if(nonImportantTab) nonImportantTab.classList.remove('tab-active');
      if(equalizerTab) equalizerTab.classList.remove('tab-active');
      if(postEqualizerTab) postEqualizerTab.classList.add('tab-active');
      showPostEqualizerView();
      if(global.QCPostEqualizer && typeof global.QCPostEqualizer.load === 'function'){
        global.QCPostEqualizer.load();
      }
      return;
    }
    
    if(savedTab === 'equalizer'){
      if(importantTab) importantTab.classList.remove('tab-active');
      if(nonImportantTab) nonImportantTab.classList.remove('tab-active');
      if(equalizerTab) equalizerTab.classList.add('tab-active');
      if(postEqualizerTab) postEqualizerTab.classList.remove('tab-active');
      showEqualizerView();
    } else if(savedTab === 'non-important'){
      if(importantTab) importantTab.classList.remove('tab-active');
      if(nonImportantTab) nonImportantTab.classList.add('tab-active');
      if(equalizerTab) equalizerTab.classList.remove('tab-active');
      if(postEqualizerTab) postEqualizerTab.classList.remove('tab-active');
      showTestbenchView();
    } else {
      if(importantTab) importantTab.classList.add('tab-active');
      if(nonImportantTab) nonImportantTab.classList.remove('tab-active');
      if(equalizerTab) equalizerTab.classList.remove('tab-active');
      if(postEqualizerTab) postEqualizerTab.classList.remove('tab-active');
      showTestbenchView();
    }
  }

  // ------------------ Initialization ------------------
  /**
   * Initialize all event handlers
   */
  function init(){
    console.log('[Timing QC] Initializing event handlers...');
    
    // Initialize script runner elements
    initScriptRunnerElements();
    
    // Wire handlers
    wireCellSelection();
    wireButtonHandlers();
    wireTabHandlers();
    wireToggleHandlers();
    wireTableHandlers();
    
    // Restore tab selection
    restoreTabSelection();
    
    console.log('[Timing QC] Event handlers initialized');
  }

  // ------------------ Export to Global Scope ------------------
  global.QCEventHandlers = {
    init,
    buildPayload,
    wireCellSelection,
    wireButtonHandlers,
    wireTabHandlers,
    wireToggleHandlers,
    wireTableHandlers,
    restoreTabSelection
  };

  console.log('[Timing QC] event_handlers.js loaded');

})(window);
