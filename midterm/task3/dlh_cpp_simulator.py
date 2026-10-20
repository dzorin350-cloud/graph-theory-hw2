import time
from typing import Dict, List, Tuple

import folium
from folium.plugins import AntPath
import networkx as nx
import osmnx as ox
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# Configure OSMnx caching to speed up repeated radius queries in Surabaya
ox.settings.use_cache = True
ox.settings.log_console = False

SURABAYA_DEFAULT_CENTER = (-7.2575, 112.7521)  # Balai Kota Surabaya area

# OSM filter targeting trunk, primary, secondary, tertiary and their link ramps
HIGHWAY_FILTER = (
    '["highway"~"trunk|primary|secondary|tertiary|'
    'trunk_link|primary_link|secondary_link|tertiary_link"]'
)


@st.cache_data(show_spinner=False)
def fetch_road_network(
    center_lat: float, center_lon: float, radius_km: float, include_links: bool
) -> nx.MultiDiGraph:
    """
    Downloads the directed road network from OpenStreetMap within radius_km
    of the specified base coordinates.
    """
    radius_m = radius_km * 1000.0
    if include_links:
        custom_filter = HIGHWAY_FILTER
    else:
        custom_filter = '["highway"~"trunk|primary|secondary|tertiary"]'

    G = ox.graph_from_point(
        (center_lat, center_lon),
        dist=radius_m,
        dist_type="bbox",
        network_type="drive",
        simplify=True,
        retain_all=True,
        custom_filter=custom_filter,
    )

    # Filter nodes strictly within the Euclidean/great-circle radius_m
    nodes_to_remove = []
    for node, data in G.nodes(data=True):
        dist = ox.distance.great_circle(
            center_lat, center_lon, data["y"], data["x"]
        )
        if dist > radius_m:
            nodes_to_remove.append(node)

    G.remove_nodes_from(nodes_to_remove)
    return G


def extract_connected_digraph(
    G: nx.MultiDiGraph, base_lat: float, base_lon: float
) -> Tuple[nx.MultiDiGraph, int, int, int]:
    """
    Finds the nearest node to the dump truck base and extracts its
    Strongly Connected Component (SCC). If the nearest node is on a tiny
    boundary stub (< 5 nodes), snaps to the nearest node in the largest SCC.
    """
    if len(G.nodes) == 0:
        raise ValueError("No matching roads found within the selected radius.")

    initial_edges = G.number_of_edges()
    nearest_node = ox.distance.nearest_nodes(G, X=base_lon, Y=base_lat)

    # Identify all strongly connected components
    sccs = list(nx.strongly_connected_components(G))
    sccs_sorted = sorted(sccs, key=len, reverse=True)

    # Find the SCC containing nearest_node
    target_scc = None
    for comp in sccs_sorted:
        if nearest_node in comp:
            target_scc = comp
            break

    # If the clicked point snapped to a 1-way boundary stub cut off by the radius,
    # fall back to the largest viable SCC and pick its closest node to the base
    if target_scc is None or (len(target_scc) < 5 and len(sccs_sorted[0]) >= 5):
        target_scc = sccs_sorted[0]
        G_scc = G.subgraph(target_scc).copy()
        base_node = ox.distance.nearest_nodes(G_scc, X=base_lon, Y=base_lat)
    else:
        G_scc = G.subgraph(target_scc).copy()
        base_node = nearest_node

    ignored_edges = initial_edges - G_scc.number_of_edges()
    return G_scc, base_node, initial_edges, ignored_edges


