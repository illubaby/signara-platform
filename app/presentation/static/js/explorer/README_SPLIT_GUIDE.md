# Explorer JS Modularization Quick Guide

This document captures the incremental refactor plan for turning the large inline `<script>` block in `templates/explorer.html` into small, maintainable JS modules under `app/static/js/explorer/`.

## Target Modules
| Module | Purpose | Exports (suggested) |
|--------|---------|---------------------|
| config.js | Constants & maps | Explorer.config |
| utils.js | Pure helpers (fetch, format, etc.) | Explorer.utils.* |
| state.js | Mutable shared state object | Explorer.state.currentExplorer |
| resize.js | Panel resize + persistence | Explorer.resize.init() |
| editor.js | Monaco init & file/Excel rendering | Explorer.editor.* |
| tree.js | Directory tree building & events | Explorer.tree.* |
| menu.js | Context menu show/hide/actions | Explorer.menu.* |
| files.js | New file + save logic | Explorer.files.* |
| compare.js | Diff/compare mode handling | Explorer.compare.* |
| mode.js | Project vs global root & URL params | Explorer.mode.init() |
| bootstrap.js | DOM queries + orchestration | (runs on load) |

You can merge some modules if desired; the list above is the maximal separation.

## Incremental Extraction Steps
Follow these steps one at a time (This is important because  AI can't handle directly due to size limits (e.g., over [number] lines or complex structures) ), reloading the page after each to verify nothing breaks.

1. config.js (DONE)
   - Create namespace: `window.Explorer = window.Explorer || {};`
   - Add constants: STORAGE_KEY, ignoredNames, ignoredPatterns, iconMap, languageMap.
   - Insert `<script src="/static/js/explorer/config.js"></script>` before inline script.

2. utils.js (DONE)
   - Move: fetchJSON, escapeHtml, formatBytes, languageFor, shouldIgnoreEntry, getFileIcon, getDiffStats, copyToClipboard.
   - Attach as `Explorer.utils`.
   - In template destructure: `const { fetchJSON, ... } = Explorer.utils;`
   - Remove original inline copies.

3. state.js (DONE)
   - `currentExplorer` moved.
   - Exported via `Explorer.state.currentExplorer`.
   - Inline replaced with alias `const currentExplorer = Explorer.state.currentExplorer;`.

4. resize.js (DONE)
   - Panel drag handlers & persistence moved.
   - `Explorer.resize.init()` invoked from template.

5. editor.js (DONE)
   - Moved: Monaco loader IIFE, editor/diff state vars, setEditorContent, displayExcelFile, switchExcelSheet, loadFileByPath (now in module), and supporting Excel table recreation logic.
   - Exposed via `Explorer.editor.{initMonaco,setEditorContent,displayExcelFile,switchExcelSheet,loadFileByPath}` plus getters for monacoEditor/diff.
   - Template now imports `editor.js` and removes inline duplicates; bridges created so existing code referencing monacoEditor/monacoDiffEditor/monacoLoaded still work.

6. tree.js (DONE ✓)
   - Moved: loadDirectoryContents, createTreeNode, expandFolder, attachTreeEventListeners, initializeTree, collapseAllFolders, refreshFileTree, expandToPath.
   - Exported via `Explorer.tree` with all tree management functions.
   - Removed duplicate functions from explorer.html template.
   - Added tree.js script tag to explorer.html.
   - Note: showFolderInfo remains in template (uses DOM elements and helper functions); may be moved to a separate helpers module later.

7. menu.js (DONE ✓)
   - Moved: showContextMenu, hideContextMenu, context menu click handler and initialization logic.
   - Exported via `Explorer.menu.{showContextMenu, hideContextMenu, init}`.
   - Removed duplicate context menu code from explorer.html template (~130 lines).
   - Added menu.js script tag and initialization call.

8. files.js (DONE ✓)
   - Moved: handleNewFile, saveCurrentFile, and save button event listener.
   - Exported via `Explorer.files.{handleNewFile, saveCurrentFile, init}`.
   - Removed duplicate file handling code from explorer.html template (~50 lines).
   - Added files.js script tag and initialization call.

9. compare.js (DONE ✓)
   - Move: handleCompareSelection, compareFiles, loadDiffView, exitCompareMode.
   - Export `Explorer.compare`.

10. mode.js (DONE ✓)
    - Move: checkURLParameters, expandToPath wrapper, explorerMode change listener, global root set logic.
    - Export `Explorer.mode.init()` and call it in bootstrap.

11. bootstrap.js (DONE ✓)
    - Created: query all DOM elements once (`Explorer.dom = {...}`).
    - Calls init functions in safe order: resize.init, menu.init, files.init, mode.init, tree.initializeTree.
    - Attaches remaining event listeners (collapse, refresh, copy path, exit compare).
    - Exposes helper functions: getFullAbsolutePath, showFolderInfo via Explorer.helpers.
    - Removed all remaining inline script from explorer.html template (~200+ lines).

## Load Order (Global Namespace Version) ✅ ALL COMPLETE
```html
<script src="/static/js/explorer/config.js"></script>       <!-- DONE ✓ -->
<script src="/static/js/explorer/utils.js"></script>        <!-- DONE ✓ -->
<script src="/static/js/explorer/state.js"></script>        <!-- DONE ✓ -->
<script src="/static/js/explorer/resize.js"></script>       <!-- DONE ✓ -->
<script src="/static/js/explorer/editor.js"></script>       <!-- DONE ✓ -->
<script src="/static/js/explorer/tree.js"></script>         <!-- DONE ✓ -->
<script src="/static/js/explorer/menu.js"></script>         <!-- DONE ✓ -->
<script src="/static/js/explorer/files.js"></script>        <!-- DONE ✓ -->
<script src="/static/js/explorer/compare.js"></script>      <!-- DONE ✓ -->
<script src="/static/js/explorer/mode.js"></script>         <!-- DONE ✓ -->
<script src="/static/js/explorer/bootstrap.js"></script>    <!-- DONE ✓ -->
```

## Verification After Each Step
- No console errors.
- Tree loads & expands.
- File open & save works.
- Compare mode works.
- Resize persists.
- Global mode switch works.

If something fails, revert just the last step and re-check the moved code for forgotten references.

## Common Pitfalls
- Forgetting to remove old inline function duplicates (shadowing new ones).
- Accessing `currentExplorer` before state.js loaded.
- Monaco functions called before monacoLoaded flag—guard with checks.
- Missing newly added script tag order dependency.

## Optional Future Enhancements
- Convert to ES modules and bundle (esbuild/Vite) for fewer HTTP requests.
- Lazy-load Monaco & Excel-related code only when needed.
- Add simple event bus to decouple modules (`Explorer.events` with on/emit).
- Unit tests for utils (formatBytes, languageFor, getDiffStats).

## Quick Recovery Prompt
If context/memory is lost, you can re-issue this concise instruction:

"Reconstruct Explorer modularization: ensure config.js & utils.js exist; progressively move state, resize, editor, tree, menu, files, compare, mode logic into separate files under app/static/js/explorer, expose via window.Explorer namespaces, then create bootstrap.js to wire DOM and remove inline script from explorer.html." 

---
Safe to proceed step-by-step using this checklist.
