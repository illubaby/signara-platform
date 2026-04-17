// Floating Terminal Button & Sidebar Chatbot - Simple click handlers
(function(){
  function qs(id){ return document.getElementById(id); }
  
  // Floating terminal button (bottom-right)
  const floatingTerminalBtn = qs('floatingTerminalBtn');
  if (floatingTerminalBtn) {
    floatingTerminalBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      if (window.ConsolePanel) {
        window.ConsolePanel.toggle();
      }
    });
  }

  // Sidebar chatbot button
  const sidebarChatbotBtn = qs('sidebarChatbotBtn');
  if (sidebarChatbotBtn) {
    sidebarChatbotBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      window.open('https://myipg/chat?agentId=6985afe06077873d691afff2&categories=%257B%257D', '_blank');
    });
  }
})();
