import base64
import binascii
import os
import secrets
from datetime import datetime, timezone

from flask import Blueprint, render_template, request, jsonify, current_app, url_for, send_from_directory, session
from werkzeug.utils import secure_filename

from utils import login_required
from models.modelsInventario import contar_alertas_inventario
from extensions import limiter

core_bp = Blueprint('core', __name__)

MAX_PDF_BYTES = 5 * 1024 * 1024

@core_bp.route('/sidebar')
@login_required
def sidebar():
    return render_template('sidebar.html')

@core_bp.route('/bienvenida')
@login_required
def bienvenida():
    alertas = contar_alertas_inventario()
    return render_template('bienvenida.html', 
                        alertas_inventario=alertas['criticas'] + alertas['normales'],
                        alertas_criticas=alertas['criticas'],
                        alertas_normales=alertas['normales'])

@core_bp.route('/confirmar-salir')
@login_required
def confirmar_salir():
    return render_template('confirmar_salir.html')

@core_bp.route('/health')
def health():
    """Comprueba proceso y conexión básica sin exponer configuración interna."""
    from bd import Conexion_BD

    connection = None
    try:
        connection = Conexion_BD()
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1 AS ok')
            result = cursor.fetchone()
        if not result or result.get('ok') != 1:
            raise RuntimeError('Respuesta inesperada de la base de datos')
        return jsonify({'status': 'ok'}), 200
    except Exception:
        current_app.logger.exception('La comprobación de salud falló')
        return jsonify({'status': 'unavailable'}), 503
    finally:
        if connection is not None:
            connection.close()

@core_bp.route('/api/guardar-pdf', methods=['POST'])
@login_required
@limiter.limit('20 per minute')
def guardar_pdf():
    """Recibe un PDF en base64 desde el frontend y lo guarda en la carpeta correspondiente."""
    try:
        data = request.get_json(silent=True) or {}
        pdf_base64 = data.get('pdf')
        nombre_archivo = data.get('nombre', 'documento.pdf')
        tipo = data.get('tipo', 'ticket')  # 'ticket' o 'corte'

        if not isinstance(pdf_base64, str) or not pdf_base64:
            return jsonify({'success': False, 'message': 'No se recibió el PDF'}), 400

        carpetas = {'ticket': current_app.config.get('PDF_TICKETS_FOLDER'), 'corte': current_app.config.get('PDF_CORTES_FOLDER')}
        if tipo not in carpetas:
            return jsonify({'success': False, 'message': 'Tipo de documento no válido'}), 400

        nombre_archivo = secure_filename(str(nombre_archivo)) or 'documento.pdf'
        base_nombre, extension = os.path.splitext(nombre_archivo)
        if extension.lower() != '.pdf':
            return jsonify({'success': False, 'message': 'Solo se permiten archivos PDF'}), 400

        try:
            pdf_bytes = base64.b64decode(pdf_base64, validate=True)
        except (binascii.Error, ValueError):
            return jsonify({'success': False, 'message': 'El contenido PDF no es válido'}), 400

        if len(pdf_bytes) > MAX_PDF_BYTES:
            return jsonify({'success': False, 'message': 'El PDF excede el tamaño permitido'}), 413

        if not pdf_bytes.startswith(b'%PDF-'):
            return jsonify({'success': False, 'message': 'El archivo no tiene una firma PDF válida'}), 400

        carpeta = carpetas[tipo]
        marca_tiempo = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        nombre_unico = f'{base_nombre[:80]}_{marca_tiempo}_{secrets.token_hex(4)}.pdf'

        ruta_completa = os.path.join(carpeta, nombre_unico)

        with open(ruta_completa, 'xb') as f:
            f.write(pdf_bytes)

        return jsonify({
            'success': True,
            'nombre': nombre_unico,
            'url': url_for('core.descargar_pdf', tipo=tipo, nombre=nombre_unico),
        })
    except Exception:
        current_app.logger.exception('Error al guardar PDF')
        return jsonify({'success': False, 'message': 'No se pudo guardar el PDF'}), 500

@core_bp.route('/api/pdfs/<tipo>/<path:nombre>', methods=['GET'])
@login_required
def descargar_pdf(tipo, nombre):
    carpetas = {'ticket': current_app.config.get('PDF_TICKETS_FOLDER'), 'corte': current_app.config.get('PDF_CORTES_FOLDER')}
    carpeta = carpetas.get(tipo)
    nombre_seguro = secure_filename(nombre)
    if not carpeta or not nombre_seguro or nombre_seguro != nombre or not nombre.endswith('.pdf'):
        return jsonify({'success': False, 'message': 'Documento no válido'}), 404
    return send_from_directory(carpeta, nombre_seguro, mimetype='application/pdf', max_age=0)
