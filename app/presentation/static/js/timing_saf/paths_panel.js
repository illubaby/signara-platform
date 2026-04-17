// Timing SAF: Library Paths Panel with Collapse State Persistence
(function() {
  const collapseCheckbox = document.getElementById('pathsConfigCollapse');
  
  if (!collapseCheckbox) {
    console.warn('Paths panel collapse checkbox not found');
    return;
  }
  
  // Load saved state from localStorage (default: expanded/checked)
  const savedState = localStorage.getItem('pathsPanelCollapsed');
  const isCollapsed = savedState === 'true';
  
  // Set initial state (checkbox checked = expanded)
  collapseCheckbox.checked = !isCollapsed;
  
  // Save state when toggled
  collapseCheckbox.addEventListener('change', function() {
    localStorage.setItem('pathsPanelCollapsed', !this.checked);
  });
})();
