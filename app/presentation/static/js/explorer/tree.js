/**
 * tree.js - Directory tree management for Explorer
 * Handles loading, displaying, expanding/collapsing the file tree
 */

(function() {
  'use strict';

  // Ensure Explorer namespace exists
  window.Explorer = window.Explorer || {};

  // Import dependencies from other modules
  const { fetchJSON, shouldIgnoreEntry, getFileIcon } = Explorer.utils;
  const { currentExplorer } = Explorer.state;

  /**
   * Load directory contents from backend API
   * @param {string} relativePath - Path relative to root
   * @returns {Promise<Object|null>} Directory data or null on error
   */
  async function loadDirectoryContents(relativePath) {
    const sel = window.AppSelection ? window.AppSelection.get() : {project:'', subproject:''};
    if (currentExplorer.mode === 'project' && (!sel.project || !sel.subproject)) return null;
    if (currentExplorer.mode === 'global' && !currentExplorer.globalRoot) return null;
    
    const cacheKey = `${currentExplorer.mode}:${currentExplorer.mode==='global'?currentExplorer.globalRoot:''}:${relativePath||''}`;
    if(currentExplorer.treeCache.has(cacheKey)) return currentExplorer.treeCache.get(cacheKey);
    
    try {
      let url;
      if(currentExplorer.mode === 'global') {
        url = `/api/explorer/global?root=${encodeURIComponent(currentExplorer.globalRoot)}&path=${encodeURIComponent(relativePath||'')}`;
      } else {
        url = `/api/explorer/${sel.project}/${sel.subproject}?path=${encodeURIComponent(relativePath||'')}`;
      }
      const data = await fetchJSON(url);
      if (data.base_path && !currentExplorer.basePathFromBackend) {
        currentExplorer.basePathFromBackend = data.base_path;
      }
      currentExplorer.treeCache.set(cacheKey, data);
      return data;
    } catch(err) {
      console.error(err);
      return null;
    }
  }

  /**
   * Create HTML for a tree node (file or folder)
   * @param {Object} entry - Entry object with name, is_dir properties
   * @param {string} path - Parent path
   * @param {number} level - Nesting level for indentation
   * @returns {string} HTML string
   */
  function createTreeNode(entry, path, level = 0) {
    const fullPath = path ? `${path}/${entry.name}` : entry.name;
    const indent = level * 16;
    
    if(entry.is_dir) {
      const nodeId = `tree-${fullPath.replace(/[^a-zA-Z0-9]/g, '-')}`;
      return `
        <div class="tree-folder" data-path="${fullPath}" data-level="${level}">
          <div class="tree-item px-2 py-1 hover:bg-base-200 rounded cursor-pointer flex items-center gap-1" style="padding-left: ${indent + 8}px" data-folder-toggle="${nodeId}" title="${entry.name}">
            <svg class="w-3 h-3 chevron transition-transform flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
            <span class="flex-shrink-0">📁</span>
            <span class="text-xs">${entry.name}</span>
          </div>
          <div class="tree-children hidden" id="${nodeId}"></div>
        </div>`;
    } else {
      const icon = getFileIcon(entry.name);
      return `
        <div class="tree-file" data-path="${fullPath}" data-level="${level}">
          <div class="tree-item px-2 py-1 hover:bg-base-200 rounded cursor-pointer flex items-center gap-1" style="padding-left: ${indent + 8}px" data-file="${fullPath}" title="${entry.name}">
            <span class="w-3 flex-shrink-0"></span>
            <span class="flex-shrink-0">${icon}</span>
            <span class="text-xs">${entry.name}</span>
          </div>
        </div>`;
    }
  }

  /**
   * Expand or collapse a folder in the tree
   * @param {string} folderPath - Path to the folder
   * @param {number} level - Nesting level
   */
  async function expandFolder(folderPath, level) {
    const nodeId = `tree-${folderPath.replace(/[^a-zA-Z0-9]/g, '-')}`;
    const container = document.getElementById(nodeId);
    const toggle = document.querySelector(`[data-folder-toggle="${nodeId}"]`);
    
    if(!container || !toggle) return;
    
    const chevron = toggle.querySelector('.chevron');
    
    // If already expanded, collapse it
    if(!container.classList.contains('hidden')) {
      container.classList.add('hidden');
      chevron.style.transform = 'rotate(0deg)';
      return;
    }
    
    // Show loading state
    container.innerHTML = '<div class="text-xs opacity-60 px-2 py-1" style="padding-left: ' + ((level + 1) * 16 + 8) + 'px">Loading...</div>';
    container.classList.remove('hidden');
    chevron.style.transform = 'rotate(90deg)';
    
    // Load contents
    const data = await loadDirectoryContents(folderPath);
    
    if(!data || !data.entries || data.entries.length === 0) {
      container.innerHTML = '<div class="text-xs opacity-60 px-2 py-1" style="padding-left: ' + ((level + 1) * 16 + 8) + 'px">(empty)</div>';
      return;
    }
    
    // Filter out ignored entries
    const filtered = data.entries.filter(entry => !shouldIgnoreEntry(entry.name));
    
    if(filtered.length === 0) {
      container.innerHTML = '<div class="text-xs opacity-60 px-2 py-1" style="padding-left: ' + ((level + 1) * 16 + 8) + 'px">(empty)</div>';
      return;
    }
    
    // Sort: folders first, then files, alphabetically
    const sorted = filtered.sort((a, b) => {
      if(a.is_dir !== b.is_dir) return a.is_dir ? -1 : 1;
      return a.name.localeCompare(b.name);
    });
    
    let html = '';
    sorted.forEach(entry => {
      html += createTreeNode(entry, folderPath, level + 1);
    });
    
    container.innerHTML = html;
    attachTreeEventListeners(container);
  }

  /**
   * Attach click and context menu event listeners to tree elements
   * @param {HTMLElement} container - Container element to attach listeners to
   */
  function attachTreeEventListeners(container) {
    // Note: showFolderInfo, handleCompareFileSelection, loadFileByPath, and showContextMenu
    // are referenced here but defined elsewhere. They're accessed from global scope.
    
    // Folder toggles
    container.querySelectorAll('[data-folder-toggle]').forEach(toggle => {
      toggle.addEventListener('click', async (e) => {
        e.stopPropagation();
        const folderElement = toggle.closest('.tree-folder');
        const folderPath = folderElement.getAttribute('data-path');
        const level = parseInt(folderElement.getAttribute('data-level'));
        
        // Show folder path in the editor info area
        if (typeof showFolderInfo === 'function') {
          showFolderInfo(folderPath);
        }
        
        // Highlight selected folder
        document.querySelectorAll('.tree-item').forEach(el => el.classList.remove('bg-primary', 'text-primary-content'));
        toggle.classList.add('bg-primary', 'text-primary-content');
        
        await expandFolder(folderPath, level);
      });
      
      // Right-click on folder
      toggle.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const folderElement = toggle.closest('.tree-folder');
        const folderPath = folderElement.getAttribute('data-path');
        if (typeof showContextMenu === 'function') {
          showContextMenu(e.pageX, e.pageY, toggle, false, folderPath);
        }
      });
    });
    
    // File clicks
    container.querySelectorAll('[data-file]').forEach(fileEl => {
      fileEl.addEventListener('click', (e) => {
        e.stopPropagation();
        const filePath = fileEl.getAttribute('data-file');
        
        if(currentExplorer.compareMode) {
          // In compare mode, collect files for comparison
          if (typeof handleCompareSelection === 'function') {
            handleCompareSelection(filePath, fileEl);
          }
        } else {
          // Normal mode: load the file
          if (Explorer.editor && typeof Explorer.editor.loadFileByPath === 'function') {
            Explorer.editor.loadFileByPath(filePath);
          }
          
          // Highlight selected file
          document.querySelectorAll('.tree-item').forEach(el => el.classList.remove('bg-primary', 'text-primary-content'));
          fileEl.classList.add('bg-primary', 'text-primary-content');
        }
      });
      
      // Right-click on file
      fileEl.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const filePath = fileEl.getAttribute('data-file');
        if (typeof showContextMenu === 'function') {
          showContextMenu(e.pageX, e.pageY, fileEl, true, filePath);
        }
      });
    });
  }

  /**
   * Initialize the tree view with root contents
   */
  async function initializeTree() {
    const explorerTree = document.getElementById('explorerTree');
    if (!explorerTree) return;
    
    const sel = window.AppSelection ? window.AppSelection.get() : {project:'', subproject:''};
    if(currentExplorer.mode === 'project' && (!sel.project || !sel.subproject)) {
      explorerTree.innerHTML = '<div class="text-sm opacity-70 text-center py-4">Select a project or switch to Global mode</div>';
      return;
    }
    if(currentExplorer.mode === 'global' && !currentExplorer.globalRoot) {
      explorerTree.innerHTML = '<div class="text-sm opacity-70 text-center py-4">Enter an absolute path above and click Set Root</div>';
      return;
    }
    explorerTree.innerHTML = '<div class="text-sm opacity-70 text-center py-4">Loading...</div>';
    const data = await loadDirectoryContents('');
    if(!data || !data.entries) {
      explorerTree.innerHTML = '<div class="text-sm opacity-70 text-center py-4">Empty directory</div>';
      return;
    }
    const filtered = data.entries.filter(entry => !shouldIgnoreEntry(entry.name));
    if(filtered.length === 0) {
      explorerTree.innerHTML = '<div class="text-sm opacity-70 text-center py-4">No files to display (all filtered)</div>';
      return;
    }
    const sorted = filtered.sort((a,b)=>{
      if(a.is_dir !== b.is_dir) return a.is_dir ? -1 : 1;
      return a.name.localeCompare(b.name);
    });
    const rootLabel = currentExplorer.mode === 'global' ? currentExplorer.globalRoot : 'design/timing';
    let html = `<div class="mb-2 text-xs font-bold opacity-70">${rootLabel}</div>`;
    sorted.forEach(entry => html += createTreeNode(entry, '', 0));
    explorerTree.innerHTML = html;
    attachTreeEventListeners(explorerTree);
  }

  /**
   * Collapse all expanded folders in the tree
   */
  function collapseAllFolders() {
    document.querySelectorAll('.tree-children').forEach(container => {
      container.classList.add('hidden');
    });
    document.querySelectorAll('.chevron').forEach(chevron => {
      chevron.style.transform = 'rotate(0deg)';
    });
  }

  /**
   * Refresh the file tree while preserving expanded state and current file
   */
  async function refreshFileTree() {
    const editorStatus = document.getElementById('editorStatus');
    const exitCompareBtn = document.getElementById('exitCompareBtn');
    const saveFileBtn = document.getElementById('saveFileBtn');
    const compareStatusBar = document.getElementById('compareStatusBar');
    const compareFileInfo = document.getElementById('compareFileInfo');
    
    // Save current state
    const currentFilePath = currentExplorer.selectedFilePath;
    const monacoDiffEditor = Explorer.editor ? Explorer.editor.getMonacoDiffEditor() : null;
    const wasInCompareMode = monacoDiffEditor !== null;
    const compareFiles = [...currentExplorer.compareFiles]; // Clone array
    
    // Save which folders are currently expanded
    const expandedFolders = new Set();
    document.querySelectorAll('.tree-children:not(.hidden)').forEach(container => {
      const folderId = container.id;
      if (folderId && folderId.startsWith('tree-')) {
        // Extract path from ID
        const path = folderId.replace('tree-', '').replace(/-/g, '/');
        expandedFolders.add(path);
      }
    });
    
    // Also get the folder paths from data attributes
    document.querySelectorAll('.tree-folder').forEach(folder => {
      const childrenContainer = folder.querySelector('.tree-children:not(.hidden)');
      if (childrenContainer) {
        const path = folder.getAttribute('data-path');
        if (path) {
          expandedFolders.add(path);
        }
      }
    });
    
    // Show loading state
    if (editorStatus) editorStatus.textContent = 'Refreshing file tree...';
    
    // Clear cache to force reload from server
    currentExplorer.treeCache.clear();
    
    // Reload the tree
    await initializeTree();
    
    // Re-expand previously expanded folders
    for (const folderPath of expandedFolders) {
      const nodeId = `tree-${folderPath.replace(/[^a-zA-Z0-9]/g, '-')}`;
      const toggle = document.querySelector(`[data-folder-toggle="${nodeId}"]`);
      if (toggle) {
        const folderElement = toggle.closest('.tree-folder');
        if (folderElement) {
          const level = parseInt(folderElement.getAttribute('data-level'));
          // Silently expand without animation
          await expandFolder(folderPath, level);
        }
      }
    }
    
    // Restore state
    if (wasInCompareMode && compareFiles.length === 2) {
      // Restore compare mode (loadDiffView is in compare.js or template)
      currentExplorer.compareFiles = compareFiles;
      if (typeof loadDiffView === 'function') {
        await loadDiffView();
      }
      if (exitCompareBtn) exitCompareBtn.style.display = 'inline-flex';
      if (saveFileBtn) saveFileBtn.style.display = 'none';
      if (compareStatusBar) compareStatusBar.style.display = 'block';
      if (compareFileInfo) compareFileInfo.textContent = `Comparing: ${compareFiles[0].name} ↔ ${compareFiles[1].name}`;
      if (editorStatus) editorStatus.textContent = 'Refreshed (compare mode restored)';
    } else if (currentFilePath) {
      // Reload the current file
      try {
        if (Explorer.editor && typeof Explorer.editor.loadFileByPath === 'function') {
          await Explorer.editor.loadFileByPath(currentFilePath);
        }
        
        // Find and highlight the file in tree
        const fileElement = document.querySelector(`[data-file="${currentFilePath}"]`);
        if (fileElement) {
          document.querySelectorAll('.tree-item').forEach(el => el.classList.remove('bg-primary', 'text-primary-content'));
          fileElement.classList.add('bg-primary', 'text-primary-content');
          
          // Scroll into view
          fileElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        
        if (editorStatus) editorStatus.textContent = 'Refreshed ✓';
        setTimeout(() => { 
          if (editorStatus && editorStatus.textContent === 'Refreshed ✓') {
            editorStatus.textContent = ''; 
          }
        }, 2000);
      } catch(err) {
        console.error('Error reloading file:', err);
        if (editorStatus) editorStatus.textContent = 'Refreshed (file reload failed)';
      }
    } else {
      if (editorStatus) editorStatus.textContent = 'Refreshed ✓';
      setTimeout(() => { 
        if (editorStatus && editorStatus.textContent === 'Refreshed ✓') {
          editorStatus.textContent = ''; 
        }
      }, 2000);
    }
  }

  /**
   * Expand tree to show a specific path
   * @param {string} targetPath - Path to expand to
   */
  async function expandToPath(targetPath) {
    const parts = targetPath.split('/').filter(Boolean);
    let currentPath = '';
    let lastToggle = null;
    
    for (const part of parts) {
      currentPath = currentPath ? `${currentPath}/${part}` : part;
      const nodeId = `tree-${currentPath.replace(/[^a-zA-Z0-9]/g, '-')}`;
      const toggle = document.querySelector(`[data-folder-toggle="${nodeId}"]`);
      
      if (toggle) {
        const container = document.getElementById(nodeId);
        // Only expand if not already expanded
        if (container && container.classList.contains('hidden')) {
          const folderPath = toggle.closest('.tree-folder').getAttribute('data-path');
          const level = parseInt(toggle.closest('.tree-folder').getAttribute('data-level'));
          await expandFolder(folderPath, level);
        }
        lastToggle = toggle;
        // Wait a bit for the content to load
        await new Promise(resolve => setTimeout(resolve, 200));
      }
    }
    
    // Scroll to the last expanded folder and highlight it
    if (lastToggle) {
      const treeContainer = document.getElementById('explorerTree');
      const folderElement = lastToggle.closest('.tree-folder');
      
      if (folderElement && treeContainer) {
        // Highlight the opened folder
        lastToggle.classList.add('bg-info', 'text-info-content', 'font-semibold');
        
        // Calculate the position to scroll to
        const containerRect = treeContainer.getBoundingClientRect();
        const elementRect = folderElement.getBoundingClientRect();
        const relativeTop = elementRect.top - containerRect.top;
        
        // Scroll so the element is near the top of the visible area (with some padding)
        treeContainer.scrollTop = treeContainer.scrollTop + relativeTop - 20;
        
        // Add a pulse animation to draw attention
        folderElement.style.animation = 'pulse 0.5s ease-in-out 2';
        
        // Remove highlight after a few seconds
        setTimeout(() => {
          lastToggle.classList.remove('bg-info', 'text-info-content', 'font-semibold');
          folderElement.style.animation = '';
        }, 3000);
      }
    }
  }

  // Export tree module
  Explorer.tree = {
    loadDirectoryContents,
    createTreeNode,
    expandFolder,
    attachTreeEventListeners,
    initializeTree,
    collapseAllFolders,
    refreshFileTree,
    expandToPath
  };

})();
