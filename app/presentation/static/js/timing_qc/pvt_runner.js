// Timing QC: PVT Runner Modal
// This module handles the Run PVT modal and job submission

(function(global){
  'use strict';

  // Verify dependencies
  if(!global.QCSharedHttp || !global.QCState || !global.QCApiClient){
    console.error('[Timing QC] pvt_runner.js requires shared_http.js, state.js, and api_client.js');
    return;
  }

  const { escapeHTML, showToast, fetchJSON } = global.QCSharedHttp;
  const { getSelectionState } = global.QCState;
  const { getPvtList, submitPvtJobs, getTaskQueueSettings, createTaskQueue } = global.QCApiClient;

  let runPvtDialog = null;

  // ------------------ Modal Creation ------------------
  /**
   * Create Run PVT dialog modal
   */
  function createModal(){
    if(runPvtDialog) return; // Already created
    
    runPvtDialog = document.createElement('dialog');
    runPvtDialog.id = 'runPvtDialog';
    runPvtDialog.className = 'modal';
    runPvtDialog.innerHTML = `
      <form method="dialog" class="modal-box w-11/12 max-w-4xl" id="runPvtForm">
        <h3 class="font-bold text-lg mb-2">Run Testbench PVTs <span class='font-mono text-sm' id='runPvtTestbenchName'></span></h3>
        <div class='flex flex-col gap-3'>
          <div>
            <label class='label'>
              <span class='label-text font-semibold'>Select PVTs to Run:</span>
              <span class='label-text-alt flex gap-1'>
                <button type='button' class='btn btn-xs btn-ghost' id='runPvtSelectAllBtn'>Select All</button>
                <button type='button' class='btn btn-xs btn-ghost' id='runPvtDeselectAllBtn'>Deselect All</button>
              </span>
            </label>
            <div id='runPvtCheckboxes' class='grid grid-cols-2 md:grid-cols-3 gap-2 p-3 border rounded bg-base-200 max-h-48 overflow-auto'></div>
          </div>
          <div>
            <label class='label'><span class='label-text font-semibold'>Run As (Impostor Mode):</span></label>
            <select id='runPvtImpostor' class='select select-sm select-bordered w-full'>
              <option value='self' selected>Self (Current User)</option>
              <option value='Impostor1'>Impostor1 (congdanh)</option>
              <option value='Impostor2'>Impostor2 (thaison)</option>
            </select>
            <div class='text-[10px] opacity-70 mt-1'>
              ⚠️ Impostor mode runs jobs under different user credentials. Use only when necessary for permissions or quotas.
            </div>
          </div>
          <div>
            <label class='label'><span class='label-text font-semibold'>LSF Queue Options:</span></label>
            <textarea id='runPvtQueueOpts' class='textarea textarea-bordered w-full font-mono text-xs' rows='3'>-app normal -n 1 -M 50G -R "span[hosts=1] rusage[mem=10GB,scratch_free=15]"</textarea>
            <div class='text-[10px] opacity-70 mt-1'>Edit these options to customize memory, CPU, and resource requirements</div>
          </div>
          <div class='collapse collapse-arrow border border-base-300 bg-base-200'>
            <input type='checkbox' id='taskQueueToggle'>
            <div class='collapse-title text-sm font-semibold flex items-center gap-2'>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path>
              </svg>
              Task Queue Configuration (Optional)
            </div>
            <div class='collapse-content'>
              <div class='grid grid-cols-2 gap-2 text-xs mt-2'>
                <label class='form-control'><span class='label-text'>normal_queue_no_prefix</span><input name='tq_normal_queue_no_prefix' class='input input-sm input-bordered' value='1'></label>
                <label class='form-control'><span class='label-text'>job_scheduler</span><input name='tq_job_scheduler' class='input input-sm input-bordered' value='lsf'></label>
                <label class='form-control'><span class='label-text'>run_list_maxsize</span><input name='tq_run_list_maxsize' class='input input-sm input-bordered' value='100'></label>
                <label class='form-control'><span class='label-text'>statistical_montecarlo_sample_size</span><input name='tq_statistical_montecarlo_sample_size' class='input input-sm input-bordered' value='250'></label>
                <label class='form-control'><span class='label-text'>netlist_max_sweeps</span><input name='tq_netlist_max_sweeps' class='input input-sm input-bordered' value='1000'></label>
                <label class='form-control'><span class='label-text'>simulator</span>
                  <select name='tq_simulator' class='select select-sm select-bordered'>
                    <option value='primesim' selected>primesim</option>
                    <option value='hspice'>hspice</option>
                  </select>
                </label>
                <label class='form-control col-span-2'><span class='label-text'>normal_queue</span><input name='tq_normal_queue' class='input input-sm input-bordered' value='-app normal -n 1 -M 50G -R "span[hosts=1] rusage[mem=10GB,scratch_free=15]"'></label>
                <label class='form-control'><span class='label-text'>write monte_carlo_settings.tcl?</span>
                  <select name='tq_write_monte_carlo' class='select select-sm select-bordered'>
                    <option value='true'>Yes</option>
                    <option value='false' selected>No</option>
                  </select>
                </label>
              </div>
              <div class='mt-3 flex justify-end'>
                <button type='button' class='btn btn-sm btn-outline' id='createTaskQueueInPvtBtn'>
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                  </svg>
                  Create Task Queue Files
                </button>
              </div>
              <div id='tqStatusInPvt' class='mt-2 text-[10px] opacity-70'></div>
            </div>
          </div>
        </div>
        <div class='mt-3 flex gap-2 justify-end'>
          <button type='button' class='btn btn-sm' id='runPvtCancelBtn'>Cancel</button>
          <button type='submit' class='btn btn-sm btn-success'>Submit Jobs</button>
        </div>
        <div id='runPvtResult' class='mt-2 text-xs max-h-64 overflow-auto'></div>
        <input type='hidden' name='testbench' id='runPvtTestbenchHidden'>
      </form>
      <form method="dialog" class="modal-backdrop">
        <button>close</button>
      </form>
    `;
    
    document.body.appendChild(runPvtDialog);
    
    // Wire event handlers
    const cancelBtn = document.getElementById('runPvtCancelBtn');
    if(cancelBtn){
      cancelBtn.addEventListener('click', () => closeModal());
    }
    
    const createTqBtn = document.getElementById('createTaskQueueInPvtBtn');
    if(createTqBtn){
      createTqBtn.addEventListener('click', handleCreateTaskQueue);
    }

    const selectAllBtn = document.getElementById('runPvtSelectAllBtn');
    if(selectAllBtn){
      selectAllBtn.addEventListener('click', () => setAllPvtCheckboxes(true));
    }

    const deselectAllBtn = document.getElementById('runPvtDeselectAllBtn');
    if(deselectAllBtn){
      deselectAllBtn.addEventListener('click', () => setAllPvtCheckboxes(false));
    }
    
    const form = document.getElementById('runPvtForm');
    if(form){
      form.addEventListener('submit', handleSubmit);
    }
  }

  // ------------------ Modal Management ------------------
  /**
   * Open Run PVT modal
   * @param {string} cell - Cell name
   * @param {string} testbench - Testbench name
   */
  async function openModal(cell, testbench){
    if(!runPvtDialog) createModal();
    if(!cell){
      showToast('Select a cell first', {type: 'warning'});
      return;
    }
    
    // Update modal title
    const testbenchName = document.getElementById('runPvtTestbenchName');
    if(testbenchName) testbenchName.textContent = `${cell} / ${testbench}`;
    
    // Set testbench hidden field
    const testbenchHidden = document.getElementById('runPvtTestbenchHidden');
    if(testbenchHidden) testbenchHidden.value = testbench;
    
    // Clear results
    const resultDiv = document.getElementById('runPvtResult');
    if(resultDiv) resultDiv.innerHTML = '';
    
    const tqStatusDiv = document.getElementById('tqStatusInPvt');
    if(tqStatusDiv) tqStatusDiv.textContent = '';
    
    // Load PVT list and task queue settings in parallel
    await Promise.all([
      loadPvtList(cell, testbench),
      loadTaskQueueSettings(cell, testbench)
    ]);
    
    // Show modal
    runPvtDialog.showModal();
  }

  /**
   * Close Run PVT modal
   */
  function closeModal(){
    if(runPvtDialog) runPvtDialog.close();
  }

  function setAllPvtCheckboxes(checked){
    document.querySelectorAll('#runPvtCheckboxes input[type=checkbox]').forEach((cb) => {
      cb.checked = checked;
    });
  }

  // ------------------ PVT List Loading ------------------
  /**
   * Load and display PVT checkboxes
   * @param {string} cell - Cell name
   * @param {string} testbench - Testbench name
   */
  async function loadPvtList(cell, testbench){
    const checkboxContainer = document.getElementById('runPvtCheckboxes');
    if(!checkboxContainer) return;
    
    checkboxContainer.innerHTML = '<div class="col-span-full text-center"><span class="loading loading-spinner loading-sm"></span> Loading PVTs...</div>';
    
    try {
      const data = await getPvtList(cell, testbench);
      
      if(data && data.pvts && data.pvts.length > 0){
        checkboxContainer.innerHTML = data.pvts.map(p => {
          const statusCls = p.status === 'Passed' ? 'text-success' 
                          : (p.status === 'Fail' ? 'text-error' 
                          : (p.status === 'Not Started' ? 'text-ghost' 
                          : 'text-warning'));
          
          // Auto-check failed, in progress, or not started PVTs
          const shouldCheck = p.status === 'Fail' || p.status === 'In Progress' 
                           || p.status === 'Not Started' || (!p.status || p.status === '');
          
          const badgeCls = p.status === 'Passed' ? 'badge-success' 
                        : (p.status === 'Fail' ? 'badge-error' 
                        : (p.status === 'Not Started' ? 'badge-ghost' 
                        : 'badge-warning'));
          
          return `<label class='flex items-center gap-2 p-2 rounded hover:bg-base-100 cursor-pointer'>
            <input type='checkbox' name='pvt' value='${escapeHTML(p.pvt)}' class='checkbox checkbox-sm' ${shouldCheck ? 'checked' : ''}>
            <span class='font-mono text-xs flex-1'>${escapeHTML(p.pvt)}</span>
            <span class='badge badge-xs ${badgeCls}'>${escapeHTML(p.status)}</span>
          </label>`;
        }).join('');
      } else {
        checkboxContainer.innerHTML = '<div class="col-span-full text-center opacity-70">No PVTs found</div>';
      }
    } catch(error){
      checkboxContainer.innerHTML = `<div class="col-span-full text-center text-error">Error loading PVTs: ${error.message}</div>`;
    }
  }

  /**
   * Load task queue settings for pre-population
   * @param {string} cell - Cell name
   * @param {string} testbench - Testbench name
   */
  async function loadTaskQueueSettings(cell, testbench){
    try {
      const data = await getTaskQueueSettings(cell, testbench);
      
      if(data && data.values){
        const form = document.getElementById('runPvtForm');
        if(!form) return;
        
        // Populate task queue fields
        for(const [key, value] of Object.entries(data.values)){
          const el = form.querySelector(`[name="tq_${key}"]`);
          if(el) el.value = value;
        }
        
        // Set write_monte_carlo
        const wmEl = form.querySelector('[name="tq_write_monte_carlo"]');
        if(wmEl){
          wmEl.value = data.exists_monte_carlo ? 'true' : 'false';
        }
        
        // Show status if files exist
        if(data.exists_task_queue || data.exists_monte_carlo){
          const names = [
            data.exists_task_queue ? 'sis_task_queue.tcl' : null,
            data.exists_monte_carlo ? 'monte_carlo_settings.tcl' : null
          ].filter(Boolean).join(' & ');
          
          const tqStatusDiv = document.getElementById('tqStatusInPvt');
          if(tqStatusDiv){
            tqStatusDiv.innerHTML = `<span class='text-info'>Existing files: ${names}</span>`;
          }
        }
      }
    } catch(error){
      // Silent fail - no existing settings
    }
  }

  // ------------------ Task Queue Creation ------------------
  /**
   * Handle create task queue button click
   */
  async function handleCreateTaskQueue(){
    const cellSelect = document.getElementById('cellSelect');
    const cell = cellSelect ? cellSelect.value : '';
    const testbenchHidden = document.getElementById('runPvtTestbenchHidden');
    const testbench = testbenchHidden ? testbenchHidden.value : '';
    const resultDiv = document.getElementById('tqStatusInPvt');
    const btn = document.getElementById('createTaskQueueInPvtBtn');
    
    if(!cell || !testbench){
      showToast('Cell or testbench not selected', {type: 'error'});
      return;
    }
    
    if(btn) btn.disabled = true;
    if(resultDiv) resultDiv.innerHTML = '<span class="loading loading-spinner loading-xs"></span> Creating task queue files...';
    
    try {
      const form = document.getElementById('runPvtForm');
      const tqPayload = {};
      
      // Extract task queue fields
      ['normal_queue_no_prefix', 'job_scheduler', 'run_list_maxsize', 'normal_queue',
       'statistical_montecarlo_sample_size', 'netlist_max_sweeps', 'simulator', 'write_monte_carlo'].forEach(key => {
        const el = form.querySelector(`[name="tq_${key}"]`);
        if(el){
          tqPayload[key] = key === 'write_monte_carlo' ? (el.value === 'true') : el.value;
        }
      });
      
      const result = await createTaskQueue(cell, testbench, tqPayload);
      
      const filesCreated = [];
      if(result.sis_task_queue_path){
        filesCreated.push(`<div class='text-success text-[10px] font-mono'>✓ ${result.sis_task_queue_path}</div>`);
      }
      if(result.monte_carlo_settings_path){
        filesCreated.push(`<div class='text-success text-[10px] font-mono'>✓ ${result.monte_carlo_settings_path}</div>`);
      }
      
      if(resultDiv){
        resultDiv.innerHTML = `<div class='text-success font-semibold mb-1'>Task queue files created:</div>${filesCreated.join('')}`;
      }
      
      showToast('Task queue files created successfully', {type: 'success', duration: 3000});
    } catch(error){
      if(resultDiv){
        resultDiv.innerHTML = `<div class='text-error'>Exception: ${error.message}</div>`;
      }
    } finally {
      if(btn) btn.disabled = false;
    }
  }

  // ------------------ Job Submission ------------------
  /**
   * Handle form submission (submit PVT jobs)
   * @param {Event} event - Submit event
   */
  async function handleSubmit(event){
    event.preventDefault();
    
    const cellSelect = document.getElementById('cellSelect');
    const cell = cellSelect ? cellSelect.value : '';
    const testbenchHidden = document.getElementById('runPvtTestbenchHidden');
    const testbench = testbenchHidden ? testbenchHidden.value : '';
    const queueOptsEl = document.getElementById('runPvtQueueOpts');
    const queueOpts = queueOptsEl ? queueOptsEl.value.trim() : '';
    const impostorEl = document.getElementById('runPvtImpostor');
    const impostor = impostorEl ? impostorEl.value : 'self';
    
    // Get selected PVTs
    const selectedPvts = Array.from(
      document.querySelectorAll('#runPvtCheckboxes input[type=checkbox]:checked')
    ).map(cb => cb.value);
    
    if(selectedPvts.length === 0){
      showToast('Please select at least one PVT to run', {type: 'warning'});
      return;
    }
    
    const resultDiv = document.getElementById('runPvtResult');
    if(resultDiv){
      resultDiv.innerHTML = '<div class="flex items-center gap-2"><span class="loading loading-spinner loading-sm"></span><span>Submitting jobs...</span></div>';
    }
    
    try {
      const payload = {
        testbench,
        pvts: selectedPvts,
        queue_opts: queueOpts,
        impostor: impostor === 'self' ? null : impostor
      };
      
      const result = await submitPvtJobs(cell, payload);
      
      // Display results
      const jobs = result.jobs || [];
      const successCount = jobs.filter(j => j.success).length;
      const failCount = jobs.length - successCount;
      
      let html = `<div class='mb-2'><span class='font-semibold'>Results:</span> <span class='text-success'>${successCount} submitted</span>`;
      if(failCount > 0) html += ` <span class='text-error'>${failCount} failed</span>`;
      if(result.note) html += ` <span class='text-info text-xs ml-2'>${escapeHTML(result.note)}</span>`;
      html += '</div><div class="space-y-1">';
      
      jobs.forEach(j => {
        const icon = j.success ? '✓' : '✗';
        const cls = j.success ? 'text-success' : 'text-error';
        const msg = escapeHTML(j.message || j.job_id || 'submitted');
        
        let cmdLine = '';
        if(j.command){
          cmdLine = `<details class='mt-1'><summary class='cursor-pointer text-[10px] underline opacity-70'>Show command</summary><pre class='text-[9px] bg-base-300 p-1 rounded mt-1 overflow-x-auto'>${escapeHTML(j.command)}</pre></details>`;
        }
        
        html += `<div class='${cls} text-[11px]'><span class='font-mono'>${icon} ${escapeHTML(j.pvt)}: ${msg}</span>${cmdLine}</div>`;
      });
      html += '</div>';
      
      if(resultDiv) resultDiv.innerHTML = html;
      
      showToast(`${successCount} job(s) submitted successfully`, {type: 'success', duration: 3000});
      
      // Refresh statuses after a delay
      setTimeout(() => {
        if(global.QCApiClient && global.QCApiClient.refreshAllStatuses){
          global.QCApiClient.refreshAllStatuses(cell);
        }
        if(global.QCTableRenderer && global.QCTableRenderer.renderTables){
          global.QCTableRenderer.renderTables();
        }
      }, 2000);
    } catch(error){
      if(resultDiv){
        resultDiv.innerHTML = `<div class='text-error'>Exception: ${error.message}</div>`;
      }
    }
  }

  // ------------------ Helper Functions ------------------
  /**
   * Get selected PVTs
   * @returns {Array} - Array of selected PVT names
   */
  function getSelectedPvts(){
    return Array.from(
      document.querySelectorAll('#runPvtCheckboxes input[type=checkbox]:checked')
    ).map(cb => cb.value);
  }

  // ------------------ Export to Global Scope ------------------
  global.QCPvtRunner = {
    createModal,
    openModal,
    closeModal,
    loadPvtList,
    getSelectedPvts,
    handleCreateTaskQueue
  };

  console.log('[Timing QC] pvt_runner.js loaded');

})(window);
