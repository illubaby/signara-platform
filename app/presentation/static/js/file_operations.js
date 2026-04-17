/**
 * File Operations - JavaScript API client
 * 
 * Simple functions to open files with their default applications.
 * Call the backend API and show notifications to users.
 */

console.log('[file_operations.js] Script loaded successfully');

/**
 * Open a file with its default system application
 * @param {string} filePath - Absolute or relative path to the file
 * @returns {Promise<void>}
 */
async function openFileWithDefaultApp(filePath) {
    console.log('[openFileWithDefaultApp] Opening file:', filePath);
    
    if (!filePath || filePath.trim() === '') {
        console.error('[openFileWithDefaultApp] Empty file path');
        showNotification('error', 'Please provide a file path');
        return;
    }
    
    try {
        const response = await fetch('/api/files/open', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                file_path: filePath.trim()
            })
        });
        
        console.log('[openFileWithDefaultApp] Response status:', response.status);
        
        const data = await response.json();
        console.log('[openFileWithDefaultApp] Response data:', data);
        
        if (response.ok) {
            // Success
            showNotification('success', data.message || 'File opened successfully');
        } else {
            // API returned an error
            showNotification('error', data.detail || 'Failed to open file');
        }
        
    } catch (error) {
        console.error('[openFileWithDefaultApp] Network error:', error);
        showNotification('error', 'Network error: Could not connect to server');
    }
}

/**
 * Download a file from the server and trigger the browser's download flow.
 * Attempts to auto-open based on browser settings (cannot force native Excel).
 * @param {string} filePath
 * @returns {Promise<void>}
 */
async function downloadAndAutoOpenFile(filePath) {
    console.log('[downloadAndAutoOpenFile] Downloading file:', filePath);
    if (!filePath || filePath.trim() === '') {
        showNotification('warning', 'Please provide a file path');
        return;
    }
    try {
        const encoded = encodeURIComponent(filePath.trim());
        const url = `/api/files/download?file_path=${encoded}`;
        const resp = await fetch(url);
        if (!resp.ok) {
            const errData = await resp.json().catch(() => ({}));
            showNotification('error', errData.detail || 'Download failed');
            return;
        }
        // Extract filename from Content-Disposition header if present
        const cd = resp.headers.get('Content-Disposition') || '';
        let filename = 'downloaded_file';
        const match = cd.match(/filename="?([^";]+)"?/);
        if (match) filename = match[1];
        const blob = await resp.blob();
        const objectUrl = URL.createObjectURL(blob);
        // Create temporary anchor to trigger download
        const a = document.createElement('a');
        a.href = objectUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(objectUrl), 5000);
        showNotification('success', `Download started: ${filename}`);
    } catch (e) {
        console.error('[downloadAndAutoOpenFile] Error:', e);
        showNotification('error', 'Network error during download');
    }
}

/**
 * Show notification to user
 * Uses DaisyUI toast if available, otherwise fallback to alert
 * @param {string} type - 'success', 'error', 'warning', 'info'
 * @param {string} message - Message to display
 */
function showNotification(type, message) {
    console.log(`[showNotification] ${type}: ${message}`);
    
    // Try to use existing notification system if available
    if (typeof window.showToast === 'function') {
        window.showToast(type, message);
        return;
    }
    
    // Fallback: Create a simple DaisyUI alert
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-error',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';
    
    const alertHtml = `
        <div class="alert ${alertClass} shadow-lg fixed top-4 right-4 w-auto max-w-md z-50" id="temp-notification">
            <div>
                <span>${message}</span>
            </div>
        </div>
    `;
    
    // Insert notification
    document.body.insertAdjacentHTML('beforeend', alertHtml);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        const notification = document.getElementById('temp-notification');
        if (notification) {
            notification.remove();
        }
    }, 3000);
}

/**
 * Initialize file open handlers for elements with data-filepath attribute
 * Usage: Add class="open-file-btn" and data-filepath="path/to/file" to any element
 */
function initializeFileOpenHandlers() {
    console.log('[initializeFileOpenHandlers] Setting up file open handlers');
    
    document.querySelectorAll('.open-file-btn').forEach(element => {
        element.addEventListener('click', async (event) => {
            event.preventDefault();
            const filePath = element.dataset.filepath;
            
            if (filePath) {
                await openFileWithDefaultApp(filePath);
            } else {
                console.error('[initializeFileOpenHandlers] No filepath in dataset');
                showNotification('error', 'No file path specified');
            }
        });
    });
}

// Export functions if using modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        openFileWithDefaultApp,
        showNotification,
        initializeFileOpenHandlers,
        downloadAndAutoOpenFile
    };
}
