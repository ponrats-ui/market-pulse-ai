/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        terminal: {
          bg: '#05070d', panel: '#0a101c', panel2: '#101827', border: '#1e2b3f', text: '#d9e7ff', muted: '#7e8da8', green: '#33d17a', red: '#ff5f6d', amber: '#f7c948', cyan: '#35d0ff'
        },
        mp: {
          bg: '#05070d',
          bg2: '#08111f',
          card: '#0a101c',
          elevated: '#101827',
          border: '#1e2b3f',
          divider: '#26364f',
          text: '#f4f8ff',
          text2: '#c6d3e6',
          muted: '#8ea0ba',
          meta: '#6f8099',
          positive: '#39e58d',
          negative: '#ff6678',
          warning: '#f5b84b',
          neutral: '#8ca3bd',
          info: '#38bdf8',
          ai: '#b78cff',
          health: '#34d399',
          risk: '#fb923c',
          news: '#38bdf8',
          selected: '#35d0ff',
          disabled: '#52627a'
        }
      },
      borderRadius: {
        card: '8px',
        control: '6px',
      },
      boxShadow: { glow: '0 0 28px rgba(53, 208, 255, 0.12)' }
    }
  },
  plugins: [],
};
