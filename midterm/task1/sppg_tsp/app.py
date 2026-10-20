"""Simple Streamlit interface for the exact Held-Karp TSP solver in Paris."""

from __future__ import annotations

import math
from typing import Any

import folium
import streamlit as st
from streamlit_folium import st_folium

from held_karp import solve_tsp
from osm_data import load_data


PARIS_LAT = 48.8575
PARIS_LON = 2.3815
AVERAGE_SPEED_KMH = 30.0
MAX_EXACT_SCHOOLS = 15
MAX_SPPG_ROAD_DISTANCE_M = 1000.0


def _initialise_state() -> None:
    if "latitude" not in st.session_state:
        st.session_state.latitude = PARIS_LAT
    if "longitude" not in st.session_state:
        st.session_state.longitude = PARIS_LON
    if "result" not in st.session_state:
        st.session_state.result = None


def _check_local_coverage(data: dict[str, Any], latitude: float, longitude: float) -> None:
    """Reject coordinates outside the local extract or far from its roads."""
    graph = data["graph"]
    if not graph.nodes:
        raise ValueError("Le fichier OSM local ne contient aucun nœud routier.")

    longitudes = [float(graph.nodes[node]["x"]) for node in graph.nodes]
    latitudes = [float(graph.nodes[node]["y"]) for node in graph.nodes]
    if not (
        min(latitudes) <= latitude <= max(latitudes)
        and min(longitudes) <= longitude <= max(longitudes)
    ):
        raise ValueError(
            "Le SPPG est hors de la zone couverte par le fichier OSM local de Paris. "
            "Choisissez une position située dans l'emprise du fichier."
        )

    latitude_scale = 111_320.0
    longitude_scale = latitude_scale * math.cos(math.radians(latitude))
    nearest_distance = min(
        math.hypot(
            (float(graph.nodes[node]["y"]) - latitude) * latitude_scale,
            (float(graph.nodes[node]["x"]) - longitude) * longitude_scale,
        )
        for node in graph.nodes
    )
    if nearest_distance > MAX_SPPG_ROAD_DISTANCE_M:
        raise ValueError(
            "Le SPPG est trop éloigné des routes du fichier OSM local "
            f"({nearest_distance:.0f} m du nœud le plus proche). "
            "Aucune association automatique n'a été effectuée."
        )


def _make_map(
    latitude: float,
    longitude: float,
    radius_km: float,
    result: dict[str, Any] | None,
) -> folium.Map:
    """Create the map and draw the current SPPG, schools, and route."""
    map_view = folium.Map(
        location=[latitude, longitude],
        zoom_start=13,
        control_scale=True,
    )
    folium.Marker(
        [latitude, longitude],
        popup="SPPG",
        tooltip="SPPG",
        icon=folium.Icon(color="red", icon="home"),
    ).add_to(map_view)

    folium.Circle(
        [latitude, longitude],
        radius=radius_km * 1000,
        color="blue",
        fill=False,
        tooltip=f"Rayon: {radius_km:.1f} km",
    ).add_to(map_view)

    if result is None:
        return map_view

    data = result["data"]
    schools = data["schools"]
    graph = data["graph"]

    solution = result["solution"]
    route = solution["route"] if solution is not None else []
    visit_numbers = {vertex: number for number, vertex in enumerate(route[1:-1], start=1)}
    for school_index, school in enumerate(schools, start=1):
        number = visit_numbers.get(school_index)
        label = (
            f"{number}. {school['name']}"
            if number is not None
            else f"{school['name']} (non visitée)"
        )
        color = "green" if number is not None else "orange"
        folium.Marker(
            [school["lat"], school["lon"]],
            popup=label,
            tooltip=label,
            icon=folium.Icon(color=color, icon="graduation-cap"),
        ).add_to(map_view)

    for source, destination in zip(route, route[1:]):
        node_path = data["paths"].get((source, destination))
        if not node_path:
            continue
        coordinates = [
            (float(graph.nodes[node]["y"]), float(graph.nodes[node]["x"]))
            for node in node_path
        ]
        folium.PolyLine(
            coordinates,
            color="purple",
            weight=5,
            opacity=0.8,
            tooltip=f"{source} → {destination}",
        ).add_to(map_view)
    return map_view


