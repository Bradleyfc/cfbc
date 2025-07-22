from django import template
from principal.models import SolicitudInscripcion

register = template.Library()

@register.simple_tag
def tiene_solicitud_pendiente(estudiante_id, curso_id):
    """
    Verifica si un estudiante tiene una solicitud pendiente para un curso específico.
    """
    return SolicitudInscripcion.objects.filter(
        estudiante_id=estudiante_id,
        curso_id=curso_id,
        estado='pendiente'
    ).exists()

@register.simple_tag
def tiene_solicitud_rechazada(estudiante_id, curso_id):
    """
    Verifica si un estudiante tiene una solicitud rechazada para un curso específico.
    """
    return SolicitudInscripcion.objects.filter(
        estudiante_id=estudiante_id,
        curso_id=curso_id,
        estado='rechazada'
    ).exists()

@register.simple_tag
def obtener_estado_solicitud(estudiante_id, curso_id):
    """
    Obtiene el estado de la solicitud de un estudiante para un curso específico.
    Retorna: 'pendiente', 'aprobada', 'rechazada' o None si no existe solicitud.
    """
    try:
        solicitud = SolicitudInscripcion.objects.get(
            estudiante_id=estudiante_id,
            curso_id=curso_id
        )
        return solicitud.estado
    except SolicitudInscripcion.DoesNotExist:
        return None