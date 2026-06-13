import React from 'react';
import { render, screen } from '@testing-library/react';
import LLMRender from '../src/index.jsx';

test('renders markdown headings', () => {
  render(<LLMRender markdown="# Title" />);
  expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Title');
});

test('renders inline LaTeX', () => {
  render(<LLMRender markdown="Inline $E=mc^2$ test" />);
  const katexSpan = screen.getByText('E=mc^2', { selector: 'span.katex' });
  expect(katexSpan).toBeInTheDocument();
});

test('renders display LaTeX', () => {
  render(<LLMRender markdown="$$\\int_{0}^{1} x dx$$" />);
  const katexDiv = screen.getByText('∫₀¹xdx', { selector: 'div.katex' });
  expect(katexDiv).toBeInTheDocument();
});
