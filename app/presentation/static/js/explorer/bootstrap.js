/**
 * bootstrap.js
 * Final orchestration module - queries DOM elements once and initializes all Explorer modules in correct order.
 * This replaces the remaining inline script in explorer.html template.
 */

(function() {
  'use strict';

  // ========== DOM ELEMENT REFERENCES ==========
  // Query all DOM elements once and expose via Explorer.dom for shared access
  Explorer.dom = {
    explorerTree: document.getElementById('explorerTree'),
    collapseAllBtn: document.getElementById('collapseAllBtn'),
    refreshBtn: document.getElementById('refreshBtn'),
    editorFilename: document.getElementById('editorFilename'),
    editorFullPath: document.getElementById('editorFullPath'),
    copyPathBtn: document.getElementById('copyPathBtn'),
    saveFileBtn: document.getElementById('saveFileBtn'),
    editorStatus: document.getElementById('editorStatus'),
    exitCompareBtn: document.getElementById('exitCompareBtn'),
    compareStatusBar: document.getElementById('compareStatusBar'),
    compareFileInfo: document.getElementById('compareFileInfo'),
    contextMenu: document.getElementById('contextMenu'),
    compareWithText: document.getElementById('compareWithText'),
    compareSelectedText: document.getElementById('compareSelectedText'),
    resizeHandle: document.getElementById('resizeHandle'),
    treeWrapper: document.querySelector('.explorer-tree-wrapper'),
    editorWrapper: document.querySelector('.explorer-editor-wrapper')
  };

  // ========== HELPER FUNCTIONS ==========
  // Destructure commonly used utilities for brevity
  const { copyToClipboard } = Explorer.utils;
  const currentExplorer = Explorer.state.currentExplorer;

  /**
   * Get full absolute path from relative path based on current mode
   */
  function getFullAbsolutePath(relativePath) {
    // Global mode: concatenate directly to provided root
    if(currentExplorer.mode === 'global') {
      if(!relativePath) return currentExplorer.globalRoot;
      const sep = currentExplorer.globalRoot.includes('\\') ? '\\' : '/';
      return `${currentExplorer.globalRoot}${sep}${relativePath.replace(/\//g, sep)}`;
    }
    // Project timing root mode
    const sel = window.AppSelection ? window.AppSelection.get() : {project:'', subproject:''};
    if (currentExplorer.basePathFromBackend) {
      const separator = currentExplorer.basePathFromBackend.includes('\\') ? '\\' : '/';
      if (relativePath) {
        const normalizedRelative = relativePath.replace(/\//g, separator);
        return `${currentExplorer.basePathFromBackend}${separator}tb${separator}${sel.project}${separator}${sel.subproject}${separator}design${separator}timing${separator}${normalizedRelative}`;
      }
      return `${currentExplorer.basePathFromBackend}${separator}tb${separator}${sel.project}${separator}${sel.subproject}${separator}design${separator}timing`;
    }
    if (relativePath) return `{BASE}/tb/${sel.project}/${sel.subproject}/design/timing/${relativePath}`;
    return `{BASE}/tb/${sel.project}/${sel.subproject}/design/timing`;
  }

  /**
   * Display folder information in the editor area
   */
  function showFolderInfo(folderPath) {
    const sel = window.AppSelection ? window.AppSelection.get() : {project:'', subproject:''};
    const folderName = folderPath.split('/').pop() || 'design/timing';
    const fullPath = getFullAbsolutePath(folderPath);
    
    Explorer.dom.editorFilename.textContent = `📁 ${folderName || 'Root'}`;
    Explorer.dom.editorFullPath.textContent = fullPath;
    Explorer.dom.editorFullPath.title = fullPath;
    Explorer.dom.copyPathBtn.style.display = 'block';
    
    // Clear editor and show folder info
    currentExplorer.selectedFile = null;
    currentExplorer.selectedFilePath = null;
    currentExplorer.fullPath = fullPath;
    currentExplorer.dirty = false;
    Explorer.dom.saveFileBtn.disabled = true;
    Explorer.dom.editorStatus.textContent = 'Folder selected';
    
    if(Explorer.editor.monacoLoaded && Explorer.editor.monacoEditor) {
      const folderInfo = `# Folder: ${folderName || 'Root'}\n\nPath: ${fullPath}\n\nThis is a directory. Click on a file to view its contents.`;
      const model = monaco.editor.createModel(folderInfo, 'markdown');
      Explorer.editor.monacoEditor.setModel(model);
      Explorer.editor.monacoEditor.updateOptions({readOnly: true});
    }
  }

  // Expose helper functions that may be needed by other modules
  Explorer.helpers = {
    getFullAbsolutePath,
    showFolderInfo
  };

  // ========== EVENT HANDLERS ==========

  /**
   * Handle copy path button click
   */
  async function handleCopyPath() {
    if(!currentExplorer.fullPath) return;
    
    try {
      await navigator.clipboard.writeText(currentExplorer.fullPath);
      const originalHTML = Explorer.dom.copyPathBtn.innerHTML;
      Explorer.dom.copyPathBtn.innerHTML = `<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
      </svg>`;
      Explorer.dom.copyPathBtn.classList.add('btn-success');
      
      setTimeout(() => {
        Explorer.dom.copyPathBtn.innerHTML = originalHTML;
        Explorer.dom.copyPathBtn.classList.remove('btn-success');
      }, 1500);
    } catch(err) {
      console.error('Failed to copy:', err);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = currentExplorer.fullPath;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      document.body.appendChild(textArea);
      textArea.select();
      try {
        document.execCommand('copy');
        const originalHTML = Explorer.dom.copyPathBtn.innerHTML;
        Explorer.dom.copyPathBtn.innerHTML = `<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
        </svg>`;
        Explorer.dom.copyPathBtn.classList.add('btn-success');
        setTimeout(() => {
          Explorer.dom.copyPathBtn.innerHTML = originalHTML;
          Explorer.dom.copyPathBtn.classList.remove('btn-success');
        }, 1500);
      } catch(err2) {
        console.error('Fallback copy failed:', err2);
      }
      document.body.removeChild(textArea);
    }
  }

  /**
   * Handle collapse all folders button click
   */
  function handleCollapseAll() {
    Explorer.tree.collapseAllFolders();
  }

  /**
   * Handle refresh button click
   */
  async function handleRefresh() {
    await Explorer.tree.refreshFileTree();
  }

  /**
   * Handle exit compare mode button click
   */
  function handleExitCompare() {
    Explorer.compare.exitCompareMode();
  }

  /**
   * Prevent default context menu on tree
   */
  function preventTreeContextMenu(e) {
    e.preventDefault();
  }

  // ========== INITIALIZATION ==========

  /**
   * Attach all event listeners to DOM elements
   */
  function attachEventListeners() {
    // Button event listeners
    Explorer.dom.collapseAllBtn.addEventListener('click', handleCollapseAll);
    Explorer.dom.refreshBtn.addEventListener('click', handleRefresh);
    Explorer.dom.copyPathBtn.addEventListener('click', handleCopyPath);
    Explorer.dom.exitCompareBtn.addEventListener('click', handleExitCompare);
    
    // Prevent default context menu on tree
    Explorer.dom.explorerTree.addEventListener('contextmenu', preventTreeContextMenu);
  }

  /**
   * Initialize all Explorer modules in correct order
   */
  function init() {
    console.log('🚀 Initializing Explorer...');
    
    // 1. Config already loaded (config.js)
    // 2. Utils already loaded (utils.js)
    // 3. State already loaded (state.js)
    
    // 4. Initialize panel resize
    Explorer.resize.init();
    console.log('✓ Panel resize initialized');
    
    // 5. Editor module will auto-initialize Monaco when loaded (editor.js handles its own init)
    console.log('✓ Editor module loaded');
    
    // 6. Initialize context menu
    Explorer.menu.init();
    console.log('✓ Context menu initialized');
    
    // 7. Initialize file operations
    Explorer.files.init();
    console.log('✓ File operations initialized');
    
    // 8. Initialize mode handling and check URL parameters
    Explorer.mode.init();
    console.log('✓ Mode handling initialized');
    
    // 9. Initialize file tree (this will load the initial tree structure)
    Explorer.tree.initializeTree();
    console.log('✓ File tree initialized');
    
    // 10. Attach remaining event listeners
    attachEventListeners();
    console.log('✓ Event listeners attached');
    
    console.log('✅ Explorer fully initialized and ready');
  }

  // ========== GLOBAL BRIDGES FOR BACKWARD COMPATIBILITY ==========
  // Expose commonly used references to window for any legacy inline code
  window.monacoEditor = Explorer.editor.monacoEditor;
  window.monacoDiffEditor = Explorer.editor.monacoDiffEditor;
  window.monacoLoaded = Explorer.editor.monacoLoaded;
  
  // Make key functions globally accessible if needed by inline scripts
  window.showFolderInfo = showFolderInfo;
  window.getFullAbsolutePath = getFullAbsolutePath;

  // ========== START BOOTSTRAP ==========
  // Run initialization when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    // DOM already loaded
    init();
  }

})();
