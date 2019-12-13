from django.contrib.gis.geos import LineString


def get_linestring_from_geolocations(geolocations_qs):
    return LineString([geolocation.position for geolocation in geolocations_qs], srid=3857)
