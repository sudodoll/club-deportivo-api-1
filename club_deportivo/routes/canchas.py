from flask import Blueprint, jsonify, request

from ..constants import ERROR_CODE_INVALID_BODY, ERROR_CODE_CANCHA_NOT_FOUND
from ..utils import construir_error_api, construir_links_paginacion
from ..validators.canchas import (
    validar_id_cancha,
    validar_filtros_canchas,
    validar_parametros_disponibilidad,
)
from ..services import canchas as canchas_service

canchas_bp = Blueprint('canchas', __name__)


def _error_body_invalido():
    return jsonify(construir_error_api(
        code=ERROR_CODE_INVALID_BODY,
        message='Cuerpo de la solicitud invalido',
        description='El cuerpo debe ser un JSON valido con Content-Type application/json'
    )), 400


def _error_cancha_no_encontrada(id_cancha):
    return jsonify(construir_error_api(
        code=ERROR_CODE_CANCHA_NOT_FOUND,
        message='Cancha no encontrada',
        description=f"No existe una cancha con id '{id_cancha}'"
    )), 404


def _respuesta_listado(canchas, filtros_query, limit, offset, total):
    return jsonify({
        'canchas': canchas,
        '_links': construir_links_paginacion(
            request.base_url, filtros_query, limit, offset, total
        ),
    })


def _filtros_de_query():
    return {
        clave: valor
        for clave, valor in request.args.items()
        if clave not in ('_limit', '_offset')
    }



@canchas_bp.route('/canchas/disponibles', methods=['GET'])
def get_canchas_disponibles():
    try:
        filtros, limit, offset = validar_parametros_disponibilidad(request.args)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    canchas, total = canchas_service.listar_canchas_disponibles(filtros, limit, offset)

    return _respuesta_listado(canchas, _filtros_de_query(), limit, offset, total)


@canchas_bp.route('/canchas', methods=['GET'])
def get_canchas():
    try:
        filtros, limit, offset = validar_filtros_canchas(request.args)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    canchas, total = canchas_service.listar_canchas(filtros, limit, offset)

    if not canchas:
        return '', 200

    return _respuesta_listado(canchas, _filtros_de_query(), limit, offset, total)


@canchas_bp.route('/canchas/<id>', methods=['GET'])
def get_cancha(id):
    try:
        id_cancha = validar_id_cancha(id)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    cancha = canchas_service.buscar_cancha_por_id(id_cancha)

    if not cancha:
        return _error_cancha_no_encontrada(id_cancha)

    return jsonify(cancha)


@canchas_bp.route('/canchas', methods=['POST'])
def post_cancha():
    body = request.get_json(silent=True)

    if not isinstance(body, dict):
        return _error_body_invalido()

    try:
        cancha = canchas_service.crear_cancha(body)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400

        return jsonify(e.args[0]), status

    return '', 201, {'Location': f"{request.base_url}/{cancha['id']}"}


@canchas_bp.route('/canchas/<id>', methods=['PATCH'])
def patch_cancha(id):
    try:
        id_cancha = validar_id_cancha(id)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    body = request.get_json(silent=True)

    if not isinstance(body, dict):
        return _error_body_invalido()

    try:
        canchas_service.actualizar_cancha_parcial(id_cancha, body)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400

        return jsonify(e.args[0]), status

    return '', 200


@canchas_bp.route('/canchas/<id>', methods=['DELETE'])
def delete_cancha(id):
    try:
        id_cancha = validar_id_cancha(id)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    try:
        canchas_service.eliminar_cancha_por_id(id_cancha)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400

        return jsonify(e.args[0]), status

    return '', 204

@canchas_bp.errorhandler(Exception)
def manejar_error_inesperado(error):
    """Responde en JSON cualquier error no previsto de estos endpoints."""
    logger.exception(f'Error inesperado en canchas: {error}')
 
    return jsonify(construir_error_api(
        code=ERROR_CODE_INTERNO,
        message='Error interno del servidor',
        description='Ocurrio un error inesperado al procesar la solicitud'
    )), 500


