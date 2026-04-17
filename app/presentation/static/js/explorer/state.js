// Explorer state module
(function(){
  window.Explorer = window.Explorer || {};
  const currentExplorer = {
    selectedFile: null,
    selectedFilePath: null,
    dirty: false,
    basePath: '',
    basePathFromBackend: '',
    treeCache: new Map(),
    compareMode: false,
    compareFiles: [],
    isNewFile: false,
    newFilePath: null,
    contextMenuTarget: null,
    compareSelection: null,
    mode: 'project',
    globalRoot: ''
  };
  window.Explorer.state = { currentExplorer };
})();