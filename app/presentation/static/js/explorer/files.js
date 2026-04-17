/**
 * files.js - File creation and saving for Explorer
 * Handles new file creation and file save operations
 */

(function() {
  'use strict';

  // Ensure Explorer namespace exists
  window.Explorer = window.Explorer || {};

  // Import dependencies from other modules
  const { currentExplorer } = Explorer.state;

  /**
   * Handle new file creation from context menu
   * @param {string} contextPath - Path where the new file should be created
   * @param {boolean} isFile - Whether the context is a file (vs folder)
   */
  async function handleNewFile(contextPath, isFile) {
    const sel = window.AppSelection ? window.AppSelection.get() : {project:'', subproject:''};
    if(!sel.project || !sel.subproject) {
      alert('Please select a project first');
      return;
    }
    
    // Determine base path
    let basePath = '';
    if (isFile && contextPath) {
      // Get parent folder of the file
      const parts = contextPath.split('/');
      parts.pop(); // Remove filename
      basePath = parts.join('/');
    } else if (!isFile && contextPath) {
      // Use the folder path
      basePath = contextPath;
    }
    
    // Prompt for filename
    const location = basePath || 'root';
    const filename = prompt(`Enter new filename:\n\nWill be created in: design/timing/${location}`, 'new_file.txt');
    if(!filename || filename.trim() === '') return;
    
    const trimmedFilename = filename.trim();
    const filePath = basePath ? `${basePath}/${trimmedFilename}` : trimmedFilename;
    
    // Set up new file in editor
    currentExplorer.selectedFile = trimmedFilename;
    currentExplorer.selectedFilePath = filePath;
    currentExplorer.isNewFile = true;
    currentExplorer.newFilePath = filePath;
    currentExplorer.dirty = true;
    
    // Update UI elements (accessing from global scope)
    const editorFilename = document.getElementById('editorFilename');
    const editorFullPath = document.getElementById('editorFullPath');
    const copyPathBtn = document.getElementById('copyPathBtn');
    const saveFileBtn = document.getElementById('saveFileBtn');
    const editorStatus = document.getElementById('editorStatus');
    
    // getFullAbsolutePath is in template
    const fullPath = typeof getFullAbsolutePath === 'function' ? getFullAbsolutePath(filePath) : filePath;
    
    if (editorFilename) editorFilename.textContent = `${trimmedFilename} (new)`;
    if (editorFullPath) {
      editorFullPath.textContent = fullPath;
      editorFullPath.title = fullPath;
    }
    if (copyPathBtn) copyPathBtn.style.display = 'block';
    
    // Create empty file in editor (setEditorContent is from Explorer.editor)
    if (Explorer.editor && typeof Explorer.editor.setEditorContent === 'function') {
      Explorer.editor.setEditorContent(trimmedFilename, '# New file\n# Enter your content here\n', false);
    }
    
    if (saveFileBtn) saveFileBtn.disabled = false;
    if (editorStatus) editorStatus.textContent = 'New file (unsaved)';
  }

  /**
   * Save the current file to the backend
   */
  async function saveCurrentFile() {
    if((!currentExplorer.selectedFilePath && !currentExplorer.isNewFile) || !currentExplorer.dirty) return;
    
    const sel = window.AppSelection ? window.AppSelection.get() : {project:'', subproject:''};
    const monacoEditor = Explorer.editor ? Explorer.editor.monacoEditor : null;
    
    if (!monacoEditor) {
      console.error('Monaco editor not available');
      return;
    }
    
    const content = monacoEditor.getValue();
    
    const editorStatus = document.getElementById('editorStatus');
    const saveFileBtn = document.getElementById('saveFileBtn');
    const editorFilename = document.getElementById('editorFilename');
    
    if (editorStatus) editorStatus.textContent = 'Saving...';
    if (saveFileBtn) saveFileBtn.disabled = true;
    
    try {
      const filePath = currentExplorer.isNewFile ? currentExplorer.newFilePath : currentExplorer.selectedFilePath;
      let url;
      let bodyObj;
      
      if(currentExplorer.mode === 'global') {
        url = `/api/explorer/global/file`;
        bodyObj = {root: currentExplorer.globalRoot, path: filePath, content};
      } else {
        url = `/api/explorer/${sel.project}/${sel.subproject}/file`;
        bodyObj = {path: filePath, content};
      }
      
      const res = await fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(bodyObj)
      });
      
      if(!res.ok) throw new Error(await res.text());
      
      currentExplorer.dirty = false;
      currentExplorer.isNewFile = false;
      
      // Update filename display to remove (new) marker
      if(currentExplorer.selectedFile && editorFilename) {
        editorFilename.textContent = currentExplorer.selectedFile;
      }
      
      if (editorStatus) editorStatus.textContent = 'Saved ✓';
      
      // Refresh tree to show new file
      if(currentExplorer.newFilePath) {
        currentExplorer.treeCache.clear();
        if (Explorer.tree && typeof Explorer.tree.initializeTree === 'function') {
          await Explorer.tree.initializeTree();
        }
        currentExplorer.newFilePath = null;
      }
      
      setTimeout(() => { 
        if (editorStatus) editorStatus.textContent = ''; 
      }, 2000);
    } catch(err){
      console.error(err);
      if (editorStatus) editorStatus.textContent = `Error: ${err.message}`;
      if (saveFileBtn) saveFileBtn.disabled = false;
    }
  }

  /**
   * Initialize file operations by binding save button
   */
  function initFileOperations() {
    const saveFileBtn = document.getElementById('saveFileBtn');
    if (saveFileBtn) {
      saveFileBtn.addEventListener('click', async () => {
        await saveCurrentFile();
      });
    }
  }

  // Export files module
  Explorer.files = {
    handleNewFile,
    saveCurrentFile,
    init: initFileOperations
  };

})();
