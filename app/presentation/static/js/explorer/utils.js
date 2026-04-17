// Explorer utility functions extracted from inline script
(function(){
  window.Explorer = window.Explorer || {};
  const cfg = window.Explorer.config;
  const utils = {};

  utils.fetchJSON = async function(url){
    const res = await fetch(url);
    if(!res.ok) throw new Error(await res.text());
    return res.json();
  };

  utils.escapeHtml = function(text){
    const map = { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#039;' };
    return text.replace(/[&<>"']/g, m => map[m]);
  };

  utils.formatBytes = function(bytes){
    if(bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes','KB','MB','GB'];
    const i = Math.floor(Math.log(bytes)/Math.log(k));
    return Math.round(bytes/Math.pow(k,i)*100)/100 + ' ' + sizes[i];
  };

  utils.languageFor = function(filename){
    const ext = filename.split('.').pop().toLowerCase();
    return cfg.languageMap[ext] || 'plaintext';
  };

  utils.shouldIgnoreEntry = function(name){
    if(cfg.ignoredNames.includes(name)) return true;
    return cfg.ignoredPatterns.some(p=>p.test(name));
  };

  utils.getFileIcon = function(filename){
    const ext = filename.split('.').pop().toLowerCase();
    return cfg.iconMap[ext] || '📄';
  };

  utils.getDiffStats = function(content1, content2){
    const lines1 = content1.split('\n').length;
    const lines2 = content2.split('\n').length;
    const diff = lines2 - lines1;
    if(diff === 0) return `${lines1} lines (same)`;
    if(diff > 0) return `+${diff} lines (${lines2} vs ${lines1})`;
    return `${diff} lines (${lines2} vs ${lines1})`;
  };

  utils.copyToClipboard = async function(text, onSuccess, onFail){
    try {
      await navigator.clipboard.writeText(text);
      if(onSuccess) onSuccess();
    } catch(err){
      // Fallback
      const ta = document.createElement('textarea');
      ta.value = text; ta.style.position='fixed'; ta.style.left='-9999px';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); if(onSuccess) onSuccess(); }
      catch(e){ if(onFail) onFail(e); }
      document.body.removeChild(ta);
    }
  };

  window.Explorer.utils = utils;
})();