from django.contrib.gis.db.models import GeometryField
from django.db.models.functions import Coalesce
from django.views.generic import ListView
from vectortiles.postgis.views import MVTView

from survey.models import HappeningSurvey


class TileView(MVTView, ListView):
    model = HappeningSurvey
    vector_tile_layer_name = "happening-surveys"
    vector_tile_fields = (
        "id",
        "category__title",
        "title",
        "description",
        "sentiment",
        "status",
        "improvement",
    )
    vector_tile_geom_name = "geom"
    vector_tile_queryset = HappeningSurvey.objects.filter(is_public=True).annotate(
        geom=Coalesce("location", "boundary", output_field=GeometryField(srid=4326))
    )
