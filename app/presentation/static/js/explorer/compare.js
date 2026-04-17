(function(){
  window.Explorer = window.Explorer || {};
  const Explorer = window.Explorer;
  Explorer.compare = Explorer.compare || {};

  // Dependencies expected: Explorer.state.currentExplorer, Explorer.utils.fetchJSON, Explorer.utils.languageFor, Explorer.utils.getDiffStats
  // Monaco editor objects exposed by Explorer.editor (monacoEditor, monacoDiffEditor, monacoLoaded) through getters.

  function _getCurrentExplorer(){
    return (Explorer.state && Explorer.state.currentExplorer) ? Explorer.state.currentExplorer : window.currentExplorer; // fallback
  }
  function _getUtils(){ return Explorer.utils || {}; }
  function _getEditor(){ return Explorer.editor || {}; }

  function handleCompareSelection(filePath, targetElement){
    const currentExplorer = _getCurrentExplorer();
    const editorStatus = document.getElementById('editorStatus');
    if (currentExplorer.compareSelection === filePath) {
      currentExplorer.compareSelection = null;
      targetElement.classList.remove('bg-info', 'text-info-content');
      editorStatus.textContent = 'Compare selection cleared';
    } else {
      document.querySelectorAll('.tree-item').forEach(el => {
        el.classList.remove('bg-info', 'text-info-content');
      });
      currentExplorer.compareSelection = filePath;
      targetElement.classList.add('bg-info', 'text-info-content');
      const fileName = filePath.split('/').pop();
      editorStatus.textContent = `Selected "${fileName}" for compare - right-click another file to compare`;
    }
  }

  async function compareFiles(file1Path, file2Path){
    const { fetchJSON, languageFor, getDiffStats } = _getUtils();
    const currentExplorer = _getCurrentExplorer();
    const sel = window.AppSelection ? window.AppSelection.get() : {project:'', subproject:''};

    try {
      let url1, url2;
      if(currentExplorer.mode === 'global') {
        url1 = `/api/explorer/global/file?root=${encodeURIComponent(currentExplorer.globalRoot)}&path=${encodeURIComponent(file1Path)}`;
        url2 = `/api/explorer/global/file?root=${encodeURIComponent(currentExplorer.globalRoot)}&path=${encodeURIComponent(file2Path)}`;
      } else {
        url1 = `/api/explorer/${sel.project}/${sel.subproject}/file?path=${encodeURIComponent(file1Path)}`;
        url2 = `/api/explorer/${sel.project}/${sel.subproject}/file?path=${encodeURIComponent(file2Path)}`;
      }
      const [data1, data2] = await Promise.all([fetchJSON(url1), fetchJSON(url2)]);

      const file1 = { path:file1Path, name:file1Path.split('/').pop(), content:data1.content||'', language:languageFor(file1Path) };
      const file2 = { path:file2Path, name:file2Path.split('/').pop(), content:data2.content||'', language:languageFor(file2Path) };

      currentExplorer.compareSelection = null;
      document.querySelectorAll('.tree-item').forEach(el => { el.classList.remove('bg-info','text-info-content'); });

      currentExplorer.compareFiles = [file1, file2];
      await loadDiffView();

      const exitCompareBtn = document.getElementById('exitCompareBtn');
      const saveFileBtn = document.getElementById('saveFileBtn');
      const compareStatusBar = document.getElementById('compareStatusBar');
      const compareFileInfo = document.getElementById('compareFileInfo');
      exitCompareBtn.style.display = 'inline-flex';
      saveFileBtn.style.display = 'none';
      compareStatusBar.style.display = 'block';
      compareFileInfo.textContent = `Comparing: ${file1.name} ↔ ${file2.name}`;
    } catch(err) {
      console.error(err);
      alert(`Error loading files for comparison: ${err.message}`);
    }
  }

  function exitCompareMode(){
    const currentExplorer = _getCurrentExplorer();
    const { getMonacoLoaded, getMonacoEditor, setMonacoEditor, getMonacoDiffEditor, setMonacoDiffEditor } = _getEditor();
    const editorStatus = document.getElementById('editorStatus');
    const editorFilename = document.getElementById('editorFilename');
    const exitCompareBtn = document.getElementById('exitCompareBtn');
    const saveFileBtn = document.getElementById('saveFileBtn');
    const compareStatusBar = document.getElementById('compareStatusBar');

    currentExplorer.compareMode = false;
    currentExplorer.compareFiles = [];

    let monacoDiffEditor = getMonacoDiffEditor ? getMonacoDiffEditor() : window.monacoDiffEditor;
    if(monacoDiffEditor){
      monacoDiffEditor.dispose();
      setMonacoDiffEditor && setMonacoDiffEditor(null);
      if(window.monacoDiffEditor) window.monacoDiffEditor = null;
    }

    const editorContainer = document.getElementById('fileEditorMonaco');
    editorContainer.innerHTML = '';

    const monacoLoaded = getMonacoLoaded ? getMonacoLoaded() : window.monacoLoaded;
    if(monacoLoaded){
      const theme = (document.documentElement.getAttribute('data-theme')||'').includes('dark') ? 'vs-dark':'vs';
      const monacoEditor = monaco.editor.create(editorContainer, {
        value:'', language:'plaintext', theme, automaticLayout:true, fontSize:12, minimap:{enabled:false}, scrollBeyondLastLine:false
      });
      monacoEditor.onDidChangeModelContent(()=>{
        if(!currentExplorer.selectedFile) return;
        currentExplorer.dirty = true;
        saveFileBtn.disabled = false;
        editorStatus.textContent = 'Modified';
      });
      setMonacoEditor && setMonacoEditor(monacoEditor);
      window.monacoEditor = monacoEditor; // fallback
    }

    exitCompareBtn.style.display = 'none';
    saveFileBtn.style.display = 'inline-flex';
    compareStatusBar.style.display = 'none';

    document.querySelectorAll('.tree-item').forEach(el => {
      el.classList.remove('bg-info','text-info-content','bg-warning','text-warning-content');
    });

    editorStatus.textContent = 'Compare mode exited';
    editorFilename.textContent = '(no file selected)';
    const editorFullPath = document.getElementById('editorFullPath');
    if(editorFullPath) editorFullPath.textContent = '';
  }

  async function loadDiffView(){
    const { getDiffStats } = _getUtils();
    const currentExplorer = _getCurrentExplorer();
    const { getMonacoLoaded, getMonacoEditor, setMonacoEditor, getMonacoDiffEditor, setMonacoDiffEditor } = _getEditor();

    const monacoLoaded = getMonacoLoaded ? getMonacoLoaded() : window.monacoLoaded;
    if(!monacoLoaded || currentExplorer.compareFiles.length !== 2) return;

    let monacoEditor = getMonacoEditor ? getMonacoEditor() : window.monacoEditor;
    if(monacoEditor){
      monacoEditor.dispose();
      setMonacoEditor && setMonacoEditor(null);
      window.monacoEditor = null;
    }

    const theme = (document.documentElement.getAttribute('data-theme')||'').includes('dark') ? 'vs-dark':'vs';
    const editorContainer = document.getElementById('fileEditorMonaco');
    editorContainer.innerHTML = '';

    const [file1, file2] = currentExplorer.compareFiles;
    const monacoDiffEditor = monaco.editor.createDiffEditor(editorContainer, {
      theme, automaticLayout:true, fontSize:12, renderSideBySide:true, readOnly:true, minimap:{enabled:false}, scrollBeyondLastLine:false, originalEditable:false, enableSplitViewResizing:true
    });
    const originalModel = monaco.editor.createModel(file1.content, file1.language);
    const modifiedModel = monaco.editor.createModel(file2.content, file2.language);
    monacoDiffEditor.setModel({ original: originalModel, modified: modifiedModel });
    setMonacoDiffEditor && setMonacoDiffEditor(monacoDiffEditor);
    window.monacoDiffEditor = monacoDiffEditor;

    const editorFilename = document.getElementById('editorFilename');
    const editorFullPath = document.getElementById('editorFullPath');
    const editorStatus = document.getElementById('editorStatus');

    editorFilename.textContent = `${file1.name} ↔ ${file2.name}`;
    const fullPath1 = typeof getFullAbsolutePath === 'function' ? getFullAbsolutePath(file1.path) : file1.path;
    const fullPath2 = typeof getFullAbsolutePath === 'function' ? getFullAbsolutePath(file2.path) : file2.path;
    if(editorFullPath){
      editorFullPath.textContent = `${fullPath1} ⟷ ${fullPath2}`;
      editorFullPath.title = `Original: ${fullPath1}\nModified: ${fullPath2}`;
    }
    editorStatus.textContent = getDiffStats ? getDiffStats(file1.content, file2.content) : '';
  }

  // Expose API
  Explorer.compare.handleCompareSelection = handleCompareSelection;
  Explorer.compare.compareFiles = compareFiles;
  Explorer.compare.exitCompareMode = exitCompareMode;
  Explorer.compare.loadDiffView = loadDiffView;
})();