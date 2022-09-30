from django.contrib.gis.db.models import GeometryField
from django.db.models.functions import Coalesce
from django.views.generic import ListView
from vectortiles.postgis.views import MVTView

from region.models import ProtectedArea


class ProtectedAreaTileView(MVTView, ListView):
    model = ProtectedArea
    vector_tile_layer_name = "protected-areas"
    vector_tile_fields = (
        "id",
        "name",
    )
    vector_tile_geom_name = "boundary"
