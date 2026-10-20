"""Read local OSM data and build a directed road-distance matrix.

The returned stop order is always: SPPG (index 0), then the schools.
"""

from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import networkx as nx
import osmnx as ox
from pyproj import Geod, Transformer
from shapely.geometry import LineString, Point
from shapely.ops import polygonize, transform, unary_union


def _validate_input(lat: float, lon: float, radius_km: float) -> None:
    try:
        lat = float(lat)
        lon = float(lon)
        radius_km = float(radius_km)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("lat, lon et radius_km doivent être numériques") from error
    if not (
        math.isfinite(lat)
        and math.isfinite(lon)
        and math.isfinite(radius_km)
        and -90 <= lat <= 90
        and -180 <= lon <= 180
        and radius_km > 0
    ):
        raise ValueError("Coordonnées ou rayon invalides")


def _distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the WGS84 distance between two GPS positions in metres."""
    _, _, distance = Geod(ellps="WGS84").inv(lon1, lat1, lon2, lat2)
    return float(distance)


def _school_position(geometry: Any, lat: float, lon: float) -> tuple[float, float]:
    """Return a representative point, transformed to local metre coordinates."""
    if geometry is None or geometry.is_empty or not geometry.is_valid:
        raise ValueError("Une école possède une géométrie OSM invalide")

    projection = (
        f"+proj=aeqd +lat_0={lat} +lon_0={lon} "
        "+datum=WGS84 +units=m +no_defs"
    )
    to_local = Transformer.from_crs("EPSG:4326", projection, always_xy=True).transform
    to_wgs84 = Transformer.from_crs(projection, "EPSG:4326", always_xy=True).transform
    representative = transform(to_wgs84, transform(to_local, geometry).representative_point())
    return float(representative.y), float(representative.x)


def _osm_file() -> Path:
    """Resolve data/paris.osm independently of the current working directory."""
    data_dir = Path(__file__).resolve().parent.parent / "data"
    requested = data_dir / "paris.osm"
    if requested.exists():
        return requested
    for path in data_dir.glob("*.osm"):
        if path.name.lower() == "paris.osm":
            return path
    raise FileNotFoundError(f"Fichier OSM introuvable: {requested}")


def _xml_tags(element: ET.Element) -> dict[str, str]:
    return {
        tag.attrib["k"]: tag.attrib["v"]
        for tag in element.findall("tag")
        if "k" in tag.attrib and "v" in tag.attrib
    }


def _school_geometry(
    element_type: str,
    element_id: str,
    node_coordinates: dict[str, tuple[float, float]],
    way_references: dict[str, list[str]],
    relation_members: list[tuple[str, str, str]],
) -> Any:
    """Build a point, polygon, or relation geometry from local OSM members."""
    if element_type == "node":
        coordinate = node_coordinates.get(element_id)
        return Point(coordinate) if coordinate else None

    if element_type == "way":
        coordinates = [
            node_coordinates[node_id]
            for node_id in way_references.get(element_id, [])
            if node_id in node_coordinates
        ]
        if len(coordinates) >= 3 and coordinates[0] == coordinates[-1]:
            from shapely.geometry import Polygon

            return Polygon(coordinates)
        return LineString(coordinates) if len(coordinates) >= 2 else None

    lines = []
    for member_type, member_id, role in relation_members:
        if member_type == "way":
            coordinates = [
                node_coordinates[node_id]
                for node_id in way_references.get(member_id, [])
                if node_id in node_coordinates
            ]
            if len(coordinates) >= 2:
                lines.append(LineString(coordinates))
    if not lines:
        return None
    polygons = list(polygonize(unary_union(lines)))
    return unary_union(polygons) if polygons else unary_union(lines)


def _get_local_schools(path: Path, lat: float, lon: float, radius_m: float) -> list[dict[str, Any]]:
    """Read amenity=school elements from a local OSM XML file."""
    school_elements: list[tuple[str, str, dict[str, str], list[tuple[str, str, str]]]] = []
    required_way_ids: set[str] = set()

    # First pass: identify schools and relation members.
    for _, element in ET.iterparse(path, events=("end",)):
        element_type = element.tag
        if element_type not in {"node", "way", "relation"}:
            continue
        tags = _xml_tags(element)
        members = [
            (member.attrib.get("type", ""), member.attrib.get("ref", ""), member.attrib.get("role", ""))
            for member in element.findall("member")
        ]
        if tags.get("amenity") == "school":
            element_id = element.attrib["id"]
            school_elements.append((element_type, element_id, tags, members))
            required_way_ids.update(
                member_id for member_type, member_id, _ in members if member_type == "way"
            )
            if element_type == "way":
                required_way_ids.add(element_id)
        if element_type in {"node", "way", "relation"}:
            element.clear()

    school_node_ids = {
        element_id
        for element_type, element_id, _, _ in school_elements
        if element_type == "node"
    }
    required_node_ids = set(school_node_ids)
    way_references: dict[str, list[str]] = {}
    for _, _, _, members in school_elements:
        for member_type, member_id, _ in members:
            if member_type == "node":
                required_node_ids.add(member_id)

    # Second pass: retain only coordinates and ways needed by schools.
    node_coordinates: dict[str, tuple[float, float]] = {}
    for _, element in ET.iterparse(path, events=("end",)):
        element_type = element.tag
        element_id = element.attrib.get("id")
        if element_type == "node" and element_id in required_node_ids:
            node_coordinates[element_id] = (
                float(element.attrib["lon"]),
                float(element.attrib["lat"]),
            )
        elif element_type == "way" and element_id in required_way_ids:
            way_references[element_id] = [
                node.attrib["ref"] for node in element.findall("nd") if "ref" in node.attrib
            ]
            required_node_ids.update(way_references[element_id])
        if element.tag in {"node", "way", "relation"}:
            element.clear()

    # A third pass is needed when a school way's node references were found
    # only while reading that way.
    missing_node_ids = required_node_ids - node_coordinates.keys()
    if missing_node_ids:
        for _, element in ET.iterparse(path, events=("end",)):
            if element.tag == "node" and element.attrib.get("id") in missing_node_ids:
                node_coordinates[element.attrib["id"]] = (
                    float(element.attrib["lon"]),
                    float(element.attrib["lat"]),
                )
            element.clear()

    schools: list[dict[str, Any]] = []
    for element_type, element_id, tags, members in school_elements:
        geometry = _school_geometry(
            element_type, element_id, node_coordinates, way_references, members
        )
        if geometry is None or geometry.is_empty or not geometry.is_valid:
            raise ValueError(f"Géométrie invalide pour l'école {element_type}/{element_id}")
        school_lat, school_lon = _school_position(geometry, lat, lon)
        if _distance_m(lat, lon, school_lat, school_lon) <= radius_m:
            schools.append(
                {
                    "id": f"{element_type}/{element_id}",
                    "name": tags.get("name", f"École OSM {element_type}/{element_id}"),
                    "lat": school_lat,
                    "lon": school_lon,
                }
            )
    return schools


def _filter_car_graph(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """Keep drivable highway edges while preserving the directed graph."""
    allowed_highways = {
        "motorway", "motorway_link", "trunk", "trunk_link", "primary",
        "primary_link", "secondary", "secondary_link", "tertiary",
        "tertiary_link", "unclassified", "residential", "living_street",
        "service", "road",
    }
    excluded_access = {"no", "private", "delivery", "customers"}
    edges_to_remove = []
    for source, target, key, data in graph.edges(keys=True, data=True):
        highway = data.get("highway")
        highway_values = highway if isinstance(highway, (list, tuple)) else [highway]
        access = data.get("access", "")
        motorcar = data.get("motorcar", "")
        access_values = access if isinstance(access, (list, tuple)) else [access]
        motorcar_values = motorcar if isinstance(motorcar, (list, tuple)) else [motorcar]
        if not any(value in allowed_highways for value in highway_values):
            edges_to_remove.append((source, target, key))
        elif any(str(value).lower() in excluded_access for value in access_values):
            edges_to_remove.append((source, target, key))
        elif any(str(value).lower() in {"no", "private"} for value in motorcar_values):
            edges_to_remove.append((source, target, key))
    graph.remove_edges_from(edges_to_remove)
    graph.remove_nodes_from(list(nx.isolates(graph)))
    return graph


def _nearest_node(graph: nx.MultiDiGraph, lon: float, lat: float) -> Any:
    """Use OSMnx nearest_nodes, with a standard-library fallback."""
    try:
        return ox.distance.nearest_nodes(graph, X=lon, Y=lat)
    except ImportError:
        return min(
            graph.nodes,
            key=lambda node: (
                (float(graph.nodes[node]["x"]) - lon) ** 2
                + (float(graph.nodes[node]["y"]) - lat) ** 2
            ),
        )


def _path_geometry(graph: nx.MultiDiGraph, path: list[Any]) -> list[tuple[float, float]]:
    """Return the path's GPS coordinates, including road geometry when present."""
    coordinates: list[tuple[float, float]] = []
    for source, target in zip(path, path[1:]):
        edge_data = graph.get_edge_data(source, target)
        if not edge_data:
            raise RuntimeError(f"Arête absente pour le chemin {source}->{target}")
        edge = min(edge_data.values(), key=lambda data: float(data.get("length", math.inf)))
        geometry = edge.get("geometry")
        if geometry is None:
            edge_coordinates = [
                (float(graph.nodes[source]["x"]), float(graph.nodes[source]["y"])),
                (float(graph.nodes[target]["x"]), float(graph.nodes[target]["y"])),
            ]
        else:
            edge_coordinates = [(float(x), float(y)) for x, y in geometry.coords]
            source_position = (float(graph.nodes[source]["x"]), float(graph.nodes[source]["y"]))
            if edge_coordinates[0] != source_position:
                edge_coordinates.reverse()
        if coordinates and edge_coordinates[0] == coordinates[-1]:
            coordinates.extend(edge_coordinates[1:])
        else:
            coordinates.extend(edge_coordinates)
    if not coordinates and path:
        coordinates = [
            (float(graph.nodes[path[0]]["x"]), float(graph.nodes[path[0]]["y"]))
        ]
    return coordinates


