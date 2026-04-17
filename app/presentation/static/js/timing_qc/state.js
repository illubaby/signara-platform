// Timing QC: State Management
// This module manages application state, localStorage persistence, and tab filtering

(function(global){
  'use strict';

  // Verify dependencies
  if(!global.QCSharedHttp){
    console.error('[Timing QC] state.js requires shared_http.js');
    return;
  }

  // LocalStorage keys
  const STORAGE_KEY_CELL = 'qc_last_cell';
  const STORAGE_KEY_PROJECT = 'qc_last_project';
  const STORAGE_KEY_SUBPROJECT = 'qc_last_subproject';
  const STORAGE_KEY_TAB = 'qc_last_tab';

  // Application state
  const state = {
    delay: [],                              // Array of testbench objects
    selectedIndex: null,                    // Currently selected row index
    loadedCell: null,                       // Currently loaded cell name
    statusPoll: null,                       // setTimeout ID for polling
    importantNumbers: new Set(),            // Set of important arc numbers
    currentTab: localStorage.getItem(STORAGE_KEY_TAB) || 'important',  // Current tab
    runningWS: null,                        // WebSocket connection
    runningProc: null                       // Process reference (unused)
  };

  // ------------------ Selection State ------------------
  /**
   * Get current project/subproject selection from global AppSelection
   * @returns {object} - {project: '', subproject: ''}
   */
  function getSelectionState(){
    return global.AppSelection ? global.AppSelection.get() : {project: '', subproject: ''};
  }

  // ------------------ State Access ------------------
  function getState(){
    return state;
  }

  function getDelays(){
    return state.delay;
  }

  function setDelays(delays){
    state.delay = delays;
  }

  function addTestbench(testbench){
    state.delay.push(testbench);
  }

  function updateTestbenchStatus(testbenchName, status, pvtDetails){
    const row = state.delay.find(r => r.testbench === testbenchName);
    if(row){
      row.status = status;
      if(pvtDetails){
        row._pvtDetails = pvtDetails;
      }
    }
  }

  // ------------------ Selection Management ------------------
  function getSelectedIndex(){
    return state.selectedIndex;
  }

  function setSelectedIndex(index){
    state.selectedIndex = index;
  }

  function getSelectedTestbench(){
    const filtered = getFilteredTestbenches();
    if(state.selectedIndex !== null && state.selectedIndex >= 0 && state.selectedIndex < filtered.length){
      return filtered[state.selectedIndex];
    }
    return null;
  }

  // ------------------ Tab Management ------------------
  function getCurrentTab(){
    return state.currentTab;
  }

  function setCurrentTab(tab){
    state.currentTab = tab;
  }

  // ------------------ Important Numbers ------------------
  function getImportantNumbers(){
    return state.importantNumbers;
  }

  function setImportantNumbers(numbers){
    state.importantNumbers = new Set(numbers);
  }

  /**
   * Extract testbench number from name (e.g., "testbench_123_xxx" -> 123)
   * @param {string} tbName - Testbench name
   * @returns {number|null} - Extracted number or null
   */
  function extractTestbenchNumber(tbName){
    const match = tbName.match(/testbench_(\d+)_/);
    return match ? parseInt(match[1]) : null;
  }

  /**
   * Check if testbench is marked as important
   * @param {string} tbName - Testbench name
   * @returns {boolean} - True if important
   */
  function isImportantTestbench(tbName){
    const num = extractTestbenchNumber(tbName);
    return num !== null && state.importantNumbers.has(num);
  }

  // ------------------ Filtering ------------------
  /**
   * Get testbenches filtered by current tab
   * @returns {Array} - Filtered testbench array
   */
  function getFilteredTestbenches(){
    if(state.currentTab === 'important'){
      return state.delay.filter(r => isImportantTestbench(r.testbench));
    }

    if(state.currentTab === 'non-important'){
      return state.delay.filter(r => !isImportantTestbench(r.testbench));
    }

    // Equalizer (or unknown tabs) should not reuse non-important rows.
    return [];
  }

  // ------------------ Persistence ------------------
  /**
   * Save last selection to localStorage
   * @param {string} project - Project name
   * @param {string} subproject - Subproject name
   * @param {string} cell - Cell name
   */
  function saveLastSelection(project, subproject, cell){
    try {
      localStorage.setItem(STORAGE_KEY_PROJECT, project);
      localStorage.setItem(STORAGE_KEY_SUBPROJECT, subproject);
      localStorage.setItem(STORAGE_KEY_CELL, cell);
    } catch(e){
      console.warn('[Timing QC] localStorage error:', e);
    }
  }

  /**
   * Get last selection from localStorage
   * @returns {object} - {project: '', subproject: '', cell: ''}
   */
  function getLastSelection(){
    try {
      return {
        project: localStorage.getItem(STORAGE_KEY_PROJECT) || '',
        subproject: localStorage.getItem(STORAGE_KEY_SUBPROJECT) || '',
        cell: localStorage.getItem(STORAGE_KEY_CELL) || ''
      };
    } catch(e){
      return {project: '', subproject: '', cell: ''};
    }
  }

  /**
   * Save last tab selection
   * @param {string} tab - 'important' or 'non-important'
   */
  function saveLastTab(tab){
    try {
      localStorage.setItem(STORAGE_KEY_TAB, tab);
    } catch(e){
      console.warn('[Timing QC] localStorage error:', e);
    }
  }

  // ------------------ WebSocket Tracking ------------------
  function getRunningWS(){
    return state.runningWS;
  }

  function setRunningWS(ws){
    state.runningWS = ws;
  }

  // ------------------ Polling Management ------------------
  function getStatusPoll(){
    return state.statusPoll;
  }

  function setStatusPoll(pollId){
    state.statusPoll = pollId;
  }

  function clearStatusPoll(){
    if(state.statusPoll){
      clearTimeout(state.statusPoll);
      state.statusPoll = null;
    }
  }

  function getLoadedCell(){
    return state.loadedCell;
  }

  function setLoadedCell(cell){
    state.loadedCell = cell;
  }

  // ------------------ Export to Global Scope ------------------
  global.QCState = {
    getState,
    getSelectionState,
    
    // Delay data
    getDelays,
    setDelays,
    addTestbench,
    updateTestbenchStatus,
    
    // Selection
    getSelectedIndex,
    setSelectedIndex,
    getSelectedTestbench,
    
    // Tab
    getCurrentTab,
    setCurrentTab,
    
    // Important numbers
    getImportantNumbers,
    setImportantNumbers,
    isImportantTestbench,
    extractTestbenchNumber,
    
    // Filtering
    getFilteredTestbenches,
    
    // Persistence
    saveLastSelection,
    getLastSelection,
    saveLastTab,
    
    // WebSocket
    getRunningWS,
    setRunningWS,
    
    // Polling
    getStatusPoll,
    setStatusPoll,
    clearStatusPoll,
    
    // Cell
    getLoadedCell,
    setLoadedCell
  };

  console.log('[Timing QC] state.js loaded');

})(window);
