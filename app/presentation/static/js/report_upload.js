// Report Upload Page JavaScript

/**
 * Handle form submission for uploading reports to P4
 */
async function handleUpload(event) {
    event.preventDefault();
    
    const uploadButton = document.getElementById('uploadButton');
    const buttonText = document.getElementById('buttonText');
    const uploadSpinner = document.getElementById('uploadSpinner');
    const statusMessage = document.getElementById('statusMessage');
    const statusAlert = document.getElementById('statusAlert');
    const statusIcon = document.getElementById('statusIcon');
    const statusText = document.getElementById('statusText');
    
    // Get form values
    const localPath = document.getElementById('localPath').value.trim();
    let depotPath = document.getElementById('depotPath').value.trim();
    const description = document.getElementById('description').value.trim();
    
    // Extract filename from local path
    const filename = localPath.split(/[\\\/]/).pop();
    console.log('[Report Upload] Extracted filename:', filename);
    
    // Auto-append filename to depot path if not already present
    if (filename && !depotPath.endsWith(filename)) {
        // Ensure depot path ends with / before appending
        if (!depotPath.endsWith('/')) {
            depotPath += '/';
        }
        depotPath += filename;
        console.log('[Report Upload] Auto-appended filename to depot path');
    }
    
    console.log('[Report Upload] Starting upload...');
    console.log('[Report Upload] Local Path:', localPath);
    console.log('[Report Upload] Depot Path (final):', depotPath);
    console.log('[Report Upload] Description:', description || '(auto-generated)');
    
    // Validate inputs
    if (!localPath || !depotPath) {
        showStatus(false, 'Please fill in both Local Path and Depot Path');
        console.error('[Report Upload] Validation failed: missing required fields');
        return;
    }
    
    // Disable button and show spinner
    uploadButton.disabled = true;
    buttonText.textContent = 'Uploading...';
    uploadSpinner.classList.remove('hidden');
    statusMessage.classList.add('hidden');
    
    try {
        console.log('[Report Upload] Sending API request...');
        
        const response = await fetch('/api/report-upload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                local_path: localPath,
                depot_path: depotPath,
                description: description
            })
        });
        
        console.log('[Report Upload] Response status:', response.status);
        
        const result = await response.json();
        console.log('[Report Upload] Response data:', result);
        
        if (response.ok && result.success) {
            console.log('[Report Upload] ✅ Upload succeeded:', result.success);
            console.log('[Report Upload] Message:', result.message);
            showStatus(true, result.message);
            // Clear form on success
            document.getElementById('uploadForm').reset();
        } else {
            console.error('[Report Upload] ❌ Upload failed:', result.success);
            console.error('[Report Upload] Error message:', result.message);
            showStatus(false, result.message || 'Upload failed');
        }
    } catch (error) {
        console.error('[Report Upload] ❌ Exception during upload:', error);
        console.error('[Report Upload] Error details:', error.message);
        showStatus(false, `Error: ${error.message}`);
    } finally {
        // Re-enable button and hide spinner
        uploadButton.disabled = false;
        buttonText.textContent = 'Upload to P4';
        uploadSpinner.classList.add('hidden');
        console.log('[Report Upload] Upload process completed');
    }
}

/**
 * Show status message to user
 */
function showStatus(isSuccess, message) {
    const statusMessage = document.getElementById('statusMessage');
    const statusAlert = document.getElementById('statusAlert');
    const statusIcon = document.getElementById('statusIcon');
    const statusText = document.getElementById('statusText');
    
    // Update alert styling
    if (isSuccess) {
        statusAlert.className = 'alert alert-success';
        statusIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>';
    } else {
        statusAlert.className = 'alert alert-error';
        statusIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>';
    }
    
    statusText.textContent = message;
    statusMessage.classList.remove('hidden');
}

/**
 * Clear form fields
 */
function handleClear() {
    console.log('[Report Upload] Clearing form');
    document.getElementById('uploadForm').reset();
    document.getElementById('statusMessage').classList.add('hidden');
}

/**
 * Get selected project/subproject from storage
 */
function getSelectedProjectInfo() {
    try {
        const project = localStorage.getItem('timing_selected_project') || 
                       sessionStorage.getItem('timing_selected_project') || '';
        const subproject = localStorage.getItem('timing_selected_subproject') || 
                          sessionStorage.getItem('timing_selected_subproject') || '';
        return { project, subproject };
    } catch (_) {
        return { project: '', subproject: '' };
    }
}

