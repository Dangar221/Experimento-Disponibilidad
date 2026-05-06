from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
from django.views import View
from .models import Proyecto, Consumo
import logging

logger = logging.getLogger(__name__)

# Health Check - Kong usa este endpoint para saber si el servidor está vivo
def health_check(request):
    return HttpResponse("OK", status=200)

class ConsumosView(View):
    """
    GET /consumos/?proyecto={id}
    Tácticas: Caché en memoria + Fallar con gracia
    """
    def get(self, request):
        proyecto_id = request.GET.get('proyecto')

        if not proyecto_id:
            return JsonResponse({'error': 'Falta el parametro proyecto'}, status=400)

        try:
            proyecto_id = int(proyecto_id)
        except ValueError:
            return JsonResponse({'error': 'proyecto debe ser un numero'}, status=400)

        # TÁCTICA 1: Caché en memoria
        cache_key = f"consumos_proyecto_{proyecto_id}"
        resultado_cache = cache.get(cache_key)
        if resultado_cache is not None:
            resultado_cache['fuente'] = 'cache'
            return JsonResponse(resultado_cache, status=200)

        # TÁCTICA 2: Fallar con gracia
        try:
            proyecto = Proyecto.objects.get(id=proyecto_id)
            consumos_qs = Consumo.objects.filter(proyecto=proyecto).select_related('recurso')

            respuesta = {
                'proyecto_id': proyecto_id,
                'proyecto_nombre': proyecto.nombre,
                'total_consumo': sum(c.cantidad for c in consumos_qs),
                'total_costo': sum(c.costo for c in consumos_qs),
                'consumos': [
                    {'recurso': c.recurso.nombre, 'tipo': c.recurso.tipo,
                     'cantidad': c.cantidad, 'costo': c.costo, 'fecha': str(c.fecha)}
                    for c in consumos_qs
                ],
                'fuente': 'base_de_datos',
            }
            cache.set(cache_key, respuesta, timeout=300)
            return JsonResponse(respuesta, status=200)

        except Proyecto.DoesNotExist:
            return JsonResponse({'error': f'Proyecto {proyecto_id} no encontrado'}, status=404)

        except Exception as e:
            logger.error(f"Error: {str(e)}")
            # Si la BD falla, intentamos servir desde caché
            if resultado_cache:
                resultado_cache['fuente'] = 'cache_fallback'
                return JsonResponse(resultado_cache, status=200)
            # Si no hay caché tampoco, respondemos 200 controlado (no 500)
            return JsonResponse({
                'proyecto_id': proyecto_id,
                'mensaje': 'Servicio temporalmente degradado',
                'consumos': [], 'total_consumo': 0, 'total_costo': 0,
                'fuente': 'fallback',
            }, status=200)
