import base64
from decimal import Decimal

import pytest
from flask import session
from werkzeug.exceptions import RequestEntityTooLarge

import bd
from blueprints import finanzas_bp, generales_bp, inventario_bp
from tests.db_fakes import connection_with_results


def test_paginas_core_y_estados_de_salud(
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
def test_guardar_pdf_rechaza_solicitudes_invalidas(
        client, authenticated_session, payload, expected_status):
    authenticated_session(client)
    response = client.post('/api/guardar-pdf', json=payload)
    assert response.status_code == expected_status
    assert response.get_json()['success'] is False


def test_guardar_pdf_maneja_error_de_almacenamiento(
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


def test_guardar_pdf_tamano_firma_exito_y_limite_peticiones(
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


def test_descarga_pdf_valido_e_invalido(
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
        {'id': 1, 'stock': -1, 'stock_min': 1, 'stock_max': 2, 'motivo': 'Ajuste'},
        {'id': 1, 'stock': 1, 'stock_min': 0, 'stock_max': 2, 'motivo': 'Ajuste'},
        {'id': 1, 'stock': 1, 'stock_min': 1, 'stock_max': 0, 'motivo': 'Ajuste'},
        {'id': 1, 'stock': 1, 'stock_min': 2, 'stock_max': 2, 'motivo': 'Ajuste'},
        {'id': 1, 'stock': 1, 'stock_min': 3, 'stock_max': 2, 'motivo': 'Ajuste'},
        {'id': 1, 'stock': 1, 'stock_min': 1, 'stock_max': 2},
        {'id': 1, 'stock': 1, 'stock_min': 1, 'stock_max': 2, 'motivo': ''},
        {'id': 1, 'stock': 1, 'stock_min': 1, 'stock_max': 2, 'motivo': '   '},
    ]
    for payload in invalid_payloads:
        response = client.post('/api/inventario/actualizar', json=payload)
        assert response.status_code == 400

    resp_sin_motivo = client.post('/api/inventario/actualizar', json={'id': 1, 'stock': 1, 'stock_min': 1, 'stock_max': 2, 'motivo': '  '})
    assert resp_sin_motivo.status_code == 400
    assert resp_sin_motivo.get_json()['message'] == 'El motivo del ajuste es obligatorio'


def test_actualizacion_inventario_faltante_exito_fallo_y_excepcion(
        client, authenticated_session, monkeypatch):
    authenticated_session(client, role='Administrador')
    payload = {'id': 1, 'stock': 5, 'stock_min': 1, 'stock_max': 10, 'motivo': 'Ajuste de inventario'}

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


def test_finanzas_paginas_filtro_corte_y_reporte(
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
    monkeypatch.setattr(finanzas_bp, 'obtener_fecha_sugerida_inicio', lambda: (None, False))
    assert client.get('/corteCaja').status_code == 200
    monkeypatch.setattr(finanzas_bp, 'obtener_cortes_con_ganancia', lambda: [])
    assert client.get('/reporteFinanciero').status_code == 200


def test_ruta_obtener_corte_caja_todos_los_resultados(
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


def test_ruta_guardar_corte_caja_ramas(
        app, client, authenticated_session, monkeypatch):
    authenticated_session(client, role='Administrador')
    totals = {
        'efectivo': Decimal('10.00'),
        'tarjeta': Decimal('20.00'),
        'transferencias': Decimal('30.00'),
    }
    monkeypatch.setattr(finanzas_bp, 'filtrar_ventas', lambda *args: totals)
    monkeypatch.setattr(finanzas_bp, 'obtener_ultimo_corte', lambda: None)

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


def test_guardar_corte_caja_rechaza_discontinuidad(
        client, authenticated_session, monkeypatch):
    from datetime import datetime
    authenticated_session(client, role='Administrador')
    monkeypatch.setattr(
        finanzas_bp,
        'obtener_ultimo_corte',
        lambda: {'fecha_hora_cierre': datetime(2026, 1, 1, 12, 0)},
    )
    # Fecha de inicio no coincide con el cierre del último corte
    response = client.post(
        '/guardarCorteCaja',
        json=_cut_payload(fecha_hora_inicio='2026-01-01T15:00:00'),
    )
    assert response.status_code == 400
    assert 'El corte debe iniciar exactamente al cierre del último corte registrado' in response.get_json()['message']


def test_api_ultimo_corte_exito_y_error(client, authenticated_session, monkeypatch):
    from datetime import datetime
    authenticated_session(client, role='Administrador')
    monkeypatch.setattr(
        finanzas_bp,
        'obtener_fecha_sugerida_inicio',
        lambda: (datetime(2026, 10, 27, 18, 0), True),
    )
    monkeypatch.setattr(
        finanzas_bp,
        'obtener_ultimo_corte',
        lambda: {'Id': 1, 'fecha_hora_cierre': '2026-10-27T18:00:00'},
    )
    response = client.get('/api/corteCaja/ultimo')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['tiene_corte_previo'] is True
    assert data['fecha_inicio_sugerida'] == '2026-10-27T18:00'

    monkeypatch.setattr(
        finanzas_bp,
        'obtener_fecha_sugerida_inicio',
        lambda: (_ for _ in ()).throw(RuntimeError('db error')),
    )
    response = client.get('/api/corteCaja/ultimo')
    assert response.status_code == 500


def test_buscar_pdf_caja_faltante_no_encontrado_y_error(
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

    bad_date = client.get('/buscar_pdf_corte/invalid-date/2026-01-02')
    assert bad_date.status_code == 400
    assert bad_date.get_json()['success'] is False

    monkeypatch.setattr(
        finanzas_bp.os,
        'listdir',
        lambda path: (_ for _ in ()).throw(OSError('disk error')),
    )
    response = client.get('/buscar_pdf_corte/2026-01-01/2026-01-02')
    assert response.status_code == 500


def test_formato_helpers_csv():
    from decimal import Decimal
    from datetime import datetime

    assert finanzas_bp._formato_fecha_csv(None) == ''
    assert finanzas_bp._formato_fecha_csv('2026-01-01') == '2026-01-01'
    assert finanzas_bp._formato_fecha_csv(datetime(2026, 1, 1, 12, 0)) == '2026-01-01 12:00:00'
    assert finanzas_bp._formato_moneda_csv(None) == '0.00'
    assert finanzas_bp._formato_moneda_csv('invalido') == '0.00'
    assert finanzas_bp._formato_moneda_csv(Decimal('12.3')) == '12.30'
    assert finanzas_bp._formato_moneda_csv(0) == '0.00'
    assert finanzas_bp._formato_moneda_csv(-45.5) == '-45.50'


def test_exportar_cortes_excel_permisos(client, authenticated_session):
    # Sin autenticación
    response_unauth = client.get('/api/cortes/exportar-excel')
    assert response_unauth.status_code in (401, 302)

    # Rol Cajero (no administrador)
    authenticated_session(client, role='Cajero')
    response_cajero = client.get('/api/cortes/exportar-excel')
    assert response_cajero.status_code in (403, 302)

    response_alias_cajero = client.get('/exportarReporteFinancieroExcel')
    assert response_alias_cajero.status_code in (403, 302)


def test_exportar_cortes_excel_exito_y_contenido_csv(client, authenticated_session, monkeypatch):
    from datetime import datetime
    import csv
    import io

    authenticated_session(client, role='Administrador')

    cortes_mock = [
        {
            'Id': 10,
            'fecha_hora_inicio': datetime(2026, 5, 1, 8, 30, 0),
            'fecha_hora_cierre': datetime(2026, 5, 1, 16, 45, 0),
            'vendedor': 'José López',
            'total_ventas': Decimal('1500.50'),
            'total_efectivo': Decimal('1000.00'),
            'total_transferencias': Decimal('300.50'),
            'total_tarjeta': Decimal('200.00'),
            'total_contado': Decimal('1500.50'),
            'pagos_realizados': Decimal('250.00'),
            'fondo': Decimal('500.00'),
            'ganancia_o_perdida': Decimal('1250.50'),
        }
    ]
    monkeypatch.setattr(finanzas_bp, 'obtener_cortes_exportacion', lambda *args: cortes_mock)

    response = client.get('/api/cortes/exportar-excel')
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'

    disp = response.headers.get('Content-Disposition', '')
    assert 'attachment' in disp
    hoy_str = datetime.now().strftime('%Y%m%d')
    assert f'filename=Reporte_Cortes_Caja_{hoy_str}.csv' in disp

    # Verificar codificación utf-8-sig (BOM presente al inicio de los bytes)
    assert response.data.startswith(b'\xef\xbb\xbf')

    # Decodificar y verificar estructura CSV
    decoded_text = response.data.decode('utf-8-sig')
    reader = list(csv.reader(io.StringIO(decoded_text)))

    encabezados_esperados = [
        'ID', 'Fecha Inicio', 'Fecha Cierre', 'Vendedor',
        'Total Ventas', 'Efectivo', 'Transferencias', 'Tarjeta',
        'Total Contado', 'Pagos Realizados', 'Fondo', 'Ganancia/Pérdida'
    ]
    assert reader[0] == encabezados_esperados
    assert len(reader) == 2

    fila1 = reader[1]
    assert fila1[0] == '10'
    assert fila1[1] == '2026-05-01 08:30:00'
    assert fila1[2] == '2026-05-01 16:45:00'
    assert fila1[3] == 'José López'
    assert fila1[4] == '1500.50'
    assert fila1[5] == '1000.00'
    assert fila1[6] == '300.50'
    assert fila1[7] == '200.00'
    assert fila1[8] == '1500.50'
    assert fila1[9] == '250.00'
    assert fila1[10] == '500.00'
    assert fila1[11] == '1250.50'

    # Verificar también que la ruta alternativa funcione idénticamente
    alias_response = client.get('/exportarReporteFinancieroExcel')
    assert alias_response.status_code == 200
    assert alias_response.mimetype == 'text/csv'
    assert alias_response.data.startswith(b'\xef\xbb\xbf')


def test_exportar_cortes_excel_vacio_y_error(client, authenticated_session, monkeypatch):
    import csv
    import io

    authenticated_session(client, role='Administrador')

    # Caso lista vacía
    monkeypatch.setattr(finanzas_bp, 'obtener_cortes_exportacion', lambda *args: [])
    response = client.get('/api/cortes/exportar-excel')
    assert response.status_code == 200
    reader = list(csv.reader(io.StringIO(response.data.decode('utf-8-sig'))))
    assert len(reader) == 1  # Solo la cabecera
    assert 'Ganancia/Pérdida' in reader[0]

    # Caso con filtro de fechas válido
    response_fechas = client.get('/api/cortes/exportar-excel?fecha_desde=2026-01-01T00:00:00&fecha_hasta=2026-01-02T00:00:00')
    assert response_fechas.status_code == 200

    # Caso con fechas inválidas (debe degradar limpiamente y no explotar)
    response_fechas_invalidas = client.get('/api/cortes/exportar-excel?fecha_desde=invalid&fecha_hasta=bad')
    assert response_fechas_invalidas.status_code == 200

    # Caso error interno
    monkeypatch.setattr(
        finanzas_bp,
        'obtener_cortes_exportacion',
        lambda *args: (_ for _ in ()).throw(RuntimeError('error de BD')),
    )
    resp_error = client.get('/api/cortes/exportar-excel')
    assert resp_error.status_code == 500
    assert resp_error.get_json()['success'] is False

