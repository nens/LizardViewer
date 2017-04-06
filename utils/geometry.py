# -*- coding: utf-8 -*-
"""Module for handling geometry."""
from qgis.core import QgsGeometry
from qgis.core import QgsPoint


def create_geometry(geometry):
    """
    Function to create a QGIS geometry.

    Arguments:
        geometry (dict): Geometry, containing the geometry types and the
                         coordinates that will be used to create the geometry.
    """
    geometry_type = geometry["type"]
    if geometry_type == "Point":
        lat = float(geometry['coordinates'][0])
        lon = float(geometry['coordinates'][1])
        return QgsGeometry.fromPoint(QgsPoint(lat, lon))
    elif geometry_type == "LineString":
        lat1 = float(geometry['coordinates'][0][0])
        lon1 = float(geometry['coordinates'][0][1])
        lat2 = float(geometry['coordinates'][1][0])
        lon2 = float(geometry['coordinates'][1][1])
        return QgsGeometry.fromPolyline([QgsPoint(lat1, lon1),
                                         QgsPoint(lat2, lon2)])
    elif geometry_type == "Polygon":
        list_of_points = []
        for points in geometry["coordinates"]:
            for point in points:
                lat = float(point[0])
                lon = float(point[1])
                list_of_points.append(QgsPoint(lat, lon))
            return QgsGeometry.fromPolygon([list_of_points])
    elif geometry_type == "MultiPolygon":
        list_of_polygons = []
        for polygons in geometry["coordinates"]:
            for polygon in polygons:
                list_of_points = []
                for point in polygon:
                    lat = float(point[0])
                    lon = float(point[1])
                    list_of_points.append(QgsPoint(lat, lon))
                list_of_polygons.append(list_of_points)
            return QgsGeometry.fromMultiPolygon([list_of_polygons])
