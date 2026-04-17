// Internal Timing v2 bootstrap
(function (global) {
  'use strict';

  global.addEventListener('DOMContentLoaded', () => {
    global.InternalTimingV2Run.init({
      onComplete: async () => {
        await global.InternalTimingV2Table.reloadRows();
      }
    });
    global.InternalTimingV2Table.init();
  });
})(window);
