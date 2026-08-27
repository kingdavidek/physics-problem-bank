"""Re-download MathJax 3.2.2 and Pyodide 0.25.0 core files into static/vendor/."""
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    'static/vendor/mathjax/tex-svg.js': 'https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js',
    'static/vendor/pyodide/pyodide.js': 'https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js',
    'static/vendor/pyodide/pyodide.asm.js': 'https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.asm.js',
    'static/vendor/pyodide/pyodide.asm.wasm': 'https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.asm.wasm',
    'static/vendor/pyodide/python_stdlib.zip': 'https://cdn.jsdelivr.net/pyodide/v0.25.0/full/python_stdlib.zip',
    'static/vendor/pyodide/pyodide-lock.json': 'https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide-lock.json',
}


def main():
    for dest, url in FILES.items():
        path = ROOT / dest
        path.parent.mkdir(parents=True, exist_ok=True)
        print('GET', url)
        urllib.request.urlretrieve(url, path)
        print(' ', path.relative_to(ROOT), path.stat().st_size)


if __name__ == '__main__':
    main()
