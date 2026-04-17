// Explorer resize module: handles left tree panel width persistence & drag
(function(){
  window.Explorer = window.Explorer || {};
  const cfg = Explorer.config;
  const state = Explorer.state.currentExplorer;

  function loadTreeWidth(treeWrapper){
    const savedWidth = localStorage.getItem(cfg.STORAGE_KEY);
    treeWrapper.style.width = savedWidth || '33%';
  }
  function saveTreeWidth(width){ localStorage.setItem(cfg.STORAGE_KEY, width); }

  function init(){
    const treeWrapper = document.querySelector('.explorer-tree-wrapper');
    const resizeHandle = document.getElementById('resizeHandle');
    if(!treeWrapper || !resizeHandle) return;
    loadTreeWidth(treeWrapper);
    let isResizing=false, startX=0, startWidth=0;
    resizeHandle.addEventListener('mousedown', (e)=>{
      isResizing = true;
      startX = e.clientX;
      startWidth = treeWrapper.offsetWidth;
      resizeHandle.classList.add('dragging');
      document.body.style.cursor='col-resize';
      document.body.style.userSelect='none';
      e.preventDefault();
    });
    document.addEventListener('mousemove', (e)=>{
      if(!isResizing) return;
      const deltaX = e.clientX - startX;
      const newWidth = startWidth + deltaX;
      const containerWidth = treeWrapper.parentElement.offsetWidth;
      const minWidth = 200;
      const maxWidth = containerWidth - 300;
      if(newWidth >= minWidth && newWidth <= maxWidth){
        const pct = (newWidth / containerWidth) * 100;
        treeWrapper.style.width = `${pct}%`;
      }
    });
    document.addEventListener('mouseup', ()=>{
      if(!isResizing) return;
      isResizing = false;
      resizeHandle.classList.remove('dragging');
      document.body.style.cursor='';
      document.body.style.userSelect='';
      saveTreeWidth(treeWrapper.style.width);
    });
  }
  Explorer.resize = { init };
})();