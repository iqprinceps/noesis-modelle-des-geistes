#!/usr/bin/env python3
"""Build two source-based EP02 context maps from U.S. Census TIGERweb geometry."""

from __future__ import annotations

import json
import pathlib
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw, ImageFont


ROOT = pathlib.Path(__file__).resolve().parent.parent
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP02_GATEWAY"
GEODATA = EP / "02_SOURCES" / "GEODATA"
OUT = EP / "03_VISUALS" / "MAPS"
SERVICE = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/0/query"


def fetch(name: str, where: str, precision: int) -> dict:
    path = GEODATA / name
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    params = {
        "where": where,
        "outFields": "STATE,STUSAB,NAME",
        "returnGeometry": "true",
        "geometryPrecision": str(precision),
        "outSR": "4326",
        "f": "geojson",
    }
    url = SERVICE + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=120) as response:
        data = json.loads(response.read().decode("utf-8"))
    GEODATA.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    (path.with_suffix(".source.json")).write_text(json.dumps({
        "source": "U.S. Census Bureau TIGERweb State and County service",
        "endpoint": url,
        "retrieved": "2026-08-26",
        "rights": "U.S. federal government data; public domain in the United States",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def rings(geometry: dict):
    coords = geometry["coordinates"]
    if geometry["type"] == "Polygon":
        yield from coords
    elif geometry["type"] == "MultiPolygon":
        for polygon in coords:
            yield from polygon


def font(size: int, bold: bool = False):
    name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(str(pathlib.Path("C:/Windows/Fonts") / name), size)


def project(lon: float, lat: float, bounds: tuple[float, float, float, float]):
    min_lon, max_lon, min_lat, max_lat = bounds
    x = int((lon - min_lon) / (max_lon - min_lon) * 1920)
    y = int((max_lat - lat) / (max_lat - min_lat) * 1080)
    return x, y


def draw_geometry(draw, data: dict, bounds, face="#142334", edge="#668097", lw=2):
    for feature in data.get("features", []):
        for ring in rings(feature["geometry"]):
            points = [project(float(lon), float(lat), bounds) for lon, lat in ring]
            draw.polygon(points, fill=face, outline=edge, width=lw)


def fort_meade(md: dict):
    image = Image.new("RGB", (1920, 1080), "#08131f")
    draw = ImageDraw.Draw(image)
    bounds = (-79.65, -74.9, 37.75, 40.1)
    draw_geometry(draw, md, bounds, face="#18314a", edge="#88a5ba", lw=3)
    sites = [
        (-77.0369, 38.9072, "Washington, D.C.", "#9bb0c0"),
        (-76.6122, 39.2904, "Baltimore", "#9bb0c0"),
        (-76.7432, 39.1082, "Fort George G. Meade", "#d7a65a"),
    ]
    for lon, lat, label, color in sites:
        x, y = project(lon, lat, bounds)
        radius = 12 if "Meade" in label else 7
        draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)
        draw.text((x + 20, y - 18), label, fill="#f4efe7" if "Meade" in label else "#b8c6d1", font=font(30 if "Meade" in label else 24, "Meade" in label))
    draw.text((80, 70), "FORT MEADE — REGIONAL CONTEXT", fill="#f4efe7", font=font(52, True))
    draw.text((80, 140), "Location marker; not a 1983 installation plan", fill="#9bb0c0", font=font(29))
    draw.text((80, 1030), "Boundary data: U.S. Census Bureau TIGERweb • coordinates approximate", fill="#8193a2", font=font(20))
    image.save(OUT / "GW_EN_MAP01_FORT_MEADE_CONTEXT.png")


def flight_191(states: dict):
    image = Image.new("RGB", (1920, 1080), "#08131f")
    draw = ImageDraw.Draw(image)
    bounds = (-125.2, -66.0, 24.0, 50.2)
    draw_geometry(draw, states, bounds, face="#13283c", edge="#526b80", lw=2)
    ord_lon, ord_lat = -87.9073, 41.9742
    lax_lon, lax_lat = -118.4085, 33.9416
    a = project(ord_lon, ord_lat, bounds)
    b = project(lax_lon, lax_lat, bounds)
    steps = 24
    for i in range(0, steps, 2):
        p0 = (int(a[0] + (b[0]-a[0])*i/steps), int(a[1] + (b[1]-a[1])*i/steps))
        p1 = (int(a[0] + (b[0]-a[0])*(i+1)/steps), int(a[1] + (b[1]-a[1])*(i+1)/steps))
        draw.line((p0, p1), fill="#d7a65a", width=6)
    for point, color, radius in [(a, "#d7a65a", 13), (b, "#9bb0c0", 10)]:
        draw.ellipse((point[0]-radius, point[1]-radius, point[0]+radius, point[1]+radius), fill=color)
    draw.multiline_text((a[0] + 25, a[1] - 35), "Chicago O’Hare\nDeparture / accident area", fill="#f4efe7", font=font(27), spacing=6)
    draw.multiline_text((b[0] + 25, b[1] + 10), "Los Angeles\nScheduled destination", fill="#d6e0e7", font=font(27), spacing=6)
    draw.text((60, 55), "AMERICAN AIRLINES FLIGHT 191", fill="#f4efe7", font=font(52, True))
    draw.text((60, 125), "May 25, 1979 • route context, not a flown-path reconstruction", fill="#9bb0c0", font=font(29))
    draw.text((60, 1030), "Boundary data: U.S. Census Bureau TIGERweb • airports: published coordinates", fill="#8193a2", font=font(20))
    image.save(OUT / "GW_EN_MAP02_FLIGHT191_ROUTE_CONTEXT.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    md = fetch("TIGERWEB_MARYLAND.geojson", "STUSAB='MD'", 4)
    contiguous = fetch(
        "TIGERWEB_CONTIGUOUS_STATES.geojson",
        "STATE NOT IN ('02','15','60','66','69','72','78')",
        2,
    )
    fort_meade(md)
    flight_191(contiguous)
    print("Wrote 2 source-based maps")


if __name__ == "__main__":
    main()