def solve_directed_cpp(
    G: nx.MultiDiGraph, base_node: int
) -> Tuple[List[Tuple[int, int, int, Dict]], float, float, float]:
    """
    Solves the Directed Chinese Postman Problem (dCPP) on a strongly connected
    MultiDiGraph using Minimum-Cost Flow for Eulerian balancing and Hierholzer's
    algorithm for circuit extraction.

    Returns:
        circuit_steps: Ordered list of (u, v, key, edge_data_dict)
        total_distance_m: Total route length in meters
        deadhead_distance_m: Extra distance from revisited segments in meters
        exec_time_s: Solver execution time in seconds
    """
    t_start = time.perf_counter()

    G_aug = G.copy()

    # Mark all original edges as primary collection passes (augmented = False)
    for u, v, k, data in G_aug.edges(keys=True, data=True):
        data["augmented"] = False

    # Step 1: Check node degree imbalances: demand(v) = out_degree(v) - in_degree(v)
    imbalances = {}
    is_balanced = True
    for node in G_aug.nodes():
        delta = G_aug.out_degree(node) - G_aug.in_degree(node)
        imbalances[node] = delta
        if delta != 0:
            is_balanced = False

    # Step 2: If unbalanced, solve Minimum-Cost Network Flow to find optimal deadheading
    if not is_balanced:
        H = nx.DiGraph()
        for node, demand in imbalances.items():
            H.add_node(node, demand=demand)

        # Keep track of the shortest parallel edge between each (u, v) pair
        shortest_edge_key = {}
        for u, v, k, data in G_aug.edges(keys=True, data=True):
            length_m = float(data.get("length", 1.0))
            weight_cm = max(1, int(round(length_m * 100)))
            if H.has_edge(u, v):
                if weight_cm < H[u][v]["weight"]:
                    H[u][v]["weight"] = weight_cm
                    shortest_edge_key[(u, v)] = (k, data)
            else:
                H.add_edge(u, v, weight=weight_cm)
                shortest_edge_key[(u, v)] = (k, data)

        # Solve integer minimum-cost flow
        flow_dict = nx.min_cost_flow(H)

        # Duplicate edges according to optimal flow values
        for u, neighbors in flow_dict.items():
            for v, flow_val in neighbors.items():
                if flow_val > 0:
                    _, orig_data = shortest_edge_key[(u, v)]
                    for _ in range(int(flow_val)):
                        aug_data = orig_data.copy()
                        aug_data["augmented"] = True
                        G_aug.add_edge(u, v, **aug_data)

    # Step 3: Extract Eulerian Circuit starting and ending at base_node
    raw_circuit = list(nx.eulerian_circuit(G_aug, source=base_node, keys=True))

    circuit_steps = []
    total_distance_m = 0.0
    deadhead_distance_m = 0.0

    for u, v, k in raw_circuit:
        edge_data = G_aug.edges[u, v, k]
        length_m = float(edge_data.get("length", 0.0))
        total_distance_m += length_m
        if edge_data.get("augmented", False):
            deadhead_distance_m += length_m
        circuit_steps.append((u, v, k, edge_data))

    exec_time_s = time.perf_counter() - t_start
    return circuit_steps, total_distance_m, deadhead_distance_m, exec_time_s


def format_edge_attr(val, default: str = "Unnamed Road") -> str:
    """Normalizes OSM edge attributes that may be lists or strings."""
    if val is None:
        return default
    if isinstance(val, list):
        return " / ".join(str(x) for x in val)
    return str(val)


def build_traversal_dataframe(
    circuit_steps: List[Tuple[int, int, int, Dict]]
) -> pd.DataFrame:
    """Builds the ordered street traversal table from the Eulerian circuit."""
    rows = []
    visit_counts: Dict[Tuple[int, int], int] = {}

    for step_idx, (u, v, k, data) in enumerate(circuit_steps, start=1):
        pair = (u, v)
        visit_counts[pair] = visit_counts.get(pair, 0) + 1
        pass_num = visit_counts[pair]

        street_name = format_edge_attr(data.get("name"), "Unnamed Street")
        highway_type = format_edge_attr(data.get("highway"), "road")
        length_m = float(data.get("length", 0.0))
        is_revisit = pass_num > 1 or data.get("augmented", False)

        rows.append(
            {
                "Order": step_idx,
                "Street Name": street_name,
                "Road Class": highway_type,
                "From Node": u,
                "To Node": v,
                "Distance (m)": round(length_m, 1),
                "Pass Type": f"Revisit (Pass #{pass_num})"
                if is_revisit
                else "Collection (Pass #1)",
            }
        )
    return pd.DataFrame(rows)


def extract_edge_coords(
    G: nx.MultiDiGraph, u: int, v: int, data: Dict
) -> List[Tuple[float, float]]:
    """Returns [(lat, lon), ...] geometry for an OSM edge."""
    if "geometry" in data and data["geometry"] is not None:
        return [(lat, lon) for lon, lat in data["geometry"].coords]
    return [
        (G.nodes[u]["y"], G.nodes[u]["x"]),
        (G.nodes[v]["y"], G.nodes[v]["x"]),
    ]


