/**
 * Version Check Module
 * 
 * Checks application version against P4 depot and shows warnings/blocks accordingly.
 * - Before deadline: Shows warning modal once per hour if outdated
 * - After deadline: Blocks usage until user updates
 * - After updating: Shows "What's New" changelog modal
 */

(function() {
    'use strict';

    const AUTO_CHECK_DELAY = 10 * 1000; // 10 seconds after page load
    const VERSION_CHECK_INTERVAL = 60 * 60 * 1000; // 1 hour in milliseconds
    const STORAGE_KEY = 'timecraft_last_version_check';
    const DISMISSED_KEY = 'timecraft_version_dismissed_until';
    const LAST_SEEN_VERSION_KEY = 'timecraft_last_seen_version';

    /**
     * Update version badge in footer
     */
    function updateVersionBadge(version, isOutdated) {
        const badge = document.getElementById('appVersionBadge');
        if (badge) {
            badge.textContent = `v${version}`;
            badge.title = isOutdated ? 'Update available! Click to check.' : 'Click to view changelog';
            if (isOutdated) {
                badge.classList.remove('badge-ghost');
                badge.classList.add('badge-warning');
            }
        }
    }

    /**
     * Check if version changed (user updated the app)
     */
    function checkVersionChanged(currentVersion) {
        const lastSeenVersion = localStorage.getItem(LAST_SEEN_VERSION_KEY);
        if (!lastSeenVersion) {
            // First time - save version but don't show modal
            localStorage.setItem(LAST_SEEN_VERSION_KEY, currentVersion);
            return false;
        }
        if (lastSeenVersion !== currentVersion) {
            console.log(`[VersionCheck] Version changed: ${lastSeenVersion} -> ${currentVersion}`);
            return true;
        }
        return false;
    }

    /**
     * Mark current version as seen
     */
    function markVersionSeen(version) {
        localStorage.setItem(LAST_SEEN_VERSION_KEY, version);
    }

    /**
     * Simple markdown to HTML converter for changelog
     */
    function parseChangelogMarkdown(markdown) {
        return markdown
            // Headers
            .replace(/^### (.*$)/gim, '<h4 class="font-semibold text-base mt-3 mb-1">$1</h4>')
            .replace(/^## (.*$)/gim, '<h3 class="font-bold text-lg mt-4 mb-2 text-primary">$1</h3>')
            .replace(/^# (.*$)/gim, '<h2 class="font-bold text-xl mb-3">$1</h2>')
            // Bold
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Code
            .replace(/`(.*?)`/g, '<code class="bg-base-300 px-1 rounded text-sm">$1</code>')
            // List items
            .replace(/^- (.*$)/gim, '<li class="ml-4">$1</li>')
            // Horizontal rules
            .replace(/^---$/gim, '<hr class="my-4 border-base-300">')
            // Line breaks
            .replace(/\n/g, '<br>')
            // Wrap consecutive <li> in <ul>
            .replace(/(<li.*<\/li>)(<br>)?(<li)/g, '$1$3')
            .replace(/(<li class="ml-4">.*?<\/li>)/g, '<ul class="list-disc">$1</ul>')
            // Clean up multiple <ul> tags
            .replace(/<\/ul><br><ul class="list-disc">/g, '');
    }

    /**
     * Show "What's New" changelog modal
     */
    async function showChangelogModal(version) {
        // Remove existing modal if present
        const existing = document.getElementById('changelogModal');
        if (existing) existing.remove();

        // Fetch changelog
        let changelogHtml = '<p class="text-base-content/70">Loading changelog...</p>';
        try {
            const response = await fetch('/api/version/changelog');
            if (response.ok) {
                const markdown = await response.text();
                changelogHtml = parseChangelogMarkdown(markdown);
            }
        } catch (error) {
            console.error('[VersionCheck] Failed to fetch changelog:', error);
            changelogHtml = '<p class="text-error">Failed to load changelog.</p>';
        }

        const modalHtml = `
            <dialog id="changelogModal" class="modal">
                <div class="modal-box w-11/12 max-w-3xl max-h-[80vh]">
                    <h3 class="font-bold text-xl flex items-center gap-3 text-success mb-4">
                        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z">
                            </path>
                        </svg>
                        🎉 What's New in v${version}
                    </h3>
                    
                    <div class="overflow-y-auto max-h-[55vh] pr-2 changelog-content">
                        ${changelogHtml}
                    </div>
                    
                    <div class="modal-action">
                        <button class="btn btn-primary" onclick="window.closeChangelogModal()">Got it!</button>
                    </div>
                </div>
                <form method="dialog" class="modal-backdrop">
                    <button>close</button>
                </form>
            </dialog>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        const modal = document.getElementById('changelogModal');
        modal.showModal();
        
        // Mark version as seen when modal is shown
        markVersionSeen(version);
    }

    /**
     * Global function to close changelog modal
     */
    window.closeChangelogModal = function() {
        const modal = document.getElementById('changelogModal');
        if (modal) {
            modal.close();
            modal.remove();
        }
    };

    /**
     * Global function to show changelog (can be called from version badge click)
     */
    window.showChangelog = async function() {
        const badge = document.getElementById('appVersionBadge');
        const version = badge ? badge.textContent.replace('v', '') : 'Unknown';
        await showChangelogModal(version);
    };

    /**
     * Check if we should show the modal (not dismissed in last hour)
     */
    function shouldShowModal() {
        const dismissedUntil = localStorage.getItem(DISMISSED_KEY);
        if (dismissedUntil) {
            const dismissTime = parseInt(dismissedUntil, 10);
            if (Date.now() < dismissTime) {
                console.log('[VersionCheck] Modal dismissed until:', new Date(dismissTime));
                return false;
            }
        }
        return true;
    }

    /**
     * Check if enough time has passed since last check (for hourly re-check)
     */
    function shouldRecheck() {
        const lastCheck = localStorage.getItem(STORAGE_KEY);
        if (!lastCheck) return true;
        const lastCheckTime = parseInt(lastCheck, 10);
        return (Date.now() - lastCheckTime) >= VERSION_CHECK_INTERVAL;
    }

    /**
     * Dismiss warning for 1 hour
     */
    function dismissForOneHour() {
        const dismissUntil = Date.now() + VERSION_CHECK_INTERVAL;
        localStorage.setItem(DISMISSED_KEY, dismissUntil.toString());
    }

    /**
     * Create and show the version warning/block modal
     */
    function showVersionModal(data) {
        // Remove existing modal if present
        const existing = document.getElementById('versionCheckModal');
        if (existing) existing.remove();

        const isBlocking = data.must_update;
        const deadlineStr = data.deadline ? new Date(data.deadline).toLocaleDateString('en-US', { 
            weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' 
        }) : 'Not set';
        
        // Parse remote changelog if available
        const changelogHtml = data.remote_changelog 
            ? parseChangelogMarkdown(data.remote_changelog)
            : '<p class="opacity-60 italic">No changelog available for this version.</p>';
        
        const modalHtml = `
            <dialog id="versionCheckModal" class="modal ${isBlocking ? 'modal-open' : ''}">
                <div class="modal-box w-11/12 max-w-3xl max-h-[90vh] ${isBlocking ? 'border-4 border-error' : 'border-2 border-warning'}">
                    <h3 class="font-bold text-xl flex items-center gap-3 ${isBlocking ? 'text-error' : 'text-warning'}">
                        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z">
                            </path>
                        </svg>
                        ${isBlocking ? 'Update Required!' : 'Update Available'}
                    </h3>
                    
                    <div class="py-4 space-y-4">
                        <div class="grid grid-cols-2 gap-4 text-base">
                            <div class="bg-base-200 rounded-lg p-4">
                                <span class="text-sm opacity-70 block mb-1">Your Version</span>
                                <span class="font-mono text-lg badge badge-lg badge-ghost">${data.local_version}</span>
                            </div>
                            <div class="bg-base-200 rounded-lg p-4">
                                <span class="text-sm opacity-70 block mb-1">Latest Version</span>
                                <span class="font-mono text-lg badge badge-lg badge-primary">${data.remote_version || 'Unknown'}</span>
                            </div>
                        </div>
                        
                        <div class="bg-base-200 rounded-lg p-4">
                            <span class="text-sm opacity-70 block mb-1">Update Deadline</span>
                            <span class="text-lg font-semibold ${data.is_past_deadline ? 'text-error' : ''}">${deadlineStr}</span>
                            ${data.is_past_deadline ? '<span class="badge badge-error badge-sm ml-2">EXPIRED</span>' : ''}
                        </div>
                        
                        <!-- What's New Section -->
                        <div class="bg-base-200 rounded-lg p-4">
                            <h4 class="font-bold text-base mb-2 flex items-center gap-2">
                                <span>🎉 What's New in v${data.remote_version || 'Latest'}</span>
                            </h4>
                            <div class="max-h-48 overflow-y-auto pr-2 text-sm changelog-content">
                                ${changelogHtml}
                            </div>
                        </div>
                        
                        <div class="divider my-2"></div>
                        
                        ${isBlocking ? `
                            <div class="alert alert-error text-base">
                                <svg class="w-8 h-8 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                        d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z">
                                    </path>
                                </svg>
                                <div>
                                    <h4 class="font-bold text-lg">Access Blocked</h4>
                                    <p>The update deadline has passed. You must update to continue using TimeCraft Platform.</p>
                                </div>
                            </div>
                        ` : `
                            <div class="alert alert-warning text-base">
                                <svg class="w-8 h-8 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                        d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z">
                                    </path>
                                </svg>
                                <div>
                                    <p>A new version of TimeCraft is available. Please update before the deadline to avoid disruption.</p>
                                </div>
                            </div>
                        `}
                        
                        <div class="bg-base-300 rounded-lg p-4 mt-4">
                            <p class="text-base font-semibold mb-3">📋 How to update:</p>
                            <code class="text-sm block bg-neutral text-neutral-content p-3 rounded font-mono">TimingCloseBeta.py -update -web</code>
                            <p class="text-xs opacity-70 mt-2">Click the Update button below or run the command manually.</p>
                        </div>
                    </div>
                    
                    <div class="modal-action flex-wrap gap-2">
                        ${isBlocking ? `
                            <button class="btn btn-success btn-lg" onclick="window.triggerAppUpdate()">
                                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4">
                                    </path>
                                </svg>
                                Update Now
                            </button>
                            <!-- Refresh button commented out - auto refresh is implemented
                            <button class="btn btn-primary btn-lg" onclick="location.reload()">
                                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15">
                                    </path>
                                </svg>
                                Refresh After Update
                            </button>
                            -->
                        ` : `
                            <button class="btn btn-ghost" onclick="window.dismissVersionWarning()">Remind me later (1 hour)</button>
                            <button class="btn btn-success" onclick="window.triggerAppUpdate()">
                                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4">
                                    </path>
                                </svg>
                                Update Now
                            </button>
                            <button class="btn btn-primary" onclick="location.reload()">I've Updated - Refresh</button>
                        `}
                    </div>
                </div>
                ${isBlocking ? '' : '<form method="dialog" class="modal-backdrop"><button>close</button></form>'}
            </dialog>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        const modal = document.getElementById('versionCheckModal');
        if (!isBlocking) {
            modal.showModal();
        }

        // For blocking modal, prevent any interaction with the page
        if (isBlocking) {
            document.body.style.overflow = 'hidden';
            // Block keyboard navigation
            document.addEventListener('keydown', preventInteraction, true);
        }
    }

    function preventInteraction(e) {
        // Only allow Tab within the modal for blocking state
        if (e.key === 'Escape') {
            e.preventDefault();
            e.stopPropagation();
        }
    }

    /**
     * Global function to dismiss warning
     */
    window.dismissVersionWarning = function() {
        dismissForOneHour();
        const modal = document.getElementById('versionCheckModal');
        if (modal) {
            modal.close();
            modal.remove();
        }
    };

    /**
     * Global function to trigger application update
     * Calls the backend API which will replace the current process
     */
    window.triggerAppUpdate = async function() {
        const btn = event.target.closest('button');
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = `
                <span class="loading loading-spinner loading-sm mr-2"></span>
                Updating...
            `;
        }

        try {
            console.log('[VersionCheck] Triggering update...');
            const response = await fetch('/api/version/update', { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                console.log('[VersionCheck] Update initiated:', data.message);
                // Show message that app is restarting
                if (btn) {
                    btn.innerHTML = `
                        <span class="loading loading-spinner loading-sm mr-2"></span>
                        Restarting...
                    `;
                }
                // Start polling for server to come back up
                waitForServerAndReload();
            } else {
                throw new Error(data.message || 'Update failed');
            }
        } catch (error) {
            console.error('[VersionCheck] Update failed:', error);
            alert('Failed to trigger update: ' + error.message + '\n\nPlease run manually:\nTimingCloseBeta.py -update -web');
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = `
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                            d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4">
                        </path>
                    </svg>
                    Update Now
                `;
            }
        }
    };

    /**
     * Poll server until it's back up, then reload the page
     */
    function waitForServerAndReload() {
        const modal = document.getElementById('versionCheckModal');
        let statusText = null;
        
        // Add status message to modal if exists
        if (modal) {
            const modalBox = modal.querySelector('.modal-box');
            if (modalBox) {
                statusText = document.createElement('div');
                statusText.className = 'alert alert-info mt-4';
                statusText.innerHTML = `
                    <span class="loading loading-spinner loading-sm"></span>
                    <span>Waiting for server to restart... Page will refresh automatically.</span>
                `;
                modalBox.appendChild(statusText);
            }
        }

        let attempts = 0;
        const maxAttempts = Infinity; // Unlimited attempts until server is back
        let pollInterval = 1000; // Check every 1 second initially

        const checkServer = async () => {
            attempts++;
            const ts = new Date().toISOString();
            console.log(`[VersionCheck] [${ts}] Attempt ${attempts}/${maxAttempts}: checking /api/version/check ...`);

            try {
                const response = await fetch('/api/version/check', {
                    method: 'GET',
                    cache: 'no-store'
                });
                console.log(`[VersionCheck] /api/version/check status=${response.status} ok=${response.ok}`);
                if (response.ok) {
                    console.log('[VersionCheck] Server is back! Reloading page...');
                    if (statusText) {
                        statusText.innerHTML = `
                            <svg class="w-5 h-5 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                            </svg>
                            <span>Server is back! Reloading...</span>
                        `;
                        statusText.className = 'alert alert-success mt-4';
                    }
                    // Small delay so user sees the success message
                    setTimeout(() => location.reload(), 500);
                    return;
                } else {
                    // Fallback: try root path in case /api/version/check isn't wired yet
                    try {
                        console.log('[VersionCheck] Fallback: checking / ...');
                        const rootResp = await fetch('/', { method: 'GET', cache: 'no-store' });
                        console.log(`[VersionCheck] / status=${rootResp.status} ok=${rootResp.ok}`);
                        if (rootResp.ok) {
                            console.log('[VersionCheck] Root path reachable. Reloading page...');
                            setTimeout(() => location.reload(), 500);
                            return;
                        }
                    } catch (fallbackErr) {
                        console.log('[VersionCheck] Fallback root check failed:', fallbackErr);
                    }
                }
            } catch (e) {
                console.log('[VersionCheck] Fetch to /api/version/check failed:', e);
            }

            // Exponential backoff after 60 attempts to reduce pressure
            if (attempts === 60) {
                pollInterval = 2000; // 2s
                console.log('[VersionCheck] Increasing poll interval to 2s');
            } else if (attempts === 120) {
                pollInterval = 5000; // 5s
                console.log('[VersionCheck] Increasing poll interval to 5s');
            }

            if (attempts < maxAttempts) {
                setTimeout(checkServer, pollInterval);
            } else {
                console.log('[VersionCheck] Timeout waiting for server after', maxAttempts, 'attempts');
                if (statusText) {
                    statusText.innerHTML = `
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        <span>Server taking longer than expected. <a href="#" onclick="location.reload()" class="link">Click to refresh manually</a></span>
                    `;
                    statusText.className = 'alert alert-warning mt-4';
                }
            }
        };

        // Start polling after a short delay (give server time to start shutting down)
        setTimeout(checkServer, 2000);
    }

    /**
     * Global function to force a version check (clears cache)
     */
    window.forceVersionCheck = async function() {
        localStorage.removeItem(STORAGE_KEY);
        localStorage.removeItem(DISMISSED_KEY);
        await checkVersion(true); // force show modal
    };

    /**
     * Perform version check
     * @param {boolean} forceShowModal - If true, show modal even if dismissed
     */
    async function checkVersion(forceShowModal = false) {
        console.log('[VersionCheck] Checking version...');

        try {
            const response = await fetch('/api/version/check');
            if (!response.ok) {
                console.warn('[VersionCheck] API error:', response.status);
                return;
            }

            const data = await response.json();
            console.log('[VersionCheck] Result:', data);

            // Always update badge with current version
            updateVersionBadge(data.local_version, data.is_outdated);

            // Record that we checked
            localStorage.setItem(STORAGE_KEY, Date.now().toString());

            // Check if version changed (user just updated) - show changelog
            if (checkVersionChanged(data.local_version)) {
                console.log('[VersionCheck] Version changed! Showing changelog...');
                await showChangelogModal(data.local_version);
                return; // Don't show update modal if we just updated
            }

            if (data.is_outdated) {
                // Clear dismissed state if we now must update (past deadline)
                if (data.must_update) {
                    localStorage.removeItem(DISMISSED_KEY);
                    showVersionModal(data);
                } else if (forceShowModal || shouldShowModal()) {
                    showVersionModal(data);
                }
            }
        } catch (error) {
            console.error('[VersionCheck] Failed:', error);
            // Don't block user if check fails - just log and continue
        }
    }

    /**
     * Auto-check version immediately on page load
     */
    function scheduleAutoCheck() {
        console.log('[VersionCheck] Running version check...');
        checkVersion(false);
    }

    // Run check when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', scheduleAutoCheck);
    } else {
        scheduleAutoCheck();
    }

})();
