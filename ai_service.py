import os
import json
from openai import OpenAI

# Obtener la clave API de OpenAI de las variables de entorno
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("ADVERTENCIA: La clave de API de OpenAI no está configurada en las variables de entorno.")

try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("Cliente de OpenAI inicializado correctamente.")
except Exception as e:
    print(f"Error al inicializar el cliente de OpenAI: {str(e)}")
    client = None

def generar_respuesta_chat(mensaje, historial=None):
    """
    Genera una respuesta utilizando el modelo GPT de OpenAI.
    
    Args:
        mensaje (str): El mensaje del usuario
        historial (list, optional): Historial previo de la conversación
        
    Returns:
        dict: Respuesta de la IA con el texto generado
    """
    # Si el cliente no está disponible, usar respuestas predefinidas
    if client is None:
        respuesta = respuestas_predefinidas(mensaje)
        if respuesta:
            return {
                "success": True,
                "mensaje": respuesta,
                "source": "predefinida"
            }
        else:
            return {
                "success": False,
                "mensaje": "Lo siento, nuestro servicio de chat está experimentando problemas técnicos. Por favor, contáctanos directamente al teléfono 787-123-4567.",
                "error": "Cliente OpenAI no inicializado",
                "source": "fallback"
            }
    
    try:
        # Preparar el sistema de mensajes
        messages = [
            {"role": "system", "content": "Eres un asistente virtual de 'Spa en Ruedas', un servicio de spa móvil. "
                                          "Proporcionas información sobre servicios, precios y ayudas con reservas. "
                                          "Eres amable, profesional y hablas siempre en español. No menciones que eres una IA. "
                                          "Actúa como si fueras un miembro del personal de Spa en Ruedas."}
        ]
        
        # Añadir historial si existe
        if historial:
            messages.extend(historial)
            
        # Añadir mensaje actual del usuario
        messages.append({"role": "user", "content": mensaje})
        
        # Llamar a la API de OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",  # El modelo más nuevo de OpenAI
            messages=messages,
            max_tokens=300,
            temperature=0.7,
        )
        
        # Extraer la respuesta
        respuesta = response.choices[0].message.content
        
        return {
            "success": True,
            "mensaje": respuesta,
            "source": "openai"
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error al generar respuesta con OpenAI: {str(e)}")
        print(f"Trace completo: {error_trace}")
        
        # Verificar si la clave API es válida
        if "Invalid API key" in str(e):
            return {
                "success": False,
                "mensaje": "Lo siento, hay un problema con la configuración del servicio. Por favor, contacta con el administrador del sitio.",
                "error": "API key inválida",
                "source": "fallback"
            }
        
        # Respuesta genérica para otros errores
        return {
            "success": False,
            "mensaje": "Lo siento, estoy teniendo problemas para responder en este momento. Por favor, intenta de nuevo más tarde o contacta con nosotros directamente.",
            "error": str(e),
            "source": "fallback"
        }

def respuestas_predefinidas(mensaje):
    """
    Devuelve respuestas predefinidas para preguntas comunes.
    Se usa como fallback cuando la API de OpenAI no está disponible.
    
    Args:
        mensaje (str): El mensaje del usuario
        
    Returns:
        str: Una respuesta predefinida o una respuesta por defecto si no hay coincidencia
    """
    mensaje = mensaje.lower()
    
    respuestas = {
        "horario": "Nuestro horario de atención es de lunes a viernes de 9:00 AM a 7:00 PM y sábados de 10:00 AM a 5:00 PM.",
        "hora": "Nuestro horario de atención es de lunes a viernes de 9:00 AM a 7:00 PM y sábados de 10:00 AM a 5:00 PM.",
        "precio": "Nuestros precios varían según el servicio. Los masajes comienzan desde $50 y los tratamientos faciales desde $40. Puede consultar todos los precios en nuestra sección de servicios.",
        "costo": "Nuestros precios varían según el servicio. Los masajes comienzan desde $50 y los tratamientos faciales desde $40. Puede consultar todos los precios en nuestra sección de servicios.",
        "tarifa": "Nuestros precios varían según el servicio. Los masajes comienzan desde $50 y los tratamientos faciales desde $40. Puede consultar todos los precios en nuestra sección de servicios.",
        "reserva": "Puede hacer una reserva directamente en nuestro sitio web en la sección 'Reservar', o llamando al 787-555-1234.",
        "reservar": "Puede hacer una reserva directamente en nuestro sitio web en la sección 'Reservar', o llamando al 787-555-1234.",
        "cita": "Puede hacer una reserva directamente en nuestro sitio web en la sección 'Reservar', o llamando al 787-555-1234.",
        "cancelar": "Para cancelar una reserva, por favor utilice el código de confirmación que recibió al hacer su reserva en la sección 'Verificar Reserva', o llámenos al 787-555-1234 con al menos 24 horas de antelación.",
        "cancela": "Para cancelar una reserva, por favor utilice el código de confirmación que recibió al hacer su reserva en la sección 'Verificar Reserva', o llámenos al 787-555-1234 con al menos 24 horas de antelación.",
        "ubicacion": "Somos un spa móvil. Vamos a donde usted esté en San Juan, Bayamón, Carolina y ahora también en Ponce.",
        "donde": "Somos un spa móvil. Vamos a donde usted esté en San Juan, Bayamón, Carolina y ahora también en Ponce.",
        "dirección": "Somos un spa móvil. Vamos a donde usted esté en San Juan, Bayamón, Carolina y ahora también en Ponce.",
        "servicio": "Ofrecemos una variedad de servicios que incluyen masajes terapéuticos, ventosaterapia, reflexología, tratamientos faciales y aromaterapia. Puede ver todos nuestros servicios en la sección 'Servicios' de nuestro sitio web.",
        "teléfono": "Puede contactarnos al 787-555-1234 para más información o reservaciones.",
        "telefono": "Puede contactarnos al 787-555-1234 para más información o reservaciones.",
        "contacto": "Puede contactarnos al 787-555-1234 o por correo electrónico a info@spaenruedas.com",
        "correo": "Nuestro correo electrónico es info@spaenruedas.com",
        "email": "Nuestro correo electrónico es info@spaenruedas.com",
        "hola": "¡Hola! Bienvenido a Spa en Ruedas. ¿En qué puedo ayudarte hoy?",
        "gracias": "¡De nada! Estamos para servirle. Si necesita algo más, no dude en preguntar."
    }
    
    for palabra_clave, respuesta in respuestas.items():
        if palabra_clave in mensaje:
            return respuesta
    
    # Respuesta por defecto si no hay coincidencia
    return "¡Gracias por contactarnos! Le puedo ayudar con información sobre nuestros servicios, precios, reservaciones o ubicaciones. ¿En qué está interesado?"