"""
Tests for NetBox Circuit Manager utility functions.
"""

import pytest
import json
from io import BytesIO
from zipfile import ZipFile
from decimal import Decimal

from circuithelper.utils import (
    parse_kmz_file,
    parse_kml_data,
    extract_coordinates,
    calculate_path_distance,
    generate_folium_map
)


class TestKMZParsing:
    """Test KMZ file parsing functions."""

    def create_test_kml(self):
        """Create a simple test KML string."""
        kml = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Test Circuit Path</name>
    <Placemark>
      <name>Circuit Route</name>
      <description>Test circuit path</description>
      <LineString>
        <coordinates>
          -122.4194,37.7749,0
          -122.4084,37.7849,0
        </coordinates>
      </LineString>
    </Placemark>
  </Document>
</kml>"""
        return kml.encode('utf-8')

    def create_test_kmz(self):
        """Create a test KMZ file in memory."""
        kml_data = self.create_test_kml()

        # Create KMZ (zipped KML)
        kmz_buffer = BytesIO()
        with ZipFile(kmz_buffer, 'w') as kmz:
            kmz.writestr('doc.kml', kml_data)

        kmz_buffer.seek(0)
        return kmz_buffer

    def test_parse_kml_data(self):
        """Test parsing KML data to GeoJSON."""
        kml_data = self.create_test_kml()
        geojson, center = parse_kml_data(kml_data)

        assert geojson is not None
        assert geojson['type'] == 'FeatureCollection'
        assert 'features' in geojson
        assert center is not None
        assert len(center) == 2  # (lat, lon)

    def test_parse_kmz_file(self):
        """Test parsing KMZ file."""
        kmz_file = self.create_test_kmz()
        geojson, center = parse_kmz_file(kmz_file)

        assert geojson is not None
        assert geojson['type'] == 'FeatureCollection'
        assert center is not None

    def test_parse_invalid_kmz(self):
        """Test parsing invalid KMZ file."""
        invalid_file = BytesIO(b"This is not a KMZ file")
        geojson, center = parse_kmz_file(invalid_file)

        assert geojson is None
        assert center is None

    def test_parse_kmz_without_kml(self):
        """Test parsing KMZ without KML file inside."""
        kmz_buffer = BytesIO()
        with ZipFile(kmz_buffer, 'w') as kmz:
            kmz.writestr('other_file.txt', b'Not a KML file')

        kmz_buffer.seek(0)
        geojson, center = parse_kmz_file(kmz_buffer)

        assert geojson is None
        assert center is None


class TestCoordinateExtraction:
    """Test coordinate extraction from geometries."""

    def test_extract_point_coordinates(self):
        """Test extracting coordinates from a Point."""
        from shapely.geometry import Point

        point = Point(10.0, 20.0)
        coords = extract_coordinates(point)

        assert len(coords) == 1
        assert coords[0] == (10.0, 20.0)

    def test_extract_linestring_coordinates(self):
        """Test extracting coordinates from a LineString."""
        from shapely.geometry import LineString

        line = LineString([(0, 0), (1, 1), (2, 2)])
        coords = extract_coordinates(line)

        assert len(coords) == 3
        assert (0, 0) in coords
        assert (2, 2) in coords

    def test_extract_polygon_coordinates(self):
        """Test extracting coordinates from a Polygon."""
        from shapely.geometry import Polygon

        polygon = Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
        coords = extract_coordinates(polygon)

        assert len(coords) == 5  # Including closing point

    def test_extract_multilinestring_coordinates(self):
        """Test extracting coordinates from a MultiLineString."""
        from shapely.geometry import MultiLineString

        multiline = MultiLineString([
            [(0, 0), (1, 1)],
            [(2, 2), (3, 3)]
        ])
        coords = extract_coordinates(multiline)

        assert len(coords) == 4


class TestPathDistanceCalculation:
    """Test circuit path distance calculation."""

    def test_calculate_linestring_distance(self):
        """Test calculating distance for a LineString."""
        geojson = {
            'type': 'FeatureCollection',
            'features': [{
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        [-122.4194, 37.7749],
                        [-122.4084, 37.7849]
                    ]
                }
            }]
        }

        distance = calculate_path_distance(geojson)

        assert distance is not None
        assert distance > 0
        # Distance should be approximately 1.5 km for this short path
        assert 0 < distance < 10

    def test_calculate_empty_geojson_distance(self):
        """Test calculating distance for empty GeoJSON."""
        geojson = {
            'type': 'FeatureCollection',
            'features': []
        }

        distance = calculate_path_distance(geojson)

        # Should return 0 or None for empty features
        assert distance == 0 or distance is None

    def test_calculate_point_distance(self):
        """Test that point geometry returns 0 distance."""
        geojson = {
            'type': 'FeatureCollection',
            'features': [{
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-122.4194, 37.7749]
                }
            }]
        }

        distance = calculate_path_distance(geojson)

        # Points have no length
        assert distance == 0 or distance is None


class TestMapGeneration:
    """Test Folium map generation."""

    def test_generate_folium_map(self):
        """Test generating a Folium map."""
        geojson = {
            'type': 'FeatureCollection',
            'features': [{
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        [-122.4194, 37.7749],
                        [-122.4084, 37.7849]
                    ]
                },
                'properties': {
                    'name': 'Test Path'
                }
            }]
        }

        center = (37.7749, -122.4194)
        zoom = 12

        html = generate_folium_map(geojson, center, zoom)

        assert html is not None
        assert isinstance(html, str)
        assert len(html) > 0
        # Check for common Folium HTML markers
        assert 'leaflet' in html.lower() or 'map' in html.lower()

    def test_generate_map_with_invalid_data(self):
        """Test generating map with invalid data."""
        geojson = {'invalid': 'data'}
        center = (0, 0)
        zoom = 10

        html = generate_folium_map(geojson, center, zoom)

        # Should return error message or empty map
        assert html is not None
        assert isinstance(html, str)

    def test_generate_map_with_multiple_features(self):
        """Test generating map with multiple features."""
        geojson = {
            'type': 'FeatureCollection',
            'features': [
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': [[-122.4194, 37.7749], [-122.4084, 37.7849]]
                    },
                    'properties': {'name': 'Path 1'}
                },
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': [[-122.4084, 37.7849], [-122.3984, 37.7949]]
                    },
                    'properties': {'name': 'Path 2'}
                }
            ]
        }

        center = (37.7849, -122.4084)
        html = generate_folium_map(geojson, center, 12)

        assert html is not None
        assert isinstance(html, str)
        assert len(html) > 0
