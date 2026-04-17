// Timing QC: Task Queue Modal
// This module handles the task queue configuration modal

(function(global){
  'use strict';

  // Verify dependencies
  if(!global.QCSharedHttp || !global.QCState || !global.QCApiClient){
    console.error('[Timing QC] task_queue.js requires shared_http.js, state.js, and api_client.js');
    return;
  }

  const { escapeHTML, showToast } = global.QCSharedHttp;
  const { getSelectionState } = global.QCState;
  const { getTaskQueueSettings, createTaskQueue } = global.QCApiClient;

  let tqDialog = null;

  // ------------------ Modal Creation ------------------
  /**
   * Create task queue dialog modal
   */
  function createModal(){
    if(tqDialog) return; // Already created
    
    tqDialog = document.createElement('dialog');
    tqDialog.id = 'taskQueueDialog';
    tqDialog.className = 'modal';
    tqDialog.innerHTML = `
      <form method="dialog" class="modal-box w-11/12 max-w-2xl" id="taskQueueForm">
        <h3 class="font-bold text-lg mb-2">Create sis_task_queue.tcl <span class='font-mono text-sm' id='tqCellName'></span></h3>
        <div class='grid grid-cols-2 gap-2 text-xs'>
          <label class='form-control'><span class='label-text'>normal_queue_no_prefix</span><input name='normal_queue_no_prefix' class='input input-sm input-bordered' value='1' required></label>
          <label class='form-control'><span class='label-text'>job_scheduler</span><input name='job_scheduler' class='input input-sm input-bordered' value='lsf' required></label>
          <label class='form-control'><span class='label-text'>run_list_maxsize</span><input name='run_list_maxsize' class='input input-sm input-bordered' value='100' required></label>
          <label class='form-control col-span-2'><span class='label-text'>normal_queue</span><input name='normal_queue' class='input input-sm input-bordered' value='-app normal -n 1 -M 50G -R "span[hosts=1] rusage[mem=10GB,scratch_free=15]"' required></label>
          <label class='form-control'><span class='label-text'>statistical_montecarlo_sample_size</span><input name='statistical_montecarlo_sample_size' class='input input-sm input-bordered' value='250' required></label>
          <label class='form-control'><span class='label-text'>netlist_max_sweeps</span><input name='netlist_max_sweeps' class='input input-sm input-bordered' value='1000' required></label>
          <label class='form-control col-span-2'><span class='label-text'>statistical_simulation_points</span><input name='statistical_simulation_points' class='input input-sm input-bordered' value='{1 3 5 7 9 11 13 15 17 19 21 23 25}' required></label>
          <label class='form-control'><span class='label-text'>simulator</span>
            <select name='simulator' class='select select-sm select-bordered'>
              <option value='primesim' selected>primesim</option>
              <option value='hspice'>hspice</option>
            </select>
          </label>
          <label class='form-control'><span class='label-text'>write monte_carlo_settings.tcl?</span>
            <select name='write_monte_carlo' class='select select-sm select-bordered'>
              <option value='true'>Yes</option>
              <option value='false' selected>No</option>
            </select>
          </label>
        </div>
        <div class='mt-3 flex gap-2 justify-end'>
          <button type='button' class='btn btn-sm' id='tqCancelBtn'>Cancel</button>
          <button type='submit' class='btn btn-sm btn-primary'>Create</button>
        </div>
        <div id='tqResult' class='mt-2 text-[11px]'></div>
        <input type='hidden' name='testbench' id='tqTestbenchHidden'>
      </form>
      <form method="dialog" class="modal-backdrop">
        <button>close</button>
      </form>
    `;
    
    document.body.appendChild(tqDialog);
    
    // Wire event handlers
    const cancelBtn = document.getElementById('tqCancelBtn');
    if(cancelBtn){
      cancelBtn.addEventListener('click', () => closeModal());
    }
    
    const form = document.getElementById('taskQueueForm');
    if(form){
      form.addEventListener('submit', handleSubmit);
    }
  }

  // ------------------ Modal Management ------------------
  /**
   * Open task queue modal
   * @param {string} cell - Cell name
   * @param {string} testbench - Testbench name
   */
  async function openModal(cell, testbench){
    if(!tqDialog) createModal();
    if(!cell){
      showToast('Select a cell first', {type: 'warning'});
      return;
    }
    
    // Update modal title
    const cellName = document.getElementById('tqCellName');
    if(cellName) cellName.textContent = `${cell} / ${testbench}`;
    
    // Set testbench hidden field
    const testbenchHidden = document.getElementById('tqTestbenchHidden');
    if(testbenchHidden) testbenchHidden.value = testbench;
    
    // Clear result
    const resultDiv = document.getElementById('tqResult');
    if(resultDiv) resultDiv.textContent = '';
    
    // Load existing settings
    await loadExistingSettings(cell, testbench);
    
    // Show modal
    tqDialog.showModal();
  }

  /**
   * Close task queue modal
   */
  function closeModal(){
    if(tqDialog) tqDialog.close();
  }

  // ------------------ Form Handling ------------------
  /**
   * Load existing task queue settings if present
   * @param {string} cell - Cell name
   * @param {string} testbench - Testbench name
   */
  async function loadExistingSettings(cell, testbench){
    try {
      const data = await getTaskQueueSettings(cell, testbench);
      
      if(data && data.values){
        const form = document.getElementById('taskQueueForm');
        if(!form) return;
        
        // Populate form fields
        for(const [key, value] of Object.entries(data.values)){
          const el = form.querySelector(`[name="${key}"]`);
          if(el) el.value = value;
        }
        
        // Set write_monte_carlo based on file existence
        const wmEl = form.querySelector('[name="write_monte_carlo"]');
        if(wmEl){
          wmEl.value = data.exists_monte_carlo ? 'true' : 'false';
        }
        
        // Show warning if files exist
        if(data.exists_task_queue || data.exists_monte_carlo){
          const names = [
            data.exists_task_queue ? 'sis_task_queue.tcl' : null,
            data.exists_monte_carlo ? 'monte_carlo_settings.tcl' : null
          ].filter(Boolean).join(' & ');
          
          updateResultDisplay(
            `<span class='text-warning'>Existing files will be overwritten: ${names}</span>`
          );
        }
      }
    } catch(error){
      // Silent fail - no existing settings
    }
  }

  /**
   * Handle form submission
   * @param {Event} event - Submit event
   */
  async function handleSubmit(event){
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const testbench = formData.get('testbench');
    const cellSelect = document.getElementById('cellSelect');
    const cell = cellSelect ? cellSelect.value : '';
    
    if(!cell || !testbench){
      showToast('Cell or testbench not selected', {type: 'error'});
      return;
    }
    
    // Build payload
    const payload = {};
    formData.forEach((value, key) => {
      if(key === 'testbench') return;
      if(key === 'write_monte_carlo'){
        payload[key] = (value === 'true');
      } else {
        payload[key] = value;
      }
    });
    
    updateResultDisplay('<span class="loading loading-spinner loading-xs"></span> Writing files...');
    
    try {
      const result = await createTaskQueue(cell, testbench, payload);
      
      const files = [];
      if(result.sis_task_queue_path){
        files.push(`<code>${result.sis_task_queue_path}</code>`);
      }
      if(result.monte_carlo_settings_path){
        files.push(`<code>${result.monte_carlo_settings_path}</code>`);
      }
      
      updateResultDisplay(
        `<div class='text-success'>${result.note || 'Done'}: ${files.join(' & ')}</div>`
      );
      
      showToast('Task queue files created successfully', {type: 'success', duration: 3000});
    } catch(error){
      updateResultDisplay(`<span class='text-error'>${error.message}</span>`);
    }
  }

  /**
   * Update result display in modal
   * @param {string} html - HTML to display
   */
  function updateResultDisplay(html){
    const resultDiv = document.getElementById('tqResult');
    if(resultDiv) resultDiv.innerHTML = html;
  }

  // ------------------ Export to Global Scope ------------------
  global.QCTaskQueue = {
    createModal,
    openModal,
    closeModal,
    loadExistingSettings,
    updateResultDisplay
  };

  console.log('[Timing QC] task_queue.js loaded');

})(window);
