// Timing QC: Datastore Handler
// Manages dynamic datastore input fields

(function(global){
  'use strict';

  let datastoreCounter = 1; // Start from 1 since we have index 0 initially

  /**
   * Initialize datastore handlers
   */
  function initDatastoreHandlers(){
    const addBtn = document.getElementById('addDatastoreBtn');
    const container = document.getElementById('datastoreContainer');

    if(!addBtn || !container){
      console.warn('[Timing QC] Datastore elements not found');
      return;
    }

    // Add button handler
    addBtn.addEventListener('click', addDatastoreEntry);

    // Initial remove button handler
    attachRemoveHandlers();
  }

  /**
   * Add a new datastore entry
   */
  function addDatastoreEntry(){
    const container = document.getElementById('datastoreContainer');
    if(!container) return;

    const newEntry = document.createElement('div');
    newEntry.className = 'flex gap-2 datastore-entry';
    newEntry.innerHTML = `
      <input type="text" class="input input-bordered flex-1 datastore-input" placeholder="Optional: specifies the path to the simulation data" data-index="${datastoreCounter}">
      <button type="button" class="btn btn-sm btn-ghost hover:btn-error remove-datastore-btn" title="Remove this datastore">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    `;

    container.appendChild(newEntry);
    datastoreCounter++;
    
    // Attach remove handler to the new button
    attachRemoveHandlers();
  }

  /**
   * Attach remove handlers to all remove buttons
   */
  function attachRemoveHandlers(){
    const removeButtons = document.querySelectorAll('.remove-datastore-btn');
    
    removeButtons.forEach(btn => {
      // Remove existing listeners to avoid duplicates
      const newBtn = btn.cloneNode(true);
      btn.parentNode.replaceChild(newBtn, btn);
      
      newBtn.addEventListener('click', function(){
        const entry = this.closest('.datastore-entry');
        const container = document.getElementById('datastoreContainer');
        
        // Keep at least one entry
        const entries = container.querySelectorAll('.datastore-entry');
        if(entries.length > 1){
          entry.remove();
        } else {
          // If it's the last one, just clear the value
          const input = entry.querySelector('.datastore-input');
          if(input) input.value = '';
        }
      });
    });
  }

  /**
   * Get all datastore values
   * @returns {Array<string>} - Array of non-empty datastore values
   */
  function getDatastoreValues(){
    const inputs = document.querySelectorAll('.datastore-input');
    const values = [];
    
    inputs.forEach(input => {
      const value = input.value.trim();
      if(value){
        values.push(value);
      }
    });
    
    return values;
  }

  // Export to global scope
  global.QCDatastoreHandler = {
    init: initDatastoreHandlers,
    getValues: getDatastoreValues
  };

  console.log('[Timing QC] datastore_handler.js loaded');

})(window);
