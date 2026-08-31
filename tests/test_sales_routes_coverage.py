import pytest

from blueprints import ventas_bp


def test_sales_menu_and_order_pages(
        client, authenticated_session, monkeypatch):
    authenticated_session(client)
    monkeypatch.setattr(ventas_bp, 'obtener_productos_menu', lambda: [])
    monkeypatch.setattr(ventas_bp, 'obtener_metodos_pago', lambda: [])
    monkeypatch.setattr(ventas_bp, 'obtener_ordenes_pendientes', lambda: [])
    monkeypatch.setattr(ventas_bp, 'obtener_vendedores_activos', lambda: [])
    assert client.get('/menu').status_code == 200
    assert client.get('/ordenes').status_code == 200


def test_get_orders_success_and_error(
        client, authenticated_session, monkeypatch):
    authenticated_session(client)
    monkeypatch.setattr(
        ventas_bp, 'obtener_ordenes_pendientes', lambda: [{'Id': 1}]
    )
    assert client.get('/api/ordenes').get_json()['success'] is True
    monkeypatch.setattr(
        ventas_bp,
        'obtener_ordenes_pendientes',
        lambda: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    assert client.get('/api/ordenes').status_code == 500


def test_get_order_detail_found_missing_and_error(
        client, authenticated_session, monkeypatch):
    authenticated_session(client)
    monkeypatch.setattr(
        ventas_bp, 'obtener_detalle_orden', lambda order_id: [{'Id': 2}]
    )
    assert client.get('/api/ordenes/1/detalles').get_json()['success'] is True
    monkeypatch.setattr(ventas_bp, 'obtener_detalle_orden', lambda order_id: [])
    assert client.get('/api/ordenes/1/detalles').get_json()['success'] is False
    monkeypatch.setattr(
        ventas_bp,
        'obtener_detalle_orden',
        lambda order_id: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    assert client.get('/api/ordenes/1/detalles').status_code == 500


def test_update_order_state_rejects_invalid_requests(
        client, authenticated_session):
    authenticated_session(client)
    assert client.post(
        '/api/ordenes/1/estado', data='not-json', content_type='text/plain'
    ).status_code == 400
    assert client.post(
        '/api/ordenes/1/estado', json={'estado': 'Inventado'}
    ).status_code == 400


def test_update_order_state_missing_order(
        client, authenticated_session, monkeypatch):
    authenticated_session(client)
    monkeypatch.setattr(ventas_bp, 'obtener_estado_orden', lambda order_id: None)
    response = client.post(
        '/api/ordenes/1/estado', json={'estado': 'En proceso'}
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    ('current_state', 'new_state', 'expected_fragment'),
    [
        (3, 'Pendiente', 'ninguno'),
        (1, 'Completado', 'En proceso'),
    ],
)
def test_update_order_state_rejects_invalid_transition(
        client, authenticated_session, monkeypatch,
        current_state, new_state, expected_fragment):
    authenticated_session(client)
    monkeypatch.setattr(
        ventas_bp,
        'obtener_estado_orden',
        lambda order_id: {'estado_id': current_state},
    )
    response = client.post(
        '/api/ordenes/1/estado', json={'estado': new_state}
    )
    assert response.status_code == 200
    assert expected_fragment in response.get_json()['message']


def test_cancel_order_validates_reason(
        client, authenticated_session, monkeypatch):
    authenticated_session(client)
    monkeypatch.setattr(
        ventas_bp, 'obtener_estado_orden', lambda order_id: {'estado_id': 1}
    )
    response = client.post(
        '/api/ordenes/1/estado',
        json={'estado': 'Cancelado', 'motivo': 'x'},
    )
    assert response.status_code == 400


@pytest.mark.parametrize('cancelled', [False, True])
def test_cancel_order_results(
        client, authenticated_session, monkeypatch, cancelled):
    authenticated_session(client, user_id=9)
    monkeypatch.setattr(
        ventas_bp, 'obtener_estado_orden', lambda order_id: {'estado_id': 1}
    )
    captured = []
    monkeypatch.setattr(
        ventas_bp,
        'cancelar_orden',
        lambda *args: captured.append(args) or cancelled,
    )
    response = client.post('/api/ordenes/1/estado', json={
        'estado': 'Cancelado',
        'motivo': 'Pedido duplicado',
    })
    assert response.status_code == (200 if cancelled else 409)
    assert captured == [(1, 9, 'Pedido duplicado')]


@pytest.mark.parametrize('updated', [False, True])
def test_update_non_cancelled_order_results(
        client, authenticated_session, monkeypatch, updated):
    authenticated_session(client)
    monkeypatch.setattr(
        ventas_bp, 'obtener_estado_orden', lambda order_id: {'estado_id': 1}
    )
    monkeypatch.setattr(
        ventas_bp, 'actualizar_estado_orden', lambda *args: updated
    )
    response = client.post(
        '/api/ordenes/1/estado', json={'estado': 'En proceso'}
    )
    assert response.status_code == (200 if updated else 409)


def test_update_order_state_handles_error(
        client, authenticated_session, monkeypatch):
    authenticated_session(client)
    monkeypatch.setattr(
        ventas_bp,
        'obtener_estado_orden',
        lambda order_id: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    response = client.post(
        '/api/ordenes/1/estado', json={'estado': 'En proceso'}
    )
    assert response.status_code == 500


def test_sales_history_page_and_api(
        client, authenticated_session, monkeypatch):
    authenticated_session(client)
    monkeypatch.setattr(ventas_bp, 'obtener_vendedores_activos', lambda: [])
    assert client.get('/historial').status_code == 200
    monkeypatch.setattr(
        ventas_bp,
        'obtener_historial_ventas',
        lambda *args: ([{'Id': 1}], 2, 16),
    )
    response = client.get(
        '/api/historial-ventas?cliente=A&vendedor=B&fechaInicio=2026-01-01'
        '&fechaFin=2026-01-02&pagina=2&por_pagina=15'
    )
    body = response.get_json()
    assert body['success'] is True
    assert body['pagina_actual'] == 2
    assert body['total_paginas'] == 2


def test_sales_history_api_handles_error(
        client, authenticated_session, monkeypatch):
    authenticated_session(client)
    monkeypatch.setattr(
        ventas_bp,
        'obtener_historial_ventas',
        lambda *args: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    assert client.get('/api/historial-ventas').status_code == 500


def test_sale_detail_found_missing_and_error(
        client, authenticated_session, monkeypatch):
    authenticated_session(client)
    monkeypatch.setattr(
        ventas_bp,
        'obtener_venta_completa',
        lambda sale_id: ({'Id': sale_id}, [{'Id': 2}]),
    )
    assert client.get('/api/historial-ventas/1').get_json()['success'] is True
    monkeypatch.setattr(
        ventas_bp, 'obtener_venta_completa', lambda sale_id: (None, None)
    )
    assert client.get('/api/historial-ventas/1').get_json()['success'] is False
    monkeypatch.setattr(
        ventas_bp,
        'obtener_venta_completa',
        lambda sale_id: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    assert client.get('/api/historial-ventas/1').status_code == 500


def test_create_sale_rejects_invalid_or_empty_request(
        client, authenticated_session):
    authenticated_session(client)
    assert client.post(
        '/api/ventas/crear', data='not-json', content_type='text/plain'
    ).status_code == 400
    response = client.post('/api/ventas/crear', json={})
    assert response.get_json()['success'] is False


def _sale_payload():
    return {
        'cliente': 'Cliente',
        'mesa': '4',
        'productos': [{'id': 1, 'cantidad': 2}],
        'metodo_pago': 'EFECTIVO',
        'dinero_recibido': 100,
    }


def test_create_sale_success(client, authenticated_session, monkeypatch):
    authenticated_session(client)
    monkeypatch.setattr(
        ventas_bp,
        'procesar_venta_completa',
        lambda *args: (True, 'Venta registrada', {'venta_id': 8, 'total': 50}),
    )
    response = client.post('/api/ventas/crear', json=_sale_payload())
    assert response.get_json()['venta_id'] == 8


@pytest.mark.parametrize('include_stock', [False, True])
def test_create_sale_failure_details(
        client, authenticated_session, monkeypatch, include_stock):
    authenticated_session(client)
    details = {'productos_sin_stock': [1]} if include_stock else None
    monkeypatch.setattr(
        ventas_bp,
        'procesar_venta_completa',
        lambda *args: (False, 'No se pudo vender', details),
    )
    response = client.post('/api/ventas/crear', json=_sale_payload())
    assert response.status_code == 400
    assert ('productos_sin_stock' in response.get_json()) is include_stock


def test_create_sale_handles_error(
        client, authenticated_session, monkeypatch):
    authenticated_session(client)
    monkeypatch.setattr(
        ventas_bp,
        'procesar_venta_completa',
        lambda *args: (_ for _ in ()).throw(RuntimeError('database error')),
    )
    assert client.post('/api/ventas/crear', json=_sale_payload()).status_code == 500
