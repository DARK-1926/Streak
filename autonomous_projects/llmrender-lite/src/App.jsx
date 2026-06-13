import React, { useState } from 'react';
import LLMRender from './index.jsx';

export default function App() {
  const [md, setMd] = useState('# Hello\n\nInline math $a^2 + b^2 = c^2$ and display:\n\n$$\n\frac{1}{n}\sum_{i=1}^{n} x_i\n$$');

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <textarea
        rows={8}
        style={{ width: '100%', marginBottom: '1rem' }}
        value={md}
        onChange={(e) => setMd(e.target.value)}
      />
      <LLMRender markdown={md} />
    </div>
  );
}
