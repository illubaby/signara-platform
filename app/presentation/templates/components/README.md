# Reusable Template Components

This directory contains reusable Jinja2 template components (macros) that ensure consistent styling across all pages in the TimeCraft Platform application.

## Available Components

### 1. `page_container.html`
**Purpose**: Provides consistent page-level container with proper spacing.

**Usage**:
```jinja
{% from 'components/page_container.html' import page_container %}

{% call page_container() %}
  <!-- Your page content goes here -->
{% endcall %}
```

**Styling**: 
- Creates a flex column layout with `gap-6` spacing
- Ensures consistent margins and padding across all pages

---

### 2. `page_header.html`
**Purpose**: Provides consistent page title and description styling.

**Usage**:
```jinja
{% from 'components/page_header.html' import page_header %}

{{ page_header('Page Title', 'Optional description text goes here.') }}
```

**Parameters**:
- `title` (required): The main page title (h1)
- `description` (optional): Subtitle or description text

**Styling**:
- Title: `text-3xl font-bold mb-2`
- Description: `text-sm opacity-80`

---

### 3. `execution_output.html`
**Purpose**: Reusable component for displaying script execution output with details.

**Usage**:
```jinja
{% from 'components/execution_output.html' import execution_output %}

{{ execution_output('Custom Title') }}
<!-- or just use default title -->
{{ execution_output() }}
```

**Parameters**:
- `title` (optional): Custom title for the execution output section (default: 'Execution Output')

**Features**:
- Collapsible output section
- Execution details (script path, working directory, status, elapsed time)
- Script output stream with ANSI color support
- Auto-scroll toggle
- Stop/Clear buttons

**Element IDs** (for JavaScript integration):
- `executionOutputGroup` - Main container
- `infoScriptPath` - Script path display
- `infoWorkingDir` - Working directory display
- `infoStatus` - Status indicator
- `infoElapsed` - Elapsed time display
- `scriptStream` - Output stream container
- `stopScriptBtn` - Stop button
- `clearScriptBtn` - Clear output button
- `autoscrollScript` - Auto-scroll checkbox

---

### 4. `file_browser_modal.html`
**Purpose**: Reusable file/directory browser modal for navigating project filesystem.

**Usage**:
```jinja
{% from 'components/file_browser_modal.html' import file_browser_modal %}

<!-- Include at the end of your page, before {% endcall %} -->
{{ file_browser_modal() }}
```

**JavaScript API**:
```javascript
// Open the file browser
window.FileBrowser.open({
  inputId: 'myInputField',      // ID of input to populate
  type: 'dir',                  // 'dir' or 'file'
  project: sel.project,         // Project name
  subproject: sel.subproject,   // Subproject name
  initialPath: 'sis',           // Optional: initial path relative to timing root
  callback: (fullPath) => {     // Optional: callback after selection
    console.log('Selected:', fullPath);
  }
});
```

**Features**:
- Breadcrumb navigation
- Directory/file browsing
- External symlink detection
- Full path resolution
- Auto-scroll for long paths
- Modal dialog interface

**Example - Add Browse Button**:
```html
<input id="pathInput" class="input input-bordered">
<button type="button" id="browseBtn" class="btn">Browse</button>

<script>
document.getElementById('browseBtn').addEventListener('click', () => {
  const sel = selState();
  if (!(sel.project && sel.subproject)) {
    alert('Select project first');
    return;
  }
  window.FileBrowser.open({
    inputId: 'pathInput',
    type: 'dir',
    project: sel.project,
    subproject: sel.subproject,
    initialPath: 'sis'
  });
});
</script>
```

---

## Complete Page Template Example

Here's a complete example showing how to use all components together:

```jinja
{% extends 'base.html' %}
{% from 'components/page_header.html' import page_header %}
{% from 'components/page_container.html' import page_container %}
{% from 'components/execution_output.html' import execution_output %}

{% block title %}My Page Title{% endblock %}

{% block content %}
{% call page_container() %}
  {{ page_header('My Page', 'This is a description of what this page does.') }}
  
  <!-- Your page-specific content -->
  <div class="card bg-base-100 shadow p-6">
    <h2 class="font-semibold mb-3">Section Title</h2>
    <!-- Content here -->
  </div>
  
  <!-- Optional: Include execution output component if needed -->
  {{ execution_output('Job Execution') }}
  
  <script>
    // Your JavaScript code
  </script>
{% endcall %}
{% endblock %}
```

---

## Benefits of Using These Components

1. **Consistency**: All pages look and feel the same
2. **Maintainability**: Change styling in one place, affects all pages
3. **DRY Principle**: Don't Repeat Yourself - write once, use everywhere
4. **Easy Updates**: Want to change the title size from `text-3xl` to `text-4xl`? Just edit `page_header.html` and all pages update!

---

## How to Make Global Style Changes

### Example 1: Change All Page Title Sizes
Edit `components/page_header.html`:
```jinja
<!-- Change from text-3xl to text-4xl -->
<h1 class="text-4xl font-bold mb-2">{{ title }}</h1>
```

### Example 2: Add More Spacing Between Page Sections
Edit `components/page_container.html`:
```jinja
<!-- Change from gap-6 to gap-8 -->
<div class="flex flex-col gap-8">
  {{ caller() }}
</div>
```

### Example 3: Change Description Color
Edit `components/page_header.html`:
```jinja
<!-- Change from opacity-80 to opacity-70 and add text-gray-600 -->
<p class="text-sm opacity-70 text-gray-600">{{ description }}</p>
```

---

## Pages Currently Using These Components

- ✅ **File Explorer** (`explorer.html`)
- ✅ **Timing SAF** (`timing_saf.html`)
- ✅ **Timing Post-Edit** (`timing_post_edit.html`)
- ✅ **Timing QC** (`timing_qc.html`)

---

## Adding a New Page

When creating a new page, always use these components:

```jinja
{% extends 'base.html' %}
{% from 'components/page_header.html' import page_header %}
{% from 'components/page_container.html' import page_container %}

{% block title %}New Page{% endblock %}

{% block content %}
{% call page_container() %}
  {{ page_header('New Page Title', 'Description here') }}
  
  <!-- Your content -->
  
{% endcall %}
{% endblock %}
```

This ensures your new page automatically matches the style of all existing pages!
