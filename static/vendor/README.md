# Vendored front-end runtimes (S2.2)

These files are served from `/static/vendor/` so visitor IPs are not sent to jsDelivr.

| Path | Upstream | Version |
|---|---|---|
| `mathjax/tex-svg.js` | MathJax `es5/tex-svg.js` | 3.2.2 |
| `pyodide/*` | Pyodide `full` core (js, asm, wasm, stdlib zip, lockfile) | 0.25.0 |

Re-download:

```bash
python scripts/vendor_cdn_assets.py
```

Do not add the rest of the Pyodide package index (200+ MB). Core files are enough to start the interpreter; extra packages are not used.

`unsafe-eval` and `wasm-unsafe-eval` remain in the CSP because MathJax and Pyodide require them. That is an accepted, scoped exception (`docs/SECURITY_AND_GDPR.md` S2.1).
