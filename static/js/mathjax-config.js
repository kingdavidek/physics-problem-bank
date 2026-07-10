window.MathJax = {
  tex: {
    inlineMath: [['\\(', '\\)']],
    displayMath: [['\\[', '\\]']],
    processEscapes: true,
  },
  options: {
    skipHtmlTags: [
      'script', 'noscript', 'style', 'textarea', 'pre', 'code',
      'annotation', 'annotation-xml', 'svg',
    ],
    ignoreHtmlClass: 'tex2jax_ignore',
    processHtmlClass: 'tex2jax_process',
  },
};