def create_simulator_map(
    G: nx.MultiDiGraph,
    base_lat: float,
    base_lon: float,
    radius_km: float,
    base_node: int = None,
    circuit_steps: List[Tuple[int, int, int, Dict]] = None,
) -> folium.Map:
    """Creates the interactive Folium map with base radius and CPP route overlay."""
    m = folium.Map(
        location=[base_lat, base_lon],
        zoom_start=14,
        tiles="CartoDB positron",
        control_scale=True,
    )

    # Draw operational radius circle
    folium.Circle(
        location=[base_lat, base_lon],
        radius=radius_km * 1000.0,
        color="#2b5c8f",
        weight=2,
        fill=True,
        fill_opacity=0.05,
        tooltip=f"Collection Radius: {radius_km:.2f} km",
    ).add_to(m)

    # User-clicked point marker
    folium.Marker(
        location=[base_lat, base_lon],
        tooltip="Selected Base Location (Click map to move)",
        icon=folium.Icon(color="darkblue", icon="info-sign"),
    ).add_to(m)

    if G is not None and circuit_steps:
        full_route_coords = []

        # Feature groups for toggling layers
        fg_primary = folium.FeatureGroup(name="Primary Collection Pass")
        fg_revisit = folium.FeatureGroup(name="Revisited Segments (Deadhead)")

        for step_idx, (u, v, k, data) in enumerate(circuit_steps, start=1):
            coords = extract_edge_coords(G, u, v, data)
            if not full_route_coords:
                full_route_coords.extend(coords)
            else:
                full_route_coords.extend(coords[1:])

            street_name = format_edge_attr(data.get("name"), "Unnamed Street")
            is_aug = data.get("augmented", False)

            line_color = "#d95f02" if is_aug else "#1b9e77"
            line_weight = 4 if is_aug else 3
            line_opacity = 0.85 if is_aug else 0.75

            folium.PolyLine(
                locations=coords,
                color=line_color,
                weight=line_weight,
                opacity=line_opacity,
                tooltip=(
                    f"Step #{step_idx}: {street_name} "
                    f"({'Revisit' if is_aug else 'Collection'})"
                ),
            ).add_to(fg_revisit if is_aug else fg_primary)

        fg_primary.add_to(m)
        fg_revisit.add_to(m)

        # Animated directional AntPath showing traversal direction along the tour
        AntPath(
            locations=full_route_coords,
            color="#08519c",
            pulse_color="#ffffff",
            weight=3,
            delay=1000,
            dash_array=[10, 25],
            tooltip="Directional CPP Traversal Flow",
        ).add_to(m)

        # Snapped Road Network Base Node Marker
        snapped_lat = G.nodes[base_node]["y"]
        snapped_lon = G.nodes[base_node]["x"]
        folium.Marker(
            location=[snapped_lat, snapped_lon],
            tooltip=f"Snapped Dump Truck Base (Node {base_node})",
            icon=folium.Icon(color="red", icon="home"),
        ).add_to(m)

        folium.LayerControl(collapsed=False).add_to(m)

    return m


