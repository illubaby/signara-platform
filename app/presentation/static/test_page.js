(function () {
  function init() {
    const button = document.getElementById('fib-toggle');
    const list = document.getElementById('fib-list');

    if (!button || !list) return;

    function setVisible(visible) {
      list.classList.toggle('hidden', !visible);
      button.textContent = visible ? 'Hide Fibonacci' : 'Show Fibonacci';
      button.setAttribute('aria-expanded', visible ? 'true' : 'false');
    }

    // Start hidden
    setVisible(false);

    button.addEventListener('click', () => {
      const isHidden = list.classList.contains('hidden');
      setVisible(isHidden);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