def load_data(lat: float, lon: float, radius_km: float) -> dict[str, Any]:
    """Read local OSM data and return roads, schools, distances and paths.

    ``matrix[i][j]`` is the directed road distance in metres.  If a school
    belongs to a disconnected component, its entry is retained and the
    corresponding unreachable distance/path is ``math.inf``/``None``.
    """
    _validate_input(lat, lon, radius_km)
    radius_m = float(radius_km) * 1000
    osm_path = _osm_file()

    try:
        graph = ox.graph_from_xml(
            osm_path,
            bidirectional=False,
            simplify=True,
            retain_all=True,
        )
        graph = _filter_car_graph(graph)
        schools = _get_local_schools(osm_path, lat, lon, radius_m)
    except FileNotFoundError:
        raise
    except (ValueError, RuntimeError):
        raise
    except Exception as error:
        raise RuntimeError(f"Échec de la lecture du fichier OSM local: {error}") from error

    if graph.number_of_nodes() == 0 or graph.number_of_edges() == 0:
        raise RuntimeError("Le fichier OSM ne contient aucune route accessible aux voitures")

    try:
        sppg_node = _nearest_node(graph, lon, lat)
        school_nodes = [
            _nearest_node(graph, school["lon"], school["lat"])
            for school in schools
        ]
    except Exception as error:
        raise RuntimeError(f"Impossible d'associer les lieux aux routes: {error}") from error

    stop_nodes = [sppg_node] + school_nodes
    count = len(stop_nodes)
    matrix = [[0.0 if i == j else math.inf for j in range(count)] for i in range(count)]
    paths: dict[tuple[int, int], list[Any] | None] = {}

    for source_index, source_node in enumerate(stop_nodes):
        lengths, shortest_paths = nx.single_source_dijkstra(
            graph, source_node, weight="length"
        )
        for target_index, target_node in enumerate(stop_nodes):
            if source_index == target_index:
                paths[(source_index, target_index)] = [source_node]
            elif target_node not in shortest_paths:
                # Keep the school; only this directed leg is unavailable.
                paths[(source_index, target_index)] = None
            else:
                matrix[source_index][target_index] = float(lengths[target_node])
                paths[(source_index, target_index)] = shortest_paths[target_node]

    for pair, node_path in list(paths.items()):
        if node_path is not None and len(node_path) > 1:
            paths[pair] = node_path

    return {
        "graph": graph,
        "schools": schools,
        "matrix": matrix,
        "stop_nodes": stop_nodes,
        "paths": paths,
        "path_geometries": {
            pair: None if node_path is None else _path_geometry(graph, node_path)
            for pair, node_path in paths.items()
        },
    }
