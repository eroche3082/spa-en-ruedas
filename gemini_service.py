import os
import google.generativeai as genai
from PIL import Image
import io
import base64

# Configurar la API de Google Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

try:
    genai.configure(api_key=GEMINI_API_KEY)
    print("Cliente de Gemini inicializado correctamente.")
    
    # Verificar modelos disponibles
    models = genai.list_models()
    gemini_models = [model.name for model in models if "gemini" in model.name]
    print(f"Modelos Gemini disponibles: {gemini_models}")
    
    # Se usará 'gemini-1.5-pro' para texto y multimedia
    gemini_model = genai.GenerativeModel('gemini-1.5-pro')
except Exception as e:
    print(f"Error al inicializar Gemini: {str(e)}")
    gemini_model = None

def generar_respuesta_gemini(mensaje, historial=None, imagen_base64=None):
    """
    Genera una respuesta utilizando Google Gemini.
    
    Args:
        mensaje (str): El mensaje del usuario
        historial (list, optional): Historial previo de la conversación
        imagen_base64 (str, optional): Imagen en formato base64
        
    Returns:
        dict: Respuesta de la IA con el texto generado
    """
    if gemini_model is None:
        return {
            "success": False,
            "mensaje": "Lo siento, el servicio de Gemini no está disponible en este momento.",
            "error": "Cliente no inicializado",
            "source": "fallback"
        }
    
    try:
        # Preparar el contexto del sistema
        system_prompt = "Eres un asistente virtual de 'Spa en Ruedas', un servicio de spa móvil. Proporcionas información sobre servicios, precios y ayudas con reservas. Eres amable, profesional y hablas siempre en español. No menciones que eres una IA. Actúa como si fueras un miembro del personal de Spa en Ruedas."
        
        # Preparar la conversación
        chat = gemini_model.start_chat(history=[])
        
        # Añadir historial si existe
        if historial:
            for msg in historial:
                if msg['role'] == 'user':
                    chat.send_message(msg['content'])
                elif msg['role'] == 'assistant':
                    # No podemos enviar mensajes como asistente, pero mantenemos el contexto
                    pass
        
        # Si hay una imagen, procesarla
        if imagen_base64:
            try:
                # Decodificar la imagen base64
                image_data = base64.b64decode(imagen_base64.split(",")[1] if "," in imagen_base64 else imagen_base64)
                image = Image.open(io.BytesIO(image_data))
                
                # Enviar mensaje con imagen
                response = chat.send_message([system_prompt, image, mensaje])
            except Exception as img_error:
                print(f"Error al procesar la imagen: {str(img_error)}")
                # Si falla con la imagen, intentar solo con texto
                response = chat.send_message(f"{system_prompt}\n\nConsulta del cliente: {mensaje}")
        else:
            # Enviar solo texto
            response = chat.send_message(f"{system_prompt}\n\nConsulta del cliente: {mensaje}")
        
        # Obtener respuesta
        respuesta = response.text
        
        return {
            "success": True,
            "mensaje": respuesta,
            "source": "gemini"
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error al generar respuesta con Gemini: {str(e)}")
        print(f"Trace completo: {error_trace}")
        
        # Respuesta genérica para otros errores
        return {
            "success": False,
            "mensaje": "Lo siento, estoy teniendo problemas para responder en este momento. Por favor, intenta de nuevo más tarde o contacta con nosotros directamente.",
            "error": str(e),
            "source": "fallback"
        }