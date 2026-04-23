from routing.stations import find_cheapest_station_near, haversine

TANK_MILES          = 500
TRUCK_MPG           = 10
REFILL_AT           = 0.80
REFILL_TRIGGER      = TANK_MILES * REFILL_AT   # 400 miles
SEARCH_RADIUS       = 30
FALLBACK_RADIUS     = 60

def plan_stops(road: dict) -> tuple[list[dict], float]:
    coords      = road["coords"]
    total_miles = road["total_miles"]
    stops: list[dict] = []
    total_cost  = 0.0
    miles_since_fill = 0.0
    prev = coords[0]

    for lat, lng in coords[1:]:
        miles_since_fill += haversine(prev[0], prev[1], lat, lng)
        prev = (lat, lng)

        if miles_since_fill < REFILL_TRIGGER:
            continue

        station = find_cheapest_station_near(lat, lng, SEARCH_RADIUS)
        if not station:
            continue

        gallons     = miles_since_fill / TRUCK_MPG
        cost        = round(gallons * station["price"], 2)
        total_cost += cost
        stops.append({
            "station_id":    station["id"],
            "name":          station["name"],
            "city":          station["city"],
            "state":         station["state"],
            "lat":           station["lat"],
            "lng":           station["lng"],
            "price_per_gal": station["price"],
            "gallons":       round(gallons, 2),
            "cost":          cost,
        })
        miles_since_fill = 0.0

    # tail segment — price it at destination rate
    if miles_since_fill > 0:
        dest = coords[-1]
        dest_station = find_cheapest_station_near(dest[0], dest[1], FALLBACK_RADIUS)
        tail_price   = dest_station["price"] if dest_station else (stops[-1]["price_per_gal"] if stops else 0)
        total_cost  += round((miles_since_fill / TRUCK_MPG) * tail_price, 2)

    # fallback: short trip with no stops and no cost yet (no station near destination)
    if not stops and total_cost == 0:
        mid     = coords[len(coords)//2]
        station = find_cheapest_station_near(mid[0], mid[1], FALLBACK_RADIUS)
        if station:
            total_cost = round((total_miles / TRUCK_MPG) * station["price"], 2)

    return stops, round(total_cost, 2)