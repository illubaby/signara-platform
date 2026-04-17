// Explorer configuration & constant maps
// Loaded first; attaches a namespace to window.
(function(){
  window.Explorer = window.Explorer || {};
  const cfg = {
    STORAGE_KEY: 'explorer-tree-width',
    ignoredNames: ['__pycache__', '.git', '.vscode', '.idea', 'node_modules', '.pytest_cache', '.mypy_cache'],
    ignoredPatterns: [/\.pyc$/, /\.pyo$/, /\.swp$/, /~$/],
    iconMap: {
      py:'🐍', sh:'📜', csh:'📜', tcl:'🔧', json:'📋', yml:'⚙️', yaml:'⚙️', md:'📝',
      log:'📊', txt:'📄', cfg:'⚙️', conf:'⚙️', js:'📜', html:'🌐', css:'🎨', xml:'📋',
      xlsx:'📊', xls:'📊', xlsm:'📊', csv:'📈'
    },
    languageMap: {
      py:'python', sh:'shell', csh:'shell', tcl:'tcl', json:'json', yml:'yaml', yaml:'yaml', md:'markdown', log:'log', txt:'plaintext',
      cfg:'ini', conf:'ini', js:'javascript', html:'html', css:'css', cpp:'cpp', c:'c', h:'c', hpp:'cpp', xml:'xml', sql:'sql'
    }
  };
  window.Explorer.config = cfg;
})();