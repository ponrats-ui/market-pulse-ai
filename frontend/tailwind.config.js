/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        terminal: {
          bg: '#05070d', panel: '#0a101c', panel2: '#101827', border: '#1e2b3f', text: '#d9e7ff', muted: '#7e8da8', green: '#33d17a', red: '#ff5f6d', amber: '#f7c948', cyan: '#35d0ff'
        }
      },
      boxShadow: { glow: '0 0 28px rgba(53, 208, 255, 0.12)' }
    }
  },
  plugins: [],
};
