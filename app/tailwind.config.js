/** Tailwind + DaisyUI configuration for offline build.
 * Run: npx tailwindcss -c tailwind.config.js -i presentation/static/css/input.css -o presentation/static/css/tailwind-daisyui.css --minify
 */
module.exports = {
  content: [
    './presentation/templates/**/*.html',
    './presentation/static/**/*.js'
  ],
  theme: { extend: {} },
  plugins: [require('daisyui')],
  // Optional DaisyUI theme config (can customize later)
  daisyui: {
    themes: ["corporate", "dark", "night"],
  }
};
