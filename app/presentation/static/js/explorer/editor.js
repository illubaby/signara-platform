// Explorer editor module: Monaco integration, file & Excel display
(function(){
  window.Explorer = window.Explorer || {};
  const { languageFor, escapeHtml, formatBytes } = Explorer.utils;
  const state = Explorer.state.currentExplorer;

  let monacoEditor = null;
  let monacoDiffEditor = null;
  let monacoLoaded = false;

  function initMonaco(){
    if(monacoLoaded) return;
    const loader = document.createElement('script');
    loader.src = 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.46.0/min/vs/loader.min.js';
    loader.onload = () => {
      window.require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.46.0/min/vs' }});
      window.require(['vs/editor/editor.main'], () => {
        monacoLoaded = true;
        const theme = (document.documentElement.getAttribute('data-theme')||'').includes('dark') ? 'vs-dark':'vs';
        monacoEditor = monaco.editor.create(document.getElementById('fileEditorMonaco'), {
          value: '', language: 'plaintext', theme, automaticLayout: true, fontSize: 12, minimap: { enabled: false }, scrollBeyondLastLine: false
        });
        monacoEditor.onDidChangeModelContent(()=>{
          if(!state.selectedFile) return;
          state.dirty = true;
          document.getElementById('saveFileBtn').disabled = false;
          document.getElementById('editorStatus').textContent = 'Modified';
        });
      });
    };
    document.head.appendChild(loader);
  }

  function recreateEditorIfExcelTablePresent(){
    if(!monacoLoaded) return;
    const container = document.getElementById('fileEditorMonaco');
    if(container.querySelector('table')){
      container.innerHTML='';
      const theme = (document.documentElement.getAttribute('data-theme')||'').includes('dark') ? 'vs-dark':'vs';
      monacoEditor = monaco.editor.create(container, { value:'', language:'plaintext', theme, automaticLayout:true, fontSize:12, minimap:{enabled:false}, scrollBeyondLastLine:false });
      monacoEditor.onDidChangeModelContent(()=>{
        if(!state.selectedFile) return;
        state.dirty = true;
        document.getElementById('saveFileBtn').disabled = false;
        document.getElementById('editorStatus').textContent = 'Modified';
      });
    }
  }

  function setEditorContent(filename, content, readOnly=false){
    if(!monacoLoaded){
      document.getElementById('editorStatus').textContent = 'Editor loading...';
      return;
    }
    recreateEditorIfExcelTablePresent();
    const lang = languageFor(filename);
    const model = monaco.editor.createModel(content, lang);
    monacoEditor.setModel(model);
    monacoEditor.updateOptions({readOnly});
    state.dirty = false;
    document.getElementById('saveFileBtn').disabled = readOnly;
    document.getElementById('editorStatus').textContent = readOnly ? 'Read-only' : '';
  }

  function displayExcelFile(filename, data){
    if(!monacoLoaded){
      document.getElementById('editorStatus').textContent = 'Editor loading...';
      return;
    }
    const editorStatus = document.getElementById('editorStatus');
    if(data.error){
      const errorMsg = `# Excel File: ${filename}\n\n## Error\n\n${data.error}`;
      const model = monaco.editor.createModel(errorMsg, 'markdown');
      monacoEditor.setModel(model);
      monacoEditor.updateOptions({readOnly:true});
      state.dirty = false;
      document.getElementById('saveFileBtn').disabled = true;
      return;
    }
    let html = `<div style="padding:16px;overflow:auto;height:100%;background:var(--fallback-b1,oklch(var(--b1)));color:var(--fallback-bc,oklch(var(--bc)));">`;
    html += `<h2 style=\"margin-top:0;\">📊 ${filename}</h2>`;
    html += `<p style=\"opacity:0.7;font-size:12px;\">Excel file with ${data.sheet_names.length} sheet(s)</p>`;
    if(data.sheet_names.length > 1){
      html += `<div class=\"tabs tabs-boxed mb-4\" style=\"margin-bottom:16px;\">`;
      data.sheet_names.forEach((sheetName, idx)=>{
        const activeClass = idx===0 ? 'tab-active' : '';
        html += `<a class=\"tab ${activeClass}\" onclick=\"Explorer.editor.switchExcelSheet('${sheetName}')\" data-sheet=\"${sheetName}\">${sheetName}</a>`;
      });
      html += `</div>`;
    }
    data.sheet_names.forEach((sheetName, idx)=>{
      const sheetData = data.excel_data[sheetName];
      const displayStyle = idx===0 ? 'block':'none';
      html += `<div id=\"excel-sheet-${sheetName.replace(/[^a-zA-Z0-9]/g,'_')}\" style=\"display:${displayStyle};\" class=\"excel-sheet-content\">`;
      if(sheetData.error){
        html += `<div class=\"alert alert-error\"><strong>Error:</strong> ${sheetData.error}</div>`;
      } else {
        html += `<p style=\"opacity:.7;font-size:11px;margin-bottom:8px;\">Showing ${sheetData.row_count} rows${data.truncated ? ' (truncated)' : ''}</p>`;
        html += `<div style=\"overflow-x:auto;\"><table class=\"table table-xs table-zebra\" style=\"font-size:11px;\">`;
        html += `<thead><tr><th style=\"position:sticky;left:0;background:var(--fallback-b2,oklch(var(--b2)));z-index:10;\">#</th>`;
        sheetData.columns.forEach(col=>{ html += `<th>${escapeHtml(String(col))}</th>`; });
        html += `</tr></thead><tbody>`;
        sheetData.data.forEach((row,rowIdx)=>{
          html += `<tr><td style=\"position:sticky;left:0;background:var(--fallback-b1,oklch(var(--b1)));font-weight:600;\">${rowIdx+1}</td>`;
          row.forEach(cell=>{ html += `<td>${escapeHtml(String(cell))}</td>`; });
          html += `</tr>`;
        });
        html += `</tbody></table></div>`;
      }
      html += `</div>`;
    });
    html += `</div>`;
    const container = document.getElementById('fileEditorMonaco');
    container.innerHTML = html;
    state.dirty = false;
    document.getElementById('saveFileBtn').disabled = true;
  }

  function switchExcelSheet(sheetName){
    document.querySelectorAll('.excel-sheet-content').forEach(el=> el.style.display='none');
    const targetId = `excel-sheet-${sheetName.replace(/[^a-zA-Z0-9]/g,'_')}`;
    const targetSheet = document.getElementById(targetId);
    if(targetSheet) targetSheet.style.display='block';
    document.querySelectorAll('.tabs .tab').forEach(tab => {
      if(tab.getAttribute('data-sheet') === sheetName) tab.classList.add('tab-active');
      else tab.classList.remove('tab-active');
    });
  }

  async function loadFileByPath(filePath){
    const sel = window.AppSelection ? window.AppSelection.get() : {project:'', subproject:''};
    const filename = filePath.split('/').pop();
    const fullPathSpan = document.getElementById('editorFullPath');
    const nameSpan = document.getElementById('editorFilename');
    const copyBtn = document.getElementById('copyPathBtn');
    const status = document.getElementById('editorStatus');

    const fullPath = getFullAbsolutePath(filePath); // existing global helper still inline for now
    nameSpan.textContent = filename;
    fullPathSpan.textContent = fullPath;
    fullPathSpan.title = fullPath;
    copyBtn.style.display = 'block';
    status.textContent = 'Loading...';
    state.selectedFile = filename;
    state.selectedFilePath = filePath;
    state.fullPath = fullPath;

    try {
      let url;
      if(state.mode === 'global') {
        url = `/api/explorer/global/file?root=${encodeURIComponent(state.globalRoot)}&path=${encodeURIComponent(filePath)}`;
      } else {
        url = `/api/explorer/${sel.project}/${sel.subproject}/file?path=${encodeURIComponent(filePath)}`;
      }
      const data = await Explorer.utils.fetchJSON(url);
      if (data.base_path && !state.basePathFromBackend) {
        state.basePathFromBackend = data.base_path;
        state.fullPath = getFullAbsolutePath(filePath);
        fullPathSpan.textContent = state.fullPath;
        fullPathSpan.title = state.fullPath;
      }
      if(data.is_excel){
        displayExcelFile(filename, data);
        status.textContent = data.truncated ? 'Loaded (truncated)' : '';
      } else {
        setEditorContent(filename, data.content || '', false);
        status.textContent = data.truncated ? 'Loaded (truncated)' : '';
      }
    } catch(err){
      console.error(err);
      setEditorContent(filename, `Error loading file: ${err.message}`, true);
      status.textContent = 'Error';
    }
  }

  // Public API
  Explorer.editor = {
    initMonaco,
    setEditorContent,
    displayExcelFile,
    switchExcelSheet,
    loadFileByPath,
    get monacoLoaded(){ return monacoLoaded; },
    get monacoEditor(){ return monacoEditor; },
    get monacoDiffEditor(){ return monacoDiffEditor; },
    set monacoDiffEditor(v){ monacoDiffEditor = v; }
  };

  // Kick off Monaco lazy load immediately
  initMonaco();
})();