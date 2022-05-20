from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import Region


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        exclude = ("boundary",)


class RegionGeoJsonSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Region
        geo_field = "boundary"
        fields = "__all__"
