/**
 * Hide Cell Feature for Project Status
 * 
 * This module implements the hide cell functionality for the Project Status page.
 * 
 * ## How it works:
 * 
 * 1. **UI Interaction**:
 *    - When in edit mode, each row has a "Hide" button (eye-slash icon) and a "Delete" button
 *    - Clicking "Hide" marks the cell as hidden (dims the row, button turns green)
 *    - Clicking again unhides it (restores opacity, button turns yellow)
 * 
 * 2. **Data Storage**:
 *    - Hidden cells are tracked in the `hiddenCells` Set
 *    - When "Done" is clicked, hidden cells are sent to the backend
 *    - Backend sets `hidden: true` in the project_status.json file in Perforce
 * 
 * 3. **Display Filtering**:
 *    - When loading data, cells with `hidden: true` are filtered out in view mode
 *    - Hidden cells are shown (dimmed) in edit mode so they can be unhidden
 * 
 * 4. **Unhiding Cells**:
 *    - In edit mode, click the green button to unhide a cell
 *    - Changes are saved when clicking "Done"
 * 
 * ## Implementation:
 * - Frontend: This module exports `handleHideCell()` and `hiddenCells` Set
 * - Backend: `/api/project-status/update-pic` endpoint with `hidden` array
 * - Data filtering: `loadProjectStatus()` filters cells with `!isHidden(item)` in view mode
 * 
 * @module hide_cell
 */

// Track cells marked as hidden while in edit mode
const hiddenCells = new Set();

/**
 * Check if a cell item is hidden (handles various value types)
 * @param {Object} item - Cell data object
 * @returns {boolean} - True if cell is hidden
 */
function isHiddenCell(item) {
    const val = item.hidden;
    return val === true || val === 1 || (typeof val === 'string' && val.toLowerCase() === 'true');
}

/**
 * Handle hide/unhide cell button click
 * Toggles the hidden state of a cell and updates UI accordingly
 * 
 * @param {string} cellName - Name of the cell (ckt_macros)
 * @param {HTMLElement} rowEl - Table row element (optional)
 * @param {HTMLElement} buttonEl - Hide button element (optional)
 */
function handleHideCell(cellName, rowEl = null, buttonEl = null) {
    console.log('[handleHideCell] Called for:', cellName);
    
    // Only works in edit mode
    if (!window.editMode) {
        console.log('[handleHideCell] Not in edit mode, ignoring');
        return;
    }
    
    // Get the row and button
    const row = rowEl || document.querySelector(`tr[data-cell="${cellName}"]`);
    const btn = buttonEl || row?.querySelector(`button[data-cell="${cellName}"]`);
    
    // Check if cell is currently marked as hidden
    const isCurrentlyHidden = row?.classList.contains('opacity-30') || hiddenCells.has(cellName);
    console.log(`[handleHideCell] ${cellName}: isCurrentlyHidden=${isCurrentlyHidden}, row has opacity-30=${row?.classList.contains('opacity-30')}, in hiddenCells=${hiddenCells.has(cellName)}`);
    
    // Toggle hide state
    if (isCurrentlyHidden) {
        // Unhide - remove from hiddenCells set
        hiddenCells.delete(cellName);
        // Also mark for unhiding if it was previously hidden in backend
        if (!window.editedCells[cellName]) window.editedCells[cellName] = {};
        window.editedCells[cellName]['hidden'] = false;
        console.log('[Hide Cell] ✅ UNHIDING:', cellName);
        console.log('[Hide Cell] - Removed from hiddenCells set');
        console.log('[Hide Cell] - Set editedCells[' + cellName + '][hidden] = false');
        console.log('[Hide Cell] - editedCells:', window.editedCells);
        // Restore visual state
        if (row) {
            row.classList.remove('opacity-30');
            console.log('[Hide Cell] - Removed opacity-30 from row');
        }
        if (btn) {
            btn.classList.remove('btn-warning');
            btn.classList.add('btn-success');
            btn.title = 'Hide cell';
            btn.dataset.hidden = 'false';
            console.log('[Hide Cell] - Button changed to GREEN (success) with title "Hide cell"');
        }
    } else {
        // Hide
        hiddenCells.add(cellName);
        console.log('[Hide Cell] ❌ HIDING:', cellName);
        console.log('[Hide Cell] - Added to hiddenCells set');
        console.log('[Hide Cell] - Total hidden cells:', hiddenCells.size);
        console.log('[Hide Cell] - Hidden list:', Array.from(hiddenCells));
        // Visually mark row as hidden (dimmed)
        if (row) {
            row.classList.add('opacity-30');
            console.log('[Hide Cell] - Added opacity-30 to row');
        }
        if (btn) {
            btn.classList.remove('btn-success');
            btn.classList.add('btn-warning');
            btn.title = 'Unhide cell';
            btn.dataset.hidden = 'true';
            console.log('[Hide Cell] - Button changed to YELLOW (warning) with title "Unhide cell"');
        }
    }
    
    console.log(`[Hide Cell] ${hiddenCells.has(cellName) ? 'Hidden' : 'Unhidden'}: ${cellName}`);
}

/**
 * Clear all hidden cells tracking
 * Called when exiting edit mode or resetting state
 */
function clearHiddenCells() {
    hiddenCells.clear();
    console.log('[Hide Cell] Cleared all hidden cells tracking');
}

/**
 * Get array of currently hidden cell names
 * @returns {string[]} - Array of cell names marked as hidden
 */
function getHiddenCellsArray() {
    return Array.from(hiddenCells);
}

// Export functions and data to global scope for use in project_status.js
window.HideCell = {
    hiddenCells,
    isHiddenCell,
    handleHideCell,
    clearHiddenCells,
    getHiddenCellsArray
};
