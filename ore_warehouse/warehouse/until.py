from shapely.geometry import Point
from shapely import wkt


def is_point_in_polygon(x: float, y: float, poly_str: str) -> bool:
    wkt_str = poly_str.strip()
    polygon = wkt.loads(wkt_str)
    point = Point(x, y)
    return polygon.covers(point)
