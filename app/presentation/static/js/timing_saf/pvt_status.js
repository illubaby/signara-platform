// Phase 2 extraction: PVT status badge rendering + run button styling.
// Provides pure functions so we can unit test mapping logic without DOM dependencies.
(function(global){
  'use strict';

  /**
   * Build HTML snippet for PVT status summary badges.
   * summary: {passed?, failed?, in_progress?, not_started?}
   */
  function buildPvtStatusHTML(summary){
    if(!summary || typeof summary !== 'object'){
      return `<span class='text-xs opacity-50'>-</span>`;
    }
    const s = summary;
    const badges = [];
    if(s.passed && s.passed > 0) badges.push(`<span class='badge badge-xs badge-success' title='${s.passed} Passed'>${s.passed}✓</span>`);
    if(s.failed && s.failed > 0) badges.push(`<span class='badge badge-xs badge-error' title='${s.failed} Failed'>${s.failed}✗</span>`);
    if(s.in_progress && s.in_progress > 0) badges.push(`<span class='badge badge-xs badge-warning' title='${s.in_progress} In Progress'>${s.in_progress}⟳</span>`);
    if(s.not_started && s.not_started > 0) badges.push(`<span class='badge badge-xs badge-ghost' title='${s.not_started} Not Started'>${s.not_started}○</span>`);
    if(!badges.length){
      return `<span class='text-xs opacity-50'>No PVTs</span>`;
    }
    return `<div class='flex flex-wrap gap-1'>${badges.join('')}</div>`;
  }

  /**
   * Determine run button class/text/icon based on summary object.
   * Returns {class, text, icon, title}
   */
  function computeRunButton(summary){
    let cls = 'btn-ghost hover:btn-primary';
    let text = 'Run';
    let icon = '';
    let title = 'Run SAF for this cell';

    if(summary && typeof summary === 'object'){
      const s = summary;
      const hasAny = (s.passed||0)+(s.failed||0)+(s.in_progress||0)+(s.not_started||0) > 0;
      if(hasAny){
        if(s.failed && s.failed > 0){
          cls = 'btn-error';
          text = 'Re-run';
          title = 'Failures present - re-run';
        } else if(s.in_progress && s.in_progress > 0){
          cls = 'btn-warning';
          text = 'Run';
          title = 'In Progress - continue run';
        } else if(s.not_started && s.not_started > 0){
          cls = 'btn-ghost hover:btn-primary';
          text = 'Run';
          title = 'Not Started - run';
        } else if(s.passed && s.passed > 0 && (s.failed||0)===0 && (s.in_progress||0)===0 && (s.not_started||0)===0){
          cls = 'btn-outline btn-success opacity-60';
          text = 'Completed ✓';
          title = 'All PVTs passed - click to re-run';
        }
      }
    }
    return {class: cls, text, icon, title};
  }

  // Export
  global.PvtStatus = { buildPvtStatusHTML, computeRunButton };

})(window);
