# DaisyUI Usage Guide for TimeCraft Platform

## What is DaisyUI?

DaisyUI is a **component library** built on top of Tailwind CSS. It provides ready-to-use UI components using simple CSS class names - no JavaScript configuration needed!

---

## How DaisyUI is Loaded in This Project

### Location: `presentation/templates/base.html` (Line 7)

```html
<link href="https://cdn.jsdelivr.net/npm/daisyui@4.12.10/dist/full.min.css" 
      rel="stylesheet" type="text/css" />
<script src="https://cdn.tailwindcss.com"></script>
```

✅ **This means:**
- DaisyUI is loaded globally via CDN
- Every page that extends `base.html` automatically has access to DaisyUI
- No npm install, no build step, no imports needed
- Just use the CSS classes in your HTML templates!

---

## How to Use DaisyUI Components

### Step 1: Find a Component

Visit: **https://daisyui.com/components/**

Browse categories:
- Actions (Button, Dropdown, Modal, Swap)
- Data Display (Accordion, Card, Table, Badge)
- Navigation (Menu, Tabs, Breadcrumbs)
- Layout (Collapse, Divider, Drawer)
- And many more!

### Step 2: Copy the HTML

Each component page shows example code. Just copy it!

### Step 3: Paste into Your Template

Add it to any `.html` file in `presentation/templates/`

### Step 4: Customize

Modify classes or content to fit your needs.

---

## Complete Example: Collapse with Arrow

### The Code:
```html
<div class="collapse collapse-arrow bg-base-100 border border-base-300 shadow-lg rounded-lg">
  <input type="checkbox" id="pathsConfigCollapse" />
  <div class="collapse-title text-base font-bold bg-primary text-primary-content rounded-t-lg">
    📚 Library Paths Configuration
  </div>
  <div class="collapse-content bg-base-100">
    <p>Your content here!</p>
  </div>
</div>
```

### What Each Class Does:

| Class | Purpose |
|-------|---------|
| `collapse` | **Core component** - Makes the container collapsible |
| `collapse-arrow` | **Adds arrow icon** - Automatically shows ▼/▲ arrow |
| `collapse-title` | **Clickable header** - The part you click to toggle |
| `collapse-content` | **Hidden content** - Shows/hides when toggled |
| `bg-base-100` | Background color (from DaisyUI theme) |
| `border border-base-300` | Border styling |
| `shadow-lg` | Drop shadow |
| `rounded-lg` | Rounded corners |
| `bg-primary` | Primary color background |
| `text-primary-content` | Text color that contrasts with primary |

### How It Works (No JavaScript!):

1. **Checkbox controls state**: When checked = expanded, unchecked = collapsed
2. **CSS does the magic**: DaisyUI's CSS watches the checkbox state
3. **Arrow rotates**: Automatically handled by DaisyUI CSS
4. **Content shows/hides**: Automatically handled by DaisyUI CSS

---

## Other Useful DaisyUI Components

### 1. Button
```html
<button class="btn btn-primary">Primary Button</button>
<button class="btn btn-sm btn-outline">Small Outline</button>
```

### 2. Card
```html
<div class="card bg-base-100 shadow-xl">
  <div class="card-body">
    <h2 class="card-title">Card Title</h2>
    <p>Card content</p>
  </div>
</div>
```

### 3. Badge
```html
<span class="badge badge-primary">New</span>
<span class="badge badge-success">Success</span>
```

### 4. Modal
```html
<dialog id="myModal" class="modal">
  <form method="dialog" class="modal-box">
    <h3 class="font-bold text-lg">Modal Title</h3>
    <p>Modal content</p>
    <button class="btn">Close</button>
  </form>
</dialog>

<!-- Open with JavaScript: -->
<script>
  document.getElementById('myModal').showModal();
</script>
```

### 5. Tabs
```html
<div role="tablist" class="tabs tabs-lifted">
  <input type="radio" name="my_tabs" class="tab" checked />
  <div role="tabpanel" class="tab-content">Tab 1 content</div>
  
  <input type="radio" name="my_tabs" class="tab" />
  <div role="tabpanel" class="tab-content">Tab 2 content</div>
</div>
```

---

## Color System (Themes)

DaisyUI uses semantic color names:

| Class | Usage |
|-------|-------|
| `bg-primary` | Primary brand color |
| `bg-secondary` | Secondary color |
| `bg-accent` | Accent color |
| `bg-neutral` | Neutral gray |
| `bg-base-100` | Base background |
| `bg-base-200` | Slightly darker |
| `bg-base-300` | Even darker |
| `bg-success` | Green (success) |
| `bg-error` | Red (error) |
| `bg-warning` | Yellow (warning) |
| `bg-info` | Blue (info) |

Current theme: `corporate` (set in `base.html` line 2: `data-theme="corporate"`)

---

## When to Add Custom JavaScript

DaisyUI handles most interactions with CSS only, but you might need JavaScript for:

### ✅ Use Cases for Custom JS:
1. **State persistence** (save collapsed/expanded state to localStorage)
2. **Programmatic control** (open modal via button click)
3. **Dynamic content loading** (fetch data when expanding)
4. **Custom validation** (before allowing collapse/expand)

### Example: Collapse with localStorage
```javascript
const checkbox = document.getElementById('myCollapse');

// Load saved state
checkbox.checked = localStorage.getItem('collapsed') !== 'true';

// Save on change
checkbox.addEventListener('change', function() {
  localStorage.setItem('collapsed', !this.checked);
});
```

---

## Common Patterns in This Project

### Pattern 1: Collapsible Configuration Section
```html
<div class="collapse collapse-arrow bg-base-100 border border-base-300 shadow-lg rounded-lg">
  <input type="checkbox" id="configCollapse" />
  <div class="collapse-title text-base font-bold bg-primary text-primary-content rounded-t-lg">
    ⚙️ Configuration
  </div>
  <div class="collapse-content bg-base-100">
    <!-- Form fields here -->
  </div>
</div>
```
**Used in:** `timing_qa.html`, `timing_post_edit.html`, `timing_saf/_paths_panel.html`

### Pattern 2: Action Buttons
```html
<button id="runBtn" class="btn btn-sm btn-primary">Run</button>
<button class="btn btn-xs btn-outline">Cancel</button>
```
**Used everywhere:** All pages

### Pattern 3: Status Badge
```html
<span class="badge badge-success">Complete</span>
<span class="badge badge-warning">Pending</span>
```
**Used in:** Dashboard, cell tables

---

## Quick Reference

### To Use DaisyUI:
1. ✅ Already loaded globally in `base.html`
2. ✅ Just add class names to HTML
3. ✅ No imports, no configuration
4. ✅ Check docs: https://daisyui.com/components/

### To Add a New Component:
1. Visit DaisyUI docs
2. Copy HTML example
3. Paste into your template
4. Customize classes/content
5. Add JS only if you need custom behavior

### To Debug:
- Inspect element in browser DevTools
- Check if classes are applied
- Verify `base.html` is loaded
- Check for typos in class names

---

## Resources

- **Official Docs**: https://daisyui.com/
- **All Components**: https://daisyui.com/components/
- **Themes**: https://daisyui.com/docs/themes/
- **Customize**: https://daisyui.com/docs/customize/

---

## Examples from Our Project

See these files for reference:
- `presentation/templates/timing_qa.html` - Collapse with arrow
- `presentation/templates/timing_post_edit.html` - Collapse with arrow
- `presentation/templates/timing_saf/partials/_paths_panel.html` - Collapse with arrow
- `presentation/templates/base.html` - Buttons, badges, navigation
- `presentation/templates/components/execution_output.html` - Card component