/**
 * Auto-fill depot path based on filename pattern
 */
function autoFillDepotPath(localPath) {
    const filename = localPath.split(/[\\\/]/).pop();
    const depotPathInput = document.getElementById('depotPath');
    
    // Don't override if user already typed something
    if (depotPathInput.value.trim()) {
        return;
    }
    
    const { project, subproject } = getSelectedProjectInfo();
    
    if (!project || !subproject) {
        console.log('[Report Upload] No project/subproject selected, skipping auto-fill');
        return;
    }
    
    let depotPath = '';
    
    // Check for TMQC_Report
    if (filename.includes('TMQC_Report')) {
        depotPath = `//wwcad/msip/projects/ucie/${project}/${subproject}/design/timing/docs/report/qc/`;
        console.log('[Report Upload] Auto-filled TMQC_Report depot path');
    }
    // Check for InternalTiming_Report
    else if (filename.includes('InternalTiming_Report')) {
        depotPath = `//wwcad/msip/projects/ucie/${project}/${subproject}/design/timing/docs/report/internal/`;
        console.log('[Report Upload] Auto-filled InternalTiming_Report depot path');
    }
    // Check for TMQA_Report
    else if (filename.includes('TMQA_Report')) {
        depotPath = `//wwcad/msip/projects/ucie/${project}/${subproject}/design/timing/docs/report/qa/`;
        console.log('[Report Upload] Auto-filled TMQA_Report depot path');
    }
    else if (filename.includes('PackageCompare_Report')) {
        depotPath = `//wwcad/msip/projects/ucie/${project}/${subproject}/design/timing/docs/report/review/`;
        console.log('[Report Upload] Auto-filled PackageCompare_Report depot path');
    }
    else if (filename.includes('SpecialCheckReport')) {
        depotPath = `//wwcad/msip/projects/ucie/${project}/${subproject}/design/timing/docs/report/review/`;
        console.log('[Report Upload] Auto-filled SpecialCheckReport depot path');
    }
    if (depotPath) {
        depotPathInput.value = depotPath;
        console.log('[Report Upload] Depot path set to:', depotPath);
    }
}

/**
 * Initialize event listeners
 */
function setupEventListeners() {
    const uploadForm = document.getElementById('uploadForm');
    const clearButton = document.getElementById('clearButton');
    const localPathInput = document.getElementById('localPath');
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleUpload);
        console.log('[Report Upload] Form submit listener attached');
    }
    
    if (clearButton) {
        clearButton.addEventListener('click', handleClear);
        console.log('[Report Upload] Clear button listener attached');
    }
    
    if (localPathInput) {
        localPathInput.addEventListener('input', (event) => {
            autoFillDepotPath(event.target.value);
        });
        localPathInput.addEventListener('change', (event) => {
            autoFillDepotPath(event.target.value);
        });
        console.log('[Report Upload] Local path auto-fill listener attached');
    }
}

/**
 * Setup FilePicker integration
 */
function setupFilePicker() {
    // Setup browse button to open FilePicker
    const browseButton = document.querySelector('button[data-browser="true"][data-target-input="localPath"]');
    const localPathInput = document.getElementById('localPath');
    
    if (browseButton && localPathInput) {
        browseButton.addEventListener('click', () => {
            console.log('[Report Upload] Browse button clicked');
            
            if (typeof FilePicker !== 'undefined' && typeof FilePicker.open === 'function') {
                console.log('[Report Upload] Opening FilePicker');
                FilePicker.open((path, isDirectory) => {
                    console.log('[Report Upload] FilePicker selected:', path, 'isDirectory:', isDirectory);
                    localPathInput.value = path;
                    // Trigger auto-fill after selection
                    autoFillDepotPath(path);
                });
            } else {
                console.error('[Report Upload] FilePicker not available');
                alert('File picker is not available. Please ensure file_picker.js is loaded.');
            }
        });
        
        console.log('[Report Upload] Browse button handler attached');
    } else {
        console.warn('[Report Upload] Browse button or input not found');
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('[Report Upload] Page loaded, initializing...');
    setupEventListeners();
    setupFilePicker();
});
