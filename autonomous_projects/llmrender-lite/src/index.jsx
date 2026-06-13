import React, { useEffect, useRef } from 'react';
import { marked } from 'marked';
import katex from 'katex';
import 'katex/dist/katex.min.css';

/**
 * Convert LaTeX delimiters to KaTeX HTML.
 * Supports $...$ for inline and $$...$$ for display.
 */
function renderMath(text) {
  // Replace display math first
  const displayReplaced = text.replace(/\$\$(.+?)\$\$/gs, (_, expr) => {
    try {
      return katex.renderToString(expr, { displayMode: true, throwOnError: false });
    } catch {
      return expr;
    }
  });
  // Then inline math
  const inlineReplaced = displayReplaced.replace(/\$(.+?)\$/g, (_, expr) => {
    try {
      return katex.renderToString(expr, { displayMode: false, throwOnError: false });
    } catch {
      return expr;
    }
  });
  return inlineReplaced;
}

/**
 * LLMRender component
 * @param {Object} props
 * @param {string} props.markdown – Markdown string possibly containing LaTeX.
 */
export default function LLMRender({ markdown }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;
    // First, render LaTeX placeholders inside the markdown text
    const withMath = renderMath(markdown);
    // Then convert markdown to HTML
    const html = marked.parse(withMath);
    containerRef.current.innerHTML = html;
  }, [markdown]);

  return <div ref={containerRef} />;
}