def _show_results(result: dict[str, Any]) -> None:
    data = result["data"]
    solution = result["solution"]
    schools = data["schools"]
    if solution is None:
        st.warning(result.get("message", (
            f"{len(schools)} école(s) ont été trouvées, mais aucune tournée complète "
            "n'est possible avec les routes disponibles."
        )))
        return
    route = solution["route"]

    st.subheader("Résultats")
    st.info(
        "Cette tournée est optimale pour la matrice routière fournie. "
        "Elle a été calculée avec Held-Karp."
    )
    left, middle, right = st.columns(3)
    left.metric("Nombre d'écoles", len(schools))
    middle.metric("Distance totale", f"{solution['distance'] / 1000:.2f} km")
    right.metric("Temps Held-Karp", f"{solution['elapsed_s']:.6f} s")

    duration_minutes = solution["distance"] / 1000 / AVERAGE_SPEED_KMH * 60
    st.write(
        f"Durée estimée à {AVERAGE_SPEED_KMH:.0f} km/h : "
        f"{duration_minutes:.1f} minutes"
    )
    st.write("Ordre de visite :")
    names = ["SPPG"]
    names.extend(schools[index - 1]["name"] for index in route[1:-1])
    names.append("SPPG")
    st.write(" → ".join(f"{index}. {name}" for index, name in enumerate(names)))


def main() -> None:
    st.set_page_config(page_title="TSP SPPG Paris", layout="wide")
    _initialise_state()
    st.title("TSP SPPG - livraisons aux écoles de Paris")
    st.write("Cliquez sur la carte pour choisir le SPPG, ou modifiez les coordonnées.")

    latitude = st.number_input(
        "Latitude du SPPG",
        min_value=-90.0,
        max_value=90.0,
        format="%.6f",
        key="latitude",
    )
    longitude = st.number_input(
        "Longitude du SPPG",
        min_value=-180.0,
        max_value=180.0,
        format="%.6f",
        key="longitude",
    )
    radius_km = st.slider(
        "Rayon de livraison (km)",
        min_value=0.2,
        max_value=1.5,
        value=0.5,
        step=0.1,
    )

    map_result = st.session_state.result
    map_view = _make_map(latitude, longitude, radius_km, map_result)
    map_event = st_folium(
        map_view,
        height=520,
        width=None,
        key="sppg_map",
        returned_objects=["last_clicked"],
    )
    clicked = map_event.get("last_clicked")
    if clicked is not None:
        clicked_lat = float(clicked["lat"])
        clicked_lon = float(clicked["lng"])
        if (
            not math.isclose(clicked_lat, latitude)
            or not math.isclose(clicked_lon, longitude)
        ):
            st.session_state.latitude = clicked_lat
            st.session_state.longitude = clicked_lon
            st.session_state.result = None
            st.rerun()

    if st.button("Calculate Route", type="primary"):
        try:
            with st.spinner("Chargement des données OSM locales et calcul de la tournée..."):
                data = load_data(latitude, longitude, radius_km)
                _check_local_coverage(data, latitude, longitude)
                if len(data["schools"]) > MAX_EXACT_SCHOOLS:
                    message = (
                        f"{len(data['schools'])} écoles ont été trouvées. "
                        f"Held-Karp est limité à {MAX_EXACT_SCHOOLS} écoles "
                        "pour éviter une consommation excessive de mémoire et de temps. "
                        "Aucune école n'a été supprimée."
                    )
                    st.session_state.result = {
                        "data": data,
                        "solution": None,
                        "message": message,
                    }
                    st.error(message)
                    st.rerun()
                try:
                    solution = solve_tsp(data["matrix"])
                except ValueError as error:
                    st.session_state.result = {
                        "data": data,
                        "solution": None,
                        "message": f"Tournée impossible : {error}",
                    }
                    st.error(f"Tournée impossible : {error}")
                    st.rerun()
            st.session_state.result = {"data": data, "solution": solution}
            st.rerun()
        except (RuntimeError, ValueError, KeyError) as error:
            st.session_state.result = None
            st.error(f"Impossible de calculer la tournée : {error}")

    if st.session_state.result is not None:
        _show_results(st.session_state.result)


if __name__ == "__main__":
    main()
