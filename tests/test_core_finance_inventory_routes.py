import base64
from decimal import Decimal

import pytest
from flask import session
from werkzeug.exceptions import RequestEntityTooLarge

import bd
from blueprints import finanzas_bp, generales_bp, inventario_bp
from tests.db_fakes import connection_with_results


def test_core_pages_and_health_states(
        client, authenticated_session, monkeypatch):
    authenticated_session(client)
    monkeypatch.setattr(
        generales_bp,
        'contar_alertas_inventario',
        lambda: {'criticas': 1, 'normales': 2},
    )
    assert client.get('/sidebar').status_code == 200
    assert client.get('/bienvenida').status_code == 200
    assert client.get('/confirmar-salir').status_code == 200

    successful = connection_with_results({'ok': 1})
    monkeypatch.setattr(bd, 'Conexion_BD', lambda: successful)
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}
    assert successful.closed is True

    unexpected = connection_with_results({'ok': 0})
    monkeypatch.setattr(bd, 'Conexion_BD', lambda: unexpected)
    assert client.get('/health').status_code == 503
    assert unexpected.closed is True

    monkeypatch.setattr(
        bd,
        'Conexion_BD',
        lambda: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    assert client.get('/health').status_code == 503


@pytest.mark.parametrize(
    ('payload', 'expected_status'),
    [
        ({}, 400),
        ({'pdf': 'abc', 'nombre': 'x.pdf', 'tipo': 'otro'}, 400),
        ({'pdf': 'abc', 'nombre': 'x.txt', 'tipo': 'ticket'}, 400),
        ({'pdf': 'not-base64!', 'nombre': 'x.pdf', 'tipo': 'ticket'}, 400),
    ],
)
def test_save_pdf_rejects_invalid_payloads(
        client, authenticated_session, payload, expected_status):
    authenticated_session(client)
    response = client.post('/api/guardar-pdf', json=payload)
    assert response.status_code == expected_status
    assert response.get_json()['success'] is False


def test_save_pdf_handles_storage_error(
        app, client, authenticated_session, monkeypatch, tmp_path):
    authenticated_session(client)
    app.config['PDF_TICKETS_FOLDER'] = str(tmp_path)
    monkeypatch.setattr(
        'builtins.open',
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError('disk error')),
    )
    response = client.post('/api/guardar-pdf', json={
        'pdf': base64.b64encode(b'%PDF-valid').decode('ascii'),
        'nombre': 'x.pdf',
        'tipo': 'ticket',
    })
    assert response.status_code == 500


def test_save_pdf_size_signature_success_and_request_limit(
        app, client, authenticated_session, monkeypatch, tmp_path):
    authenticated_session(client)
    app.config['PDF_TICKETS_FOLDER'] = str(tmp_path)

    monkeypatch.setattr(generales_bp, 'MAX_PDF_BYTES', 3)
    oversized = client.post('/api/guardar-pdf', json={
        'pdf': base64.b64encode(b'%PDF-').decode('ascii'),
        'nombre': 'x.pdf',
        'tipo': 'ticket',
    })
    assert oversized.status_code == 413

    monkeypatch.setattr(generales_bp, 'MAX_PDF_BYTES', 1024)
    invalid_signature = client.post('/api/guardar-pdf', json={
        'pdf': base64.b64encode(b'not-a-pdf').decode('ascii'),
        'nombre': 'x.pdf',
        'tipo': 'ticket',
    })
    assert invalid_signature.status_code == 400

    saved = client.post('/api/guardar-pdf', json={
        'pdf': base64.b64encode(b'%PDF-valid').decode('ascii'),
        'nombre': 'ticket.pdf',
        'tipo': 'ticket',
    })
    assert saved.status_code == 200
    assert saved.get_json()['success'] is True
    assert len(list(tmp_path.glob('ticket_*.pdf'))) == 1

    original_view = generales_bp.guardar_pdf.__wrapped__.__wrapped__
    with app.test_request_context('/api/guardar-pdf', method='POST', json={
        'pdf': 'valid-looking',
        'nombre': 'x.pdf',
        'tipo': 'ticket',
    }):
        monkeypatch.setattr(
            generales_bp.base64,
            'b64decode',
            lambda *args, **kwargs: (_ for _ in ()).throw(RequestEntityTooLarge()),
        )
        with pytest.raises(RequestEntityTooLarge):
            original_view()


def test_download_pdf_valid_and_invalid(
        app, client, authenticated_session, tmp_path):
    authenticated_session(client)
    app.config['PDF_TICKETS_FOLDER'] = str(tmp_path)
    (tmp_path / 'ticket.pdf').write_bytes(b'%PDF-valid')

    response = client.get('/api/pdfs/ticket/ticket.pdf')
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
    assert client.get('/api/pdfs/otro/ticket.pdf').status_code == 404
    assert client.get('/api/pdfs/ticket/ticket.txt').status_code == 404


