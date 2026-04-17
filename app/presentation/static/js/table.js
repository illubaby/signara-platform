// Reusable CSV-like table renderer for text files
// Provides a small API via window.TableView
(function() {
    const TableView = {
        async fetchText(filePath) {
            // Add timestamp for cache-busting and no-store to prevent stale data
            const url = `/api/files/download?file_path=${encodeURIComponent(filePath)}&t=${Date.now()}`;
            const resp = await fetch(url, { cache: 'no-store' });
            if (!resp.ok) throw new Error(`Failed to fetch file: ${resp.status}`);
            return await resp.text();
        },

        parseCsvLike(text, startLine = 1) {
            // startLine is 1-based line index within the file where headers exist
            const lines = text.split(/\r?\n/);
            // Guard: if startLine is out of range
            if (startLine < 1 || startLine > lines.length) return { headers: [], rows: [] };
            // Slice from startLine-1 onward, trim and drop comments/empties
            const sliced = lines.slice(startLine - 1).map(l => l.trim());
            const filtered = sliced.filter(l => l.length > 0 && !l.startsWith('#'));
            if (filtered.length === 0) return { headers: [], rows: [] };
            const headers = filtered[0].split(',').map(h => h.trim());
            const rows = [];
            for (let i = 1; i < filtered.length; i++) {
                const cols = filtered[i].split(',').map(c => c.trim());
                if (cols.every(c => c === '')) continue;
                rows.push(cols);
            }
            return { headers, rows };
        },

        // Find or create a container, preferring main content wrappers
        ensureContainer(selector, defaultId = 'package-summary', maxWidth = '80vw') {
            const host = document.querySelector('main, #app-content, .page-content') || document.body;
            let container = selector ? document.querySelector(selector) : document.getElementById(defaultId);
            if (!container && !selector) {
                container = document.createElement('div');
                container.id = defaultId;
                container.className = 'mt-6 mx-auto relative z-0';
                container.style.maxWidth = maxWidth;
                host.appendChild(container);
            } else if (container) {
                container.classList.add('mx-auto');
                container.classList.add('relative');
                container.classList.add('z-0');
                container.style.maxWidth = maxWidth;
            }
            return container || host;
        },

        renderTable(container, data, title = 'Table', maxWidth = '80vw') {
            const { headers, rows } = data;
            if (!container) return;

            // Enforce width and clear previous content
            container.style.maxWidth = maxWidth;
            container.innerHTML = '';

            const card = document.createElement('div');
            // Use the same glass effect class as navbar/sidebar for consistent blur
            // Add pb-8 class and a slight bottom offset per your tested rule
            card.className = 'card shadow-md glass-panel-card';
            card.style.position = 'relative';
            card.style.bottom = '15px';
            const cardBody = document.createElement('div');
            // Add slight bottom padding to give breathing room below the table
            cardBody.className = 'card-body';

            const h2 = document.createElement('h2');
            h2.className = 'card-title';
            h2.textContent = title;
            cardBody.appendChild(h2);

            const wrapper = document.createElement('div');
            // Keep rounded edges; glass effect already on card
            wrapper.className = 'overflow-x-auto rounded-box';

            const table = document.createElement('table');
            // Use a consistent row style (no zebra) and compact spacing
            table.className = 'table table-compact';

            const thead = document.createElement('thead');
            const trHead = document.createElement('tr');
            headers.forEach(h => {
                const th = document.createElement('th');
                th.textContent = h;
                trHead.appendChild(th);
            });
            thead.appendChild(trHead);

            const tbody = document.createElement('tbody');
            rows.forEach(cols => {
                const tr = document.createElement('tr');
                const normalized = cols.length >= headers.length
                    ? cols.slice(0, headers.length)
                    : cols.concat(Array(headers.length - cols.length).fill(''));
                normalized.forEach(val => {
                    const td = document.createElement('td');
                    td.textContent = val;
                    const v = (val || '').toString().trim().toUpperCase();
                    // Strict match: only highlight if the entire cell equals the keyword
                    const isNegative = /^(MISMATCH|VIOLATE)$/i.test(v);
                    const isPositive = /^(MATCH|MET)$/i.test(v);
                    if (isNegative) {
                        td.classList.add('text-error');
                        td.classList.add('font-medium');
                        td.classList.add('font-bold');
                    } else if (isPositive) {
                        td.classList.add('text-success');
                        td.classList.add('font-medium');
                        td.classList.add('font-bold');
                    } else {
                        // If the cell is a plain number and negative, highlight as error
                        const numMatch = /^-?\d+(?:\.\d+)?$/.test(v);
                        if (numMatch) {
                            const numVal = parseFloat(val);
                            if (!isNaN(numVal) && numVal < 0) {
                                td.classList.add('text-error');
                                td.classList.add('font-bold');
                            }
                        }
                    }
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });

            table.appendChild(thead);
            table.appendChild(tbody);
            wrapper.appendChild(table);
            cardBody.appendChild(wrapper);
            card.appendChild(cardBody);
            container.appendChild(card);
        },

        async renderFromFile(filePath, options = {}) {
            const { containerSelector, title = 'Table', maxWidth = '80vw', startLine = 1 } = options;
            const container = this.ensureContainer(containerSelector, 'package-summary', maxWidth);
            try {
                const text = await this.fetchText(filePath);
                const parsed = this.parseCsvLike(text, startLine);
                if (parsed.headers.length && parsed.rows.length) {
                    this.renderTable(container, parsed, title, maxWidth);
                } else {
                    container.textContent = 'No data found in file';
                }
            } catch (err) {
                container.textContent = `Error loading file: ${err.message}`;
                console.error('[TableView] renderFromFile error', err);
            }
        },

        renderFromText(text, options = {}) {
            const { containerSelector, title = 'Table', maxWidth = '80vw', startLine = 1 } = options;
            const container = this.ensureContainer(containerSelector, 'package-summary', maxWidth);
            const parsed = this.parseCsvLike(text, startLine);
            if (parsed.headers.length && parsed.rows.length) {
                this.renderTable(container, parsed, title, maxWidth);
            } else {
                container.textContent = 'No data to display';
            }
        },

        // Render with real-time polling - automatically updates when file appears/changes
        // Returns a stop function to cancel polling
        renderWithPolling(filePathOrGetter, options = {}) {
            const {
                containerSelector,
                containerId = 'table-polling',
                title = 'Table',
                maxWidth = '80vw',
                startLine = 1,
                pollIntervalMs = 3000,
                waitingMessage = 'Waiting for file...',
                columnFilter = null,  // Function to filter columns: (headers, rows) => ({headers, rows})
                logPrefix = '[TableView]'
            } = options;

            let pollInterval = null;
            let hasRendered = false;

            const loadAndRender = async () => {
                try {
                    // Support both static string and dynamic getter function
                    const filePath = typeof filePathOrGetter === 'function' ? await filePathOrGetter() : filePathOrGetter;
                    const text = await this.fetchText(filePath);
                    const parsed = this.parseCsvLike(text, startLine);
                    
                    if (parsed.headers.length) {
                        let { headers, rows } = parsed;
                        
                        // Apply column filter if provided
                        if (columnFilter && typeof columnFilter === 'function') {
                            const filtered = columnFilter(headers, rows);
                            headers = filtered.headers;
                            rows = filtered.rows;
                        }
                        
                        const container = this.ensureContainer(containerSelector, containerId, maxWidth);
                        this.renderTable(container, { headers, rows }, title, maxWidth);
                        hasRendered = true;
                        return true; // Success
                    }
                    return false; // No data yet
                } catch (err) {
                    console.debug(`${logPrefix} File not yet available:`, err.message);
                    return false;
                }
            };

            const startPolling = async () => {
                const container = this.ensureContainer(containerSelector, containerId, maxWidth);
                // Waiting message removed - container will remain empty until data loads
                
                // Try to load immediately
                const success = await loadAndRender();
                if (success) {
                    if (pollInterval) {
                        clearInterval(pollInterval);
                        pollInterval = null;
                    }
                    return;
                }

                // If not successful, start polling
                if (!pollInterval) {
                    pollInterval = setInterval(async () => {
                        const success = await loadAndRender();
                        if (success && pollInterval) {
                            clearInterval(pollInterval);
                            pollInterval = null;
                        }
                    }, pollIntervalMs);
                }
            };

            // Auto-start polling
            startPolling();

            // Return stop function and manual refresh function
            return {
                stop: () => {
                    if (pollInterval) {
                        clearInterval(pollInterval);
                        pollInterval = null;
                    }
                },
                refresh: startPolling
            };
        }
    };

    window.TableView = TableView;
})();