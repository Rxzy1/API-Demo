import csv, math, logging
from collections import defaultdict
from django.conf import settings

logger = logging.getLogger(__name__)
STATIONS: list[dict] = []
_GRID: defaultdict[tuple[int,int], list[dict]] = defaultdict(list)

def load_stations():
    city_coords = {}
    with open(settings.US_CITIES_CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["city"].strip().lower(), row["state_id"].strip())
            city_coords.setdefault(key, (float(row["lat"]), float(row["lng"])))

    with open(settings.FUEL_CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                city, state = row["City"].strip(), row["State"].strip()
                coords = city_coords.get((city.lower(), state))
                if not coords:
                    continue
                lat, lng = coords
                s = {
                    "id":    int(row["OPIS Truckstop ID"]),
                    "name":  row["Truckstop Name"].strip(),
                    "city":  city, "state": state,
                    "lat":   lat,  "lng":   lng,
                    "price": float(row["Retail Price"]),
                }
                STATIONS.append(s)
                _GRID[(int(lat), int(lng))].append(s)  # bucket by 1° cell
            except (KeyError, ValueError):
                continue

    logger.info("Loaded %d stations", len(STATIONS))

def haversine(lat1, lon1, lat2, lon2):
    R = 3956
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def find_cheapest_station_near(lat: float, lng: float, radius_miles: float = 30) -> dict | None:
    # check only the 9 surrounding 1° grid cells instead of all 8000 stations
    ilat, ilng = int(lat), int(lng)
    candidates = [
        s for di in (-1, 0, 1) for dj in (-1, 0, 1)
        for s in _GRID[(ilat+di, ilng+dj)]
    ]
    return min(
        (s for s in candidates if haversine(lat, lng, s["lat"], s["lng"]) <= radius_miles),
        key=lambda s: s["price"],
        default=None,
    )