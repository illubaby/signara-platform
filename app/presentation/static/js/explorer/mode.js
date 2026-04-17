(function(){
  window.Explorer = window.Explorer || {};
  const Explorer = window.Explorer;
  Explorer.mode = Explorer.mode || {};

  function init(){
    const currentExplorer = Explorer.state.currentExplorer;
    const explorerModeSel = document.getElementById('explorerMode');
    const globalRootInput = document.getElementById('globalRootInput');
    const setGlobalRootBtn = document.getElementById('setGlobalRootBtn');

    function checkURLParameters() {
      const urlParams = new URLSearchParams(window.location.search);
      const project = urlParams.get('project');
      const subproject = urlParams.get('subproject');
      const path = urlParams.get('path');

      if (project && subproject && window.AppSelection) {
        window.AppSelection.set(project, subproject);
        Explorer.tree.initializeTree().then(() => {
          if (path) {
            Explorer.tree.expandToPath(path);
          }
        });
      } else {
        Explorer.tree.initializeTree();
      }
    }

    // Listen for app-selection-ready event
    window.addEventListener('app-selection-ready', () => {
      checkURLParameters();
    });

    // Immediate load if selection already exists
    if(window.AppSelection && window.AppSelection.get().project){
      checkURLParameters();
    }

    // Mode switching
    explorerModeSel.addEventListener('change', () => {
      currentExplorer.mode = explorerModeSel.value;
      if(currentExplorer.mode === 'global') {
        globalRootInput.style.display = 'block';
        setGlobalRootBtn.style.display = 'inline-flex';
      } else {
        globalRootInput.style.display = 'none';
        setGlobalRootBtn.style.display = 'none';
      }
      currentExplorer.treeCache.clear();
      Explorer.tree.initializeTree();
    });

    // Set global root logic
    setGlobalRootBtn.addEventListener('click', () => {
      const v = globalRootInput.value.trim();
      if(!v) { alert('Enter an absolute path'); return; }
      currentExplorer.globalRoot = v;
      currentExplorer.treeCache.clear();
      Explorer.tree.initializeTree();
    });

    // Expose for debugging
    Explorer.mode.checkURLParameters = checkURLParameters;
  }

  Explorer.mode.init = init;
})();