// Phase 3 extraction: Post-Edit and Timing QA iframe helpers
(function(global){
  'use strict';
  function sel(){ return global.AppSelection ? global.AppSelection.get() : {project:'', subproject:''}; }

  function _layoutFormStorageKey(pageId, path){
    return `layoutFormState:${pageId}:${path}`;
  }

  function _mergeLayoutFormState(pageId, path, patch){
    const key = _layoutFormStorageKey(pageId, path);
    let existing = {};
    try {
      const raw = localStorage.getItem(key);
      if(raw){
        const parsed = JSON.parse(raw);
        if(parsed && typeof parsed === 'object') existing = parsed;
      }
    } catch (_) {
      existing = {};
    }

    const next = { ...existing, ...patch };
    try {
      localStorage.setItem(key, JSON.stringify(next));
    } catch (_) {
      // non-fatal
    }
  }

  function _pathJoin(base, ...parts){
    const b = (base || '').toString();
    const sep = b.includes('\\') ? '\\' : '/';
    const trimEnd = (s) => s.replace(/[\\/]+$/, '');
    const trimBoth = (s) => s.replace(/^[\\/]+|[\\/]+$/g, '');
    let out = trimEnd(b);
    for(const p of parts){
      const chunk = trimBoth((p || '').toString());
      if(!chunk) continue;
      out = out ? (out + sep + chunk) : chunk;
    }
    return out;
  }

  async function openPostEdit(cell){
    const s=sel();
    const iframe=document.getElementById('postEditIframe');
    if(!iframe) return;

    const pagePath = '/post-edit-v2';
    const pageId = 'post-edit-v2';

    let configFilePath = '';
    let libPath = '';
    if(s.project && s.subproject && cell){
      try {
        // Preferred: build config path under PROJECTS_BASE/<project>/<subproject>/design/timing/sis/<cell>.cfg
        const baseRes = await fetch(`/api/file-picker/default-path?project=${encodeURIComponent(s.project)}&subproject=${encodeURIComponent(s.subproject)}`);
        if(baseRes.ok){
          const baseJson = await baseRes.json();
          const timingPath = (baseJson && baseJson.path) ? String(baseJson.path) : '';
          if(timingPath){
            configFilePath = _pathJoin(timingPath, 'sis', `${cell}.cfg`);
            libPath = _pathJoin(timingPath, 'release', 'raw_lib');
          }
        }

        // If SAF page has an explicit Raw Libs Path, prefer it.
        const rawLibsFromPanel = (document.getElementById('rawLibsPathInput')?.value || '').trim();
        if(rawLibsFromPanel){
          libPath = rawLibsFromPanel;
        }

        // Fallback: use legacy Post-Edit defaults endpoint if needed
        if(!configFilePath){
          const defsUrl = `/api/post-edit/${encodeURIComponent(s.project)}/${encodeURIComponent(s.subproject)}/defaults?cell=${encodeURIComponent(cell)}`;
          const res = await fetch(defsUrl);
          if(res.ok){
            const defs = await res.json();
            configFilePath = (defs && (defs.config_file || defs.config_dir)) ? (defs.config_file || defs.config_dir) : '';
          }
        }
      } catch (_) {
        // defaults are best-effort; still open the page
      }
    }

    // Seed Post-Edit V2 layout_form state so it auto-fills on load.
    // Key format must match shared/layout_form.js: layoutFormState:<page_id>:</post-edit-v2>
    _mergeLayoutFormState(pageId, pagePath, {
      cell: cell || '',
      configfile: configFilePath || '',
      lib: libPath || ''
    });

    const url=new URL(`${pagePath}?embedded=1`, window.location.origin);
    // Vary query params to force iframe reload per click (page itself ignores these).
    if(s.project) url.searchParams.set('project', s.project);
    if(s.subproject) url.searchParams.set('subproject', s.subproject);
    if(cell) url.searchParams.set('cell', cell);
    const targetUrl = url.toString();

    // After iframe loads, force-set form fields (belt-and-suspenders for autofill).
    const onLoad = () => {
      try {
        const doc = iframe.contentDocument;
        const cellInput = doc?.getElementById('cell');
        if(cellInput) {
          cellInput.value = cell || '';
          cellInput.dispatchEvent(new Event('input', { bubbles: true }));
          cellInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
        const cfgInput = doc?.getElementById('configfile');
        if(cfgInput) {
          cfgInput.value = configFilePath || '';
          cfgInput.dispatchEvent(new Event('input', { bubbles: true }));
          cfgInput.dispatchEvent(new Event('change', { bubbles: true }));
        }

        const libInput = doc?.getElementById('lib');
        if(libInput) {
          libInput.value = libPath || '';
          libInput.dispatchEvent(new Event('input', { bubbles: true }));
          libInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
      } catch (err) {
        console.warn('[timing_saf] Unable to inject post-edit-v2 defaults into iframe', err);
      }
      iframe.removeEventListener('load', onLoad);
    };
    iframe.addEventListener('load', onLoad);

    iframe.src = targetUrl;
    const span=document.getElementById('postEditDialogCell');
    if(span) span.textContent = cell?`(${cell})`:'';
    document.getElementById('postEditDialog').showModal();
  }

  function openTimingQA(cell){
    const s=sel(); const iframe=document.getElementById('timingQAIframe'); if(!iframe) return;

    // Prepare optional single-cell list file for TMQA v2
    const prepareSingleCellList = async () => {
      if(!(s.project && s.subproject && cell)) return null;
      try {
        const baseRes = await fetch('/api/config/base-path');
        const baseJson = await baseRes.json();
        const base = baseJson.base_path || '';
        if(!base) return null;
        const dir = `${base}/${s.project}/${s.subproject}/design/timing/release/process`;
        const filename = 'dwc_single_cell.lst';
        const content = `${cell}\n`;
        const createRes = await fetch('/api/files/create', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ dir, filename, content })
        });
        const createJson = await createRes.json();
        return createJson.path || null;
      } catch(err){ console.warn('Single-cell list creation failed', err); return null; }
    };

    const url=new URL('/timing-qa-v2?embedded=1', window.location.origin);
    if(s.project&&s.subproject){ url.searchParams.set('project', s.project); url.searchParams.set('subproject', s.subproject); }

    (async () => {
      let singleCellListPath = null;
      if(cell){
        url.searchParams.set('cell', cell);
        const pePath=(document.getElementById('posteditLibsPathInput')?.value||'').trim();
        if(pePath) url.searchParams.set('data', pePath);
        singleCellListPath = await prepareSingleCellList();
        if(singleCellListPath) url.searchParams.set('celllist', singleCellListPath);
      }

      iframe.src=url.toString();

      // After iframe loads, inject the single-cell list path into the form if available
      if(singleCellListPath){
        const onLoad = () => {
          try {
            const doc = iframe.contentDocument;
            const cellListInput = doc?.getElementById('celllist');
            if(cellListInput) cellListInput.value = singleCellListPath;
          } catch(err){ console.warn('Unable to set cell list in TMQA v2 iframe', err); }
          iframe.removeEventListener('load', onLoad);
        };
        iframe.addEventListener('load', onLoad);
      }

      const span=document.getElementById('timingQADialogCell'); if(span) span.textContent = cell?`(${cell})`:'';
      document.getElementById('timingQADialog').showModal();
    })();
  }

  async function checkPosteditLibCount(cell){
    const s=sel(); if(!s.project||!s.subproject||!cell) return;
    try{ 
      const row=document.querySelector(`tr[data-cell="${cell}"]`); if(!row) return; 
      const btn=row.querySelector('.postedit-settings-btn'); if(!btn) return;
      
      // Get pvt_count from button or row data attribute
      const pvtCount = parseInt(btn.getAttribute('data-pvt-count') || row.getAttribute('data-pvt-count') || '8', 10);
      
      // Get custom postedit libs path from input field
      const posteditPathInput = document.getElementById('posteditLibsPathInput');
      const posteditPath = posteditPathInput?.value?.trim() || '';
      
      // Build API URL with query parameters
      let url = `/api/saf/${s.project}/${s.subproject}/cells/${cell}/postedit-lib-count?pvt_count=${pvtCount}`;
      if(posteditPath){ url += `&postedit_libs_path=${encodeURIComponent(posteditPath)}`; }
      
      const res=await fetch(url); 
      if(!res.ok){ return; }
      const data=await res.json(); 
      const count=data.lib_count||0; 
      
      btn.title = `${count} libs in Post-Edit (expected ${2*pvtCount})`; 
      
      // Remove all color classes including ghost and hover states
      btn.classList.remove('btn-error','btn-success','btn-warning','btn-ghost','hover:btn-primary','btn-outline','opacity-60'); 
      
      if(count >= 2 * pvtCount) { 
        // Match the "Run" button style when complete: btn-outline btn-success opacity-60
        btn.classList.add('btn-outline', 'btn-success', 'opacity-60'); 
        btn.textContent = 'Completed ✓';
        btn.title = `Completed: ${count} libs in Post-Edit (expected ${2*pvtCount}) - click to re-run`;
      } else {
        // Keep default style (btn-ghost hover:btn-primary) for unfinished
        btn.classList.add('btn-ghost', 'hover:btn-primary');
        btn.textContent = 'Run';
        btn.title = `${count}/${2*pvtCount} libs in Post-Edit - click to run`;
      }
    }catch(err){ /* silent */ }
  }

  async function checkPostQALibCount(cell){
    const s=sel(); if(!s.project||!s.subproject||!cell) return;
    try{ 
      const row=document.querySelector(`tr[data-cell="${cell}"]`); if(!row) return; 
      const btn=row.querySelector('.timingqa-settings-btn'); if(!btn) return;
      
      // Get pvt_count from button or row data attribute
      const pvtCount = parseInt(btn.getAttribute('data-pvt-count') || row.getAttribute('data-pvt-count') || '8', 10);
      
      // Build API URL with pvt_count parameter
      const url = `/api/saf/${s.project}/${s.subproject}/cells/${cell}/postqa-lib-count?pvt_count=${pvtCount}`;
      
      const res=await fetch(url); 
      if(!res.ok){ return; }
      const data=await res.json(); 
      const count=data.lib_count||0; 
      const expectedCount = data.expected_count || (2 * pvtCount);
      
      btn.classList.remove('btn-error','btn-success','btn-warning','btn-ghost','hover:btn-primary','btn-outline','opacity-60'); 
      
      if(count >= expectedCount) { 
        // Match the "Run" button style when complete: btn-outline btn-success opacity-60
        btn.classList.add('btn-outline', 'btn-success', 'opacity-60'); 
        btn.textContent = 'Completed ✓';
        btn.title = `Completed: ${count} libs in Timing QA (expected ${expectedCount}) - click to re-run`;
      } else {
        // Keep default style (btn-ghost hover:btn-primary) for unfinished
        btn.classList.add('btn-ghost', 'hover:btn-primary');
        btn.textContent = 'Run';
        btn.title = `${count}/${expectedCount} libs in Timing QA - click to run`;
      }
    }catch(err){ /* silent */ }
  }

  function init(){ /* placeholder for future wiring if needed */ }

  global.SAFPostEditQA = { init, openPostEdit, openTimingQA, checkPosteditLibCount, checkPostQALibCount };
})(window);
