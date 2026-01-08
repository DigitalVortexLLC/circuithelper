import json
import zipfile
from io import BytesIO
from typing import Dict, Optional, Tuple

from fastkml import kml
from lxml import etree
from shapely.geometry import shape, mapping
from shapely.ops import linemerge


def parse_kmz_file(kmz_file) -> Tuple[Optional[Dict], Optional[Tuple[float, float]]]:
    """
    Parse a KMZ file and extract GeoJSON data and map center coordinates.

    Args:
        kmz_file: File object containing KMZ data

    Returns:
        Tuple of (geojson_data, center_coords) where:
        - geojson_data is a dict containing GeoJSON FeatureCollection
        - center_coords is a tuple of (lat, lon) for map centering
    """
    try:
        # KMZ is a zipped KML file
        with zipfile.ZipFile(BytesIO(kmz_file.read())) as kmz:
            # Find the KML file inside
            kml_file = None
            for name in kmz.namelist():
                if name.endswith('.kml'):
                    kml_file = name
                    break

            if not kml_file:
                return None, None

            # Read and parse KML
            kml_data = kmz.read(kml_file)
            return parse_kml_data(kml_data)

    except Exception as e:
        print(f"Error parsing KMZ file: {e}")
        return None, None


def parse_kml_data(kml_data: bytes) -> Tuple[Optional[Dict], Optional[Tuple[float, float]]]:
    """
    Parse KML data and convert to GeoJSON.

    Args:
        kml_data: Bytes containing KML XML data

    Returns:
        Tuple of (geojson_data, center_coords)
    """
    try:
        # Parse KML
        root = etree.fromstring(kml_data)
        k = kml.KML()
        k.from_string(kml_data)

        features = []
        all_coords = []

        # Extract features from KML
        for feature in k.features():
            features_from_document(feature, features, all_coords)

        # Create GeoJSON FeatureCollection
        geojson = {
            'type': 'FeatureCollection',
            'features': features
        }

        # Calculate center point
        center = None
        if all_coords:
            avg_lat = sum(c[1] for c in all_coords) / len(all_coords)
            avg_lon = sum(c[0] for c in all_coords) / len(all_coords)
            center = (avg_lat, avg_lon)

        return geojson, center

    except Exception as e:
        print(f"Error parsing KML data: {e}")
        return None, None


def features_from_document(document, features_list, coords_list):
    """
    Recursively extract features from KML document/folder structure.
    """
    if hasattr(document, 'features'):
        for feature in document.features():
            if hasattr(feature, 'geometry') and feature.geometry:
                # Convert to GeoJSON feature
                geom = shape(feature.geometry)
                coords = extract_coordinates(geom)
                coords_list.extend(coords)

                feature_dict = {
                    'type': 'Feature',
                    'geometry': mapping(geom),
                    'properties': {
                        'name': getattr(feature, 'name', ''),
                        'description': getattr(feature, 'description', ''),
                    }
                }
                features_list.append(feature_dict)

            # Recursively process folders
            if hasattr(feature, 'features'):
                features_from_document(feature, features_list, coords_list)


def extract_coordinates(geometry):
    """
    Extract coordinate pairs from a Shapely geometry.
    """
    coords = []
    geom_type = geometry.geom_type

    if geom_type == 'Point':
        coords.append((geometry.x, geometry.y))
    elif geom_type in ['LineString', 'LinearRing']:
        coords.extend(geometry.coords)
    elif geom_type == 'Polygon':
        coords.extend(geometry.exterior.coords)
    elif geom_type.startswith('Multi') or geom_type == 'GeometryCollection':
        for geom in geometry.geoms:
            coords.extend(extract_coordinates(geom))

    return coords


def calculate_path_distance(geojson_data: Dict) -> Optional[float]:
    """
    Calculate total path distance in kilometers from GeoJSON data.

    Args:
        geojson_data: GeoJSON FeatureCollection dict

    Returns:
        Distance in kilometers, or None if calculation fails
    """
    try:
        from shapely.ops import transform
        import pyproj

        total_distance = 0

        # Set up projection to calculate distance in meters
        wgs84 = pyproj.CRS('EPSG:4326')
        utm = pyproj.CRS('EPSG:3857')  # Web Mercator

        # Create transformer for pyproj 2.x+
        transformer = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True)

        for feature in geojson_data.get('features', []):
            geom = shape(feature['geometry'])

            if geom.geom_type in ['LineString', 'MultiLineString']:
                # Transform to projected coordinate system
                projected_geom = transform(transformer.transform, geom)
                total_distance += projected_geom.length

        # Convert meters to kilometers
        return round(total_distance / 1000, 2)

    except Exception as e:
        print(f"Error calculating path distance: {e}")
        return None


def generate_folium_map(geojson_data: Dict, center_coords: Tuple[float, float], zoom: int = 10) -> str:
    """
    Generate HTML for an interactive Folium map.

    Args:
        geojson_data: GeoJSON FeatureCollection dict
        center_coords: Tuple of (lat, lon) for map center
        zoom: Initial zoom level

    Returns:
        HTML string containing the interactive map
    """
    try:
        import folium

        # Create map centered on coordinates
        m = folium.Map(
            location=center_coords,
            zoom_start=zoom,
            tiles='OpenStreetMap'
        )

        # Add GeoJSON layer
        folium.GeoJson(
            geojson_data,
            name='Circuit Path',
            style_function=lambda x: {
                'color': '#3388ff',
                'weight': 3,
                'opacity': 0.8
            },
            highlight_function=lambda x: {
                'weight': 5,
                'opacity': 1.0
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['name', 'description'],
                aliases=['Name:', 'Description:'],
                localize=True
            )
        ).add_to(m)

        # Add layer control
        folium.LayerControl().add_to(m)

        # Return HTML
        return m._repr_html_()

    except Exception as e:
        print(f"Error generating map: {e}")
        return f"<p>Error generating map: {e}</p>"
