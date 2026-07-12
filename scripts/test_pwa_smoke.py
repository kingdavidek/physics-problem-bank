"""M2 PWA smoke test — run: python scripts/test_pwa_smoke.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app  # noqa: E402


def main():
    with app.test_client() as client:
        r = client.get('/manifest.webmanifest')
        assert r.status_code == 200, r.data
        assert 'application/manifest+json' in (r.content_type or '')
        data = r.get_json(silent=True)
        # Flask may return as bytes for send_from_directory — parse if needed
        if data is None:
            import json
            data = json.loads(r.data.decode())
        assert data['name'] == 'Problem Bank'
        assert data['display'] == 'standalone'
        assert data['start_url'] == '/'
        assert any(icon['sizes'] == '192x192' for icon in data['icons'])

        r = client.get('/sw.js')
        assert r.status_code == 200, r.data
        assert 'serviceWorker' in r.data.decode() or 'STATIC_CACHE' in r.data.decode()
        assert r.headers.get('Service-Worker-Allowed') == '/'

        r = client.get('/offline')
        assert r.status_code == 200
        assert b'offline' in r.data.lower()

        r = client.get('/')
        assert r.status_code == 200
        html = r.data.decode()
        assert 'manifest.webmanifest' in html or 'web_manifest' in html or 'rel="manifest"' in html
        assert 'pwa.js' in html
        assert 'theme-color' in html
        assert 'pwa-install-banner' in html
        assert 'pwa-offline-bar' in html

        for path in (
            '/static/icons/icon-192.png',
            '/static/icons/icon-512.png',
            '/static/icons/icon-maskable-512.png',
            '/static/js/pwa.js',
            '/static/js/sw.js',
            '/static/manifest.webmanifest',
        ):
            r = client.get(path)
            assert r.status_code == 200, path

    print('PWA smoke tests passed.')


if __name__ == '__main__':
    main()
