/**
 * Shared form utilities for auto-populating fields from AppSelection
 *   window.FormConfig = async function() {
 *     return {
 *       output_dir: '/path/to/output',
 *       script_name: 'script.csh',
 *       executionDir: '/path/to/exec',
 *       command: '/path/to/script.csh',
 *       cell_root: '/path/to/cell'
 *     };
 *   };
 */

/**
 * Toggle all checkboxes in a check_group (used for bulk tick/untick)
 * @param {string} checkGroup - The check_group value to target
 * @param {boolean} checked - True to check, false to uncheck
 */
window.toggleCheckGroup = function(checkGroup, checked) {
  const checkboxes = document.querySelectorAll(`input[type="checkbox"][data-check-group="${checkGroup}"]`);
  checkboxes.forEach(cb => {
    cb.checked = checked;
  });
};

(function(global) {
  'use strict';

  /**
   * Setup optional checkbox handlers to enable/disable fields
   */
  function setupOptionalCheckboxes() {
    const optionalCheckboxes = document.querySelectorAll('input[data-optional-checkbox="true"]');
    optionalCheckboxes.forEach(checkbox => {
      const targetFieldId = checkbox.dataset.targetField;
      const targetField = document.getElementById(targetFieldId);
      
      if (!targetField) return;
      
      // Initial state
      targetField.disabled = !checkbox.checked;
      
      // Toggle field on checkbox change
      checkbox.addEventListener('change', function() {
        targetField.disabled = !this.checked;
        if (!this.checked) {
          // Optionally clear the field when disabled (comment out to preserve value)
          // targetField.value = '';
        }
      });
    });
  }

  /**
   * Setup multi-value field handlers (add/remove buttons)
   */
  function setupMultiValueFields() {
    // Handle "Add" buttons
    document.querySelectorAll('.multi-add-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        const targetId = this.dataset.target;
        const fieldName = this.dataset.fieldName;
        const placeholder = this.dataset.placeholder || '';
        const container = document.getElementById(targetId);
        
        if (container) {
          const newRow = document.createElement('div');
          newRow.className = 'flex gap-2 mb-2 multi-input-row';
          newRow.innerHTML = `
            <input type="text" name="${fieldName}[]" value="" class="input input-bordered flex-1" placeholder="${placeholder}">
            <button type="button" class="btn btn-error btn-sm multi-remove-btn">Remove</button>
          `;
          
          // Insert before the "Add" button
          container.insertBefore(newRow, this);
          
          // Attach remove handler to the new button
          newRow.querySelector('.multi-remove-btn').addEventListener('click', function() {
            newRow.remove();
          });
        }
      });
    });
    
    // Handle "Remove" buttons
    document.querySelectorAll('.multi-remove-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        this.closest('.multi-input-row').remove();
      });
    });
  }

  /**
   * Attach handlers for Browse buttons that use FilePicker
   */
  function setupBrowserButtons() {
    const buttons = document.querySelectorAll('button[data-browser="true"][data-target-input]');
    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const targetId = btn.getAttribute('data-target-input');
        const input = document.getElementById(targetId);
        if (!input) return;
        console.debug('[layout_form] Browse clicked. targetId=', targetId, 'current input value=', input.value);
        // Use global FilePicker (const/let globals aren't on window)
        /* eslint-disable no-undef */
        if (typeof FilePicker !== 'undefined' && typeof FilePicker.open === 'function') {
          console.debug('[layout_form] Opening FilePicker');
          FilePicker.open((path /*, isDirectory*/ ) => {
            console.debug('[layout_form] FilePicker selected path:', path);
            input.value = path;
          });
        } else {
          console.warn('[layout_form] FilePicker not available');
        }
      });
    });
  }

  /**
   * Auto-populate prj and rel fields from AppSelection on page load
   * Call this function in pages that need project/subproject auto-fill
   */
  function autoPopulateProjectFields() {
    const selection = global.AppSelection ? global.AppSelection.get() : {project: '', subproject: ''};
    
    const prjInput = document.getElementById('prj');
    const relInput = document.getElementById('rel');
    const dataReleaseInput = document.getElementById('dataRelease');
    const planInput = document.getElementById('plan');
    const prjInfoInput = document.getElementById('prj_info');
    
    if (prjInput && selection.project) {
      prjInput.value = selection.project;
    }
    
    if (relInput && selection.subproject) {
      relInput.value = selection.subproject;
    }
    
    // Auto-populate dataRelease with template format
    if (dataReleaseInput && selection.project && selection.subproject) {
      const now = new Date();
      const month = now.toLocaleString('en-US', { month: 'short' });
      const year = now.getFullYear();
      dataReleaseInput.value = `Release_${selection.project}_${selection.subproject}_${month}_${year}`;
    }

    // Auto-populate plan based on project prefix (h1/h2/h3)
    const projectLower = (selection.project || '').toLowerCase().trim();
    if (planInput && projectLower) {
      if (projectLower.startsWith('h1')) {
        planInput.value = "//wwcad/msip/projects/ucie/tb/gr_ucie/design/timing/plan/uciephy_constraint.xlsx";
      } else if (projectLower.startsWith('h2')) {
        planInput.value = "//wwcad/msip/projects/ucie/tb/gr_ucie2_v2/design/timing/plan/uciephy_constraint.xlsx";
      } else if (projectLower.startsWith('h3')) {
        planInput.value = "//wwcad/msip/projects/ucie/tb/gr_ucie3_v1/design/timing/plan/uciephy_constraint.xlsx";
      }
    }

    // Auto-populate specs based on project prefix (h1/h2/h3)
    const specsInput = document.getElementById('specs');
    if (specsInput && projectLower) {
      if (projectLower.startsWith('h1')) {
        specsInput.value = "//wwcad/msip/projects/ucie/tb/gr_ucie/design/timing/sc/SpecialCheck.xlsx";
      } else if (projectLower.startsWith('h2')) {
        specsInput.value = "//wwcad/msip/projects/ucie/tb/gr_ucie2_v2/design/timing/sc/SpecialCheck.xlsx";
      } else if (projectLower.startsWith('h3')) {
        specsInput.value = "//wwcad/msip/projects/ucie/tb/gr_ucie3_v1/design/timing/sc/SpecialCheck.xlsx";
      }
    }

    // Auto-populate prj_info path if both project and release are available
    if (prjInfoInput && selection.project && selection.subproject) {
      prjInfoInput.value = `//wwcad/msip/projects/ucie/${selection.project}/${selection.subproject}/pcs/design/timing/ProjectInfo.xlsx`;
    }
  }

  /**
   * Handle form submission for script generation and execution
   * Automatically submits to /api/script/runall endpoint then streams execution
   */
  function setupFormSubmission() {
    const form = document.querySelector('form');
    if (!form) return;

    const runBtn = document.getElementById('layoutFormRunBtn');
    const statusElement = document.getElementById('layoutFormStatus');

    form.addEventListener('submit', async function(e) {
      e.preventDefault();

      if (runBtn) runBtn.disabled = true;
      if (statusElement) statusElement.innerHTML = '<span class="loading loading-spinner loading-xs"></span> Generating script...';

      // Mark execution lifecycle START (script generation + streaming)
      global.__layoutFormRunning = true;
      console.log('[layout_form] Execution start detected; enabling navigation interception');
      try { global.dispatchEvent(new CustomEvent('execution:start', { detail: { page: getPageCacheKey() } })); } catch (_) {}

      // Detect literal fields by data-literal attribute
      const literalFields = new Set();
      form.querySelectorAll('[data-literal="true"]').forEach(el => {
        literalFields.add(el.name);
      });
      // Detect fields with no-prefix attribute (bare options)
      const noPrefixFields = new Set();
      form.querySelectorAll('[data-no-prefix="true"]').forEach(el => {
        noPrefixFields.add(el.name);
      });
      // Detect fields to exclude from options
      const excludeFields = new Set();
      form.querySelectorAll('[data-exclude-option="true"]').forEach(el => {
        const name = el.getAttribute('name') || el.getAttribute('data-field-name');
        if (name) excludeFields.add(name);
      });


      // Detect optional fields by data-optional attribute
      const optionalFields = new Set();
      form.querySelectorAll('[data-optional="true"]').forEach(el => {
        optionalFields.add(el.name);
      });

      // Detect multi-value fields by data-multi attribute
      const multiFields = new Set();
      form.querySelectorAll('[data-multi="true"]').forEach(el => {
        multiFields.add(el.dataset.fieldName);
      });

      // Detect checkbox fields
      const checkboxFields = new Set();
      form.querySelectorAll('[data-checkbox="true"]').forEach(el => {
        checkboxFields.add(el.name);
      });

      // Collect custom line endings for fields with data-line-ending attribute
      const lineEndingMap = new Map();
      form.querySelectorAll('[data-line-ending]').forEach(el => {
        lineEndingMap.set(el.name, el.getAttribute('data-line-ending'));
      });

      // Collect form data
      const formData = new FormData(form);
      const formObj = {};
      
      // Handle multi-value fields (collect all values into arrays)
      multiFields.forEach(fieldName => {
        if (excludeFields.has(fieldName)) return; // skip excluded multi
        const values = formData.getAll(`${fieldName}[]`).filter(v => v.trim() !== '');
        if (values.length > 0) {
          formObj[fieldName] = values;
        }
      });
      
      // Handle regular fields
      formData.forEach((value, key) => {
        // Skip multi-value array fields (already processed)
        if (key.endsWith('[]')) return;
        // Skip excluded fields
        if (excludeFields.has(key)) return;
        formObj[key] = value;
      });

      // Extract command and convert rest to options array
      // Options format: [key, value, line_ending, no_prefix] where last two are optional
      const command = formObj.command || 'TimingCloseBeta.py';
      const commandLineEnding = lineEndingMap.get('command');  // Get command's custom line ending
      const options = [];
      
      for (const [key, value] of Object.entries(formObj)) {
        if (key === 'command') continue;
        
        // Get custom line ending for this key (if defined)
        const lineEnding = lineEndingMap.get(key);
        const noPrefix = noPrefixFields.has(key);
        
        // For multi-value fields, add each value as a separate option
        if (multiFields.has(key)) {
          if (excludeFields.has(key)) {
            continue; // skip excluded multi
          }
          if (Array.isArray(value)) {
            value.forEach(v => {
              if (v) {
                if (lineEnding !== undefined && noPrefix) {
                  options.push([key, v, lineEnding, true]);
                } else if (lineEnding !== undefined) {
                  options.push([key, v, lineEnding]);
                } else if (noPrefix) {
                  options.push([key, v, undefined, true]);
                } else {
                  options.push([key, v]);
                }
              }
            });
          }
          continue;
        }
        
        // For literal fields, use the value itself as the key (e.g., "serial" instead of "mode")
        if (checkboxFields.has(key)) {
          if (excludeFields.has(key)) continue; // skip excluded checkbox
          // Include flag only if checkbox is present (checked); unchecked not in formObj
          if (lineEnding !== undefined && noPrefix) {
            options.push([key, "", lineEnding, true]);
          } else if (lineEnding !== undefined) {
            options.push([key, "", lineEnding]);
          } else if (noPrefix) {
            options.push([key, "", undefined, true]);
          } else {
            options.push([key, ""]);
          }
        } else if (literalFields.has(key)) {
          if (excludeFields.has(key)) continue; // skip excluded literal
          const el = form.querySelector('[name="' + key + '"]');
          const includeAttr = el && el.getAttribute('data-include-attribute') === 'true';
          if (includeAttr) {
            // Include attribute name (key) with its value (or empty for flag-like)
            if (lineEnding !== undefined && noPrefix) {
              options.push([key, value || "", lineEnding, true]);
            } else if (lineEnding !== undefined) {
              options.push([key, value || "", lineEnding]);
            } else if (noPrefix) {
              options.push([key, value || "", undefined, true]);
            } else {
              options.push([key, value || ""]);
            }
          } else if (value) {
            // Original behavior: treat value itself as flag key
            if (lineEnding !== undefined && noPrefix) {
              options.push([value, "", lineEnding, true]);
            } else if (lineEnding !== undefined) {
              options.push([value, "", lineEnding]);
            } else if (noPrefix) {
              options.push([value, "", undefined, true]);
            } else {
              options.push([value, ""]);  // -serial \ (value becomes key, empty string for value)
            }
          }
        } else {
          if (excludeFields.has(key)) continue; // skip excluded text/number
          // For optional fields, skip if empty (empty string, null, undefined)
          if (optionalFields.has(key) && (!value || value === '')) {
            continue;
          }
          // For other fields, include even if empty (e.g., -release \)
          if (lineEnding !== undefined && noPrefix) {
            options.push([key, value || "", lineEnding, true]);
          } else if (lineEnding !== undefined) {
            options.push([key, value || "", lineEnding]);
          } else if (noPrefix) {
            options.push([key, value || "", undefined, true]);
          } else {
            options.push([key, value || ""]);  // empty string = flag only, no value
          }
        }
      }

      const payload = {
        command: command,
        options: options,
        fill_space: " \\",
        command_line_ending: commandLineEnding  // Pass command's custom line ending
      };

      // Sanitize options: remove boolean literals from values for flags
      payload.options = payload.options.map(pair => {
        const key = pair[0];
        let val = pair[1];
        const lineEnding = pair[2];  // May be undefined
        const noPrefix = pair[3];    // May be undefined
        if (val === 'False' || val === 'True' || val === false || val === true) {
          val = ""; // flags should not carry True/False values
        }
        // Build result array dynamically based on what's defined
        if (noPrefix) {
          return lineEnding !== undefined ? [key, val, lineEnding, true] : [key, val, undefined, true];
        } else if (lineEnding !== undefined) {
          return [key, val, lineEnding];
        } else {
          return [key, val];
        }
      });

      // Check if page has custom FormConfig (e.g., project_release.js)
      let executionConfig = null;
      if (global.FormConfig) {
        try {
          executionConfig = await global.FormConfig();
          payload.output_dir = executionConfig.output_dir;
          payload.script_name = executionConfig.script_name;
        } catch (error) {
          console.error('[setupFormSubmission] Error getting release config:', error);
          if (statusElement) statusElement.innerHTML = '<span class="text-error">Error: Configuration failed</span>';
          if (runBtn) runBtn.disabled = false;
          return;
        }
      }

      // Create symlinks before script generation
      if (executionConfig && executionConfig.cell_root) {
        await fetch('/api/files/symlinks', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ cell_root: executionConfig.cell_root })
        });
      }

      try {
        const response = await fetch('/api/script/runall', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (response.ok) {
          const fileName = payload.script_name || 'runall.csh';
          const filePath = payload.output_dir ? `${payload.output_dir}/${fileName}` : fileName;
          if (statusElement) statusElement.innerHTML = `<span class="text-success">✓ Script generated: ${fileName}</span>`;
          
          // Start streaming execution if ExecutionStreamFactory available and config exists
          if (global.ExecutionStreamFactory && executionConfig) {
            if (statusElement) statusElement.innerHTML = '<span class="text-info">Starting execution...</span>';
            
            const streamController = global.ExecutionStreamFactory.create({
              executionDir: executionConfig.executionDir || executionConfig.output_dir,
              command: executionConfig.command,
              containerId: 'layoutFormExecution',
              shell: '/bin/csh',
              onComplete: (result) => {
                if (statusElement) {
                  const msg = result.success 
                    ? `<span class="text-success">✓ Execution completed successfully</span>` 
                    : `<span class="text-error">✗ Execution failed (exit code: ${result.returnCode})</span>`;
                  statusElement.innerHTML = msg;
                }
                if (runBtn) runBtn.disabled = false;
                global.__layoutFormRunning = false;
                console.log('[layout_form] Execution completed; success=', result.success);
                try { global.dispatchEvent(new CustomEvent('execution:end', { detail: { success: result.success } })); } catch (_) {}
              },
              onError: (error) => {
                if (statusElement) statusElement.innerHTML = `<span class="text-error">✗ Execution error: ${error.detail || 'Unknown error'}</span>`;
                if (runBtn) runBtn.disabled = false;
                global.__layoutFormRunning = false;
                console.log('[layout_form] Execution error; details=', error);
                try { global.dispatchEvent(new CustomEvent('execution:end', { detail: { success: false, error } })); } catch (_) {}
              }
            });
            
            if (streamController) {
              streamController.connect();
            } else {
              if (statusElement) statusElement.innerHTML = '<span class="text-error">✗ Failed to create execution stream</span>';
              if (runBtn) runBtn.disabled = false;
            }
          } else {
            // No streaming available, just show success
            if (runBtn) runBtn.disabled = false;
            global.__layoutFormRunning = false; // Nothing to stream; treat as ended
            console.log('[layout_form] No streaming; marking execution end; ok=', response.ok);
            try { global.dispatchEvent(new CustomEvent('execution:end', { detail: { success: response.ok } })); } catch (_) {}
          }
        } else {
          if (statusElement) statusElement.innerHTML = `<span class="text-error">✗ Error: Failed to generate script</span>`;
          if (runBtn) runBtn.disabled = false;
          global.__layoutFormRunning = false;
          console.log('[layout_form] Script generation failed; response not ok');
          try { global.dispatchEvent(new CustomEvent('execution:end', { detail: { success: false } })); } catch (_) {}
        }
      } catch (error) {
        console.error('Error:', error);
        if (statusElement) statusElement.innerHTML = `<span class="text-error">✗ Network error: ${error.message}</span>`;
        if (runBtn) runBtn.disabled = false;
        global.__layoutFormRunning = false;
        console.log('[layout_form] Network error during execution start:', error);
        try { global.dispatchEvent(new CustomEvent('execution:end', { detail: { success: false, error } })); } catch (_) {}
      }
    });
  }

  /**
   * Build localStorage key based on page id
   */
  function getPageCacheKey() {
    const form = document.querySelector('form[data-page-id]');
    if (!form) return null;
    const pageId = form.getAttribute('data-page-id') || 'unknown';
    const path = (global.location && global.location.pathname) ? global.location.pathname : 'unknown-path';
    return `layoutFormState:${pageId}:${path}`;
  }

  /**
   * Persist current form state (text, number, selects, checkboxes, multi-value arrays)
   */
  function saveFormState() {
    const form = document.querySelector('form[data-page-id]');
    if (!form) return;
    const key = getPageCacheKey();
    if (!key) return;

    const state = {};

    // Multi-value containers
    form.querySelectorAll('[data-multi="true"]').forEach(container => {
      const fieldName = container.getAttribute('data-field-name');
      if (!fieldName) return;
      const values = [];
      container.querySelectorAll('input[name="' + fieldName + '[]"]').forEach(inp => {
        const v = inp.value.trim();
        if (v) values.push(v);
      });
      state[fieldName] = values; // empty array OK
    });

    // Regular inputs/selects (exclude multi array inputs processed above)
    form.querySelectorAll('input, select, textarea').forEach(el => {
      const name = el.name;
      if (!name || name.endsWith('[]')) return;
      if (el.type === 'checkbox') {
        state[name] = el.checked;
      } else {
        state[name] = el.value;
      }
    });

    try {
      localStorage.setItem(key, JSON.stringify(state));
    } catch (err) {
      // Non-fatal; storage may be full or disabled
      console.debug('[layout_form] saveFormState failed', err);
    }
  }

  /**
   * Restore form state from localStorage (rebuild multi-value rows)
   */
  function restoreFormState() {
    const form = document.querySelector('form[data-page-id]');
    if (!form) return;
    const key = getPageCacheKey();
    if (!key) return;
    let raw = null;
    try { raw = localStorage.getItem(key); } catch (_) { return; }
    if (!raw) return;
    let state = null;
    try { state = JSON.parse(raw); } catch (_) { return; }
    if (!state || typeof state !== 'object') return;

    // Restore multi-value fields first
    form.querySelectorAll('[data-multi="true"]').forEach(container => {
      const fieldName = container.getAttribute('data-field-name');
      if (!fieldName) return;
      const values = state[fieldName];
      if (!Array.isArray(values)) return;

      // Remove existing rows
      container.querySelectorAll('.multi-input-row').forEach(row => row.remove());

      // Insert rows for each saved value, or one empty row if none
      if (values.length === 0) {
        const emptyRow = document.createElement('div');
        emptyRow.className = 'flex gap-2 mb-2 multi-input-row';
        emptyRow.innerHTML = `
          <input type="text" name="${fieldName}[]" value="" class="input input-bordered flex-1" placeholder="">
          <button type="button" class="btn btn-error btn-sm multi-remove-btn">Remove</button>
        `;
        container.insertBefore(emptyRow, container.querySelector('.multi-add-btn'));
      } else {
        values.forEach(v => {
          const newRow = document.createElement('div');
          newRow.className = 'flex gap-2 mb-2 multi-input-row';
          newRow.innerHTML = `
            <input type="text" name="${fieldName}[]" value="${v}" class="input input-bordered flex-1" placeholder="">
            <button type="button" class="btn btn-error btn-sm multi-remove-btn">Remove</button>
          `;
          container.insertBefore(newRow, container.querySelector('.multi-add-btn'));
        });
      }
    });

    // Reattach remove handlers to restored rows
    form.querySelectorAll('.multi-remove-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        this.closest('.multi-input-row').remove();
        saveFormState();
      });
    });

    // Restore other fields
    Object.entries(state).forEach(([name, value]) => {
      // Skip multi since handled
      const container = form.querySelector('[data-multi="true"][data-field-name="' + name + '"]');
      if (container) return;
      const el = form.querySelector('[name="' + name + '"]');
      if (!el) return;
      if (el.type === 'checkbox') {
        el.checked = !!value;
      } else if (value !== undefined && value !== null) {
        el.value = value;
      }
    });
  }

  /**
   * Attach auto-save listeners (debounced) and ensure restore executes once
   */
  function setupFormStatePersistence() {
    const form = document.querySelector('form[data-page-id]');
    if (!form) return;
    // Only restore on load; do NOT auto-save on every input/change.
    restoreFormState();
    // Persist ONLY on explicit Run (submit) as requested.
    form.addEventListener('submit', () => {
      saveFormState();
    });
  }

  // Auto-execute on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      setupOptionalCheckboxes();
      setupMultiValueFields();
      setupBrowserButtons();
      autoPopulateProjectFields();
      setupFormSubmission();
      setupFormStatePersistence();
    });
  } else {
    // DOM already loaded
    setupOptionalCheckboxes();
    setupMultiValueFields();
    setupBrowserButtons();
    autoPopulateProjectFields();
    setupFormSubmission();
    setupFormStatePersistence();
  }

  // Export to global scope for manual invocation if needed
  global.LayoutForm = global.LayoutForm || {};
  global.LayoutForm.setupMultiValueFields = setupMultiValueFields;
  global.LayoutForm.setupBrowserButtons = setupBrowserButtons;
  global.LayoutForm.autoPopulateProjectFields = autoPopulateProjectFields;
  global.LayoutForm.setupFormSubmission = setupFormSubmission;
  global.LayoutForm.saveFormState = saveFormState;
  global.LayoutForm.restoreFormState = restoreFormState;
  global.LayoutForm.setupFormStatePersistence = setupFormStatePersistence;

  /**
   * Intercept navigation while a layout form execution is running.
   * If running, open requested link in a NEW TAB instead of navigating away
   * to avoid terminating the background execution.
   */
  function setupNavigationInterception() {
    document.addEventListener('click', function(ev) {
      // Only act if execution in progress
      if (!global.__layoutFormRunning) return; // Not running; allow normal navigation
      const anchor = ev.target.closest ? ev.target.closest('a[href]') : null;
      if (!anchor) return;
      // Ignore anchors explicitly marked to skip interception
      if (anchor.hasAttribute('data-skip-exec-intercept')) return;
      // Ignore hash-only and javascript:void(0)
      const href = anchor.getAttribute('href');
      if (!href || href.startsWith('#') || href.startsWith('javascript:')) return;
      console.log('[layout_form] Intercepting navigation while running; opening in new tab:', href);
      ev.preventDefault();
      try {
        window.open(anchor.href, '_blank');
      } catch (_) {
        console.log('[layout_form] window.open failed; falling back to setting target attributes');
        // Fallback: set target if open failed
        anchor.setAttribute('target', '_blank');
        anchor.setAttribute('rel', 'noopener');
        // Allow default after setting target - but we already prevented, so simulate
        anchor.click();
      }
    }, true); // capture to get ahead of other handlers
  }

  setupNavigationInterception();
  global.LayoutForm.setupNavigationInterception = setupNavigationInterception;

})(window);