def test_inventory_page_and_update_validation(
        client, authenticated_session, monkeypatch):
    authenticated_session(client, role='Administrador')
    monkeypatch.setattr(inventario_bp, 'obtener_productos_inventario', lambda: [])
    assert client.get('/inventario').status_code == 200

    invalid_payloads = [
        {},
        {'id': 1, 'stock': -1, 'stock_min': 1, 'stock_max': 2},
        {'id': 1, 'stock': 1, 'stock_min': 0, 'stock_max': 2},
        {'id': 1, 'stock': 1, 'stock_min': 1, 'stock_max': 0},
        {'id': 1, 'stock': 1, 'stock_min': 2, 'stock_max': 2},
        {'id': 1, 'stock': 1, 'stock_min': 3, 'stock_max': 2},
    ]
    for payload in invalid_payloads:
        response = client.post('/api/inventario/actualizar', json=payload)
        assert response.status_code == 400


def test_inventory_update_missing_success_failure_and_exception(
        client, authenticated_session, monkeypatch):
    authenticated_session(client, role='Administrador')
    payload = {'id': 1, 'stock': 5, 'stock_min': 1, 'stock_max': 10}

    monkeypatch.setattr(
        inventario_bp, 'obtener_producto_inventario_por_id', lambda product_id: None
    )
    assert client.post('/api/inventario/actualizar', json=payload).status_code == 404

    monkeypatch.setattr(
        inventario_bp,
        'obtener_producto_inventario_por_id',
        lambda product_id: {
            'Id': product_id,
            'stock': 5,
            'stock_minimo': 1,
            'stock_maximo': 10,
        },
    )
    response = client.post('/api/inventario/actualizar', json=payload)
    assert response.get_json()['message'] == 'No se realizaron cambios en el inventario'

    current_product = {
        'Id': 1,
        'stock': 4,
        'stock_minimo': 1,
        'stock_maximo': 10,
    }
    monkeypatch.setattr(
        inventario_bp,
        'obtener_producto_inventario_por_id',
        lambda product_id: current_product,
    )
    monkeypatch.setattr(inventario_bp, 'actualizar_stock_producto', lambda *args: True)
    response = client.post('/api/inventario/actualizar', json=payload)
    assert response.status_code == 200
    assert response.get_json()['success'] is True
    assert response.get_json()['message'] == 'Stock actualizado correctamente'

    current_product.update(stock=5, stock_minimo=2)
    response = client.post('/api/inventario/actualizar', json=payload)
    assert response.get_json()['message'] == 'Límites de stock actualizados correctamente'

    current_product.update(stock=4, stock_minimo=2)
    response = client.post('/api/inventario/actualizar', json=payload)
    assert response.get_json()['message'] == 'Inventario actualizado correctamente'

    monkeypatch.setattr(inventario_bp, 'actualizar_stock_producto', lambda *args: False)
    response = client.post('/api/inventario/actualizar', json=payload)
    assert response.status_code == 200
    assert response.get_json() == {
        'success': False,
        'message': 'Error al actualizar inventario',
    }

    monkeypatch.setattr(
        inventario_bp,
        'obtener_producto_inventario_por_id',
        lambda product_id: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    response = client.post('/api/inventario/actualizar', json=payload)
    assert response.status_code == 500


@pytest.mark.parametrize('value', ['bad', None, -1])
def test_finance_decimal_validation(value):
    with pytest.raises(ValueError):
        finanzas_bp._decimal_no_negativo(value, 'Campo')


def test_finance_date_range_validation():
    with pytest.raises(ValueError, match='Selecciona'):
        finanzas_bp._rango_fechas({})
    with pytest.raises(ValueError, match='no es válido'):
        finanzas_bp._rango_fechas({'fechaDesde': 'bad', 'fechaHasta': 'bad'})
    with pytest.raises(ValueError, match='anterior'):
        finanzas_bp._rango_fechas({
            'fechaDesde': '2026-01-02', 'fechaHasta': '2026-01-01'
        })
    start, end = finanzas_bp._rango_fechas({
        'fechaDesde': '2026-01-01', 'fechaHasta': '2026-01-02'
    })
    assert start < end


def test_finance_filter_cut_and_report_pages(
        client, authenticated_session, monkeypatch):
    authenticated_session(client, role='Administrador')
    totals = {
        'efectivo': Decimal('10.00'),
        'tarjeta': Decimal('20.00'),
        'transferencias': Decimal('30.00'),
    }
    monkeypatch.setattr(finanzas_bp, 'filtrar_ventas', lambda *args: totals)
    response = client.post('/filtrarVentas', json={
        'fechaDesde': '2026-01-01', 'fechaHasta': '2026-01-02'
    })
    assert response.status_code == 200

    assert client.post('/filtrarVentas', json={}).status_code == 400

    monkeypatch.setattr(finanzas_bp, 'obtener_todos_cortes', lambda: [])
    assert client.get('/corteCaja').status_code == 200
    monkeypatch.setattr(finanzas_bp, 'obtener_cortes_con_ganancia', lambda: [])
    assert client.get('/reporteFinanciero').status_code == 200


def test_get_cash_cut_route_all_results(
        client, authenticated_session, monkeypatch):
    authenticated_session(client, role='Administrador')
    monkeypatch.setattr(finanzas_bp, 'obtener_corte_por_id', lambda cut_id: {'id': cut_id})
    assert client.get('/api/corteCaja/1').get_json()['success'] is True
    monkeypatch.setattr(finanzas_bp, 'obtener_corte_por_id', lambda cut_id: None)
    assert client.get('/api/corteCaja/1').get_json()['success'] is False
    monkeypatch.setattr(
        finanzas_bp,
        'obtener_corte_por_id',
        lambda cut_id: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    assert client.get('/api/corteCaja/1').status_code == 500


def _cut_payload(**overrides):
    payload = {
        'fecha_hora_inicio': '2026-01-01T00:00:00',
        'fecha_hora_cierre': '2026-01-02T00:00:00',
        'total_contado': '60.00',
        'pagos_realizados': '10.00',
        'fondo': '5.00',
    }
    payload.update(overrides)
    return payload


def test_save_cash_cut_route_branches(
        app, client, authenticated_session, monkeypatch):
    authenticated_session(client, role='Administrador')
    totals = {
        'efectivo': Decimal('10.00'),
        'tarjeta': Decimal('20.00'),
        'transferencias': Decimal('30.00'),
    }
    monkeypatch.setattr(finanzas_bp, 'filtrar_ventas', lambda *args: totals)

    original_view = finanzas_bp.guardar_corte.__wrapped__.__wrapped__
    with app.test_request_context('/guardarCorteCaja', method='POST', json=_cut_payload()):
        session['rol'] = 'Administrador'
        response, status = original_view()
        assert status == 401

    authenticated_session(client, role='Administrador')
    assert client.post(
        '/guardarCorteCaja', json=_cut_payload(total_contado='59.00')
    ).status_code == 409
    assert client.post(
        '/guardarCorteCaja', json=_cut_payload(pagos_realizados='100.00')
    ).status_code == 400

    monkeypatch.setattr(
        finanzas_bp,
        'guardar_corte_caja',
        lambda *args: (True, 'ok', 7),
    )
    assert client.post('/guardarCorteCaja', json=_cut_payload()).get_json()['corte_id'] == 7
    monkeypatch.setattr(
        finanzas_bp,
        'guardar_corte_caja',
        lambda *args: (False, 'overlap', None),
    )
    assert client.post('/guardarCorteCaja', json=_cut_payload()).status_code == 409
    assert client.post('/guardarCorteCaja', json={}).status_code == 400

    monkeypatch.setattr(
        finanzas_bp,
        'filtrar_ventas',
        lambda *args: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    assert client.post('/guardarCorteCaja', json=_cut_payload()).status_code == 500


def test_search_cash_pdf_missing_not_found_and_error(
        app, client, authenticated_session, monkeypatch, tmp_path):
    authenticated_session(client, role='Administrador')
    missing = tmp_path / 'missing'
    app.config['PDF_CORTES_FOLDER'] = str(missing)
    response = client.get('/buscar_pdf_corte/2026-01-01/2026-01-02')
    assert response.get_json()['success'] is False

    app.config['PDF_CORTES_FOLDER'] = str(tmp_path)
    response = client.get('/buscar_pdf_corte/2026-01-01/2026-01-02')
    assert response.get_json()['success'] is False

    (tmp_path / 'corte_2026-01-01_2026-01-02.pdf').write_bytes(b'%PDF-valid')
    response = client.get('/buscar_pdf_corte/2026-01-01/2026-01-02')
    assert response.get_json()['success'] is True

    monkeypatch.setattr(
        finanzas_bp.os,
        'listdir',
        lambda path: (_ for _ in ()).throw(OSError('disk error')),
    )
    response = client.get('/buscar_pdf_corte/2026-01-01/2026-01-02')
    assert response.status_code == 500