def main():
    st.set_page_config(
        page_title="DLH Surabaya CPP Dump Truck Simulator",
        layout="wide",
    )

    st.title("DLH Surabaya Dump Truck Route Simulator (Directed CPP)")
    st.markdown(
        "Click anywhere on the Surabaya map to relocate the **Dump Truck Base**, "
        "adjust the **Delivery Radius**, and compute the optimal Directed Chinese "
        "Postman route across `trunk`, `primary`, `secondary`, and `tertiary` roads."
    )

    # Initialize session state for base coordinates
    if "base_lat" not in st.session_state:
        st.session_state.base_lat = SURABAYA_DEFAULT_CENTER[0]
    if "base_lon" not in st.session_state:
        st.session_state.base_lon = SURABAYA_DEFAULT_CENTER[1]

    # Sidebar Controls
    with st.sidebar:
        st.header("Simulation Parameters")
        radius_km = st.slider(
            "Collection Radius x (km)",
            min_value=0.5,
            max_value=5.0,
            value=1.5,
            step=0.25,
        )
        avg_speed_kmh = st.slider(
            "Average Dump Truck Speed (km/h)",
            min_value=10.0,
            max_value=50.0,
            value=20.0,
            step=2.5,
        )
        include_links = st.checkbox(
            "Include highway link ramps (*_link)",
            value=True,
            help="Keeps slip roads and turnaround ramps connecting divided roads.",
        )

        st.subheader("Base Coordinates")
        manual_lat = st.number_input(
            "Base Latitude",
            value=float(st.session_state.base_lat),
            format="%.6f",
        )
        manual_lon = st.number_input(
            "Base Longitude",
            value=float(st.session_state.base_lon),
            format="%.6f",
        )
        if (
            abs(manual_lat - st.session_state.base_lat) > 1e-6
            or abs(manual_lon - st.session_state.base_lon) > 1e-6
        ):
            st.session_state.base_lat = manual_lat
            st.session_state.base_lon = manual_lon

    # Solve CPP for current base & radius
    G_scc = None
    base_node = None
    circuit_steps = None
    df_schedule = None
    error_msg = None

    try:
        with st.spinner("Fetching OSM road network and solving Directed CPP..."):
            G_raw = fetch_road_network(
                st.session_state.base_lat,
                st.session_state.base_lon,
                radius_km,
                include_links,
            )
            G_scc, base_node, initial_edges, ignored_edges = (
                extract_connected_digraph(
                    G_raw,
                    st.session_state.base_lat,
                    st.session_state.base_lon,
                )
            )
            (
                circuit_steps,
                total_dist_m,
                deadhead_dist_m,
                solver_time_s,
            ) = solve_directed_cpp(G_scc, base_node)
            df_schedule = build_traversal_dataframe(circuit_steps)
    except Exception as exc:
        error_msg = str(exc)

    # Display Top-Level Metrics
    if error_msg:
        st.error(f"Could not compute route: {error_msg}")
    else:
        total_dist_km = total_dist_m / 1000.0
        est_time_min = (total_dist_km / avg_speed_kmh) * 60.0
        efficiency_pct = (
            ((total_dist_m - deadhead_dist_m) / total_dist_m) * 100.0
            if total_dist_m > 0
            else 0.0
        )

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Route Distance", f"{total_dist_km:.2f} km")
        col2.metric("Estimated Travel Time", f"{est_time_min:.1f} min")
        col3.metric("CPP Solver Execution Time", f"{solver_time_s * 1000:.2f} ms")
        col4.metric(
            "Traversals (Required / Total)",
            f"{G_scc.number_of_edges()} / {len(circuit_steps)}",
        )
        col5.metric(
            "Route Efficiency",
            f"{efficiency_pct:.1f}%",
            help="Percentage of total distance spent on first-pass collection.",
        )

        if ignored_edges > 0:
            st.caption(
                f"Note: Ignored {ignored_edges} out of {initial_edges} road segments "
                "within the radius because they were not strongly connected to the "
                "dump truck base component."
            )

    # Render Map and Capture Clicks
    sim_map = create_simulator_map(
        G_scc,
        st.session_state.base_lat,
        st.session_state.base_lon,
        radius_km,
        base_node=base_node,
        circuit_steps=circuit_steps,
    )

    map_col, table_col = st.columns([3, 2])
    with map_col:
        st.subheader("Interactive Route Map (Click to Move Base)")
        map_output = st_folium(
            sim_map, width="100%", height=620, returned_objects=["last_clicked"]
        )
        if map_output and map_output.get("last_clicked"):
            clicked_lat = map_output["last_clicked"]["lat"]
            clicked_lon = map_output["last_clicked"]["lng"]
            if (
                abs(clicked_lat - st.session_state.base_lat) > 1e-5
                or abs(clicked_lon - st.session_state.base_lon) > 1e-5
            ):
                st.session_state.base_lat = clicked_lat
                st.session_state.base_lon = clicked_lon
                st.rerun()

    with table_col:
        st.subheader("Street Traversal Order")
        if df_schedule is not None:
            st.dataframe(
                df_schedule,
                use_container_width=True,
                height=560,
                hide_index=True,
            )
            csv_bytes = df_schedule.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Traversal Schedule (CSV)",
                data=csv_bytes,
                file_name="surabaya_dlh_cpp_schedule.csv",
                mime="text/csv",
            )


if __name__ == "__main__":
    main()