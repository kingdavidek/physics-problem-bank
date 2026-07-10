/**
 * Syntax highlighting for Python example blocks in the CS Python lesson.
 */
(function () {
  'use strict';

  var KEYWORDS = new Set([
    'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break',
    'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally',
    'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal',
    'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield',
  ]);

  var BUILTINS = new Set([
    'print', 'input', 'int', 'float', 'str', 'bool', 'type', 'len', 'range',
    'open', 'list', 'dict', 'set', 'tuple', 'abs', 'max', 'min', 'sum',
    'round', 'sorted', 'enumerate', 'zip', 'map', 'filter', 'isinstance',
  ]);

  function escapeHtml(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function span(cls, text) {
    return '<span class="' + cls + '">' + escapeHtml(text) + '</span>';
  }

  function highlightPython(source) {
    var out = [];
    var i = 0;
    var n = source.length;

    while (i < n) {
      var ch = source[i];

      if (ch === '#') {
        var cEnd = i;
        while (cEnd < n && source[cEnd] !== '\n') cEnd++;
        out.push(span('py-comment', source.slice(i, cEnd)));
        i = cEnd;
        continue;
      }

      if (ch === '"' || ch === "'") {
        var q = ch;
        var sEnd = i + 1;
        while (sEnd < n) {
          if (source[sEnd] === '\\') {
            sEnd += 2;
            continue;
          }
          if (source[sEnd] === q) {
            sEnd++;
            break;
          }
          sEnd++;
        }
        out.push(span('py-str', source.slice(i, sEnd)));
        i = sEnd;
        continue;
      }

      if (/[0-9]/.test(ch) || (ch === '.' && i + 1 < n && /[0-9]/.test(source[i + 1]))) {
        var numEnd = i;
        while (numEnd < n && /[0-9._]/.test(source[numEnd])) numEnd++;
        out.push(span('py-num', source.slice(i, numEnd)));
        i = numEnd;
        continue;
      }

      if (/[A-Za-z_]/.test(ch)) {
        var idEnd = i;
        while (idEnd < n && /[A-Za-z0-9_]/.test(source[idEnd])) idEnd++;
        var word = source.slice(i, idEnd);
        var next = source[idEnd];
        if (KEYWORDS.has(word)) {
          out.push(span('py-kw', word));
        } else if (BUILTINS.has(word)) {
          out.push(span('py-builtin', word));
        } else if (next === '(') {
          out.push(span('py-fn', word));
        } else {
          out.push(span('py-name', word));
        }
        i = idEnd;
        continue;
      }

      out.push(escapeHtml(ch));
      i++;
    }

    return out.join('');
  }

  function highlightBlock(codeEl) {
    if (codeEl.dataset.highlighted === '1') return;
    codeEl.innerHTML = highlightPython(codeEl.textContent);
    codeEl.dataset.highlighted = '1';
  }

  function init() {
    document.querySelectorAll('pre.py-snippet code').forEach(highlightBlock);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
