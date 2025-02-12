from django.contrib.gis.db.models import GeometryField
from django.db.models.functions import Coalesce
from django.views.generic import ListView
from vectortiles import VectorLayer
from vectortiles.views import MVTView

from region.models import ProtectedArea


class ProtectedAreaVector(VectorLayer):
    model = ProtectedArea
    id = "id"
    layer_name = "protected-areas"
    tile_fields = (
        "id",
        "name",
    )
    geom_field = "boundary"


class ProtectedAreaTileView(MVTView, ListView):
    layer_classes = [ProtectedAreaVector]
