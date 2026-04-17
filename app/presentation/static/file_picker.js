/**
 * Reusable File/Folder Picker Component
 * 
 * Usage:
 * 1. Include this script in your HTML: <script src="/static/file_picker.js"></script>
 * 2. Call FilePicker.open() to show the picker
 * 3. Handle selection with callback: FilePicker.open((path, isDir) => { console.log(path); })
 */

const FilePicker = (function() {
    let modal = null;
    let currentPath = '';
    let lastBrowsedPath = '';
    let onSelectCallback = null;
    // Track the input that triggered the picker (captured on button click)
    let pendingTargetInputId = null;
    let pendingInitialPath = '';
    let pendingPreselectFile = '';
    const STORAGE_KEY = 'file_picker_last_path';

    // Attach a global click listener immediately (not inside init) so
    // clicks that trigger FilePicker.open are captured before open() runs.
    (function attachBrowseClickCapture() {
        if (typeof document !== 'undefined') {
            document.addEventListener('click', (evt) => {
                const el = evt.target && evt.target.closest ? evt.target.closest('button[data-browser="true"][data-target-input]') : null;
                if (!el) return;
                const targetId = el.getAttribute('data-target-input');
                const inputEl = document.getElementById(targetId);
                const val = (inputEl && typeof inputEl.value === 'string') ? inputEl.value.trim() : '';
                const placeholder = (inputEl && inputEl.getAttribute) ? (inputEl.getAttribute('placeholder') || '') : '';
                pendingTargetInputId = targetId;
                pendingInitialPath = val;
                console.debug('[FilePicker] Captured browse click. targetId=', targetId, 'initialPath=', val, 'placeholder=', placeholder, 'inputEl:', inputEl);
            }, true);
        }
    })();

    /**
     * Initialize the file picker (creates modal if needed)
     */
    function init() {
        if (modal) return; // Already initialized
        
        // Load last browsed path from localStorage
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (saved) {
                lastBrowsedPath = saved;
                console.log('[FilePicker] Loaded last path:', lastBrowsedPath);
            }
        } catch (e) {
            console.warn('[FilePicker] Failed to load last path:', e);
        }

        // Create modal HTML
        const modalHtml = `
            <dialog id="filePickerModal" class="modal">
                <div class="modal-box w-11/12 max-w-7xl">
                    <h3 class="font-bold text-lg mb-4">Select File or Folder</h3>
                    
                    <div class="form-control mb-4">
                        <div class="flex items-center gap-2 w-full">
                            <input type="text" id="filePickerPathInput" placeholder="Enter path..." 
                                   class="input input-bordered flex-1 font-mono text-sm"/>
                            <button onclick="FilePicker._browseInputPath()" class="btn btn-ghost btn-square">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                </svg>
                            </button>
                        </div>
                        <label class="label">
                            <span class="label-text-alt text-error hidden" id="filePickerError"></span>
                        </label>
                    </div>

                    <div class="breadcrumb-nav mb-4">
                        <div class="text-sm breadcrumbs">
                            <ul id="filePickerBreadcrumb"></ul>
                        </div>
                    </div>

                    <div class="overflow-x-auto border rounded-lg" style="max-height: 400px;">
                        <table class="table table-zebra table-sm w-full">
                            <thead class="sticky top-0 bg-base-200">
                                <tr>
                                    <th>Name</th>
                                    <th class="text-right">Size</th>
                                    <th>Modified</th>
                                </tr>
                            </thead>
                            <tbody id="filePickerEntries">
                                <tr><td colspan="3" class="text-center">Loading...</td></tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="modal-action">
                        <button onclick="FilePicker._selectCurrent()" class="btn btn-primary">
                            Select Current Folder
                        </button>
                        <button onclick="FilePicker.close()" class="btn">Cancel</button>
                    </div>
                </div>
                <form method="dialog" class="modal-backdrop">
                    <button onclick="FilePicker.close()">close</button>
                </form>
            </dialog>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        modal = document.getElementById('filePickerModal');

    }

    /**
     * Open the file picker
     * @param {Function} callback - Called with (path, isDirectory) when selection is made
     */
    async function open(callback) {
        init();
        onSelectCallback = callback;
        modal.showModal();

        // Priority 1: Use the captured initial path from the clicked Browse button
        if (pendingTargetInputId) {
            console.debug('[FilePicker.open] pendingTargetInputId:', pendingTargetInputId, 'pendingInitialPath:', pendingInitialPath);
            if (pendingInitialPath) {
                // Validate the path to determine if it's a directory or file
                try {
                    const validateResp = await fetch('/api/file-picker/validate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ path: pendingInitialPath })
                    });
                    const validateData = await validateResp.json();
                    console.debug('[FilePicker.open] validate result:', validateData);
                    if (validateData.is_valid) {
                        if (validateData.is_directory) {
                            console.log('[FilePicker] Starting from directory:', pendingInitialPath);
                            await browsePath(pendingInitialPath);
                        } else {
                            // Browse parent directory and remember file for highlight
                            const parentPath = deriveParentPath(pendingInitialPath);
                            pendingPreselectFile = pendingInitialPath;
                            console.log('[FilePicker] Starting from file; browsing parent:', parentPath, 'file:', pendingPreselectFile);
                            await browsePath(parentPath);
                        }
                        // reset initial tracking (keep preselect for later)
                        pendingTargetInputId = null;
                        pendingInitialPath = '';
                        return;
                    } else {
                        console.debug('[FilePicker.open] Path invalid, falling back:', pendingInitialPath);
                    }
                } catch (e) {
                    console.warn('[FilePicker.open] Validation failed, fallback to last/default. Error:', e);
                }
            }
            // reset if empty path or validation failed
            pendingTargetInputId = null;
            pendingInitialPath = '';
            console.debug('[FilePicker.open] No usable initial path, continuing');
        }

        // Priority 2: Use last browsed path if available
        if (lastBrowsedPath) {
            console.log('[FilePicker] Resuming from last path:', lastBrowsedPath);
            browsePath(lastBrowsedPath);
            return;
        }

        // Priority 3: Fallback to default path from API
        try {
            // Get project/subproject from AppSelection if available
            const selection = window.AppSelection ? window.AppSelection.get() : {project: '', subproject: ''};
            const params = new URLSearchParams();
            if (selection.project) params.append('project', selection.project);
            if (selection.subproject) params.append('subproject', selection.subproject);
            
            const url = '/api/file-picker/default-path' + (params.toString() ? '?' + params.toString() : '');
            console.debug('[FilePicker] Fetching default path with:', {project: selection.project, subproject: selection.subproject});
            
            const response = await fetch(url);
            const data = await response.json();
            console.log('[FilePicker] Got default path:', data.path);
            browsePath(data.path);
        } catch (error) {
            console.error('[FilePicker] Failed to get default path:', error);
            browsePath('/');
        }
    }

    /**
     * Close the file picker
     */
    function close() {
        if (modal) modal.close();
    }

    /**
     * Browse a directory
     */
    async function browsePath(path) {
        console.log('[FilePicker] Browsing:', path);
        
        const pathInput = document.getElementById('filePickerPathInput');
        const errorEl = document.getElementById('filePickerError');
        const entriesEl = document.getElementById('filePickerEntries');
        
        pathInput.value = path;
        currentPath = path;
        errorEl.textContent = '';
        errorEl.classList.add('hidden');
        entriesEl.innerHTML = '<tr><td colspan="3" class="text-center">Loading...</td></tr>';
        
        try {
            const response = await fetch('/api/file-picker/browse', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: path })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to browse directory');
            }
            
            const data = await response.json();
            updateBreadcrumb(data.current_path, data.parent_path);
            displayEntries(data.entries);
            
            // Save last browsed path to localStorage
            lastBrowsedPath = path;
            try {
                localStorage.setItem(STORAGE_KEY, path);
            } catch (e) {
                console.warn('[FilePicker] Failed to save last path:', e);
            }
        } catch (error) {
            console.error('[FilePicker] Error:', error);
            errorEl.textContent = error.message;
            errorEl.classList.remove('hidden');
            entriesEl.innerHTML = `<tr><td colspan="3" class="text-center text-error">${error.message}</td></tr>`;
        }
    }

    /**
     * Update breadcrumb navigation
     */
    function updateBreadcrumb(currentPath, parentPath) {
        const breadcrumb = document.getElementById('filePickerBreadcrumb');
        breadcrumb.innerHTML = '';
        
        if (parentPath) {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = '#';
            a.textContent = '..';
            a.onclick = (e) => { e.preventDefault(); browsePath(parentPath); };
            li.appendChild(a);
            breadcrumb.appendChild(li);
        }
        
        const normalizedPath = currentPath.replace(/\\/g, '/');
        if (normalizedPath === '/') {
            breadcrumb.innerHTML += '<li>/</li>';
            return;
        }
        
        const isWindows = /^[A-Za-z]:/.test(normalizedPath);
        const segments = isWindows ? normalizedPath.split('/').filter(s => s) : normalizedPath.replace(/^\/+/, '').split('/').filter(s => s);
        
        segments.forEach((segment, index) => {
            const li = document.createElement('li');
            const accumulatedPath = isWindows 
                ? (index === 0 ? segment + '/' : segments.slice(0, index + 1).join('/'))
                : '/' + segments.slice(0, index + 1).join('/');
            
            if (index === segments.length - 1) {
                li.textContent = segment;
            } else {
                const a = document.createElement('a');
                a.href = '#';
                a.textContent = segment;
                a.onclick = (e) => { e.preventDefault(); browsePath(accumulatedPath); };
                li.appendChild(a);
            }
            breadcrumb.appendChild(li);
        });
    }

    /**
     * Display directory entries
     */
    function displayEntries(entries) {
        const entriesEl = document.getElementById('filePickerEntries');
        
        if (entries.length === 0) {
            entriesEl.innerHTML = '<tr><td colspan="3" class="text-center">Empty directory</td></tr>';
            return;
        }
        
        entriesEl.innerHTML = entries.map(entry => {
            const icon = entry.is_dir ? '📁' : '📄';
            const size = entry.size !== null ? formatSize(entry.size) : '';
            const modified = entry.modified_time ? formatDate(entry.modified_time) : '';
            const highlighted = (pendingPreselectFile && entry.path === pendingPreselectFile);
            return `
                <tr class="cursor-pointer hover:bg-base-200 ${highlighted ? 'bg-primary/20 outline outline-primary' : ''}" 
                    data-path="${escapeHtml(entry.path)}" 
                    data-is-dir="${entry.is_dir}"
                    onclick="FilePicker._selectEntry(this)">
                    <td><span>${icon}</span> <span class="font-mono text-sm">${escapeHtml(entry.name)}</span></td>
                    <td class="text-right font-mono text-xs">${size}</td>
                    <td class="text-sm">${modified}</td>
                </tr>
            `;
        }).join('');

        if (pendingPreselectFile) {
            console.debug('[FilePicker.displayEntries] Attempted highlight for:', pendingPreselectFile);
            // Clear after attempting highlight
            pendingPreselectFile = '';
        }
    }

    /**
     * Handle entry selection/browsing
     */
    function selectEntry(element) {
        const path = element.dataset.path;
        const isDir = element.dataset.isDir === 'true';
        
        if (isDir) {
            browsePath(path);
        } else {
            selectPath(path, false);
        }
    }

    /**
     * Select a path and close picker
     */
    function selectPath(path, isDirectory) {
        console.log('[FilePicker] Selected:', path, 'isDirectory:', isDirectory);
        close();
        if (onSelectCallback) {
            onSelectCallback(path, isDirectory);
        }
    }

    /**
     * Select current directory
     */
    function selectCurrent() {
        selectPath(currentPath, true);
    }

    /**
     * Browse path from input field
     */
    function browseInputPath() {
        const pathInput = document.getElementById('filePickerPathInput');
        const path = pathInput.value.trim();
        if (path) browsePath(path);
    }

    // Utility functions
    function formatSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function formatDate(isoString) {
        try {
            return new Date(isoString).toLocaleString();
        } catch (e) {
            return isoString;
        }
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function deriveParentPath(p) {
        if (!p) return '/';
        // Normalize slashes
        const norm = p.replace(/\\/g, '/');
        // Windows drive root pattern e.g. C:/
        if (/^[A-Za-z]:\/$/.test(norm)) return norm; // already at drive root
        const segments = norm.split('/').filter(s => s);
        if (segments.length <= 1) {
            // Single segment; could be drive like C: without slash
            if (/^[A-Za-z]:$/.test(segments[0])) return segments[0] + '/';
            return '/';
        }
        // Remove last segment (file)
        segments.pop();
        // Windows drive path logic
        if (/^[A-Za-z]:/.test(segments[0])) {
            return segments.join('/') + '/';
        }
        return '/' + segments.join('/');
    }

    // Public API
    return {
        open: open,
        close: close,
        _browsePath: browsePath,
        _selectEntry: selectEntry,
        _selectCurrent: selectCurrent,
        _browseInputPath: browseInputPath
    };
})();
