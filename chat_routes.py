from flask import Blueprint, request, jsonify, session
from ai_service import generar_respuesta_chat, respuestas_predefinidas
import uuid

# Crear el blueprint de chat
chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/enviar', methods=['POST'])
def enviar_mensaje():
    """
    Procesa un mensaje de chat del usuario y devuelve una respuesta.
    """
    data = request.json
    mensaje = data.get('mensaje', '')
    
    if not mensaje:
        return jsonify({
            'success': False,
            'error': 'Mensaje vacío'
        }), 400
    
    # Inicializar historial de chat si no existe
    if 'chat_id' not in session:
        session['chat_id'] = str(uuid.uuid4())
        session['chat_history'] = []
    
    # Añadir mensaje del usuario al historial
    session['chat_history'].append({
        'role': 'user',
        'content': mensaje
    })
    
    # Intentar obtener una respuesta predefinida primero (palabras clave importantes)
    respuesta_predefinida = respuestas_predefinidas(mensaje)
    
    # Verificar si es una respuesta predefinida para palabras clave importantes
    palabras_clave_importantes = ["hora", "precio", "costo", "reserva", "ubica", "canc", "cita", "telef", "contac"]
    es_pregunta_clave = any(palabra in mensaje.lower() for palabra in palabras_clave_importantes)
    
    if respuesta_predefinida and es_pregunta_clave:
        respuesta = {
            'success': True,
            'mensaje': respuesta_predefinida,
            'source': 'predefinida'
        }
    else:
        # Generar respuesta con IA para preguntas más complejas
        respuesta = generar_respuesta_chat(mensaje, session.get('chat_history', [])[:-1])
    
    # Si la respuesta fue exitosa, añadir al historial
    if respuesta['success']:
        session['chat_history'].append({
            'role': 'assistant',
            'content': respuesta['mensaje']
        })
        
        # Limitar el historial a los últimos 10 mensajes
        if len(session['chat_history']) > 10:
            session['chat_history'] = session['chat_history'][-10:]
    
    return jsonify(respuesta)

@chat_bp.route('/historial', methods=['GET'])
def obtener_historial():
    """
    Devuelve el historial de chat para la sesión actual.
    """
    historial = []
    
    # Convertir formato interno a formato para el cliente
    for mensaje in session.get('chat_history', []):
        historial.append({
            'role': mensaje['role'],
            'content': mensaje['content']
        })
    
    return jsonify({
        'success': True,
        'historial': historial,
        'chat_id': session.get('chat_id', '')
    })

@chat_bp.route('/reiniciar', methods=['POST'])
def reiniciar_chat():
    """
    Reinicia la sesión de chat actual.
    """
    session['chat_id'] = str(uuid.uuid4())
    session['chat_history'] = []
    
    return jsonify({
        'success': True,
        'mensaje': 'Chat reiniciado'
    })