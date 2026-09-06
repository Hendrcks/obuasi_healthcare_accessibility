"""Create walking catchments around healthcare facilities in Obuasi, Ghana."""

from pathlib import Path

import folium
import geopandas as gpd
import networkx as nx
import osmnx as ox
import pandas as pd
from shapely.geometry import Point


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs"
PLACE_NAMES = [
    "Obuasi Municipal District, Ashanti Region, Ghana",
    "Obuasi East Municipal District, Ashanti Region, Ghana",
]
WALKING_SPEED_KPH = 4.8
TRAVEL_TIMES_MINUTES = [5, 10, 15]


def load_study_area() -> gpd.GeoDataFrame:
    """Geocode and combine the two municipal boundaries."""
    areas = [ox.geocode_to_gdf(place) for place in PLACE_NAMES]
    combined = gpd.GeoDataFrame(
        pd.concat(areas, ignore_index=True), crs=areas[0].crs
    )
    return combined.dissolve().reset_index(drop=True)


def load_healthcare_facilities(polygon) -> gpd.GeoDataFrame:
    """Retrieve mapped healthcare facilities within the study area."""
    tags = {"amenity": ["hospital", "clinic", "doctors"]}
    facilities = ox.features_from_polygon(polygon, tags)
    facilities = facilities.reset_index()
    facilities = facilities[facilities.geometry.notna()].copy()
    facilities["geometry"] = facilities.geometry.apply(
        lambda geom: geom if isinstance(geom, Point) else geom.representative_point()
    )
    facilities["name"] = facilities.get("name", pd.Series(index=facilities.index)).fillna(
        "Unnamed healthcare facility"
    )
    return gpd.GeoDataFrame(facilities, geometry="geometry", crs="EPSG:4326")


def add_travel_time(graph):
    """Calculate walking minutes for every network edge."""
    metres_per_minute = WALKING_SPEED_KPH * 1000 / 60
    for _, _, _, data in graph.edges(keys=True, data=True):
        data["travel_time"] = data["length"] / metres_per_minute
    return graph


def create_isochrones(graph, facilities: gpd.GeoDataFrame) -> dict[int, gpd.GeoDataFrame]:
    """Build dissolved convex-hull catchments for each travel-time threshold."""
    facility_nodes = ox.distance.nearest_nodes(
        graph, X=facilities.geometry.x, Y=facilities.geometry.y
    )
    graph_crs = graph.graph["crs"]
    results = {}

    for minutes in TRAVEL_TIMES_MINUTES:
        polygons = []
        for node in set(facility_nodes):
            ego = nx.ego_graph(
                graph, node, radius=minutes, distance="travel_time", undirected=True
            )
            nodes, _ = ox.graph_to_gdfs(ego)
            if len(nodes) >= 3:
                polygons.append(nodes.geometry.unary_union.convex_hull)

        layer = gpd.GeoDataFrame(geometry=polygons, crs=graph_crs)
        if not layer.empty:
            layer = layer.dissolve().reset_index(drop=True).to_crs("EPSG:4326")
        results[minutes] = layer

    return results


def build_map(study_area, facilities, isochrones) -> folium.Map:
    """Create an interactive map with boundary, facilities and catchments."""
    centre = study_area.to_crs(3857).geometry.centroid.to_crs(4326).iloc[0]
    map_object = folium.Map(
        location=[centre.y, centre.x], zoom_start=12, tiles="CartoDB positron"
    )

    folium.GeoJson(
        study_area,
        name="Study area",
        style_function=lambda _: {"color": "#111827", "weight": 3, "fillOpacity": 0},
    ).add_to(map_object)

    colours = {15: "#93c5fd", 10: "#3b82f6", 5: "#1d4ed8"}
    for minutes in [15, 10, 5]:
        layer = isochrones[minutes]
        if not layer.empty:
            folium.GeoJson(
                layer,
                name=f"{minutes}-minute walking area",
                style_function=lambda _, colour=colours[minutes]: {
                    "color": colour,
                    "fillColor": colour,
                    "weight": 1,
                    "fillOpacity": 0.35,
                },
            ).add_to(map_object)

    for _, facility in facilities.iterrows():
        folium.CircleMarker(
            location=[facility.geometry.y, facility.geometry.x],
            radius=5,
            color="#991b1b",
            fill=True,
            fill_color="#ef4444",
            fill_opacity=0.9,
            tooltip=str(facility["name"]),
        ).add_to(map_object)

    folium.LayerControl(collapsed=False).add_to(map_object)
    return map_object


def main() -> None:
    """Run the complete accessibility workflow and export the outputs."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ox.settings.use_cache = True
    ox.settings.log_console = True

    study_area = load_study_area()
    polygon = study_area.geometry.iloc[0]
    graph = ox.graph_from_polygon(polygon, network_type="walk", simplify=True)
    graph = add_travel_time(graph)
    facilities = load_healthcare_facilities(polygon)

    if facilities.empty:
        raise RuntimeError("No healthcare facilities were returned by OpenStreetMap.")

    isochrones = create_isochrones(graph, facilities)
    interactive_map = build_map(study_area, facilities, isochrones)
    interactive_map.save(OUTPUT_DIR / "obuasi_healthcare_accessibility.html")

    facilities.drop(columns="geometry").to_csv(
        OUTPUT_DIR / "healthcare_facilities.csv", index=False
    )
    pd.DataFrame(
        {
            "indicator": ["Mapped healthcare facilities", "Walking speed (km/h)"],
            "value": [len(facilities), WALKING_SPEED_KPH],
        }
    ).to_csv(OUTPUT_DIR / "analysis_summary.csv", index=False)

    print(f"Analysis complete. Outputs saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

