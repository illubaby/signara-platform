/**
 * File Editor functionality for layout forms
 * Allows inline editing of file contents directly from form inputs
 */

/**
 * Load file content from server into editor textarea
 * @param {string} fieldName - The form field name (also used as element ID)
 */
window.loadFileContent = async function(fieldName) {
  const filePathInput = document.getElementById(fieldName);
  const editorTextarea = document.getElementById(`editor-${fieldName}`);
  const statusDiv = document.getElementById(`editor-status-${fieldName}`);

  if (!filePathInput || !editorTextarea || !statusDiv) {
    console.error(`[loadFileContent] Missing elements for field: ${fieldName}`);
    return;
  }

  const filePath = filePathInput.value.trim();
  if (!filePath) {
    statusDiv.innerHTML = '<span class="text-warning">⚠ Please enter a file path first</span>';
    return;
  }

  statusDiv.innerHTML = '<span class="loading loading-spinner loading-xs"></span> Loading...';

  try {
    const response = await fetch('/api/files/read', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: filePath })
    });

    const result = await response.json();

    if (response.ok && result.content !== undefined) {
      editorTextarea.value = result.content;
      statusDiv.innerHTML = '<span class="text-success">✓ File loaded</span>';
      setTimeout(() => { statusDiv.innerHTML = ''; }, 3000);
    } else {
      const errorMsg = result.detail || result.error || 'Failed to read file';
      statusDiv.innerHTML = `<span class="text-error">✗ ${errorMsg}</span>`;
    }
  } catch (error) {
    console.error('[loadFileContent] Error:', error);
    statusDiv.innerHTML = `<span class="text-error">✗ Network error: ${error.message}</span>`;
  }
};

/**
 * Save editor textarea content back to file on server
 * @param {string} fieldName - The form field name (also used as element ID)
 */
window.saveFileContent = async function(fieldName) {
  const filePathInput = document.getElementById(fieldName);
  const editorTextarea = document.getElementById(`editor-${fieldName}`);
  const statusDiv = document.getElementById(`editor-status-${fieldName}`);

  if (!filePathInput || !editorTextarea || !statusDiv) {
    console.error(`[saveFileContent] Missing elements for field: ${fieldName}`);
    return;
  }

  const filePath = filePathInput.value.trim();
  if (!filePath) {
    statusDiv.innerHTML = '<span class="text-warning">⚠ Please enter a file path first</span>';
    return;
  }

  const content = editorTextarea.value;

  statusDiv.innerHTML = '<span class="loading loading-spinner loading-xs"></span> Saving...';

  try {
    const response = await fetch('/api/files/write', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: filePath, content: content })
    });

    const result = await response.json();

    if (response.ok) {
      statusDiv.innerHTML = '<span class="text-success">✓ File saved</span>';
      setTimeout(() => { statusDiv.innerHTML = ''; }, 3000);
    } else {
      const errorMsg = result.detail || result.error || 'Failed to write file';
      statusDiv.innerHTML = `<span class="text-error">✗ ${errorMsg}</span>`;
    }
  } catch (error) {
    console.error('[saveFileContent] Error:', error);
    statusDiv.innerHTML = `<span class="text-error">✗ Network error: ${error.message}</span>`;
  }
};
