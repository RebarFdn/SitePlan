/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "../siteplan/**/*.{py, js, html}",
    "../siteplan/modules/**/*.{py, js, html}",
    "../templates/**/*.{html, js}",
    
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require("rippleui")
  ],
}

