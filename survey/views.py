from django.contrib.gis.db.models import GeometryField
from django.db.models.functions import Coalesce
from django.views.generic import ListView
from vectortiles import VectorLayer
from vectortiles.views import MVTView

from survey.models import HappeningSurvey


class TileVectorLayer(VectorLayer):
    model = HappeningSurvey
    id = "is"
    layer_name = "happening-surveys"
    tile_fields = (
        "id",
        "category__title",
        "title",
        "description",
        "sentiment",
        "status",
        "improvement",
    )
    geom_name = "geom"
    queryset = HappeningSurvey.objects.filter(is_public=True).annotate(
        geom=Coalesce("location", "boundary", output_field=GeometryField(srid=4326))
    )


class TileView(MVTView, ListView):
    layer_classes = [TileVectorLayer]
