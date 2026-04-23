# Truck Route Fuel Planner — Demo API

A simple API that plans a cross-country truck route and figures out the cheapest places to stop for fuel along the way.

---

## What it does

You give it a start and end location (latitude/longitude), and it gives you back:

- The full driving route
- How long the trip is (miles and hours)
- A list of recommended fuel stops, picked for the lowest price near your route
- The estimated total fuel cost for the trip

It assumes a standard semi-truck — 500-mile tank range, 10 miles per gallon — and plans stops before the tank hits 80% empty, so you're never cutting it close.

---

## How it works (plain English)

1. Your start and finish coordinates go in as a POST request
2. The route is fetched from a road routing service, which returns the actual driving path (not a straight line)
3. That path is walked mile by mile, and every time the truck is getting low on fuel, the planner looks at real truck stop data nearby and picks the cheapest one
4. The whole trip is priced out and returned to you

---

## The API

### `POST /route`

**Request body:**
```json
{
  "start":  [41.8781, -87.6298],
  "finish": [34.0522, -118.2437]
}
```
Coordinates are `[latitude, longitude]`.

**Response:**
```json
{
  "total_miles": 2016.3,
  "duration_hours": 29.4,
  "total_fuel_cost": 987.50,
  "fuel_stops": [
    {
      "name": "PILOT TRAVEL CENTER",
      "city": "Kansas City",
      "state": "MO",
      "lat": 39.0997,
      "lng": -94.5786,
      "price_per_gal": 3.82,
      "gallons": 40.1,
      "cost": 153.18
    }
  ],
  "route_polyline": [[41.87, -87.62], [41.80, -88.10], ...]
}
```

### `GET /health`

Returns `200 OK` if the server is up and how many fuel stations are loaded.

---

## Running it locally

```bash
pip install -r requirements.txt
python manage.py runserver
```

You'll need two CSV files configured in settings — one with US city coordinates, one with truck stop fuel prices. The app loads those at startup.

---

## Known limitations (it's a demo)

- The routing depends on a free public routing server that can be slow or occasionally time out
- Fuel prices in the CSV are a snapshot — not live
- Coordinates only work for the continental US (that's where the station data is)