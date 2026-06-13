# LLMRender Lite

A **10 KB** React component that renders Markdown with embedded LaTeX (KaTeX) without pulling in heavy markdown or math libraries.

## Features
- ✅ Markdown via **marked** (tiny, fast)
- ✅ LaTeX rendering via **KaTeX** (CSS‑only, no MathJax)
- ✅ Works as a React component `<LLMRender markdown="..." />`
- ✅ ES‑module build for tree‑shaking
- ✅ Zero runtime dependencies beyond React, marked and KaTeX (≈ 10 KB gzipped)
- ✅ Jest + Testing Library test suite

## Install
```bash
npm i llmrender-lite
```

## Usage
```jsx
import React from 'react';
import LLMRender from 'llmrender-lite';

const md = `# Title\n\nThis is inline math $E = mc^2$ and a block:\n\n$$\n\int_{a}^{b} f(x)dx\n$$`;

function App() {
  return <LLMRender markdown={md} />;
}
```

## Development
```bash
npm run dev        # start Vite dev server
npm run build      # produce lib files in /dist
npm run test       # run Jest tests
```

## License
MIT
