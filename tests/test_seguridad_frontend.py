from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_frontend_usa_renderizado_dom_seguro_en_vistas_dinamicas():
    javascript = '\n'.join(path.read_text(encoding='utf-8') for path in (PROJECT_ROOT / 'static' / 'js').glob('*.js'))

    assert 'innerHTML' not in javascript
    assert 'insertAdjacentHTML' not in javascript
    assert 'outerHTML' not in javascript
