/**
 * menu.js - Context menu management for Explorer
 * Handles right-click context menu display and actions
 */

(function() {
  'use strict';

  // Ensure Explorer namespace exists
  window.Explorer = window.Explorer || {};

  // Import dependencies from other modules
  const { copyToClipboard } = Explorer.utils;
  const { currentExplorer } = Explorer.state;

  /**
   * Show context menu at specified position
   * @param {number} x - X coordinate
   * @param {number} y - Y coordinate
   * @param {HTMLElement} target - Target element that was right-clicked
   * @param {boolean} isFile - Whether target is a file (vs folder)
   * @param {string} filePath - Path to the file/folder
   */
  function showContextMenu(x, y, target, isFile, filePath) {
    const contextMenu = document.getElementById('contextMenu');
    const compareSelectedText = document.getElementById('compareSelectedText');
    const compareWithText = document.getElementById('compareWithText');
    
    if (!contextMenu) return;
    
    currentExplorer.contextMenuTarget = { target, isFile, filePath };
    
    // Update menu items based on context
    const openItem = contextMenu.querySelector('[data-action="open"]');
    const newFileItem = contextMenu.querySelector('[data-action="new-file"]');
    const compareWithItem = contextMenu.querySelector('[data-action="compare-with"]');
    const compareSelectedItem = contextMenu.querySelector('[data-action="compare-selected"]');
    
    if (isFile) {
      if (openItem) openItem.classList.remove('disabled');
      if (newFileItem) newFileItem.querySelector('span').textContent = 'New File in Parent Folder...';
      if (compareWithItem) compareWithItem.classList.remove('disabled');
      
      // Show "Compare with Selected" if we have a selection
      if (currentExplorer.compareSelection && currentExplorer.compareSelection !== filePath) {
        if (compareSelectedItem) {
          compareSelectedItem.style.display = 'flex';
          compareSelectedItem.classList.remove('disabled');
        }
        const selectedFileName = currentExplorer.compareSelection.split('/').pop();
        if (compareSelectedText) {
          compareSelectedText.textContent = `Compare with "${selectedFileName}"`;
        }
      } else {
        if (compareSelectedItem) compareSelectedItem.style.display = 'none';
      }
      
      // Update compare text based on selection state
      if (compareWithText) {
        if (currentExplorer.compareSelection === filePath) {
          compareWithText.textContent = '✓ Selected for Compare';
        } else {
          compareWithText.textContent = 'Select for Compare';
        }
      }
    } else {
      // Folder context
      if (openItem) openItem.classList.add('disabled');
      if (newFileItem) newFileItem.querySelector('span').textContent = 'New File in This Folder...';
      if (compareWithItem) compareWithItem.classList.add('disabled');
      if (compareSelectedItem) compareSelectedItem.style.display = 'none';
    }
    
    // Position the menu
    contextMenu.style.left = `${x}px`;
    contextMenu.style.top = `${y}px`;
    contextMenu.classList.add('show');
    
    // Adjust if menu goes off-screen
    setTimeout(() => {
      const rect = contextMenu.getBoundingClientRect();
      if (rect.right > window.innerWidth) {
        contextMenu.style.left = `${x - rect.width}px`;
      }
      if (rect.bottom > window.innerHeight) {
        contextMenu.style.top = `${y - rect.height}px`;
      }
    }, 0);
  }

  /**
   * Hide the context menu
   */
  function hideContextMenu() {
    const contextMenu = document.getElementById('contextMenu');
    if (contextMenu) {
      contextMenu.classList.remove('show');
    }
    currentExplorer.contextMenuTarget = null;
  }

  /**
   * Initialize context menu by binding click handlers
   */
  function initContextMenu() {
    const contextMenu = document.getElementById('contextMenu');
    if (!contextMenu) return;

    // Context menu actions
    contextMenu.addEventListener('click', async (e) => {
      const item = e.target.closest('.context-menu-item');
      if (!item || item.classList.contains('disabled')) return;
      
      const action = item.getAttribute('data-action');
      const { target, isFile, filePath } = currentExplorer.contextMenuTarget || {};
      
      hideContextMenu();
      
      switch(action) {
        case 'open':
          if (isFile && filePath) {
            // loadFileByPath is from Explorer.editor
            if (Explorer.editor && typeof Explorer.editor.loadFileByPath === 'function') {
              await Explorer.editor.loadFileByPath(filePath);
            }
            // Highlight selected file
            document.querySelectorAll('.tree-item').forEach(el => el.classList.remove('bg-primary', 'text-primary-content'));
            if (target) target.classList.add('bg-primary', 'text-primary-content');
          }
          break;
          
        case 'new-file':
          // handleNewFile is in files.js or template
          if (typeof handleNewFile === 'function') {
            await handleNewFile(filePath, isFile);
          }
          break;
          
        case 'compare-with':
          if (isFile && filePath) {
            // handleCompareSelection is in compare.js or template
            if (typeof handleCompareSelection === 'function') {
              handleCompareSelection(filePath, target);
            }
          }
          break;
          
        case 'compare-selected':
          if (isFile && filePath && currentExplorer.compareSelection) {
            // compareFiles is in compare.js or template
            if (typeof compareFiles === 'function') {
              await compareFiles(currentExplorer.compareSelection, filePath);
            }
          }
          break;
          
        case 'copy-path':
          if (filePath !== undefined) {
            // getFullAbsolutePath is in template
            if (typeof getFullAbsolutePath === 'function') {
              const fullPath = getFullAbsolutePath(filePath);
              await copyToClipboard(fullPath);
            }
          }
          break;
          
        case 'copy-relative-path':
          if (filePath !== undefined) {
            const sel = window.AppSelection ? window.AppSelection.get() : {project:'', subproject:''};
            const relativePath = `${sel.project}/${sel.subproject}/design/timing/${filePath}`;
            await copyToClipboard(relativePath);
          }
          break;
      }
    });

    // Hide context menu on click outside
    document.addEventListener('click', (e) => {
      if (!contextMenu.contains(e.target)) {
        hideContextMenu();
      }
    });
  }

  // Export menu module
  Explorer.menu = {
    showContextMenu,
    hideContextMenu,
    init: initContextMenu
  };

})();
