import requests

OSRM_BASE = "http://router.project-osrm.org"


def get_road(start, finish):
    """Call OSRM and return distance, duration, and waypoint coords."""
    url = (
        f"{OSRM_BASE}/route/v1/driving/"
        f"{start[1]},{start[0]};{finish[1]},{finish[0]}"
        f"?overview=full&geometries=geojson&steps=false"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("routes"):
        raise ValueError("OSRM returned no route for that start/finish")

    leg    = data["routes"][0]
    coords = leg["geometry"]["coordinates"]  # OSRM gives [lng, lat], flip below

    return {
        "total_miles":      leg["distance"] / 1609.34,
        "duration_seconds": leg["duration"],
        "coords":           [[c[1], c[0]] for c in coords],  # flip to [lat, lng]
    }
