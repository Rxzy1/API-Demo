import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from routing.osrm import get_road
from routing.stations import STATIONS
from routing.planner import plan_stops


def health(_request):
    return JsonResponse({
        "status": "ok",
        "stations_loaded": len(STATIONS),
    })


@csrf_exempt
@require_http_methods(["POST"])
def route(request):
    try:
        body   = json.loads(request.body)
        start  = tuple(float(x) for x in body["start"])
        finish = tuple(float(x) for x in body["finish"])
        if len(start) != 2 or len(finish) != 2:
            raise ValueError
    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        return JsonResponse(
            {"error": 'Send JSON: {"start": [lat, lng], "finish": [lat, lng]}'},
            status=400,
        )

    try:
        road = get_road(start, finish)
        stops, cost = plan_stops(road)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({
        "total_miles":     round(road["total_miles"], 1),
        "duration_hours":  round(road["duration_seconds"] / 3600, 1),
        "total_fuel_cost": cost,
        "fuel_stops":      stops,
        "route_polyline":  road["coords"],
    })
