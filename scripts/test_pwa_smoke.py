"""M4 PWA smoke test — run: python scripts/test_pwa_smoke.py"""
import json
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
        if data is None:
            data = json.loads(r.data.decode())
        assert data['name'] == 'Problem Bank'
        assert data['display'] == 'standalone'
        assert data['scope'] == '/'
        assert data['start_url'] in ('/', '/?source=pwa')
        assert data.get('id') == '/'
        assert data.get('theme_color') == '#1a86d4'
        assert data.get('background_color') == '#f2f6fa'
        sizes = {icon['sizes'] for icon in data['icons']}
        assert '192x192' in sizes
        assert '512x512' in sizes
        assert any(icon.get('purpose') == 'maskable' for icon in data['icons'])
        shortcuts = data.get('shortcuts') or []
        assert len(shortcuts) >= 2
        assert any('/topics' in (s.get('url') or '') for s in shortcuts)

        r = client.get('/sw.js')
        assert r.status_code == 200, r.data
        sw = r.data.decode()
        assert 'STATIC_CACHE' in sw
        assert 'pb-v43' in sw
        # JS and CSS must stay network-first or ?v= cache-busts never land.
        assert 'isVersionedAsset' in sw
        assert '/static/css/tokens.css' in sw
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
        assert 'pwa-ios-hint' in html
        assert 'pwa-offline-bar' in html
        assert 'pwa-standalone' in html
        assert 'app-tab-bar' in html
        assert 'tab-bar.js' in html
        assert 'header-primary-nav' in html
        assert 'apple-mobile-web-app-capable' in html
        assert 'black-translucent' in html

        # U0.10 — every stylesheet linked by base.html must actually serve, and
        # the load order in the template must match the order asserted here.
        stylesheets = [
            'tokens.css', 'base.css', 'components.css', 'chrome.css',
            'practice.css', 'pages.css', 'responsive.css', 'diagrams.css',
            'lesson-assist.css',
        ]
        positions = [html.index(f'css/{name}') for name in stylesheets]
        assert positions == sorted(positions), 'stylesheet load order changed'
        assert '<style>' not in html, 'CSS belongs in static/css, not inline'

        for path in (
            '/static/icons/icon-192.png',
            '/static/icons/icon-512.png',
            '/static/icons/icon-maskable-512.png',
            '/static/js/pwa.js',
            '/static/js/sw.js',
            '/static/manifest.webmanifest',
            *(f'/static/css/{name}' for name in stylesheets),
        ):
            r = client.get(path)
            assert r.status_code == 200, path

        pwa = client.get('/static/js/pwa.js').data.decode()
        assert 'isStandalone' in pwa or 'display-mode: standalone' in pwa
        assert 'pwa_ios_hint_dismissed' in pwa

    print('PWA smoke tests passed.')


if __name__ == '__main__':
    main()
